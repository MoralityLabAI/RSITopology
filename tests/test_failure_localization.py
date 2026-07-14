from __future__ import annotations

import numpy as np

from rsi_topology.failure_localization import (
    balanced_axis_decomposition,
    fragility_curve,
    heldout_retention_rows,
    leave_one_level_out,
    projector_from_signature,
    spectral_endpoint,
)


def test_spectral_endpoint_distinguishes_floor_gap_and_pass() -> None:
    passed = spectral_endpoint(
        np.array([4.0, 2.0, 0.5]),
        rank=1,
        relative_floor=1e-4,
        minimum_boundary_gap_ratio=1.25,
    )
    unresolved = spectral_endpoint(
        np.array([4.0, 3.8, 0.5]),
        rank=1,
        relative_floor=1e-4,
        minimum_boundary_gap_ratio=1.25,
    )
    below = spectral_endpoint(
        np.array([4.0, 1e-5, 1e-6]),
        rank=2,
        relative_floor=1e-4,
        minimum_boundary_gap_ratio=1.25,
    )
    assert passed["status"] == "local_endpoint_pass"
    assert unresolved["status"] == "unresolved_boundary"
    assert below["status"] == "below_spectral_floor"


def test_projector_and_heldout_rows_reproduce_known_retention() -> None:
    signature = np.array([[3.0, 0.0], [0.0, 1.0]])
    projector = projector_from_signature(signature, rank=1)
    assert np.allclose(projector, np.diag([1.0, 0.0]))
    tilted = np.array([[np.sqrt(0.8)], [np.sqrt(0.2)]])
    tilted_projector = tilted @ tilted.T
    projectors = {
        "a": projector,
        "b": projector,
        "c": tilted_projector,
        "d": projector,
    }
    folds = [
        ("left->right", ["a", "b"], ["c"]),
        ("right->left", ["c", "d"], ["a", "b", "d"]),
    ]
    rows, receipts = heldout_retention_rows(
        projectors,
        folds,
        rank=1,
        minimum_consensus_gap_ratio=1.0,
    )
    assert len(rows) == 4
    assert len(receipts) == 2
    assert abs(rows[0]["worst_direction_retention"] - 0.8) < 1e-12
    assert rows[0]["gauge_invariant_energy_retention"] == rows[0][
        "worst_direction_retention"
    ]


def test_fragility_curve_crossing_is_derived_from_order_statistics() -> None:
    result = fragility_curve([0.01, 0.02, 0.5, 0.8], threshold=0.1)
    assert result["cells_at_or_below_threshold"] == 2
    assert result["exclusions_required_to_cross_threshold"] == 2
    assert result["remaining_fraction_at_crossing"] == 0.5
    assert result["points"][2]["retention_floor"] == 0.5


def test_balanced_axis_decomposition_and_leave_one_level_out() -> None:
    rows = [
        {"prompt": prompt, "replica": replica, "checkpoint": checkpoint, "value": value}
        for prompt, prompt_effect in (("p0", 0.0), ("p1", 2.0))
        for replica, replica_effect in (("r0", 0.0), ("r1", 1.0))
        for checkpoint, checkpoint_effect in ((1, 0.0), (2, 0.5))
        for value in (prompt_effect + replica_effect + checkpoint_effect,)
    ]
    result = balanced_axis_decomposition(
        rows,
        value_field="value",
        axes=("prompt", "replica", "checkpoint"),
    )
    fractions = result["axes"]
    assert fractions["prompt"]["fraction_total"] > fractions["replica"][
        "fraction_total"
    ]
    assert result["residual_sum_squares"] < 1e-12
    exclusions = leave_one_level_out(
        rows,
        value_field="value",
        axis="prompt",
        threshold=0.25,
    )
    by_level = {row["excluded_level"]: row for row in exclusions}
    assert by_level["p0"]["remaining_floor"] == 2.0
    assert by_level["p1"]["remaining_floor"] == 0.0
