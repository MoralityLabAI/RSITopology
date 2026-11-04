"""Write-once prospective registration for ASMP-9 v0.54."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT = HERE / "verification_registration_v0_54.json"
RESULT = HERE / "VERIFY_RESULT_v0_54.json"

PREFIX = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "stochastic_choice_trichotomy_v0_54/"
)
SOURCE_FILES = tuple(
    PREFIX + name
    for name in (
        "PRIOR_ART_GATE_v0_54.md",
        "THEOREM_DRAFT_v0_54.md",
        "VERIFICATION_PROTOCOL_v0_54.md",
        "stochastic_choice.py",
        "test_stochastic_choice.py",
        "test_verifier_v0_54.py",
        "verify_theorems_v0_54.py",
        "register_verification_v0_54.py",
    )
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if RESULT.exists():
        raise FileExistsError("cannot register after a verification result exists")
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        text=True,
    ).strip()
    registration = {
        "schema": "asmp9-v0.54-verification-registration-v1",
        "protocol_id": "asmp9-finite-stochastic-choice-trichotomy-v0.54",
        "source_commit": commit,
        "source_sha256": {
            relative: sha256(REPO / relative)
            for relative in SOURCE_FILES
        },
        "expected_test_count": 11,
        "universe": ["a", "b", "c"],
        "grid_denominator": 6,
        "expected_kernel_count": 1250,
        "expected_class_counts": {
            "scalar_luce": 1,
            "random_utility_non_luce": 230,
            "no_random_utility_representation": 1019,
        },
        "canonical_no_object_certificate": {
            "choice": "a",
            "lower_menu": ["a", "b"],
            "value": "-1/4",
        },
        "resource_caps": {
            "seconds": 60,
            "resident_bytes": 268435456,
            "workers": 1,
        },
        "test_command": (
            "python -m pytest -q -p no:cacheprovider "
            + PREFIX
            + "test_stochastic_choice.py "
            + PREFIX
            + "test_verifier_v0_54.py"
        ),
        "verification_command": (
            "python " + PREFIX + "verify_theorems_v0_54.py"
        ),
        "claim_boundary": (
            "Exact finite stochastic-choice classification built from "
            "classical Luce/Falmagne/McFadden-Richter results; no novelty, "
            "finite-sample or general incomplete-menu theorem, human/model "
            "rationality, moral value, strategic robustness, physical "
            "preference-channel validation, or ASMP-9 resolution."
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

