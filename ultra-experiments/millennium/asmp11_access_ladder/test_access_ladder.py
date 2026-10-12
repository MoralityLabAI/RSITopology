from fractions import Fraction

from access_ladder import (
    N_VARIABLES,
    Mechanism,
    detector_advantage,
    mechanisms,
    nonzero_signature_entries,
    query_upper_bound,
    simulator_contains,
)


def test_registered_ensemble_count() -> None:
    assert sum(len(mechanisms(k)) for k in range(2, 7)) == 114


def test_sharp_observation_intervention_tradeoff() -> None:
    for degree in range(2, 7):
        for order in range(7):
            for interventions in range(7):
                expected = Fraction(int(order + interventions >= degree))
                assert detector_advantage(degree, order, interventions) == expected


def test_specific_parity_is_invisible_then_visible() -> None:
    mechanism = Mechanism((0, 1, 2, 3), 1)
    assert not nonzero_signature_entries(mechanism, 1, 2)
    assert nonzero_signature_entries(mechanism, 1, 3)


def test_access_lattice_simulation() -> None:
    mechanism = Mechanism((0, 2, 4, 5), -1)
    assert simulator_contains(mechanism, 1, 1, 2, 3)


def test_query_cost_is_monotone_coordinatewise() -> None:
    for order in range(N_VARIABLES):
        for interventions in range(N_VARIABLES):
            base = query_upper_bound(order, interventions)
            assert query_upper_bound(order + 1, interventions) >= base
            assert query_upper_bound(order, interventions + 1) >= base
