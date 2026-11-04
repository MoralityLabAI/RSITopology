"""Assemble and analyze a completed ASMP-9 v0.67 split."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("bridge_core_v067", HERE / "bridge_core.py")
assert SPEC and SPEC.loader
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


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


def analyze(args: argparse.Namespace) -> None:
    registration_path = args.registration.resolve()
    registration = _load(registration_path)
    if registration["schema_version"] != "asmp9_physical_dynamic_bridge_registration_v0_67":
        raise ValueError("unexpected registration schema")
    result_dir = args.result_dir.resolve()
    completion = _load(result_dir / "completion_summary.json")
    if completion["status"] != "completed":
        raise ValueError("model split is not complete")
    if completion["registration_sha256"] != core.sha256_file(registration_path):
        raise ValueError("completion is bound to a different registration")
    manifest = core.load_manifest(Path(registration["scenario_manifest"]["path"]))
    expected_jobs = core.score_jobs(manifest, registration["phase"])
    expected_by_id = {job["record_id"]: job for job in expected_jobs}
    expected_ids = set(expected_by_id)
    records = []
    for path in sorted((result_dir / "work_units").glob("*.json")):
        record = _load(path)["record"]
        if record["record_id"] not in expected_by_id:
            raise ValueError(f"unregistered work unit: {record['record_id']}")
        core.validate_scored_record(record, expected_by_id[record["record_id"]])
        rendered_path = result_dir / "rendered_inputs" / (
            __import__("hashlib").sha256(
                record["record_id"].encode("utf-8")
            ).hexdigest()
            + ".txt"
        )
        if (
            not rendered_path.exists()
            or core.sha256_file(rendered_path) != record["model_input_sha256"]
        ):
            raise ValueError(
                f"rendered input hash mismatch: {record['record_id']}"
            )
        records.append(record)
    actual_ids = {record["record_id"] for record in records}
    if actual_ids != expected_ids or len(records) != len(expected_ids):
        raise ValueError("work-unit universe does not exactly match registration")
    records.sort(key=lambda item: item["record_id"])
    records_path = args.output_dir.resolve() / "records.jsonl"
    records_payload = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
        for row in records
    ).encode("utf-8")
    _write_once_or_equal(records_path, records_payload)
    if registration["phase"] == "construction":
        calibration = core.derive_construction_calibration(records)
    else:
        calibration_item = registration["calibration"]
        if core.sha256_file(Path(calibration_item["path"])) != calibration_item["sha256"]:
            raise ValueError("confirmation calibration hash mismatch")
        calibration = _load(Path(calibration_item["path"]))
    analysis = core.analyze_records(records, calibration)
    output = args.output_dir.resolve()
    calibration_path = output / "calibration.json"
    if registration["phase"] == "construction":
        _write_once_or_equal(
            calibration_path, core.canonical_json_bytes(calibration)
        )
    analysis_path = output / "analysis.json"
    _write_once_or_equal(analysis_path, core.canonical_json_bytes(analysis))
    receipt = {
        "schema_version": "asmp9_dynamic_bridge_analysis_receipt_v0_67",
        "phase": registration["phase"],
        "registration": {
            "path": str(registration_path),
            "sha256": core.sha256_file(registration_path),
        },
        "completion": {
            "path": str((result_dir / "completion_summary.json").resolve()),
            "sha256": core.sha256_file(result_dir / "completion_summary.json"),
        },
        "records": {
            "path": str(records_path),
            "sha256": core.sha256_file(records_path),
            "count": len(records),
        },
        "analysis": {
            "path": str(analysis_path),
            "sha256": core.sha256_file(analysis_path),
        },
    }
    if registration["phase"] == "construction":
        receipt["calibration"] = {
            "path": str(calibration_path),
            "sha256": core.sha256_file(calibration_path),
        }
    _write_once_or_equal(output / "analysis_receipt.json", core.canonical_json_bytes(receipt))
    print(json.dumps(receipt, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    analyze(parser.parse_args())


if __name__ == "__main__":
    main()
