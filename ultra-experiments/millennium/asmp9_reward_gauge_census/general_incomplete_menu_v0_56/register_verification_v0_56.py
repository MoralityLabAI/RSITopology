"""Write-once prospective registration for ASMP-9 v0.56."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT = HERE / "verification_registration_v0_56.json"
RESULT = HERE / "VERIFY_RESULT_v0_56.json"
PREFIX = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "general_incomplete_menu_v0_56/"
)
SOURCE_FILES = tuple(
    PREFIX + name
    for name in (
        "PRIOR_ART_GATE_v0_56.md",
        "PROOF_AUDIT_v0_56.md",
        "THEOREM_DRAFT_v0_56.md",
        "VERIFICATION_PROTOCOL_v0_56.md",
        "general_incomplete.py",
        "test_general_incomplete.py",
        "test_verifier_v0_56.py",
        "verify_theorems_v0_56.py",
        "register_verification_v0_56.py",
    )
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if RESULT.exists():
        raise FileExistsError("cannot register after a verification result exists")
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()
    registration = {
        "claim_boundary": (
            "Candidate finite exact full-kernel tier-identification theorem "
            "under unrestricted positive completion. Classical limited-domain "
            "RUM and arbitrary-menu Luce ingredients; no novelty, sampling, "
            "endogenous/strategic/dynamic, human/model-value, welfare, "
            "physical-channel, or full ASMP-9 resolution claim."
        ),
        "expected_n6_affine_rank": 130,
        "expected_test_count": 11,
        "maximum_partition_n": 20,
        "maximum_zeta_width": 8,
        "minimum_witness_cases": 300,
        "protocol_id": "asmp9-general-incomplete-menu-theorem-v0.56",
        "resource_caps": {
            "resident_bytes": 536870912,
            "seconds": 120,
            "workers": 1,
        },
        "schema": "asmp9-v0.56-verification-registration-v1",
        "source_commit": commit,
        "source_sha256": {
            relative: sha256(REPO / relative) for relative in SOURCE_FILES
        },
        "test_command": (
            "python -m pytest -q -p no:cacheprovider "
            + PREFIX
            + "test_general_incomplete.py "
            + PREFIX
            + "test_verifier_v0_56.py"
        ),
        "verification_command": (
            "python " + PREFIX + "verify_theorems_v0_56.py"
        ),
        "witness_seed": 560026,
    }
    encoded = (json.dumps(registration, indent=2, sort_keys=True) + "\n").encode()
    if OUTPUT.exists():
        if OUTPUT.read_bytes() != encoded:
            raise FileExistsError("registration exists with different bytes")
    else:
        OUTPUT.write_bytes(encoded)
    print(sha256(OUTPUT))


if __name__ == "__main__":
    main()
