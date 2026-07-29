"""Exact finite aggregate-randomized confidence procedures.

Development-only ASMP-9 v0.53 instrument.  A randomized direct procedure is a
conditional distribution q(report | outcome).  Coverage is imposed only after
averaging over the external randomization.  The exact optimizer is recovered
by rational basic-feasible-solution enumeration for small finite problems.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import combinations, product
from typing import Sequence


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def _validate_experiment(
    risks: Sequence[object],
    probability_rows: Sequence[Sequence[object]],
    alpha: object,
) -> tuple[tuple[Q, ...], tuple[tuple[Q, ...], ...], Q]:
    risks = tuple(q(value) for value in risks)
    rows = tuple(
        tuple(q(value) for value in row)
        for row in probability_rows
    )
    alpha = q(alpha)
    if not risks or len(risks) != len(rows):
        raise ValueError("risks and probability rows differ")
    widths = {len(row) for row in rows}
    if len(widths) != 1 or next(iter(widths)) < 1:
        raise ValueError("probability rows have inconsistent width")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0,1)")
    if any(risk < 0 for risk in risks):
        raise ValueError("risks must be nonnegative")
    if any(
        any(value < 0 for value in row)
        or sum(row, Q(0)) != 1
        for row in rows
    ):
        raise ValueError("invalid probability row")
    return risks, rows, alpha


def subset_bound_table(
    risks: Sequence[object],
    probability_rows: Sequence[Sequence[object]],
    alpha: object,
) -> tuple[Q, ...]:
    """Return B(S)=max{risk:P_theta(S)>alpha} for every subset."""

    risks, rows, alpha = _validate_experiment(
        risks, probability_rows, alpha
    )
    width = len(rows[0])
    result = []
    for mask in range(1 << width):
        eligible = []
        for risk, row in zip(risks, rows):
            mass = sum(
                (
                    row[index]
                    for index in range(width)
                    if mask & (1 << index)
                ),
                Q(0),
            )
            if mass > alpha:
                eligible.append(risk)
        result.append(max(eligible, default=Q(0)))
    return tuple(result)


def randomized_coverage_valid(
    probabilities: Sequence[Sequence[object]],
    risks: Sequence[object],
    probability_rows: Sequence[Sequence[object]],
    report_levels: Sequence[object],
    alpha: object,
) -> bool:
    """Check coverage of q(report | outcome) exactly."""

    risks, rows, alpha = _validate_experiment(
        risks, probability_rows, alpha
    )
    reports = tuple(q(value) for value in report_levels)
    conditional = tuple(
        tuple(q(value) for value in row)
        for row in probabilities
    )
    width = len(rows[0])
    if len(conditional) != width:
        raise ValueError("conditional distribution has wrong width")
    if any(
        len(row) != len(reports)
        or any(value < 0 for value in row)
        or sum(row, Q(0)) != 1
        for row in conditional
    ):
        raise ValueError("invalid conditional report distribution")
    for risk, law in zip(risks, rows):
        success = sum(
            (
                law[outcome] * conditional[outcome][report_index]
                for outcome in range(width)
                for report_index, report in enumerate(reports)
                if report >= risk
            ),
            Q(0),
        )
        if success < 1 - alpha:
            return False
    return True


def expected_report(
    probabilities: Sequence[Sequence[object]],
    report_levels: Sequence[object],
    reference_weights: Sequence[object],
) -> Q:
    reports = tuple(q(value) for value in report_levels)
    weights = tuple(q(value) for value in reference_weights)
    conditional = tuple(
        tuple(q(value) for value in row)
        for row in probabilities
    )
    if len(conditional) != len(weights):
        raise ValueError("reference width mismatch")
    if any(value <= 0 for value in weights):
        raise ValueError("reference weights must be positive")
    if sum(weights, Q(0)) != 1:
        raise ValueError("reference weights must sum to one")
    return sum(
        (
            weights[outcome]
            * conditional[outcome][report_index]
            * report
            for outcome in range(len(weights))
            for report_index, report in enumerate(reports)
        ),
        Q(0),
    )


def _solve_square(
    matrix: Sequence[Sequence[Q]],
    target: Sequence[Q],
) -> tuple[Q, ...] | None:
    size = len(target)
    if len(matrix) != size or any(len(row) != size for row in matrix):
        raise ValueError("linear system is not square")
    augmented = [
        list(row) + [value]
        for row, value in zip(matrix, target)
    ]
    for column in range(size):
        pivot = next(
            (
                row
                for row in range(column, size)
                if augmented[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            return None
        augmented[column], augmented[pivot] = (
            augmented[pivot],
            augmented[column],
        )
        scale = augmented[column][column]
        augmented[column] = [
            value / scale for value in augmented[column]
        ]
        for row in range(size):
            if row == column:
                continue
            scale = augmented[row][column]
            if scale:
                augmented[row] = [
                    left - scale * right
                    for left, right in zip(
                        augmented[row], augmented[column]
                    )
                ]
    return tuple(augmented[row][-1] for row in range(size))


@dataclass(frozen=True)
class RandomizedOptimum:
    value: Q
    optimizer: tuple[tuple[Q, ...], ...]
    optimal_vertex_count: int
    feasible_vertex_count: int
    maximum_positive_support: int


def exact_randomized_optimum(
    risks: Sequence[object],
    probability_rows: Sequence[Sequence[object]],
    report_levels: Sequence[object],
    alpha: object,
    reference_weights: Sequence[object],
) -> RandomizedOptimum:
    """Solve the finite randomized procedure by exact vertex enumeration."""

    risks, rows, alpha = _validate_experiment(
        risks, probability_rows, alpha
    )
    reports = tuple(q(value) for value in report_levels)
    weights = tuple(q(value) for value in reference_weights)
    width = len(rows[0])
    report_count = len(reports)
    variable_count = width * report_count
    if not 1 <= width <= 4 or not 2 <= report_count <= 4:
        raise ValueError("exact development solver cap exceeded")
    if len(weights) != width or any(value <= 0 for value in weights):
        raise ValueError("invalid reference weights")
    if sum(weights, Q(0)) != 1:
        raise ValueError("reference weights must sum to one")

    equalities = []
    targets = []
    for outcome in range(width):
        row = [Q(0)] * variable_count
        for report_index in range(report_count):
            row[outcome * report_count + report_index] = Q(1)
        equalities.append(tuple(row))
        targets.append(Q(1))

    active_candidates = []
    for risk, law in zip(risks, rows):
        row = [Q(0)] * variable_count
        for outcome in range(width):
            for report_index, report in enumerate(reports):
                if report >= risk:
                    row[outcome * report_count + report_index] = law[
                        outcome
                    ]
        active_candidates.append(
            ("coverage", tuple(row), Q(1) - alpha)
        )
    for variable in range(variable_count):
        row = [Q(0)] * variable_count
        row[variable] = Q(1)
        active_candidates.append(("zero", tuple(row), Q(0)))

    vertices = set()
    active_needed = variable_count - width
    for active in combinations(active_candidates, active_needed):
        solution = _solve_square(
            tuple(equalities) + tuple(row for _, row, _ in active),
            tuple(targets) + tuple(value for _, _, value in active),
        )
        if solution is None or any(value < 0 for value in solution):
            continue
        conditional = tuple(
            tuple(
                solution[outcome * report_count + report_index]
                for report_index in range(report_count)
            )
            for outcome in range(width)
        )
        if randomized_coverage_valid(
            conditional, risks, rows, reports, alpha
        ):
            vertices.add(conditional)
    if not vertices:
        raise AssertionError("feasible randomized polytope has no vertex")
    values = {
        vertex: expected_report(vertex, reports, weights)
        for vertex in vertices
    }
    optimum = min(values.values())
    optimizers = tuple(
        sorted(
            vertex
            for vertex, value in values.items()
            if value == optimum
        )
    )
    return RandomizedOptimum(
        value=optimum,
        optimizer=optimizers[0],
        optimal_vertex_count=len(optimizers),
        feasible_vertex_count=len(vertices),
        maximum_positive_support=max(
            sum(value > 0 for row in vertex for value in row)
            for vertex in vertices
        ),
    )


def exact_deterministic_optimum(
    risks: Sequence[object],
    probability_rows: Sequence[Sequence[object]],
    report_levels: Sequence[object],
    alpha: object,
    reference_weights: Sequence[object],
) -> tuple[Q, tuple[Q, ...]]:
    """Enumerate all deterministic direct maps."""

    risks, rows, alpha = _validate_experiment(
        risks, probability_rows, alpha
    )
    reports = tuple(q(value) for value in report_levels)
    weights = tuple(q(value) for value in reference_weights)
    width = len(rows[0])
    feasible = []
    for assignment in product(reports, repeat=width):
        conditional = tuple(
            tuple(
                Q(1) if report == selected else Q(0)
                for report in reports
            )
            for selected in assignment
        )
        if randomized_coverage_valid(
            conditional, risks, rows, reports, alpha
        ):
            feasible.append(
                (
                    expected_report(conditional, reports, weights),
                    assignment,
                )
            )
    if not feasible:
        raise AssertionError("no deterministic valid map")
    return min(feasible)


def two_experiment_witness() -> dict[str, object]:
    """Same deterministic subset table, different randomized optima."""

    alpha = Q(1, 2)
    reports = (Q(0), Q(1))
    weights = (Q(1, 2), Q(1, 2))
    rows = (
        (Q(3, 5), Q(2, 5)),
        (Q(9, 10), Q(1, 10)),
    )
    result = []
    for row in rows:
        deterministic = exact_deterministic_optimum(
            (Q(1),), (row,), reports, alpha, weights
        )
        randomized = exact_randomized_optimum(
            (Q(1),), (row,), reports, alpha, weights
        )
        p = row[0]
        dual_lambda = weights[0] / p
        dual_value = dual_lambda * (1 - alpha)
        result.append(
            {
                "probability_row": row,
                "subset_table": subset_bound_table(
                    (Q(1),), (row,), alpha
                ),
                "deterministic_value": deterministic[0],
                "deterministic_optimizer": deterministic[1],
                "randomized_value": randomized.value,
                "randomized_optimizer": randomized.optimizer,
                "dual_lambda": dual_lambda,
                "dual_value": dual_value,
                "dual_feasible": all(
                    dual_lambda * probability <= weight
                    for probability, weight in zip(row, weights)
                ),
            }
        )
    return {
        "alpha": alpha,
        "reports": reports,
        "reference_weights": weights,
        "experiments": tuple(result),
    }


def one_outcome_strict_gain(alpha: object = Q(1, 2)):
    """Return the minimal randomization-gain control."""

    alpha = q(alpha)
    deterministic = exact_deterministic_optimum(
        (Q(1),),
        ((Q(1),),),
        (Q(0), Q(1)),
        alpha,
        (Q(1),),
    )
    randomized = exact_randomized_optimum(
        (Q(1),),
        ((Q(1),),),
        (Q(0), Q(1)),
        alpha,
        (Q(1),),
    )
    return {
        "deterministic_value": deterministic[0],
        "randomized_value": randomized.value,
        "optimizer": randomized.optimizer,
    }
