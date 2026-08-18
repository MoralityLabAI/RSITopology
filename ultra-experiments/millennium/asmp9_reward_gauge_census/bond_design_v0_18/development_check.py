from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

from bond_design import (
    all_simple_graphs,
    cactus_closed_form,
    cyclic_core_bonds,
)


HERE = Path(__file__).resolve().parent
V017 = HERE.parent / "general_graph_design_v0_17" / "general_graph.py"


def _load_v017() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "asmp9_v017_general_graph", V017
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load v0.17 comparison module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _connected(node_count: int, edges: tuple[tuple[int, int], ...]) -> bool:
    adjacency = [[] for _ in range(node_count)]
    for source, target in edges:
        adjacency[source].append(target)
        adjacency[target].append(source)
    seen = {0}
    stack = [0]
    while stack:
        node = stack.pop()
        for neighbor in adjacency[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == node_count


def run() -> dict[str, Any]:
    v017 = _load_v017()
    checked = 0
    mismatches: list[dict[str, object]] = []
    order_counts: dict[str, int] = {}
    for node_count in (2, 3, 4):
        count = 0
        for edges in all_simple_graphs(node_count):
            if not _connected(node_count, edges):
                continue
            if v017.graph_cycle_rank(node_count, edges) == 0:
                continue
            expected = v017.minimal_bad_boundary_supports(
                node_count, edges
            )
            actual = cyclic_core_bonds(node_count, edges)
            checked += 1
            count += 1
            if actual != expected:
                mismatches.append(
                    {
                        "node_count": node_count,
                        "edges": edges,
                        "v017": expected,
                        "bonds": actual,
                    }
                )
        order_counts[str(node_count)] = count

    triangle_square_bridge = (
        (0, 1),
        (1, 2),
        (2, 0),
        (3, 4),
        (4, 5),
        (5, 6),
        (6, 3),
        (2, 3),
    )
    cactus = cactus_closed_form(7, triangle_square_bridge)
    cactus_bonds = cyclic_core_bonds(7, triangle_square_bridge)
    expected_cactus_bonds = tuple(
        sorted(
            tuple(pair)
            for cycle in cactus["cycles"]
            for pair in __import__("itertools").combinations(cycle, 2)
        )
    )

    return {
        "status": "pass" if not mismatches else "fail",
        "development_only": True,
        "orders": order_counts,
        "graph_count": checked,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "cactus_control": {
            "threshold": str(cactus["threshold"]),
            "weights": [str(value) for value in cactus["weights"]],
            "cycles": cactus["cycles"],
            "bonds_match_cycle_pairs": (
                set(cactus_bonds) == set(expected_cactus_bonds)
            ),
            "bridge_weight_zero": cactus["weights"][-1] == 0,
        },
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
