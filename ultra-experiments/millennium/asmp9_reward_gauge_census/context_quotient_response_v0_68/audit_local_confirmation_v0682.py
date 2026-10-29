"""Independent post-run audit for the ASMP-9 v0.68.2.1 confirmation.

This deliberately rederives the registered local/global gates from the sealed
JSONL records without importing the execution runner or frozen analyzer.
It is an audit of one finite registry, not a second statistical analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median


ARMS_UNTARGETED = ("baseline", "balanced", "balanced_washout")
ARMS_TARGETED = ("content", "content_washout", "label", "repeated_content")
ORDERS = (0, 1)
TARGETS = (0, 1)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSONL line {line_number}") from error
    return rows


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    run_root = args.run_root.resolve()
    confirmation = run_root / "confirmation"
    registration_path = confirmation / "registration.json"
    authorization_path = confirmation / "authorization.json"
    result_dir = confirmation / "result"
    analysis_dir = confirmation / "analysis"
    records_path = analysis_dir / "records.jsonl"
    analysis_path = analysis_dir / "analysis.json"
    decision_path = analysis_dir / "decision.json"
    completion_path = result_dir / "completion_summary.json"

    registration = load_json(registration_path)
    authorization = load_json(authorization_path)
    completion = load_json(completion_path)
    frozen_analysis = load_json(analysis_path)
    frozen_decision = load_json(decision_path)
    records = load_jsonl(records_path)

    registration_hash = sha256(registration_path)
    if authorization["registration"]["sha256"] != registration_hash:
        raise ValueError("authorization does not bind registration")
    if completion["registration_sha256"] != registration_hash:
        raise ValueError("completion does not bind registration")
    if completion["status"] != "completed":
        raise ValueError("confirmation did not complete")

    source_hash_failures = []
    for entry in registration["source_files"]:
        path = Path(entry["path"])
        actual = sha256(path) if path.is_file() else None
        if actual != entry["sha256"]:
            source_hash_failures.append(
                {"path": str(path), "expected": entry["sha256"], "actual": actual}
            )
    model_hash_failures = []
    for entry in registration["model_files"]:
        path = Path(entry["path"])
        actual = sha256(path) if path.is_file() else None
        if actual != entry["sha256"]:
            model_hash_failures.append(
                {"path": str(path), "expected": entry["sha256"], "actual": actual}
            )
    if source_hash_failures or model_hash_failures:
        raise ValueError("registered source or model bytes changed")

    if len(records) != 528:
        raise ValueError(f"expected 528 records, found {len(records)}")
    record_ids = [str(row["record_id"]) for row in records]
    if len(set(record_ids)) != 528:
        raise ValueError("record IDs are not unique")

    scenarios = sorted({str(row["scenario_id"]) for row in records})
    if len(scenarios) != 12:
        raise ValueError("expected 12 confirmation scenarios")

    expected_semantic_keys = set()
    for scenario in scenarios:
        for arm in ARMS_UNTARGETED:
            for order in ORDERS:
                expected_semantic_keys.add((scenario, arm, None, order))
        for arm in ARMS_TARGETED:
            for target in TARGETS:
                for order in ORDERS:
                    expected_semantic_keys.add((scenario, arm, target, order))
    if len(expected_semantic_keys) != 264:
        raise AssertionError("internal semantic-universe error")

    groups: dict[tuple[str, str, int | None, int], list[dict]] = defaultdict(list)
    max_logp_scale = 1.0
    for row in records:
        key = (
            str(row["scenario_id"]),
            str(row["arm"]),
            None if row["target"] is None else int(row["target"]),
            int(row["display_order"]),
        )
        if key not in expected_semantic_keys:
            raise ValueError(f"unregistered semantic key: {key}")
        for field in ("logp_a", "logp_b", "raw_log_odds_a_over_b"):
            value = float(row[field])
            if not math.isfinite(value):
                raise ValueError(f"nonfinite {field}: {row['record_id']}")
        if not close(
            float(row["logp_a"]) - float(row["logp_b"]),
            float(row["raw_log_odds_a_over_b"]),
            tolerance=1e-7,
        ):
            raise ValueError(f"log-odds arithmetic mismatch: {row['record_id']}")
        max_logp_scale = max(
            max_logp_scale, abs(float(row["logp_a"])), abs(float(row["logp_b"]))
        )
        groups[key].append(row)
    if set(groups) != expected_semantic_keys:
        raise ValueError("semantic universe is incomplete")

    canonical: dict[tuple[str, str, int | None, int], float] = {}
    repeat_failures = []
    checked_fields = (
        "logp_a",
        "logp_b",
        "raw_log_odds_a_over_b",
        "model_input_sha256",
        "prompt_token_count",
    )
    for key, pair in groups.items():
        pair.sort(key=lambda row: int(row["repeat_index"]))
        if [int(row["repeat_index"]) for row in pair] != [0, 1]:
            raise ValueError(f"incomplete repeat pair: {key}")
        differences = [
            field for field in checked_fields if pair[0][field] != pair[1][field]
        ]
        if differences:
            repeat_failures.append({"semantic_key": key, "fields": differences})
        raw = float(pair[0]["raw_log_odds_a_over_b"])
        canonical[key] = raw if key[3] == 0 else -raw

    score_lattice_guard = 1.0 / 64.0
    analytic_float_guard = 32.0 * (2.0**-23) * max_logp_scale
    epsilon = score_lattice_guard + analytic_float_guard
    scenario_vectors: dict[str, list[float]] = defaultdict(list)
    cell_intervals = []
    confirmation_global_checks = []
    construction_interval = registration["construction_specificity_intersection"]

    for scenario in scenarios:
        for target in TARGETS:
            direction = 1.0 if target == 0 else -1.0
            specificity = []
            for order in ORDERS:
                content = canonical[(scenario, "content", target, order)]
                label = canonical[(scenario, "label", target, order)]
                specificity.append(direction * (content - label))
            scenario_vectors[scenario].extend(specificity)
            lower = min(specificity) - epsilon
            upper = max(specificity) + epsilon
            cell_intervals.append((lower, upper))
            confirmation_global_checks.append(
                {
                    "scenario_id": scenario,
                    "target": target,
                    "lower": lower,
                    "upper": upper,
                    "intersects_construction": (
                        lower <= float(construction_interval["upper"])
                        and upper >= float(construction_interval["lower"])
                    ),
                }
            )

    scenario_success = {
        scenario: all(value > epsilon for value in vector)
        for scenario, vector in scenario_vectors.items()
    }
    scenario_successes = sum(scenario_success.values())
    median_worst = median(min(vector) for vector in scenario_vectors.values())
    mean_scenario_mean = sum(
        sum(vector) / len(vector) for vector in scenario_vectors.values()
    ) / len(scenario_vectors)
    local_established = (
        not repeat_failures
        and scenario_successes >= 10
        and median_worst > epsilon
        and mean_scenario_mean > epsilon
    )
    global_intersection_lower = max(lower for lower, _ in cell_intervals)
    global_intersection_upper = min(upper for _, upper in cell_intervals)
    global_compatible = global_intersection_lower <= global_intersection_upper
    confirmation_global_established = local_established and all(
        item["intersects_construction"] for item in confirmation_global_checks
    )

    comparisons = {
        "record_count": len(records) == frozen_analysis["record_count"],
        "scenario_successes": (
            scenario_successes
            == frozen_analysis["local_specificity"]["scenario_successes"]
        ),
        "epsilon": close(epsilon, frozen_analysis["thresholds"]["endpoint_epsilon"]),
        "median_worst": close(
            median_worst, frozen_analysis["median_specificity_minimum_directed"]
        ),
        "mean_scenario_mean": close(
            mean_scenario_mean,
            frozen_analysis["local_specificity"][
                "mean_scenario_mean_specificity"
            ],
        ),
        "global_lower": close(
            global_intersection_lower,
            frozen_analysis["global_specificity"]["intersection_lower"],
        ),
        "global_upper": close(
            global_intersection_upper,
            frozen_analysis["global_specificity"]["intersection_upper"],
        ),
        "local_decision": (
            local_established == frozen_decision["local_result_established"]
        ),
        "global_decision": (
            confirmation_global_established
            == frozen_decision["global_result_established"]
        ),
        "analysis_hash": sha256(analysis_path)
        == frozen_decision["analysis_sha256"],
        "records_hash": sha256(records_path) == frozen_decision["records_sha256"],
    }
    if not all(comparisons.values()):
        raise ValueError(f"independent audit disagrees: {comparisons}")

    wrapper_summaries = list(
        (confirmation / "_wrapper" / "attempts").glob("*/wrapper_summary.json")
    )
    if len(wrapper_summaries) != 1:
        raise ValueError("expected exactly one repaired wrapper attempt")
    wrapper_path = wrapper_summaries[0]
    wrapper = load_json(wrapper_path)

    audit = {
        "schema_version": "asmp9_context_quotient_independent_audit_v0_68_2_1",
        "run_root": str(run_root),
        "registration_sha256": registration_hash,
        "authorization_sha256": sha256(authorization_path),
        "completion_sha256": sha256(completion_path),
        "records_sha256": sha256(records_path),
        "analysis_sha256": sha256(analysis_path),
        "decision_sha256": sha256(decision_path),
        "wrapper_summary_sha256": sha256(wrapper_path),
        "registered_source_hash_failures": source_hash_failures,
        "registered_model_hash_failures": model_hash_failures,
        "records": len(records),
        "semantic_inputs": len(groups),
        "scenarios": len(scenarios),
        "repeat_failures": repeat_failures,
        "epsilon": epsilon,
        "scenario_successes": scenario_successes,
        "scenario_trials": len(scenarios),
        "median_worst_direction_specificity": median_worst,
        "mean_scenario_mean_specificity": mean_scenario_mean,
        "confirmation_intersection": {
            "lower": global_intersection_lower,
            "upper": global_intersection_upper,
            "margin": global_intersection_upper - global_intersection_lower,
        },
        "construction_overlap_checks_passed": sum(
            item["intersects_construction"] for item in confirmation_global_checks
        ),
        "construction_overlap_checks_total": len(confirmation_global_checks),
        "local_result_rederived": local_established,
        "global_result_rederived": confirmation_global_established,
        "frozen_output_comparisons": comparisons,
        "execution_wrapper_status": wrapper["status"],
        "page_file_increase_mb": wrapper["page_file_increase_mb"],
        "cleanup_passed": wrapper["cleanup"]["cleanup_passed"],
        "scientific_readout": frozen_decision["decision"],
        "release_status": (
            "scientific_gates_rederived_but_execution_cleanup_invalid"
            if wrapper["status"] != "completed"
            else "scientific_and_execution_gates_rederived"
        ),
        "claim_boundary": (
            "Independent finite-registry arithmetic and integrity audit only. "
            "The execution wrapper's cleanup-invalid status is preserved; "
            "this audit does not waive or reinterpret the zero-swap contract."
        ),
    }
    payload = (
        json.dumps(audit, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() and args.output.read_bytes() != payload:
        raise FileExistsError(f"write-once audit differs: {args.output}")
    args.output.write_bytes(payload)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
