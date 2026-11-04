from pathlib import Path
from fractions import Fraction
import itertools
import sys

import pytest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from zero_radius_width import (  # noqa: E402
    construct_exact_separator,
    dot,
    farey_fractions,
    lower_witness,
    narrower_exact_separator_exists,
    primitive_rays,
    sharp_zero_width,
    sign,
)


@pytest.mark.parametrize(
    ("bound", "expected"),
    [(1, 1), (2, 1), (3, 2), (4, 3), (8, 7)],
)
def test_width_formula(bound: int, expected: int) -> None:
    assert sharp_zero_width(bound) == expected


@pytest.mark.parametrize("dimension", [2, 3, 4])
@pytest.mark.parametrize("bound", [1, 2, 3])
def test_constructor_on_full_small_registry(
    dimension: int, bound: int
) -> None:
    rays = primitive_rays(dimension, bound)
    for first, second in itertools.combinations(rays, 2):
        query = construct_exact_separator(first, second, bound)
        assert max(map(abs, query)) <= sharp_zero_width(bound)
        assert sign(dot(query, first)) != sign(dot(query, second))


@pytest.mark.parametrize("bound", list(range(1, 17)))
def test_lower_witness_is_sharp(bound: int) -> None:
    assert not narrower_exact_separator_exists(2, bound)


@pytest.mark.parametrize("order", [1, 2, 3, 4, 8])
def test_farey_cells_contain_at_most_one_next_height_fraction(order: int) -> None:
    sequence = farey_fractions(order)
    targets = [
        Fraction(numerator, denominator)
        for denominator in range(1, order + 2)
        for numerator in range(denominator + 1)
    ]
    reduced_targets = sorted(set(targets))
    for left, right in zip(sequence, sequence[1:]):
        interior = [
            value for value in reduced_targets if left < value < right
        ]
        assert len(interior) <= 1


def test_lower_witness_attains_bound() -> None:
    for bound in range(3, 10):
        first, second = lower_witness(3, bound)
        query = construct_exact_separator(first, second, bound)
        assert max(map(abs, query)) == bound - 1
        assert 0 in (dot(query, first), dot(query, second))
