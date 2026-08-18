"""Create the write-once ASMP-9 v0.41 prereveal registration."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from execute_confirmation import canonical_bytes, sha256_file


BASE = Path(__file__).resolve().parent
PROTOCOL_ID = "asmp9-sequential-risk-access-v0.41"
SEALED = (
    "../decision_relative_access_v0_38/relative_deficiency.py",
    "PRIOR_ART_GATE_v0_41.md",
    "PROTOCOL_v0_41.md",
    "THEOREM_DRAFT_v0_41.md",
    "confirmation.py",
    "environment_lock_v0_41.json",
    "execute_confirmation.py",
    "protocol_v0_41.json",
    "sequential_access.py",
    "test_confirmation_structure.py",
    "test_execute_confirmation.py",
    "test_sequential_access.py",
    "verify_result_v0_41.py",
)


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=BASE,
        text=True,
    ).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tests-passed", type=int, required=True)
    parser.add_argument("--test-seconds", type=float, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE / "registration_v0_41.json",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    if args.tests_passed != 14:
        raise ValueError("registration requires exactly fourteen passing tests")
    sealed = {}
    for relative in SEALED:
        path = (BASE / relative).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        sealed[relative] = sha256_file(path)
    payload = {
        "protocol_id": PROTOCOL_ID,
        "version": "0.41",
        "status": "registered_prereveal",
        "registered_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "implementation_commit": git_head(),
        "preflight": {
            "command": (
                "python -m pytest -q "
                "ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "sequential_risk_access_v0_41"
            ),
            "status": "pass",
            "tests_passed": args.tests_passed,
            "elapsed_seconds": args.test_seconds,
        },
        "confirmation_fixture": json.loads(
            (BASE / "protocol_v0_41.json").read_text(encoding="utf-8")
        )["confirmation_fixture"],
        "resource_ceiling": {
            "max_wall_seconds": 600,
            "max_peak_working_set_bytes": 1073741824,
            "processes": 1,
            "network": False,
        },
        "sealed_files": sealed,
    }
    output.write_bytes(canonical_bytes(payload))
    print(output)


if __name__ == "__main__":
    main()
