"""Create the exact local v0.82 registration and authorization prereveal."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
V068 = HERE.parent / "context_quotient_response_v0_68"
BASE_REGISTRATION = (
    V068
    / "artifacts_v0_68_2_1_confirmation"
    / "registration_v0_68_2_1.json"
)
DEFAULT_RUN_ROOT = Path(
    r"D:\Research_Engine\runs\asmp9_out_of_family_transport_v0_82_20260801"
)


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


design = _module("asmp9_design_v068_register_v082", V068 / "successor_design.py")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact(path: Path) -> dict:
    value = path.resolve()
    return {"path": str(value), "sha256": _sha256(value)}


def _canonical(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    path.write_bytes(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    args = parser.parse_args()
    validation_path = HERE / "prereveal_validation_v0_82.json"
    if not validation_path.exists():
        raise FileNotFoundError("run validate_prereveal_v082.py first")
    validation = _load(validation_path)
    if validation.get("status") != "passed" or validation.get("outcomes_read") is not False:
        raise ValueError("prereveal validation is not outcome-free/pass")

    base = _load(BASE_REGISTRATION)
    manifest_path = HERE / "scenario_manifest_v0_82.json"
    manifest = design.load_manifest(manifest_path)
    jobs = design.score_jobs(manifest, "confirmation")
    protocol_path = HERE / "protocol_v0_82.json"
    resource_path = HERE / "RESOURCE_CONTRACT_v0_82.md"
    decision_path = HERE / "calibration_decision_v0_82.json"
    old_runner = V068 / "run_qwen_v068.py"
    old_design = V068 / "successor_design.py"
    old_core = HERE.parent / "physical_dynamic_bridge_v0_67" / "bridge_core.py"
    analyzer = HERE / "analyze_transport_v082.py"
    gate = HERE / "transport_gate.py"

    resource = dict(base["resource_contract"])
    resource["swap_policy"] = "system_wide_telemetry_only_v0_82"
    registration = {
        "schema_version": "asmp9_context_quotient_execution_registration_v0_68_1",
        "status": "registered_prereveal",
        "run_id": "asmp9-out-of-family-v082-local3050",
        "phase": "confirmation",
        "execution_contract_version": "local_windows_v0_68_2_1",
        "protocol": _artifact(protocol_path),
        "protocol_amendment": _artifact(resource_path),
        "scenario_manifest": _artifact(manifest_path),
        "prereveal_validation": _artifact(validation_path),
        "source_files": [
            _artifact(path)
            for path in (old_runner, old_design, old_core, analyzer, gate)
        ],
        "model_path": base["model_path"],
        "model_files": base["model_files"],
        "environment": validation["environment"],
        "tokenizer_contract": base["tokenizer_contract"],
        "job_list_sha256": hashlib.sha256(
            design.canonical_json_bytes(jobs)
        ).hexdigest(),
        "split_counts": {
            "scenarios": 12,
            "semantic_inputs": 264,
            "records": 528,
            "exact_repeats": 2,
        },
        "resource_contract": resource,
        "construction_decision": _artifact(decision_path),
        "global_lane_authorized": True,
        "construction_specificity_intersection": {
            "lower": 0.7343614199407966,
            "upper": 0.750013550256881,
        },
        "outcomes_read": False,
        "v082_scientific_protocol": _artifact(HERE / "PROTOCOL_v0_82.md"),
        "claim_boundary": _load(protocol_path)["claim_boundary"],
    }
    registration_path = HERE / "registration_v0_82.json"
    _write_once(registration_path, _canonical(registration))

    run_root = args.run_root.resolve()
    result_dir = run_root / "confirmation" / "result"
    analysis_dir = run_root / "confirmation" / "analysis"
    wrapper_dir = run_root / "confirmation" / "_wrapper"
    wrapper = V068 / "windows" / "run_windows_guarded_v0_68_2.ps1"
    cleanup = V068 / "windows" / "post_run_windows_v0_68_2.ps1"
    authorization = {
        "schema_version": "asmp9_context_quotient_authorization_v0_68_2_windows",
        "run_id": registration["run_id"],
        "phase": "confirmation",
        "exact_runner_command": [
            sys.executable,
            str(old_runner.resolve()),
            "--registration",
            str(registration_path.resolve()),
            "--output-dir",
            str(result_dir),
        ],
        "exact_analysis_command": [
            sys.executable,
            str(analyzer.resolve()),
            "--registration",
            str(registration_path.resolve()),
            "--result-dir",
            str(result_dir),
            "--output-dir",
            str(analysis_dir),
        ],
        "wrapper_output_dir": str(wrapper_dir),
        "capture_parameters": {
            "result_dir": str(result_dir),
            "analysis_dir": str(analysis_dir),
        },
        "resource_caps": resource,
        "hard_cap_wrapper": _artifact(wrapper),
        "cleanup_script": _artifact(cleanup),
        "registration": _artifact(registration_path),
    }
    authorization_path = HERE / "authorization_v0_82.json"
    _write_once(authorization_path, _canonical(authorization))
    print(
        json.dumps(
            {
                "registration": str(registration_path),
                "registration_sha256": _sha256(registration_path),
                "authorization": str(authorization_path),
                "authorization_sha256": _sha256(authorization_path),
                "job_count": len(jobs),
                "outcomes_read": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

