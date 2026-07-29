from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

LOCAL_NAMES = (
    "AMENDMENT_v0_22_1.md",
    "README.md",
    "burned_graph_registry_v0_22_1.json",
    "environment_lock_v0_22_1.json",
    "make_burned_graph_registry_v0_22_1.py",
    "protocol_v0_22_1.json",
    "register_v0_22_1.py",
    "run_verification_v0_22_1.py",
    "test_protocol_v0_22_1.py",
    "verify_result_v0_22_1.py",
)

DEPENDENCIES = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "uniform_above_floor_v0_22/POSTRUN_NOTE_v0_22.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "uniform_above_floor_v0_22/PRIOR_ART_GATE_v0_22.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "uniform_above_floor_v0_22/THEORY_DRAFT_v0_22.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "uniform_above_floor_v0_22/artifacts_v0_22/"
    "independent_verification_v0_22.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "uniform_above_floor_v0_22/artifacts_v0_22/result_v0_22.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "uniform_above_floor_v0_22/artifacts_v0_22/run_receipt_v0_22.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "uniform_above_floor_v0_22/registration_v0_22.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "uniform_above_floor_v0_22/uniform_above_floor.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "uniform_above_floor_v0_22/verify_result_v0_22.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "block_factorization_v0_20/block_factorization.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("tracked tree must be clean before registration")

    paths = [HERE / name for name in LOCAL_NAMES] + [
        REPO / relative for relative in DEPENDENCIES
    ]
    sealed: dict[str, str] = {}
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        relative = path.relative_to(REPO).as_posix()
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", relative],
            cwd=REPO,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        sealed[relative] = sha256(path)

    registration = {
        "implementation_commit": git("rev-parse", "HEAD"),
        "protocol_path": (
            HERE / "protocol_v0_22_1.json"
        ).relative_to(REPO).as_posix(),
        "registered_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "registration_id": (
            "ASMP-9-UNIFORM-ABOVE-FLOOR-v0.22.1-registration"
        ),
        "sealed_files": sealed,
    }
    write_json_exclusive(output, registration)
    print(
        json.dumps(
            {
                "implementation_commit": registration[
                    "implementation_commit"
                ],
                "registration_sha256": sha256(output),
                "sealed_file_count": len(sealed),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
