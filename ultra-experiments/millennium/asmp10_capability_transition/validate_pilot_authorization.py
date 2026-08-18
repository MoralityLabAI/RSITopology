"""Validate the ASMP-10 pilot authorization before invoking the hard-cap wrapper."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import torch


REPO_ROOT = Path(__file__).resolve().parents[3]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=text
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("authorization", type=Path)
    args = parser.parse_args()
    path = args.authorization.resolve()
    authorization = json.loads(path.read_text(encoding="utf-8"))
    assert authorization["status"] == "authorized_pilot_only_not_claim_eligible"
    assert authorization["resource_caps"]["swap_bytes"] == 0
    assert authorization["resource_caps"]["minimum_free_memory_mb"] == (
        authorization["resource_caps"]["memory_mb"]
        + authorization["resource_caps"]["host_reserve_mb"]
    )
    for role in ("hard_cap_wrapper", "hard_cap_validation_receipt", "cleanup_script"):
        record = authorization[role]
        target = Path(record["path"])
        assert target.is_file(), role
        assert sha256(target) == record["sha256"], role
    receipt = json.loads(
        Path(authorization["hard_cap_validation_receipt"]["path"]).read_text(encoding="utf-8-sig")
    )
    assert receipt["hard_cap_validation_status"] == "passed"
    assert receipt["wrapper"]["sha256"] == authorization["hard_cap_wrapper"]["sha256"]
    assert receipt["cleanup"]["sha256"] == authorization["cleanup_script"]["sha256"]

    source_commit = authorization["source_commit"]
    for role, record in authorization["sealed_inputs"].items():
        target = Path(record["path"])
        assert target.is_file(), role
        assert sha256(target) == record["sha256"], role
        relative = target.resolve().relative_to(REPO_ROOT).as_posix()
        committed = git("show", f"{source_commit}:{relative}", text=False).stdout
        assert hashlib.sha256(committed).hexdigest() == record["sha256"], role
        assert not git("status", "--porcelain", "--", relative).stdout.strip(), role

    command = authorization["exact_inner_command"]
    assert Path(command[1]).resolve() == Path(authorization["sealed_inputs"]["trainer"]["path"]).resolve()
    config_index = command.index("--config") + 1
    output_index = command.index("--output-dir") + 1
    assert Path(command[config_index]).resolve() == Path(authorization["sealed_inputs"]["config"]["path"]).resolve()
    assert Path(command[output_index]).resolve() == Path(authorization["capture_parameters"]["output_dir"]).resolve()
    assert torch.cuda.is_available(), "CUDA unavailable"
    assert torch.cuda.get_device_properties(0).total_memory >= 3 * 1024**3, "GPU too small"
    print("ASMP-10 pilot authorization validation passed")
    print(
        json.dumps(
            {
                "source_commit": source_commit,
                "wrapper_sha256": authorization["hard_cap_wrapper"]["sha256"],
                "device": torch.cuda.get_device_name(0),
                "memory_cap_mb": authorization["resource_caps"]["memory_mb"],
                "gpu_cap_mb": authorization["resource_caps"]["gpu_allowance_mb"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
