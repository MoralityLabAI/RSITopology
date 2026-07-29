from fractions import Fraction

from .linear_access import (
    known_numeraire_law,
    population_law,
    quotient_identifiable,
    quotient_stability,
    scaled_population_law,
    scaled_reward_known_numeraire_law,
    scaled_unknown_numeraire_law,
    unknown_numeraire_law,
)


def test_transition_only_queries_preserve_positive_scale_exactly():
    matrix = (
        (1, -1, 0, 0),
        (0, 1, -1, 0),
        (1, 0, 0, -1),
        (2, -3, 1, 0),
    )
    reward = (Fraction(1, 3), Fraction(-5, 4), 2, Fraction(7, 9))
    for alpha in (Fraction(2, 3), Fraction(5, 2), Fraction(17, 7)):
        assert population_law(matrix, reward) == scaled_population_law(
            matrix, reward, alpha
        )


def test_unknown_value_side_feature_is_not_a_numeraire():
    matrix = ((1, -1, 0), (0, 1, -1), (1, 0, -1))
    reward = (Fraction(2, 5), Fraction(-7, 8), Fraction(11, 6))
    offsets = (Fraction(-3, 2), Fraction(4, 3), Fraction(9, 5))
    coefficient = Fraction(13, 7)
    for alpha in (Fraction(3, 4), Fraction(9, 2)):
        assert unknown_numeraire_law(
            matrix, reward, offsets, coefficient
        ) == scaled_unknown_numeraire_law(
            matrix, reward, offsets, coefficient, alpha
        )


def test_known_numeraire_breaks_the_scale_coupling():
    matrix = ((1, -1, 0), (0, 1, -1), (1, 0, -1))
    reward = (Fraction(2, 5), Fraction(-7, 8), Fraction(11, 6))
    offsets = (Fraction(-3, 2), Fraction(4, 3), Fraction(9, 5))
    baseline = known_numeraire_law(matrix, reward, offsets)
    for alpha in (Fraction(3, 4), Fraction(9, 2)):
        assert baseline != scaled_reward_known_numeraire_law(
            matrix, reward, offsets, alpha
        )


def test_kernel_equals_constant_gauge_for_connected_differences():
    matrix = (
        (1, -1, 0, 0),
        (0, 1, -1, 0),
        (0, 0, 1, -1),
        (1, 0, 0, -1),
    )
    gauge = ((1, 1, 1, 1),)
    result = quotient_identifiable(matrix, gauge)
    assert result["identifiable_modulo_gauge"]
    assert result["measurement_rank"] == 3


def test_missing_direction_exceeds_declared_gauge():
    matrix = ((1, -1, 0, 0), (0, 1, -1, 0))
    gauge = ((1, 1, 1, 1),)
    result = quotient_identifiable(matrix, gauge)
    assert result["annihilates_gauge"]
    assert not result["identifiable_modulo_gauge"]


def test_ill_conditioning_is_separate_from_rank():
    quotient_basis = ((1, 0, 0), (0, 1, 0))
    healthy = quotient_stability(((1, 0, 0), (0, 1, 0)), quotient_basis)
    weak = quotient_stability(
        ((1, 0, 0), (1, Fraction(1, 1000), 0)), quotient_basis
    )
    assert healthy["design_rank"] == weak["design_rank"] == 2
    assert weak["amplification"] > 1000 * healthy["amplification"]
