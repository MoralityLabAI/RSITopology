"""Write-once prospective registration for ASMP-9 v0.52."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT = HERE / "verification_registration_v0_52.json"
RESULT = HERE / "VERIFY_RESULT_v0_52.json"

SOURCE_FILES = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "direct_map_completeness_v0_52/PRIOR_ART_GATE_v0_52.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "direct_map_completeness_v0_52/THEOREM_DRAFT_v0_52.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "direct_map_completeness_v0_52/VERIFICATION_PROTOCOL_v0_52.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "direct_map_completeness_v0_52/direct_map_completeness.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "direct_map_completeness_v0_52/test_direct_map_completeness.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "direct_map_completeness_v0_52/test_verifier_v0_52.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "direct_map_completeness_v0_52/verify_theorems_v0_52.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "direct_map_completeness_v0_52/register_verification_v0_52.py",
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
        "schema": "asmp9-v0.52-verification-registration-v1",
        "protocol_id": (
            "asmp9-deterministic-direct-map-completeness-v0.52"
        ),
        "source_commit": commit,
        "source_sha256": {
            relative: sha256(REPO / relative)
            for relative in SOURCE_FILES
        },
        "expected_test_count": 11,
        "expected_census": {
            "table_count": 148,
            "candidate_direct_map_count": 3996,
            "valid_direct_map_count": 1494,
            "invalid_direct_map_count": 2502,
            "consistent_order_check_count": 3342,
            "strict_dominance_check_count": 2454,
            "dominance_mismatch_count": 0,
            "buehler_validity_mismatch_count": 0,
            "reference_grid_count": 10,
            "global_optimum_check_count": 1480,
            "global_optimum_mismatch_count": 0,
        },
        "reference_grid": (
            "all positive denominator-six triples summing to one"
        ),
        "controls": {
            "table": [0, 1, 1, 2],
            "order": [0, 1],
            "equality_input": [1, 2],
            "equality_output": [1, 2],
            "strict_input": [2, 2],
            "strict_output": [1, 2],
            "experiment": {
                "alpha": "1/2",
                "risks": [1, 1, 2],
                "probability_rows": [
                    ["1", "0"],
                    ["0", "1"],
                    ["1/2", "1/2"],
                ],
            },
        },
        "resource_caps": {
            "seconds": 120,
            "peak_working_set_bytes": 536870912,
            "workers": 1,
        },
        "test_command": (
            "python -m pytest -q -p no:cacheprovider "
            "ultra-experiments/millennium/"
            "asmp9_reward_gauge_census/"
            "direct_map_completeness_v0_52/"
            "test_direct_map_completeness.py "
            "ultra-experiments/millennium/"
            "asmp9_reward_gauge_census/"
            "direct_map_completeness_v0_52/"
            "test_verifier_v0_52.py"
        ),
        "verification_command": (
            "python ultra-experiments/millennium/"
            "asmp9_reward_gauge_census/"
            "direct_map_completeness_v0_52/"
            "verify_theorems_v0_52.py"
        ),
        "claim_boundary": (
            "Exact finite deterministic direct-map completeness only; "
            "classical Buehler corollary; no novelty, aggregate randomized "
            "coverage, continuous or strategic robustness, physical "
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
