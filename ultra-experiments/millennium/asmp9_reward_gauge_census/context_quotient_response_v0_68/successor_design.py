"""Prospective score universe and gate evaluator for ASMP-9 v0.68.

This module is outcome-blind infrastructure.  It does not load model weights.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from collections import defaultdict
from itertools import product
from pathlib import Path
from statistics import median
from typing import Mapping, Sequence


HERE = Path(__file__).resolve().parent
V067_CORE = HERE.parent / "physical_dynamic_bridge_v0_67" / "bridge_core.py"
CORE_SPEC = importlib.util.spec_from_file_location("bridge_core_v067", V067_CORE)
assert CORE_SPEC and CORE_SPEC.loader
v067 = importlib.util.module_from_spec(CORE_SPEC)
CORE_SPEC.loader.exec_module(v067)


SCHEMA = "asmp9_context_quotient_score_v0_68"
DISPLAY_ORDERS = (0, 1)
REPEATS = (0, 1)
UNTARGETED_ARMS = ("baseline", "balanced", "balanced_washout")
TARGETED_ARMS = ("content", "content_washout", "label", "repeated_content")
ENDPOINT_COEFFICIENTS = {
    "content_effect": {"content": 1, "balanced": -1},
    "label_effect": {"label": 1, "balanced": -1},
    "specificity": {"content": 1, "label": -1},
    "washout_effect": {"content_washout": 1, "balanced_washout": -1},
    "repeat_increment": {"repeated_content": 1, "content": -1},
}


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        + "\n"
    ).encode("utf-8")


def load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "asmp9_context_quotient_scenarios_v0_68":
        raise ValueError("unexpected scenario schema")
    rows = manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != 24:
        raise ValueError("manifest requires exactly 24 scenarios")
    ids = {row["scenario_id"] for row in rows}
    families = {row["family"] for row in rows}
    if len(ids) != 24 or len(families) != 12:
        raise ValueError("manifest IDs or families are not unique/balanced")
    for family in families:
        family_rows = [row for row in rows if row["family"] == family]
        if len(family_rows) != 2 or {
            row["split"] for row in family_rows
        } != {"construction", "confirmation"}:
            raise ValueError("each family requires one row in each split")
    return manifest


def score_jobs(manifest: Mapping, split: str) -> list[dict]:
    if split not in {"construction", "confirmation"}:
        raise ValueError("invalid split")
    jobs: list[dict] = []
    for row in manifest["rows"]:
        if row["split"] != split:
            continue
        arm_targets = [
            *((arm, None) for arm in UNTARGETED_ARMS),
            *((arm, target) for arm in TARGETED_ARMS for target in (0, 1)),
        ]
        for arm, target in arm_targets:
            for order in DISPLAY_ORDERS:
                messages = v067.build_messages(
                    manifest, row, arm, order, target
                )
                messages_hash = hashlib.sha256(
                    v067.canonical_json_bytes(messages)
                ).hexdigest()
                target_label = "none" if target is None else str(target)
                semantic_id = (
                    f"{split}::{row['scenario_id']}::{arm}::"
                    f"target-{target_label}::order-{order}"
                )
                for repeat in REPEATS:
                    jobs.append(
                        {
                            "schema_version": SCHEMA,
                            "record_id": f"{semantic_id}::repeat-{repeat}",
                            "semantic_id": semantic_id,
                            "repeat_index": repeat,
                            "scenario_id": row["scenario_id"],
                            "family": row["family"],
                            "split": split,
                            "arm": arm,
                            "target": target,
                            "display_order": order,
                            "messages": messages,
                            "messages_sha256": messages_hash,
                        }
                    )
    jobs.sort(key=lambda item: item["record_id"])
    if len(jobs) != 528:
        raise AssertionError(f"unexpected score job count: {len(jobs)}")
    return jobs


def validate_endpoint_coefficients() -> dict[str, bool]:
    return {
        name: sum(coefficients.values()) == 0
        for name, coefficients in ENDPOINT_COEFFICIENTS.items()
    }


def _canonical_score(record: Mapping) -> float:
    raw = float(record["raw_log_odds_a_over_b"])
    return raw if int(record["display_order"]) == 0 else -raw


def exact_scenario_sign_orbit(
    specificity_vectors: Sequence[Sequence[float]],
) -> dict[str, float | int]:
    """Exact sign-orbit sensitivity under scenario-level arm inversions.

    One sign is flipped for the complete target-by-order vector of each
    scenario.  The statistic is the mean across scenario means, which changes
    sign exactly when content and label are exchanged inside a scenario.

    This is not a p-value: the fixed scenario registry has no randomized
    content/label assignment and no registered symmetric superpopulation law.
    """

    if not specificity_vectors:
        raise ValueError("at least one scenario vector is required")
    if any(len(vector) != 4 for vector in specificity_vectors):
        raise ValueError("each scenario requires two targets by two orders")
    scenario_means = [
        sum(vector) / len(vector) for vector in specificity_vectors
    ]
    observed = sum(scenario_means) / len(scenario_means)
    exceedances = 0
    total = 0
    for signs in product((-1.0, 1.0), repeat=len(specificity_vectors)):
        statistic = sum(
            sign * scenario_mean
            for sign, scenario_mean in zip(
                signs, scenario_means, strict=True
            )
        ) / len(scenario_means)
        exceedances += int(statistic >= observed)
        total += 1
    return {
        "observed_mean_scenario_mean": observed,
        "exceedances": exceedances,
        "sign_orbit_size": total,
        "upper_tail_fraction": exceedances / total,
        "probability_interpretation": False,
        "consumed_by_gate": False,
    }


def exact_scenario_sign_flip_p(
    specificity_vectors: Sequence[Sequence[float]],
) -> dict[str, float | int]:
    """Deprecated compatibility alias; the returned value is not a p-value."""

    return exact_scenario_sign_orbit(specificity_vectors)


def analyze_records(
    records: Sequence[Mapping], manifest: Mapping, split: str
) -> dict:
    expected_jobs = score_jobs(manifest, split)
    expected = {job["record_id"]: job for job in expected_jobs}
    if len(records) != len(expected):
        raise ValueError("record count differs from registered universe")
    actual = {str(record["record_id"]): record for record in records}
    if len(actual) != len(records) or set(actual) != set(expected):
        raise ValueError("record ID universe differs from registered universe")

    mechanical_failures = []
    semantic_groups: dict[str, list[Mapping]] = defaultdict(list)
    max_logp_scale = 1.0
    for record_id, record in actual.items():
        job = expected[record_id]
        for field in (
            "semantic_id",
            "repeat_index",
            "scenario_id",
            "family",
            "split",
            "arm",
            "target",
            "display_order",
            "messages_sha256",
        ):
            if record.get(field) != job.get(field):
                raise ValueError(f"registered field mismatch: {record_id} {field}")
        for field in ("logp_a", "logp_b", "raw_log_odds_a_over_b"):
            value = float(record[field])
            if not math.isfinite(value):
                raise ValueError(f"nonfinite score: {record_id}")
        max_logp_scale = max(
            max_logp_scale,
            abs(float(record["logp_a"])),
            abs(float(record["logp_b"])),
        )
        semantic_groups[str(record["semantic_id"])].append(record)

    canonical: dict[tuple[str, str, int | None, int], float] = {}
    for semantic_id, pair in semantic_groups.items():
        pair.sort(key=lambda item: int(item["repeat_index"]))
        if [int(item["repeat_index"]) for item in pair] != [0, 1]:
            raise ValueError(f"incomplete repeat pair: {semantic_id}")
        checked_fields = (
            "logp_a",
            "logp_b",
            "raw_log_odds_a_over_b",
            "model_input_sha256",
            "prompt_token_count",
        )
        differences = [
            field
            for field in checked_fields
            if pair[0].get(field) != pair[1].get(field)
        ]
        if differences:
            mechanical_failures.append(
                {"semantic_id": semantic_id, "differing_fields": differences}
            )
        first = pair[0]
        key = (
            str(first["scenario_id"]),
            str(first["arm"]),
            None if first["target"] is None else int(first["target"]),
            int(first["display_order"]),
        )
        canonical[key] = _canonical_score(first)

    analytic_guard = 32.0 * (2.0**-23) * max_logp_scale
    score_lattice_guard = 1.0 / 64.0
    epsilon = score_lattice_guard + analytic_guard
    cells = []
    for scenario_id in sorted({key[0] for key in canonical}):
        family = next(
            row["family"]
            for row in manifest["rows"]
            if row["scenario_id"] == scenario_id
        )
        for target in (0, 1):
            direction = 1.0 if target == 0 else -1.0
            endpoint_values = defaultdict(list)
            for order in DISPLAY_ORDERS:
                value = lambda arm, arm_target: canonical[  # noqa: E731
                    (scenario_id, arm, arm_target, order)
                ]
                endpoint_values["content_effect"].append(
                    direction
                    * (value("content", target) - value("balanced", None))
                )
                endpoint_values["label_effect"].append(
                    direction
                    * (value("label", target) - value("balanced", None))
                )
                endpoint_values["specificity"].append(
                    direction
                    * (value("content", target) - value("label", target))
                )
                endpoint_values["washout_effect"].append(
                    direction
                    * (
                        value("content_washout", target)
                        - value("balanced_washout", None)
                    )
                )
                endpoint_values["repeat_increment"].append(
                    direction
                    * (
                        value("repeated_content", target)
                        - value("content", target)
                    )
                )
            cells.append(
                {
                    "scenario_id": scenario_id,
                    "family": family,
                    "target": target,
                    "endpoints": {
                        endpoint: {
                            "by_order": values,
                            "minimum_directed": min(values),
                            "maximum_directed": max(values),
                            "order_transportable_positive": min(values) > epsilon,
                            "order_transportable_negative": max(values) < -epsilon,
                        }
                        for endpoint, values in endpoint_values.items()
                    },
                }
            )

    scenario_success = {}
    scenario_vectors = {}
    for scenario_id in sorted({cell["scenario_id"] for cell in cells}):
        scenario_cells = [
            cell for cell in cells if cell["scenario_id"] == scenario_id
        ]
        vector = [
            value
            for cell in sorted(scenario_cells, key=lambda item: item["target"])
            for value in cell["endpoints"]["specificity"]["by_order"]
        ]
        scenario_vectors[scenario_id] = vector
        scenario_success[scenario_id] = all(
            value > epsilon for value in vector
        )
    successes = sum(scenario_success.values())
    scenario_means = [
        sum(scenario_vectors[key]) / len(scenario_vectors[key])
        for key in sorted(scenario_vectors)
    ]
    mean_scenario_mean = sum(scenario_means) / len(scenario_means)
    sign_orbit = exact_scenario_sign_orbit(
        [scenario_vectors[key] for key in sorted(scenario_vectors)]
    )
    specificity_intervals = [
        (
            cell["endpoints"]["specificity"]["minimum_directed"] - epsilon,
            cell["endpoints"]["specificity"]["maximum_directed"] + epsilon,
        )
        for cell in cells
    ]
    intersection_lower = max(item[0] for item in specificity_intervals)
    intersection_upper = min(item[1] for item in specificity_intervals)
    terminal_counts = {
        "restored": 0,
        "persistent": 0,
        "reversed": 0,
        "inconclusive": 0,
    }
    for cell in cells:
        values = cell["endpoints"]["washout_effect"]["by_order"]
        if max(abs(value) for value in values) <= epsilon:
            terminal_counts["restored"] += 1
        elif min(values) > epsilon:
            terminal_counts["persistent"] += 1
        elif max(values) < -epsilon:
            terminal_counts["reversed"] += 1
        else:
            terminal_counts["inconclusive"] += 1

    coefficient_gate = validate_endpoint_coefficients()
    return {
        "schema_version": "asmp9_context_quotient_analysis_v0_68_1",
        "split": split,
        "record_count": len(records),
        "scenario_count": len(scenario_success),
        "thresholds": {
            "analytic_float_guard": analytic_guard,
            "score_lattice_guard": score_lattice_guard,
            "endpoint_epsilon": epsilon,
            "required_scenario_successes": 10,
            "scenario_trials": 12,
            "descriptive_sign_orbit_size": 4096,
        },
        "instrument": {
            "mechanical_repeat_status": (
                "passed" if not mechanical_failures else "failed"
            ),
            "mechanical_failures": mechanical_failures,
            "quotient_admission_status": (
                "passed"
                if all(coefficient_gate.values())
                else "failed_nonzero_block_sum"
            ),
            "coefficient_admission": coefficient_gate,
        },
        "local_specificity": {
            "scenario_successes": successes,
            "scenario_trials": len(scenario_success),
            "mean_scenario_mean_specificity": mean_scenario_mean,
            "descriptive_sign_orbit": sign_orbit,
            "scenario_success_by_id": scenario_success,
            "status": (
                "local_response_family_established_on_frozen_registry"
                if not mechanical_failures
                and all(coefficient_gate.values())
                and successes >= 10
                and median(
                    min(vector) for vector in scenario_vectors.values()
                )
                > epsilon
                and mean_scenario_mean > epsilon
                else "local_response_family_not_established"
            ),
        },
        "global_specificity": {
            "intersection_lower": intersection_lower,
            "intersection_upper": intersection_upper,
            "intersection_margin": intersection_upper - intersection_lower,
            "status": (
                "shared_effect_compatible"
                if intersection_lower <= intersection_upper
                else "context_conditioning_required"
            ),
        },
        "terminal": {
            "counts": terminal_counts,
            "status": "descriptive_context_local",
        },
        "median_specificity_minimum_directed": median(
            min(vector) for vector in scenario_vectors.values()
        ),
        "cells": cells,
        "claim_boundary": (
            "Exact finite-registry nuisance-quotiented expressed response "
            "contrasts in one frozen model only; no random-sample inference, "
            "value, reward-orbit, or ASMP-9 resolution claim."
        ),
    }
