"""Create the write-once ASMP-9 v0.45 registration."""

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
    "sample_allocation_v0_45/PRIOR_ART_GATE_v0_45.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/PROTOCOL_v0_45.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/THEOREM_DRAFT_v0_45.md",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/environment_lock_v0_45.json",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/allocation_design.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/audit_formula_universe.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/test_allocation_design.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/run_confirmation_v0_45.py",
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "sample_allocation_v0_45/verify_result_v0_45.py",
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
        "protocol_id": (
            "asmp9-decision-directed-sample-allocation-v0.45"
        ),
        "version": "0.45",
        "status": "registered_before_confirmation",
        "registered_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "implementation_commit": git("rev-parse", "HEAD"),
        "expected_status": (
            "decision_directed_sample_allocation_established"
        ),
        "expected_test_count": 21,
        "test_command": (
            "python -m pytest -q ultra-experiments/millennium/"
            "asmp9_reward_gauge_census/sample_allocation_v0_45/"
            "test_allocation_design.py"
        ),
        "frozen_universe": {
            "targets": 4,
            "queries": ["root", "left", "right"],
            "shared_flip_parameters": 3,
            "horizon": 2,
            "total_budget": 60,
            "positive_allocations_per_problem": 1711,
            "decision_problems": [
                "4_class_identification",
                "root_group",
                "all_query_serial_control",
            ],
            "alpha": "1/20",
            "method_of_types_formula": (
                "log(3*(n+1)/0.05)/n"
            ),
            "decimal_digits": 12,
            "two_point_grid_denominator": 200,
        },
        "frozen_predictions": {
            "classification_optimum": [26, 17, 17],
            "classification_minimum_relative_improvement": 0.01,
            "root_group_optimum": [58, 1, 1],
            "root_group_minimum_relative_improvement": 0.35,
            "serial_control_optimum": [20, 20, 20],
            "constructive_underbound_count": 0,
        },
        "development_disclosure": {
            "burned_total_budget": 54,
            "confirmation_total_budget": 60,
            "burned_classification_formula_mismatches": 92,
            "burned_constructive_underbounds": 0,
            "burned_outputs_claim_eligible": False,
        },
        "resource_ceiling": {
            "seconds": 420,
            "peak_aggregate_working_set_bytes": 1342177280,
            "worker_processes": 4,
        },
        "source_sha256": {
            relative: sha256(REPO / relative)
            for relative in SEALED
        },
        "claim_boundary": (
            "Exact finite integer allocation under one iid shared-flip "
            "calibration grammar, with inherited adaptive risk polytopes, "
            "policy-specific KL/Pinsker boxes, exact deficiency LPs, a "
            "matched serial control, and a registered-grid two-point lower "
            "benchmark. Not a target-dependent cell-allocation theorem, "
            "general optimal design, minimax deficiency rate, efficient "
            "policy search result, real preference-channel validation, or "
            "ASMP-9 resolution."
        ),
    }
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    output = HERE / "registration_v0_45.json"
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
