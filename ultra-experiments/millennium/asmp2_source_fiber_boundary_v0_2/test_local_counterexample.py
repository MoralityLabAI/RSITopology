from fractions import Fraction

from local_counterexample import (
    ACTIONS,
    RADIUS,
    build_local_counterexample,
    observation_probability,
    risk,
)


def test_observation_family_is_regular_and_full_support() -> None:
    assert observation_probability(-RADIUS) == Fraction(3, 8)
    assert observation_probability(0) == Fraction(1, 2)
    assert observation_probability(RADIUS) == Fraction(5, 8)


def test_every_action_has_identified_nonzero_risk_derivative() -> None:
    for action in ACTIONS:
        derivative = (
            risk(action, Fraction(1, 1000)) - risk(action, Fraction(0))
        ) * 1000
        assert derivative == Fraction(action, 4)


def test_no_registered_action_is_uniformly_safe() -> None:
    for action in ACTIONS:
        worst = max(risk(action, -RADIUS), risk(action, RADIUS))
        assert worst == Fraction(5, 8)
        assert worst > Fraction(1, 2)


def test_all_counterexample_gates_pass() -> None:
    result = build_local_counterexample()
    assert result["all_gates_passed"]
    assert all(result["gates"].values())
