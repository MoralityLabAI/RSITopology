from __future__ import annotations

from fractions import Fraction

from .finite_upper_bound import (
    binomial_tail,
    fixed_design,
    optimize_midpoint_grid,
)


def test_binomial_tail_is_exact_on_small_known_case() -> None:
    assert binomial_tail(2, 1, Fraction(1, 2), True) == Fraction(3, 4)
    assert binomial_tail(2, 1, Fraction(1, 2), False) == Fraction(1, 4)


def test_frozen_constructive_design_is_uniformly_delta_correct() -> None:
    design = fixed_design(return_blocks=32, mixture_blocks=47)
    assert design.return_channel.samples == 64
    assert design.mechanics.samples == 64
    assert design.mixture.samples == 3196
    assert design.mixture.threshold == 1645
    assert design.total_queries == 3324
    assert design.errors.worst < Fraction(1, 20)
    assert design.errors.worst == design.errors.base


def test_exact_midpoint_grid_search_returns_frozen_design() -> None:
    design = optimize_midpoint_grid(Fraction(1, 20))
    assert design.return_channel.samples == 64
    assert design.mixture.samples == 3196
    assert design.total_queries == 3324
