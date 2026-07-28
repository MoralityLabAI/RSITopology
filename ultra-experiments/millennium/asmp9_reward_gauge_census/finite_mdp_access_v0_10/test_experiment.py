from __future__ import annotations

from experiment import (
    graph_component_count,
    run_deterministic_census,
    run_stochastic_cells,
    run_structured_cells,
    run_trajectory_census,
)
from run_verification import peak_resident_bytes


def test_graph_component_count_includes_isolates() -> None:
    assert graph_component_count(4, ((0, 1),)) == 3


def test_small_deterministic_census_replays() -> None:
    result = run_deterministic_census(
        {
            "state_count": 2,
            "action_count": 2,
            "discount": "1/2",
        }
    )
    assert result["count"] == 16
    assert result["component_distribution"] == {1: 12, 2: 4}
    assert result["rank_mismatch_count"] == 0
    assert result["intersection_mismatch_count"] == 0


def test_stochastic_cells_match_action_rank() -> None:
    result = run_stochastic_cells(
        {
            "seed": 1,
            "count": 32,
            "minimum_states": 2,
            "maximum_states": 4,
            "minimum_actions": 2,
            "maximum_actions": 3,
            "maximum_weight": 7,
            "discounts": ["1/3", "1/2", "3/4"],
        }
    )
    assert result["shaping_rank_mismatch_count"] == 0
    assert result["intersection_mismatch_count"] == 0
    assert result["actual_count"] == 32
    assert set(result["state_distribution"]) == {2, 3, 4}
    assert set(result["action_distribution"]) == {2, 3}
    assert set(result["discount_distribution"]) == {"1/3", "1/2", "3/4"}


def test_structured_cells_close_both_access_routes() -> None:
    result = run_structured_cells(
        {
            "state_counts": [2, 3, 4],
            "transition_discount": "2/3",
            "discount_pair": ["1/3", "3/4"],
        }
    )
    assert result["mismatch_count"] == 0


def test_trajectory_census_has_tree_threshold() -> None:
    result = run_trajectory_census({"coordinate_count": 4})
    assert result["component_mismatch_count"] == 0
    assert result["minimum_connected_queries"] == 3


def test_peak_resident_measurement_is_live() -> None:
    assert peak_resident_bytes() > 0
