"""Write-once prospective registration for ASMP-9 v0.55."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT = HERE / "verification_registration_v0_55.json"
RESULT = HERE / "VERIFY_RESULT_v0_55.json"
PREFIX = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "incomplete_menu_access_v0_55/"
)
SOURCE_FILES = tuple(
    PREFIX + name
    for name in (
        "PRIOR_ART_GATE_v0_55.md",
        "THEOREM_DRAFT_v0_55.md",
        "VERIFICATION_PROTOCOL_v0_55.md",
        "incomplete_menu.py",
        "test_incomplete_menu.py",
        "test_verifier_v0_55.py",
        "verify_theorems_v0_55.py",
        "register_verification_v0_55.py",
    )
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if RESULT.exists():
        raise FileExistsError("cannot register after a verification result exists")
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()
    registration = {
        "schema": "asmp9-v0.55-verification-registration-v1",
        "protocol_id": "asmp9-incomplete-menu-tier-identification-v0.55",
        "source_commit": commit,
        "source_sha256": {
            relative: sha256(REPO / relative) for relative in SOURCE_FILES
        },
        "expected_test_count": 9,
        "expected_domain_count": 15,
        "expected_proper_domain_count": 14,
        "expected_proper_projection_count": 1125,
        "expected_proper_tier_counts": {
            "scalar_luce|random_utility_non_luce|no_random_utility_representation": 128,
            "random_utility_non_luce|no_random_utility_representation": 422,
            "no_random_utility_representation": 575,
        },
        "expected_full_tier_counts": {
            "scalar_luce": 1,
            "random_utility_non_luce": 230,
            "no_random_utility_representation": 1019,
        },
        "expected_domain_summary_sha256": (
            "a584b8954bc7ddfb8901d7b6907fa90c0b5c0b45eb770de5c8cd30e9e6241e69"
        ),
        "resource_caps": {
            "seconds": 60,
            "resident_bytes": 268435456,
            "workers": 1,
        },
        "test_command": (
            "python -m pytest -q -p no:cacheprovider "
            + PREFIX
            + "test_incomplete_menu.py "
            + PREFIX
            + "test_verifier_v0_55.py"
        ),
        "verification_command": (
            "python " + PREFIX + "verify_theorems_v0_55.py"
        ),
        "claim_boundary": (
            "Elementary finite completion-ambiguity theorem layered on "
            "classical Luce and ARSP tests; no representation-theorem "
            "novelty, finite-sample or general-domain identification, "
            "endogenous-menu, human/model, moral-value, strategic, dynamic, "
            "physical-channel, or full ASMP-9 claim."
        ),
    }
    encoded = (
        json.dumps(registration, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if OUTPUT.exists():
        if OUTPUT.read_bytes() != encoded:
            raise FileExistsError("registration exists with different bytes")
    else:
        OUTPUT.write_bytes(encoded)
    print(sha256(OUTPUT))


if __name__ == "__main__":
    main()

