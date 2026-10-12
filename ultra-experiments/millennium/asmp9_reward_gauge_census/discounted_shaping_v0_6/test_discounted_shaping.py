from __future__ import annotations

import random
from fractions import Fraction

import pytest

from discounted_shaping import (
    balanced_component_count,
    boundary_signature,
    component_heights,
    enumerate_oriented_simple_graphs,
    predicted_rank,
    quotient_dimension,
    rational_rank,
    shaping_pairing,
    twisted_incidence,
    weak_components,
)


@pytest.mark.parametrize("gamma", [Fraction(1, 2), Fraction(2, 3)])
@pytest.mark.parametrize("vertex_count", [2, 3, 4])
def test_gain_graph_rank_formula_exhaustive(
    gamma: Fraction, vertex_count: int
) -> None:
    for edges in enumerate_oriented_simple_graphs(vertex_count):
        assert rational_rank(
            twisted_incidence(vertex_count, edges, gamma)
        ) == predicted_rank(vertex_count, edges, gamma)


@pytest.mark.parametrize("vertex_count", [2, 3, 4])
def test_undiscounted_rank_formula_exhaustive(vertex_count: int) -> None:
    for edges in enumerate_oriented_simple_graphs(vertex_count):
        expected = vertex_count - len(weak_components(vertex_count, edges))
        assert predicted_rank(
            vertex_count, edges, Fraction(1)
        ) == expected
        assert rational_rank(
            twisted_incidence(vertex_count, edges, Fraction(1))
        ) == expected


def test_directed_cycle_loses_ordinary_cycle_dimension() -> None:
    edges = ((0, 1), (1, 2), (2, 0))
    assert balanced_component_count(3, edges) == 0
    assert quotient_dimension(3, edges, Fraction(1, 2)) == 0
    assert quotient_dimension(3, edges, Fraction(1)) == 1


def test_equal_length_route_difference_survives() -> None:
    edges = ((0, 1), (1, 3), (0, 2), (2, 3))
    assert component_heights((0, 1, 2, 3), edges) == {
        0: 0,
        1: 1,
        2: 1,
        3: 2,
    }
    assert quotient_dimension(4, edges, Fraction(1, 2)) == 1


def test_unequal_length_shortcut_kills_quotient() -> None:
    edges = ((0, 1), (1, 2), (0, 2))
    assert component_heights((0, 1, 2), edges) is None
    assert quotient_dimension(3, edges, Fraction(1, 2)) == 0


def test_zero_discount_rank_is_source_count() -> None:
    edges = ((0, 1), (0, 2), (3, 2))
    assert predicted_rank(4, edges, Fraction(0)) == 2
    assert rational_rank(
        twisted_incidence(4, edges, Fraction(0))
    ) == 2


def test_telescoping_identity_seeded() -> None:
    rng = random.Random(96001)
    gamma = Fraction(2, 3)
    for _ in range(1000):
        vertex_count = 8
        length = rng.randint(0, 12)
        trajectory = [rng.randrange(vertex_count)]
        trajectory.extend(rng.randrange(vertex_count) for _ in range(length))
        potential = [
            Fraction(rng.randint(-10, 10), rng.randint(1, 7))
            for _ in range(vertex_count)
        ]
        signature = boundary_signature(
            trajectory, vertex_count, gamma
        )
        boundary_value = sum(
            coefficient * value
            for coefficient, value in zip(signature, potential)
        )
        assert shaping_pairing(
            trajectory, potential, gamma
        ) == boundary_value


def test_same_boundary_signature_cancels_shaping() -> None:
    gamma = Fraction(3, 4)
    left = (0, 1, 3)
    right = (0, 2, 3)
    assert boundary_signature(left, 4, gamma) == boundary_signature(
        right, 4, gamma
    )
    potentials = [
        Fraction(7, 3),
        Fraction(-2, 5),
        Fraction(11, 4),
        Fraction(1, 9),
    ]
    assert shaping_pairing(left, potentials, gamma) == shaping_pairing(
        right, potentials, gamma
    )


def test_unequal_horizon_same_endpoint_is_not_invariant() -> None:
    gamma = Fraction(1, 2)
    short = (0, 2)
    long = (0, 1, 2)
    assert boundary_signature(short, 3, gamma) != boundary_signature(
        long, 3, gamma
    )
    potential = [Fraction(0), Fraction(0), Fraction(1)]
    assert shaping_pairing(short, potential, gamma) != shaping_pairing(
        long, potential, gamma
    )
