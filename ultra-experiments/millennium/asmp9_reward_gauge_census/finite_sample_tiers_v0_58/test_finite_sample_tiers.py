import importlib.util
import math
import sys
from fractions import Fraction
from pathlib import Path

from finite_sample_tiers import (
    INCONCLUSIVE,
    LUCE,
    NON_RUM,
    RUM_NON_LUCE,
    classify_from_distances,
    close_luce_rum_kernel,
    close_rum_nonrum_kernel,
    coordinate_tolerance,
    eta_for_error_target,
    lecam_error_lower_bound,
    likelihood_oscillation_l1_bound,
    luce_rum_single_draw_kl,
    margin_promised_query_lower_bound,
    maximum_interpolation_norm,
    observed_coordinate_count,
    reconstruction_l1_bound,
    rum_boundary_kernel,
    rum_boundary_luce_distance_lower_bound,
    rum_nonrum_margin_single_draw_kl,
    sample_count_per_menu,
    uniform_luce_kernel,
)


def _load_v054_classifier():
    path = (
        Path(__file__).resolve().parent.parent
        / "stochastic_choice_trichotomy_v0_54"
        / "stochastic_choice.py"
    )
    spec = importlib.util.spec_from_file_location("asmp9_v054_classifier", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_close_luce_rum_path_with_independent_v054_classifier():
    classifier = _load_v054_classifier()
    p0 = uniform_luce_kernel()
    assert classifier.classify(p0).status == classifier.SCALAR_LUCE
    for eta in (Fraction(1, 1000), Fraction(1, 100), Fraction(1, 12)):
        kernel = close_luce_rum_kernel(eta)
        assert (
            classifier.classify(kernel).status
            == classifier.RANDOM_UTILITY_NON_LUCE
        )
        for menu in (("a", "b"), ("a", "c"), ("b", "c")):
            for item in menu:
                assert kernel[(menu, item)] == Fraction(1, 2)
        assert kernel[(("a", "b", "c"), "a")] == Fraction(1, 3) - eta
        assert kernel[(("a", "b", "c"), "b")] == Fraction(1, 3)
        assert kernel[(("a", "b", "c"), "c")] == Fraction(1, 3) + eta


def test_close_rum_nonrum_path_with_independent_v054_classifier():
    classifier = _load_v054_classifier()
    boundary = rum_boundary_kernel()
    assert (
        classifier.classify(boundary).status
        == classifier.RANDOM_UTILITY_NON_LUCE
    )
    assert boundary[(("a", "b"), "a")] == Fraction(2, 5)
    assert boundary[(("a", "b", "c"), "a")] == Fraction(2, 5)
    for epsilon in (Fraction(1, 1000), Fraction(1, 100), Fraction(1, 10)):
        kernel = close_rum_nonrum_kernel(epsilon)
        result = classifier.classify(kernel)
        assert result.status == classifier.NO_RANDOM_UTILITY
        assert kernel[(("a", "b", "c"), "a")] > kernel[(("a", "b"), "a")]


def test_rum_nonrum_pair_lies_in_margin_promise_and_forces_gamma_squared_rate():
    boundary = rum_boundary_kernel()
    binary_cycle_left = (
        boundary[(("a", "b"), "a")]
        * boundary[(("b", "c"), "b")]
        * boundary[(("a", "c"), "c")]
    )
    binary_cycle_right = (
        boundary[(("a", "b"), "b")]
        * boundary[(("b", "c"), "c")]
        * boundary[(("a", "c"), "a")]
    )
    assert abs(binary_cycle_left - binary_cycle_right) == Fraction(6, 125)
    assert rum_boundary_luce_distance_lower_bound() == Fraction(1, 125)

    for gamma in (1e-4, 1e-3, 1 / 125):
        epsilon = 2 * gamma
        p = (2 / 5, 2 / 5, 1 / 5)
        q = (2 / 5 + epsilon, 2 / 5 - epsilon, 1 / 5)
        direct = sum(left * math.log(left / right) for left, right in zip(p, q))
        assert math.isclose(
            direct,
            rum_nonrum_margin_single_draw_kl(gamma),
            rel_tol=1e-12,
            abs_tol=1e-15,
        )
        # The regularity violation is 2*gamma and the defining functional is
        # 2-Lipschitz in maximum menuwise L1, hence d(q,P) >= gamma.
        perturbed = close_rum_nonrum_kernel(Fraction(str(epsilon)))
        assert (
            float(
                perturbed[(("a", "b", "c"), "a")]
                - perturbed[(("a", "b"), "a")]
            )
            >= 2 * gamma - 1e-15
        )
        required = margin_promised_query_lower_bound(gamma, 0.05)
        if required > 1:
            divergence = (required - 1) * rum_nonrum_margin_single_draw_kl(
                gamma
            )
            lower_error = (1 - math.sqrt(divergence / 2)) / 2
            assert lower_error > 0.05


def test_kl_formula_and_lecam_obstruction_for_arbitrary_finite_budgets():
    for eta in (1e-5, 1e-3, 0.05, 0.1):
        p = (1 / 3, 1 / 3, 1 / 3)
        q = (1 / 3 - eta, 1 / 3, 1 / 3 + eta)
        direct = sum(left * math.log(left / right) for left, right in zip(p, q))
        assert math.isclose(
            direct,
            luce_rum_single_draw_kl(eta),
            rel_tol=1e-6,
            abs_tol=1e-15,
        )
    for budget in (1, 10, 1_000, 1_000_000):
        for target in (0.05, 0.2, 0.49):
            eta = eta_for_error_target(budget, target)
            assert 0 < eta < 1 / 6
            assert lecam_error_lower_bound(budget, eta) > target


def test_margin_classifier_is_total_and_correct_with_one_third_error():
    for gamma in (0.02, 0.2, 1.0):
        error = gamma / 3
        assert classify_from_distances(error, error, gamma) == LUCE
        assert (
            classify_from_distances(gamma - error, error, gamma)
            == RUM_NON_LUCE
        )
        assert (
            classify_from_distances(gamma, gamma - error, gamma) == NON_RUM
        )
        assert (
            classify_from_distances(gamma, gamma / 2, gamma) == INCONCLUSIVE
        )
        assert (
            classify_from_distances(gamma / 2, error, gamma) == INCONCLUSIVE
        )


def test_sample_bound_closes_the_registered_hoeffding_union_bound():
    cells = (
        (3, 1, 0.20, 0.20, 0.05),
        (5, 1, 0.05, 0.10, 0.01),
        (6, 2, 0.02, 0.05, 0.05),
        (8, 4, 0.01, 0.02, 0.01),
    )
    for n, degree, floor, gamma, delta in cells:
        condition = maximum_interpolation_norm(n, degree)
        tolerance = coordinate_tolerance(floor, gamma, condition)
        count = sample_count_per_menu(n, degree, floor, gamma, delta)
        coordinates = observed_coordinate_count(n, degree)
        assert 2 * coordinates * math.exp(-2 * count * tolerance**2) <= delta
        assert reconstruction_l1_bound(tolerance, floor, condition) <= (
            gamma / 3 + 1e-12
        )


def test_likelihood_oscillation_bound_is_attained_on_two_points():
    for error in (0.0, 0.01, 0.2, 1.0, 3.0):
        if error == 0:
            assert likelihood_oscillation_l1_bound(error) == 0
            continue
        p_high = 1 / (math.exp(error) + 1)
        p = (1 - p_high, p_high)
        tilts = (math.exp(-error), math.exp(error))
        normalizer = sum(probability * tilt for probability, tilt in zip(p, tilts))
        q = tuple(
            probability * tilt / normalizer
            for probability, tilt in zip(p, tilts)
        )
        l1 = sum(abs(left - right) for left, right in zip(p, q))
        assert math.isclose(
            l1,
            likelihood_oscillation_l1_bound(error),
            rel_tol=1e-12,
            abs_tol=1e-15,
        )


def test_interpolation_condition_exposes_interior_order_instability():
    assert maximum_interpolation_norm(8, 0) == 1
    assert maximum_interpolation_norm(8, 1) == 11
    assert maximum_interpolation_norm(8, 2) == 49
    assert maximum_interpolation_norm(8, 3) == 111
    assert maximum_interpolation_norm(8, 4) == 129
    assert maximum_interpolation_norm(8, 5) == 63
    assert maximum_interpolation_norm(8, 6) == 1
