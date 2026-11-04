from fractions import Fraction as Q

from verify_theorems_v0_50 import (
    exhaustive_common,
    monotone_binary_tables,
    positive_denominator_grid,
)


def test_admissible_three_outcome_monotone_count():
    tables = monotone_binary_tables(3)
    assert len(tables) == 19
    assert all(table[0] == 0 for table in tables)


def test_exhaustive_common_detects_reference_switch():
    bounds = (Q(0), Q(0), Q(0), Q(1))
    vertices = (
        (Q(3, 4), Q(1, 4)),
        (Q(1, 4), Q(3, 4)),
    )
    assert not exhaustive_common((bounds,), vertices)


def test_positive_denominator_six_grid_count():
    grid = positive_denominator_grid(6, 3)
    assert len(grid) == 10
    assert all(sum(row, Q(0)) == 1 for row in grid)
    assert all(all(value > 0 for value in row) for row in grid)
