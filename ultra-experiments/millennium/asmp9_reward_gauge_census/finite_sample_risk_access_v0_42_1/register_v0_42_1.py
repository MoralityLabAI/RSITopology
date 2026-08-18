"""Create the write-once ASMP-9 v0.42.1 repair registration."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from execute_confirmation_v0_42_1 import (
    EXPECTED_TESTS,
    PROTOCOL_ID,
    canonical_bytes,
    sha256_file,
)


BASE = Path(__file__).resolve().parent
PARENT = BASE.parent / "finite_sample_risk_access_v0_42"
SEALED = (
    "../finite_sample_risk_access_v0_42/FAILED_EXECUTION_v0_42.json",
    "../finite_sample_risk_access_v0_42/FAILED_EXECUTION_v0_42.md",
    "../finite_sample_risk_access_v0_42/PROTOCOL_v0_42.md",
    "../finite_sample_risk_access_v0_42/THEOREM_DRAFT_v0_42.md",
    "../finite_sample_risk_access_v0_42/confirmation.stderr.log",
    "../finite_sample_risk_access_v0_42/execute_confirmation_v0_42.py",
    "../finite_sample_risk_access_v0_42/finite_sample_access.py",
    "../finite_sample_risk_access_v0_42/registration_v0_42.json",
    "../finite_sample_risk_access_v0_42/sampled_confirmation.py",
    "PROTOCOL_AMENDMENT_v0_42_1.md",
    "environment_lock_v0_42_1.json",
    "execute_confirmation_v0_42_1.py",
    "protocol_v0_42_1.json",
    "test_repair_v0_42_1.py",
    "verify_result_v0_42_1.py",
    "write_environment_lock_v0_42_1.py",
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
        default=BASE / "registration_v0_42_1.json",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    if args.tests_passed != EXPECTED_TESTS:
        raise ValueError(
            f"registration requires exactly {EXPECTED_TESTS} passing tests"
        )
    sealed = {}
    for relative in SEALED:
        path = (BASE / relative).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        sealed[relative] = sha256_file(path)
    parent_registration = PARENT / "registration_v0_42.json"
    parent_protocol = json.loads(
        (PARENT / "protocol_v0_42.json").read_text(encoding="utf-8")
    )
    repair_protocol = json.loads(
        (BASE / "protocol_v0_42_1.json").read_text(encoding="utf-8")
    )
    payload = {
        "protocol_id": PROTOCOL_ID,
        "version": "0.42.1",
        "status": "registered_prereveal",
        "registered_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "implementation_commit": git_head(),
        "parent_failed_registration_sha256": sha256_file(
            parent_registration
        ),
        "repair_scope": repair_protocol["allowed_changes"],
        "preflight": {
            "command": (
                "python -m pytest -q "
                "ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "finite_sample_risk_access_v0_42 "
                "ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "finite_sample_risk_access_v0_42_1"
            ),
            "status": "pass",
            "tests_passed": args.tests_passed,
            "elapsed_seconds": args.test_seconds,
        },
        "confidence": parent_protocol["confidence"],
        "sampling": parent_protocol["sampling"],
        "practical_margins": {
            name: row["practical_margin"]
            for name, row in parent_protocol[
                "decision_problems"
            ].items()
        },
        "expected_decisions_on_simultaneous_event": parent_protocol[
            "expected_decisions_on_simultaneous_event"
        ],
        "resource_ceiling": parent_protocol["resource_ceiling"],
        "sealed_files": sealed,
    }
    output.write_bytes(canonical_bytes(payload))
    print(output)


if __name__ == "__main__":
    main()
