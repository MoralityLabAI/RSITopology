from fractions import Fraction

from moment_order import (
    LIMIT,
    ORDER_FOUR_WITNESS,
    ORDER_THREE_WITNESS,
    build_result,
    exact_upper_envelope,
    order_four_dual,
    reference_moment,
    tail,
    validate_law,
)


def test_order_three_counterexample_matches_reference_moments() -> None:
    validate_law(ORDER_THREE_WITNESS, 3)
    assert tail(ORDER_THREE_WITNESS) == Fraction(39, 625) > LIMIT


def test_order_four_dual_dominates_majority_indicator() -> None:
    assert all(
        order_four_dual(count) >= (1 if count >= 5 else 0)
        for count in range(10)
    )
    assert reference_moment(4) / 120 == Fraction(126, 3125) < LIMIT


def test_order_four_primal_witness_is_sharp() -> None:
    validate_law(ORDER_FOUR_WITNESS, 4)
    assert tail(ORDER_FOUR_WITNESS) == Fraction(126, 3125)


def test_vertex_enumeration_recovers_orders_one_through_four() -> None:
    expected = {
        1: Fraction(9, 25),
        2: Fraction(8, 75),
        3: Fraction(39, 625),
        4: Fraction(126, 3125),
    }
    for order, target in expected.items():
        maximum, _ = exact_upper_envelope(order)
        assert maximum == target


def test_minimum_certifying_order_is_four() -> None:
    result = build_result()
    assert result["certified"] is True
    assert result["minimum_certifying_order"] == 4

