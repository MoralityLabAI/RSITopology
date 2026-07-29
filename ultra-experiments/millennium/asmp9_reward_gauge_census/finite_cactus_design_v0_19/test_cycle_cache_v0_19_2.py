from fractions import Fraction

from cycle_cache_v0_19_2 import (
    optimize_cycle_totals_cached_independent,
)
from finite_cactus_design import (
    optimize_cactus_dp,
    optimize_cycle_totals_exhaustive,
)


def test_cached_independent_matches_burned_quad_cell() -> None:
    lengths = (4, 6, 8, 11)
    total = 46
    bridges = 2
    epsilon = Fraction(4, 17)
    cached = optimize_cycle_totals_cached_independent(
        lengths, total, epsilon, bridges
    )
    dynamic = optimize_cactus_dp(lengths, total, epsilon, bridges)
    assert cached.value == dynamic.value
    assert cached.cycle_totals == dynamic.cycle_totals
    assert cached.independent_cycle_values_evaluated < (
        cached.allocations_evaluated * len(lengths)
    )


def test_cached_independent_matches_original_small_cells() -> None:
    cells = (
        ((3, 3), 10, 0, Fraction(1, 4)),
        ((3, 4), 12, 0, Fraction(1, 10)),
        ((5, 6, 8), 31, 1, Fraction(3, 11)),
    )
    for lengths, total, bridges, epsilon in cells:
        cached = optimize_cycle_totals_cached_independent(
            lengths, total, epsilon, bridges
        )
        original = optimize_cycle_totals_exhaustive(
            lengths, total, epsilon, bridges
        )
        assert cached.value == original.value
        assert cached.cycle_totals == original.cycle_totals


def test_cached_independent_rejects_invalid_inputs() -> None:
    for lengths, total, bridges in (
        ((), 10, 0),
        ((2, 3), 10, 0),
        ((3, 3), 5, 0),
        ((3,), 3, -1),
    ):
        try:
            optimize_cycle_totals_cached_independent(
                lengths, total, Fraction(1, 4), bridges
            )
        except ValueError:
            pass
        else:
            raise AssertionError((lengths, total, bridges))
