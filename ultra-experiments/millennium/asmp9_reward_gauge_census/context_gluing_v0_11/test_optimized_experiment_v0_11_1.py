from __future__ import annotations

import pytest

from experiment import run_tuple_census
from optimized_experiment_v0_11_1 import run_tuple_census_optimized


@pytest.mark.parametrize(
    ("item_count", "context_count", "maximum"),
    ((2, 3, 64), (3, 2, 64), (3, 3, 512), (4, 2, 4096)),
)
def test_optimized_census_matches_literal_burned_cells(
    item_count: int, context_count: int, maximum: int
) -> None:
    spec = {
        "item_count": item_count,
        "context_count": context_count,
        "maximum_tuple_count": maximum,
    }
    literal = run_tuple_census(spec)
    optimized = run_tuple_census_optimized(spec)
    ignored = {"implementation", "precomputed_graph_count"}
    optimized_shared = {
        key: value for key, value in optimized.items() if key not in ignored
    }
    assert optimized_shared == literal
