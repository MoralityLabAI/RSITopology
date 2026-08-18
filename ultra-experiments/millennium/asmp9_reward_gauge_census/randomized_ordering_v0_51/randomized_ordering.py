"""Exact mixed evidence-ordering certificates for finite ASMP-9 games."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import combinations, permutations
from typing import Sequence


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def _solve_square(
    matrix: Sequence[Sequence[Q]],
    right: Sequence[Q],
) -> tuple[Q, ...] | None:
    width = len(right)
    if len(matrix) != width or any(
        len(row) != width for row in matrix
    ):
        raise ValueError("linear system must be square")
    augmented = [
        [q(value) for value in row] + [q(rhs)]
        for row, rhs in zip(matrix, right)
    ]
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(column, width)
                if augmented[row][column]
            ),
            None,
        )
        if pivot is None:
            return None
        if pivot != column:
            augmented[column], augmented[pivot] = (
                augmented[pivot],
                augmented[column],
            )
        scale = augmented[column][column]
        augmented[column] = [
            value / scale for value in augmented[column]
        ]
        for row in range(width):
            if row == column:
                continue
            scale = augmented[row][column]
            if not scale:
                continue
            augmented[row] = [
                left - scale * right_value
                for left, right_value in zip(
                    augmented[row], augmented[column]
                )
            ]
    return tuple(augmented[row][-1] for row in range(width))


@dataclass(frozen=True)
class MinimaxStrategy:
    value: Q
    probabilities: tuple[Q, ...]
    active_scenarios: tuple[int, ...]
    support: tuple[int, ...]
    feasible_vertex_count: int


def exact_minimax_strategy(
    payoff: Sequence[Sequence[object]],
) -> MinimaxStrategy:
    """Solve min_p max_j E_p[A_ij] by exact LP vertex enumeration."""

    matrix = tuple(
        tuple(q(value) for value in row) for row in payoff
    )
    if not matrix or not matrix[0]:
        raise ValueError("payoff matrix must be nonempty")
    column_count = len(matrix[0])
    if any(len(row) != column_count for row in matrix):
        raise ValueError("payoff matrix must be rectangular")
    row_count = len(matrix)
    if row_count > 9 or column_count > 20:
        raise ValueError("exact vertex enumeration cap exceeded")

    # Variables are p_0,...,p_(m-1),t.  The simplex equality is always
    # active.  A vertex has m additional independent active inequalities,
    # selected from n scenario bounds and m nonnegativity bounds.
    constraint_count = column_count + row_count
    feasible = []
    for active in combinations(range(constraint_count), row_count):
        equations = [[Q(0)] * (row_count + 1)]
        equations[0][:row_count] = [Q(1)] * row_count
        right = [Q(1)]
        for constraint in active:
            row = [Q(0)] * (row_count + 1)
            if constraint < column_count:
                scenario = constraint
                for action in range(row_count):
                    row[action] = matrix[action][scenario]
                row[-1] = Q(-1)
            else:
                action = constraint - column_count
                row[action] = Q(1)
            equations.append(row)
            right.append(Q(0))
        solution = _solve_square(equations, right)
        if solution is None:
            continue
        probabilities = solution[:-1]
        value = solution[-1]
        if any(probability < 0 for probability in probabilities):
            continue
        scenario_values = tuple(
            sum(
                (
                    probabilities[action] * matrix[action][scenario]
                    for action in range(row_count)
                ),
                Q(0),
            )
            for scenario in range(column_count)
        )
        if any(result > value for result in scenario_values):
            continue
        feasible.append(
            (
                value,
                probabilities,
                tuple(
                    scenario
                    for scenario, result in enumerate(scenario_values)
                    if result == value
                ),
            )
        )
    if not feasible:
        raise AssertionError("bounded minimax LP has no feasible vertex")
    optimum = min(row[0] for row in feasible)
    candidates = [row for row in feasible if row[0] == optimum]
    # Deterministic tie-break: lexicographically maximize probabilities on
    # earlier action indices.
    value, probabilities, active_scenarios = max(
        candidates, key=lambda row: row[1]
    )
    return MinimaxStrategy(
        value=value,
        probabilities=probabilities,
        active_scenarios=active_scenarios,
        support=tuple(
            index
            for index, probability in enumerate(probabilities)
            if probability
        ),
        feasible_vertex_count=len(feasible),
    )


def exact_zero_sum_certificate(
    payoff: Sequence[Sequence[object]],
) -> tuple[MinimaxStrategy, MinimaxStrategy]:
    """Return exact primal and dual strategies for a finite matrix game."""

    matrix = tuple(
        tuple(q(value) for value in row) for row in payoff
    )
    primal = exact_minimax_strategy(matrix)
    negative_transpose = tuple(
        tuple(-matrix[action][scenario] for action in range(len(matrix)))
        for scenario in range(len(matrix[0]))
    )
    dual_min = exact_minimax_strategy(negative_transpose)
    dual = MinimaxStrategy(
        value=-dual_min.value,
        probabilities=dual_min.probabilities,
        active_scenarios=dual_min.active_scenarios,
        support=dual_min.support,
        feasible_vertex_count=dual_min.feasible_vertex_count,
    )
    if primal.value != dual.value:
        raise AssertionError("exact primal and dual values differ")
    return primal, dual


def ordering_feature_vector(
    ordering: Sequence[int],
    bounds: Sequence[object],
) -> tuple[Q, ...]:
    ordering = tuple(int(index) for index in ordering)
    bounds = tuple(q(value) for value in bounds)
    width = len(ordering)
    if sorted(ordering) != list(range(width)):
        raise ValueError("ordering is not a permutation")
    if len(bounds) != 1 << width:
        raise ValueError("bound table has wrong width")
    result = [Q(0)] * width
    mask = 0
    for index in ordering:
        mask |= 1 << index
        result[index] = bounds[mask]
    return tuple(result)


def ordering_cost(ordering, bounds, weights) -> Q:
    feature = ordering_feature_vector(ordering, bounds)
    weights = tuple(q(value) for value in weights)
    if len(weights) != len(feature):
        raise ValueError("reference weights have wrong width")
    return sum(
        (left * right for left, right in zip(feature, weights)),
        Q(0),
    )


def _validated_inputs(bound_tables, reference_vertices):
    tables = tuple(
        tuple(q(value) for value in table)
        for table in bound_tables
    )
    if not tables:
        raise ValueError("at least one objective is required")
    sizes = {len(table) for table in tables}
    if len(sizes) != 1:
        raise ValueError("bound tables have different widths")
    size = next(iter(sizes))
    if size < 2 or size & (size - 1):
        raise ValueError("bound table size must be a power of two")
    width = size.bit_length() - 1
    if width > 8:
        raise ValueError("ordering enumeration cap exceeded")
    vertices = tuple(
        tuple(q(value) for value in row)
        for row in reference_vertices
    )
    if not vertices:
        raise ValueError("at least one reference vertex is required")
    for vertex in vertices:
        if len(vertex) != width:
            raise ValueError("reference vertex has wrong width")
        if any(value <= 0 for value in vertex):
            raise ValueError("reference weights must be positive")
        if sum(vertex, Q(0)) != 1:
            raise ValueError("reference weights must sum to one")
    return tables, vertices, width


@dataclass(frozen=True)
class RandomizedOrderingCertificate:
    outcome_count: int
    ordering_count: int
    scenario_count: int
    payoff_matrix: tuple[tuple[Q, ...], ...]
    common_zero_order_count: int
    deterministic_value: Q
    deterministic_optimizer_count: int
    randomized_value: Q
    randomization_gain: Q
    primal_probabilities: tuple[Q, ...]
    primal_support_orders: tuple[tuple[int, ...], ...]
    dual_probabilities: tuple[Q, ...]
    dual_support_scenarios: tuple[tuple[int, int], ...]
    primal_dual_match: bool
    complementary_slackness: bool


def randomized_ordering_certificate(
    bound_tables: Sequence[Sequence[object]],
    reference_vertices: Sequence[Sequence[object]],
) -> RandomizedOrderingCertificate:
    tables, vertices, width = _validated_inputs(
        bound_tables, reference_vertices
    )
    orders = tuple(permutations(range(width)))
    scenarios = tuple(
        (objective, vertex)
        for objective in range(len(tables))
        for vertex in range(len(vertices))
    )
    optima = {}
    for objective, vertex in scenarios:
        optima[(objective, vertex)] = min(
            ordering_cost(order, tables[objective], vertices[vertex])
            for order in orders
        )
    payoff = tuple(
        tuple(
            ordering_cost(
                order, tables[objective], vertices[vertex]
            )
            - optima[(objective, vertex)]
            for objective, vertex in scenarios
        )
        for order in orders
    )
    row_worst = tuple(max(row) for row in payoff)
    deterministic = min(row_worst)
    deterministic_count = sum(
        value == deterministic for value in row_worst
    )
    common_zero = sum(all(value == 0 for value in row) for row in payoff)
    primal, dual = exact_zero_sum_certificate(payoff)

    column_expectations = tuple(
        sum(
            (
                primal.probabilities[action]
                * payoff[action][scenario]
                for action in range(len(orders))
            ),
            Q(0),
        )
        for scenario in range(len(scenarios))
    )
    row_expectations = tuple(
        sum(
            (
                dual.probabilities[scenario]
                * payoff[action][scenario]
                for scenario in range(len(scenarios))
            ),
            Q(0),
        )
        for action in range(len(orders))
    )
    slackness = (
        all(value <= primal.value for value in column_expectations)
        and all(value >= dual.value for value in row_expectations)
        and all(
            not primal.probabilities[action]
            or row_expectations[action] == primal.value
            for action in range(len(orders))
        )
        and all(
            not dual.probabilities[scenario]
            or column_expectations[scenario] == dual.value
            for scenario in range(len(scenarios))
        )
    )
    if (primal.value == 0) != bool(common_zero):
        raise AssertionError("zero-regret support theorem failed")
    return RandomizedOrderingCertificate(
        outcome_count=width,
        ordering_count=len(orders),
        scenario_count=len(scenarios),
        payoff_matrix=payoff,
        common_zero_order_count=common_zero,
        deterministic_value=deterministic,
        deterministic_optimizer_count=deterministic_count,
        randomized_value=primal.value,
        randomization_gain=deterministic - primal.value,
        primal_probabilities=primal.probabilities,
        primal_support_orders=tuple(
            orders[index] for index in primal.support
        ),
        dual_probabilities=dual.probabilities,
        dual_support_scenarios=tuple(
            scenarios[index] for index in dual.support
        ),
        primal_dual_match=primal.value == dual.value,
        complementary_slackness=slackness,
    )


def minimal_randomization_gain_witness():
    bounds = (Q(0), Q(0), Q(0), Q(1))
    vertices = (
        (Q(3, 4), Q(1, 4)),
        (Q(1, 4), Q(3, 4)),
    )
    return randomized_ordering_certificate((bounds,), vertices)
