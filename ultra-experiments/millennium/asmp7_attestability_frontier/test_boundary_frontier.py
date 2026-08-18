from fractions import Fraction
from math import comb

from attestability import ERROR_LIMIT
from boundary_frontier import (
    M_CAP,
    exact_optimal_test,
    forbidden_class_size,
    normal_reference_m,
    separation,
)


def test_compliant_boundary_and_gap_formula() -> None:
    for theta in (Fraction(1, 2), Fraction(3, 5), Fraction(2, 3), Fraction(1)):
        assert separation(8 + 1, theta) == (2 * theta - 1) * Fraction(1, 16)


def test_exact_size_and_predecessor_on_v0_1_cells() -> None:
    expected = {Fraction(3, 4): 73, Fraction(4, 5): 50, Fraction(1): 15}
    for theta, m_star in expected.items():
        current = exact_optimal_test(m_star, 14, theta)
        previous = exact_optimal_test(m_star - 1, 14, theta)
        assert current.fp == ERROR_LIMIT
        assert current.fn <= ERROR_LIMIT
        assert previous.fn > ERROR_LIMIT


def test_old_cap_failures_reproduce() -> None:
    for theta in (Fraction(1, 2), Fraction(3, 5), Fraction(2, 3)):
        assert not exact_optimal_test(128, 14, theta).feasible


def test_class_sizes_and_singleton_boundary() -> None:
    for k1 in range(9, 17):
        assert forbidden_class_size(k1) == sum(comb(16, k) for k in range(k1, 17))
    assert forbidden_class_size(14) == 137
    assert forbidden_class_size(15) == 17
    assert forbidden_class_size(16) == 1


def test_normal_reference_is_descriptive_and_ordered() -> None:
    assert normal_reference_m(9, Fraction(3, 5)) is not None
    assert normal_reference_m(9, Fraction(3, 5)) > normal_reference_m(9, Fraction(4, 5))
    assert normal_reference_m(9, Fraction(4, 5)) > normal_reference_m(14, Fraction(4, 5))


def test_uniform_cap_is_frozen_power_of_two() -> None:
    assert M_CAP == 32768

