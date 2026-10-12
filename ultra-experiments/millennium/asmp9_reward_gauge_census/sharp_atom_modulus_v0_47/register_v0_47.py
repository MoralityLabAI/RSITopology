"""Create the write-once ASMP-9 v0.47 preregistration."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

SEALED = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "decision_relative_access_v0_38/relative_deficiency.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sequential_risk_access_v0_41/sequential_access.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/allocation_design.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/audit_formula_universe.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/coupled_uncertainty.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sharp_atom_modulus_v0_47/README.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sharp_atom_modulus_v0_47/PRIOR_ART_GATE_v0_47.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sharp_atom_modulus_v0_47/PROTOCOL_v0_47.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sharp_atom_modulus_v0_47/THEOREM_DRAFT_v0_47.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sharp_atom_modulus_v0_47/environment_lock_v0_47.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sharp_atom_modulus_v0_47/sharp_atom_modulus.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sharp_atom_modulus_v0_47/test_sharp_atom_modulus.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sharp_atom_modulus_v0_47/run_confirmation_v0_47.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sharp_atom_modulus_v0_47/verify_result_v0_47.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sharp_atom_modulus_v0_47/build_release_v0_47.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def main() -> None:
    for relative in SEALED:
        path = REPO / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", relative],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        if tracked.returncode:
            raise RuntimeError(f"sealed file is not tracked: {relative}")
        dirty = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=REPO,
        )
        if dirty.returncode:
            raise RuntimeError(
                f"sealed file differs from implementation commit: {relative}"
            )

    payload = {
        "protocol_id": "asmp9-sharp-atom-modulus-v0.47",
        "version": "0.47",
        "status": "registered_before_confirmation",
        "registered_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "implementation_commit": git("rev-parse", "HEAD"),
        "expected_status": (
            "sharp_atom_modulus_established_"
            "allocation_ranking_changed"
        ),
        "expected_test_count": 15,
        "test_command": (
            "python -m pytest -q ultra-experiments/millennium/"
            "asmp9_reward_gauge_census/sharp_atom_modulus_v0_47/"
            "test_sharp_atom_modulus.py"
        ),
        "frozen_universe": {
            "targets": 4,
            "queries": ["root", "left", "right"],
            "horizon": 2,
            "symbolic_policy_count": 3748,
            "total_budget": 72,
            "alpha": "1/20",
            "statistic": "total_observed_calibration_errors",
            "confidence_class": (
                "deterministic nondecreasing direct upper bounds"
            ),
            "strict_eligibility": "P_theta(T<=t)>alpha",
            "levels": [
                "0",
                "1/50",
                "1/25",
                "1/20",
                "3/50",
                "2/25",
                "1/10",
                "3/25",
                "13/100",
                "7/50",
                "3/20",
            ],
            "parameter_count": 1331,
            "mandatory_counts": {
                "30,21,21": 113,
                "70,1,1": 281,
                "24,24,24": 111,
            },
        },
        "frozen_designs": {
            "four_class_directed": [30, 21, 21],
            "root_directed": [70, 1, 1],
            "uniform": [24, 24, 24],
        },
        "frozen_predictions": {
            "lower_equals_upper_all_rows": True,
            "all_moduli_nonzero": True,
            "classification_uniform_better_than_directed": True,
            "root_directed_better_than_uniform": True,
            "method_of_types_strictly_above_sharp": True,
            "rectangle_strictly_above_method_of_types": True,
            "zero_boundary_equalities": True,
            "radius_control_risks": ["1/10", "19/100"],
        },
        "development_disclosure": {
            "burned_total_budget": 66,
            "burned_coarse_grid_sha256": (
                "d41f441c4c7e2d26b6fcc2f3645fe742206b2ce2d"
                "6748020ffdc9007e10cf316"
            ),
            "burned_targeted_grid_sha256": (
                "98dba1dff0acfcce4d75cceaa499a41a68aac97d"
                "cd30d6ecbbb07be1711f4949"
            ),
            "burned_outputs_claim_eligible": False,
        },
        "resource_ceiling": {
            "seconds": 180,
            "peak_aggregate_working_set_bytes": 1073741824,
            "worker_processes": 4,
        },
        "source_sha256": {
            relative: sha256(REPO / relative)
            for relative in SEALED
        },
        "claim_boundary": (
            "Classical finite confidence theory specialized to one "
            "registered all-zero atom, total-error ordering, finite "
            "shared-BSC grid, complete horizon-two adaptive policy class, "
            "and two decision risks. Not a globally optimal statistic, "
            "randomized-confidence theorem, continuous minimax rate, "
            "strategic robustness result, real preference-access "
            "validation, or ASMP-9 resolution."
        ),
    }
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    output = HERE / "registration_v0_47.json"
    if output.exists():
        if output.read_bytes() != encoded:
            raise RuntimeError("write-once registration mismatch")
    else:
        output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "path": output.relative_to(REPO).as_posix(),
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "implementation_commit": payload[
                    "implementation_commit"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
