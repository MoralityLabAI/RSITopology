"""Exact finite statistical-experiment tools for ASMP-9 v0.37 development."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Hashable, Iterable, Sequence

import numpy as np
from scipy.optimize import linprog


Q = Fraction


@dataclass(frozen=True)
class LinearConstraint:
    coefficients: tuple[Q, ...]
    rhs: Q
    label: str


@dataclass(frozen=True)
class LinearOptimum:
    value: Q
    variables: tuple[Q, ...]
    active_labels: tuple[str, ...]
    dual_weights: tuple[Q, ...] = ()


@dataclass(frozen=True)
class BinaryExperiment:
    """Bernoulli response probabilities indexed by target then nuisance."""

    probabilities: tuple[tuple[Q, ...], ...]

    def __post_init__(self) -> None:
        if not self.probabilities or not self.probabilities[0]:
            raise ValueError("experiment must have targets and nuisance states")
        width = len(self.probabilities[0])
        for row in self.probabilities:
            if len(row) != width:
                raise ValueError("ragged nuisance dimension")
            if any(value < 0 or value > 1 for value in row):
                raise ValueError("probabilities must lie in [0,1]")

    @property
    def theta_count(self) -> int:
        return len(self.probabilities)

    @property
    def nuisance_count(self) -> int:
        return len(self.probabilities[0])

    def states(self) -> Iterable[tuple[int, int, Q]]:
        for theta, row in enumerate(self.probabilities):
            for nuisance, probability in enumerate(row):
                yield theta, nuisance, probability


def dot(left: Sequence[Q], right: Sequence[Q]) -> Q:
    return sum((a * b for a, b in zip(left, right)), Q(0))


def solve_square(
    matrix: Sequence[Sequence[Q]],
    rhs: Sequence[Q],
) -> tuple[Q, ...] | None:
    """Solve one exact square linear system, returning None if singular."""

    size = len(rhs)
    work = [list(row) + [rhs[index]] for index, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(
            (
                row
                for row in range(column, size)
                if work[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            return None
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(
                        work[row], work[column]
                    )
                ]
    return tuple(work[row][-1] for row in range(size))


def minimize_last_coordinate(
    constraints: Sequence[LinearConstraint],
    dimension: int,
) -> LinearOptimum:
    """Minimize the last variable with an exact primal-dual certificate."""

    best: LinearOptimum | None = None
    objective = tuple([Q(0)] * (dimension - 1) + [Q(1)])
    float_result = linprog(
        c=np.asarray([float(value) for value in objective]),
        A_ub=np.asarray(
            [
                [float(value) for value in constraint.coefficients]
                for constraint in constraints
            ]
        ),
        b_ub=np.asarray([float(constraint.rhs) for constraint in constraints]),
        bounds=[(None, None)] * dimension,
        method="highs",
    )
    if not float_result.success:
        raise ValueError(f"floating LP proposal failed: {float_result.message}")
    slacks = np.asarray(float_result.ineqlin.residual)
    tight = tuple(
        index for index, slack in enumerate(slacks) if abs(slack) <= 1e-7
    )
    proposed = tuple(
        tuple(constraints[index] for index in indices)
        for indices in combinations(tight, dimension)
    )
    active_sets: Iterable[tuple[LinearConstraint, ...]]
    active_sets = proposed or combinations(constraints, dimension)
    for active in active_sets:
        candidate = solve_square(
            [constraint.coefficients for constraint in active],
            [constraint.rhs for constraint in active],
        )
        if candidate is None:
            continue
        if any(
            dot(constraint.coefficients, candidate) > constraint.rhs
            for constraint in constraints
        ):
            continue
        dual = solve_square(
            [
                [active[row].coefficients[column] for row in range(dimension)]
                for column in range(dimension)
            ],
            tuple(-value for value in objective),
        )
        if dual is None or any(weight < 0 for weight in dual):
            continue
        dual_value = -sum(
            (
                constraint.rhs * weight
                for constraint, weight in zip(active, dual)
            ),
            Q(0),
        )
        if dual_value != candidate[-1]:
            continue
        optimum = LinearOptimum(
            value=candidate[-1],
            variables=candidate,
            active_labels=tuple(constraint.label for constraint in active),
            dual_weights=dual,
        )
        if best is None or (
            optimum.value,
            optimum.variables,
            optimum.active_labels,
        ) < (
            best.value,
            best.variables,
            best.active_labels,
        ):
            best = optimum
    if best is None:
        # Degenerate floating solutions can expose too few tight constraints.
        # The fallback is slower but remains exact and complete.
        for active in combinations(constraints, dimension):
            candidate = solve_square(
                [constraint.coefficients for constraint in active],
                [constraint.rhs for constraint in active],
            )
            if candidate is None or any(
                dot(constraint.coefficients, candidate) > constraint.rhs
                for constraint in constraints
            ):
                continue
            dual = solve_square(
                [
                    [
                        active[row].coefficients[column]
                        for row in range(dimension)
                    ]
                    for column in range(dimension)
                ],
                tuple(-value for value in objective),
            )
            if dual is None or any(weight < 0 for weight in dual):
                continue
            dual_value = -sum(
                (
                    constraint.rhs * weight
                    for constraint, weight in zip(active, dual)
                ),
                Q(0),
            )
            if dual_value != candidate[-1]:
                continue
            optimum = LinearOptimum(
                value=candidate[-1],
                variables=candidate,
                active_labels=tuple(
                    constraint.label for constraint in active
                ),
                dual_weights=dual,
            )
            if best is None or (
                optimum.value,
                optimum.variables,
                optimum.active_labels,
            ) < (
                best.value,
                best.variables,
                best.active_labels,
            ):
                best = optimum
    if best is None:
        raise ValueError("no exact primal-dual LP certificate found")
    return best


def bounded_variable_constraints(
    dimension: int,
    *,
    probability_variables: int,
) -> list[LinearConstraint]:
    constraints: list[LinearConstraint] = []
    for index in range(probability_variables):
        lower = [Q(0)] * dimension
        lower[index] = Q(-1)
        constraints.append(
            LinearConstraint(tuple(lower), Q(0), f"x{index}>=0")
        )
        upper = [Q(0)] * dimension
        upper[index] = Q(1)
        constraints.append(
            LinearConstraint(tuple(upper), Q(1), f"x{index}<=1")
        )
    lower_t = [Q(0)] * dimension
    lower_t[-1] = Q(-1)
    constraints.append(LinearConstraint(tuple(lower_t), Q(0), "t>=0"))
    upper_t = [Q(0)] * dimension
    upper_t[-1] = Q(1)
    constraints.append(LinearConstraint(tuple(upper_t), Q(1), "t<=1"))
    return constraints


def directional_deficiency(
    source: BinaryExperiment,
    target: BinaryExperiment,
) -> LinearOptimum:
    """Exact directional deficiency for two binary-output experiments."""

    if (
        source.theta_count != target.theta_count
        or source.nuisance_count != target.nuisance_count
    ):
        raise ValueError("experiments must share target/nuisance indices")

    # K is a binary Markov kernel:
    # a=P(target-output 1 | source-output 0)
    # b=P(target-output 1 | source-output 1).
    dimension = 3
    constraints = bounded_variable_constraints(
        dimension, probability_variables=2
    )
    for theta in range(source.theta_count):
        for nuisance in range(source.nuisance_count):
            p = source.probabilities[theta][nuisance]
            q = target.probabilities[theta][nuisance]
            positive = (Q(1) - p, p, Q(-1))
            negative = (-(Q(1) - p), -p, Q(-1))
            cell = f"{theta}:{nuisance}"
            constraints.append(
                LinearConstraint(positive, q, f"{cell}:mapped-q<=t")
            )
            constraints.append(
                LinearConstraint(negative, -q, f"{cell}:q-mapped<=t")
            )
    return minimize_last_coordinate(constraints, dimension)


def normalized_decisions(
    decisions: Sequence[Hashable],
) -> tuple[tuple[int, ...], int]:
    labels: dict[Hashable, int] = {}
    normalized: list[int] = []
    for decision in decisions:
        if decision not in labels:
            labels[decision] = len(labels)
        normalized.append(labels[decision])
    return tuple(normalized), len(labels)


def minimax_sample_risk(
    experiment: BinaryExperiment,
    decisions: Sequence[Hashable],
) -> LinearOptimum:
    """Exact minimax 0-1 risk from one sampled binary transcript."""

    if len(decisions) != experiment.theta_count:
        raise ValueError("one decision is required per target")
    normalized, action_count = normalized_decisions(decisions)
    if action_count == 1:
        return LinearOptimum(Q(0), (Q(0),), ("constant-decision",))

    free_per_observation = action_count - 1
    free_variables = 2 * free_per_observation
    dimension = free_variables + 1
    constraints = bounded_variable_constraints(
        dimension, probability_variables=free_variables
    )
    for observation in range(2):
        coefficients = [Q(0)] * dimension
        start = observation * free_per_observation
        for action in range(free_per_observation):
            coefficients[start + action] = Q(1)
        constraints.append(
            LinearConstraint(
                tuple(coefficients),
                Q(1),
                f"obs{observation}:simplex",
            )
        )

    for theta, nuisance, probability in experiment.states():
        true_action = normalized[theta]
        coefficients = [Q(0)] * dimension
        coefficients[-1] = Q(-1)
        if true_action < free_per_observation:
            coefficients[true_action] = -(Q(1) - probability)
            coefficients[
                free_per_observation + true_action
            ] = -probability
            rhs = Q(-1)
        else:
            for action in range(free_per_observation):
                coefficients[action] = Q(1) - probability
                coefficients[
                    free_per_observation + action
                ] = probability
            rhs = Q(0)
        constraints.append(
            LinearConstraint(
                tuple(coefficients),
                rhs,
                f"risk:{theta}:{nuisance}",
            )
        )
    return minimize_last_coordinate(constraints, dimension)


def minimax_correspondence_risk(
    observation_sets: Sequence[Iterable[Hashable]],
    decisions: Sequence[Hashable],
) -> LinearOptimum:
    """Exact minimax 0-1 risk for a set-valued population-law oracle."""

    if len(observation_sets) != len(decisions):
        raise ValueError("one observation set is required per target")
    frozen_sets = tuple(frozenset(values) for values in observation_sets)
    if any(not values for values in frozen_sets):
        raise ValueError("observation sets must be nonempty")
    universe = tuple(sorted(set().union(*frozen_sets), key=repr))
    observation_index = {
        observation: index for index, observation in enumerate(universe)
    }
    normalized, action_count = normalized_decisions(decisions)
    if action_count == 1:
        return LinearOptimum(Q(0), (Q(0),), ("constant-decision",))

    free_per_observation = action_count - 1
    free_variables = len(universe) * free_per_observation
    dimension = free_variables + 1
    constraints = bounded_variable_constraints(
        dimension, probability_variables=free_variables
    )
    for observation, index in observation_index.items():
        coefficients = [Q(0)] * dimension
        start = index * free_per_observation
        for action in range(free_per_observation):
            coefficients[start + action] = Q(1)
        constraints.append(
            LinearConstraint(
                tuple(coefficients),
                Q(1),
                f"obs:{observation!r}:simplex",
            )
        )

    for theta, observations in enumerate(frozen_sets):
        true_action = normalized[theta]
        for observation in observations:
            index = observation_index[observation]
            start = index * free_per_observation
            coefficients = [Q(0)] * dimension
            coefficients[-1] = Q(-1)
            if true_action < free_per_observation:
                coefficients[start + true_action] = Q(-1)
                rhs = Q(-1)
            else:
                for action in range(free_per_observation):
                    coefficients[start + action] = Q(1)
                rhs = Q(0)
            constraints.append(
                LinearConstraint(
                    tuple(coefficients),
                    rhs,
                    f"risk:{theta}:{observation!r}",
                )
            )
    return minimize_last_coordinate(constraints, dimension)


def connected_components(
    observation_sets: Sequence[Iterable[Hashable]],
) -> tuple[tuple[int, ...], ...]:
    frozen = tuple(frozenset(values) for values in observation_sets)
    adjacency = [
        {
            other
            for other, other_values in enumerate(frozen)
            if values & other_values
        }
        for values in frozen
    ]
    unseen = set(range(len(frozen)))
    components: list[tuple[int, ...]] = []
    while unseen:
        root = min(unseen)
        stack = [root]
        component: set[int] = set()
        while stack:
            node = stack.pop()
            if node in component:
                continue
            component.add(node)
            stack.extend(adjacency[node] - component)
        unseen -= component
        components.append(tuple(sorted(component)))
    return tuple(components)


def population_observation_sets(
    experiment: BinaryExperiment,
) -> tuple[frozenset[Q], ...]:
    return tuple(frozenset(row) for row in experiment.probabilities)


def sampled_support_sets(
    experiment: BinaryExperiment,
) -> tuple[frozenset[int], ...]:
    output: list[frozenset[int]] = []
    for row in experiment.probabilities:
        support: set[int] = set()
        if any(probability < 1 for probability in row):
            support.add(0)
        if any(probability > 0 for probability in row):
            support.add(1)
        output.append(frozenset(support))
    return tuple(output)
