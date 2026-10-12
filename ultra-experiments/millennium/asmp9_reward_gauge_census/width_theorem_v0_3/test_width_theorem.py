from pathlib import Path
import itertools
import sys

import pytest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from width_theorem import (  # noqa: E402
    any_separator_below_sharp_width,
    construct_separator,
    dot,
    lower_witness,
    primitive_rays,
    sharp_width,
)


@pytest.mark.parametrize(
    ("bound", "expected"), [(1, 2), (2, 3), (3, 5), (4, 7)]
)
def test_sharp_width_formula(bound: int, expected: int) -> None:
    assert sharp_width(bound) == expected


@pytest.mark.parametrize("dimension", [2, 3, 4])
@pytest.mark.parametrize("bound", [1, 2])
def test_constructed_separator_on_full_small_registry(
    dimension: int, bound: int
) -> None:
    rays = primitive_rays(dimension, bound)
    for first, second in itertools.combinations(rays, 2):
        query = construct_separator(first, second, bound)
        assert max(map(abs, query)) <= sharp_width(bound)
        assert dot(query, first) * dot(query, second) < 0


@pytest.mark.parametrize("bound", [1, 2, 3, 4, 5, 6])
def test_lower_witness_has_no_narrower_separator(bound: int) -> None:
    assert not any_separator_below_sharp_width(2, bound)


@pytest.mark.parametrize("bound", [1, 2, 3, 4])
def test_lower_witness_is_primitive_and_bounded(bound: int) -> None:
    first, second = lower_witness(3, bound)
    assert max(map(abs, first + second)) <= bound
    query = construct_separator(first, second, bound)
    assert max(map(abs, query)) == sharp_width(bound)

