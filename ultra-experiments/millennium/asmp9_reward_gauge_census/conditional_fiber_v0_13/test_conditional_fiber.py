from fractions import Fraction

from conditional_fiber import (
    conditional_weights,
    enumerate_fibers,
    exact_randomized_upper_test,
    fiber_affine_rank,
    flat_null_state_mass,
    gauge_transform_odds,
    graph_cycle_rank,
    incidence_rows,
)


def test_triangle_zero_balance_fiber_is_one_dimensional() -> None:
    edges = [(0, 1), (1, 2), (2, 0)]
    rows = incidence_rows(3, edges)
    fibers = enumerate_fibers([2, 2, 2], rows)
    zero = fibers[(0, 0, 0)]
    assert zero == [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    assert graph_cycle_rank(3, edges) == 1
    assert fiber_affine_rank(zero) == 1


def test_scalar_gauge_transform_is_exactly_invisible_on_fiber() -> None:
    edges = [(0, 1), (1, 2), (2, 0)]
    rows = incidence_rows(3, edges)
    fiber = enumerate_fibers([3, 3, 3], rows)[(0, 0, 0)]
    odds = (Fraction(2), Fraction(3, 2), Fraction(5, 3))
    transformed = gauge_transform_odds(
        odds, edges, (Fraction(2), Fraction(3), Fraction(5))
    )
    assert conditional_weights(fiber, [3, 3, 3], odds) == conditional_weights(
        fiber, [3, 3, 3], transformed
    )


def test_cycle_circulation_changes_conditional_law() -> None:
    edges = [(0, 1), (1, 2), (2, 0)]
    rows = incidence_rows(3, edges)
    fiber = enumerate_fibers([2, 2, 2], rows)[(0, 0, 0)]
    null = conditional_weights(
        fiber, [2, 2, 2], (Fraction(1),) * 3
    )
    alternative = conditional_weights(
        fiber, [2, 2, 2], (Fraction(2), Fraction(1), Fraction(1))
    )
    assert null != alternative
    ratios = [
        alternative[(z, z, z)] / null[(z, z, z)] for z in range(3)
    ]
    assert ratios[1] / ratios[0] == 2
    assert ratios[2] / ratios[1] == 2


def test_singleton_fiber_has_zero_visible_rank() -> None:
    edges = [(0, 1), (1, 2)]
    rows = incidence_rows(3, edges)
    fibers = enumerate_fibers([1, 1], rows)
    assert graph_cycle_rank(3, edges) == 0
    assert all(fiber_affine_rank(fiber) == 0 for fiber in fibers.values())


def test_flat_null_fiber_mass_is_normalized() -> None:
    edges = [(0, 1), (1, 2), (2, 0)]
    rows = incidence_rows(3, edges)
    mass = flat_null_state_mass(enumerate_fibers([2] * 3, rows), [2] * 3)
    assert sum(mass.values(), Fraction(0, 1)) == 1
    assert set(mass) == {0, 1}
    assert mass[1] > 0


def test_randomized_test_has_exact_size_and_increasing_power() -> None:
    weak = exact_randomized_upper_test(4, 3, Fraction(3, 2), Fraction(1, 20))
    strong = exact_randomized_upper_test(4, 3, Fraction(2), Fraction(1, 20))
    assert weak["size"] == Fraction(1, 20)
    assert strong["size"] == Fraction(1, 20)
    assert strong["power"] > weak["power"] > weak["size"]
