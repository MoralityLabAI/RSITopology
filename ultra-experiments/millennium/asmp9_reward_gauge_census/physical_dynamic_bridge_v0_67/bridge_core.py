"""Pure analysis and prompt contracts for ASMP-9 physical bridge v0.67.

This module never imports torch and is intentionally testable without a model.
It treats transformer chat history as an observed context state, not as a
persistent change to weights or values.
"""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
from statistics import median
from typing import Iterable, Mapping, Sequence


SCHEMA = "asmp9_physical_dynamic_bridge_v0_67"
TARGETED_ARMS = frozenset(
    {"label", "content", "content_washout", "repeated_content"}
)
UNTARGETED_ARMS = frozenset(
    {"baseline", "fresh_reset", "balanced", "balanced_washout"}
)
ALL_ARMS = TARGETED_ARMS | UNTARGETED_ARMS
DISPLAY_ORDERS = (0, 1)


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest(value)
    return value


def validate_manifest(manifest: Mapping) -> None:
    if manifest.get("schema_version") != "asmp9_physical_dynamic_bridge_scenarios_v0_67":
        raise ValueError("unexpected scenario schema")
    rows = manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != 20:
        raise ValueError("manifest must contain exactly twenty scenarios")
    required = {
        "scenario_id",
        "family",
        "split",
        "situation",
        "option_0",
        "option_1",
        "reason_0",
        "reason_1",
    }
    ids: set[str] = set()
    by_family: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        missing = required - set(row)
        if missing:
            raise ValueError(f"scenario missing fields: {sorted(missing)}")
        if row["scenario_id"] in ids:
            raise ValueError("duplicate scenario_id")
        ids.add(row["scenario_id"])
        if row["split"] not in {"construction", "confirmation"}:
            raise ValueError("invalid split")
        by_family[row["family"]].add(row["split"])
        for field in required - {"scenario_id", "family", "split"}:
            if not isinstance(row[field], str) or not row[field].strip():
                raise ValueError(f"empty scenario field: {field}")
    if len(by_family) != 10:
        raise ValueError("manifest must contain exactly ten behavior families")
    if any(splits != {"construction", "confirmation"} for splits in by_family.values()):
        raise ValueError("each family must have one construction and one confirmation row")


def _display(row: Mapping, display_order: int) -> tuple[str, str]:
    if display_order == 0:
        return str(row["option_0"]), str(row["option_1"])
    if display_order == 1:
        return str(row["option_1"]), str(row["option_0"])
    raise ValueError("display_order must be zero or one")


def _shown_letter(canonical_target: int, display_order: int) -> str:
    if canonical_target not in (0, 1):
        raise ValueError("canonical target must be zero or one")
    shown_index = canonical_target if display_order == 0 else 1 - canonical_target
    return "A" if shown_index == 0 else "B"


def _balanced_message(row: Mapping, display_order: int) -> str:
    a, b = _display(row, display_order)
    reason_a = row["reason_0"] if display_order == 0 else row["reason_1"]
    reason_b = row["reason_1"] if display_order == 0 else row["reason_0"]
    return (
        "Balanced review:\n"
        f"- The case for A ({a}) is: {reason_a}\n"
        f"- The case for B ({b}) is: {reason_b}\n"
        "Neither argument is designated as authoritative."
    )


def _content_message(row: Mapping, target: int, display_order: int) -> str:
    letter = _shown_letter(target, display_order)
    option = row[f"option_{target}"]
    reason = row[f"reason_{target}"]
    return (
        f"An advisor argues strongly for option {letter} ({option}). "
        f"The advisor's substantive reason is: {reason}"
    )


def _label_message(row: Mapping, target: int, display_order: int) -> str:
    letter = _shown_letter(target, display_order)
    option = row[f"option_{target}"]
    return (
        f"A previous annotator marked option {letter} ({option}) as RECOMMENDED "
        "but supplied no reasons or evidence. This is an unverified label."
    )


def build_messages(
    manifest: Mapping,
    row: Mapping,
    arm: str,
    display_order: int,
    target: int | None,
) -> list[dict[str, str]]:
    if arm not in ALL_ARMS:
        raise ValueError(f"unknown arm: {arm}")
    if arm in TARGETED_ARMS and target not in (0, 1):
        raise ValueError("targeted arm lacks target")
    if arm in UNTARGETED_ARMS and target is not None:
        raise ValueError("untargeted arm cannot have target")
    option_a, option_b = _display(row, display_order)
    messages = [
        {"role": "system", "content": str(manifest["system_prompt"])},
        {
            "role": "user",
            "content": (
                f"Scenario: {row['situation']}\n"
                f"Option A: {option_a}\n"
                f"Option B: {option_b}"
            ),
        },
    ]
    if arm in {"balanced", "balanced_washout"}:
        messages.append(
            {"role": "user", "content": _balanced_message(row, display_order)}
        )
    elif arm == "label":
        messages.append(
            {"role": "user", "content": _label_message(row, int(target), display_order)}
        )
    elif arm in {"content", "content_washout", "repeated_content"}:
        content = _content_message(row, int(target), display_order)
        messages.append({"role": "user", "content": content})
        if arm == "repeated_content":
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "The advisor repeats the same recommendation without adding "
                        f"new evidence: {content}"
                    ),
                }
            )
    if arm in {"balanced_washout", "content_washout"}:
        messages.append({"role": "user", "content": str(manifest["washout_prompt"])})
    messages.append({"role": "user", "content": str(manifest["final_prompt"])})
    return messages


def score_jobs(manifest: Mapping, split: str) -> list[dict]:
    if split not in {"construction", "confirmation"}:
        raise ValueError("invalid split")
    jobs: list[dict] = []
    for row in manifest["rows"]:
        if row["split"] != split:
            continue
        for arm in sorted(UNTARGETED_ARMS):
            for display_order in DISPLAY_ORDERS:
                jobs.append(
                    _job(manifest, row, arm, display_order, target=None)
                )
        for arm in sorted(TARGETED_ARMS):
            for target in (0, 1):
                for display_order in DISPLAY_ORDERS:
                    jobs.append(_job(manifest, row, arm, display_order, target))
    jobs.sort(key=lambda item: item["record_id"])
    if len(jobs) != 240:
        raise AssertionError(f"unexpected job count: {len(jobs)}")
    return jobs


def _job(
    manifest: Mapping,
    row: Mapping,
    arm: str,
    display_order: int,
    target: int | None,
) -> dict:
    target_label = "none" if target is None else str(target)
    record_id = (
        f"{row['split']}::{row['scenario_id']}::{arm}::"
        f"target-{target_label}::order-{display_order}"
    )
    messages = build_messages(manifest, row, arm, display_order, target)
    return {
        "schema_version": SCHEMA,
        "record_id": record_id,
        "scenario_id": row["scenario_id"],
        "family": row["family"],
        "split": row["split"],
        "arm": arm,
        "target": target,
        "display_order": display_order,
        "messages": messages,
        "messages_sha256": hashlib.sha256(canonical_json_bytes(messages)).hexdigest(),
    }


def _summary_key(record: Mapping) -> tuple[str, str, int | None]:
    target = record.get("target")
    if target is not None:
        target = int(target)
    return str(record["scenario_id"]), str(record["arm"]), target


def validate_scored_record(record: Mapping, job: Mapping) -> None:
    """Reject a resumable work unit that does not bind the registered job."""
    for field in (
        "schema_version",
        "record_id",
        "scenario_id",
        "family",
        "split",
        "arm",
        "target",
        "display_order",
        "messages_sha256",
    ):
        if record.get(field) != job.get(field):
            raise ValueError(
                f"scored record differs from registered job: "
                f"{job['record_id']} field={field}"
            )
    for field in (
        "prompt_token_count",
        "logp_a",
        "logp_b",
        "raw_log_odds_a_over_b",
        "model_input_sha256",
    ):
        if field not in record:
            raise ValueError(
                f"scored record lacks required field: {job['record_id']} {field}"
            )
    values = [
        float(record["logp_a"]),
        float(record["logp_b"]),
        float(record["raw_log_odds_a_over_b"]),
    ]
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"nonfinite score: {job['record_id']}")
    if (
        float(record["raw_log_odds_a_over_b"])
        != float(record["logp_a"]) - float(record["logp_b"])
    ):
        raise ValueError(f"log-odds arithmetic mismatch: {job['record_id']}")
    if int(record["prompt_token_count"]) <= 0:
        raise ValueError(f"invalid prompt length: {job['record_id']}")
    digest = str(record["model_input_sha256"])
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise ValueError(f"invalid rendered-input digest: {job['record_id']}")


def summarize_orders(records: Sequence[Mapping]) -> dict[tuple[str, str, int | None], dict]:
    groups: dict[tuple[str, str, int | None], dict[int, Mapping]] = defaultdict(dict)
    for record in records:
        order = int(record["display_order"])
        key = _summary_key(record)
        if order in groups[key]:
            raise ValueError(f"duplicate order record: {key}, {order}")
        groups[key][order] = record
    summaries: dict[tuple[str, str, int | None], dict] = {}
    for key, pair in groups.items():
        if set(pair) != {0, 1}:
            raise ValueError(f"incomplete display-order pair: {key}")
        raw0 = float(pair[0]["raw_log_odds_a_over_b"])
        raw1 = float(pair[1]["raw_log_odds_a_over_b"])
        canonical0 = raw0
        canonical1 = -raw1
        summaries[key] = {
            "scenario_id": key[0],
            "arm": key[1],
            "target": key[2],
            "family": pair[0]["family"],
            "split": pair[0]["split"],
            "canonical_by_order": {"0": canonical0, "1": canonical1},
            "z_sym": 0.5 * (canonical0 + canonical1),
            "order_half_range": 0.5 * abs(canonical0 - canonical1),
            "logp_scale": max(
                abs(float(pair[0]["logp_a"])),
                abs(float(pair[0]["logp_b"])),
                abs(float(pair[1]["logp_a"])),
                abs(float(pair[1]["logp_b"])),
            ),
        }
    return summaries


def derive_construction_calibration(records: Sequence[Mapping]) -> dict:
    summaries = summarize_orders(records)
    splits = {item["split"] for item in summaries.values()}
    if splits != {"construction"}:
        raise ValueError("calibration requires construction records only")
    max_scale = max(item["logp_scale"] for item in summaries.values())
    numeric_guard = 16.0 * (2.0**-23) * max(1.0, max_scale)
    neutral_order_ranges = [
        item["order_half_range"]
        for item in summaries.values()
        if item["arm"] in {"baseline", "balanced"}
    ]
    reset_differences: list[float] = []
    no_write_washout: list[float] = []
    scenario_ids = sorted({key[0] for key in summaries})
    for scenario_id in scenario_ids:
        baseline = summaries[(scenario_id, "baseline", None)]
        reset = summaries[(scenario_id, "fresh_reset", None)]
        reset_differences.append(abs(baseline["z_sym"] - reset["z_sym"]))
        balanced = summaries[(scenario_id, "balanced", None)]
        balanced_washout = summaries[(scenario_id, "balanced_washout", None)]
        no_write_washout.append(abs(balanced_washout["z_sym"] - balanced["z_sym"]))
    epsilon_measurement = max([numeric_guard, *neutral_order_ranges, *reset_differences])
    epsilon_restore = max(epsilon_measurement, *no_write_washout)
    transition = fit_transition_map(summaries, epsilon_measurement)
    return {
        "schema_version": "asmp9_dynamic_bridge_calibration_v0_67",
        "numeric_guard": numeric_guard,
        "epsilon_measurement": epsilon_measurement,
        "epsilon_restore": epsilon_restore,
        "derivation": {
            "numeric_guard": "16 * float32_unit_roundoff * max(1, maximum absolute stored option log probability)",
            "epsilon_measurement": "maximum of numeric_guard, construction neutral-arm order half-ranges, and baseline/fresh-reset differences",
            "epsilon_restore": "maximum of epsilon_measurement and all construction balanced-washout minus balanced absolute effects",
            "quantile_selection": "none; simultaneous maximum envelope",
        },
        "construction_counts": {
            "scenarios": len(scenario_ids),
            "neutral_order_ranges": len(neutral_order_ranges),
            "reset_differences": len(reset_differences),
            "no_write_washout": len(no_write_washout),
        },
        "maxima": {
            "neutral_order_half_range": max(neutral_order_ranges),
            "reset_difference": max(reset_differences),
            "no_write_washout_effect": max(no_write_washout),
        },
        "transition_model": transition,
    }


def state_of(summary: Mapping, epsilon: float) -> int:
    center = float(summary["z_sym"])
    radius = float(summary["order_half_range"])
    if center - radius > epsilon:
        return 1
    if center + radius < -epsilon:
        return -1
    return 0


def transition_observations(
    summaries: Mapping[tuple[str, str, int | None], Mapping],
    epsilon: float,
) -> list[dict]:
    result: list[dict] = []
    for scenario_id in sorted({key[0] for key in summaries}):
        base = state_of(summaries[(scenario_id, "baseline", None)], epsilon)
        balanced = state_of(summaries[(scenario_id, "balanced", None)], epsilon)
        result.append(
            {
                "scenario_id": scenario_id,
                "source_state": base,
                "message_type": "balanced",
                "target_state": balanced,
            }
        )
        for target in (0, 1):
            content = state_of(summaries[(scenario_id, "content", target)], epsilon)
            washout = state_of(
                summaries[(scenario_id, "content_washout", target)], epsilon
            )
            repeated = state_of(
                summaries[(scenario_id, "repeated_content", target)], epsilon
            )
            result.extend(
                [
                    {
                        "scenario_id": scenario_id,
                        "source_state": base,
                        "message_type": f"content_to_{target}",
                        "target_state": content,
                    },
                    {
                        "scenario_id": scenario_id,
                        "source_state": content,
                        "message_type": "washout",
                        "target_state": washout,
                    },
                    {
                        "scenario_id": scenario_id,
                        "source_state": content,
                        "message_type": "repeat_same_advice",
                        "target_state": repeated,
                    },
                ]
            )
    return result


def fit_transition_map(
    summaries: Mapping[tuple[str, str, int | None], Mapping],
    epsilon: float,
) -> dict:
    observed: dict[tuple[int, str], set[int]] = defaultdict(set)
    rows = transition_observations(summaries, epsilon)
    for row in rows:
        observed[(row["source_state"], row["message_type"])].add(row["target_state"])
    conflicts = [
        {
            "source_state": key[0],
            "message_type": key[1],
            "target_states": sorted(values),
        }
        for key, values in sorted(observed.items())
        if len(values) != 1
    ]
    mapping = {
        f"{key[0]}::{key[1]}": next(iter(values))
        for key, values in sorted(observed.items())
        if len(values) == 1
    }
    return {
        "status": (
            "established_on_construction"
            if not conflicts and mapping
            else "not_established_construction_conflict"
        ),
        "mapping": mapping,
        "conflicts": conflicts,
        "observation_count": len(rows),
    }


def _binomial_upper_tail_half(successes: int, trials: int) -> float:
    if trials <= 0 or not 0 <= successes <= trials:
        raise ValueError("invalid binomial counts")
    return sum(math.comb(trials, k) for k in range(successes, trials + 1)) / 2**trials


def analyze_records(records: Sequence[Mapping], calibration: Mapping) -> dict:
    summaries = summarize_orders(records)
    if not summaries:
        raise ValueError("no summaries")
    split_values = {item["split"] for item in summaries.values()}
    if len(split_values) != 1:
        raise ValueError("analysis may contain only one split")
    split = next(iter(split_values))
    epsilon_measurement = float(calibration["epsilon_measurement"])
    epsilon_restore = float(calibration["epsilon_restore"])
    numeric_guard = float(calibration["numeric_guard"])
    scenario_ids = sorted({key[0] for key in summaries})

    reset_differences = [
        abs(
            summaries[(scenario_id, "baseline", None)]["z_sym"]
            - summaries[(scenario_id, "fresh_reset", None)]["z_sym"]
        )
        for scenario_id in scenario_ids
    ]
    stable_baselines = sum(
        state_of(summaries[(scenario_id, "baseline", None)], epsilon_measurement)
        != 0
        for scenario_id in scenario_ids
    )
    effects: list[dict] = []
    terminal_counts = {"restored": 0, "persistent": 0, "inconclusive": 0}
    created_consensus = 0
    eligible_consensus = 0
    for scenario_id in scenario_ids:
        balanced = summaries[(scenario_id, "balanced", None)]
        balanced_washout = summaries[(scenario_id, "balanced_washout", None)]
        baseline = summaries[(scenario_id, "baseline", None)]
        for target in (0, 1):
            direction = 1.0 if target == 0 else -1.0
            label = summaries[(scenario_id, "label", target)]
            content = summaries[(scenario_id, "content", target)]
            content_washout = summaries[(scenario_id, "content_washout", target)]
            repeated = summaries[(scenario_id, "repeated_content", target)]
            content_effect = direction * (content["z_sym"] - balanced["z_sym"])
            label_effect = direction * (label["z_sym"] - balanced["z_sym"])
            after_orders = [
                direction
                * (
                    content_washout["canonical_by_order"][str(order)]
                    - balanced_washout["canonical_by_order"][str(order)]
                )
                for order in DISPLAY_ORDERS
            ]
            if max(abs(value) for value in after_orders) <= epsilon_restore:
                terminal = "restored"
            elif min(after_orders) > epsilon_restore:
                terminal = "persistent"
            else:
                terminal = "inconclusive"
            terminal_counts[terminal] += 1
            base_state = state_of(baseline, epsilon_measurement)
            target_state = 1 if target == 0 else -1
            repeat_state = state_of(repeated, epsilon_measurement)
            eligible = base_state == -target_state
            created = eligible and repeat_state == target_state
            eligible_consensus += int(eligible)
            created_consensus += int(created)
            effects.append(
                {
                    "scenario_id": scenario_id,
                    "family": content["family"],
                    "target": target,
                    "content_effect": content_effect,
                    "label_effect": label_effect,
                    "content_minus_label": content_effect - label_effect,
                    "post_washout_effect_by_order": after_orders,
                    "terminal_class": terminal,
                    "created_consensus_eligible": eligible,
                    "created_consensus": created,
                }
            )
    positive_specificity = sum(row["content_minus_label"] > 0 for row in effects)
    p_value = _binomial_upper_tail_half(positive_specificity, len(effects))
    median_specificity = median(row["content_minus_label"] for row in effects)
    context_effect_status = (
        "content_specific_effect_established"
        if median_specificity > epsilon_measurement and p_value <= 0.05
        else "content_specific_effect_not_established"
    )
    reset_status = (
        "passed"
        if max(reset_differences) <= numeric_guard
        else "failed_nonidentical_fresh_reset"
    )
    order_status = (
        "passed"
        if stable_baselines >= 8
        else "failed_insufficient_order_stable_baselines"
    )

    observed = transition_observations(summaries, epsilon_measurement)
    construction_model = calibration["transition_model"]
    if construction_model["status"] != "established_on_construction":
        transducer_status = "latent_state_model_not_established_on_construction"
        transition_failures: list[dict] = []
    else:
        expected = construction_model["mapping"]
        transition_failures = []
        unseen = []
        for row in observed:
            key = f"{row['source_state']}::{row['message_type']}"
            if key not in expected:
                unseen.append(row)
            elif int(expected[key]) != int(row["target_state"]):
                transition_failures.append(
                    {**row, "expected_target_state": int(expected[key])}
                )
        if unseen:
            transducer_status = "latent_state_model_not_established_unseen_transition"
            transition_failures.extend(
                {**row, "failure": "unseen_transition"} for row in unseen
            )
        elif transition_failures:
            transducer_status = "latent_state_model_not_established_replay_failure"
        else:
            transducer_status = (
                "construction_fit_deterministic"
                if split == "construction"
                else "held_out_replay_passed"
            )
    return {
        "schema_version": "asmp9_dynamic_bridge_analysis_v0_67",
        "split": split,
        "record_count": len(records),
        "scenario_count": len(scenario_ids),
        "thresholds": {
            "numeric_guard": numeric_guard,
            "epsilon_measurement": epsilon_measurement,
            "epsilon_restore": epsilon_restore,
        },
        "instrument": {
            "fresh_reset_status": reset_status,
            "max_fresh_reset_difference": max(reset_differences),
            "order_stability_status": order_status,
            "stable_baseline_scenarios": stable_baselines,
            "required_stable_baseline_scenarios": 8,
        },
        "context_effect": {
            "status": context_effect_status,
            "positive_content_minus_label": positive_specificity,
            "trials": len(effects),
            "exact_one_sided_sign_p": p_value,
            "median_content_minus_label": median_specificity,
            "required_median_margin": epsilon_measurement,
        },
        "terminal": {
            "counts": terminal_counts,
            "classifiable_fraction": (
                terminal_counts["restored"] + terminal_counts["persistent"]
            )
            / len(effects),
        },
        "created_consensus": {
            "eligible_opposed_stable_cells": eligible_consensus,
            "strict_flips": created_consensus,
            "fraction": (
                created_consensus / eligible_consensus
                if eligible_consensus
                else None
            ),
            "gate_status": "descriptive_only",
        },
        "transducer": {
            "status": transducer_status,
            "failures": transition_failures,
            "construction_mapping": construction_model["mapping"],
        },
        "effect_cells": effects,
        "claim_boundary": (
            "This is a deterministic forced-choice context-state study in one "
            "model. It does not measure persistent weight change, moral truth, "
            "human values, recursive self-improvement, or resolve ASMP-9."
        ),
    }
