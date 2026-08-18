from __future__ import annotations

import sympy as sp

from coordinate_metric import (
    canonical_fixture,
    exact_metric_optimum,
    functional_risk,
    information_from_rows,
    quadratic_risk,
    rational_matrix,
    reframe_functional,
    reframe_information,
    reframe_loss_metric,
    reframe_rows,
)


def test_information_congruence_matches_reframed_rows() -> None:
    rows, information = canonical_fixture()
    transform = rational_matrix([[2, 1], [0, 1]])
    reframed_rows = reframe_rows(rows, transform)
    from_rows = information_from_rows(reframed_rows, (5, 5, 2))
    assert from_rows == reframe_information(information, transform)


def test_quadratic_risk_is_coordinate_invariant_with_metric() -> None:
    _, information = canonical_fixture()
    metric = rational_matrix([[2, 0], [0, 3]])
    transform = rational_matrix([[2, 1], [0, 1]])
    original = quadratic_risk(information, metric)
    reframed = quadratic_risk(
        reframe_information(information, transform),
        reframe_loss_metric(metric, transform),
    )
    assert original == reframed


def test_policy_functional_risk_is_coordinate_invariant() -> None:
    _, information = canonical_fixture()
    functional = rational_matrix([[1], [-1]])
    transform = rational_matrix([[2, 1], [0, 1]])
    original = functional_risk(information, functional)
    reframed = functional_risk(
        reframe_information(information, transform),
        reframe_functional(functional, transform),
    )
    assert original == reframed


def test_silent_identity_metric_reset_changes_scientific_loss() -> None:
    _, information = canonical_fixture()
    transform = rational_matrix([[2, 1], [0, 1]])
    reframed_information = reframe_information(information, transform)
    assert quadratic_risk(information, sp.eye(2)) != quadratic_risk(
        reframed_information, sp.eye(2)
    )
    transported = reframe_loss_metric(sp.eye(2), transform)
    assert quadratic_risk(information, sp.eye(2)) == quadratic_risk(
        reframed_information, transported
    )


def test_metric_choice_changes_exact_parameter_allocation() -> None:
    rows, _ = canonical_fixture()
    isotropic = exact_metric_optimum(rows, 12, sp.eye(2))
    first_heavy = exact_metric_optimum(
        rows, 12, rational_matrix([[100, 0], [0, 1]])
    )
    second_heavy = exact_metric_optimum(
        rows, 12, rational_matrix([[1, 0], [0, 100]])
    )
    assert isotropic.allocations == ((5, 5, 2),)
    assert first_heavy.allocations == ((10, 1, 1),)
    assert second_heavy.allocations == ((1, 10, 1),)
    assert isotropic.risk == sp.Rational(14, 45)
    assert first_heavy.risk == second_heavy.risk == sp.Rational(211, 21)


def test_orthogonal_reframing_preserves_identity_metric() -> None:
    _, information = canonical_fixture()
    transform = rational_matrix([[0, -1], [1, 0]])
    assert reframe_loss_metric(sp.eye(2), transform) == sp.eye(2)
    assert quadratic_risk(information, sp.eye(2)) == quadratic_risk(
        reframe_information(information, transform), sp.eye(2)
    )
