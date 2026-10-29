import importlib.util
import math
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

import pytest

from contamination_radius import (
    clean_coordinate_tolerance,
    common_huber_observation,
    contamination_ceiling_from_observed_gap,
    huber_neighborhoods_overlap,
    kernel_huber_neighborhoods_overlap,
    kernel_tv_distance,
    maximum_interpolation_norm,
    minimum_huber_contamination_for_overlap,
    minimum_huber_contamination_for_kernel_overlap,
    observed_coordinate_count,
    observed_tv_modulus_lower_bound,
    population_identifiability_status,
    reconstruction_l1_bound_under_contamination,
    robust_sample_count_per_menu,
    rum_nonrum_full_menu_pair,
    rum_nonrum_witness_contamination_threshold,
    total_variation,
)


def _simplex(denominator: int, dimension: int):
    for numerators in product(range(denominator + 1), repeat=dimension):
        if sum(numerators) == denominator:
            yield tuple(Fraction(value, denominator) for value in numerators)


def _load_v054_classifier():
    path = (
        Path(__file__).resolve().parent.parent
        / "stochastic_choice_trichotomy_v0_54"
        / "stochastic_choice.py"
    )
    spec = importlib.util.spec_from_file_location("asmp9_v054_for_v059", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_v058_module():
    path = (
        Path(__file__).resolve().parent.parent
        / "finite_sample_tiers_v0_58"
        / "finite_sample_tiers.py"
    )
    spec = importlib.util.spec_from_file_location("asmp9_v058_for_v059", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_exact_huber_overlap_theorem_on_rational_simplex_grid():
    distributions = tuple(_simplex(6, 3))
    for left in distributions:
        for right in distributions:
            threshold = minimum_huber_contamination_for_overlap(left, right)
            assert threshold == total_variation(left, right) / (
                1 + total_variation(left, right)
            )
            for epsilon in (
                Fraction(0),
                threshold / 2,
                threshold,
                (threshold + 1) / 2,
            ):
                expected = epsilon >= threshold
                assert huber_neighborhoods_overlap(left, right, epsilon) is expected
                if expected:
                    observed, left_bad, right_bad = common_huber_observation(
                        left,
                        right,
                        epsilon,
                    )
                    assert tuple(
                        (1 - epsilon) * clean + epsilon * bad
                        for clean, bad in zip(left, left_bad)
                    ) == observed
                    assert tuple(
                        (1 - epsilon) * clean + epsilon * bad
                        for clean, bad in zip(right, right_bad)
                    ) == observed


def test_menu_family_overlap_is_controlled_by_the_worst_menu():
    left = (
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(3, 5), Fraction(1, 5), Fraction(1, 5)),
    )
    right = (
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(2, 5), Fraction(2, 5), Fraction(1, 5)),
    )
    assert kernel_tv_distance(left, right) == Fraction(1, 5)
    threshold = Fraction(1, 6)
    assert minimum_huber_contamination_for_kernel_overlap(left, right) == threshold
    assert not kernel_huber_neighborhoods_overlap(
        left,
        right,
        threshold - Fraction(1, 100),
    )
    assert kernel_huber_neighborhoods_overlap(left, right, threshold)


def test_cross_tier_witness_is_exactly_ambiguous_at_registered_threshold():
    classifier = _load_v054_classifier()
    v058 = _load_v058_module()
    for gamma in (Fraction(1, 1000), Fraction(1, 250), Fraction(1, 125)):
        boundary, nonrum = rum_nonrum_full_menu_pair(gamma)
        epsilon = rum_nonrum_witness_contamination_threshold(gamma)
        assert total_variation(boundary, nonrum) == 2 * gamma
        assert epsilon == 2 * gamma / (1 + 2 * gamma)
        observed, left_bad, right_bad = common_huber_observation(
            boundary,
            nonrum,
            epsilon,
        )
        assert left_bad == (Fraction(1), Fraction(0), Fraction(0))
        assert right_bad == (Fraction(0), Fraction(1), Fraction(0))
        assert population_identifiability_status(2 * gamma, epsilon) == (
            "boundary_inconclusive"
        )

        rum_kernel = v058.rum_boundary_kernel()
        nonrum_kernel = v058.close_rum_nonrum_kernel(2 * gamma)
        assert classifier.classify(rum_kernel).status == (
            classifier.RANDOM_UTILITY_NON_LUCE
        )
        assert classifier.classify(nonrum_kernel).status == (
            classifier.NO_RANDOM_UTILITY
        )
        assert observed == tuple(
            (1 - epsilon) * clean + epsilon * bad
            for clean, bad in zip(boundary, left_bad)
        )


def test_inverse_modulus_gives_a_population_contamination_ceiling():
    cells = (
        (3, 1, 0.20, 0.20),
        (5, 1, 0.05, 0.10),
        (6, 2, 0.02, 0.05),
        (8, 4, 0.01, 0.02),
    )
    for n, degree, floor_value, gamma in cells:
        condition = maximum_interpolation_norm(n, degree)
        gap = observed_tv_modulus_lower_bound(
            floor_value,
            gamma,
            condition,
        )
        epsilon_boundary = contamination_ceiling_from_observed_gap(gap)
        assert epsilon_boundary / (1 - epsilon_boundary) == pytest.approx(gap)
        below = epsilon_boundary * 0.99
        assert below / (1 - below) < gap


def test_sampling_and_contamination_consume_separate_tolerance_terms():
    cells = (
        (3, 1, 0.20, 0.20, 0.05),
        (5, 1, 0.05, 0.10, 0.01),
        (6, 2, 0.02, 0.05, 0.05),
    )
    for n, degree, floor_value, gamma, delta in cells:
        condition = maximum_interpolation_norm(n, degree)
        clean = clean_coordinate_tolerance(floor_value, gamma, condition)
        epsilon = clean / 4
        count = robust_sample_count_per_menu(
            n,
            degree,
            floor_value,
            gamma,
            epsilon,
            delta,
        )
        assert count is not None
        coordinates = observed_coordinate_count(n, degree)
        sampling_error = math.sqrt(
            math.log(2 * coordinates / delta) / (2 * count)
        )
        assert epsilon + sampling_error < clean
        assert reconstruction_l1_bound_under_contamination(
            epsilon,
            sampling_error,
            floor_value,
            condition,
        ) < gamma / 3
        assert robust_sample_count_per_menu(
            n,
            degree,
            floor_value,
            gamma,
            clean,
            delta,
        ) is None


def test_zero_contamination_recovers_the_clean_bound_up_to_strict_rounding():
    v058 = _load_v058_module()
    for cell in (
        (3, 1, 0.20, 0.20, 0.05),
        (5, 1, 0.05, 0.10, 0.01),
        (6, 2, 0.02, 0.05, 0.05),
    ):
        robust = robust_sample_count_per_menu(*cell[:4], 0.0, cell[4])
        clean = v058.sample_count_per_menu(*cell)
        assert robust in (clean, clean + 1)


def test_population_status_is_total_and_equality_is_not_a_pass():
    gap = Fraction(1, 10)
    boundary = gap / (1 + gap)
    assert population_identifiability_status(gap, boundary / 2) == "identifiable"
    assert (
        population_identifiability_status(gap, boundary)
        == "boundary_inconclusive"
    )
    assert population_identifiability_status(gap, Fraction(1, 5)) == "ambiguous"
