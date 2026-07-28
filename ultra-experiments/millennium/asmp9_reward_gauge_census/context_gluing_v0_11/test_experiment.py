from __future__ import annotations

import random

from experiment import (
    contexts_from_masks,
    graph_from_mask,
    random_contexts,
    run_random_cells,
    run_tuple_census,
)


def test_graph_mask_round_trip_shape() -> None:
    assert graph_from_mask(3, 0) == ()
    assert graph_from_mask(3, 7) == ((0, 1), (0, 2), (1, 2))
    contexts = contexts_from_masks(3, (1, 2))
    assert contexts[0].edges == ((0, 1),)
    assert contexts[1].edges == ((0, 2),)


def test_random_contexts_are_reproducible() -> None:
    assert random_contexts(5, 3, random.Random(7)) == random_contexts(
        5, 3, random.Random(7)
    )


def test_small_tuple_census_matches_all_rank_formulas() -> None:
    result = run_tuple_census(
        {
            "item_count": 3,
            "context_count": 2,
            "maximum_tuple_count": 1000,
        }
    )
    assert result["tuple_count"] == 64
    assert result["rank_formula_mismatch_count"] == 0
    assert result["live_tuple_count"] > 0
    assert result["forced_by_design_tuple_count"] > 0


def test_random_cells_exercise_total_decision() -> None:
    result = run_random_cells(
        {
            "seed": 11,
            "count": 64,
            "minimum_items": 3,
            "maximum_items": 6,
            "minimum_contexts": 2,
            "maximum_contexts": 4,
        }
    )
    assert result["actual_count"] == 64
    assert result["rank_formula_mismatch_count"] == 0
    assert result["basis_dimension_mismatch_count"] == 0
    assert result["witness_existence_mismatch_count"] == 0
    assert result["shared_control_mismatch_count"] == 0
    assert result["exact_decision_mismatch_count"] == 0
    assert result["local_failure_control_count"] > 0
    assert result["local_failure_mismatch_count"] == 0
    assert set(result["status_counts"]) == {
        "shared_scalar_forced_by_design",
        "shared_scalar_refuted",
        "shared_scalar_verified",
    }
