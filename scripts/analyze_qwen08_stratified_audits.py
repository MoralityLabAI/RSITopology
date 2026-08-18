"""Analyze stratified Qwen completion receipts without outcome labels."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_qwen08_stratified_audits as runner  # noqa: E402


RESULT_SCHEMA = "qwen08_stratified_audit_analysis_v0_1"


def atomic_json(path: Path, value: Any) -> None:
    runner.atomic_json(path, value)


def load_records(records_dir: Path) -> list[dict[str, Any]]:
    records = [
        json.loads(path.read_text(encoding="utf-8-sig"))
        for path in sorted(records_dir.glob("*.json"))
    ]
    for expected_index, record in enumerate(records):
        if int(record["global_index"]) != expected_index:
            raise ValueError("records are not contiguous from global index zero")
        recorded_hash = record["record_sha256"]
        payload = {key: value for key, value in record.items() if key != "record_sha256"}
        if runner.sha256_bytes(runner.canonical_bytes(payload)) != recorded_hash:
            raise ValueError(f"record hash mismatch at index {expected_index}")
    return records


def population_stats(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {
            "count": 0,
            "mean": None,
            "variance": None,
            "sd": None,
            "minimum": None,
            "maximum": None,
        }
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return {
        "count": len(values),
        "mean": mean,
        "variance": variance,
        "sd": math.sqrt(max(0.0, variance)),
        "minimum": min(values),
        "maximum": max(values),
    }


def token_signature(record: dict[str, Any]) -> str:
    return json.dumps(
        {
            "content": record.get("content"),
            "tokens": record.get("tokens"),
            "stop": record.get("stop"),
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def analyze(
    *,
    manifest: dict[str, Any],
    plan: dict[str, Any],
    records: list[dict[str, Any]],
    probability_tolerance: float,
    liveness_variance_floor: float,
) -> dict[str, Any]:
    expected_items = list(plan["items"])
    plan_binding_failures: list[int] = []
    for index, record in enumerate(records):
        if index >= len(expected_items):
            plan_binding_failures.append(index)
            continue
        if record["plan_item_sha256"] != expected_items[index]["plan_item_sha256"]:
            plan_binding_failures.append(index)

    by_row: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_row[str(record["row_id"])].append(record)

    census_rows = {
        str(row["row_id"]): row for row in manifest["rows"]
    }
    census_failures: list[str] = []
    maximum_census_probability_range = 0.0
    for row_id in census_rows:
        row_records = [
            record
            for record in by_row.get(row_id, [])
            if record["phase"] == "census_crossover"
        ]
        if len(row_records) != 4:
            census_failures.append(f"{row_id}:count={len(row_records)}")
            continue
        signatures = {token_signature(record) for record in row_records}
        probabilities = [
            float(record["probability"])
            for record in row_records
            if record.get("probability") is not None
        ]
        if len(signatures) != 1:
            census_failures.append(f"{row_id}:token_mismatch")
        if len(probabilities) != 4:
            census_failures.append(f"{row_id}:probability_missing")
        else:
            probability_range = max(probabilities) - min(probabilities)
            maximum_census_probability_range = max(
                maximum_census_probability_range, probability_range
            )
            if probability_range > probability_tolerance:
                census_failures.append(
                    f"{row_id}:probability_range={probability_range}"
                )

    stability_row_ids = {
        str(item["row_id"])
        for item in expected_items
        if item["phase"] == "repeat_cached"
    }
    repeat_failures: list[str] = []
    maximum_repeat_probability_range = 0.0
    repeat_prompt_stats: dict[str, Any] = {}
    expected_repeat_count = int(plan["stability_repeats_per_epoch"]) * 2
    for row_id in sorted(stability_row_ids):
        row_records = [
            record
            for record in by_row.get(row_id, [])
            if record["phase"] == "repeat_cached"
        ]
        signatures = {token_signature(record) for record in row_records}
        probabilities = [
            float(record["probability"])
            for record in row_records
            if record.get("probability") is not None
        ]
        stats = population_stats(probabilities)
        repeat_prompt_stats[row_id] = stats
        if len(row_records) != expected_repeat_count:
            repeat_failures.append(f"{row_id}:count={len(row_records)}")
        if len(signatures) != 1:
            repeat_failures.append(f"{row_id}:token_mismatch")
        if len(probabilities) != expected_repeat_count:
            repeat_failures.append(f"{row_id}:probability_missing")
        elif probabilities:
            probability_range = max(probabilities) - min(probabilities)
            maximum_repeat_probability_range = max(
                maximum_repeat_probability_range, probability_range
            )
            if probability_range > probability_tolerance:
                repeat_failures.append(
                    f"{row_id}:probability_range={probability_range}"
                )

    reference_records = [
        record
        for record in records
        if record["phase"] == "census_crossover"
        and int(record["planned_epoch"]) == 0
        and record["pair_order"] == "uncached_then_cached:first"
    ]
    strata: dict[str, list[float]] = defaultdict(list)
    applications: dict[str, list[float]] = defaultdict(list)
    for record in reference_records:
        if record.get("probability") is None:
            continue
        probability = float(record["probability"])
        stratum = f"{record['application']}::{record['geometry_half']}"
        strata[stratum].append(probability)
        applications[str(record["application"])].append(probability)
    stratum_stats = {
        key: population_stats(values) for key, values in sorted(strata.items())
    }
    application_stats = {
        key: population_stats(values)
        for key, values in sorted(applications.items())
    }
    liveness_failures = [
        key
        for key, stats in stratum_stats.items()
        if stats["count"] != 32
        or stats["variance"] is None
        or float(stats["variance"]) <= liveness_variance_floor
    ]
    expected_strata = len(manifest["applications"]) * 2
    if len(stratum_stats) != expected_strata:
        liveness_failures.append(
            f"stratum_count={len(stratum_stats)};expected={expected_strata}"
        )

    sessions_by_epoch: dict[int, set[int]] = defaultdict(set)
    for record in records:
        sessions_by_epoch[int(record["planned_epoch"])].add(
            int(record["server_session"])
        )
    session_integrity_failures = [
        f"epoch={epoch}:sessions={sorted(sessions_by_epoch.get(epoch, set()))}"
        for epoch in range(int(plan["planned_epoch_count"]))
        if len(sessions_by_epoch.get(epoch, set())) != 1
    ]

    gates = {
        "P0_plan_and_session_integrity": {
            "status": (
                "pass"
                if not plan_binding_failures and not session_integrity_failures
                else "fail"
            ),
            "plan_binding_failures": plan_binding_failures,
            "session_integrity_failures": session_integrity_failures,
        },
        "C0_full_census_and_cache_order_invariance": {
            "status": "pass" if not census_failures else "fail",
            "failure_count": len(census_failures),
            "failures": census_failures,
            "maximum_probability_range": maximum_census_probability_range,
            "registered_tolerance": probability_tolerance,
        },
        "R0_restart_and_repeat_stability": {
            "status": "pass" if not repeat_failures else "fail",
            "failure_count": len(repeat_failures),
            "failures": repeat_failures,
            "maximum_probability_range": maximum_repeat_probability_range,
            "registered_tolerance": probability_tolerance,
        },
        "L0_proxy_liveness": {
            "status": "pass" if not liveness_failures else "fail",
            "failures": liveness_failures,
            "registered_variance_floor": liveness_variance_floor,
        },
    }
    overall_status = (
        "measurement_instrument_pass"
        if all(gate["status"] == "pass" for gate in gates.values())
        else "measurement_instrument_not_established"
    )
    return {
        "schema_version": RESULT_SCHEMA,
        "status": overall_status,
        "record_count": len(records),
        "record_target": int(plan["item_count"]),
        "unique_prompt_count": len(by_row),
        "gates": gates,
        "application_descriptives": application_stats,
        "stratum_descriptives": stratum_stats,
        "repeat_prompt_descriptives": repeat_prompt_stats,
        "claim_boundary": (
            "The result concerns measurement coverage and invariance only. "
            "The manifest supplies no outcome labels, so no correctness, "
            "calibration, oversight, Goodhart, or recursive-improvement claim is available."
        ),
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# Qwen0.8B stratified completion-measurement report",
        "",
        f"Status: `{result['status']}`",
        "",
        f"- Records: {result['record_count']} / {result['record_target']}",
        f"- Unique prompts: {result['unique_prompt_count']}",
        "",
        "## Gates",
        "",
    ]
    for name, gate in result["gates"].items():
        lines.append(f"- `{name}`: **{gate['status']}**")
    lines.extend(
        [
            "",
            "## Application descriptives",
            "",
            "| Application | n | Mean top-token probability | SD |",
            "|---|---:|---:|---:|",
        ]
    )
    for application, stats in result["application_descriptives"].items():
        lines.append(
            f"| {application} | {stats['count']} | "
            f"{float(stats['mean']):.6f} | {float(stats['sd']):.6f} |"
        )
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            result["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    manifest = runner.load_manifest(args.prompt_manifest)
    plan = json.loads(args.plan.read_text(encoding="utf-8-sig"))
    records = load_records(args.records_dir)
    result = analyze(
        manifest=manifest,
        plan=plan,
        records=records,
        probability_tolerance=args.probability_tolerance,
        liveness_variance_floor=args.liveness_variance_floor,
    )
    atomic_json(args.output_json, result)
    args.output_report.write_text(render_report(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-manifest", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--records-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-report", type=Path, required=True)
    parser.add_argument("--probability-tolerance", type=float, default=1e-6)
    parser.add_argument("--liveness-variance-floor", type=float, default=1e-8)
    return parser.parse_args(argv)


if __name__ == "__main__":
    run(parse_args())
