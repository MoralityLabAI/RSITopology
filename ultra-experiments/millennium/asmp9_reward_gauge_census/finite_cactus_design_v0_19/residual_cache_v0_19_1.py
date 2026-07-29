"""Exact cached residual evaluator for the v0.19.1 amendment."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Sequence

from finite_cactus_design import (
    CactusGraph,
    _residual_full_liveness_validated,
    validate_cactus,
)


Status = tuple[str, ...]


def live_status_table(graph: CactusGraph) -> tuple[Status, ...]:
    """Compute graph liveness once for every ternary residual state."""

    validate_cactus(graph)
    return tuple(
        statuses
        for statuses in product(
            ("Z", "I", "F"), repeat=len(graph.edges)
        )
        if _residual_full_liveness_validated(graph, statuses)
    )


def integer_status_law(
    count: int, epsilon: Fraction, label: int
) -> tuple[dict[str, int], int]:
    """Return exact status numerators under one common denominator."""

    if count < 1:
        raise ValueError("counts must be positive")
    if not Fraction(0) < epsilon <= Fraction(1, 2):
        raise ValueError("epsilon must lie in (0,1/2]")
    if label not in (0, 1):
        raise ValueError("label must be zero or one")
    denominator_base = epsilon.denominator
    low_numerator = epsilon.numerator
    high_numerator = denominator_base - low_numerator
    p_numerator = low_numerator if label == 0 else high_numerator
    q_numerator = denominator_base - p_numerator
    denominator = denominator_base**count
    zero = q_numerator**count
    full = p_numerator**count
    interior = denominator - zero - full
    return {"Z": zero, "I": interior, "F": full}, denominator


def graph_availability_cached(
    graph: CactusGraph,
    live_statuses: Sequence[Status],
    counts: Sequence[int],
    epsilon: Fraction,
    labels: Sequence[int],
) -> Fraction:
    """Contract an exact integer status tensor over cached live states."""

    if len(counts) != len(graph.edges) or len(labels) != len(graph.edges):
        raise ValueError("counts and labels must cover every edge")
    laws = [
        integer_status_law(count, epsilon, label)
        for count, label in zip(counts, labels, strict=True)
    ]
    denominator = 1
    for _, edge_denominator in laws:
        denominator *= edge_denominator
    numerator = 0
    for statuses in live_statuses:
        term = 1
        for index, status in enumerate(statuses):
            term *= laws[index][0][status]
        numerator += term
    return Fraction(numerator, denominator)

