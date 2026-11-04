"""Materialize the outcome-blind ASMP-9 v0.35 execution registration."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from pilot_design_v035 import (  # noqa: E402
    build_manifest,
    canonical_bytes,
    sha256_bytes,
)


DEFAULT_MANIFEST = HERE / "measurement_pilot_prompt_manifest_v035.json"
DEFAULT_REGISTRATION = HERE / "measurement_pilot_registration_v035.json"
DEFAULT_RUN_ROOT = Path("/workspace/asmp9_measurement_v035")

IMPLEMENTATION_PATHS = {
    "scientific_protocol": (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "measurement_channel_v0_35/PILOT_PROTOCOL_v0_35.json"
    ),
    "design": (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "measurement_channel_v0_35/pilot_design_v035.py"
    ),
    "monotone_ruler": (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "measurement_channel_v0_35/monotone_ruler.py"
    ),
    "runner_adapter": (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "measurement_channel_v0_35/run_measurement_pilot_v035.py"
    ),
    "sealed_runner": (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "physical_acquisition_v0_34/run_burned_pilot.py"
    ),
    "analyzer": (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "measurement_channel_v0_35/pilot_analyzer_v035.py"
    ),
    "preparer": (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "measurement_channel_v0_35/prepare_registration_v035.py"
    ),
    "hard_cap_wrapper": "scripts/run_prime_asmp9_measurement_v035_guarded.sh",
    "cleanup": "scripts/post_run_prime_asmp9_v0343.sh",
    "tests": "tests/test_asmp9_measurement_channel_v035.py",
}

SOURCE_PATHS = {
    "v0_34_prime_result": (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "physical_acquisition_v0_34/PRIME_RESULT_v0_34_4.md"
    ),
    "v0_34_analysis": (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "physical_acquisition_v0_34/BURNED_PILOT_ANALYSIS_v0_34_4.json"
    ),
    "v0_34_repair_radius": (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "measurement_channel_v0_35/REPAIR_RADIUS_RESULT_v0_35.json"
    ),
    "v0_33_query_span": (
        "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "decision_quotient_information_v0_33/"
        "QUERY_SPAN_DEVELOPMENT_v0_33_3.json"
    ),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=REPO,
        text=True,
    ).strip()


def registered_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def file_record(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return {
        "path": registered_path(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def repo_record(relative_path: str) -> dict[str, Any]:
    return file_record(REPO / relative_path)


def compare_or_fail(path: Path, payload: Mapping[str, Any]) -> None:
    data = canonical_bytes(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"refusing to replace unequal artifact: {path}")
        return
    path.write_bytes(data)


def registered_manifest(git_commit: str) -> dict[str, Any]:
    payload = copy.deepcopy(build_manifest())
    payload.pop("manifest_content_sha256", None)
    payload.update(
        {
            "manifest_id": "ASMP-9-MEASUREMENT-CHANNEL-PILOT-v0.35",
            "status": "registered_not_run",
            "execution_authorized": True,
            "registered_git_commit": git_commit,
        }
    )
    payload["manifest_content_sha256"] = sha256_bytes(
        canonical_bytes(payload)
    )
    return payload


def build_registration(
    *,
    manifest_path: Path,
    registration_path: Path,
    model_path: Path,
    server_path: Path,
    cuda_library_path: Path,
    output_dir: Path,
    prepared_utc: str,
    git_commit: str,
    git_branch: str,
    pod_id: str,
    provider: str,
    region: str,
    gpu_description: str,
    listed_hourly_usd: float,
    port: int = 8835,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("status") != "registered_not_run"
        or manifest.get("execution_authorized") is not True
        or manifest.get("outcomes_consumed") is not False
    ):
        raise ValueError("manifest is not an outcome-blind registered manifest")
    expected_manifest_hash = str(manifest["manifest_content_sha256"])
    actual_manifest_hash = sha256_bytes(
        canonical_bytes(
            {
                key: value
                for key, value in manifest.items()
                if key != "manifest_content_sha256"
            }
        )
    )
    if actual_manifest_hash != expected_manifest_hash:
        raise ValueError("manifest content hash mismatch")

    implementation = {
        name: repo_record(path)
        for name, path in IMPLEMENTATION_PATHS.items()
    }
    implementation["cuda_library"] = file_record(cuda_library_path)
    source_artifacts = {
        name: repo_record(path) for name, path in SOURCE_PATHS.items()
    }

    runner_path = (
        REPO
        / IMPLEMENTATION_PATHS["runner_adapter"]
    ).resolve()
    registration_path = registration_path.resolve()
    payload: dict[str, Any] = {
        "schema_version": "asmp9_measurement_channel_registration_v0_35",
        "registration_id": "ASMP-9-MEASUREMENT-CHANNEL-PRIME-v0.35",
        "status": "registered_not_run",
        "prepared_utc": prepared_utc,
        "git_commit_before_registration": git_commit,
        "git_branch": git_branch,
        "outcomes_consumed": False,
        "manifest": {
            **file_record(manifest_path),
            "content_sha256": expected_manifest_hash,
        },
        "model": {
            **file_record(model_path),
            "model_id": "Qwen3.5-0.8B-Q4_K_M",
            "precision": "Q4_K_M",
        },
        "server": {
            **file_record(server_path),
            "llama_cpp_tag": "b10064",
            "llama_cpp_commit": "86d86ed4396b4130922f7b9af26e3d9fc11a591b",
            "cuda_library_sha256": sha256_file(cuda_library_path.resolve()),
        },
        "cleanup_script": repo_record(
            "scripts/post_run_prime_asmp9_v0343.sh"
        ),
        "implementation": implementation,
        "source_artifacts": source_artifacts,
        "capture_parameters": {
            "output_dir": output_dir.resolve().as_posix(),
            "port": port,
            "context_size": 1024,
            "batch_size": 512,
            "ubatch_size": 256,
            "gpu_layers": 99,
            "threads": 2,
            "checkpoint_every": 24,
        },
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
            "seed_base": 935202607,
        },
        "phase_authorization": {
            "authorized_phase": "burned_measurement_pilot",
            "confirmation": "not_authorized",
            "v0_34_future_holdout": "ineligible",
            "pilot_rows": 2412,
            "planned_cold_start_epochs": 2,
            "planned_receipts": 4824,
        },
        "resource_caps": {
            "memory_mb": 4096,
            "swap_bytes": 0,
            "cpu_percent": 50,
            "io_mb_s": 50,
            "timeout_seconds": 1800,
            "gpu_allowance_mb": 1600,
            "gpu_clean_start_ceiling_mb": 64,
            "hard_abort_temperature_c": 88,
            "thermal_pause_temperature_c": 84,
            "thermal_resume_temperature_c": 82,
            "checkpoint_every_seconds": 60,
        },
        "environment": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "gpu": gpu_description,
            "pod_id": pod_id,
            "provider": provider,
            "region": region,
            "listed_hourly_usd": listed_hourly_usd,
        },
        "exact_inner_command": [
            "/usr/bin/python3",
            runner_path.as_posix(),
            "--registration",
            registration_path.as_posix(),
            "--output-dir",
            output_dir.resolve().as_posix(),
            "--execution-class",
            "measurement_pilot",
        ],
        "exact_launch_command": [
            "/usr/bin/bash",
            (REPO / IMPLEMENTATION_PATHS["hard_cap_wrapper"]).resolve().as_posix(),
        ],
        "exact_launch_environment": {
            "RUN_ROOT": output_dir.resolve().parent.as_posix(),
            "REPO_ROOT": REPO.resolve().as_posix(),
            "OUTPUT_DIR": output_dir.resolve().as_posix(),
            "REGISTRATION": registration_path.as_posix(),
            "UNIT_NAME": "asmp9-measurement-v035",
        },
        "wrapper_output_dir": output_dir.resolve().as_posix(),
        "claim_boundary": (
            "This burned measurement pilot may validate or reject one "
            "semantic-choice channel on one quantized Qwen model and one "
            "registered runtime. It is not confirmation evidence, cannot "
            "establish mixture affinity or the decision quotient, does not "
            "authorize edits, and does not resolve ASMP-9."
        ),
    }
    payload["registration_content_sha256"] = sha256_bytes(
        canonical_bytes(payload)
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--server-path", type=Path, required=True)
    parser.add_argument("--cuda-library-path", type=Path, required=True)
    parser.add_argument("--prepared-utc", required=True)
    parser.add_argument("--pod-id", required=True)
    parser.add_argument("--provider", default="massedcompute")
    parser.add_argument("--region", default="US")
    parser.add_argument("--gpu-description", required=True)
    parser.add_argument("--listed-hourly-usd", type=float, required=True)
    parser.add_argument("--port", type=int, default=8835)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RUN_ROOT / "output")
    parser.add_argument("--manifest-output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--registration-output",
        type=Path,
        default=DEFAULT_REGISTRATION,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if git("status", "--porcelain"):
        raise RuntimeError("registration requires a clean worktree")
    expected_cuda_directory = Path(
        "/workspace/llama.cpp/build-sm89/bin"
    ).resolve()
    if args.cuda_library_path.resolve().parent != expected_cuda_directory:
        raise ValueError(
            "registered CUDA library must come from the wrapper's frozen "
            "LD_LIBRARY_PATH"
        )
    git_commit = git("rev-parse", "HEAD")
    git_branch = git("branch", "--show-current")
    manifest = registered_manifest(git_commit)
    manifest_path = args.manifest_output.resolve()
    compare_or_fail(manifest_path, manifest)
    registration = build_registration(
        manifest_path=manifest_path,
        registration_path=args.registration_output,
        model_path=args.model_path,
        server_path=args.server_path,
        cuda_library_path=args.cuda_library_path,
        output_dir=args.output_dir,
        prepared_utc=args.prepared_utc,
        git_commit=git_commit,
        git_branch=git_branch,
        pod_id=args.pod_id,
        provider=args.provider,
        region=args.region,
        gpu_description=args.gpu_description,
        listed_hourly_usd=args.listed_hourly_usd,
        port=args.port,
    )
    compare_or_fail(args.registration_output.resolve(), registration)
    print(json.dumps(registration, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
