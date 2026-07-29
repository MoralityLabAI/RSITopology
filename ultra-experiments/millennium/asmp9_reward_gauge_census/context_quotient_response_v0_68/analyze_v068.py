"""Assemble, analyze, and authorize one completed ASMP-9 v0.68 split."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DESIGN_SPEC = importlib.util.spec_from_file_location(
    "asmp9_successor_design_v068", HERE / "successor_design.py"
)
assert DESIGN_SPEC and DESIGN_SPEC.loader
design = importlib.util.module_from_spec(DESIGN_SPEC)
DESIGN_SPEC.loader.exec_module(design)
RUNNER_SPEC = importlib.util.spec_from_file_location(
    "asmp9_runner_v068", HERE / "run_qwen_v068.py"
)
assert RUNNER_SPEC and RUNNER_SPEC.loader
runner = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(runner)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_once_or_equal(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    registration_path = args.registration.resolve()
    registration, _, manifest = runner._validate_registration(
        registration_path
    )
    completion_path = args.result_dir.resolve() / "completion_summary.json"
    completion = _load(completion_path)
    if (
        completion.get("status") != "completed"
        or completion.get("registration_sha256")
        != runner.sha256(registration_path)
    ):
        raise ValueError("completion does not bind this registration")
    jobs = design.score_jobs(manifest, registration["phase"])
    expected = {job["record_id"]: job for job in jobs}
    records = []
    for unit_path in sorted((args.result_dir / "work_units").glob("*.json")):
        record = _load(unit_path)["record"]
        if record["record_id"] not in expected:
            raise ValueError(f"unregistered work unit: {record['record_id']}")
        runner.validate_scored_record(record, expected[record["record_id"]])
        rendered = (
            args.result_dir
            / "rendered_inputs"
            / (
                hashlib.sha256(
                    record["record_id"].encode("utf-8")
                ).hexdigest()
                + ".txt"
            )
        )
        if (
            not rendered.exists()
            or runner.sha256(rendered) != record["model_input_sha256"]
        ):
            raise ValueError("rendered-input hash mismatch")
        records.append(record)
    if (
        len(records) != len(expected)
        or {record["record_id"] for record in records} != set(expected)
    ):
        raise ValueError("work-unit universe is incomplete")
    records.sort(key=lambda item: item["record_id"])
    output = args.output_dir.resolve()
    records_path = output / "records.jsonl"
    records_payload = "".join(
        json.dumps(
            record, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        + "\n"
        for record in records
    ).encode("utf-8")
    _write_once_or_equal(records_path, records_payload)
    analysis = design.analyze_records(
        records, manifest, registration["phase"]
    )
    analysis_path = output / "analysis.json"
    _write_once_or_equal(
        analysis_path, design.canonical_json_bytes(analysis)
    )

    local_established = (
        analysis["instrument"]["mechanical_repeat_status"] == "passed"
        and analysis["instrument"]["quotient_admission_status"] == "passed"
        and analysis["local_specificity"]["status"]
        == "local_response_family_established"
    )
    global_compatible = (
        local_established
        and analysis["global_specificity"]["status"]
        == "shared_effect_compatible"
    )
    decision = {
        "schema_version": "asmp9_context_quotient_decision_v0_68",
        "phase": registration["phase"],
        "registration_sha256": runner.sha256(registration_path),
        "records_sha256": runner.sha256(records_path),
        "analysis_sha256": runner.sha256(analysis_path),
        "claim_boundary": analysis["claim_boundary"],
    }
    if registration["phase"] == "construction":
        decision.update(
            {
                "local_confirmation_authorized": local_established,
                "global_confirmation_authorized": global_compatible,
                "construction_specificity_intersection": {
                    "lower": analysis["global_specificity"][
                        "intersection_lower"
                    ],
                    "upper": analysis["global_specificity"][
                        "intersection_upper"
                    ],
                },
                "decision": (
                    "local_and_global_confirmation_authorized"
                    if global_compatible
                    else "local_confirmation_authorized"
                    if local_established
                    else "confirmation_closed"
                ),
            }
        )
    else:
        global_established = False
        global_cell_checks = []
        if registration.get("global_lane_authorized", False):
            construction_interval = registration[
                "construction_specificity_intersection"
            ]
            epsilon = float(analysis["thresholds"]["endpoint_epsilon"])
            for cell in analysis["cells"]:
                values = cell["endpoints"]["specificity"]["by_order"]
                interval = {
                    "lower": min(values) - epsilon,
                    "upper": max(values) + epsilon,
                }
                intersects = (
                    interval["lower"]
                    <= float(construction_interval["upper"])
                    and interval["upper"]
                    >= float(construction_interval["lower"])
                )
                global_cell_checks.append(
                    {
                        "scenario_id": cell["scenario_id"],
                        "target": cell["target"],
                        "interval": interval,
                        "intersects_construction": intersects,
                    }
                )
            global_established = local_established and all(
                item["intersects_construction"] for item in global_cell_checks
            )
        decision.update(
            {
                "local_result_established": local_established,
                "global_result_established": global_established,
                "global_cell_checks": global_cell_checks,
                "decision": (
                    "confirmation_local_and_global_established"
                    if global_established
                    else "confirmation_local_established"
                    if local_established
                    else "confirmation_not_established"
                ),
            }
        )
    decision_path = output / "decision.json"
    _write_once_or_equal(
        decision_path, design.canonical_json_bytes(decision)
    )
    receipt = {
        "schema_version": "asmp9_context_quotient_analysis_receipt_v0_68",
        "phase": registration["phase"],
        "registration": {
            "path": str(registration_path),
            "sha256": runner.sha256(registration_path),
        },
        "completion": {
            "path": str(completion_path),
            "sha256": runner.sha256(completion_path),
        },
        "records": {
            "path": str(records_path),
            "sha256": runner.sha256(records_path),
            "count": len(records),
        },
        "analysis": {
            "path": str(analysis_path),
            "sha256": runner.sha256(analysis_path),
        },
        "decision": {
            "path": str(decision_path),
            "sha256": runner.sha256(decision_path),
        },
    }
    _write_once_or_equal(
        output / "analysis_receipt.json",
        design.canonical_json_bytes(receipt),
    )
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
