import itertools
from fractions import Fraction

from fiber_lp import dual_fiber_value, primal_fiber_value, solve_linear_system


def nonempty_subsets(actions: tuple[int, ...]) -> tuple[frozenset[int], ...]:
    return tuple(
        frozenset(action for index, action in enumerate(actions) if mask & (1 << index))
        for mask in range(1, 1 << len(actions))
    )


def test_rational_linear_solver() -> None:
    solution = solve_linear_system(
        (
            (Fraction(2), Fraction(1)),
            (Fraction(1), Fraction(-1)),
        ),
        (Fraction(1), Fraction(0)),
    )
    assert solution == (Fraction(1, 3), Fraction(1, 3))


def test_opposite_singletons_have_half_value_and_dual_witness() -> None:
    actions = (-1, 1)
    good_sets = (frozenset((-1,)), frozenset((1,)))
    probabilities, primal = primal_fiber_value(good_sets, actions)
    weights, dual = dual_fiber_value(good_sets, actions)
    assert probabilities == (Fraction(1, 2), Fraction(1, 2))
    assert weights == (Fraction(1, 2), Fraction(1, 2))
    assert primal == dual == Fraction(1, 2)


def test_common_good_action_has_value_one() -> None:
    actions = (-1, 1, 2)
    good_sets = (frozenset((-1, 2)), frozenset((1, 2)), frozenset((2,)))
    probabilities, primal = primal_fiber_value(good_sets, actions)
    _weights, dual = dual_fiber_value(good_sets, actions)
    assert probabilities[2] == 1
    assert primal == dual == 1


def test_primal_dual_equality_over_complete_small_hypergraph_census() -> None:
    for action_count in (2, 3):
        actions = tuple(range(action_count))
        subsets = nonempty_subsets(actions)
        for world_count in (1, 2, 3):
            for good_sets in itertools.product(subsets, repeat=world_count):
                probabilities, primal = primal_fiber_value(good_sets, actions)
                weights, dual = dual_fiber_value(good_sets, actions)
                assert sum(probabilities) == 1
                assert sum(weights) == 1
                assert primal == dual
