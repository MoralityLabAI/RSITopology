"""Exact primal/dual solvers for finite source-fiber safety games."""

from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Iterable


def solve_linear_system(
    matrix: tuple[tuple[Fraction, ...], ...],
    rhs: tuple[Fraction, ...],
) -> tuple[Fraction, ...] | None:
    """Solve a square rational system, returning None when singular."""

    size = len(matrix)
    if size == 0 or len(rhs) != size or any(len(row) != size for row in matrix):
        raise ValueError("a nonempty square system is required")
    augmented = [
        [Fraction(value) for value in row] + [Fraction(rhs[index])]
        for index, row in enumerate(matrix)
    ]

    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if augmented[row][column] != 0),
            None,
        )
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    value - factor * pivot_entry
                    for value, pivot_entry in zip(augmented[row], augmented[column])
                ]
    return tuple(augmented[index][-1] for index in range(size))


def incidence_matrix(
    good_sets: Iterable[frozenset[int]], actions: tuple[int, ...]
) -> tuple[tuple[Fraction, ...], ...]:
    sets = tuple(good_sets)
    if not sets or not actions or len(set(actions)) != len(actions):
        raise ValueError("nonempty worlds and distinct actions are required")
    if any(not good for good in sets):
        raise ValueError("every world must have at least one good action")
    action_set = set(actions)
    if any(not good.issubset(action_set) for good in sets):
        raise ValueError("good sets must use registered actions")
    return tuple(
        tuple(Fraction(int(action in good)) for action in actions) for good in sets
    )


def primal_fiber_value(
    good_sets: Iterable[frozenset[int]], actions: tuple[int, ...]
) -> tuple[tuple[Fraction, ...], Fraction]:
    """Maximize the minimum good-action probability exactly."""

    incidence = incidence_matrix(good_sets, actions)
    action_count = len(actions)
    variable_count = action_count + 1  # probabilities, then t
    equality = tuple([Fraction(1)] * action_count + [Fraction(0)])

    active_candidates: list[tuple[Fraction, ...]] = []
    # A world constraint is sum_good p - t >= 0.
    active_candidates.extend(tuple(list(row) + [Fraction(-1)]) for row in incidence)
    # Probability nonnegativity p_j >= 0.
    for action_index in range(action_count):
        row = [Fraction(0)] * variable_count
        row[action_index] = 1
        active_candidates.append(tuple(row))

    feasible: list[tuple[Fraction, tuple[Fraction, ...]]] = []
    for active in itertools.combinations(active_candidates, action_count):
        matrix = (equality,) + active
        rhs = (Fraction(1),) + (Fraction(0),) * action_count
        solution = solve_linear_system(matrix, rhs)
        if solution is None:
            continue
        probabilities = solution[:-1]
        value = solution[-1]
        if any(probability < 0 for probability in probabilities):
            continue
        if any(
            sum(
                coefficient * probability
                for coefficient, probability in zip(row, probabilities)
            )
            < value
            for row in incidence
        ):
            continue
        feasible.append((value, tuple(probabilities)))

    if not feasible:
        raise AssertionError("fiber LP has no enumerated feasible vertex")
    value, probabilities = max(feasible, key=lambda item: (item[0], item[1]))
    return probabilities, value


def dual_fiber_value(
    good_sets: Iterable[frozenset[int]], actions: tuple[int, ...]
) -> tuple[tuple[Fraction, ...], Fraction]:
    """Minimize the largest action coverage under an adversarial world mixture."""

    incidence = incidence_matrix(good_sets, actions)
    world_count = len(incidence)
    variable_count = world_count + 1  # world weights, then z
    equality = tuple([Fraction(1)] * world_count + [Fraction(0)])

    active_candidates: list[tuple[Fraction, ...]] = []
    # z - sum_m incidence[m,a] lambda_m >= 0.
    for action_index in range(len(actions)):
        row = [
            -incidence[world_index][action_index] for world_index in range(world_count)
        ]
        row.append(Fraction(1))
        active_candidates.append(tuple(row))
    # World-mixture nonnegativity.
    for world_index in range(world_count):
        row = [Fraction(0)] * variable_count
        row[world_index] = 1
        active_candidates.append(tuple(row))

    feasible: list[tuple[Fraction, tuple[Fraction, ...]]] = []
    for active in itertools.combinations(active_candidates, world_count):
        matrix = (equality,) + active
        rhs = (Fraction(1),) + (Fraction(0),) * world_count
        solution = solve_linear_system(matrix, rhs)
        if solution is None:
            continue
        weights = solution[:-1]
        value = solution[-1]
        if any(weight < 0 for weight in weights):
            continue
        if any(
            value
            < sum(
                incidence[world_index][action_index] * weights[world_index]
                for world_index in range(world_count)
            )
            for action_index in range(len(actions))
        ):
            continue
        feasible.append((value, tuple(weights)))

    if not feasible:
        raise AssertionError("dual fiber LP has no enumerated feasible vertex")
    value, weights = min(feasible, key=lambda item: (item[0], item[1]))
    return weights, value
