"""Write-once prospective registration for ASMP-9 v0.53."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT = HERE / "verification_registration_v0_53.json"
RESULT = HERE / "VERIFY_RESULT_v0_53.json"

PREFIX = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "aggregate_randomized_v0_53/"
)
SOURCE_FILES = tuple(
    PREFIX + name
    for name in (
        "PRIOR_ART_GATE_v0_53.md",
        "THEOREM_DRAFT_v0_53.md",
        "VERIFICATION_PROTOCOL_v0_53.md",
        "aggregate_randomized.py",
        "test_aggregate_randomized.py",
        "test_verifier_v0_53.py",
        "verify_theorems_v0_53.py",
        "register_verification_v0_53.py",
    )
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if RESULT.exists():
        raise FileExistsError(
            "cannot register after a verification result exists"
        )
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        text=True,
    ).strip()
    registration = {
        "schema": "asmp9-v0.53-verification-registration-v1",
        "protocol_id": (
            "asmp9-aggregate-randomized-subset-insufficiency-v0.53"
        ),
        "source_commit": commit,
        "source_sha256": {
            relative: sha256(REPO / relative)
            for relative in SOURCE_FILES
        },
        "expected_test_count": 9,
        "expected_family_size": 10,
        "family": {
            "alpha": "1/2",
            "reports": ["0", "1"],
            "reference_weights": ["1/2", "1/2"],
            "risk": "1",
            "p_numerators_over_20": list(range(11, 21)),
            "common_subset_table": ["0", "1", "0", "1"],
            "deterministic_value": "1/2",
            "randomized_formula": "1/(4p)",
        },
        "primary_witness": {
            "p_first": "3/5",
            "p_second": "9/10",
            "first_randomized_value": "5/12",
            "second_randomized_value": "5/18",
        },
        "resource_caps": {
            "seconds": 60,
            "peak_working_set_bytes": 268435456,
            "workers": 1,
        },
        "test_command": (
            "python -m pytest -q -p no:cacheprovider "
            + PREFIX
            + "test_aggregate_randomized.py "
            + PREFIX
            + "test_verifier_v0_53.py"
        ),
        "verification_command": (
            "python "
            + PREFIX
            + "verify_theorems_v0_53.py"
        ),
        "claim_boundary": (
            "Exact finite subset-table insufficiency inside classical "
            "randomized confidence theory; no novelty, operational "
            "desirability, continuous or strategic robustness, physical "
            "preference-channel validation, or ASMP-9 resolution."
        ),
    }
    encoded = (
        json.dumps(registration, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    if OUTPUT.exists():
        if OUTPUT.read_bytes() != encoded:
            raise FileExistsError(
                "registration exists with different bytes"
            )
    else:
        OUTPUT.write_bytes(encoded)
    print(sha256(OUTPUT))


if __name__ == "__main__":
    main()
