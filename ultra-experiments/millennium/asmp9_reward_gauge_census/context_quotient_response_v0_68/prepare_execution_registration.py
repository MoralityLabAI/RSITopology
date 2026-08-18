"""Create a write-once v0.68.1 execution registration and authorization."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SPEC = importlib.util.spec_from_file_location(
    "asmp9_successor_design_v068", HERE / "successor_design.py"
)
assert SPEC and SPEC.loader
design = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(design)

DEFAULT_MODEL = Path(
    r"D:\Research_Engine\models\Qwen3.5\Qwen3.5-0.8B-Instruct"
)
DEFAULT_OUTPUT = Path(
    r"D:\Research_Engine\runs\asmp9_context_quotient_response_v0_68_1"
)
DEFAULT_WRAPPER = HERE / "prime" / "run_prime_guarded_v0_68.sh"
DEFAULT_CLEANUP = HERE / "prime" / "post_run_prime_v0_68.sh"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact(path: Path) -> dict:
    resolved = path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    return {"path": str(resolved), "sha256": sha256(resolved)}


def _write_once_or_equal(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def _git_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def prepare(args: argparse.Namespace) -> None:
    if args.phase != "construction" and args.construction_decision is None:
        raise ValueError("confirmation requires a construction decision")
    protocol_path = (HERE / "protocol_v0_68.json").resolve()
    amendment_path = (HERE / "protocol_amendment_v0_68_1.json").resolve()
    manifest_path = (HERE / "scenario_manifest_v0_68.json").resolve()
    validation_path = args.prereveal_validation.resolve()
    validation = _load(validation_path)
    if (
        validation.get("status") != "passed"
        or validation.get("outcomes_read") is not False
    ):
        raise ValueError("invalid prereveal validation")
    for name, path in (
        ("protocol", protocol_path),
        ("protocol_amendment", amendment_path),
        ("scenario_manifest", manifest_path),
    ):
        if validation[name]["sha256"] != sha256(path):
            raise ValueError(f"validation does not bind {name}")
    manifest = design.load_manifest(manifest_path)
    jobs = design.score_jobs(manifest, args.phase)
    phase_root = args.output_dir.resolve() / args.phase
    registration_path = phase_root / "registration.json"
    model_path = args.model.resolve()
    source_paths = [
        HERE / "response_quotient.py",
        HERE / "successor_design.py",
        HERE / "run_qwen_v068.py",
        HERE / "analyze_v068.py",
        HERE / "prepare_execution_registration.py",
        HERE / "validate_prereveal_v068.py",
        HERE / "protocol_amendment_v0_68_1.json",
        HERE / "SCIENTIFIC_PROTOCOL_AMENDMENT_v0_68_1.md",
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
    registration = {
        "schema_version": (
            "asmp9_context_quotient_execution_registration_v0_68_1"
        ),
        "status": "registered_prereveal",
        "phase": args.phase,
        "run_id": f"asmp9-context-quotient-v0681-{args.phase}",
        "git_commit_before_registration": _git_commit(),
        "protocol": _artifact(protocol_path),
        "protocol_amendment": _artifact(amendment_path),
        "scenario_manifest": _artifact(manifest_path),
        "prereveal_validation": _artifact(validation_path),
        "source_files": [_artifact(path) for path in source_paths],
        "model_path": str(model_path),
        "model_files": [_artifact(path) for path in model_paths],
        "environment": validation["environment"],
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
        "resource_contract": {
            "memory_mb": 8192,
            "minimum_free_memory_mb": 12288,
            "cpu_percent": 50,
            "io_mb_s": 50,
            "gpu_allowance_mb": 4096,
            "timeout_seconds": 3600,
            "swap_bytes": 0,
            "batch_size": 1,
            "max_prompt_tokens": 768,
            "checkpoint_every_records": 1,
        },
        "outcomes_read": False,
    }
    if args.phase == "confirmation":
        decision_path = args.construction_decision.resolve()
        decision = _load(decision_path)
        if not decision.get("local_confirmation_authorized", False):
            raise ValueError("construction decision does not authorize confirmation")
        registration["construction_decision"] = _artifact(decision_path)
        registration["global_lane_authorized"] = bool(
            decision.get("global_confirmation_authorized", False)
        )
        if registration["global_lane_authorized"]:
            registration["construction_specificity_intersection"] = decision[
                "construction_specificity_intersection"
            ]
    _write_once_or_equal(
        registration_path, design.canonical_json_bytes(registration)
    )

    result_dir = phase_root / "result"
    analysis_dir = phase_root / "analysis"
    command = [
        sys.executable,
        str((HERE / "run_qwen_v068.py").resolve()),
        "--registration",
        str(registration_path.resolve()),
        "--output-dir",
        str(result_dir.resolve()),
    ]
    authorization = {
        "schema_version": "asmp9_context_quotient_authorization_v0_68_1",
        "run_id": registration["run_id"],
        "phase": args.phase,
        "exact_inner_command": command,
        "wrapper_output_dir": str((phase_root / "_wrapper").resolve()),
        "capture_parameters": {
            "result_dir": str(result_dir.resolve()),
            "analysis_dir": str(analysis_dir.resolve()),
        },
        "resource_caps": registration["resource_contract"],
        "hard_cap_wrapper": _artifact(args.wrapper.resolve()),
        "cleanup_script": _artifact(args.cleanup.resolve()),
        "registration": _artifact(registration_path),
    }
    authorization_path = phase_root / "authorization.json"
    _write_once_or_equal(
        authorization_path, design.canonical_json_bytes(authorization)
    )
    print(
        json.dumps(
            {
                "status": "prepared",
                "phase": args.phase,
                "registration": str(registration_path),
                "registration_sha256": sha256(registration_path),
                "authorization": str(authorization_path),
                "authorization_sha256": sha256(authorization_path),
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--phase",
        choices=("construction", "confirmation"),
        required=True,
    )
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--prereveal-validation", type=Path, required=True)
    parser.add_argument("--wrapper", type=Path, default=DEFAULT_WRAPPER)
    parser.add_argument("--cleanup", type=Path, default=DEFAULT_CLEANUP)
    parser.add_argument("--construction-decision", type=Path)
    prepare(parser.parse_args())


if __name__ == "__main__":
    main()
