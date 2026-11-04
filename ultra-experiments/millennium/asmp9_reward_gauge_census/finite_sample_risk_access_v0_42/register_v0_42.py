"""Create the write-once ASMP-9 v0.42 prereveal registration."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import json
from pathlib import Path
import subprocess

from execute_confirmation_v0_42 import (
    EXPECTED_TESTS,
    canonical_bytes,
    sha256_file,
)


BASE = Path(__file__).resolve().parent
PROTOCOL_ID = "asmp9-finite-sample-risk-access-v0.42"
SEALED = (
    "../decision_relative_access_v0_38/relative_deficiency.py",
    "../sequential_risk_access_v0_41/confirmation.py",
    "../sequential_risk_access_v0_41/sequential_access.py",
    "PRIOR_ART_GATE_v0_42.md",
    "PROTOCOL_v0_42.md",
    "THEOREM_DRAFT_v0_42.md",
    "environment_lock_v0_42.json",
    "execute_confirmation_v0_42.py",
    "finite_sample_access.py",
    "protocol_v0_42.json",
    "sampled_confirmation.py",
    "test_execute_confirmation_v0_42.py",
    "test_finite_sample_access.py",
    "test_sampled_confirmation.py",
    "test_small_exact_perturbations.py",
    "verify_result_v0_42.py",
    "write_environment_lock_v0_42.py",
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
        default=BASE / "registration_v0_42.json",
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
    protocol = json.loads(
        (BASE / "protocol_v0_42.json").read_text(encoding="utf-8")
    )
    payload = {
        "protocol_id": PROTOCOL_ID,
        "version": "0.42",
        "status": "registered_prereveal",
        "registered_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "implementation_commit": git_head(),
        "parent": protocol["parent"],
        "preflight": {
            "command": (
                "python -m pytest -q "
                "ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "finite_sample_risk_access_v0_42"
            ),
            "status": "pass",
            "tests_passed": args.tests_passed,
            "elapsed_seconds": args.test_seconds,
        },
        "confidence": protocol["confidence"],
        "sampling": protocol["sampling"],
        "practical_margins": {
            name: str(Q(row["practical_margin"]))
            for name, row in protocol["decision_problems"].items()
        },
        "expected_decisions_on_simultaneous_event": protocol[
            "expected_decisions_on_simultaneous_event"
        ],
        "resource_ceiling": protocol["resource_ceiling"],
        "sealed_files": sealed,
    }
    output.write_bytes(canonical_bytes(payload))
    print(output)


if __name__ == "__main__":
    main()
