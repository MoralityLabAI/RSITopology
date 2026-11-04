"""Resource repair for the unchanged ASMP-9 v0.11 scientific census."""

from __future__ import annotations

from collections import Counter
from itertools import product
from typing import Any

from context_gluing import component_count, incidence_matrix, matrix_rank
from experiment import (
    edge_universe,
    graph_from_mask,
    run_minimality_controls,
    run_random_cells,
)


def run_tuple_census_optimized(spec: dict[str, Any]) -> dict[str, Any]:
    """Exact census with graph-level rank/component precomputation."""
    item_count = int(spec["item_count"])
    context_count = int(spec["context_count"])
    graph_count = 1 << len(edge_universe(item_count))
    expected = graph_count**context_count
    if expected > int(spec["maximum_tuple_count"]):
        raise ValueError("tuple census exceeds frozen maximum")

    ranks: list[int] = []
    components: list[int] = []
    edge_counts: list[int] = []
    cycle_ranks: list[int] = []
    for mask in range(graph_count):
        edges = graph_from_mask(item_count, mask)
        rank = matrix_rank(incidence_matrix(item_count, edges))
        count = component_count(item_count, edges)
        ranks.append(rank)
        components.append(count)
        edge_counts.append(len(edges))
        cycle_ranks.append(len(edges) - item_count + count)

    mixed_distribution: Counter[int] = Counter()
    mismatch_count = 0
    liveness_count = 0
    total = 0
    for masks in product(range(graph_count), repeat=context_count):
        union_mask = 0
        labelled_edge_count = 0
        local_cycle_rank = 0
        local_rank = 0
        for mask in masks:
            union_mask |= mask
            labelled_edge_count += edge_counts[mask]
            local_cycle_rank += cycle_ranks[mask]
            local_rank += ranks[mask]
        global_rank = ranks[union_mask]
        rank_difference = local_rank - global_rank
        union_cycle_rank = labelled_edge_count - item_count + components[union_mask]
        mixed_cycle_rank = union_cycle_rank - local_cycle_rank
        mismatch_count += int(rank_difference != mixed_cycle_rank)
        mixed_distribution[mixed_cycle_rank] += 1
        liveness_count += int(mixed_cycle_rank > 0)
        total += 1

    return {
        **spec,
        "implementation": "precomputed exact graph ranks and components",
        "precomputed_graph_count": graph_count,
        "graph_count_per_context": graph_count,
        "tuple_count": total,
        "mixed_cycle_rank_distribution": dict(sorted(mixed_distribution.items())),
        "live_tuple_count": liveness_count,
        "forced_by_design_tuple_count": total - liveness_count,
        "rank_formula_mismatch_count": mismatch_count,
    }


__all__ = [
    "run_minimality_controls",
    "run_random_cells",
    "run_tuple_census_optimized",
]
