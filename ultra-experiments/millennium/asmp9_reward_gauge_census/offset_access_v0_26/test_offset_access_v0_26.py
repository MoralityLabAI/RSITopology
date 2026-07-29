from fractions import Fraction

import pytest

from offset_access import (
    bounded_error_patterns,
    ceil_log2_fraction,
    flat_link_sup_deviation,
    hoeffding_samples_per_query,
    midpoint_sign,
    no_offset_matching_laws,
    no_offset_nonaffine_witness,
    population_bisection,
    population_query_upper_bound,
    rational_link_margin_constant,
    reconstruct_anchored_utility,
    restricted_offset_witness,
    restricted_transcript,
    robust_bisection_with_bounded_probability_error,
    volume_query_lower_bound,
)


def test_ceil_log2_fraction_exact():
    assert ceil_log2_fraction(Fraction(1)) == 0
    assert ceil_log2_fraction(Fraction(2)) == 1
    assert ceil_log2_fraction(Fraction(3)) == 2
    assert ceil_log2_fraction(Fraction(17, 8)) == 2


@pytest.mark.parametrize("radius,tolerance", [(8, Fraction(1, 16)), (5, Fraction(1, 32))])
def test_population_bisection_uniform_grid(radius, tolerance):
    radius = Fraction(radius)
    denominator = 37
    for numerator in range(-int(radius) * denominator, int(radius) * denominator + 1):
        gap = Fraction(numerator, denominator)
        receipt = population_bisection(gap, radius, tolerance)
        assert receipt.absolute_error <= tolerance
        assert receipt.query_count <= ceil_log2_fraction(radius / tolerance)


def test_star_reconstruction_and_upper_bound():
    gaps = tuple(map(Fraction, (-7, Fraction(-3, 5), 0, Fraction(19, 7), 8)))
    receipts = reconstruct_anchored_utility(gaps, Fraction(8), Fraction(1, 64))
    assert all(receipt.absolute_error <= Fraction(1, 64) for receipt in receipts)
    assert sum(receipt.query_count for receipt in receipts) <= population_query_upper_bound(
        len(gaps), Fraction(8), Fraction(1, 64)
    )


def test_metric_entropy_lower_bound_matches_power_of_two_cells():
    assert volume_query_lower_bound(5, Fraction(8), Fraction(1, 32)) == 40
    assert population_query_upper_bound(5, Fraction(8), Fraction(1, 32)) == 40


def test_restricted_offsets_have_exact_indistinguishable_witness():
    radius = Fraction(8)
    maximum_offset = Fraction(3)
    first, second = restricted_offset_witness(radius, maximum_offset)
    offsets = [Fraction(k, 8) for k in range(-24, 25)]
    assert restricted_transcript(first, offsets) == restricted_transcript(second, offsets)
    assert set(restricted_transcript(first, offsets)) == {1}
    assert abs(first - second) / 2 == Fraction(5, 4)


def test_midpoint_sign_is_link_independent_algebraically():
    for gap in map(Fraction, (-4, -1, 0, 2, 7)):
        for offset in map(Fraction, (-8, -2, 0, 3, 9)):
            assert midpoint_sign(gap, offset) == ((gap + offset > 0) - (gap + offset < 0))


def test_robust_bisection_all_extremal_error_paths():
    radius = Fraction(2)
    tolerance = Fraction(1, 4)
    rounds = ceil_log2_fraction(radius / tolerance)
    bound = rational_link_margin_constant(radius) * tolerance / 2
    gaps = [Fraction(k, 8) for k in range(-16, 17)]
    for gap in gaps:
        for errors in bounded_error_patterns(rounds, bound):
            receipt = robust_bisection_with_bounded_probability_error(
                gap, radius, tolerance, errors
            )
            assert receipt.absolute_error <= tolerance


def test_hoeffding_sample_bound_is_monotone():
    base = hoeffding_samples_per_query(0.1, 0.1, 1.0, 0.05, 40)
    tighter = hoeffding_samples_per_query(0.1, 0.05, 1.0, 0.05, 40)
    more_confident = hoeffding_samples_per_query(0.1, 0.1, 1.0, 0.01, 40)
    assert tighter > base
    assert more_confident > base


def test_flat_link_family_converges_uniformly_to_half():
    deviations = [
        flat_link_sup_deviation(Fraction(8), Fraction(1, 2**power))
        for power in range(1, 13)
    ]
    assert all(left > right for left, right in zip(deviations, deviations[1:]))
    assert deviations[-1] < Fraction(1, 250)


def test_no_offset_witness_remains_nonaffine():
    witness = no_offset_nonaffine_witness()
    source, target = witness["source"], witness["target"]
    source_scale = source[1] - source[0]
    target_scale = target[1] - target[0]
    assert source_scale == target_scale == 1
    assert source[2] != target[2]
    laws = no_offset_matching_laws()
    assert laws["same_law"]
    assert laws["admissible_target_knots"]
