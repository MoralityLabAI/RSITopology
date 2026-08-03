from fractions import Fraction

from adaptive_reuse import (
    adaptive_census,
    local_monotonicity_failures,
    policy_registry,
    robust_lower_bound,
    robustness_probes,
    true_gain,
)


def test_policy_registry_is_probability_valid():
    policies = policy_registry(6)
    assert len(policies) == 30
    assert all(min(policy["distribution"]) >= 0 and sum(policy["distribution"]) == 1 for policy in policies)


def test_pointwise_bound_on_representative_errors_and_masks():
    policies = policy_registry(6)
    errors = tuple(Fraction(value) for value in (-1, 0, 1, 1, -1, 0))
    for mask in (0, 1, 0b010101, 0b111111):
        for policy in policies:
            assert robust_lower_bound(policy, errors, mask, Fraction(1)) <= true_gain(policy, errors)


def test_full_census_is_exact():
    errors = tuple(Fraction(value) for value in (1, -1, 0, 1, 0, -1))
    for policy in policy_registry(6):
        assert robust_lower_bound(policy, errors, 0b111111, Fraction(1)) == true_gain(policy, errors)


def test_reveal_increment_is_monotone():
    assert local_monotonicity_failures(6, Fraction(1)) == 0


def test_adaptive_negative_control_is_live_and_robust_bound_is_sound():
    result = adaptive_census(4, Fraction(1))
    assert result["adaptive_robust_false_declarations"] == 0
    assert result["adaptive_naive_false_declarations"] > 0


def test_metric_robustness_probes_on_small_complete_summary():
    adaptive = adaptive_census(4, Fraction(1))
    summary = {
        "adaptive": adaptive,
        "pointwise": {"full_census_failures": 0},
        "local_monotonicity_failures": 0,
    }
    # The relabeling fixture is six-dimensional, so retain the registered
    # dimension while injecting the exact small adaptive census.
    probes = robustness_probes(summary, 6, Fraction(1))
    assert set(probes) == {"invariance", "sensitivity", "monotonicity", "anti_gaming", "clean_control"}
    assert all(record["pass"] for record in probes.values())
