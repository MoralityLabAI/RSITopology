"""Exact finite risk-polytope access compiler for ASMP-9 v0.40."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import sys
from typing import Iterable, Mapping, Sequence


V38 = Path(__file__).resolve().parents[1] / "decision_relative_access_v0_38"
if str(V38) not in sys.path:
    sys.path.append(str(V38))

from relative_deficiency import (  # noqa: E402
    DecisionProblem,
    FiniteExperiment,
    independent_binary_product,
    relative_deficiency,
)


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def constant_experiment(target_count: int) -> FiniteExperiment:
    if target_count < 2:
        raise ValueError("at least two targets are required")
    return FiniteExperiment(tuple((Q(1),) for _ in range(target_count)))


def drop_zero_columns(experiment: FiniteExperiment) -> FiniteExperiment:
    keep = tuple(
        column
        for column in range(experiment.observation_count)
        if any(
            experiment.rows[target][column] != 0
            for target in range(experiment.target_count)
        )
    )
    if not keep:
        raise ValueError("an experiment cannot lose every observation column")
    return FiniteExperiment(
        tuple(
            tuple(row[column] for column in keep)
            for row in experiment.rows
        )
    )


def subset_experiment(
    queries: Mapping[str, Sequence[Q]],
    subset: Sequence[str],
) -> FiniteExperiment:
    names = tuple(subset)
    if not queries:
        raise ValueError("the query registry cannot be empty")
    target_count = len(next(iter(queries.values())))
    if any(len(row) != target_count for row in queries.values()):
        raise ValueError("query target counts differ")
    unknown = set(names).difference(queries)
    if unknown:
        raise ValueError(f"unknown queries: {sorted(unknown)}")
    if not names:
        return constant_experiment(target_count)
    return drop_zero_columns(
        independent_binary_product(
            tuple(tuple(map(q, queries[name])) for name in names)
        )
    )


def all_subsets(names: Sequence[str]) -> Iterable[tuple[str, ...]]:
    frozen = tuple(names)
    for size in range(len(frozen) + 1):
        yield from combinations(frozen, size)


@dataclass(frozen=True)
class AccessRow:
    subset: tuple[str, ...]
    epsilon: Q
    source_observations: int
    worst_problem: str
    witness_reference_rule: tuple[int, ...]

    def jsonable(self) -> dict:
        return {
            "subset": list(self.subset),
            "subset_size": len(self.subset),
            "epsilon": qstr(self.epsilon),
            "source_observations": self.source_observations,
            "worst_problem": self.worst_problem,
            "witness_reference_rule": list(self.witness_reference_rule),
        }


def compile_access_table(
    queries: Mapping[str, Sequence[Q]],
    problems: Sequence[DecisionProblem],
) -> tuple[AccessRow, ...]:
    if not problems:
        raise ValueError("at least one decision problem is required")
    names = tuple(queries)
    reference = subset_experiment(queries, names)
    rows = []
    for subset in all_subsets(names):
        source = subset_experiment(queries, subset)
        certificate = relative_deficiency(source, reference, problems)
        rows.append(
            AccessRow(
                subset=subset,
                epsilon=certificate.epsilon,
                source_observations=source.observation_count,
                worst_problem=certificate.problem,
                witness_reference_rule=certificate.reference_rule,
            )
        )
    return tuple(rows)


def minimal_access_sets(
    rows: Sequence[AccessRow], tolerance: Q
) -> tuple[tuple[str, ...], ...]:
    tolerance = q(tolerance)
    feasible = {
        row.subset for row in rows if row.epsilon <= tolerance
    }
    minimal = [
        subset
        for subset in feasible
        if not any(
            other != subset and set(other).issubset(subset)
            for other in feasible
        )
    ]
    return tuple(sorted(minimal, key=lambda item: (len(item), item)))


def persistence_curve(rows: Sequence[AccessRow]) -> tuple[dict, ...]:
    critical = sorted({row.epsilon for row in rows})
    return tuple(
        {
            "tolerance": qstr(tolerance),
            "minimal_access_sets": [
                list(subset)
                for subset in minimal_access_sets(rows, tolerance)
            ],
        }
        for tolerance in critical
    )


def deterministic_signatures(
    queries: Mapping[str, Sequence[Q]], subset: Sequence[str]
) -> tuple[tuple[int, ...], ...]:
    names = tuple(subset)
    target_count = len(next(iter(queries.values())))
    signatures = []
    for target in range(target_count):
        signature = []
        for name in names:
            value = q(queries[name][target])
            if value not in (Q(0), Q(1)):
                raise ValueError("test-cover signatures require deterministic queries")
            signature.append(int(value))
        signatures.append(tuple(signature))
    return tuple(signatures)


def is_test_cover(
    queries: Mapping[str, Sequence[Q]], subset: Sequence[str]
) -> bool:
    signatures = deterministic_signatures(queries, subset)
    return len(set(signatures)) == len(signatures)


def deterministic_partition(
    queries: Mapping[str, Sequence[Q]], subset: Sequence[str]
) -> tuple[tuple[int, ...], ...]:
    signatures = deterministic_signatures(queries, subset)
    blocks: dict[tuple[int, ...], list[int]] = {}
    for target, signature in enumerate(signatures):
        blocks.setdefault(signature, []).append(target)
    return tuple(
        tuple(blocks[signature])
        for signature in sorted(blocks)
    )


def classification_partition_deficiency(
    queries: Mapping[str, Sequence[Q]], subset: Sequence[str]
) -> Q:
    """Exact deficiency against full revelation for zero-one classification."""

    max_block = max(len(block) for block in deterministic_partition(queries, subset))
    return Q(max_block - 1, max_block)


def binary_group_partition_deficiency(
    queries: Mapping[str, Sequence[Q]],
    subset: Sequence[str],
    labels: Sequence[int],
    false_positive_cost: Q,
    false_negative_cost: Q = Q(1),
) -> Q:
    """Exact full-reference deficiency for one asymmetric binary group loss."""

    labels = tuple(labels)
    if len(labels) != len(next(iter(queries.values()))):
        raise ValueError("one label is required per target")
    false_positive_cost = q(false_positive_cost)
    false_negative_cost = q(false_negative_cost)
    for block in deterministic_partition(queries, subset):
        if len({labels[target] for target in block}) > 1:
            return (
                false_positive_cost
                * false_negative_cost
                / (false_positive_cost + false_negative_cost)
            )
    return Q(0)


def classification_problem(target_count: int = 3) -> DecisionProblem:
    return DecisionProblem(
        (
            "three_class_identification"
            if target_count == 3
            else f"{target_count}_class_identification"
        ),
        tuple(
            tuple(Q(int(target != action)) for action in range(target_count))
            for target in range(target_count)
        ),
    )


def group_problem(
    name: str,
    labels: Sequence[int],
    false_positive_cost: Q,
    false_negative_cost: Q = Q(1),
) -> DecisionProblem:
    labels = tuple(labels)
    if set(labels) != {0, 1}:
        raise ValueError("the frozen group loss needs both binary labels")
    false_positive_cost = q(false_positive_cost)
    false_negative_cost = q(false_negative_cost)
    return DecisionProblem(
        name,
        tuple(
            (
                Q(0) if label == 0 else false_negative_cost,
                false_positive_cost if label == 0 else Q(0),
            )
            for label in labels
        ),
    )


DEVELOPMENT_QUERIES = {
    "q0": (Q(0), Q(0), Q(1)),
    "q1": (Q(0), Q(1), Q(0)),
    "q2": (Q(0), Q(1), Q(1)),
    "q_const": (Q(1), Q(1), Q(1)),
}


def development_problems() -> dict[str, tuple[DecisionProblem, ...]]:
    q0_group = group_problem(
        "q0_asymmetric_group",
        (0, 0, 1),
        false_positive_cost=Q(1, 3),
    )
    q1_group = group_problem(
        "q1_asymmetric_group",
        (0, 1, 0),
        false_positive_cost=Q(2, 5),
    )
    return {
        "classification": (classification_problem(),),
        "q0_asymmetric": (q0_group,),
        "q1_asymmetric": (q1_group,),
        "combined_groups": (q0_group, q1_group),
    }


def run_burned_development() -> dict:
    results = {}
    for name, problems in development_problems().items():
        rows = compile_access_table(DEVELOPMENT_QUERIES, problems)
        results[name] = {
            "rows": [row.jsonable() for row in rows],
            "persistence_curve": list(persistence_curve(rows)),
        }
    return {
        "phase": "burned_development",
        "queries": {
            name: [qstr(value) for value in row]
            for name, row in DEVELOPMENT_QUERIES.items()
        },
        "decision_types": results,
    }
