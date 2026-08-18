from __future__ import annotations

import random
from fractions import Fraction

import pytest

from unknown_link import (
    _same_labeled_difference_order_direct,
    complete_pairwise_law,
    explicit_counterexample,
    interpolated_matching_link,
    inverse_rational_symmetric_link,
    labeled_difference_order_key,
    positive_affine_equivalent,
    rational_symmetric_link,
    recover_scaled_utility,
    same_labeled_difference_order,
    temperature_law,
)


@pytest.mark.parametrize(
    "value",
    [Fraction(index, 7) for index in range(-50, 51)],
)
def test_rational_link_inverse(value: Fraction) -> None:
    probability = rational_symmetric_link(value)
    assert inverse_rational_symmetric_link(probability) == value
    assert rational_symmetric_link(-value) == 1 - probability


@pytest.mark.parametrize("seed", range(16))
def test_unknown_temperature_recovers_scaled_utility(seed: int) -> None:
    rng = random.Random(seed)
    item_count = rng.randint(2, 12)
    utility = tuple(
        Fraction(rng.randint(-20, 20), rng.randint(1, 7))
        for _ in range(item_count)
    )
    beta = Fraction(rng.randint(1, 12), rng.randint(1, 12))
    law = temperature_law(utility, beta)
    recovered = recover_scaled_utility(item_count, law)
    expected = tuple(beta * (value - utility[0]) for value in utility)
    assert recovered == expected


def test_three_item_non_affine_models_have_identical_complete_laws() -> None:
    record = explicit_counterexample()
    assert record["same_law"]
    assert record["same_difference_order"]
    assert not record["positive_affine_equivalent"]
    assert record["source_law"] == {
        (0, 1): Fraction(3, 4),
        (0, 2): Fraction(7, 8),
        (1, 2): Fraction(5, 6),
    }


def test_same_known_link_distinguishes_the_counterexample() -> None:
    source = tuple(map(Fraction, (0, 1, 3)))
    target = tuple(map(Fraction, (0, 1, 4)))
    assert complete_pairwise_law(
        source, rational_symmetric_link
    ) != complete_pairwise_law(target, rational_symmetric_link)


@pytest.mark.parametrize(
    ("source", "target"),
    [
        ((0, 1, 3), (0, 1, 4)),
        ((0, 2, 7), (0, 3, 11)),
        ((-3, 0, 5), (-4, 0, 7)),
        ((0, 1, 4, 10), (0, 2, 7, 16)),
    ],
)
def test_interpolated_link_matches_order_aligned_models(
    source: tuple[int, ...], target: tuple[int, ...]
) -> None:
    source_q = tuple(map(Fraction, source))
    target_q = tuple(map(Fraction, target))
    assert same_labeled_difference_order(source_q, target_q)
    link = interpolated_matching_link(source_q, target_q)
    assert complete_pairwise_law(
        source_q, rational_symmetric_link
    ) == complete_pairwise_law(target_q, link)


def test_difference_order_mismatch_is_rejected() -> None:
    source = tuple(map(Fraction, (0, 1, 3)))
    target = tuple(map(Fraction, (0, 2, 3)))
    assert not same_labeled_difference_order(source, target)
    with pytest.raises(ValueError):
        interpolated_matching_link(source, target)


@pytest.mark.parametrize("seed", range(16))
def test_difference_order_key_matches_direct_reference(seed: int) -> None:
    rng = random.Random(seed)
    left = tuple(Fraction(rng.randint(-8, 8)) for _ in range(6))
    right = tuple(Fraction(rng.randint(-8, 8)) for _ in range(6))
    assert same_labeled_difference_order(
        left, right
    ) == _same_labeled_difference_order_direct(left, right)
    assert (
        labeled_difference_order_key(left)
        == labeled_difference_order_key(right)
    ) == same_labeled_difference_order(left, right)


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ((0, 1), (0, 17)),
        ((-5, 8), (100, 101)),
        ((3, 3), (-2, -2)),
    ],
)
def test_two_item_models_are_affine_equivalent(
    left: tuple[int, int], right: tuple[int, int]
) -> None:
    assert positive_affine_equivalent(
        tuple(map(Fraction, left)), tuple(map(Fraction, right))
    )


def test_repetition_cannot_separate_identical_population_laws() -> None:
    record = explicit_counterexample()
    for repetition_count in (1, 2, 10, 1000, 10**9):
        assert record["source_law"] == record["target_law"]
        assert repetition_count > 0
