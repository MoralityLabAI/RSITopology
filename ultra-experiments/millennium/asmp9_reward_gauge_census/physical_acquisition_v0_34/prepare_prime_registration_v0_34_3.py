"""Prepare the prospective Prime execution registration for ASMP-9 v0.34.3."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from pilot_design import canonical_bytes, sha256_bytes  # noqa: E402


BASE_REGISTRATION = HERE / "burned_pilot_registration_v0_34_2.json"
OUTPUT = HERE / "burned_pilot_registration_v0_34_3.json"
REMOTE_ROOT = "/workspace/asmp9_physical_v0343"
REMOTE_REPO = f"{REMOTE_ROOT}/repo"


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


def artifact(path: str) -> dict[str, Any]:
    target = REPO / path
    return {
        "path": path,
        "bytes": target.stat().st_size,
        "sha256": sha256_file(target),
    }


def compare_or_fail(path: Path, payload: dict[str, Any]) -> None:
    data = canonical_bytes(payload)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"refusing to replace unequal registration: {path}")
        return
    path.write_bytes(data)


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    if git("status", "--porcelain"):
        raise RuntimeError("registration requires a clean worktree")
    source = json.loads(BASE_REGISTRATION.read_text(encoding="utf-8"))
    payload = copy.deepcopy(source)
    payload.pop("registration_content_sha256", None)

    payload.update(
        {
            "schema_version": (
                "asmp9_physical_acquisition_burned_pilot_registration_v0_34_3"
            ),
            "registration_id": (
                args.registration_id
            ),
            "status": "burned_pilot_registered_not_run",
            "prepared_utc": args.prepared_utc,
            "git_commit_before_registration": git("rev-parse", "HEAD"),
            "outcomes_consumed": False,
            "exact_inner_command": [
                "/usr/bin/python3",
                (
                    f"{REMOTE_REPO}/ultra-experiments/millennium/"
                    "asmp9_reward_gauge_census/physical_acquisition_v0_34/"
                    "run_burned_pilot_prime_v0_34_3.py"
                ),
                "--registration",
                (
                    f"{REMOTE_REPO}/ultra-experiments/millennium/"
                    "asmp9_reward_gauge_census/physical_acquisition_v0_34/"
                    f"{args.output.name}"
                ),
                "--output-dir",
                f"{REMOTE_ROOT}/output",
                "--execution-class",
                "burned_pilot",
            ],
            "environment": {
                "platform": "Ubuntu-22.04.5-LTS",
                "python_version": "3.10.12",
                "gpu": (
                    "NVIDIA RTX 6000 Ada Generation, driver 580.126.09, "
                    "46068 MiB"
                ),
                "cuda_toolkit": "12.8.93",
                "pod_id": args.pod_id,
                "provider": "massedcompute",
                "region": "US",
                "listed_hourly_usd": 0.75,
                "local_preparer_platform": platform.platform(),
            },
            "execution_surface": {
                "kind": "Prime non-spot pod",
                "pod_id": args.pod_id,
                "ip_at_registration": args.ip,
                "availability_id": "03c728",
                "gpu_type": "RTX6000Ada 48GB",
                "scientific_contract_changed": False,
                "local_partial_receipts_reused": False,
                "query_count_before_registration": 0,
                "setup_attempts_before_registration": [
                    "missing_cuda_toolkit_zero_query",
                    "unresolved_nvcc_path_zero_query",
                    "missing_cuda_host_compiler_zero_query",
                    "non_target_findmnt_zero_query",
                    "unprivileged_systemd_run_zero_query",
                    "missing_shim_entrypoint_zero_query",
                ],
            },
        }
    )

    payload["capture_parameters"].update(
        {
            "output_dir": f"{REMOTE_ROOT}/output",
            "threads": 2,
            "gpu_layers": 99,
        }
    )
    payload["resource_caps"] = {
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
    }
    payload["wrapper_output_dir"] = f"{REMOTE_ROOT}/output"

    payload["model"].update(
        {
            "path": (
                f"{REMOTE_ROOT}/model/Qwen3.5-0.8B-Q4_K_M.gguf"
            ),
        }
    )
    payload["server"] = {
        "path": "/workspace/llama.cpp/build-sm89/bin/llama-server",
        "bytes": int(args.server_bytes),
        "sha256": args.server_sha256,
        "llama_cpp_tag": "b10064",
        "llama_cpp_commit": "86d86ed4396b4130922f7b9af26e3d9fc11a591b",
        "cuda_architecture": "sm_89",
        "cuda_library_sha256": args.cuda_library_sha256,
    }
    payload["cleanup_script"] = artifact(
        "scripts/post_run_prime_asmp9_v0343.sh"
    )

    payload["implementation"] = {
        "design": artifact(
            "ultra-experiments/millennium/asmp9_reward_gauge_census/"
            "physical_acquisition_v0_34/pilot_design.py"
        ),
        "design_note": artifact(
            "ultra-experiments/millennium/asmp9_reward_gauge_census/"
            "physical_acquisition_v0_34/BURNED_PILOT_DESIGN_v0_34.md"
        ),
        "sealed_runner": artifact(
            "ultra-experiments/millennium/asmp9_reward_gauge_census/"
            "physical_acquisition_v0_34/run_burned_pilot.py"
        ),
        "runner": artifact(
            "ultra-experiments/millennium/asmp9_reward_gauge_census/"
            "physical_acquisition_v0_34/run_burned_pilot_prime_v0_34_3.py"
        ),
        "analyzer": artifact(
            "ultra-experiments/millennium/asmp9_reward_gauge_census/"
            "physical_acquisition_v0_34/analyze_burned_pilot.py"
        ),
        "preparer": artifact(
            "ultra-experiments/millennium/asmp9_reward_gauge_census/"
            "physical_acquisition_v0_34/prepare_prime_registration_v0_34_3.py"
        ),
        "hard_cap_wrapper": artifact(
            "scripts/run_prime_asmp9_v0343_guarded.sh"
        ),
        "setup": artifact("scripts/setup_prime_asmp9_v0343.sh"),
        "cleanup": artifact("scripts/post_run_prime_asmp9_v0343.sh"),
        "base_tests": artifact(
            "tests/test_asmp9_physical_acquisition_v034.py"
        ),
        "prime_tests": artifact(
            "tests/test_asmp9_physical_acquisition_prime_v0343.py"
        ),
        "v033_query_span": artifact(
            "ultra-experiments/millennium/asmp9_reward_gauge_census/"
            "decision_quotient_information_v0_33/"
            "QUERY_SPAN_DEVELOPMENT_v0_33_3.json"
        ),
    }

    payload["claim_boundary"] = (
        "This burned pilot may calibrate one prompt-level ASMP-9 successor "
        "on one quantized Qwen model and one separately reported Prime "
        "runtime. It is not confirmation evidence, does not validate expected "
        "utility or semantic policy identity, does not authorize edits or "
        "stochastic policy trials, and does not resolve ASMP-9."
    )
    payload["registration_content_sha256"] = sha256_bytes(
        canonical_bytes(payload)
    )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pod-id", required=True)
    parser.add_argument("--ip", required=True)
    parser.add_argument("--server-sha256", required=True)
    parser.add_argument("--server-bytes", type=int, required=True)
    parser.add_argument("--cuda-library-sha256", required=True)
    parser.add_argument("--prepared-utc", required=True)
    parser.add_argument(
        "--registration-id",
        default="ASMP-9-PHYSICAL-ACQUISITION-BURNED-PILOT-PRIME-v0.34.3",
    )
    parser.add_argument("--output", type=Path, default=OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = prepare(args)
    compare_or_fail(args.output.resolve(), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
