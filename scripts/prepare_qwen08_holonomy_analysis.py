"""Create a provenance-stamped hard-cap authorization for one CPU pair."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal
from rsi_topology.qwen_geometry_analysis import (
    load_analysis_protocol,
    pair_analysis_protocol,
    pair_slug,
)


ROOT = Path(__file__).resolve().parents[1]


def _environment() -> dict:
    import numpy
    import scipy
    import sklearn

    return {
        "python_executable": str(Path(sys.executable).resolve()),
        "python_version": sys.version,
        "platform": platform.platform(),
        "packages": {
            "numpy": numpy.__version__,
            "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__,
        },
        "thread_environment": {
            "CUDA_VISIBLE_DEVICES": "",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
        },
    }


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--registration", type=Path, required=True)
    value.add_argument("--pair", nargs=2, required=True)
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
    value.add_argument("--seed", type=int, default=2026071605)
    value.add_argument("--confirm-caps", action="store_true")
    return value


def main() -> None:
    args = parser().parse_args()
    if not args.confirm_caps:
        raise ValueError("analysis authorization requires --confirm-caps")
    if args.swap_bytes != 0:
        raise ValueError("analysis authorization requires registered zero swap")
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
        raise ValueError("resource caps must be explicit and positive")
    registration_path = args.registration.resolve()
    registration = load_analysis_protocol(registration_path)
    pair = tuple(map(str, args.pair))
    pair_analysis_protocol(registration, pair)
    for state in pair:
        entry = registration["state_capture_indices"][state]
        path = Path(entry["path"])
        if not path.is_file() or sha256_file(path) != entry["sha256"]:
            raise ValueError(f"registered state index changed: {state}")

    validation = json.loads(
        args.hard_cap_validation_receipt.read_text(encoding="utf-8-sig")
    )
    if validation.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap validation has not passed")
    if sha256_file(args.hard_cap_wrapper) != validation["wrapper"]["sha256"]:
        raise ValueError("validation receipt does not bind the current wrapper")

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

    entrypoint = ROOT / "scripts" / "analyze_qwen08_holonomy_geometry.py"
    source_paths = {
        "entrypoint": entrypoint,
        "pair_analysis": ROOT / "rsi_topology" / "qwen_geometry_analysis.py",
        "godel_analysis": ROOT / "rsi_topology" / "godel_analysis.py",
        "discovery": ROOT / "rsi_topology" / "discovery.py",
        "bifiltration": ROOT / "rsi_topology" / "bifiltration.py",
        "attestation": ROOT / "rsi_topology" / "attestation.py",
        "holonomy": ROOT / "rsi_topology" / "holonomy.py",
        "sectioning": ROOT / "rsi_topology" / "sectioning.py",
    }
    command = [
        str(Path(sys.executable).resolve()),
        str(entrypoint.resolve()),
        "--registration",
        str(registration_path),
        "--output-dir",
        str(args.analysis_output_dir.resolve()),
        "--seed",
        str(args.seed),
        "--pair",
        *pair,
    ]
    authorization = {
        "schema_version": "qwen_holonomy_geometry_analysis_authorization_v0_1",
        "status": "authorized_for_target_blind_cpu_geometry_analysis",
        "run_id": f"qwen08-holonomy-geometry-{pair_slug(pair)}-v01",
        "analysis_registration": {
            "path": str(registration_path),
            "sha256": sha256_file(registration_path),
        },
        "state_pair": list(pair),
        "implementation_commit": commit,
        "remote_refs_containing_commit": remote.splitlines(),
        "environment_lock": _environment(),
        "source_paths": {key: str(path.resolve()) for key, path in source_paths.items()},
        "source_sha256": {key: sha256_file(path) for key, path in source_paths.items()},
        "hard_cap_validation_receipt": {
            "path": str(args.hard_cap_validation_receipt.resolve()),
            "sha256": sha256_file(args.hard_cap_validation_receipt),
        },
        "hard_cap_wrapper": {
            "path": str(args.hard_cap_wrapper.resolve()),
            "sha256": sha256_file(args.hard_cap_wrapper),
        },
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
        "checkpoint_strategy": "one independently replayable state-pair analysis",
        "wrapper_output_dir": str(
            (args.analysis_output_dir.resolve() / pair_slug(pair) / "_wrapper")
        ),
        "exact_inner_command": command,
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
    }
    write_once_or_equal(args.authorization_output, canonical_json_bytes(authorization))
    print(json.dumps(authorization, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
