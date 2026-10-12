import importlib.util
import math
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

import pytest

from selection_channel import (
    bounded_recording_neighborhoods_overlap,
    categorical_kl,
    common_bounded_recorded_joint,
    common_outcome_selected_observation,
    incomplete_domain_compatible_tiers,
    l1_margin_recording_ratio_ceiling,
    observed_support,
    outcome_selected_observation,
    preselection_joint,
    preselection_joint_kl,
    recover_from_known_recording,
    recover_preselection_joint,
    recording_ratio_required_for_overlap,
    selection_scaled_lecam_lower_bound,
    total_draws_for_per_menu_count,
)


def _positive_simplex(denominator: int, dimension: int):
    for numerators in product(range(1, denominator), repeat=dimension):
        if sum(numerators) == denominator:
            yield tuple(Fraction(value, denominator) for value in numerators)


def _load_v054_classifier():
    path = (
        Path(__file__).resolve().parent.parent
        / "stochastic_choice_trichotomy_v0_54"
        / "stochastic_choice.py"
    )
    spec = importlib.util.spec_from_file_location("asmp9_v054_for_v060", path)
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
    spec = importlib.util.spec_from_file_location("asmp9_v058_for_v060", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_recorded_preselection_recovers_every_positive_support_conditional():
    kernel = (
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(1, 3), Fraction(2, 3)),
        (Fraction(1, 5), Fraction(2, 5), Fraction(2, 5)),
    )
    selection = (Fraction(2, 7), Fraction(0), Fraction(5, 7))
    joint = preselection_joint(kernel, selection)
    recovered_selection, recovered_kernel = recover_preselection_joint(joint)
    assert recovered_selection == selection
    assert observed_support(selection) == (0, 2)
    assert recovered_kernel == (kernel[0], None, kernel[2])


def test_preselection_support_reduces_exactly_to_v056_tier_ledger():
    assert incomplete_domain_compatible_tiers(
        complete_support=True,
        full_tier="R",
    ) == ("R",)
    assert incomplete_domain_compatible_tiers(
        complete_support=False,
        has_rum_completion=False,
        has_luce_completion=False,
    ) == ("N",)
    assert incomplete_domain_compatible_tiers(
        complete_support=False,
        has_rum_completion=True,
        has_luce_completion=False,
    ) == ("R", "N")
    assert incomplete_domain_compatible_tiers(
        complete_support=False,
        has_rum_completion=True,
        has_luce_completion=True,
    ) == ("L", "R", "N")


def test_preselection_joint_kl_is_menu_probability_weighted():
    selection = (Fraction(9, 10), Fraction(1, 10))
    left = (
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(2, 5), Fraction(2, 5), Fraction(1, 5)),
    )
    right = (
        left[0],
        (Fraction(21, 50), Fraction(19, 50), Fraction(1, 5)),
    )
    factorized = preselection_joint_kl(selection, left, right)
    flat_left = tuple(value for menu in preselection_joint(left, selection) for value in menu)
    flat_right = tuple(value for menu in preselection_joint(right, selection) for value in menu)
    assert factorized == pytest.approx(categorical_kl(flat_left, flat_right))
    assert factorized == pytest.approx(
        float(selection[1]) * categorical_kl(left[1], right[1])
    )


def test_arbitrary_positive_outcome_selection_confounds_every_clean_pair():
    distributions = tuple(_positive_simplex(7, 3))
    for left in distributions:
        for right in distributions:
            (
                record_rate,
                selected,
                recording_left,
                recording_right,
                joint,
            ) = common_outcome_selected_observation(left, right)
            assert record_rate > 0
            assert selected == (Fraction(1, 3),) * 3
            assert all(0 < value <= 1 for value in recording_left)
            assert all(0 < value <= 1 for value in recording_right)
            assert tuple(
                clean * recording
                for clean, recording in zip(left, recording_left)
            ) == joint
            assert tuple(
                clean * recording
                for clean, recording in zip(right, recording_right)
            ) == joint


def test_known_positive_recording_weights_restore_the_clean_law():
    clean = (Fraction(1, 5), Fraction(1, 2), Fraction(3, 10))
    target = (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3))
    selected, recording, joint = outcome_selected_observation(
        clean,
        target,
        Fraction(3, 10),
    )
    assert selected == target
    assert recover_from_known_recording(joint, recording) == clean


def test_bounded_outcome_selection_has_an_exact_multiplicative_radius():
    distributions = tuple(_positive_simplex(7, 3))
    bounds = (
        (Fraction(1, 1), Fraction(1, 1)),
        (Fraction(3, 4), Fraction(1, 1)),
        (Fraction(1, 2), Fraction(1, 1)),
        (Fraction(1, 4), Fraction(3, 4)),
    )
    for left in distributions:
        for right in distributions:
            required = recording_ratio_required_for_overlap(left, right)
            for lower, upper in bounds:
                expected = required <= upper / lower
                assert bounded_recording_neighborhoods_overlap(
                    left,
                    right,
                    lower,
                    upper,
                ) is expected
                if expected:
                    (
                        left_recording,
                        right_recording,
                        joint,
                        rate,
                    ) = common_bounded_recorded_joint(
                        left,
                        right,
                        lower,
                        upper,
                    )
                    assert all(
                        lower <= probability <= upper
                        for probability in left_recording + right_recording
                    )
                    assert tuple(
                        clean * probability
                        for clean, probability in zip(left, left_recording)
                    ) == joint
                    assert tuple(
                        clean * probability
                        for clean, probability in zip(right, right_recording)
                    ) == joint
                    assert sum(joint) == rate


def test_margin_gives_a_live_bounded_recording_positive_region():
    for gamma in (0.01, 0.05, 0.2, 0.5):
        ratio = l1_margin_recording_ratio_ceiling(gamma)
        assert ratio == pytest.approx((2 + gamma) / (2 - gamma))
        assert 2 * math.tanh(math.log(ratio) / 2) == pytest.approx(gamma)


def test_cross_tier_pair_has_an_exact_recording_ratio_witness():
    for gamma in (Fraction(1, 1000), Fraction(1, 250), Fraction(1, 125)):
        left = (Fraction(2, 5), Fraction(2, 5), Fraction(1, 5))
        right = (
            Fraction(2, 5) + 2 * gamma,
            Fraction(2, 5) - 2 * gamma,
            Fraction(1, 5),
        )
        required = recording_ratio_required_for_overlap(left, right)
        assert required == 1 / (1 - 5 * gamma)
        lower = 1 - 5 * gamma
        assert bounded_recording_neighborhoods_overlap(
            left,
            right,
            lower,
            Fraction(1),
        )
        assert not bounded_recording_neighborhoods_overlap(
            left,
            right,
            lower + Fraction(1, 10_000),
            Fraction(1),
        )


def test_selection_floor_yields_matching_inverse_probability_scaling():
    v058 = _load_v058_module()
    per_menu_count = v058.sample_count_per_menu(
        3,
        1,
        0.2,
        0.2,
        0.025,
    )
    assert per_menu_count == 76_463
    expected_totals = {
        0.25: 611_704,
        0.10: 1_529_260,
        0.05: 3_058_520,
        0.01: 15_292_600,
        0.001: 152_926_000,
    }
    previous_upper = None
    previous_lower = None
    informative_kl = 0.001
    for floor_value, expected_upper in expected_totals.items():
        upper = total_draws_for_per_menu_count(
            per_menu_count,
            4,
            floor_value,
            0.025,
        )
        assert upper == expected_upper
        lower = selection_scaled_lecam_lower_bound(
            floor_value,
            informative_kl,
            0.1,
        )
        if previous_upper is not None:
            assert upper / previous_upper == pytest.approx(
                previous_floor / floor_value
            )
            assert lower / previous_lower == pytest.approx(
                previous_floor / floor_value
            )
        previous_upper = upper
        previous_lower = lower
        previous_floor = floor_value


def test_no_uniform_rate_without_a_selection_floor_on_cross_tier_pair():
    classifier = _load_v054_classifier()
    v058 = _load_v058_module()
    gamma = Fraction(1, 250)
    rum = v058.rum_boundary_kernel()
    nonrum = v058.close_rum_nonrum_kernel(2 * gamma)
    assert classifier.classify(rum).status == classifier.RANDOM_UTILITY_NON_LUCE
    assert classifier.classify(nonrum).status == classifier.NO_RANDOM_UTILITY
    informative_kl = v058.rum_nonrum_margin_single_draw_kl(float(gamma))
    target_error = 0.1
    fixed_budget = 10_000
    for eta in (1e-2, 1e-4, 1e-6):
        necessary = selection_scaled_lecam_lower_bound(
            eta,
            informative_kl,
            target_error,
        )
        assert necessary > fixed_budget
    assert math.isclose(
        selection_scaled_lecam_lower_bound(
            0.01,
            informative_kl,
            target_error,
        )
        / selection_scaled_lecam_lower_bound(
            0.005,
            informative_kl,
            target_error,
        ),
        0.5,
    )
