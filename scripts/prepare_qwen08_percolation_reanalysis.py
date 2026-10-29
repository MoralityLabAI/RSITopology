"""Authorize the bounded retrospective Qwen percolation reanalysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.confinement_experiments.common import (
    canonical_json_bytes,
    file_sha256,
    write_bytes_compare_or_fail,
)


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
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
    parser.add_argument("--confirm-caps", action="store_true")
    args = parser.parse_args()
    if not args.confirm_caps or args.swap_bytes != 0:
        raise ValueError("explicit caps and zero registered swap are required")
    protocol_path = args.protocol.resolve()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8-sig"))
    if protocol.get("protocol_id") != "qwen08_percolation_reanalysis_v0_1":
        raise ValueError("unexpected Qwen percolation protocol")
    registered = protocol["resource_caps"]
    supplied = {
        "memory_mb": args.memory_mb,
        "cpu_percent": args.cpu_percent,
        "io_mb_s": args.io_mb_s,
        "swap_bytes": args.swap_bytes,
    }
    if any(int(registered[key]) != value for key, value in supplied.items()):
        raise ValueError("supplied caps differ from frozen protocol")
    wrapper = args.hard_cap_wrapper.resolve()
    validation_path = args.hard_cap_validation_receipt.resolve()
    cleanup = args.cleanup_script.resolve()
    validation = json.loads(validation_path.read_text(encoding="utf-8-sig"))
    if validation.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap validation has not passed")
    if file_sha256(wrapper) != validation["wrapper"]["sha256"]:
        raise ValueError("hard-cap validation does not bind wrapper")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    remote = subprocess.run(
        ["git", "branch", "-r", "--contains", commit], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    if not remote:
        raise ValueError("implementation commit must exist on a remote ref")
    entrypoint = ROOT / "scripts" / "run_qwen08_percolation_reanalysis.py"
    sources = {
        "entrypoint": entrypoint,
        "qwen_reanalysis": ROOT / "rsi_topology" / "qwen_percolation_reanalysis.py",
        "percolation": ROOT / "rsi_topology" / "percolation.py",
        "bifiltration": ROOT / "rsi_topology" / "bifiltration.py",
        "rank1_w1": ROOT / "rsi_topology" / "rank1_w1.py",
    }
    output = args.output.resolve()
    command = [
        str(Path(sys.executable).resolve()),
        str(entrypoint.resolve()),
        "--protocol", str(protocol_path),
        "--output", str(output),
    ]
    authorization = {
        "schema_version": "qwen_holonomy_geometry_analysis_authorization_v0_1",
        "status": "authorized_for_cpu_only_retrospective_qwen_percolation_reanalysis",
        "run_id": "qwen08-percolation-reanalysis-v01",
        "protocol": {"path": str(protocol_path), "sha256": file_sha256(protocol_path)},
        "implementation_commit": commit,
        "remote_refs_containing_commit": remote.splitlines(),
        "environment_lock": {
            "python_executable": str(Path(sys.executable).resolve()),
            "python_version": sys.version,
            "platform": platform.platform(),
            "thread_environment": {
                "CUDA_VISIBLE_DEVICES": "", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"
            }
        },
        "source_paths": {key: str(path.resolve()) for key, path in sources.items()},
        "source_sha256": {key: file_sha256(path) for key, path in sources.items()},
        "hard_cap_validation_receipt": {"path": str(validation_path), "sha256": file_sha256(validation_path)},
        "hard_cap_wrapper": {"path": str(wrapper), "sha256": file_sha256(wrapper)},
        "cleanup_script": {"path": str(cleanup), "sha256": file_sha256(cleanup)},
        "resource_caps": {
            **supplied,
            "timeout_seconds": args.timeout_seconds,
            "gpu_allowance_mb": 1,
            "checkpoint_every_seconds": args.checkpoint_every_seconds
        },
        "checkpoint_strategy": "one write-once exact retrospective curve receipt",
        "wrapper_output_dir": str(output.parent / "_wrapper"),
        "exact_inner_command": command,
        "outcomes_consumed": False,
        "weight_mutation_performed": False
    }
    write_bytes_compare_or_fail(args.authorization_output, canonical_json_bytes(authorization))
    print(json.dumps(authorization, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
