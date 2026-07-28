from __future__ import annotations

import math

import pytest

from finite_sample import theorem_width
from information_design import (
    bhattacharyya_information,
    mle_union_bound_samples,
    solve_information_design,
)


@pytest.mark.parametrize("eta", [0.0, 0.1, 0.25, 0.49])
def test_information_ordering(eta: float) -> None:
    tie_strict = bhattacharyya_information(0, 1, eta)
    strict_opposite = bhattacharyya_information(-1, 1, eta)
    assert tie_strict > 0
    assert strict_opposite >= tie_strict


@pytest.mark.parametrize("bound", [3, 4, 5])
def test_design_turns_positive_at_exact_width(bound: int) -> None:
    critical = theorem_width(bound)
    below = solve_information_design(2, bound, critical - 1, 0.1)
    at = solve_information_design(2, bound, critical, 0.1)
    assert below.status == "zero"
    assert below.minimum_information <= 1e-10
    assert at.status == "positive"
    assert at.minimum_information > 1e-10


def test_union_bound_is_finite_only_for_live_design() -> None:
    dead = solve_information_design(2, 4, 2, 0.1)
    live = solve_information_design(2, 4, 3, 0.1)
    assert math.isinf(
        mle_union_bound_samples(
            dead.hypothesis_count, dead.minimum_information, 0.05
        )
    )
    assert mle_union_bound_samples(
        live.hypothesis_count, live.minimum_information, 0.05
    ) > 0
