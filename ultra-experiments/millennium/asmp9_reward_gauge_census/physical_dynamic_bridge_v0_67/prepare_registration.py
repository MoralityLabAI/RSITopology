"""Prepare one write-once ASMP-9 v0.67 registration and authorization."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import platform
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SPEC = importlib.util.spec_from_file_location("bridge_core_v067", HERE / "bridge_core.py")
assert SPEC and SPEC.loader
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


DEFAULT_MODEL = Path(r"D:\Research_Engine\models\Qwen3.5\Qwen3.5-0.8B-Instruct")
DEFAULT_OUTPUT = Path(r"D:\Research_Engine\runs\asmp9_physical_dynamic_bridge_v0_67")
DEFAULT_WRAPPER = ROOT / "scripts" / "run_qwen_holonomy_jobobject.ps1"
DEFAULT_CLEANUP = Path(
    r"C:\Users\patri\.codex\skills\hrm-trainer\scripts\post_run_memory_cleanup.ps1"
)


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


def _artifact(path: Path) -> dict:
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    return {"path": str(path), "sha256": core.sha256_file(path)}


def prepare(args: argparse.Namespace) -> None:
    protocol_path = args.protocol.resolve()
    manifest_path = args.scenarios.resolve()
    protocol = _load(protocol_path)
    core.load_manifest(manifest_path)
    if protocol.get("status") != "registered_prereveal":
        raise ValueError(
            "refusing to prepare: protocol status must be registered_prereveal"
        )
    phase = args.phase
    phase_root = args.output_dir.resolve() / phase
    result_dir = phase_root / "result"
    analysis_dir = phase_root / "analysis"
    registration_path = phase_root / "registration.json"
    model_path = args.model.resolve()
    source_paths = [
        HERE / "bridge_core.py",
        HERE / "run_qwen_bridge.py",
        HERE / "analyze_bridge.py",
        HERE / "prepare_registration.py",
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
        "schema_version": "asmp9_physical_dynamic_bridge_registration_v0_67",
        "phase": phase,
        "run_id": f"asmp9-physical-dynamic-v067-{phase}",
        "protocol": _artifact(protocol_path),
        "scenario_manifest": _artifact(manifest_path),
        "source_files": [_artifact(path) for path in source_paths],
        "model_path": str(model_path),
        "model_files": [_artifact(path) for path in model_paths],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "packages": {
                name: importlib.metadata.version(name)
                for name in ("torch", "transformers", "accelerate", "safetensors")
            },
        },
        "split_counts": {
            "scenarios": 10,
            "records": 240,
            "display_orders": 2,
        },
        "outcomes_read": False,
    }
    if phase == "confirmation":
        if (
            args.construction_records is None
            or args.calibration is None
            or args.construction_receipt is None
        ):
            raise ValueError(
                "confirmation requires construction records, calibration, and "
                "the construction analysis receipt"
            )
        construction_receipt_path = args.construction_receipt.resolve()
        construction_receipt = _load(construction_receipt_path)
        if (
            construction_receipt.get("schema_version")
            != "asmp9_dynamic_bridge_analysis_receipt_v0_67"
            or construction_receipt.get("phase") != "construction"
        ):
            raise ValueError("invalid construction analysis receipt")
        records_path = args.construction_records.resolve()
        calibration_path = args.calibration.resolve()
        if (
            construction_receipt["records"]["sha256"]
            != core.sha256_file(records_path)
            or Path(construction_receipt["records"]["path"]).resolve() != records_path
        ):
            raise ValueError("construction receipt does not bind supplied records")
        if (
            construction_receipt["calibration"]["sha256"]
            != core.sha256_file(calibration_path)
            or Path(construction_receipt["calibration"]["path"]).resolve()
            != calibration_path
        ):
            raise ValueError("construction receipt does not bind supplied calibration")
        registration["construction_records"] = _artifact(
            records_path
        )
        registration["calibration"] = _artifact(calibration_path)
        registration["construction_analysis_receipt"] = _artifact(
            construction_receipt_path
        )
        calibration = _load(calibration_path)
        if calibration.get("schema_version") != "asmp9_dynamic_bridge_calibration_v0_67":
            raise ValueError("unexpected calibration schema")
        registration["frozen_thresholds"] = {
            key: calibration[key]
            for key in ("numeric_guard", "epsilon_measurement", "epsilon_restore")
        }
        registration["frozen_transition_model"] = calibration["transition_model"]
    _write_once_or_equal(registration_path, core.canonical_json_bytes(registration))

    command = [
        sys.executable,
        str((HERE / "run_qwen_bridge.py").resolve()),
        "--registration",
        str(registration_path.resolve()),
        "--output-dir",
        str(result_dir.resolve()),
    ]
    authorization = {
        "schema_version": "asmp9_physical_dynamic_bridge_authorization_v0_67",
        "run_id": registration["run_id"],
        "resource_caps": protocol["resource_contract"],
        "exact_inner_command": command,
        "wrapper_output_dir": str((phase_root / "_wrapper").resolve()),
        "capture_parameters": {
            "phase": phase,
            "result_dir": str(result_dir.resolve()),
            "analysis_dir": str(analysis_dir.resolve()),
        },
        "hard_cap_wrapper": _artifact(args.wrapper.resolve()),
        "cleanup_script": _artifact(args.cleanup.resolve()),
        "registration": _artifact(registration_path),
    }
    _write_once_or_equal(
        phase_root / "authorization.json", core.canonical_json_bytes(authorization)
    )
    print(
        json.dumps(
            {
                "status": "prepared",
                "phase": phase,
                "registration": str(registration_path),
                "registration_sha256": core.sha256_file(registration_path),
                "authorization": str(phase_root / "authorization.json"),
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("construction", "confirmation"), required=True)
    parser.add_argument(
        "--protocol", type=Path, default=HERE / "protocol_v0_67.json"
    )
    parser.add_argument(
        "--scenarios", type=Path, default=HERE / "scenario_manifest_v0_67.json"
    )
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--wrapper", type=Path, default=DEFAULT_WRAPPER)
    parser.add_argument("--cleanup", type=Path, default=DEFAULT_CLEANUP)
    parser.add_argument("--construction-records", type=Path)
    parser.add_argument("--calibration", type=Path)
    parser.add_argument("--construction-receipt", type=Path)
    prepare(parser.parse_args())


if __name__ == "__main__":
    main()
