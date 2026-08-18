"""Independent post-run audit for ASMP-9 v0.82.

This file deliberately does not import the registered scorer, analyzer, or
transport-gate module.  It recomputes the registered statistics from JSONL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--transport-analysis", type=Path, required=True)
    parser.add_argument("--wrapper-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    registration = load(args.registration)
    protocol = load(Path(registration["protocol"]["path"]))
    manifest = load(Path(registration["scenario_manifest"]["path"]))
    records = [
        json.loads(line)
        for line in args.records.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(records) != 528 or len({row["record_id"] for row in records}) != 528:
        raise ValueError("record universe is not exactly 528 unique IDs")

    confirmation_ids = {
        row["scenario_id"] for row in manifest["rows"] if row["split"] == "confirmation"
    }
    if len(confirmation_ids) != 12 or {row["scenario_id"] for row in records} != confirmation_ids:
        raise ValueError("executed scenario universe differs from manifest")

    repeats: dict[str, list[dict]] = defaultdict(list)
    max_scale = 1.0
    for row in records:
        if not all(
            math.isfinite(float(row[field]))
            for field in ("logp_a", "logp_b", "raw_log_odds_a_over_b")
        ):
            raise ValueError("nonfinite score")
        if float(row["raw_log_odds_a_over_b"]) != float(row["logp_a"]) - float(row["logp_b"]):
            raise ValueError("score arithmetic mismatch")
        max_scale = max(max_scale, abs(float(row["logp_a"])), abs(float(row["logp_b"])))
        repeats[str(row["semantic_id"])].append(row)

    canonical_scores = {}
    for semantic_id, pair in repeats.items():
        pair.sort(key=lambda row: int(row["repeat_index"]))
        if [int(row["repeat_index"]) for row in pair] != [0, 1]:
            raise ValueError("incomplete repeat pair")
        for field in (
            "logp_a",
            "logp_b",
            "raw_log_odds_a_over_b",
            "model_input_sha256",
            "prompt_token_count",
        ):
            if pair[0][field] != pair[1][field]:
                raise ValueError(f"repeat mismatch: {semantic_id} {field}")
        first = pair[0]
        score = float(first["raw_log_odds_a_over_b"])
        if int(first["display_order"]) == 1:
            score = -score
        canonical_scores[
            (
                str(first["scenario_id"]),
                str(first["arm"]),
                None if first["target"] is None else int(first["target"]),
                int(first["display_order"]),
            )
        ] = score

    epsilon = 1.0 / 64.0 + 32.0 * (2.0**-23) * max_scale
    vectors: dict[str, list[float]] = defaultdict(list)
    cells = []
    calibration = protocol["calibration"]
    common_lower = float(calibration["common_coefficient_interval_lower"])
    common_upper = float(calibration["common_coefficient_interval_upper"])
    for scenario_id in sorted(confirmation_ids):
        for target in (0, 1):
            direction = 1.0 if target == 0 else -1.0
            values = []
            for order in (0, 1):
                content = canonical_scores[(scenario_id, "content", target, order)]
                label = canonical_scores[(scenario_id, "label", target, order)]
                values.append(direction * (content - label))
            vectors[scenario_id].extend(values)
            cells.append(
                {
                    "scenario_id": scenario_id,
                    "target": target,
                    "values": values,
                    "intersects": min(values) - epsilon <= common_upper
                    and max(values) + epsilon >= common_lower,
                }
            )

    scenario_means = {key: mean(value) for key, value in vectors.items()}
    envelope_lower = float(calibration["prediction_envelope_lower"])
    envelope_upper = float(calibration["prediction_envelope_upper"])
    successes = sum(all(value > epsilon for value in vector) for vector in vectors.values())
    gates = {
        "N0": "pass",
        "I0": "pass",
        "L0": (
            "pass"
            if successes >= 10
            and median(min(vector) for vector in vectors.values()) > epsilon
            and mean(scenario_means.values()) > epsilon
            else "fail"
        ),
        "T0": (
            "pass"
            if sum(envelope_lower <= value <= envelope_upper for value in scenario_means.values()) >= 10
            else "fail"
        ),
        "G0": "pass" if all(cell["intersects"] for cell in cells) else "fail",
    }

    wrapper = load(args.wrapper_summary)
    cleanup = wrapper.get("cleanup") or {}
    runner = wrapper.get("runner") or {}
    analysis_phase = wrapper.get("analysis") or {}
    r0 = (
        int(runner.get("exit_code", -1)) == 0
        and int(analysis_phase.get("exit_code", -1)) == 0
        and cleanup.get("cleanup_passed") is True
        and not runner.get("abort_reasons")
        and not analysis_phase.get("abort_reasons")
    )
    gates["R0"] = "pass" if r0 else "fail"

    final = (
        "out_of_family_response_transport_established_on_frozen_registry"
        if all(value == "pass" for value in gates.values())
        else "out_of_family_response_transport_not_established"
    )
    registered_transport = load(args.transport_analysis)
    comparison = {
        "epsilon": epsilon,
        "scenario_means": scenario_means,
        "envelope_hits": sum(
            envelope_lower <= value <= envelope_upper
            for value in scenario_means.values()
        ),
        "intersection_hits": sum(cell["intersects"] for cell in cells),
        "maximum_absolute_error_from_construction_center": max(
            abs(value - float(calibration["scenario_mean_center"]))
            for value in scenario_means.values()
        ),
    }
    if comparison["envelope_hits"] != registered_transport["gates"]["T0"]["envelope_hits"]:
        raise ValueError("independent T0 differs from registered analyzer")
    if comparison["intersection_hits"] != registered_transport["gates"]["G0"]["intersection_hits"]:
        raise ValueError("independent G0 differs from registered analyzer")

    receipt = {
        "schema_version": "asmp9_out_of_family_independent_audit_v0_82",
        "status": "passed_independent_recomputation",
        "registration_sha256": sha256(args.registration),
        "records_sha256": sha256(args.records),
        "transport_analysis_sha256": sha256(args.transport_analysis),
        "wrapper_summary_sha256": sha256(args.wrapper_summary),
        "gates": gates,
        "final_decision": final,
        "recomputed": comparison,
        "wrapper_native_status": wrapper.get("status"),
        "system_wide_page_file_increase_mb": wrapper.get("page_file_increase_mb"),
        "claim_boundary": protocol["claim_boundary"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() and args.output.read_bytes() != canonical(receipt):
        raise FileExistsError("audit output differs")
    args.output.write_bytes(canonical(receipt))
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()

