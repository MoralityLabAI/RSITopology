from __future__ import annotations

import numpy as np

from rsi_topology.qwen_precision_filtration_w1 import (
    _edge_specs,
    cycle_space,
    gauge_preflight,
    measure_graph,
)


def _flat_bases() -> dict:
    vector = np.asarray([1.0, 0.0, 0.0])
    return {
        (state, f"shard-{column:02d}"): {
            "construction": vector.copy(),
            "geometry_validation": vector.copy(),
        }
        for state in ("base", "naive_qlora")
        for column in range(4)
    }


def test_cycle_space_is_complete_and_honest_about_simple_cycles() -> None:
    cycles = cycle_space()
    assert len(cycles) == 7
    assert sorted(row["edge_count"] for row in cycles) == [4, 4, 4, 6, 6, 8, 8]
    assert sum(row["connected_simple_loop"] for row in cycles) == 6
    assert max(row["edge_count"] for row in cycles if row["connected_simple_loop"]) == 8
    assert len(_edge_specs()) == 10


def test_flat_rank_one_ladder_percolates_and_is_orientable() -> None:
    graph = measure_graph(_flat_bases())
    assert graph.tau_conn == 1.0
    assert graph.tau_cycle == 1.0
    assert graph.tau_loop == 1.0
    assert all(row["geometry_validation_sign"] == 1 for row in graph.cycles)
    assert all(row["canonical_angles_degrees"] is None for row in graph.cycles)


def test_cycle_signs_are_gauge_invariant() -> None:
    bases = _flat_bases()
    rng = np.random.default_rng(81)
    for value in bases.values():
        for half in tuple(value):
            value[half] *= rng.choice((-1.0, 1.0))
    graph = measure_graph(bases)
    receipt = gauge_preflight(graph, reframings=128, seed=77)
    assert receipt["passed"] is True
    assert receipt["determinant_decision_mismatches"] == 0
    assert receipt["cycle_decisions_checked"] == 128 * 7


def test_weak_context_edge_moves_connectivity_threshold() -> None:
    bases = _flat_bases()
    # Rotate the final base-context node so its only context edge is weak;
    # the matched state edge still supplies an alternate route.
    angle = np.arccos(np.sqrt(0.4))
    bases[("base", "shard-03")]["construction"] = np.asarray(
        [np.cos(angle), np.sin(angle), 0.0]
    )
    bases[("base", "shard-03")]["geometry_validation"] = np.asarray(
        [np.cos(angle), np.sin(angle), 0.0]
    )
    graph = measure_graph(bases)
    assert graph.tau_conn >= 0.4 - 1e-12
    assert graph.tau_cycle >= 0.4 - 1e-12
    assert any(abs(row["tau"] - 0.4) < 1e-12 for row in graph.filtration)
