import itertools
from fractions import Fraction

from decision_deficiency import majority_success
from finite_deficiency_lp import (
    dual_safety_value,
    primal_safety_value,
    product_experiment,
)


ACTIONS = (-1, 1)
OPPOSITE_GOOD = (frozenset((1,)), frozenset((-1,)))


def test_identical_experiment_has_exact_half_value() -> None:
    experiment = (
        (Fraction(1, 2), Fraction(1, 2)),
        (Fraction(1, 2), Fraction(1, 2)),
    )
    kernel, primal = primal_safety_value(experiment, OPPOSITE_GOOD, ACTIONS)
    weights, dual = dual_safety_value(experiment, OPPOSITE_GOOD, ACTIONS)
    assert primal == dual == Fraction(1, 2)
    assert sum(weights) == 1
    assert all(sum(row) == 1 for row in kernel)


def test_symmetric_separated_experiment_has_exact_three_quarters_value() -> None:
    experiment = (
        (Fraction(3, 4), Fraction(1, 4)),
        (Fraction(1, 4), Fraction(3, 4)),
    )
    _kernel, primal = primal_safety_value(experiment, OPPOSITE_GOOD, ACTIONS)
    _weights, dual = dual_safety_value(experiment, OPPOSITE_GOOD, ACTIONS)
    assert primal == dual == Fraction(3, 4)


def test_product_lp_matches_exact_majority_formula() -> None:
    signal = Fraction(1, 8)
    one_sample = (
        (Fraction(1, 2) + signal, Fraction(1, 2) - signal),
        (Fraction(1, 2) - signal, Fraction(1, 2) + signal),
    )
    for sample_size in range(3):
        experiment = product_experiment(one_sample, sample_size)
        _kernel, primal = primal_safety_value(experiment, OPPOSITE_GOOD, ACTIONS)
        _weights, dual = dual_safety_value(experiment, OPPOSITE_GOOD, ACTIONS)
        assert primal == dual == majority_success(sample_size, signal)


def test_complete_small_finite_experiment_primal_dual_census() -> None:
    probabilities = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))
    good_options = (
        frozenset((-1,)),
        frozenset((1,)),
        frozenset((-1, 1)),
    )
    for first_probability, second_probability in itertools.product(
        probabilities, repeat=2
    ):
        experiment = (
            (first_probability, 1 - first_probability),
            (second_probability, 1 - second_probability),
        )
        for good_sets in itertools.product(good_options, repeat=2):
            _kernel, primal = primal_safety_value(experiment, good_sets, ACTIONS)
            _weights, dual = dual_safety_value(experiment, good_sets, ACTIONS)
            assert primal == dual


def test_total_variation_upper_bounds_opposite_action_success() -> None:
    probabilities = (
        Fraction(1, 8),
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(3, 4),
        Fraction(7, 8),
    )
    for first_probability, second_probability in itertools.product(
        probabilities, repeat=2
    ):
        experiment = (
            (first_probability, 1 - first_probability),
            (second_probability, 1 - second_probability),
        )
        _kernel, success = primal_safety_value(experiment, OPPOSITE_GOOD, ACTIONS)
        total_variation = abs(first_probability - second_probability)
        assert success <= (1 + total_variation) / 2
