"""Authorize the frozen CPU-only Qwen support-recovery diagnostic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal
from rsi_topology.qwen_support_recovery import load_protocol


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--analysis-output-dir", type=Path, required=True)
    parser.add_argument("--authorization-output", type=Path, required=True)
    parser.add_argument("--hard-cap-wrapper", type=Path, required=True)
    parser.add_argument("--hard-cap-validation-receipt", type=Path, required=True)
    parser.add_argument("--cleanup-script", type=Path, required=True)
    parser.add_argument("--memory-mb", type=int, required=True)
    parser.add_argument("--cpu-percent", type=int, required=True)
    parser.add_argument("--io-mb-s", type=int, required=True)
    parser.add_argument("--timeout-seconds", type=int, required=True)
    parser.add_argument("--checkpoint-every-seconds", type=int, required=True)
    parser.add_argument("--swap-bytes", type=int, required=True)
    parser.add_argument("--seed", type=int, default=2026071606)
    parser.add_argument("--confirm-caps", action="store_true")
    args = parser.parse_args()
    if not args.confirm_caps or args.swap_bytes != 0:
        raise ValueError("explicit caps and registered zero swap are required")
    if any(
        value <= 0
        for value in (
            args.memory_mb,
            args.cpu_percent,
            args.io_mb_s,
            args.timeout_seconds,
            args.checkpoint_every_seconds,
        )
    ):
        raise ValueError("resource caps must be positive")
    protocol_path = args.protocol.resolve()
    protocol = load_protocol(protocol_path)
    parent_path = (ROOT / protocol["parent_analysis_registration"]["path"]).resolve()
    if sha256_file(parent_path) != protocol["parent_analysis_registration"]["sha256"]:
        raise ValueError("parent analysis registration changed")
    parent = json.loads(parent_path.read_text(encoding="utf-8"))
    for state, entry in parent["state_capture_indices"].items():
        path = Path(entry["path"])
        if not path.is_file() or sha256_file(path) != entry["sha256"]:
            raise ValueError(f"state capture index changed: {state}")

    validation_path = args.hard_cap_validation_receipt.resolve()
    validation = json.loads(validation_path.read_text(encoding="utf-8-sig"))
    if validation.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap validation is not passed")
    wrapper = args.hard_cap_wrapper.resolve()
    if sha256_file(wrapper) != validation["wrapper"]["sha256"]:
        raise ValueError("validation receipt does not bind wrapper")

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    remote = subprocess.run(
        ["git", "branch", "-r", "--contains", commit],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not remote:
        raise ValueError("implementation commit must exist on a remote ref")
    entrypoint = ROOT / "scripts" / "run_qwen08_support_recovery.py"
    source_paths = {
        "entrypoint": entrypoint,
        "support_recovery": ROOT / "rsi_topology" / "qwen_support_recovery.py",
        "discovery": ROOT / "rsi_topology" / "discovery.py",
        "pair_input_validation": ROOT / "rsi_topology" / "qwen_geometry_analysis.py",
        "capture_contract": ROOT / "rsi_topology" / "qwen_state_capture.py",
    }
    output = args.analysis_output_dir.resolve()
    authorization = {
        "schema_version": "qwen_holonomy_geometry_analysis_authorization_v0_1",
        "status": "authorized_for_target_blind_cpu_support_recovery",
        "run_id": "qwen08-between-class-support-recovery-v01",
        "analysis_registration": {
            "path": str(protocol_path),
            "sha256": sha256_file(protocol_path),
        },
        "implementation_commit": commit,
        "remote_refs_containing_commit": remote.splitlines(),
        "source_paths": {key: str(path.resolve()) for key, path in source_paths.items()},
        "source_sha256": {key: sha256_file(path) for key, path in source_paths.items()},
        "hard_cap_validation_receipt": {
            "path": str(validation_path),
            "sha256": sha256_file(validation_path),
        },
        "hard_cap_wrapper": {"path": str(wrapper), "sha256": sha256_file(wrapper)},
        "cleanup_script": {
            "path": str(args.cleanup_script.resolve()),
            "sha256": sha256_file(args.cleanup_script),
        },
        "resource_caps": {
            "memory_mb": args.memory_mb,
            "cpu_percent": args.cpu_percent,
            "io_mb_s": args.io_mb_s,
            "timeout_seconds": args.timeout_seconds,
            "gpu_allowance_mb": 1,
            "checkpoint_every_seconds": args.checkpoint_every_seconds,
            "swap_bytes": args.swap_bytes,
        },
        "checkpoint_strategy": "one support-recovery analysis with one final write-once result",
        "wrapper_output_dir": str(output / "_wrapper"),
        "exact_inner_command": [
            str(Path(sys.executable).resolve()),
            str(entrypoint.resolve()),
            "--protocol",
            str(protocol_path),
            "--output-dir",
            str(output),
            "--seed",
            str(args.seed),
        ],
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
    }
    write_once_or_equal(args.authorization_output, canonical_json_bytes(authorization))
    print(json.dumps(authorization, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
