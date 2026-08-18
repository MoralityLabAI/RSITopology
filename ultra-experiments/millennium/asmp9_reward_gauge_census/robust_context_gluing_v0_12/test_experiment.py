from __future__ import annotations

from experiment import run_exact_witness, run_fresh_cells


def test_exact_witness_matches_registered_values() -> None:
    assert run_exact_witness()["exact_match"]


def test_burned_small_cells_exercise_every_control() -> None:
    result = run_fresh_cells(
        {
            "seed": 12,
            "count": 32,
            "item_count": 5,
            "context_count": 2,
            "edges_per_context": 4,
            "tolerance": 1e-8,
        }
    )
    assert result["actual_count"] == 32
    for field in (
        "pythagorean_mismatch_count",
        "dimension_mismatch_count",
        "shared_control_mismatch_count",
        "local_projection_mismatch_count",
        "radius_optimality_mismatch_count",
        "underquery_mismatch_count",
        "orthonormal_mismatch_count",
        "normalized_bound_mismatch_count",
        "cycle_basis_mismatch_count",
    ):
        assert result[field] == 0
    assert result["locally_scalar_gluing_positive_count"] > 0
