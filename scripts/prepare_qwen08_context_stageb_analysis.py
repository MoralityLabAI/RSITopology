"""Seal a hard-cap authorization for the fresh-context Stage-B analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal
from rsi_topology.qwen_context_stageb import load_protocol


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
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--protocol", type=Path, required=True)
    value.add_argument("--causal-protocol", type=Path, required=True)
    value.add_argument("--manifest", type=Path, required=True)
    value.add_argument("--main-base-index", type=Path, required=True)
    value.add_argument("--main-naive-index", type=Path, required=True)
    value.add_argument("--control-base-index", type=Path, required=True)
    value.add_argument("--control-naive-index", type=Path, required=True)
    value.add_argument("--analysis-output-dir", type=Path, required=True)
    value.add_argument("--authorization-output", type=Path, required=True)
    value.add_argument("--hard-cap-wrapper", type=Path, required=True)
    value.add_argument("--hard-cap-validation-receipt", type=Path, required=True)
    value.add_argument("--cleanup-script", type=Path, required=True)
    value.add_argument("--seed", type=int, default=2026071702)
    value.add_argument("--confirm-caps", action="store_true")
    return value


def main() -> None:
    args = parser().parse_args()
    protocol = load_protocol(args.protocol)
    if not args.confirm_caps:
        raise ValueError("Stage-B analysis authorization requires --confirm-caps")
    caps = protocol["resource_contract"]["analysis"]
    if int(caps["swap_bytes"]) != 0:
        raise ValueError("Stage-B analysis requires zero registered swap")
    validation = json.loads(args.hard_cap_validation_receipt.read_text(encoding="utf-8-sig"))
    if validation.get("hard_cap_validation_status") != "passed":
        raise ValueError("hard-cap validation has not passed")
    if sha256_file(args.hard_cap_wrapper) != validation["wrapper"]["sha256"]:
        raise ValueError("hard-cap validation does not bind the wrapper")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    remote = subprocess.run(
        ["git", "branch", "-r", "--contains", commit], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    if not remote:
        raise ValueError("Stage-B analysis implementation is not on a remote ref")
    entrypoint = ROOT / "scripts" / "run_qwen08_context_stageb.py"
    sources = {
        "entrypoint": entrypoint,
        "preparation": Path(__file__).resolve(),
        "stageb": ROOT / "rsi_topology" / "qwen_context_stageb.py",
        "godel_analysis": ROOT / "rsi_topology" / "godel_analysis.py",
        "discovery": ROOT / "rsi_topology" / "discovery.py",
        "bifiltration": ROOT / "rsi_topology" / "bifiltration.py",
        "percolation": ROOT / "rsi_topology" / "percolation.py",
        "attestation": ROOT / "rsi_topology" / "attestation.py",
        "holonomy": ROOT / "rsi_topology" / "holonomy.py",
        "sectioning": ROOT / "rsi_topology" / "sectioning.py",
    }
    for path in sources.values():
        if subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", str(path.relative_to(ROOT))], cwd=ROOT
        ).returncode != 0:
            raise ValueError(f"Stage-B source differs from HEAD: {path}")
    inputs = {
        "protocol": args.protocol,
        "causal_protocol": args.causal_protocol,
        "manifest": args.manifest,
        "main_base_index": args.main_base_index,
        "main_naive_index": args.main_naive_index,
        "control_base_index": args.control_base_index,
        "control_naive_index": args.control_naive_index,
    }
    parameters = {
        key: {"path": str(path.resolve()), "sha256": sha256_file(path)}
        for key, path in inputs.items()
    }
    parameters.update({"output_dir": str(args.analysis_output_dir.resolve()), "seed": args.seed})
    command = [
        str(Path(sys.executable).resolve()), str(entrypoint.resolve()),
        "--protocol", str(args.protocol.resolve()),
        "--causal-protocol", str(args.causal_protocol.resolve()),
        "--manifest", str(args.manifest.resolve()),
        "--authorization", str(args.authorization_output.resolve()),
        "--main-base-index", str(args.main_base_index.resolve()),
        "--main-naive-index", str(args.main_naive_index.resolve()),
        "--control-base-index", str(args.control_base_index.resolve()),
        "--control-naive-index", str(args.control_naive_index.resolve()),
        "--output-dir", str(args.analysis_output_dir.resolve()),
        "--seed", str(args.seed),
    ]
    authorization = {
        "schema_version": "qwen_holonomy_geometry_analysis_authorization_v0_1",
        "status": "authorized_for_target_blind_stage_b_analysis",
        "run_id": "qwen08-context-stageb-analysis-v0-1",
        "implementation_commit": commit,
        "remote_refs_containing_commit": remote.splitlines(),
        "environment_lock": _environment(),
        "source_paths": {key: str(path.resolve()) for key, path in sources.items()},
        "source_sha256": {key: sha256_file(path) for key, path in sources.items()},
        "analysis_parameters": parameters,
        "hard_cap_validation_receipt": {"path": str(args.hard_cap_validation_receipt.resolve()), "sha256": sha256_file(args.hard_cap_validation_receipt)},
        "hard_cap_wrapper": {"path": str(args.hard_cap_wrapper.resolve()), "sha256": sha256_file(args.hard_cap_wrapper)},
        "cleanup_script": {"path": str(args.cleanup_script.resolve()), "sha256": sha256_file(args.cleanup_script)},
        "resource_caps": caps,
        "checkpoint_strategy": "one target-blind Stage-B main/control analysis",
        "wrapper_output_dir": str((args.analysis_output_dir.resolve() / "_wrapper")),
        "exact_inner_command": command,
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
    }
    write_once_or_equal(args.authorization_output, canonical_json_bytes(authorization))
    print(json.dumps(authorization, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
