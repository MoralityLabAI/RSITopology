"""Create the write-once ASMP-9 v0.46 preregistration."""

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
    "occupancy_information_v0_44/occupancy_information.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/allocation_design.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/audit_formula_universe.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/README.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/PRIOR_ART_GATE_v0_46.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/PROTOCOL_v0_46.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/THEOREM_DRAFT_v0_46.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/environment_lock_v0_46.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/coupled_uncertainty.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/test_coupled_uncertainty.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/run_confirmation_v0_46.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/verify_result_v0_46.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "coupled_uncertainty_v0_46/build_release_v0_46.py",
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
        "protocol_id": "asmp9-coupled-shared-channel-v0.46",
        "version": "0.46",
        "status": "registered_before_confirmation",
        "registered_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "implementation_commit": git("rev-parse", "HEAD"),
        "expected_status": (
            "coupled_image_conservatism_established_"
            "allocation_unchanged"
        ),
        "expected_test_count": 21,
        "test_command": (
            "python -m pytest -q ultra-experiments/millennium/"
            "asmp9_reward_gauge_census/coupled_uncertainty_v0_46/"
            "test_coupled_uncertainty.py"
        ),
        "frozen_universe": {
            "targets": 4,
            "queries": ["root", "left", "right"],
            "shared_flip_parameters": 3,
            "horizon": 2,
            "symbolic_policy_count": 3748,
            "total_budget": 66,
            "positive_allocations_per_problem": 2080,
            "decision_problems": [
                "4_class_identification",
                "root_group",
            ],
            "alpha": "1/20",
            "method_of_types_formula": (
                "log(3*(n+1)/0.05)/n"
            ),
            "probability_endpoint": (
                "min(1/2,1-exp(-kappa(n)))"
            ),
            "decimal_digits": 12,
        },
        "frozen_predictions": {
            "coupled_classification_optimum": [28, 19, 19],
            "coupled_root_group_optimum": [64, 1, 1],
            "rectangular_classification_optimum": [28, 19, 19],
            "rectangular_root_group_optimum": [64, 1, 1],
            "uniform": [22, 22, 22],
            "strict_conservatism_at_optimum_and_uniform": True,
            "allocation_changed": False,
            "product_rectangle_exact": True,
        },
        "development_disclosure": {
            "burned_total_budget": 60,
            "confirmation_total_budget": 66,
            "burned_coupled_classification_optimum": [26, 17, 17],
            "burned_coupled_root_group_optimum": [58, 1, 1],
            "burned_outputs_claim_eligible": False,
        },
        "resource_ceiling": {
            "seconds": 600,
            "peak_aggregate_working_set_bytes": 1610612736,
            "worker_processes": 4,
        },
        "source_sha256": {
            relative: sha256(REPO / relative)
            for relative in SEALED
        },
        "claim_boundary": (
            "Exact finite coupled-image audit under one iid zero-error "
            "three-parameter symmetric-flip calibration grammar, with a "
            "complete horizon-two adaptive policy class, certified rational "
            "minimax bounds, an inherited rectangular comparator, and an "
            "exact product control. Not a general nonrectangular robust-"
            "control theorem, efficient policy-search result, minimax "
            "confidence theorem, strategic robustness result, real "
            "preference-channel validation, or ASMP-9 resolution."
        ),
    }
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    output = HERE / "registration_v0_46.json"
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

