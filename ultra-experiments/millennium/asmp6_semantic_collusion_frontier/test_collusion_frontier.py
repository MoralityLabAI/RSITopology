from fractions import Fraction

from collusion_frontier import (
    COVER,
    as_distribution,
    audit_maps,
    chi_squared,
    covertness,
    encoder_laws,
    minimax_binary_error,
    mixture,
    pushforward_counts,
)


def test_registered_counts() -> None:
    assert len(encoder_laws()) == 35
    assert len(audit_maps()) == 256


def test_randomized_minimax_decoder_boundaries() -> None:
    same = COVER
    assert minimax_binary_error(same, same) == Fraction(1, 2)
    left = (Fraction(1), Fraction(0), Fraction(0), Fraction(0))
    right = (Fraction(0), Fraction(1), Fraction(0), Fraction(0))
    assert minimax_binary_error(left, right) == 0


def test_mixture_and_messagewise_covertness_are_distinct() -> None:
    p0 = (Fraction(1, 2), Fraction(1, 2), Fraction(0), Fraction(0))
    p1 = (Fraction(0), Fraction(0), Fraction(1, 2), Fraction(1, 2))
    assert mixture(p0, p1) == COVER
    assert covertness(p0, p1, "mixture") == 0
    assert covertness(p0, p1, "per_message") == Fraction(1, 2)


def test_dual_chi_squared_orientation_and_support() -> None:
    sparse = (Fraction(1, 2), Fraction(1, 2), Fraction(0), Fraction(0))
    assert chi_squared(COVER, sparse) is None
    assert chi_squared(sparse, COVER) == 1
    assert chi_squared(COVER, COVER) == 0


def test_constant_audit_map_kills_every_registered_code() -> None:
    mapping = (0, 0, 0, 0)
    for left in encoder_laws():
        for right in encoder_laws():
            pushed_left = as_distribution(pushforward_counts(left, mapping))
            pushed_right = as_distribution(pushforward_counts(right, mapping))
            assert minimax_binary_error(pushed_left, pushed_right) == Fraction(1, 2)
