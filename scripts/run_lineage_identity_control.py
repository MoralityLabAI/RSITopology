"""Unit-scale occupancy-matched, low-lineage synthetic construction."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.discovery import (
    DiscoveryConfig,
    discover_consensus_bands,
    evaluate_discovery,
    subspace_lineage,
)
from rsi_topology.synthetic import build_fixture


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/lineage_identity_control_unit.json"),
    )
    return parser.parse_args()


def planted_overlap(planted: np.ndarray, basis: np.ndarray) -> float:
    if basis.shape[1] == 0:
        return 0.0
    return float(np.linalg.norm(planted.T @ basis, ord="fro") ** 2 / basis.shape[1])


def main() -> None:
    args = parse_args()
    fixture_args = {
        "seed": 20260711,
        "contexts": 4,
        "candidates_per_context": 24,
        "dimension": 24,
        "planted_rank": 6,
        "geometry_noise": 0.08,
    }
    reference = build_fixture(**fixture_args, lineage_rotation_radians=0.0)
    rotated = build_fixture(
        **fixture_args, lineage_rotation_radians=float(np.pi / 2)
    )
    config = DiscoveryConfig(
        minimum_consensus_rank=4,
        maximum_consensus_rank=12,
        chunk_rows=24,
    )
    reference_bands = discover_consensus_bands(reference.laplacians, config)
    rotated_bands = discover_consensus_bands(rotated.laplacians, config)
    reference_low = reference_bands["low"]
    rotated_low = rotated_bands["low"]
    reference_result = evaluate_discovery(
        laplacians=reference.laplacians,
        vectors=reference.vectors,
        baseline_covariates=reference.baseline_covariates,
        outcomes=reference.outcomes,
        groups=reference.groups,
        config=config,
    )
    rotated_result = evaluate_discovery(
        laplacians=rotated.laplacians,
        vectors=rotated.vectors,
        baseline_covariates=rotated.baseline_covariates,
        outcomes=rotated.outcomes,
        groups=rotated.groups,
        config=config,
    )
    lineage = subspace_lineage(reference_low.basis, rotated_low.basis)
    occupancy_difference = float(
        np.max(np.abs(reference_low.occupancies - rotated_low.occupancies))
    )
    vectors_identical = bool(np.array_equal(reference.vectors, rotated.vectors))
    outcomes_identical = bool(np.array_equal(reference.outcomes, rotated.outcomes))
    receipt = {
        "control_id": "occupancy-matched-low-lineage-unit-v0.1",
        "status": "unit_fixture_validation_only",
        "construction": (
            "One common orthogonal rotation conjugates every context operator, "
            "preserving every consensus occupancy while rotating the low-band "
            "identity away from the planted outcome subspace."
        ),
        "claim_boundary": (
            "Synthetic construction validation only. It shows that lineage can "
            "separate identity from occupancy and band labels by construction; "
            "it does not establish real-model incremental value."
        ),
        "fixture": fixture_args,
        "reference": {
            "selected_band": reference_result.geometry.get("selected_band"),
            "rank": reference_low.rank,
            "minimum_occupancy": reference_low.minimum_occupancy,
            "planted_overlap": planted_overlap(
                reference.planted_basis, reference_low.basis
            ),
            "policy_passed": reference_result.policy["passed"],
            "edit_passed": reference_result.direct_edit["passed"],
        },
        "rotated": {
            "selected_band": rotated_result.geometry.get("selected_band"),
            "rank": rotated_low.rank,
            "minimum_occupancy": rotated_low.minimum_occupancy,
            "planted_overlap": planted_overlap(rotated.planted_basis, rotated_low.basis),
            "policy_passed": rotated_result.policy["passed"],
            "edit_passed": rotated_result.direct_edit["passed"],
        },
        "maximum_occupancy_difference": occupancy_difference,
        "candidate_vectors_identical": vectors_identical,
        "outcomes_identical": outcomes_identical,
        "lineage": lineage,
    }
    receipt["passed"] = bool(
        reference_result.geometry.get("selected_band") == "low"
        and rotated_result.geometry.get("selected_band") == "low"
        and reference_low.rank == rotated_low.rank
        and occupancy_difference <= 1e-10
        and vectors_identical
        and outcomes_identical
        and lineage["mean_chordal_lineage"] <= 0.01
        and receipt["reference"]["planted_overlap"] >= 0.95
        and receipt["rotated"]["planted_overlap"] <= 0.05
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
