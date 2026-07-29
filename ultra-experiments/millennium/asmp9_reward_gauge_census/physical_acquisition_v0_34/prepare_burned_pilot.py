from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V033 = HERE.parent / "decision_quotient_information_v0_33"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(V033) not in sys.path:
    sys.path.insert(0, str(V033))

from pilot_design import build_manifest, canonical_bytes, sha256_bytes  # noqa: E402
from asmp9_native_fixture import load_native_sources  # noqa: E402
from robust_probe_design import minimum_linf_factorized_probe_design  # noqa: E402


SCHEMA_VERSION = "asmp9_physical_acquisition_burned_pilot_registration_v0_34"
DEFAULT_MODEL = Path(
    r"D:\Research_Engine\models\Qwen3.5\Qwen3.5-0.8B"
    r"\Qwen3.5-0.8B-Q4_K_M.gguf"
)
DEFAULT_SERVER = Path(
    r"D:\models\Tesseract\runtime\llama.cpp\b10064-cuda12.4"
    r"\payload\llama-server.exe"
)
DEFAULT_OUTPUT = Path(
    r"D:\Research_Engine\runs\asmp9_physical_acquisition_burned_pilot_v0_34"
)
DEFAULT_CLEANUP = Path(
    r"C:\Users\patri\.codex\skills\hrm-trainer\scripts"
    r"\post_run_memory_cleanup.ps1"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(REPO).as_posix()


def write_once_or_equal(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"refusing to overwrite unequal file: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def git_output(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=REPO,
        text=True,
        encoding="utf-8",
    ).strip()


def assert_clean_before_generation(
    manifest_path: Path,
    registration_path: Path,
) -> None:
    allowed = {
        repo_path(manifest_path),
        repo_path(registration_path),
    }
    dirty = {
        line[3:].replace("\\", "/")
        for line in git_output("status", "--porcelain=v1").splitlines()
        if line.strip()
    }
    unexpected = dirty - allowed
    if unexpected:
        raise RuntimeError(
            "worktree must contain only generated pilot artifacts: "
            + ", ".join(sorted(unexpected))
        )


def environment_lock() -> dict[str, Any]:
    gpu = subprocess.check_output(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,memory.total",
            "--format=csv,noheader,nounits",
        ],
        text=True,
        encoding="utf-8",
        timeout=20,
    ).strip()
    return {
        "python_executable": str(Path(sys.executable).resolve()),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "processor_count": os.cpu_count(),
        "gpu": gpu,
        "packages": {
            name: metadata.version(name)
            for name in ("numpy", "pytest")
        },
    }


def artifact(path: Path) -> dict[str, Any]:
    return {
        "path": repo_path(path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def external_artifact(path: Path) -> dict[str, Any]:
    path = path.resolve()
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def build_registration(args: argparse.Namespace) -> dict[str, Any]:
    for path in (args.model, args.server, args.cleanup):
        if not path.is_file():
            raise FileNotFoundError(path)

    sources = load_native_sources()
    robust = minimum_linf_factorized_probe_design(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    if robust.policy_contrast_basis_indices != (0, 1, 2):
        raise RuntimeError("preferred policy basis changed")
    if robust.cell_basis_indices != (0, 1, 2, 4, 5, 7):
        raise RuntimeError("preferred behavioral-cell basis changed")
    if str(robust.combined_amplification) != "8":
        raise RuntimeError("preferred reconstruction amplification changed")

    manifest = build_manifest()
    manifest_path = args.manifest.resolve()
    write_once_or_equal(manifest_path, canonical_bytes(manifest))
    pilot_rows = [
        row for row in manifest["rows"] if row["phase"] == "burned_pilot"
    ]
    holdout_rows = [
        row for row in manifest["rows"] if row["phase"] == "future_holdout"
    ]
    if len(pilot_rows) != 972 or len(holdout_rows) != 972:
        raise RuntimeError("unexpected phase row count")

    code_paths = {
        "design": HERE / "pilot_design.py",
        "preparer": Path(__file__).resolve(),
        "runner": HERE / "run_burned_pilot.py",
        "analyzer": HERE / "analyze_burned_pilot.py",
        "hard_cap_wrapper": REPO
        / "scripts"
        / "run_asmp9_v034_jobobject.ps1",
        "tests": REPO / "tests" / "test_asmp9_physical_acquisition_v034.py",
        "design_note": HERE / "BURNED_PILOT_DESIGN_v0_34.md",
        "v033_query_span": V033 / "QUERY_SPAN_DEVELOPMENT_v0_33_3.json",
    }
    missing = [name for name, path in code_paths.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing registered files: " + ", ".join(missing))

    registration_path = args.registration.resolve()
    output = args.output.resolve()
    runner = code_paths["runner"].resolve()
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "registration_id": (
            "ASMP-9-PHYSICAL-ACQUISITION-BURNED-PILOT-v0.34"
        ),
        "status": "burned_pilot_registered_not_run",
        "prepared_utc": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(),
        ),
        "git_commit_before_registration": git_output("rev-parse", "HEAD"),
        "git_branch": git_output("branch", "--show-current"),
        "outcomes_consumed": False,
        "phase_authorization": {
            "authorized_phase": "burned_pilot",
            "forbidden_phase": "future_holdout",
            "pilot_rows": len(pilot_rows),
            "holdout_rows": len(holdout_rows),
            "planned_cold_start_epochs": 2,
            "planned_receipts": 2 * len(pilot_rows),
        },
        "preferred_probe_basis": {
            "policy_contrast_indices": list(
                robust.policy_contrast_basis_indices
            ),
            "cell_indices": list(robust.cell_basis_indices),
            "scalar_probe_count": 18,
            "decision_rank": 18,
            "reconstruction_linf_amplification": "8",
        },
        "manifest": {
            "path": repo_path(manifest_path),
            "sha256": sha256_file(manifest_path),
            "bytes": manifest_path.stat().st_size,
            "content_sha256": manifest["manifest_content_sha256"],
        },
        "source_artifacts": {
            **{
                path: {
                    "sha256": digest,
                }
                for path, digest in sorted(sources.source_hashes.items())
            },
            repo_path(code_paths["v033_query_span"]): {
                "sha256": sha256_file(code_paths["v033_query_span"])
            },
        },
        "implementation": {
            name: artifact(path) for name, path in sorted(code_paths.items())
        },
        "environment": environment_lock(),
        "model": {
            **external_artifact(args.model),
            "model_id": "Qwen3.5-0.8B-Q4_K_M",
            "precision": "Q4_K_M",
        },
        "server": {
            **external_artifact(args.server),
            "llama_cpp_tag": "b10064",
            "llama_cpp_commit": "86d86ed4396b4130922f7b9af26e3d9fc11a591b",
        },
        "cleanup_script": external_artifact(args.cleanup),
        "sampling_contract": {
            "grammar": "root ::= [AB]",
            "n_predict": 1,
            "temperature": 1.0,
            "top_k": 0,
            "top_p": 1.0,
            "min_p": 0.0,
            "min_keep": 2,
            "n_probs": 2,
            "post_sampling_probs": True,
            "cache_prompt": False,
            "cold_start_epochs": 2,
            "seed_base": 934202607,
        },
        "resource_caps": {
            "memory_mb": 2048,
            "cpu_percent": 50,
            "io_mb_s": 50,
            "io_sustained_samples": 3,
            "timeout_seconds": 7200,
            "gpu_allowance_mb": 1600,
            "checkpoint_every_seconds": 60,
            "swap_bytes": 0,
            "thermal_pause_temperature_c": 84,
            "thermal_resume_temperature_c": 82,
            "hard_abort_temperature_c": 88,
        },
        "capture_parameters": {
            "output_dir": str(output),
            "context_size": 1024,
            "batch_size": 512,
            "ubatch_size": 256,
            "gpu_layers": 99,
            "threads": 2,
            "port": 8834,
            "checkpoint_every": 18,
        },
        "checkpoint_strategy": (
            "One write-once receipt per query; progress checkpoint every 18 "
            "receipts and at every planned cold-start boundary."
        ),
        "wrapper_output_dir": str(output / "wrapper"),
        "exact_inner_command": [
            str(Path(sys.executable).resolve()),
            str(runner),
            "--registration",
            str(registration_path),
            "--output-dir",
            str(output),
            "--execution-class",
            "burned_pilot",
        ],
        "pilot_analysis_contract": {
            "primary_scalar": (
                "order-corrected log probability ratio of target to comparator"
            ),
            "standard_gamble_estimator": (
                "linear interpolation of the family-specific zero crossing on "
                "the frozen five-point anchor-probability grid"
            ),
            "policy_secant": (
                "least-squares line through the norm-zero response within each "
                "registered probe and prompt family"
            ),
            "confirmation_thresholds": (
                "unset until this burned pilot is complete; no pilot row may "
                "enter confirmation"
            ),
        },
        "claim_boundary": (
            "This burned pilot may calibrate one prompt-level ASMP-9 successor "
            "on one quantized Qwen model. It is not confirmation evidence, does "
            "not validate expected utility or semantic policy identity, does "
            "not authorize edits or stochastic policy trials, and does not "
            "resolve ASMP-9."
        ),
    }
    payload["registration_content_sha256"] = sha256_bytes(
        canonical_bytes(
            {
                key: value
                for key, value in payload.items()
                if key != "registration_content_sha256"
            }
        )
    )
    return payload


def run(args: argparse.Namespace) -> None:
    args.manifest = args.manifest.resolve()
    args.registration = args.registration.resolve()
    assert_clean_before_generation(args.manifest, args.registration)
    registration = build_registration(args)
    write_once_or_equal(args.registration, canonical_bytes(registration))
    print(json.dumps(registration, indent=2, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=HERE / "burned_pilot_prompt_manifest_v0_34.json",
    )
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "burned_pilot_registration_v0_34.json",
    )
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--server", type=Path, default=DEFAULT_SERVER)
    parser.add_argument("--cleanup", type=Path, default=DEFAULT_CLEANUP)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
