"""Exact fast seeded-cell checks for ASMP-9 context gluing v0.11.2."""

from __future__ import annotations

import random
from collections import Counter
from fractions import Fraction
from typing import Any, Iterable, Sequence

from context_gluing import (
    ContextGraph,
    Vector,
    component_count,
    cycle_circulations,
    fundamental_cycle_basis,
    global_flow,
    labelled_edges,
    local_cycle_basis,
    local_incidence_matrix,
)
from experiment import random_contexts


def support_bits(vector: Sequence[object]) -> int:
    result = 0
    for index, value in enumerate(vector):
        if Fraction(value) != 0:
            result |= 1 << index
    return result


def gf2_rank(rows: Iterable[int]) -> int:
    pivots: dict[int, int] = {}
    for source in rows:
        row = int(source)
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def incidence_bits(
    item_count: int, contexts: Sequence[ContextGraph], local: bool
) -> tuple[int, ...]:
    rows = []
    for context_index, edge in labelled_edges(contexts):
        left, right = edge
        offset = context_index * item_count if local else 0
        rows.append((1 << (offset + left)) | (1 << (offset + right)))
    return tuple(rows)


def fast_dimensions(
    item_count: int, contexts: Sequence[ContextGraph]
) -> dict[str, int]:
    union_edges = tuple(edge for _, edge in labelled_edges(contexts))
    local_rank = gf2_rank(incidence_bits(item_count, contexts, local=True))
    global_rank = gf2_rank(
        incidence_bits(item_count, contexts, local=False)
    )
    local_cycle_rank = sum(
        len(context.edges)
        - item_count
        + component_count(item_count, context.edges)
        for context in contexts
    )
    union_cycle_rank = (
        len(union_edges)
        - item_count
        + component_count(item_count, union_edges)
    )
    return {
        "local_rank": local_rank,
        "global_rank": global_rank,
        "rank_difference": local_rank - global_rank,
        "local_cycle_rank": local_cycle_rank,
        "union_cycle_rank": union_cycle_rank,
        "mixed_cycle_rank": union_cycle_rank - local_cycle_rank,
    }


class IncrementalGF2Basis:
    def __init__(self) -> None:
        self.pivots: dict[int, int] = {}

    def add(self, source: int) -> bool:
        row = int(source)
        while row:
            pivot = row.bit_length() - 1
            if pivot in self.pivots:
                row ^= self.pivots[pivot]
            else:
                self.pivots[pivot] = row
                return True
        return False

    @property
    def rank(self) -> int:
        return len(self.pivots)


def mixed_cycle_basis_fast(
    item_count: int, contexts: Sequence[ContextGraph]
) -> tuple[Vector, ...]:
    union_edges = tuple(edge for _, edge in labelled_edges(contexts))
    basis = IncrementalGF2Basis()
    for cycle in local_cycle_basis(item_count, contexts):
        if not basis.add(support_bits(cycle)):
            raise AssertionError("local cycle basis is dependent over GF(2)")
    mixed = []
    for cycle in fundamental_cycle_basis(item_count, union_edges):
        if basis.add(support_bits(cycle)):
            mixed.append(cycle)
    expected = fast_dimensions(item_count, contexts)["mixed_cycle_rank"]
    if len(mixed) != expected:
        raise AssertionError("fast mixed basis has wrong dimension")
    return tuple(mixed)


def fast_non_gluing_witness(
    item_count: int,
    contexts: Sequence[ContextGraph],
    mixed_cycles: Sequence[Vector],
) -> Vector | None:
    if not mixed_cycles:
        return None
    matrix = local_incidence_matrix(item_count, contexts)
    width = len(matrix[0]) if matrix else 0
    for column in range(width):
        candidate = tuple(row[column] for row in matrix)
        if any(
            value != 0
            for value in cycle_circulations(candidate, mixed_cycles)
        ):
            return candidate
    raise AssertionError("live quotient lacks a local nongluing witness")


def run_random_cells_fast(spec: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(int(spec["seed"]))
    count = int(spec["count"])
    status_counts: Counter[str] = Counter()
    item_distribution: Counter[int] = Counter()
    context_distribution: Counter[int] = Counter()
    rank_mismatch_count = 0
    basis_mismatch_count = 0
    sharpness_mismatch_count = 0
    witness_mismatch_count = 0
    shared_control_mismatch_count = 0
    exact_decision_mismatch_count = 0
    local_failure_control_count = 0
    local_failure_mismatch_count = 0
    for _ in range(count):
        item_count = rng.randint(
            int(spec["minimum_items"]), int(spec["maximum_items"])
        )
        context_count = rng.randint(
            int(spec["minimum_contexts"]), int(spec["maximum_contexts"])
        )
        contexts = random_contexts(item_count, context_count, rng)
        dimensions = fast_dimensions(item_count, contexts)
        mixed_rank = dimensions["mixed_cycle_rank"]
        rank_mismatch_count += int(
            dimensions["rank_difference"] != mixed_rank
        )
        cycles = mixed_cycle_basis_fast(item_count, contexts)
        basis_mismatch_count += int(len(cycles) != mixed_rank)
        for retained in range(mixed_rank + 1):
            sharpness_mismatch_count += int(
                gf2_rank(support_bits(cycle) for cycle in cycles[:retained])
                != retained
            )

        utility = tuple(
            Fraction(rng.randint(-11, 11)) for _ in range(item_count)
        )
        shared = global_flow(item_count, contexts, utility)
        shared_circulations = cycle_circulations(shared, cycles)
        expected_shared_status = (
            "shared_scalar_forced_by_design"
            if mixed_rank == 0
            else "shared_scalar_verified"
        )
        observed_shared_status = (
            "shared_scalar_forced_by_design"
            if not cycles
            else (
                "shared_scalar_refuted"
                if any(value != 0 for value in shared_circulations)
                else "shared_scalar_verified"
            )
        )
        shared_control_mismatch_count += int(
            observed_shared_status != expected_shared_status
        )
        status_counts[observed_shared_status] += 1

        witness = fast_non_gluing_witness(
            item_count, contexts, cycles
        )
        witness_mismatch_count += int(
            (witness is not None) != (mixed_rank > 0)
        )
        if witness is not None:
            witness_circulations = cycle_circulations(witness, cycles)
            witness_refuted = any(
                value != 0 for value in witness_circulations
            )
            exact_decision_mismatch_count += int(not witness_refuted)
            status_counts[
                (
                    "shared_scalar_refuted"
                    if witness_refuted
                    else "shared_scalar_verified"
                )
            ] += 1

        for context_index, context in enumerate(contexts):
            local_cycles = fundamental_cycle_basis(
                item_count, context.edges
            )
            if not local_cycles:
                continue
            inconsistent = list(shared)
            offset = sum(
                len(previous.edges)
                for previous in contexts[:context_index]
            )
            changed_edge = next(
                index
                for index, coefficient in enumerate(local_cycles[0])
                if coefficient != 0
            )
            inconsistent[offset + changed_edge] += Fraction(1)
            local_flow_slice = inconsistent[
                offset : offset + len(context.edges)
            ]
            local_failed = any(
                value != 0
                for value in cycle_circulations(
                    local_flow_slice, local_cycles
                )
            )
            local_failure_control_count += 1
            local_failure_mismatch_count += int(not local_failed)
            status_counts[
                "local_scalar_failed"
                if local_failed
                else "shared_scalar_verified"
            ] += 1
            break

        item_distribution[item_count] += 1
        context_distribution[context_count] += 1
    return {
        **spec,
        "implementation": (
            "exact GF(2) incidence rank with signed rational circulations"
        ),
        "actual_count": count,
        "item_distribution": dict(sorted(item_distribution.items())),
        "context_distribution": dict(
            sorted(context_distribution.items())
        ),
        "status_counts": dict(sorted(status_counts.items())),
        "rank_formula_mismatch_count": rank_mismatch_count,
        "basis_dimension_mismatch_count": basis_mismatch_count,
        "sharpness_mismatch_count": sharpness_mismatch_count,
        "witness_existence_mismatch_count": witness_mismatch_count,
        "shared_control_mismatch_count": shared_control_mismatch_count,
        "exact_decision_mismatch_count": exact_decision_mismatch_count,
        "local_failure_control_count": local_failure_control_count,
        "local_failure_mismatch_count": local_failure_mismatch_count,
    }
