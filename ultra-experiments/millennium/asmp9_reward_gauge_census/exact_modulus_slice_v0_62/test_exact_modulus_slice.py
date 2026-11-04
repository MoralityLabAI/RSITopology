from fractions import Fraction

from exact_modulus_slice import (
    ALTERNATIVES,
    MENUS,
    common_huber_observation,
    common_recording_observation,
    delta_modulus,
    huber_threshold,
    kernel_from_ranking_weights,
    kernel_tv,
    lambda_modulus,
    luce_cycle_defect,
    nonrum_point,
    primal_parameters,
    regularity_gap,
    rum_point,
    rum_ranking_weights,
    symmetric_ratio,
)


GAMMAS = (
    Fraction(1, 4096),
    Fraction(3, 1600),
    Fraction(1, 200),
    Fraction(1, 128),
)


def test_rum_segment_has_explicit_ranking_mixture_and_non_luce_defect():
    for gamma in GAMMAS:
        for t in (Fraction(0), gamma / 4, gamma / 2):
            point = rum_point(gamma, t)
            assert kernel_from_ranking_weights(rum_ranking_weights(t)) == point
            assert luce_cycle_defect(point) == Fraction(6, 125)


def test_nonrum_segment_has_registered_margin():
    for gamma in GAMMAS:
        for s in (gamma, 3 * gamma / 2, 2 * gamma):
            point = nonrum_point(gamma, s)
            assert regularity_gap(point) == s
            assert s >= gamma


def test_tv_modulus_has_matching_primal_and_event_dual():
    for gamma in GAMMAS:
        for t in (Fraction(0), gamma / 4, gamma / 2):
            for s in (gamma, 3 * gamma / 2, 2 * gamma):
                left = rum_point(gamma, t)
                right = nonrum_point(gamma, s)
                assert kernel_tv(left, right) == s
                assert (
                    right[(ALTERNATIVES, "a")]
                    - left[(ALTERNATIVES, "a")]
                    == s
                )
        assert delta_modulus(gamma) == gamma


def test_ratio_modulus_has_matching_primal_and_coordinate_dual():
    for gamma in GAMMAS:
        t_star, s_star = primal_parameters(gamma)
        left = rum_point(gamma, t_star)
        right = nonrum_point(gamma, s_star)
        expected = 1 + Fraction(5, 2) * gamma
        assert symmetric_ratio(left, right) == expected
        assert lambda_modulus(gamma) == expected
        for t in (Fraction(0), gamma / 4, gamma / 2):
            for s in (gamma, 3 * gamma / 2, 2 * gamma):
                assert symmetric_ratio(
                    rum_point(gamma, t),
                    nonrum_point(gamma, s),
                ) >= expected


def test_huber_boundary_constructs_one_common_kernel():
    for gamma in GAMMAS:
        t_star, s_star = primal_parameters(gamma)
        left = rum_point(gamma, t_star)
        right = nonrum_point(gamma, s_star)
        epsilon = huber_threshold(gamma)
        observed = common_huber_observation(left, right, epsilon)
        for menu in MENUS:
            assert sum(observed[(menu, item)] for item in menu) == 1
            for clean in (left, right):
                contaminant = tuple(
                    (
                        observed[(menu, item)]
                        - (1 - epsilon) * clean[(menu, item)]
                    )
                    / epsilon
                    for item in menu
                )
                assert min(contaminant) >= 0
                assert sum(contaminant, Fraction(0)) == 1


def test_recording_boundary_constructs_one_complete_record_law():
    for gamma in GAMMAS:
        t_star, s_star = primal_parameters(gamma)
        left = rum_point(gamma, t_star)
        right = nonrum_point(gamma, s_star)
        ratio = lambda_modulus(gamma)
        lower = 1 / ratio
        joint, left_recording, right_recording = common_recording_observation(
            left,
            right,
            lower,
            Fraction(1),
        )
        for key in joint:
            assert left[key] * left_recording[key] == joint[key]
            assert right[key] * right_recording[key] == joint[key]

