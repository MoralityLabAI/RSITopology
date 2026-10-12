"""Create a pushed-commit, hard-cap authorization for the rank-one reanalysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--protocol", type=Path, required=True)
    value.add_argument("--analysis-output-dir", type=Path, required=True)
    value.add_argument("--authorization-output", type=Path, required=True)
    value.add_argument("--hard-cap-wrapper", type=Path, required=True)
    value.add_argument("--hard-cap-validation-receipt", type=Path, required=True)
    value.add_argument("--cleanup-script", type=Path, required=True)
    value.add_argument("--memory-mb", type=int, required=True)
    value.add_argument("--cpu-percent", type=int, required=True)
    value.add_argument("--io-mb-s", type=int, required=True)
    value.add_argument("--timeout-seconds", type=int, required=True)
    value.add_argument("--checkpoint-every-seconds", type=int, required=True)
    value.add_argument("--swap-bytes", type=int, required=True)
    value.add_argument("--confirm-caps", action="store_true")
    return value


def main() -> None:
    args = parser().parse_args()
    if not args.confirm_caps or args.swap_bytes != 0:
        raise ValueError("explicit caps and zero registered swap are required")
    protocol = args.protocol.resolve()
    wrapper = args.hard_cap_wrapper.resolve()
    validation_path = args.hard_cap_validation_receipt.resolve()
    cleanup = args.cleanup_script.resolve()
    validation = json.loads(validation_path.read_text(encoding="utf-8-sig"))
    if validation.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap validation has not passed")
    if sha256_file(wrapper) != validation["wrapper"]["sha256"]:
        raise ValueError("hard-cap validation does not bind the wrapper")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    remote = subprocess.run(
        ["git", "branch", "-r", "--contains", commit], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    if not remote:
        raise ValueError("implementation commit must be present on a remote ref")
    entrypoint = ROOT / "scripts" / "run_qwen08_rank1_w1.py"
    sources = {
        "entrypoint": entrypoint,
        "rank1_w1": ROOT / "rsi_topology" / "rank1_w1.py",
        "qwen_geometry_analysis": ROOT / "rsi_topology" / "qwen_geometry_analysis.py",
        "godel_analysis": ROOT / "rsi_topology" / "godel_analysis.py",
    }
    command = [
        str(Path(sys.executable).resolve()),
        str(entrypoint.resolve()),
        "--protocol", str(protocol),
        "--output-dir", str(args.analysis_output_dir.resolve()),
    ]
    authorization = {
        "schema_version": "qwen_holonomy_geometry_analysis_authorization_v0_1",
        "status": "authorized_for_cpu_only_retrospective_rank1_w1_reanalysis",
        "run_id": "qwen08-rank1-w1-reanalysis-v01",
        "protocol": {"path": str(protocol), "sha256": sha256_file(protocol)},
        "implementation_commit": commit,
        "remote_refs_containing_commit": remote.splitlines(),
        "environment_lock": {
            "python_executable": str(Path(sys.executable).resolve()),
            "python_version": sys.version,
            "platform": platform.platform(),
            "thread_environment": {
                "CUDA_VISIBLE_DEVICES": "", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"
            },
        },
        "source_paths": {key: str(value.resolve()) for key, value in sources.items()},
        "source_sha256": {key: sha256_file(value) for key, value in sources.items()},
        "hard_cap_validation_receipt": {"path": str(validation_path), "sha256": sha256_file(validation_path)},
        "hard_cap_wrapper": {"path": str(wrapper), "sha256": sha256_file(wrapper)},
        "cleanup_script": {"path": str(cleanup), "sha256": sha256_file(cleanup)},
        "resource_caps": {
            "memory_mb": args.memory_mb,
            "cpu_percent": args.cpu_percent,
            "io_mb_s": args.io_mb_s,
            "timeout_seconds": args.timeout_seconds,
            "gpu_allowance_mb": 1,
            "checkpoint_every_seconds": args.checkpoint_every_seconds,
            "swap_bytes": args.swap_bytes,
        },
        "checkpoint_strategy": "write-once final result after bounded deterministic resampling",
        "wrapper_output_dir": str((args.analysis_output_dir.resolve() / "_wrapper")),
        "exact_inner_command": command,
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
    }
    write_once_or_equal(args.authorization_output, canonical_json_bytes(authorization))
    print(json.dumps(authorization, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
