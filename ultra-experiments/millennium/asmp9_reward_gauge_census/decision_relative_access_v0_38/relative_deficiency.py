"""Exact finite decision-relative experiment comparison for ASMP-9 v0.38.

This module implements a finite specialization of the rule-by-rule
comparison described by Torgersen for a *registered type* of decision
problems.  Nuisance is handled separately, using a frozen conditional law and
the marginal experiment described by Goel and DeGroot.

All scientific inputs and all returned optima are rational.  SymPy's exact
simplex implementation is used only as an optimizer; every returned rule and
risk vector is rechecked with :class:`fractions.Fraction`.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import linprog


Q = Fraction


def q(value: object) -> Q:
    if isinstance(value, Q):
        return value
    return Q(str(value))


@dataclass(frozen=True)
class _LinearConstraint:
    coefficients: tuple[Q, ...]
    rhs: Q
    label: str


@dataclass(frozen=True)
class _LinearOptimum:
    value: Q
    variables: tuple[Q, ...]
    active_labels: tuple[str, ...]
    dual_weights: tuple[Q, ...]


def _dot(left: Sequence[Q], right: Sequence[Q]) -> Q:
    return sum((a * b for a, b in zip(left, right)), Q(0))


def _solve_square(
    matrix: Sequence[Sequence[Q]], rhs: Sequence[Q]
) -> tuple[Q, ...] | None:
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


def _matrix_rank(matrix: Sequence[Sequence[Q]]) -> int:
    if not matrix:
        return 0
    work = [list(row) for row in matrix]
    row_count = len(work)
    column_count = len(work[0])
    rank = 0
    for column in range(column_count):
        pivot = next(
            (
                row
                for row in range(rank, row_count)
                if work[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(work[row], work[rank])
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def _minimize_last_coordinate(
    constraints: Sequence[_LinearConstraint], dimension: int
) -> _LinearOptimum:
    """Use a float proposal but accept only an exact primal-dual certificate."""

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

    def search(
        active_sets: Iterable[tuple[_LinearConstraint, ...]],
    ) -> _LinearOptimum | None:
        best: _LinearOptimum | None = None
        for active in active_sets:
            candidate = _solve_square(
                [constraint.coefficients for constraint in active],
                [constraint.rhs for constraint in active],
            )
            if candidate is None:
                continue
            if any(
                _dot(constraint.coefficients, candidate) > constraint.rhs
                for constraint in constraints
            ):
                continue
            dual = _solve_square(
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
            optimum = _LinearOptimum(
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
        return best

    marginals = np.asarray(float_result.ineqlin.marginals)
    ordered_tight = sorted(
        tight,
        key=lambda index: (
            0 if marginals[index] < -1e-9 else 1,
            -abs(marginals[index]),
            index,
        ),
    )
    basis_indices: list[int] = []
    basis_rows: list[tuple[Q, ...]] = []
    for index in ordered_tight:
        candidate_rows = basis_rows + [constraints[index].coefficients]
        if _matrix_rank(candidate_rows) > len(basis_rows):
            basis_indices.append(index)
            basis_rows.append(constraints[index].coefficients)
        if len(basis_indices) == dimension:
            break
    proposed = None
    if len(basis_indices) == dimension:
        proposed = search(
            [
                tuple(
                    constraints[index] for index in tuple(basis_indices)
                )
            ]
        )
    if proposed is None:
        proposed = search(
            (
                tuple(constraints[index] for index in indices)
                for indices in combinations(tight, dimension)
            )
        )
    if proposed is not None:
        return proposed
    fallback = search(combinations(constraints, dimension))
    if fallback is None:
        raise RuntimeError("no exact primal-dual LP certificate was found")
    return fallback


def _exact_linprog(
    objective: Sequence[Q],
    inequalities: Sequence[Sequence[Q]],
    inequality_rhs: Sequence[Q],
    equalities: Sequence[Sequence[Q]],
    equality_rhs: Sequence[Q],
) -> _LinearOptimum:
    """Solve an LP and return an exact checked primal-dual optimum."""

    if not inequalities:
        raise ValueError("at least one inequality is required")
    dimension = len(objective)
    if tuple(objective) != tuple([Q(0)] * (dimension - 1) + [Q(1)]):
        raise ValueError("exact helper expects the final coordinate objective")
    constraints = [
        _LinearConstraint(tuple(row), rhs, f"ub:{index}")
        for index, (row, rhs) in enumerate(
            zip(inequalities, inequality_rhs)
        )
    ]
    for index, (row, rhs) in enumerate(zip(equalities, equality_rhs)):
        frozen = tuple(row)
        constraints.append(_LinearConstraint(frozen, rhs, f"eq+:{index}"))
        constraints.append(
            _LinearConstraint(
                tuple(-value for value in frozen), -rhs, f"eq-:{index}"
            )
        )
    for index in range(dimension):
        row = [Q(0)] * dimension
        row[index] = Q(-1)
        constraints.append(
            _LinearConstraint(tuple(row), Q(0), f"nonnegative:{index}")
        )
    solution = _minimize_last_coordinate(constraints, dimension)
    optimum = solution.value
    variables = solution.variables
    if any(value < 0 for value in variables):
        raise RuntimeError("exact LP returned a negative variable")
    if any(
        sum((a * x for a, x in zip(row, variables)), Q(0)) > rhs
        for row, rhs in zip(inequalities, inequality_rhs)
    ):
        raise RuntimeError("exact simplex solution violates an inequality")
    if any(
        sum((a * x for a, x in zip(row, variables)), Q(0)) != rhs
        for row, rhs in zip(equalities, equality_rhs)
    ):
        raise RuntimeError("exact simplex solution violates an equality")
    if sum(
        (coefficient * value for coefficient, value in zip(objective, variables)),
        Q(0),
    ) != optimum:
        raise RuntimeError("exact simplex objective does not match its solution")
    return solution


@dataclass(frozen=True)
class FiniteExperiment:
    """A finite experiment with rows indexed by the target parameter."""

    rows: tuple[tuple[Q, ...], ...]

    def __post_init__(self) -> None:
        if not self.rows or not self.rows[0]:
            raise ValueError("an experiment needs targets and observations")
        width = len(self.rows[0])
        for row in self.rows:
            if len(row) != width:
                raise ValueError("experiment rows must have equal width")
            if any(value < 0 for value in row):
                raise ValueError("experiment probabilities must be nonnegative")
            if sum(row, Q(0)) != 1:
                raise ValueError("each experiment row must sum exactly to one")

    @property
    def target_count(self) -> int:
        return len(self.rows)

    @property
    def observation_count(self) -> int:
        return len(self.rows[0])


@dataclass(frozen=True)
class ExpandedExperiment:
    """A finite experiment indexed by target, nuisance, then observation."""

    rows: tuple[tuple[tuple[Q, ...], ...], ...]

    def __post_init__(self) -> None:
        if not self.rows or not self.rows[0] or not self.rows[0][0]:
            raise ValueError("expanded experiment dimensions must be nonempty")
        nuisance_count = len(self.rows[0])
        observation_count = len(self.rows[0][0])
        for target_rows in self.rows:
            if len(target_rows) != nuisance_count:
                raise ValueError("nuisance dimension must be rectangular")
            for row in target_rows:
                if len(row) != observation_count:
                    raise ValueError("observation dimension must be rectangular")
                if any(value < 0 for value in row):
                    raise ValueError("probabilities must be nonnegative")
                if sum(row, Q(0)) != 1:
                    raise ValueError("each expanded row must sum to one")

    @property
    def target_count(self) -> int:
        return len(self.rows)

    @property
    def nuisance_count(self) -> int:
        return len(self.rows[0])

    @property
    def observation_count(self) -> int:
        return len(self.rows[0][0])

    def flatten(self) -> FiniteExperiment:
        return FiniteExperiment(
            tuple(row for target_rows in self.rows for row in target_rows)
        )


@dataclass(frozen=True)
class DecisionProblem:
    """A bounded loss matrix with rows target and columns policy/action."""

    name: str
    losses: tuple[tuple[Q, ...], ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("decision problem needs a name")
        if not self.losses or not self.losses[0]:
            raise ValueError("loss matrix dimensions must be nonempty")
        width = len(self.losses[0])
        for row in self.losses:
            if len(row) != width:
                raise ValueError("loss matrix must be rectangular")
            if any(value < 0 or value > 1 for value in row):
                raise ValueError("registered losses must lie in [0,1]")

    @property
    def target_count(self) -> int:
        return len(self.losses)

    @property
    def action_count(self) -> int:
        return len(self.losses[0])


@dataclass(frozen=True)
class RuleTransferCertificate:
    problem: str
    reference_rule: tuple[int, ...]
    epsilon: Q
    source_rule: tuple[tuple[Q, ...], ...]
    source_risk: tuple[Q, ...]
    reference_risk: tuple[Q, ...]
    active_labels: tuple[str, ...]
    dual_weights: tuple[Q, ...]


@dataclass(frozen=True)
class RelativeDeficiencyCertificate:
    epsilon: Q
    problem: str
    reference_rule: tuple[int, ...]
    transfer: RuleTransferCertificate
    rules_checked: int


@dataclass(frozen=True)
class ValueCertificate:
    value: Q
    rule: tuple[tuple[Q, ...], ...]
    risks: tuple[Q, ...]
    active_labels: tuple[str, ...]
    dual_weights: tuple[Q, ...]


@dataclass(frozen=True)
class DeficiencyCertificate:
    epsilon: Q
    kernel: tuple[tuple[Q, ...], ...]
    total_variation: tuple[Q, ...]
    active_labels: tuple[str, ...]
    dual_weights: tuple[Q, ...]


def marginalize_nuisance(
    experiment: ExpandedExperiment,
    nuisance_law: Sequence[Sequence[Q]],
) -> FiniteExperiment:
    """Integrate nuisance with a registered P(xi | target)."""

    if len(nuisance_law) != experiment.target_count:
        raise ValueError("one nuisance law row is required per target")
    normalized = tuple(tuple(map(q, row)) for row in nuisance_law)
    for row in normalized:
        if len(row) != experiment.nuisance_count:
            raise ValueError("nuisance-law width mismatch")
        if any(value < 0 for value in row) or sum(row, Q(0)) != 1:
            raise ValueError("each nuisance-law row must be a distribution")
    return FiniteExperiment(
        tuple(
            tuple(
                sum(
                    (
                        normalized[target][nuisance]
                        * experiment.rows[target][nuisance][observation]
                        for nuisance in range(experiment.nuisance_count)
                    ),
                    Q(0),
                )
                for observation in range(experiment.observation_count)
            )
            for target in range(experiment.target_count)
        )
    )


def independent_binary_product(
    one_probabilities: Sequence[Sequence[Q]],
) -> FiniteExperiment:
    """Product of conditionally independent binary target experiments."""

    queries = tuple(tuple(map(q, row)) for row in one_probabilities)
    if not queries:
        raise ValueError("at least one binary query is required")
    target_count = len(queries[0])
    if any(len(row) != target_count for row in queries):
        raise ValueError("query target counts differ")
    if any(value < 0 or value > 1 for row in queries for value in row):
        raise ValueError("binary probabilities must lie in [0,1]")
    outcomes = tuple(product((0, 1), repeat=len(queries)))
    return FiniteExperiment(
        tuple(
            tuple(
                _product_fraction(
                    (
                        queries[index][target]
                        if bit
                        else Q(1) - queries[index][target]
                        for index, bit in enumerate(outcome)
                    )
                )
                for outcome in outcomes
            )
            for target in range(target_count)
        )
    )


def independent_binary_product_expanded(
    one_probabilities: Sequence[Sequence[Sequence[Q]]],
) -> ExpandedExperiment:
    """Product of binary experiments indexed by target and nuisance."""

    queries = tuple(
        tuple(tuple(map(q, row)) for row in query)
        for query in one_probabilities
    )
    if not queries:
        raise ValueError("at least one binary query is required")
    target_count = len(queries[0])
    nuisance_count = len(queries[0][0])
    if any(
        len(query) != target_count
        or any(len(row) != nuisance_count for row in query)
        for query in queries
    ):
        raise ValueError("expanded query dimensions differ")
    if any(
        value < 0 or value > 1
        for query in queries
        for row in query
        for value in row
    ):
        raise ValueError("binary probabilities must lie in [0,1]")
    outcomes = tuple(product((0, 1), repeat=len(queries)))
    return ExpandedExperiment(
        tuple(
            tuple(
                tuple(
                    _product_fraction(
                        (
                            queries[index][target][nuisance]
                            if bit
                            else Q(1)
                            - queries[index][target][nuisance]
                            for index, bit in enumerate(outcome)
                        )
                    )
                    for outcome in outcomes
                )
                for nuisance in range(nuisance_count)
            )
            for target in range(target_count)
        )
    )


def _product_fraction(values: Iterable[Q]) -> Q:
    result = Q(1)
    for value in values:
        result *= value
    return result


def deterministic_rules(
    observation_count: int, action_count: int
) -> Iterable[tuple[int, ...]]:
    return product(range(action_count), repeat=observation_count)


def deterministic_risk(
    experiment: FiniteExperiment,
    problem: DecisionProblem,
    rule: Sequence[int],
) -> tuple[Q, ...]:
    if experiment.target_count != problem.target_count:
        raise ValueError("experiment and loss target counts differ")
    if len(rule) != experiment.observation_count:
        raise ValueError("one action is required per observation")
    if any(action < 0 or action >= problem.action_count for action in rule):
        raise ValueError("rule action out of range")
    return tuple(
        sum(
            (
                experiment.rows[target][observation]
                * problem.losses[target][rule[observation]]
                for observation in range(experiment.observation_count)
            ),
            Q(0),
        )
        for target in range(experiment.target_count)
    )


def stochastic_risk(
    experiment: FiniteExperiment,
    problem: DecisionProblem,
    rule: Sequence[Sequence[Q]],
) -> tuple[Q, ...]:
    if len(rule) != experiment.observation_count:
        raise ValueError("one action distribution is required per observation")
    normalized = tuple(tuple(map(q, row)) for row in rule)
    for row in normalized:
        if len(row) != problem.action_count or sum(row, Q(0)) != 1:
            raise ValueError("invalid action distribution")
    return tuple(
        sum(
            (
                experiment.rows[target][observation]
                * normalized[observation][action]
                * problem.losses[target][action]
                for observation in range(experiment.observation_count)
                for action in range(problem.action_count)
            ),
            Q(0),
        )
        for target in range(experiment.target_count)
    )


def _unpack_rule(
    variables: Sequence[Q], observation_count: int, action_count: int
) -> tuple[tuple[Q, ...], ...]:
    return tuple(
        tuple(
            variables[observation * action_count + action]
            for action in range(action_count)
        )
        for observation in range(observation_count)
    )


def minimax_value(
    experiment: FiniteExperiment, problem: DecisionProblem
) -> ValueCertificate:
    """Exact optimized worst-target risk for one registered decision problem."""

    if experiment.target_count != problem.target_count:
        raise ValueError("experiment and loss target counts differ")
    probability_variables = experiment.observation_count * problem.action_count
    dimension = probability_variables + 1
    objective = [Q(0)] * dimension
    objective[-1] = Q(1)
    inequalities: list[list[Q]] = []
    rhs: list[Q] = []
    for target in range(experiment.target_count):
        row = [Q(0)] * dimension
        for observation in range(experiment.observation_count):
            for action in range(problem.action_count):
                row[observation * problem.action_count + action] = (
                    experiment.rows[target][observation]
                    * problem.losses[target][action]
                )
        row[-1] = Q(-1)
        inequalities.append(row)
        rhs.append(Q(0))
    equalities: list[list[Q]] = []
    equality_rhs: list[Q] = []
    for observation in range(experiment.observation_count):
        row = [Q(0)] * dimension
        for action in range(problem.action_count):
            row[observation * problem.action_count + action] = Q(1)
        equalities.append(row)
        equality_rhs.append(Q(1))
    solution = _exact_linprog(
        objective, inequalities, rhs, equalities, equality_rhs
    )
    value, variables = solution.value, solution.variables
    rule = _unpack_rule(
        variables, experiment.observation_count, problem.action_count
    )
    risks = stochastic_risk(experiment, problem, rule)
    if max(risks) != value:
        raise RuntimeError("minimax value does not equal maximum checked risk")
    return ValueCertificate(
        value=value,
        rule=rule,
        risks=risks,
        active_labels=solution.active_labels,
        dual_weights=solution.dual_weights,
    )


def transfer_reference_rule(
    source: FiniteExperiment,
    reference: FiniteExperiment,
    problem: DecisionProblem,
    reference_rule: Sequence[int],
) -> RuleTransferCertificate:
    """Minimum additive relaxation needed to dominate one reference rule."""

    if source.target_count != reference.target_count:
        raise ValueError("experiments must share a target space")
    if source.target_count != problem.target_count:
        raise ValueError("experiment and loss target counts differ")
    frozen_reference_rule = tuple(reference_rule)
    reference_risk = deterministic_risk(
        reference, problem, frozen_reference_rule
    )
    probability_variables = source.observation_count * problem.action_count
    dimension = probability_variables + 1
    objective = [Q(0)] * dimension
    objective[-1] = Q(1)
    inequalities: list[list[Q]] = []
    rhs: list[Q] = []
    for target in range(source.target_count):
        row = [Q(0)] * dimension
        for observation in range(source.observation_count):
            for action in range(problem.action_count):
                row[observation * problem.action_count + action] = (
                    source.rows[target][observation]
                    * problem.losses[target][action]
                )
        row[-1] = Q(-1)
        inequalities.append(row)
        rhs.append(reference_risk[target])
    equalities: list[list[Q]] = []
    equality_rhs: list[Q] = []
    for observation in range(source.observation_count):
        row = [Q(0)] * dimension
        for action in range(problem.action_count):
            row[observation * problem.action_count + action] = Q(1)
        equalities.append(row)
        equality_rhs.append(Q(1))
    solution = _exact_linprog(
        objective, inequalities, rhs, equalities, equality_rhs
    )
    epsilon, variables = solution.value, solution.variables
    rule = _unpack_rule(
        variables, source.observation_count, problem.action_count
    )
    source_risk = stochastic_risk(source, problem, rule)
    if any(
        left > right + epsilon
        for left, right in zip(source_risk, reference_risk)
    ):
        raise RuntimeError("transfer rule fails its exact risk bound")
    if epsilon < 0 or epsilon > 1:
        raise RuntimeError("normalized relative deficiency left [0,1]")
    return RuleTransferCertificate(
        problem=problem.name,
        reference_rule=frozen_reference_rule,
        epsilon=epsilon,
        source_rule=rule,
        source_risk=source_risk,
        reference_risk=reference_risk,
        active_labels=solution.active_labels,
        dual_weights=solution.dual_weights,
    )


def relative_deficiency(
    source: FiniteExperiment,
    reference: FiniteExperiment,
    problems: Sequence[DecisionProblem],
) -> RelativeDeficiencyCertificate:
    """Exact deficiency relative to a finite registered decision type.

    For each problem and every rule in the reference experiment, this finds a
    source rule whose target-risk vector is no more than ``epsilon`` worse.
    Deterministic reference rules suffice: the directed distance to the
    source's convex upper risk set is convex on the reference risk polytope,
    so its maximum is attained at an image of a deterministic rule.
    """

    if not problems:
        raise ValueError("at least one decision problem is required")
    worst: RuleTransferCertificate | None = None
    rules_checked = 0
    for problem in problems:
        for reference_rule in deterministic_rules(
            reference.observation_count, problem.action_count
        ):
            transfer = transfer_reference_rule(
                source, reference, problem, reference_rule
            )
            rules_checked += 1
            if worst is None or (
                transfer.epsilon,
                transfer.problem,
                transfer.reference_rule,
            ) > (
                worst.epsilon,
                worst.problem,
                worst.reference_rule,
            ):
                worst = transfer
    if worst is None:
        raise RuntimeError("relative-deficiency enumeration was empty")
    return RelativeDeficiencyCertificate(
        epsilon=worst.epsilon,
        problem=worst.problem,
        reference_rule=worst.reference_rule,
        transfer=worst,
        rules_checked=rules_checked,
    )


def optimized_value_gap(
    source: FiniteExperiment,
    reference: FiniteExperiment,
    problems: Sequence[DecisionProblem],
) -> Q:
    """Registered optimized minimax value gap G_D, not a deficiency."""

    if not problems:
        raise ValueError("at least one decision problem is required")
    return max(
        (
            max(
                Q(0),
                minimax_value(source, problem).value
                - minimax_value(reference, problem).value,
            )
            for problem in problems
        ),
        default=Q(0),
    )


def ordinary_deficiency(
    source: FiniteExperiment, reference: FiniteExperiment
) -> DeficiencyCertificate:
    """Exact directional Le Cam deficiency under total variation."""

    if source.target_count != reference.target_count:
        raise ValueError("experiments must share a parameter space")
    kernel_variables = source.observation_count * reference.observation_count
    deviation_variables = (
        source.target_count * reference.observation_count
    )
    dimension = kernel_variables + deviation_variables + 1
    t_index = dimension - 1
    objective = [Q(0)] * dimension
    objective[t_index] = Q(1)
    inequalities: list[list[Q]] = []
    rhs: list[Q] = []

    def kernel_index(source_observation: int, reference_observation: int) -> int:
        return (
            source_observation * reference.observation_count
            + reference_observation
        )

    def deviation_index(target: int, reference_observation: int) -> int:
        return (
            kernel_variables
            + target * reference.observation_count
            + reference_observation
        )

    for target in range(source.target_count):
        for reference_observation in range(reference.observation_count):
            mapped_minus_reference = [Q(0)] * dimension
            reference_minus_mapped = [Q(0)] * dimension
            for source_observation in range(source.observation_count):
                index = kernel_index(
                    source_observation, reference_observation
                )
                mapped_minus_reference[index] = source.rows[target][
                    source_observation
                ]
                reference_minus_mapped[index] = -source.rows[target][
                    source_observation
                ]
            deviation = deviation_index(target, reference_observation)
            mapped_minus_reference[deviation] = Q(-1)
            reference_minus_mapped[deviation] = Q(-1)
            inequalities.append(mapped_minus_reference)
            rhs.append(reference.rows[target][reference_observation])
            inequalities.append(reference_minus_mapped)
            rhs.append(-reference.rows[target][reference_observation])
        tv_row = [Q(0)] * dimension
        for reference_observation in range(reference.observation_count):
            tv_row[deviation_index(target, reference_observation)] = Q(1)
        tv_row[t_index] = Q(-2)
        inequalities.append(tv_row)
        rhs.append(Q(0))

    equalities: list[list[Q]] = []
    equality_rhs: list[Q] = []
    for source_observation in range(source.observation_count):
        row = [Q(0)] * dimension
        for reference_observation in range(reference.observation_count):
            row[kernel_index(source_observation, reference_observation)] = Q(1)
        equalities.append(row)
        equality_rhs.append(Q(1))
    solution = _exact_linprog(
        objective, inequalities, rhs, equalities, equality_rhs
    )
    epsilon, variables = solution.value, solution.variables
    kernel = tuple(
        tuple(
            variables[kernel_index(source_observation, reference_observation)]
            for reference_observation in range(reference.observation_count)
        )
        for source_observation in range(source.observation_count)
    )
    total_variation: list[Q] = []
    for target in range(source.target_count):
        mapped = tuple(
            sum(
                (
                    source.rows[target][source_observation]
                    * kernel[source_observation][reference_observation]
                    for source_observation in range(source.observation_count)
                ),
                Q(0),
            )
            for reference_observation in range(reference.observation_count)
        )
        tv = sum(
            (
                abs(mapped[observation] - reference.rows[target][observation])
                for observation in range(reference.observation_count)
            ),
            Q(0),
        ) / 2
        total_variation.append(tv)
    if max(total_variation) != epsilon:
        raise RuntimeError("deficiency optimum does not match checked TV")
    return DeficiencyCertificate(
        epsilon=epsilon,
        kernel=kernel,
        total_variation=tuple(total_variation),
        active_labels=solution.active_labels,
        dual_weights=solution.dual_weights,
    )


def policy_regret_problem(
    name: str,
    policy_occupancies: Sequence[Sequence[Q]],
    reward_representatives: Sequence[Sequence[Q]],
    normalization: Q = Q(1),
) -> DecisionProblem:
    """Construct a normalized policy-regret loss matrix."""

    occupancies = tuple(tuple(map(q, row)) for row in policy_occupancies)
    rewards = tuple(tuple(map(q, row)) for row in reward_representatives)
    if not occupancies or not rewards or normalization <= 0:
        raise ValueError("policy, reward, and normalization inputs are required")
    width = len(occupancies[0])
    if any(len(row) != width for row in occupancies + rewards):
        raise ValueError("occupancy and reward dimensions differ")
    losses: list[tuple[Q, ...]] = []
    for reward in rewards:
        values = tuple(
            sum((x * r for x, r in zip(policy, reward)), Q(0))
            for policy in occupancies
        )
        optimum = max(values)
        row = tuple((optimum - value) / normalization for value in values)
        if any(value < 0 or value > 1 for value in row):
            raise ValueError("normalization does not bound policy regret by one")
        losses.append(row)
    return DecisionProblem(name=name, losses=tuple(losses))
