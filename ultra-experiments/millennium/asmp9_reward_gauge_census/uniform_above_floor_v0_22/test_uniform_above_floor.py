import itertools
from fractions import Fraction

import pytest

from uniform_above_floor import (
    backman_parameters,
    backman_tutte_availability,
    microtrial_availability,
    weighted_availability_exhaustive,
)


TRIANGLE = ((0, 1), (1, 2), (2, 0))
DIAMOND = ((0, 1), (1, 2), (2, 0), (0, 3), (3, 2))
THETA = (
    (0, 2),
    (2, 1),
    (0, 3),
    (3, 1),
    (0, 4),
    (4, 1),
)
K4 = tuple(itertools.combinations(range(4), 2))


@pytest.mark.parametrize(
    ("node_count", "edges"),
    [(3, TRIANGLE), (4, DIAMOND), (5, THETA), (4, K4)],
)
@pytest.mark.parametrize("trial_count", [1, 2, 3, 4])
def test_backman_formula_matches_status_census(
    node_count: int,
    edges: tuple[tuple[int, int], ...],
    trial_count: int,
) -> None:
    assert weighted_availability_exhaustive(
        node_count, edges, trial_count
    ) == backman_tutte_availability(
        node_count, edges, trial_count
    )


@pytest.mark.parametrize("trial_count", [1, 2, 3, 4, 8])
def test_every_uniform_count_lies_on_h_minus_one(
    trial_count: int,
) -> None:
    _, x_value, y_value = backman_parameters(trial_count)
    assert (x_value - 1) * (y_value - 1) == -1


def test_minimal_above_floor_point_is_two_thirds_four() -> None:
    z, x_value, y_value = backman_parameters(2)
    assert z == Fraction(1, 4)
    assert x_value == Fraction(2, 3)
    assert y_value == 4


@pytest.mark.parametrize("trial_count", [1, 2, 3])
def test_triangle_microtrials_match_both_exact_routes(
    trial_count: int,
) -> None:
    micro = microtrial_availability(3, TRIANGLE, trial_count)
    assert micro == weighted_availability_exhaustive(
        3, TRIANGLE, trial_count
    )
    assert micro == backman_tutte_availability(
        3, TRIANGLE, trial_count
    )

