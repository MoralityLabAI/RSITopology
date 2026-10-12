from __future__ import annotations

import sympy as sp

from stochastic_target import (
    affinity,
    analyze_stochastic_interface,
    exact_binary_bayes_error,
    hellinger_mle_union_bound,
    iid_tv_misspecification_penalty,
    law,
    minimum_exact_binary_bayes_samples,
    minimum_hellinger_bound_samples,
    robustified_error_bound,
)


P = law(("9/10", "1/10"))
Q = law(("1/10", "9/10"))


def test_population_target_is_identified_with_exact_h2_gap() -> None:
    result = analyze_stochastic_interface(("left", "right"), (P, Q))
    assert result.status == "exact_stochastic_target_interface"
    assert result.population_target_recoverable
    assert result.representative_insensitive
    assert affinity(P, Q) == sp.Rational(3, 5)
    assert result.minimum_cross_target_hellinger_squared == sp.Rational(2, 5)


def test_identical_cross_target_laws_are_underidentified() -> None:
    result = analyze_stochastic_interface(("left", "right"), (P, P))
    assert result.status == "population_underidentified"
    assert not result.population_target_recoverable
    assert result.minimum_cross_target_hellinger_squared == 0


def test_same_target_distinct_laws_create_distributional_leakage() -> None:
    result = analyze_stochastic_interface(("same", "same"), (P, Q))
    assert result.status == "recoverable_with_distributional_leakage"
    assert result.population_target_recoverable
    assert not result.representative_insensitive
    assert result.maximum_within_target_hellinger_squared == sp.Rational(2, 5)


def test_hellinger_union_bound_has_frozen_six_sample_threshold() -> None:
    assert hellinger_mle_union_bound(("left", "right"), (P, Q), 6) == sp.Rational(
        729, 15625
    )
    assert minimum_hellinger_bound_samples(
        ("left", "right"),
        (P, Q),
        sp.Rational(1, 20),
    ) == 6


def test_exact_binary_bayes_threshold_is_three_samples() -> None:
    assert exact_binary_bayes_error(P, Q, 3) == sp.Rational(7, 250)
    assert minimum_exact_binary_bayes_samples(P, Q, sp.Rational(1, 20)) == 3


def test_tv_misspecification_can_break_registered_bound() -> None:
    registered = hellinger_mle_union_bound(("left", "right"), (P, Q), 6)
    penalty = iid_tv_misspecification_penalty(sp.Rational(1, 1000), 6)
    robust = robustified_error_bound(registered, sp.Rational(1, 1000), 6)
    assert registered < sp.Rational(1, 20)
    assert penalty == 1 - sp.Rational(999, 1000) ** 6
    assert robust > sp.Rational(1, 20)


def test_invalid_probability_law_is_rejected() -> None:
    try:
        law(("1/2", "1/3"))
    except ValueError as error:
        assert "sum to one" in str(error)
    else:
        raise AssertionError("invalid law was accepted")
