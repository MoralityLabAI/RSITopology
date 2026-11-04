from fractions import Fraction as Q

import pytest

from ordering_modulus import (
    buehler_subset_bounds,
    count_outcomes,
    count_probability,
    coverage_by_parameter,
    cross_costs,
    dynamic_cross_audit,
    dynamic_ordering_census,
    exhaustive_cross_audit,
    exhaustive_ordering_census,
    experiment_rows,
    ordering_cost,
    ordered_bound_vector,
    prefix_probability_tables,
    uniform_parameter_mixture,
)


def test_count_experiment_is_exact():
    parameters = ((Q(0),), (Q(1, 4),))
    outcomes, rows = experiment_rows(parameters, (2,))
    assert outcomes == ((0,), (1,), (2,))
    assert rows[(Q(0),)] == (Q(1), Q(0), Q(0))
    assert rows[(Q(1, 4),)] == (Q(9, 16), Q(3, 8), Q(1, 16))


def test_count_probability_validates_inputs():
    with pytest.raises(ValueError):
        count_probability((Q(3, 4),), (1,), (0,))
    with pytest.raises(ValueError):
        count_probability((Q(1, 4),), (1,), (2,))


def test_subset_probabilities_match_direct_sums():
    probabilities = {
        "a": (Q(1, 4), Q(1, 2), Q(1, 4)),
        "b": (Q(1, 2), Q(1, 4), Q(1, 4)),
    }
    subsets = prefix_probability_tables(probabilities)
    assert subsets["a"][0b011] == Q(3, 4)
    assert subsets["b"][0b101] == Q(3, 4)
    assert subsets["a"][-1] == 1


def test_buehler_subset_bound_uses_strict_alpha():
    probabilities = {
        "low": (Q(1, 20), Q(19, 20)),
        "high": (Q(1, 10), Q(9, 10)),
    }
    subsets = prefix_probability_tables(probabilities)
    bounds = buehler_subset_bounds(
        {"low": Q(1, 10), "high": Q(2, 5)},
        subsets,
        Q(1, 20),
    )
    assert bounds[0b01] == Q(2, 5)
    assert bounds[0b10] == Q(2, 5)


def test_uniform_parameter_mixture_is_probability_law():
    probabilities = {
        "a": (Q(1, 4), Q(3, 4)),
        "b": (Q(1, 2), Q(1, 2)),
    }
    assert uniform_parameter_mixture(probabilities) == (
        Q(3, 8),
        Q(5, 8),
    )


def test_ordering_cost_uses_post_admission_prefix_bound():
    weights = (Q(1, 3), Q(2, 3))
    bounds = (Q(0), Q(1, 10), Q(1, 5), Q(2, 5))
    assert ordering_cost((0, 1), bounds, weights) == (
        Q(1, 3) * Q(1, 10) + Q(2, 3) * Q(2, 5)
    )


def test_ordered_bounds_and_coverage_are_exact():
    probabilities = {
        "low": (Q(1, 4), Q(3, 4)),
        "high": (Q(1, 10), Q(9, 10)),
    }
    risks = {"low": Q(1, 10), "high": Q(2, 5)}
    subsets = prefix_probability_tables(probabilities)
    subset_bounds = buehler_subset_bounds(
        risks, subsets, Q(1, 20)
    )
    reported = ordered_bound_vector((0, 1), subset_bounds)
    coverage = coverage_by_parameter(
        risks, probabilities, reported
    )
    assert min(coverage.values()) >= Q(19, 20)


def test_exhaustive_census_finds_unique_order():
    weights = (Q(1, 2), Q(1, 2))
    bounds = (Q(0), Q(1, 10), Q(1, 5), Q(2, 5))
    result = exhaustive_ordering_census(bounds, weights)
    assert result.order_count == 2
    assert result.optimizers == ((0, 1),)


def test_cross_costs_certify_disjoint_optima():
    weights = (Q(1, 2), Q(1, 2))
    first_bounds = (Q(0), Q(1, 10), Q(1, 5), Q(2, 5))
    second_bounds = (Q(0), Q(1, 5), Q(1, 10), Q(2, 5))
    first = exhaustive_ordering_census(first_bounds, weights)
    second = exhaustive_ordering_census(second_bounds, weights)
    audit = cross_costs(
        first, first_bounds, second, second_bounds, weights
    )
    assert audit["common_optimizer_count"] == 0
    assert Q(audit["first_cross_regret"]) > 0
    assert Q(audit["second_cross_regret"]) > 0


def test_streaming_cross_audit_matches_retained_cross_audit():
    weights = (Q(1, 2), Q(1, 2))
    first_bounds = (Q(0), Q(1, 10), Q(1, 5), Q(2, 5))
    second_bounds = (Q(0), Q(1, 5), Q(1, 10), Q(2, 5))
    first = exhaustive_ordering_census(first_bounds, weights)
    second = exhaustive_ordering_census(second_bounds, weights)
    retained = cross_costs(
        first, first_bounds, second, second_bounds, weights
    )
    streamed = exhaustive_cross_audit(
        first.optimum,
        first_bounds,
        second.optimum,
        second_bounds,
        weights,
    )
    assert streamed == retained


def test_dynamic_census_matches_exhaustive_census():
    weights = (Q(1, 6), Q(1, 3), Q(1, 2))
    bounds = (
        Q(0),
        Q(1, 10),
        Q(1, 5),
        Q(1, 4),
        Q(3, 10),
        Q(7, 20),
        Q(2, 5),
        Q(1, 2),
    )
    exhaustive = exhaustive_ordering_census(bounds, weights)
    dynamic = dynamic_ordering_census(bounds, weights)
    assert dynamic.optimum == exhaustive.optimum
    assert dynamic.optimizer_count == exhaustive.optimizer_count
    assert dynamic.lexicographic_optimizer == exhaustive.optimizers[0]


def test_dynamic_cross_audit_matches_exhaustive_cross_audit():
    weights = (Q(1, 6), Q(1, 3), Q(1, 2))
    first_bounds = (
        Q(0),
        Q(1, 10),
        Q(1, 5),
        Q(1, 4),
        Q(3, 10),
        Q(7, 20),
        Q(2, 5),
        Q(1, 2),
    )
    second_bounds = tuple(reversed(first_bounds))
    first = exhaustive_ordering_census(first_bounds, weights)
    second = exhaustive_ordering_census(second_bounds, weights)
    exhaustive = exhaustive_cross_audit(
        first.optimum,
        first_bounds,
        second.optimum,
        second_bounds,
        weights,
    )
    dynamic = dynamic_cross_audit(
        first_bounds, second_bounds, weights
    )
    assert dynamic == exhaustive


def test_outcome_count_is_product_of_cell_supports():
    assert len(count_outcomes((1, 1, 1))) == 8
    assert len(count_outcomes((2, 1, 1))) == 12
