from fractions import Fraction

import pytest

from nonuniform_multivariate import (
    K4_EDGES,
    K4_HIGH_EDGES,
    K4_LOW_EDGES,
    direct_nonuniform_availability,
    k4_balanced_closed_form,
    k4_balanced_counts,
    k4_balanced_minus_trap_gap,
    k4_m_concavity_deficit,
    k4_neighbor_gap_certificate,
    k4_opposite_pair_numerator,
    k4_trap_closed_form,
    k4_trap_counts,
    multivariate_coefficient,
    multivariate_tutte_availability,
    one_unit_exchange_neighbors,
    oriented_completion_count,
    trial_numerator,
    uniform_backman_availability,
)


GRAPHS = {
    "triangle": (3, ((0, 1), (1, 2), (2, 0))),
    "diamond": (
        4,
        ((0, 1), (1, 2), (2, 0), (1, 3), (3, 2)),
    ),
    "theta": (
        5,
        ((0, 1), (1, 4), (0, 2), (2, 4), (0, 3), (3, 4)),
    ),
    "k4": (4, K4_EDGES),
}


@pytest.mark.parametrize("name", sorted(GRAPHS))
def test_multivariate_identity_matches_direct_ternary_census(
    name: str,
) -> None:
    node_count, edges = GRAPHS[name]
    counts = tuple(1 + (2 * index + 1) % 4 for index in range(len(edges)))
    assert direct_nonuniform_availability(
        node_count, edges, counts
    ) == multivariate_tutte_availability(node_count, edges, counts)


@pytest.mark.parametrize("name", ("triangle", "diamond", "theta"))
def test_every_multivariate_coefficient_counts_completions(
    name: str,
) -> None:
    node_count, edges = GRAPHS[name]
    for mask in range(1 << len(edges)):
        interior = tuple(
            index
            for index in range(len(edges))
            if (mask >> index) & 1
        )
        assert multivariate_coefficient(
            node_count, edges, interior
        ) == oriented_completion_count(node_count, edges, interior)


@pytest.mark.parametrize("name", sorted(GRAPHS))
@pytest.mark.parametrize("trial_count", (1, 2, 3, 5))
def test_uniform_specialization_matches_backman(
    name: str, trial_count: int
) -> None:
    node_count, edges = GRAPHS[name]
    counts = (trial_count,) * len(edges)
    assert multivariate_tutte_availability(
        node_count, edges, counts
    ) == uniform_backman_availability(
        node_count, edges, trial_count
    )


@pytest.mark.parametrize("s", (2, 3, 4, 7))
def test_k4_closed_forms_match_multivariate_numerator(s: int) -> None:
    t = 2**s
    trap = k4_trap_counts(s)
    balanced = k4_balanced_counts(s)
    trap_value = trial_numerator(4, K4_EDGES, trap)
    balanced_value = trial_numerator(4, K4_EDGES, balanced)
    assert trap_value == k4_trap_closed_form(t)
    assert balanced_value == k4_balanced_closed_form(t)
    assert (
        balanced_value - trap_value
        == k4_balanced_minus_trap_gap(t)
        > 0
    )
    assert trap_value == k4_opposite_pair_numerator(t // 2, t, 2 * t)
    assert balanced_value == k4_opposite_pair_numerator(t, t, t)


@pytest.mark.parametrize("s", (2, 3, 5, 8))
def test_k4_trap_is_strict_one_exchange_local_maximum(s: int) -> None:
    t = 2**s
    trap = k4_trap_counts(s)
    trap_value = trial_numerator(4, K4_EDGES, trap)
    neighbors = one_unit_exchange_neighbors(trap, floor=1)
    assert len(neighbors) == (20 if s == 2 else 30)
    for donor, recipient, counts in neighbors:
        label, certified_gap = k4_neighbor_gap_certificate(
            donor, recipient, t
        )
        assert label
        assert certified_gap > 0
        assert (
            trap_value - trial_numerator(4, K4_EDGES, counts)
            == certified_gap
        )


def test_nine_neighbor_factor_classes_cover_all_ordered_moves() -> None:
    labels = {
        k4_neighbor_gap_certificate(donor, recipient, 8)[0]
        for donor in range(6)
        for recipient in range(6)
        if donor != recipient
    }
    assert labels == {
        "low_to_low",
        "low_to_middle",
        "low_to_high",
        "middle_to_low",
        "middle_to_middle",
        "middle_to_high",
        "high_to_low",
        "high_to_middle",
        "high_to_high",
    }


@pytest.mark.parametrize("s", (2, 3, 6))
def test_explicit_m_concavity_exchange_violation(s: int) -> None:
    t = 2**s
    x = k4_trap_counts(s)
    y = k4_balanced_counts(s)
    fx = trial_numerator(4, K4_EDGES, x)
    fy = trial_numerator(4, K4_EDGES, y)
    for high in K4_HIGH_EDGES:
        assert x[high] > y[high]
        for low in K4_LOW_EDGES:
            assert x[low] < y[low]
            x_exchange = list(x)
            y_exchange = list(y)
            x_exchange[high] -= 1
            x_exchange[low] += 1
            y_exchange[high] += 1
            y_exchange[low] -= 1
            deficit = (
                fx
                + fy
                - trial_numerator(4, K4_EDGES, x_exchange)
                - trial_numerator(4, K4_EDGES, y_exchange)
            )
            assert deficit == k4_m_concavity_deficit(t) > 0


def test_known_small_values_are_exact_fractions() -> None:
    triangle = GRAPHS["triangle"]
    assert direct_nonuniform_availability(
        *triangle, (1, 2, 3)
    ) == Fraction(21, 32)
    assert multivariate_tutte_availability(
        *triangle, (2, 4, 2)
    ) == Fraction(107, 128)

