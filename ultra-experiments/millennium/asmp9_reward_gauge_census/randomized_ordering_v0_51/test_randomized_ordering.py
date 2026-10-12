from fractions import Fraction as Q
from itertools import product

from randomized_ordering import (
    exact_minimax_strategy,
    exact_zero_sum_certificate,
    minimal_randomization_gain_witness,
    randomized_ordering_certificate,
)


def test_exact_matrix_game_primal_dual_and_strategies():
    payoff = (
        (Q(0), Q(1, 2)),
        (Q(1, 2), Q(0)),
    )
    primal, dual = exact_zero_sum_certificate(payoff)
    assert primal.value == Q(1, 4)
    assert dual.value == Q(1, 4)
    assert primal.probabilities == (Q(1, 2), Q(1, 2))
    assert dual.probabilities == (Q(1, 2), Q(1, 2))


def test_minimal_witness_halves_but_does_not_remove_regret():
    result = minimal_randomization_gain_witness()
    assert result.common_zero_order_count == 0
    assert result.deterministic_value == Q(1, 2)
    assert result.randomized_value == Q(1, 4)
    assert result.randomization_gain == Q(1, 4)
    assert result.primal_support_orders == ((0, 1), (1, 0))
    assert result.primal_dual_match
    assert result.complementary_slackness


def test_randomization_zero_iff_common_zero_order_exists():
    tables = (
        (Q(0), Q(0), Q(1), Q(1)),
        (Q(0), Q(0), Q(2), Q(2)),
    )
    vertices = (
        (Q(3, 4), Q(1, 4)),
        (Q(2, 3), Q(1, 3)),
    )
    result = randomized_ordering_certificate(tables, vertices)
    assert result.common_zero_order_count == 1
    assert result.randomized_value == 0
    assert result.deterministic_value == 0
    assert result.randomization_gain == 0
    assert result.primal_support_orders == ((0, 1),)


def test_randomization_never_worse_than_deterministic():
    tables = (
        (Q(0), Q(0), Q(1), Q(1), Q(0), Q(1), Q(1), Q(2)),
        (Q(0), Q(1), Q(0), Q(1), Q(0), Q(1), Q(2), Q(2)),
    )
    vertices = (
        (Q(1, 2), Q(1, 3), Q(1, 6)),
        (Q(1, 6), Q(1, 3), Q(1, 2)),
    )
    result = randomized_ordering_certificate(tables, vertices)
    assert result.randomized_value <= result.deterministic_value
    assert result.primal_dual_match
    assert result.complementary_slackness


def test_rectangular_game_exact_solver():
    payoff = (
        (Q(0), Q(1), Q(1)),
        (Q(1), Q(0), Q(1)),
    )
    strategy = exact_minimax_strategy(payoff)
    assert strategy.value == Q(1)
    assert sum(strategy.probabilities, Q(0)) == 1


def test_degenerate_game_uses_deterministic_tie_break():
    payoff = (
        (Q(0), Q(0)),
        (Q(0), Q(0)),
    )
    strategy = exact_minimax_strategy(payoff)
    assert strategy.value == 0
    assert strategy.probabilities == (Q(1), Q(0))


def test_all_small_two_by_two_values_match_direct_breakpoint_search():
    levels = (Q(0), Q(1, 2), Q(1))
    for entries in product(levels, repeat=4):
        payoff = (entries[:2], entries[2:])
        candidates = {Q(0), Q(1)}
        first_slope = payoff[0][0] - payoff[1][0]
        second_slope = payoff[0][1] - payoff[1][1]
        denominator = first_slope - second_slope
        if denominator:
            crossing = (
                payoff[1][1] - payoff[1][0]
            ) / denominator
            if 0 <= crossing <= 1:
                candidates.add(crossing)
        direct = min(
            max(
                probability * payoff[0][scenario]
                + (1 - probability) * payoff[1][scenario]
                for scenario in range(2)
            )
            for probability in candidates
        )
        assert exact_minimax_strategy(payoff).value == direct
