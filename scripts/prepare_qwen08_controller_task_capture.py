"""Prepare a sealed, hard-cap-only controller-task Qwen capture authorization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rsi_topology.godel_capture import canonical_json_bytes, runtime_environment, sha256_file, write_once_or_equal
from rsi_topology.qwen_controller_task_capture import (
    AUTH_SCHEMA,
    AUTH_STATUS,
    load_protocol,
    validate_prompt_manifest,
)


DEFAULT_PROTOCOL = ROOT / "protocols" / "qwen08_controller_task_capture_v0_1.json"
DEFAULT_MANIFEST = Path(
    r"C:\projects\HybridTRMLDT\ldt_trm_research_gym_v0_0_2\ldt_trm_research_gym\data\bridge\qwen08_controller_task_prompt_manifest_v0_1.json"
)
DEFAULT_WRAPPER = ROOT / "scripts" / "run_qwen_holonomy_jobobject.ps1"
DEFAULT_VALIDATION = ROOT / "artifacts" / "hard_cap_validation" / "qwen_holonomy_jobobject_v0_1" / "hard_cap_validation_receipt.json"
DEFAULT_CLEANUP = Path(r"C:\Users\patri\.codex\skills\hrm-trainer\scripts\post_run_memory_cleanup.ps1")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _validate_hard_cap_receipt(receipt: dict, *, wrapper: Path, cleanup: Path) -> None:
    if receipt.get("schema_version") != "qwen_holonomy_hard_cap_validation_v0_1" or receipt.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap validation receipt is not a pass")
    if receipt.get("wrapper", {}).get("sha256") != sha256_file(wrapper):
        raise ValueError("hard-cap validation wrapper hash mismatch")
    if receipt.get("cleanup", {}).get("sha256") != sha256_file(cleanup):
        raise ValueError("hard-cap validation cleanup hash mismatch")


def prepare(args: argparse.Namespace) -> dict:
    if not args.confirm_caps:
        raise ValueError("live capture authorization requires --confirm-caps")
    protocol = load_protocol(args.protocol)
    manifest = _load(args.prompt_manifest)
    validate_prompt_manifest(manifest, protocol=protocol)
    if sha256_file(args.prompt_manifest) != protocol["controller_study"]["prompt_manifest_file_sha256"]:
        raise ValueError("prompt manifest file hash differs from the registered protocol")
    study_config = Path(protocol["controller_study"]["root"]) / protocol["controller_study"]["config_path"]
    if not study_config.is_file() or sha256_file(study_config) != protocol["controller_study"]["config_file_sha256"]:
        raise ValueError("controller study config is missing or changed")
    parent_protocol = ROOT / protocol["parent_model_protocol"]["path"]
    if not parent_protocol.is_file() or sha256_file(parent_protocol) != protocol["parent_model_protocol"]["sha256"]:
        raise ValueError("parent model protocol is missing or changed")
    for path in (args.hard_cap_wrapper, args.cleanup_script, args.hard_cap_validation_receipt):
        if not path.is_file():
            raise FileNotFoundError(path)
    _validate_hard_cap_receipt(
        _load(args.hard_cap_validation_receipt),
        wrapper=args.hard_cap_wrapper,
        cleanup=args.cleanup_script,
    )
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    if dirty:
        raise ValueError("capture authorization requires a clean committed RSITopology worktree")
    remote_refs = subprocess.run(
        ["git", "branch", "-r", "--contains", commit], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    if not remote_refs:
        raise ValueError("capture authorization requires the implementation commit on a remote ref")
    capture_entrypoint = ROOT / "scripts" / "capture_qwen08_controller_tasks.py"
    sources = {
        "capture_entrypoint": capture_entrypoint,
        "prepare_entrypoint": Path(__file__).resolve(),
        "capture_contract": ROOT / "rsi_topology" / "qwen_controller_task_capture.py",
        "state_capture_contract": ROOT / "rsi_topology" / "qwen_state_capture.py",
    }
    caps = dict(protocol["resource_contract"])
    for non_cap in ("batch_size", "abort_is_valid", "local_uncapped_execution_prohibited"):
        caps.pop(non_cap, None)
    exact_command = [
        sys.executable,
        str(capture_entrypoint.resolve()),
        "--protocol",
        str(args.protocol.resolve()),
        "--prompt-manifest",
        str(args.prompt_manifest.resolve()),
        "--authorization",
        str(args.output.resolve()),
        "--output-dir",
        str(args.capture_output_dir.resolve()),
        "--batch-size",
        str(protocol["resource_contract"]["batch_size"]),
    ]
    authorization = {
        "schema_version": AUTH_SCHEMA,
        "status": AUTH_STATUS,
        "run_id": args.run_id,
        "protocol_sha256": sha256_file(args.protocol),
        "prompt_manifest_sha256": sha256_file(args.prompt_manifest),
        "prompt_manifest_semantic_sha256": manifest["manifest_semantic_sha256"],
        "study_config_sha256": protocol["controller_study"]["config_sha256"],
        "caps_confirmed_by_user": True,
        "hard_cap_validation_status": "passed",
        "implementation_commit": commit,
        "remote_refs_containing_commit": remote_refs.splitlines(),
        "environment_lock": runtime_environment(),
        "source_paths": {name: str(path.resolve()) for name, path in sorted(sources.items())},
        "source_sha256": {name: sha256_file(path) for name, path in sorted(sources.items())},
        "scientific_protocol": {"path": str(args.protocol.resolve()), "sha256": sha256_file(args.protocol), "protocol_id": protocol["protocol_id"]},
        "parent_model_protocol": {"path": str(parent_protocol.resolve()), "sha256": sha256_file(parent_protocol)},
        "controller_study_config": {"path": str(study_config.resolve()), "sha256": sha256_file(study_config), "semantic_sha256": protocol["controller_study"]["config_sha256"]},
        "hard_cap_validation_receipt": {"path": str(args.hard_cap_validation_receipt.resolve()), "sha256": sha256_file(args.hard_cap_validation_receipt)},
        "hard_cap_wrapper": {"path": str(args.hard_cap_wrapper.resolve()), "sha256": sha256_file(args.hard_cap_wrapper)},
        "cleanup_script": {"path": str(args.cleanup_script.resolve()), "sha256": sha256_file(args.cleanup_script)},
        "resource_caps": caps,
        "capture_contract": {
            **protocol["capture_contract"],
            "activation_sites": protocol["capture_contract"]["sites"],
        },
        "capture_parameters": {
            "output_dir": str(args.capture_output_dir.resolve()),
            "batch_size": int(protocol["resource_contract"]["batch_size"]),
            "quantization": protocol["capture_contract"]["quantization"],
        },
        "checkpoint_strategy": "one immutable application-half chunk group at a time; validate existing hashes before resume",
        "wrapper_output_dir": str((args.capture_output_dir.resolve() / "_wrapper")),
        "exact_inner_command": exact_command,
    }
    write_once_or_equal(args.output, canonical_json_bytes(authorization))
    return authorization


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    value.add_argument("--prompt-manifest", type=Path, default=DEFAULT_MANIFEST)
    value.add_argument("--hard-cap-wrapper", type=Path, default=DEFAULT_WRAPPER)
    value.add_argument("--hard-cap-validation-receipt", type=Path, default=DEFAULT_VALIDATION)
    value.add_argument("--cleanup-script", type=Path, default=DEFAULT_CLEANUP)
    value.add_argument("--capture-output-dir", type=Path, required=True)
    value.add_argument("--run-id", required=True)
    value.add_argument("--output", type=Path, required=True)
    value.add_argument("--confirm-caps", action="store_true")
    return value


if __name__ == "__main__":
    result = prepare(parser().parse_args())
    print(json.dumps(result, indent=2, sort_keys=True))
