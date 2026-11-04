from fractions import Fraction

import pytest

from .decision_relevance import (
    decision_gauge_valid,
    evaluate_plugin_policy,
    quotient_residual,
    scaled_cardinal_target,
)


def test_constant_gauge_is_decision_null_at_fixed_horizon():
    occupancies = ((3, 0, 0), (0, 3, 0), (1, 1, 1))
    assert decision_gauge_valid(occupancies, ((1, 1, 1),))


def test_varying_horizon_invalidates_constant_gauge():
    occupancies = ((3, 0, 0), (0, 2, 0), (1, 1, 1))
    assert not decision_gauge_valid(occupancies, ((1, 1, 1),))


def test_quotient_projection_removes_exact_gauge_component():
    true = (Fraction(1, 3), Fraction(-2, 5), Fraction(7, 11))
    structural_error = (Fraction(1, 7), Fraction(-1, 7), 0)
    gauge_shift = (Fraction(13, 9),) * 3
    estimated = tuple(
        t + e + g for t, e, g in zip(true, structural_error, gauge_shift)
    )
    assert quotient_residual(estimated, true, ((1, 1, 1),)) == structural_error


def test_plugin_regret_bound_is_exactly_sharp():
    a = Fraction(3, 7)
    result = evaluate_plugin_policy(
        ((1, 0), (0, 1)),
        (-a, a),
        (0, 0),
        ((1, 1),),
    )
    assert result["true_policy"] == 1
    assert result["estimated_policy"] == 0
    assert result["regret"] == 2 * a
    assert result["regret"] ** 2 == result["selected_bound_squared"]
    assert result["global_bound_valid"]


def test_strict_margin_can_certify_policy_identity():
    result = evaluate_plugin_policy(
        ((2, 0, 0), (0, 2, 0), (0, 0, 2)),
        (4, 1, 0),
        (Fraction(15, 4), Fraction(5, 4), 0),
        ((1, 1, 1),),
    )
    assert result["true_policy"] == result["estimated_policy"] == 0
    assert result["policy_identity_certified"]


def test_invalid_gauge_forces_unavailable_certificate():
    result = evaluate_plugin_policy(
        ((2, 0), (0, 1)),
        (1, 0),
        (1, 0),
        ((1, 1),),
    )
    assert result == {
        "status": "decision_gauge_invalid",
        "certificate_available": False,
    }


def test_positive_scale_preserves_policy_but_not_cardinal_threshold():
    rows = scaled_cardinal_target(
        ((1, 0), (0, 1)),
        (-2, 2),
        evaluated_policy=0,
        scale_factors=(Fraction(1, 4), 3),
        fixed_regret_threshold=5,
    )
    assert {row["optimal_policy"] for row in rows} == {1}
    assert [row["regret"] for row in rows] == [1, 12]
    assert [row["fixed_threshold_pass"] for row in rows] == [True, False]


def test_dependent_gauge_basis_is_rejected():
    with pytest.raises(ValueError, match="singular"):
        quotient_residual((1, 0), (0, 0), ((1, 1), (2, 2)))
