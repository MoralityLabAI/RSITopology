"""Monotone audit-threshold experiment for ASMP-8 v0.4."""

from __future__ import annotations

import csv
import io
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.stats import beta


HERE = Path(__file__).resolve().parent
V03 = HERE.parent / "v0_3_calibrated_certificate"
if str(V03) not in sys.path:
    sys.path.insert(0, str(V03))

from calibration import error_populations, policy_coordinates, policy_registry  # noqa: E402


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def clopper_pearson_upper(failures: int, trials: int, confidence: float = 0.95) -> float:
    if failures == trials:
        return 1.0
    return float(beta.ppf(confidence, failures + 1, trials - failures))


def nested_envelopes(
    errors: np.ndarray,
    checkpoints: list[int],
    streams: int,
    seed: int,
    familywise_alpha: float,
) -> dict[str, np.ndarray]:
    if sorted(checkpoints) != checkpoints or len(set(checkpoints)) != len(checkpoints):
        raise ValueError("checkpoints must be unique and increasing")
    rng = np.random.default_rng(seed)
    probability = np.full(errors.size, 1 / errors.size)
    counts = np.zeros((streams, errors.size), dtype=np.int64)
    envelope_1 = np.ones(streams)
    envelope_2 = np.ones(streams)
    all_1 = []
    all_2 = []
    alpha_each = familywise_alpha / (2 * len(checkpoints))
    previous = 0
    for checkpoint in checkpoints:
        increment = checkpoint - previous
        counts += rng.multinomial(increment, probability, size=streams)
        mean_abs = counts @ np.abs(errors) / checkpoint
        mean_sq = counts @ (errors**2) / checkpoint
        radius = math.sqrt(math.log(1 / alpha_each) / (2 * checkpoint))
        raw_1 = np.minimum(1.0, mean_abs + radius)
        raw_2 = np.sqrt(np.minimum(1.0, mean_sq + radius))
        envelope_1 = np.minimum(envelope_1, raw_1)
        envelope_2 = np.minimum(envelope_2, raw_2)
        all_1.append(envelope_1.copy())
        all_2.append(envelope_2.copy())
        previous = checkpoint
    return {
        "u1": np.asarray(all_1),
        "u2": np.asarray(all_2),
        "alpha_each": np.asarray(alpha_each),
    }


def predicted_crossing(
    gain: float,
    coordinates: dict[str, float],
    actual_l1: float,
    actual_l2: float,
    checkpoints: list[int],
    alpha_each: float,
) -> int | None:
    for checkpoint in checkpoints:
        radius = math.sqrt(math.log(1 / alpha_each) / (2 * checkpoint))
        u1 = min(1.0, actual_l1 + radius)
        u2 = math.sqrt(min(1.0, actual_l2**2 + radius))
        margin = max(
            gain - u1 * coordinates["movement_linf"],
            gain - u2 * coordinates["movement_l2"],
            gain - coordinates["movement_l1"],
        )
        if margin > 0:
            return checkpoint
    return None


def summarize_first_crossings(first: np.ndarray, cap: int) -> dict[str, Any]:
    crossed = first[first > 0]
    payload: dict[str, Any] = {
        "crossed_streams": int(crossed.size),
        "censored_streams": int(first.size - crossed.size),
        "crossing_fraction_descriptive": float(crossed.size / first.size),
    }
    if crossed.size:
        payload.update(
            {
                "minimum": int(np.min(crossed)),
                "q25": float(np.quantile(crossed, 0.25, method="inverted_cdf")),
                "median": float(np.quantile(crossed, 0.5, method="inverted_cdf")),
                "q75": float(np.quantile(crossed, 0.75, method="inverted_cdf")),
                "maximum": int(np.max(crossed)),
            }
        )
    else:
        payload.update({"minimum": None, "q25": None, "median": None, "q75": None, "maximum": None})
    payload["cap"] = cap
    return payload


def run_dynamic(protocol: dict[str, Any], streams_override: int | None = None) -> tuple[
    dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    audit = protocol["audit_dynamics"]
    checkpoints = [int(value) for value in audit["checkpoints"]]
    streams = int(streams_override or audit["nested_streams"])
    alpha = float(audit["familywise_alpha"])
    proxy = np.linspace(-0.5, 0.5, 64)
    p0 = np.full(64, 1 / 64)
    populations = error_populations(64)
    parent_protocol = json.loads((V03 / "protocol_v0_3.json").read_text(encoding="utf-8"))
    policies = policy_registry(proxy, parent_protocol)
    seeds = np.random.SeedSequence(int(audit["root_seed"])).spawn(len(populations))

    conditions: list[dict[str, Any]] = []
    policy_rows: list[dict[str, Any]] = []
    cdf_rows: list[dict[str, Any]] = []
    monotone_violations = 0
    reversions = 0
    conditional_false_crossings = 0
    instrument_failure_streams_total = 0

    for family_index, (family, errors) in enumerate(populations.items()):
        seed = int(seeds[family_index].generate_state(1, dtype=np.uint64)[0])
        envelopes = nested_envelopes(errors, checkpoints, streams, seed, alpha)
        actual_l1 = float(np.mean(np.abs(errors)))
        actual_l2 = float(np.sqrt(np.mean(errors**2)))
        valid_stream = np.all(envelopes["u1"] + 1e-15 >= actual_l1, axis=0) & np.all(
            envelopes["u2"] + 1e-15 >= actual_l2, axis=0
        )
        invalid_count = int(np.sum(~valid_stream))
        instrument_failure_streams_total += invalid_count
        conditions.append(
            {
                "error_family": family,
                "streams": streams,
                "seed": seed,
                "actual_l1": actual_l1,
                "actual_l2": actual_l2,
                "instrument_failure_streams": invalid_count,
                "failure_rate": invalid_count / streams,
                "failure_cp_upper_95": clopper_pearson_upper(invalid_count, streams),
            }
        )

        for record in policies:
            coordinates = policy_coordinates(record, p0)
            gain = float(record["proxy_gain"])
            true_gain = float(np.dot(record["policy"] - p0, proxy + errors))
            oracle_margin = max(
                gain - actual_l1 * coordinates["movement_linf"],
                gain - actual_l2 * coordinates["movement_l2"],
                gain - float(np.max(np.abs(errors))) * coordinates["movement_l1"],
            )
            margins = np.maximum.reduce(
                [
                    gain - envelopes["u1"] * coordinates["movement_linf"],
                    gain - envelopes["u2"] * coordinates["movement_l2"],
                    np.full_like(envelopes["u1"], gain - coordinates["movement_l1"]),
                ]
            )
            differences = np.diff(margins, axis=0)
            monotone_violations += int(np.sum(differences < -1e-12))
            positive = margins > 0
            first = np.zeros(streams, dtype=np.int64)
            has_crossed = np.any(positive, axis=0)
            first_indices = np.argmax(positive, axis=0)
            first[has_crossed] = np.asarray(checkpoints)[first_indices[has_crossed]]
            for stream_index in np.flatnonzero(has_crossed):
                start = first_indices[stream_index]
                if not np.all(positive[start:, stream_index]):
                    reversions += 1
            if true_gain <= 0:
                conditional_false_crossings += int(np.sum(has_crossed & valid_stream))
            predicted = predicted_crossing(
                gain,
                coordinates,
                actual_l1,
                actual_l2,
                checkpoints,
                float(envelopes["alpha_each"]),
            )
            crossing = summarize_first_crossings(first, checkpoints[-1])
            oracle_class = "oracle_certifiable" if oracle_margin > 0 else "structurally_uncertifiable"
            policy_rows.append(
                {
                    "error_family": family,
                    "policy_id": record["policy_id"],
                    "optimizer_family": record["family"],
                    "proxy_gain": gain,
                    "true_gain": true_gain,
                    "oracle_margin": oracle_margin,
                    "oracle_class": oracle_class,
                    "predicted_crossing_checkpoint": predicted,
                    **crossing,
                }
            )
            for checkpoint_index, checkpoint in enumerate(checkpoints):
                cdf_rows.append(
                    {
                        "error_family": family,
                        "policy_id": record["policy_id"],
                        "optimizer_family": record["family"],
                        "checkpoint": checkpoint,
                        "crossing_fraction_descriptive": float(np.mean(first > 0) if checkpoint == checkpoints[-1] else np.mean((first > 0) & (first <= checkpoint))),
                        "mean_margin": float(np.mean(margins[checkpoint_index])),
                    }
                )

    numeric = protocol["gates_numeric"]
    max_cp = max(row["failure_cp_upper_95"] for row in conditions)
    structural_consistency = all(
        (row["oracle_class"] == "oracle_certifiable") == (row["oracle_margin"] > 0)
        for row in policy_rows
    )
    top_spike = [
        row
        for row in policy_rows
        if row["error_family"] == "diffuse_low_error" and row["optimizer_family"] == "top_spike"
    ]
    top_spike_crossed = sum(row["crossed_streams"] for row in top_spike)
    gates = {
        "G1_simultaneous_instrument": {
            "pass": max_cp <= float(numeric["maximum_instrument_failure_cp_upper"]),
            "maximum_cp_upper": max_cp,
            "instrument_failure_streams_total": instrument_failure_streams_total,
        },
        "G2_monotone_dynamics": {
            "pass": monotone_violations == 0,
            "violations": monotone_violations,
        },
        "G3_conditional_soundness": {
            "pass": conditional_false_crossings == 0,
            "conditional_false_crossings": conditional_false_crossings,
        },
        "G4_oracle_consistency": {
            "pass": structural_consistency,
            "oracle_certifiable_policies": sum(
                row["oracle_class"] == "oracle_certifiable" for row in policy_rows
            ),
            "structurally_uncertifiable_policies": sum(
                row["oracle_class"] == "structurally_uncertifiable" for row in policy_rows
            ),
        },
        "G5_top_spike_liveness": {
            "pass": top_spike_crossed > 0,
            "crossed_streams_across_five_policies": top_spike_crossed,
            "possible_streams": streams * len(top_spike),
            "note": "Crossing count is a liveness check only; no fraction is a pass threshold.",
        },
        "G6_no_reversion": {"pass": reversions == 0, "reversions": reversions},
    }
    result = {
        "schema_version": "asmp8_dynamic_threshold_result_v0_4",
        "streams_per_error_family": streams,
        "checkpoints": checkpoints,
        "condition_count": len(conditions),
        "policy_condition_count": len(policy_rows),
        "gates": gates,
        "focus": {"diffuse_top_spike": top_spike},
        "claim_boundary": protocol["claim_boundary"],
    }
    return result, conditions, policy_rows, cdf_rows


def rows_csv(rows: Iterable[dict[str, Any]], fields: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()
