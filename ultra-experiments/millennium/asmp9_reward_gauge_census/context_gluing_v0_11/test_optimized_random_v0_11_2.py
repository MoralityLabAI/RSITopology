from __future__ import annotations

import pytest

from experiment import run_random_cells
from optimized_random_v0_11_2 import (
    fast_dimensions,
    gf2_rank,
    run_random_cells_fast,
)


def test_gf2_rank() -> None:
    assert gf2_rank(()) == 0
    assert gf2_rank((0b0011, 0b0110, 0b0101)) == 2
    assert gf2_rank((0b0001, 0b0010, 0b0100, 0b1000)) == 4


@pytest.mark.parametrize(
    "spec",
    (
        {
            "seed": 11,
            "count": 64,
            "minimum_items": 3,
            "maximum_items": 6,
            "minimum_contexts": 2,
            "maximum_contexts": 4,
        },
        {
            "seed": 1101101,
            "count": 4,
            "minimum_items": 5,
            "maximum_items": 9,
            "minimum_contexts": 2,
            "maximum_contexts": 5,
        },
    ),
)
def test_fast_random_cells_match_literal_burned_cells(
    spec: dict[str, int],
) -> None:
    literal = run_random_cells(spec)
    optimized = run_random_cells_fast(spec)
    optimized_shared = {
        key: value
        for key, value in optimized.items()
        if key != "implementation"
    }
    assert optimized_shared == literal
