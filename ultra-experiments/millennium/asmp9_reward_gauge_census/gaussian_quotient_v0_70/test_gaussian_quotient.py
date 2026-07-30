from __future__ import annotations

from fractions import Fraction
from math import isclose

import sympy as sp

from gaussian_quotient import (
    biased_parameter_mse,
    canonical_fixture,
    estimator_bias,
    exact_allocation_optimum,
    functional_variance,
    information_matrix,
    parameter_minimax_risk,
    quadratic_minimax_risk,
    rational_matrix,
    two_policy_plugin_error,
    weak_compositions,
    worst_vertex_bias_mse,
)


def test_information_and_minimax_risk_are_exact() -> None:
    rows, variances = canonical_fixture()
    information = information_matrix(rows, variances, (5, 5, 2))
    assert information == rational_matrix([[7, 2], [2, 7]])
    assert parameter_minimax_risk(information) == sp.Rational(14, 45)
    assert quadratic_minimax_risk(information, sp.eye(2)) == sp.Rational(
        14, 45
    )


def test_singular_information_is_an_access_failure() -> None:
    rows, variances = canonical_fixture()
    information = information_matrix(rows, variances, (12, 0, 0))
    assert information.rank() == 1
    assert parameter_minimax_risk(information) is sp.oo
    assert functional_variance(
        information, rational_matrix([[1], [0]])
    ) is sp.oo


def test_parameter_and_policy_allocations_differ() -> None:
    rows, variances = canonical_fixture()
    parameter = exact_allocation_optimum(rows, variances, 12)
    policy = exact_allocation_optimum(
        rows,
        variances,
        12,
        functional=rational_matrix([[1], [0]]),
    )
    assert parameter.objective == sp.Rational(14, 45)
    assert set(parameter.allocations) == {(5, 5, 2)}
    assert policy.objective == sp.Rational(1, 11)
    assert set(policy.allocations) == {(11, 0, 1), (11, 1, 0)}
    assert parameter.objective != policy.objective
    assert parameter.evaluated_allocations == 91
    assert parameter.identified_allocations < 91


def test_functional_variance_matches_direct_inverse() -> None:
    rows, variances = canonical_fixture()
    information = information_matrix(rows, variances, (11, 1, 0))
    c = rational_matrix([[1], [0]])
    assert functional_variance(information, c) == sp.Rational(1, 11)


def test_fixed_mean_bias_has_exact_mse_decomposition() -> None:
    rows, variances = canonical_fixture()
    allocation = (5, 5, 2)
    mean_bias = (Fraction(1, 10), Fraction(0), Fraction(-1, 20))
    information = information_matrix(rows, variances, allocation)
    bias = estimator_bias(rows, variances, allocation, mean_bias)
    assert bias is not None
    expected = parameter_minimax_risk(information) + (bias.T * bias)[0]
    assert biased_parameter_mse(
        rows, variances, allocation, mean_bias
    ) == expected
    assert expected > parameter_minimax_risk(information)


def test_rectangular_bias_vertex_audit_is_complete() -> None:
    rows, variances = canonical_fixture()
    result = worst_vertex_bias_mse(
        rows,
        variances,
        (5, 5, 2),
        (Fraction(1, 20), Fraction(1, 20), Fraction(1, 20)),
    )
    assert result["vertex_count"] == 8
    assert result["witnesses"]


def test_two_policy_formula_has_expected_monotonicity() -> None:
    weak = two_policy_plugin_error(0.5, 0.25)
    strong = two_policy_plugin_error(1.0, 0.25)
    assert isclose(weak["z_score"], 1.0)
    assert isclose(strong["z_score"], 2.0)
    assert strong["error_probability"] < weak["error_probability"]


def test_weak_compositions_cover_exact_allocation_universe() -> None:
    values = list(weak_compositions(12, 3))
    assert len(values) == 91
    assert len(set(values)) == 91
    assert all(sum(value) == 12 for value in values)
