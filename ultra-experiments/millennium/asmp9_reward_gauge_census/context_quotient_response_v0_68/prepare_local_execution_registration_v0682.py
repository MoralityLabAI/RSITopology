"""Create the write-once local v0.68.2 confirmation registration."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DESIGN_SPEC = importlib.util.spec_from_file_location(
    "asmp9_successor_design_v068_local", HERE / "successor_design.py"
)
assert DESIGN_SPEC and DESIGN_SPEC.loader
design = importlib.util.module_from_spec(DESIGN_SPEC)
DESIGN_SPEC.loader.exec_module(design)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact(path: Path) -> dict:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return {"path": str(resolved), "sha256": sha256(resolved)}


def write_once_or_equal(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def git_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def gpu_probe() -> dict:
    command = [
        "nvidia-smi",
        "--query-gpu=name,uuid,driver_version,memory.total",
        "--format=csv,noheader,nounits",
    ]
    row = subprocess.check_output(command, text=True).strip().split(",")
    if len(row) != 4:
        raise ValueError("unexpected nvidia-smi result")
    return {
        "name": row[0].strip(),
        "uuid": row[1].strip(),
        "driver_version": row[2].strip(),
        "memory_total_mb": int(row[3].strip()),
    }


def prepare(args: argparse.Namespace) -> dict:
    paths = {
        "protocol": HERE / "protocol_v0_68.json",
        "protocol_amendment": HERE / "protocol_amendment_v0_68_1.json",
        "scenario_manifest": HERE / "scenario_manifest_v0_68.json",
        "execution_amendment": (
            HERE / "local_execution_resource_amendment_v0_68_2.json"
        ),
        "execution_amendment_text": (
            HERE / "LOCAL_EXECUTION_RESOURCE_AMENDMENT_v0_68_2.md"
        ),
    }
    validation_path = args.prereveal_validation.resolve()
    validation = load(validation_path)
    if validation.get("status") != "passed":
        raise ValueError("prereveal validation did not pass")
    if validation.get("outcomes_read") is not False:
        raise ValueError("prereveal validation records outcome access")
    for name in ("protocol", "protocol_amendment", "scenario_manifest"):
        if validation[name]["sha256"] != sha256(paths[name]):
            raise ValueError(f"validation does not bind {name}")

    amendment = load(paths["execution_amendment"])
    if amendment["status"] != "frozen_prereveal_execution_only":
        raise ValueError("local execution amendment is not frozen")
    for key, filename in (
        ("base_resource_plan", "EXECUTION_RESOURCE_PLAN_v0_68.md"),
        ("scientific_protocol", "protocol_v0_68.json"),
        ("scientific_amendment", "protocol_amendment_v0_68_1.json"),
    ):
        target = HERE / filename
        if amendment[key]["sha256"] != sha256(target):
            raise ValueError(f"execution amendment does not bind {filename}")

    decision_path = args.construction_decision.resolve()
    decision = load(decision_path)
    if not decision.get("local_confirmation_authorized", False):
        raise ValueError("construction does not authorize confirmation")

    model_path = args.model.resolve()
    manifest = design.load_manifest(paths["scenario_manifest"])
    jobs = design.score_jobs(manifest, "confirmation")
    if len(jobs) != 528:
        raise ValueError("confirmation job count changed")
    output_root = args.output_dir.resolve()
    phase_root = output_root / "confirmation"
    registration_path = phase_root / "registration.json"

    source_paths = [
        HERE / "response_quotient.py",
        HERE / "successor_design.py",
        HERE / "run_qwen_v068.py",
        HERE / "analyze_v068.py",
        HERE / "validate_prereveal_v068.py",
        HERE / "prepare_local_execution_registration_v0682.py",
        HERE / "windows" / "run_windows_guarded_v0_68_2.ps1",
        HERE / "windows" / "post_run_windows_v0_68_2.ps1",
        HERE / "smoke_windows_wrapper_v0682.ps1",
        HERE / "test_local_execution_contract_v0682.py",
        paths["execution_amendment"],
        paths["execution_amendment_text"],
        HERE.parent / "physical_dynamic_bridge_v0_67" / "bridge_core.py",
    ]
    model_paths = [
        model_path / "model.safetensors-00001-of-00001.safetensors",
        model_path / "model.safetensors",
        model_path / "config.json",
        model_path / "tokenizer.json",
        model_path / "tokenizer_config.json",
        model_path / "chat_template.jinja",
    ]
    gpu = gpu_probe()
    expected_gpu = amendment["host_class"]["gpu"]
    if gpu["name"] != expected_gpu:
        raise ValueError(f"GPU differs: {gpu['name']} != {expected_gpu}")
    if gpu["memory_total_mb"] < amendment["host_class"][
        "minimum_gpu_memory_mb"
    ]:
        raise ValueError("GPU memory is below the frozen local floor")

    registration = {
        "schema_version": (
            "asmp9_context_quotient_execution_registration_v0_68_1"
        ),
        "execution_contract_version": "local_windows_v0_68_2",
        "status": "registered_prereveal",
        "phase": "confirmation",
        "run_id": "asmp9-context-quotient-v0682-confirmation-local3050",
        "git_commit_before_registration": git_commit(),
        "protocol": artifact(paths["protocol"]),
        "protocol_amendment": artifact(paths["protocol_amendment"]),
        "scenario_manifest": artifact(paths["scenario_manifest"]),
        "execution_resource_amendment": artifact(
            paths["execution_amendment"]
        ),
        "execution_resource_amendment_text": artifact(
            paths["execution_amendment_text"]
        ),
        "prereveal_validation": artifact(validation_path),
        "source_files": [artifact(path) for path in source_paths],
        "model_path": str(model_path),
        "model_files": [artifact(path) for path in model_paths],
        "environment": {
            **validation["environment"],
            "os": platform.platform(),
            "gpu": gpu,
        },
        "tokenizer_contract": validation["tokenizer_contract"],
        "job_list_sha256": hashlib.sha256(
            design.canonical_json_bytes(jobs)
        ).hexdigest(),
        "split_counts": {
            "scenarios": 12,
            "semantic_inputs": 264,
            "records": 528,
            "exact_repeats": 2,
        },
        "resource_contract": amendment["resource_contract"],
        "construction_decision": artifact(decision_path),
        "global_lane_authorized": bool(
            decision.get("global_confirmation_authorized", False)
        ),
        "construction_specificity_intersection": decision.get(
            "construction_specificity_intersection"
        ),
        "outcomes_read": False,
    }
    write_once_or_equal(
        registration_path, design.canonical_json_bytes(registration)
    )

    result_dir = phase_root / "result"
    analysis_dir = phase_root / "analysis"
    runner_command = [
        sys.executable,
        str((HERE / "run_qwen_v068.py").resolve()),
        "--registration",
        str(registration_path.resolve()),
        "--output-dir",
        str(result_dir.resolve()),
    ]
    analysis_command = [
        sys.executable,
        str((HERE / "analyze_v068.py").resolve()),
        "--registration",
        str(registration_path.resolve()),
        "--result-dir",
        str(result_dir.resolve()),
        "--output-dir",
        str(analysis_dir.resolve()),
    ]
    wrapper = (HERE / "windows" / "run_windows_guarded_v0_68_2.ps1")
    cleanup = (HERE / "windows" / "post_run_windows_v0_68_2.ps1")
    authorization = {
        "schema_version": (
            "asmp9_context_quotient_authorization_v0_68_2_windows"
        ),
        "run_id": registration["run_id"],
        "phase": "confirmation",
        "exact_runner_command": runner_command,
        "exact_analysis_command": analysis_command,
        "wrapper_output_dir": str((phase_root / "_wrapper").resolve()),
        "capture_parameters": {
            "result_dir": str(result_dir.resolve()),
            "analysis_dir": str(analysis_dir.resolve()),
        },
        "resource_caps": registration["resource_contract"],
        "hard_cap_wrapper": artifact(wrapper),
        "cleanup_script": artifact(cleanup),
        "registration": artifact(registration_path),
    }
    authorization_path = phase_root / "authorization.json"
    write_once_or_equal(
        authorization_path, design.canonical_json_bytes(authorization)
    )
    return {
        "schema_version": (
            "asmp9_context_quotient_local_preparation_receipt_v0_68_2"
        ),
        "status": "prepared_prereveal",
        "outcomes_read": False,
        "git_commit": registration["git_commit_before_registration"],
        "registration": artifact(registration_path),
        "authorization": artifact(authorization_path),
        "prereveal_validation": artifact(validation_path),
        "gpu": gpu,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--prereveal-validation", type=Path, required=True)
    parser.add_argument("--construction-decision", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    value = prepare(args)
    write_once_or_equal(
        args.receipt.resolve(), design.canonical_json_bytes(value)
    )
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
