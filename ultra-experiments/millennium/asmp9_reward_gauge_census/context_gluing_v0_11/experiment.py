"""Census helpers for the ASMP-9 v0.11 context-gluing theorem."""

from __future__ import annotations

import random
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from typing import Any

from context_gluing import (
    ContextGraph,
    global_flow,
    has_shared_scalar,
    is_locally_scalar,
    fundamental_cycle_basis,
    mixed_cycle_basis,
    non_gluing_witness,
    obstruction_dimensions,
    shared_scalar_status,
)


def edge_universe(item_count: int) -> tuple[tuple[int, int], ...]:
    return tuple(combinations(range(item_count), 2))


def graph_from_mask(item_count: int, mask: int) -> tuple[tuple[int, int], ...]:
    universe = edge_universe(item_count)
    if not 0 <= mask < 1 << len(universe):
        raise ValueError("graph mask outside registered universe")
    return tuple(edge for index, edge in enumerate(universe) if mask & (1 << index))


def contexts_from_masks(
    item_count: int, masks: tuple[int, ...]
) -> tuple[ContextGraph, ...]:
    return tuple(
        ContextGraph(f"context_{index}", graph_from_mask(item_count, mask))
        for index, mask in enumerate(masks)
    )


def run_tuple_census(spec: dict[str, Any]) -> dict[str, Any]:
    item_count = int(spec["item_count"])
    context_count = int(spec["context_count"])
    graph_count = 1 << len(edge_universe(item_count))
    expected = graph_count**context_count
    if expected > int(spec["maximum_tuple_count"]):
        raise ValueError("tuple census exceeds frozen maximum")
    mixed_distribution: Counter[int] = Counter()
    mismatch_count = 0
    liveness_count = 0
    total = 0
    for masks in product(range(graph_count), repeat=context_count):
        contexts = contexts_from_masks(item_count, tuple(masks))
        dimensions = obstruction_dimensions(item_count, contexts)
        mismatch_count += int(
            dimensions["rank_difference"] != dimensions["mixed_cycle_rank"]
        )
        mixed = dimensions["mixed_cycle_rank"]
        mixed_distribution[mixed] += 1
        liveness_count += int(mixed > 0)
        total += 1
    return {
        **spec,
        "graph_count_per_context": graph_count,
        "tuple_count": total,
        "mixed_cycle_rank_distribution": dict(sorted(mixed_distribution.items())),
        "live_tuple_count": liveness_count,
        "forced_by_design_tuple_count": total - liveness_count,
        "rank_formula_mismatch_count": mismatch_count,
    }


def random_contexts(
    item_count: int,
    context_count: int,
    rng: random.Random,
) -> tuple[ContextGraph, ...]:
    universe = edge_universe(item_count)
    return tuple(
        ContextGraph(
            f"context_{context}",
            tuple(edge for edge in universe if rng.randrange(2)),
        )
        for context in range(context_count)
    )


def run_random_cells(spec: dict[str, Any]) -> dict[str, Any]:
    rng = random.Random(int(spec["seed"]))
    count = int(spec["count"])
    status_counts: Counter[str] = Counter()
    item_distribution: Counter[int] = Counter()
    context_distribution: Counter[int] = Counter()
    rank_mismatch_count = 0
    basis_mismatch_count = 0
    witness_mismatch_count = 0
    shared_control_mismatch_count = 0
    exact_decision_mismatch_count = 0
    local_failure_control_count = 0
    local_failure_mismatch_count = 0
    for _ in range(count):
        item_count = rng.randint(int(spec["minimum_items"]), int(spec["maximum_items"]))
        context_count = rng.randint(
            int(spec["minimum_contexts"]), int(spec["maximum_contexts"])
        )
        contexts = random_contexts(item_count, context_count, rng)
        dimensions = obstruction_dimensions(item_count, contexts)
        mixed_rank = dimensions["mixed_cycle_rank"]
        rank_mismatch_count += int(dimensions["rank_difference"] != mixed_rank)
        cycles = mixed_cycle_basis(item_count, contexts)
        basis_mismatch_count += int(len(cycles) != mixed_rank)

        utility = tuple(Fraction(rng.randint(-11, 11)) for _ in range(item_count))
        shared = global_flow(item_count, contexts, utility)
        shared_status = shared_scalar_status(item_count, contexts, shared)
        expected_shared_status = (
            "shared_scalar_forced_by_design"
            if mixed_rank == 0
            else "shared_scalar_verified"
        )
        shared_control_mismatch_count += int(
            shared_status["status"] != expected_shared_status
        )
        status_counts[shared_status["status"]] += 1

        witness = non_gluing_witness(item_count, contexts)
        witness_mismatch_count += int((witness is not None) != (mixed_rank > 0))
        if witness is not None:
            witness_status = shared_scalar_status(item_count, contexts, witness)
            exact_decision_mismatch_count += int(
                witness_status["status"] != "shared_scalar_refuted"
                or not is_locally_scalar(item_count, contexts, witness)
                or has_shared_scalar(item_count, contexts, witness)
            )
            status_counts[witness_status["status"]] += 1

        for context_index, context in enumerate(contexts):
            local_cycles = fundamental_cycle_basis(item_count, context.edges)
            if not local_cycles:
                continue
            inconsistent = list(shared)
            offset = sum(len(previous.edges) for previous in contexts[:context_index])
            changed_edge = next(
                index
                for index, coefficient in enumerate(local_cycles[0])
                if coefficient != 0
            )
            inconsistent[offset + changed_edge] += Fraction(1)
            local_failure_control_count += 1
            local_failure_mismatch_count += int(
                shared_scalar_status(item_count, contexts, inconsistent)["status"]
                != "local_scalar_failed"
            )
            break

        item_distribution[item_count] += 1
        context_distribution[context_count] += 1
    return {
        **spec,
        "actual_count": count,
        "item_distribution": dict(sorted(item_distribution.items())),
        "context_distribution": dict(sorted(context_distribution.items())),
        "status_counts": dict(sorted(status_counts.items())),
        "rank_formula_mismatch_count": rank_mismatch_count,
        "basis_dimension_mismatch_count": basis_mismatch_count,
        "witness_existence_mismatch_count": witness_mismatch_count,
        "shared_control_mismatch_count": shared_control_mismatch_count,
        "exact_decision_mismatch_count": exact_decision_mismatch_count,
        "local_failure_control_count": local_failure_control_count,
        "local_failure_mismatch_count": local_failure_mismatch_count,
    }
