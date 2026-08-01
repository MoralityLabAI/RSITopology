"""Exact finite-experiment safety-deficiency primal and dual."""

from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Iterable

from fiber_lp import solve_linear_system


def validate_problem(
    experiment: tuple[tuple[Fraction, ...], ...],
    good_sets: tuple[frozenset[int], ...],
    actions: tuple[int, ...],
) -> None:
    if not experiment or not actions or len(experiment) != len(good_sets):
        raise ValueError(
            "nonempty matching models, good sets, and actions are required"
        )
    outcome_count = len(experiment[0])
    if outcome_count == 0 or any(len(row) != outcome_count for row in experiment):
        raise ValueError("experiment rows must have a common nonzero outcome count")
    if any(any(probability < 0 for probability in row) for row in experiment):
        raise ValueError("experiment probabilities must be nonnegative")
    if any(sum(row) != 1 for row in experiment):
        raise ValueError("every experiment row must sum to one")
    if len(set(actions)) != len(actions):
        raise ValueError("actions must be distinct")
    action_set = set(actions)
    if any(not good or not good.issubset(action_set) for good in good_sets):
        raise ValueError("every good set must be nonempty and use registered actions")


def primal_safety_value(
    experiment: tuple[tuple[Fraction, ...], ...],
    good_sets: tuple[frozenset[int], ...],
    actions: tuple[int, ...],
) -> tuple[tuple[tuple[Fraction, ...], ...], Fraction]:
    """Maximize uniform success over all observation-to-action kernels."""

    validate_problem(experiment, good_sets, actions)
    model_count = len(experiment)
    outcome_count = len(experiment[0])
    action_count = len(actions)
    kernel_variables = outcome_count * action_count
    variable_count = kernel_variables + 1  # terminal t

    equalities: list[tuple[Fraction, ...]] = []
    for outcome in range(outcome_count):
        row = [Fraction(0)] * variable_count
        for action_index in range(action_count):
            row[outcome * action_count + action_index] = 1
        equalities.append(tuple(row))

    active_candidates: list[tuple[Fraction, ...]] = []
    for model in range(model_count):
        row = [Fraction(0)] * variable_count
        for outcome in range(outcome_count):
            for action_index, action in enumerate(actions):
                if action in good_sets[model]:
                    row[outcome * action_count + action_index] = experiment[model][
                        outcome
                    ]
        row[-1] = -1
        active_candidates.append(tuple(row))
    for index in range(kernel_variables):
        row = [Fraction(0)] * variable_count
        row[index] = 1
        active_candidates.append(tuple(row))

    active_count = variable_count - len(equalities)
    rhs = (Fraction(1),) * len(equalities) + (Fraction(0),) * active_count
    feasible: list[tuple[Fraction, tuple[Fraction, ...]]] = []
    for active in itertools.combinations(active_candidates, active_count):
        solution = solve_linear_system(tuple(equalities) + active, rhs)
        if solution is None:
            continue
        kernel_flat = solution[:-1]
        value = solution[-1]
        if any(probability < 0 for probability in kernel_flat):
            continue
        successes = []
        for model in range(model_count):
            success = Fraction(0)
            for outcome in range(outcome_count):
                success += experiment[model][outcome] * sum(
                    kernel_flat[outcome * action_count + action_index]
                    for action_index, action in enumerate(actions)
                    if action in good_sets[model]
                )
            successes.append(success)
        if any(success < value for success in successes):
            continue
        feasible.append((value, tuple(kernel_flat)))

    if not feasible:
        raise AssertionError("finite safety LP has no enumerated primal vertex")
    value, kernel_flat = max(feasible, key=lambda item: (item[0], item[1]))
    kernel = tuple(
        tuple(
            kernel_flat[outcome * action_count + action_index]
            for action_index in range(action_count)
        )
        for outcome in range(outcome_count)
    )
    return kernel, value


def dual_safety_value(
    experiment: tuple[tuple[Fraction, ...], ...],
    good_sets: tuple[frozenset[int], ...],
    actions: tuple[int, ...],
) -> tuple[tuple[Fraction, ...], Fraction]:
    """Minimize Bayes-optimal success over least-favorable model priors."""

    validate_problem(experiment, good_sets, actions)
    model_count = len(experiment)
    outcome_count = len(experiment[0])
    variable_count = model_count + outcome_count  # lambdas, then z_x
    equality = tuple([Fraction(1)] * model_count + [Fraction(0)] * outcome_count)

    active_candidates: list[tuple[Fraction, ...]] = []
    for outcome in range(outcome_count):
        for action in actions:
            row = [Fraction(0)] * variable_count
            for model in range(model_count):
                if action in good_sets[model]:
                    row[model] = -experiment[model][outcome]
            row[model_count + outcome] = 1
            active_candidates.append(tuple(row))
    for model in range(model_count):
        row = [Fraction(0)] * variable_count
        row[model] = 1
        active_candidates.append(tuple(row))

    active_count = variable_count - 1
    rhs = (Fraction(1),) + (Fraction(0),) * active_count
    feasible: list[tuple[Fraction, tuple[Fraction, ...]]] = []
    for active in itertools.combinations(active_candidates, active_count):
        solution = solve_linear_system((equality,) + active, rhs)
        if solution is None:
            continue
        weights = solution[:model_count]
        outcome_values = solution[model_count:]
        if any(weight < 0 for weight in weights):
            continue
        valid = True
        for outcome in range(outcome_count):
            for action in actions:
                action_mass = sum(
                    weights[model] * experiment[model][outcome]
                    for model in range(model_count)
                    if action in good_sets[model]
                )
                if outcome_values[outcome] < action_mass:
                    valid = False
        if not valid:
            continue
        feasible.append((sum(outcome_values), tuple(weights)))

    if not feasible:
        raise AssertionError("finite safety LP has no enumerated dual vertex")
    value, weights = min(feasible, key=lambda item: (item[0], item[1]))
    return weights, value


def product_experiment(
    experiment: tuple[tuple[Fraction, ...], ...], sample_size: int
) -> tuple[tuple[Fraction, ...], ...]:
    """Return the ordered-sequence product experiment exactly."""

    if sample_size < 0:
        raise ValueError("sample_size must be nonnegative")
    if sample_size == 0:
        return tuple((Fraction(1),) for _row in experiment)
    outcome_count = len(experiment[0])
    sequences = tuple(itertools.product(range(outcome_count), repeat=sample_size))
    return tuple(
        tuple(_product(row[outcome] for outcome in sequence) for sequence in sequences)
        for row in experiment
    )


def _product(values: Iterable[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result
