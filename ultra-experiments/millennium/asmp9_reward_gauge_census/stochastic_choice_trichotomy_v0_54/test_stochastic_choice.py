from fractions import Fraction

import pytest

from stochastic_choice import (
    NO_RANDOM_UTILITY,
    RANDOM_UTILITY_NON_LUCE,
    SCALAR_LUCE,
    block_marschak_table,
    canonical_witnesses,
    classify,
    denominator_six_census,
    pair_projection,
)


def test_three_canonical_tiers_are_nonempty():
    witnesses = canonical_witnesses()
    assert classify(witnesses["scalar"]).status == SCALAR_LUCE
    assert classify(witnesses["random_utility_non_luce"]).status == RANDOM_UTILITY_NON_LUCE
    assert classify(witnesses["none"]).status == NO_RANDOM_UTILITY


def test_binary_access_cannot_decide_the_trichotomy():
    witnesses = canonical_witnesses()
    scalar = witnesses["scalar_access"]
    none = witnesses["none"]
    assert pair_projection(scalar) == pair_projection(none)
    assert classify(scalar).status == SCALAR_LUCE
    assert classify(none).status == NO_RANDOM_UTILITY


def test_no_object_witness_has_exact_regularity_violation():
    none = canonical_witnesses()["none"]
    assert none[(("a", "b", "c"), "a")] == Fraction(3, 4)
    assert none[(("a", "b"), "a")] == Fraction(1, 2)
    negative = [value for value in block_marschak_table(none, ("a", "b", "c")).values() if value < 0]
    assert negative


def test_middle_tier_certificate_reproduces_every_event():
    result = classify(canonical_witnesses()["random_utility_non_luce"])
    assert result.ranking_mixture is not None
    assert all(value >= 0 for _, value in result.ranking_mixture)
    assert sum((value for _, value in result.ranking_mixture), Fraction(0)) == 1


def test_denominator_six_census_is_complete_and_total():
    counts = {SCALAR_LUCE: 0, RANDOM_UTILITY_NON_LUCE: 0, NO_RANDOM_UTILITY: 0}
    total = 0
    for kernel in denominator_six_census():
        counts[classify(kernel).status] += 1
        total += 1
    assert total == 1250
    assert all(counts[status] > 0 for status in counts)


def test_invalid_kernel_is_rejected():
    broken = dict(canonical_witnesses()["scalar"])
    broken[(("a", "b"), "a")] = Fraction(1, 2)
    with pytest.raises(ValueError, match="normalize"):
        classify(broken)

