from fractions import Fraction
from pathlib import Path
import sys

import pytest


HERE = Path(__file__).resolve().parent
V03 = HERE.parent / "width_theorem_v0_3"
sys.path.insert(0, str(V03))

from width_theorem import dot, lower_witness, sharp_width  # noqa: E402


def possible_signs(score: int, delta: Fraction) -> set[int]:
    low = Fraction(score) - delta
    high = Fraction(score) + delta
    values = set()
    if low < 0:
        values.add(-1)
    if low <= 0 <= high:
        values.add(0)
    if high > 0:
        values.add(1)
    return values


def tie_query(bound: int) -> tuple[int, int]:
    return (0, 1) if bound == 1 else (bound - 2, -(bound - 1))


@pytest.mark.parametrize("bound", [1, 2, 8, 32])
def test_zero_endpoint_has_narrow_tie_separator(bound: int) -> None:
    first, second = lower_witness(2, bound)
    query = tie_query(bound)
    scores = (dot(query, first), dot(query, second))
    assert 0 in scores
    assert scores[0] != scores[1]
    assert max(map(abs, query)) < sharp_width(bound)
    assert possible_signs(scores[0], Fraction(0)).isdisjoint(
        possible_signs(scores[1], Fraction(0))
    )


@pytest.mark.parametrize("bound", [1, 2, 8, 32])
def test_same_tie_query_is_not_robust_at_positive_delta(bound: int) -> None:
    first, second = lower_witness(2, bound)
    query = tie_query(bound)
    scores = (dot(query, first), dot(query, second))
    assert not possible_signs(scores[0], Fraction(1, 2)).isdisjoint(
        possible_signs(scores[1], Fraction(1, 2))
    )

