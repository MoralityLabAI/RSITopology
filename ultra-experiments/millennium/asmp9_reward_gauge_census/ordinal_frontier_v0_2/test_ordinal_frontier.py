from fractions import Fraction
from pathlib import Path
import sys

import pytest


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ordinal_frontier import (  # noqa: E402
    build_coverage,
    possible_signs,
    primitive_vectors,
    robustly_separates,
    solve_minimum_query_cover,
    vector_gcd,
)


def test_primitive_reward_rays_keep_opposite_orientation() -> None:
    rays = primitive_vectors(2, 2, canonical_orientation=False)
    assert (1, 0) in rays
    assert (-1, 0) in rays
    assert (2, 0) not in rays
    assert all(vector_gcd(ray) == 1 for ray in rays)


def test_query_normals_deduplicate_sign_orientation() -> None:
    queries = primitive_vectors(2, 1, canonical_orientation=True)
    assert len(queries) == 4
    assert (1, 0) in queries
    assert (-1, 0) not in queries


@pytest.mark.parametrize(
    ("score", "delta", "expected"),
    [
        (0, Fraction(0), {0}),
        (1, Fraction(0), {1}),
        (-1, Fraction(0), {-1}),
        (0, Fraction(1, 2), {-1, 0, 1}),
        (1, Fraction(1, 2), {1}),
        (-1, Fraction(1, 2), {-1}),
        (1, Fraction(1), {0, 1}),
        (-1, Fraction(1), {-1, 0}),
    ],
)
def test_possible_signs(score: int, delta: Fraction, expected: set[int]) -> None:
    assert possible_signs(score, delta) == expected


def test_positive_scale_sign_invariance_and_opposite_separation() -> None:
    query = (1, -1)
    assert not robustly_separates(
        query, (1, 0), (2, 0), Fraction(0)
    )
    assert robustly_separates(query, (1, 0), (-1, 0), Fraction(0))


def test_dimension_one_anchor_is_one_query() -> None:
    coverage = build_coverage(1, 1, 1, Fraction(0))
    assert coverage.complete
    result = solve_minimum_query_cover(coverage, time_limit_seconds=5)
    assert result.status == "optimal"
    assert result.objective == 1
    assert result.independently_covers_all


def test_query_width_cannot_increase_unresolved_pairs() -> None:
    values = [
        len(build_coverage(2, 2, width, Fraction(1, 2)).unresolved_pair_indices)
        for width in (1, 2, 3)
    ]
    assert values[1] <= values[0]
    assert values[2] <= values[1]


def test_misspecification_cannot_improve_pair_separation() -> None:
    exact = build_coverage(3, 1, 1, Fraction(0))
    perturbed = build_coverage(3, 1, 1, Fraction(1, 2))
    assert len(perturbed.unresolved_pair_indices) >= len(
        exact.unresolved_pair_indices
    )

