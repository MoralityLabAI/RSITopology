"""Exact finite sequential risk-access compiler for ASMP-9 v0.41.

The compiler represents a finite-horizon adaptive experiment by generators of
its coordinate-wise upper risk polytope.  It intentionally targets small exact
registries: the number of deterministic policy trees grows rapidly.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import sys
from typing import Iterable, Sequence


V38 = Path(__file__).resolve().parents[1] / "decision_relative_access_v0_38"
if str(V38) not in sys.path:
    sys.path.append(str(V38))

from relative_deficiency import _exact_linprog  # noqa: E402


RiskVector = tuple[Q, ...]


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


@dataclass(frozen=True)
class DecisionProblem:
    name: str
    losses: tuple[tuple[Q, ...], ...]

    def __post_init__(self) -> None:
        if not self.losses or not self.losses[0]:
            raise ValueError("a decision problem needs targets and actions")
        action_count = len(self.losses[0])
        for row in self.losses:
            if len(row) != action_count:
                raise ValueError("loss rows must have one common action count")
            if any(value < 0 for value in row):
                raise ValueError("losses must be nonnegative")

    @property
    def target_count(self) -> int:
        return len(self.losses)

    @property
    def action_count(self) -> int:
        return len(self.losses[0])


@dataclass(frozen=True)
class QueryChannel:
    name: str
    rows: tuple[tuple[Q, ...], ...]

    def __post_init__(self) -> None:
        if not self.rows or not self.rows[0]:
            raise ValueError("a query needs targets and outcomes")
        outcome_count = len(self.rows[0])
        for row in self.rows:
            if len(row) != outcome_count:
                raise ValueError("query rows must have one outcome count")
            if any(value < 0 for value in row):
                raise ValueError("query probabilities must be nonnegative")
            if sum(row, Q(0)) != 1:
                raise ValueError("every query row must sum exactly to one")

    @property
    def target_count(self) -> int:
        return len(self.rows)

    @property
    def outcome_count(self) -> int:
        return len(self.rows[0])


def classification_problem(target_count: int) -> DecisionProblem:
    if target_count < 2:
        raise ValueError("classification needs at least two targets")
    return DecisionProblem(
        name=f"{target_count}_class_identification",
        losses=tuple(
            tuple(Q(int(target != action)) for action in range(target_count))
            for target in range(target_count)
        ),
    )


def binary_group_problem(
    name: str,
    labels: Sequence[int],
    false_positive_cost: Q,
    false_negative_cost: Q = Q(1),
) -> DecisionProblem:
    frozen = tuple(int(value) for value in labels)
    if set(frozen) != {0, 1}:
        raise ValueError("a binary group problem needs both labels")
    false_positive_cost = q(false_positive_cost)
    false_negative_cost = q(false_negative_cost)
    if false_positive_cost <= 0 or false_negative_cost <= 0:
        raise ValueError("both error costs must be positive")
    return DecisionProblem(
        name,
        tuple(
            (
                (Q(0), false_positive_cost)
                if label == 0
                else (false_negative_cost, Q(0))
            )
            for label in frozen
        ),
    )


def deterministic_binary_query(
    name: str, outcomes_by_target: Sequence[int]
) -> QueryChannel:
    frozen = tuple(int(value) for value in outcomes_by_target)
    if set(frozen).difference((0, 1)):
        raise ValueError("binary outcomes must be zero or one")
    return QueryChannel(
        name,
        tuple(
            (Q(1), Q(0)) if value == 0 else (Q(0), Q(1))
            for value in frozen
        ),
    )


def terminal_generators(problem: DecisionProblem) -> tuple[RiskVector, ...]:
    return tuple(
        tuple(problem.losses[target][action] for target in range(problem.target_count))
        for action in range(problem.action_count)
    )


def _dominates(left: RiskVector, right: RiskVector) -> bool:
    return left != right and all(a <= b for a, b in zip(left, right))


def upper_minimal_generators(
    vectors: Iterable[RiskVector],
) -> tuple[RiskVector, ...]:
    """Drop duplicates and coordinate-wise dominated risk generators.

    Removing a dominated vector preserves the coordinate-wise upper convex
    closure used by the access criterion.
    """

    unique = tuple(sorted(set(tuple(map(q, vector)) for vector in vectors)))
    if not unique:
        raise ValueError("at least one risk vector is required")
    width = len(unique[0])
    if any(len(vector) != width for vector in unique):
        raise ValueError("risk vectors must share one target dimension")
    return tuple(
        vector
        for vector in unique
        if not any(_dominates(other, vector) for other in unique)
    )


def query_step_generators(
    query: QueryChannel,
    continuation: Sequence[RiskVector],
) -> tuple[RiskVector, ...]:
    """Compose one query with outcome-indexed continuation policies."""

    continuation = upper_minimal_generators(continuation)
    if len(continuation[0]) != query.target_count:
        raise ValueError("query and continuation target counts differ")
    generated = []
    for branch_vectors in product(
        continuation, repeat=query.outcome_count
    ):
        generated.append(
            tuple(
                sum(
                    (
                        query.rows[target][outcome]
                        * branch_vectors[outcome][target]
                        for outcome in range(query.outcome_count)
                    ),
                    Q(0),
                )
                for target in range(query.target_count)
            )
        )
    return upper_minimal_generators(generated)


def adaptive_upper_generators(
    queries: Sequence[QueryChannel],
    problem: DecisionProblem,
    horizon: int,
) -> tuple[RiskVector, ...]:
    """Generators for policies using at most ``horizon`` adaptive queries."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    queries = tuple(queries)
    if not queries and horizon:
        raise ValueError("a positive horizon needs at least one query")
    if any(query.target_count != problem.target_count for query in queries):
        raise ValueError("query and problem target counts differ")
    terminal = terminal_generators(problem)
    current = upper_minimal_generators(terminal)
    for _ in range(horizon):
        generated = list(terminal)
        for query in queries:
            generated.extend(query_step_generators(query, current))
        current = upper_minimal_generators(generated)
    return current


def fixed_sequence_upper_generators(
    sequence: Sequence[QueryChannel],
    problem: DecisionProblem,
) -> tuple[RiskVector, ...]:
    """Generators when the full query sequence is chosen before outcomes."""

    current = upper_minimal_generators(terminal_generators(problem))
    for query in reversed(tuple(sequence)):
        if query.target_count != problem.target_count:
            raise ValueError("query and problem target counts differ")
        current = query_step_generators(query, current)
    return current


def nonadaptive_upper_generators(
    queries: Sequence[QueryChannel],
    problem: DecisionProblem,
    horizon: int,
) -> tuple[RiskVector, ...]:
    """Generators for randomized open-loop sequences of at most ``horizon``."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    queries = tuple(queries)
    generated = list(terminal_generators(problem))
    for length in range(1, horizon + 1):
        for sequence in product(queries, repeat=length):
            generated.extend(
                fixed_sequence_upper_generators(sequence, problem)
            )
    return upper_minimal_generators(generated)


@dataclass(frozen=True)
class DeficiencyCertificate:
    epsilon: Q
    reference_vector: RiskVector
    source_risk: RiskVector
    source_weights: tuple[Q, ...]

    def jsonable(self) -> dict:
        return {
            "epsilon": qstr(self.epsilon),
            "reference_vector": [qstr(value) for value in self.reference_vector],
            "source_risk": [qstr(value) for value in self.source_risk],
            "source_weights": [qstr(value) for value in self.source_weights],
        }


def directed_upper_deficiency(
    source: Sequence[RiskVector],
    reference: Sequence[RiskVector],
) -> DeficiencyCertificate:
    """Exact directed containment radius between two generated upper hulls."""

    source = upper_minimal_generators(source)
    reference = upper_minimal_generators(reference)
    target_count = len(source[0])
    if any(len(vector) != target_count for vector in reference):
        raise ValueError("source and reference target counts differ")
    source_count = len(source)
    best: DeficiencyCertificate | None = None
    for reference_vector in reference:
        inequalities = []
        rhs = []
        for target in range(target_count):
            inequalities.append(
                tuple(vector[target] for vector in source) + (Q(-1),)
            )
            rhs.append(reference_vector[target])
        equalities = (tuple([Q(1)] * source_count + [Q(0)]),)
        solution = _exact_linprog(
            objective=tuple([Q(0)] * source_count + [Q(1)]),
            inequalities=tuple(inequalities),
            inequality_rhs=tuple(rhs),
            equalities=equalities,
            equality_rhs=(Q(1),),
        )
        weights = solution.variables[:-1]
        source_risk = tuple(
            sum(
                (
                    weights[index] * source[index][target]
                    for index in range(source_count)
                ),
                Q(0),
            )
            for target in range(target_count)
        )
        certificate = DeficiencyCertificate(
            epsilon=solution.value,
            reference_vector=reference_vector,
            source_risk=source_risk,
            source_weights=weights,
        )
        if best is None or certificate.epsilon > best.epsilon:
            best = certificate
    if best is None:
        raise RuntimeError("no reference risk vector was checked")
    return best


def zero_risk_available(generators: Sequence[RiskVector]) -> bool:
    generators = upper_minimal_generators(generators)
    return tuple([Q(0)] * len(generators[0])) in generators


ADAPTIVITY_GAP_QUERIES = (
    deterministic_binary_query("root", (0, 0, 1, 1)),
    deterministic_binary_query("left", (0, 1, 0, 0)),
    deterministic_binary_query("right", (0, 0, 0, 1)),
)


def burned_adaptivity_gap() -> dict:
    problem = classification_problem(4)
    adaptive_h2 = adaptive_upper_generators(
        ADAPTIVITY_GAP_QUERIES, problem, 2
    )
    open_h2 = nonadaptive_upper_generators(
        ADAPTIVITY_GAP_QUERIES, problem, 2
    )
    open_h3 = nonadaptive_upper_generators(
        ADAPTIVITY_GAP_QUERIES, problem, 3
    )
    full = ((Q(0), Q(0), Q(0), Q(0)),)
    result = {
        "phase": "burned_development",
        "fixture": "four_target_branching_identification",
        "frozen_development_prediction": {
            "adaptive_h2_deficiency": "0",
            "nonadaptive_h2_deficiency": "1/2",
            "nonadaptive_h3_deficiency": "0",
        },
        "query_signatures": {
            query.name: [
                int(query.rows[target][1])
                for target in range(query.target_count)
            ]
            for query in ADAPTIVITY_GAP_QUERIES
        },
        "adaptive_h2": {
            "upper_generators": len(adaptive_h2),
            "zero_risk": zero_risk_available(adaptive_h2),
            "deficiency_to_full": directed_upper_deficiency(
                adaptive_h2, full
            ).jsonable(),
        },
        "nonadaptive_h2": {
            "upper_generators": len(open_h2),
            "zero_risk": zero_risk_available(open_h2),
            "deficiency_to_full": directed_upper_deficiency(
                open_h2, full
            ).jsonable(),
        },
        "nonadaptive_h3": {
            "upper_generators": len(open_h3),
            "zero_risk": zero_risk_available(open_h3),
            "deficiency_to_full": directed_upper_deficiency(
                open_h3, full
            ).jsonable(),
        },
        "witness_policy": {
            "step_1": "root",
            "if_0": "left",
            "if_1": "right",
            "worst_case_queries": 2,
        },
    }
    result["prediction_match"] = {
        "adaptive_h2": (
            result["adaptive_h2"]["deficiency_to_full"]["epsilon"] == "0"
        ),
        "nonadaptive_h2": (
            result["nonadaptive_h2"]["deficiency_to_full"]["epsilon"]
            == "1/2"
        ),
        "nonadaptive_h3": (
            result["nonadaptive_h3"]["deficiency_to_full"]["epsilon"] == "0"
        ),
    }
    return result
