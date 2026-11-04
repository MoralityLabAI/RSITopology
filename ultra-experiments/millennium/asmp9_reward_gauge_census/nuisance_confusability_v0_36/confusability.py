"""Exact finite nuisance-confusability constructions."""

from __future__ import annotations

from itertools import product
from typing import Iterable, Sequence


Observation = tuple[int, ...]
Table = tuple[int, ...]
Relation = tuple[tuple[bool, ...], ...]


def table_value(
    table: Table,
    theta: int,
    nuisance: int,
    nuisance_count: int,
) -> int:
    return table[theta * nuisance_count + nuisance]


def all_tables(
    theta_count: int,
    nuisance_count: int,
    alphabet_count: int,
) -> Iterable[Table]:
    if min(theta_count, nuisance_count, alphabet_count) <= 0:
        raise ValueError("all cardinalities must be positive")
    return product(
        range(alphabet_count),
        repeat=theta_count * nuisance_count,
    )


def shared_signature(
    tables: Sequence[Table],
    theta: int,
    nuisance_count: int,
) -> frozenset[Observation]:
    if not tables:
        raise ValueError("at least one query table is required")
    return frozenset(
        tuple(
            table_value(table, theta, nuisance, nuisance_count)
            for table in tables
        )
        for nuisance in range(nuisance_count)
    )


def reset_signature(
    tables: Sequence[Table],
    theta: int,
    nuisance_count: int,
) -> frozenset[Observation]:
    if not tables:
        raise ValueError("at least one query table is required")
    per_query = [
        {
            table_value(table, theta, nuisance, nuisance_count)
            for nuisance in range(nuisance_count)
        }
        for table in tables
    ]
    return frozenset(product(*per_query))


def signatures(
    tables: Sequence[Table],
    theta_count: int,
    nuisance_count: int,
    *,
    nuisance_mode: str,
) -> tuple[frozenset[Observation], ...]:
    if nuisance_mode == "shared":
        builder = shared_signature
    elif nuisance_mode == "reset":
        builder = reset_signature
    else:
        raise ValueError("nuisance_mode must be shared or reset")
    return tuple(
        builder(tables, theta, nuisance_count)
        for theta in range(theta_count)
    )


def confusability_relation(
    observation_sets: Sequence[frozenset[Observation]],
) -> Relation:
    return tuple(
        tuple(bool(left & right) for right in observation_sets)
        for left in observation_sets
    )


def set_equality_relation(
    observation_sets: Sequence[frozenset[Observation]],
) -> Relation:
    return tuple(
        tuple(left == right for right in observation_sets)
        for left in observation_sets
    )


def is_reflexive(relation: Relation) -> bool:
    return all(relation[index][index] for index in range(len(relation)))


def is_symmetric(relation: Relation) -> bool:
    return all(
        relation[i][j] == relation[j][i]
        for i in range(len(relation))
        for j in range(len(relation))
    )


def is_transitive(relation: Relation) -> bool:
    return all(
        not (relation[i][j] and relation[j][k]) or relation[i][k]
        for i in range(len(relation))
        for j in range(len(relation))
        for k in range(len(relation))
    )


def is_equivalence_relation(relation: Relation) -> bool:
    return (
        is_reflexive(relation)
        and is_symmetric(relation)
        and is_transitive(relation)
    )


def decision_identifiable(
    relation: Relation,
    decisions: Sequence[int],
) -> bool:
    if len(relation) != len(decisions):
        raise ValueError("decision count does not match relation")
    return all(
        decisions[i] == decisions[j] or not relation[i][j]
        for i in range(len(decisions))
        for j in range(i + 1, len(decisions))
    )


def decoder_exists(
    observation_sets: Sequence[frozenset[Observation]],
    decisions: Sequence[int],
) -> bool:
    """Direct transcript-fiber check, independent of graph construction."""

    transcript_decisions: dict[Observation, set[int]] = {}
    for theta, observations in enumerate(observation_sets):
        for observation in observations:
            transcript_decisions.setdefault(observation, set()).add(
                decisions[theta]
            )
    return all(len(values) == 1 for values in transcript_decisions.values())


def relation_subset(left: Relation, right: Relation) -> bool:
    if len(left) != len(right):
        raise ValueError("relation sizes differ")
    return all(
        not left[i][j] or right[i][j]
        for i in range(len(left))
        for j in range(len(left))
    )


def relation_edge_bits(relation: Relation) -> str:
    return "".join(
        "1" if relation[i][j] else "0"
        for i in range(len(relation))
        for j in range(i + 1, len(relation))
    )


def mirrored_threshold_tables() -> tuple[Table, Table]:
    """Return q0=1{theta>=h}, q1=1{theta>=3-h}; h is 1 or 2."""

    q0 = tuple(
        int(theta >= threshold)
        for theta in range(3)
        for threshold in (1, 2)
    )
    q1 = tuple(
        int(theta >= 3 - threshold)
        for theta in range(3)
        for threshold in (1, 2)
    )
    return q0, q1
