"""Reproduce the burned ASMP-9 v0.20 development census.

This is development evidence, not a prospectively registered experiment.
The graph cells and all parameter cells in this script are burned.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import platform
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Sequence

import networkx as nx

from block_factorization import (
    Edge,
    availability,
    biconnected_edge_blocks,
    block_product_availability,
)


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "artifacts_v0_20" / "development_census.json"

HAND_GRAPHS: dict[str, tuple[int, tuple[Edge, ...]]] = {
    "two_diamonds": (
        7,
        (
            (0, 1),
            (1, 2),
            (2, 0),
            (0, 3),
            (3, 2),
            (0, 4),
            (4, 5),
            (5, 0),
            (0, 6),
            (6, 5),
        ),
    ),
    "k4_plus_triangle": (
        6,
        (
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 2),
            (1, 3),
            (2, 3),
            (0, 4),
            (4, 5),
            (5, 0),
        ),
    ),
    "theta_plus_triangle": (
        7,
        (
            (0, 2),
            (2, 1),
            (0, 3),
            (3, 1),
            (0, 4),
            (4, 1),
            (0, 5),
            (5, 6),
            (6, 0),
        ),
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_edges(graph: nx.Graph) -> tuple[Edge, ...]:
    return tuple(
        sorted(
            (min(int(source), int(target)), max(int(source), int(target)))
            for source, target in graph.edges()
        )
    )


def networkx_blocks(edges: Sequence[Edge]) -> tuple[tuple[int, ...], ...]:
    graph = nx.Graph()
    graph.add_edges_from(edges)
    edge_lookup = {
        frozenset(edge): edge_id for edge_id, edge in enumerate(edges)
    }
    blocks = []
    for raw_block in nx.biconnected_component_edges(graph):
        blocks.append(
            tuple(
                sorted(
                    edge_lookup[frozenset((source, target))]
                    for source, target in raw_block
                )
            )
        )
    return tuple(sorted(blocks, key=lambda block: (min(block), block)))


def bridge_ids(edges: Sequence[Edge]) -> frozenset[int]:
    graph = nx.Graph()
    graph.add_edges_from(edges)
    edge_lookup = {
        frozenset(edge): edge_id for edge_id, edge in enumerate(edges)
    }
    return frozenset(
        edge_lookup[frozenset((source, target))]
        for source, target in nx.bridges(graph)
    )


def reachability(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[int],
    edge_ids: Sequence[int] | None = None,
) -> tuple[int, ...]:
    selected = (
        range(len(edges)) if edge_ids is None else edge_ids
    )
    reach = [1 << node for node in range(node_count)]
    for edge_id in selected:
        source, target = edges[edge_id]
        status = statuses[edge_id]
        if status in (0, 1):
            reach[source] |= 1 << target
        if status in (1, 2):
            reach[target] |= 1 << source
    for intermediate in range(node_count):
        flag = 1 << intermediate
        for source in range(node_count):
            if reach[source] & flag:
                reach[source] |= reach[intermediate]
    return tuple(reach)


def direct_oracle(
    node_count: int,
    edges: Sequence[Edge],
    bridges: frozenset[int],
    statuses: Sequence[int],
) -> bool:
    reach = reachability(node_count, edges, statuses)
    return all(
        edge_id in bridges
        or (
            reach[source] & (1 << target)
            and reach[target] & (1 << source)
        )
        for edge_id, (source, target) in enumerate(edges)
    )


def block_oracle(
    node_count: int,
    edges: Sequence[Edge],
    blocks: Sequence[Sequence[int]],
    statuses: Sequence[int],
) -> bool:
    for block in blocks:
        if len(block) == 1:
            continue
        vertices = {
            vertex for edge_id in block for vertex in edges[edge_id]
        }
        reach = reachability(node_count, edges, statuses, block)
        root = next(iter(vertices))
        if any(
            not (reach[root] & (1 << vertex))
            or not (reach[vertex] & (1 << root))
            for vertex in vertices
        ):
            return False
    return True


def census_graph(
    node_count: int, edges: tuple[Edge, ...]
) -> dict[str, object]:
    observed_blocks = biconnected_edge_blocks(node_count, edges)
    oracle_blocks = networkx_blocks(edges)
    bridges = bridge_ids(edges)
    mismatch_count = 0
    statuses_checked = 0
    for statuses in itertools.product(
        (0, 1, 2), repeat=len(edges)
    ):
        statuses_checked += 1
        if direct_oracle(
            node_count, edges, bridges, statuses
        ) != block_oracle(
            node_count, edges, oracle_blocks, statuses
        ):
            mismatch_count += 1
    return {
        "node_count": node_count,
        "edge_count": len(edges),
        "edge_blocks": [list(block) for block in observed_blocks],
        "networkx_edge_blocks": [
            list(block) for block in oracle_blocks
        ],
        "block_partition_match": observed_blocks == oracle_blocks,
        "cyclic_block_count": sum(
            len(block) > 1 for block in observed_blocks
        ),
        "statuses_checked": statuses_checked,
        "liveness_mismatches": mismatch_count,
    }


def atlas_census() -> dict[str, object]:
    graph_count = 0
    multiblock_count = 0
    status_count = 0
    partition_mismatches = 0
    liveness_mismatches = 0
    shape_counts: Counter[tuple[int, int]] = Counter()
    for graph in nx.graph_atlas_g():
        node_count = graph.number_of_nodes()
        edge_count = graph.number_of_edges()
        if not (
            3 <= node_count <= 6
            and nx.is_connected(graph)
            and node_count <= edge_count <= 9
        ):
            continue
        edges = canonical_edges(graph)
        row = census_graph(node_count, edges)
        graph_count += 1
        status_count += int(row["statuses_checked"])
        partition_mismatches += int(
            not row["block_partition_match"]
        )
        liveness_mismatches += int(row["liveness_mismatches"])
        multiblock_count += int(row["cyclic_block_count"]) > 1
        shape_counts[(node_count, edge_count)] += 1
    return {
        "graph_count": graph_count,
        "multiblock_graph_count": multiblock_count,
        "status_vectors_checked": status_count,
        "block_partition_mismatches": partition_mismatches,
        "liveness_mismatches": liveness_mismatches,
        "shape_counts": {
            f"n{nodes}_m{edges}": count
            for (nodes, edges), count in sorted(shape_counts.items())
        },
    }


def exact_probability_check() -> dict[str, object]:
    node_count, edges = HAND_GRAPHS["two_diamonds"]
    counts = (1, 2, 3, 2, 1, 2, 1, 3, 2, 1)
    epsilon = Fraction(3, 11)
    labels = (0, 1, 0, 1, 1, 0, 0, 1, 0, 1)
    probabilities = tuple(
        epsilon if label == 0 else 1 - epsilon
        for label in labels
    )
    direct = availability(
        node_count,
        edges,
        counts,
        probabilities,
        blockwise=False,
    )
    product = block_product_availability(
        node_count, edges, counts, probabilities
    )
    return {
        "counts": list(counts),
        "epsilon": f"{epsilon.numerator}/{epsilon.denominator}",
        "labels": "".join(str(label) for label in labels),
        "direct_fraction": (
            f"{direct.numerator}/{direct.denominator}"
        ),
        "block_product_fraction": (
            f"{product.numerator}/{product.denominator}"
        ),
        "exact_match": direct == product,
    }


def main() -> None:
    hand = {
        name: census_graph(node_count, edges)
        for name, (node_count, edges) in HAND_GRAPHS.items()
    }
    receipt = {
        "status": "development_only_all_cells_burned",
        "claim_eligible": False,
        "python": platform.python_version(),
        "networkx": nx.__version__,
        "source_hashes": {
            "block_factorization.py": sha256(
                HERE / "block_factorization.py"
            ),
            "run_development_census.py": sha256(Path(__file__)),
        },
        "hand_graphs": hand,
        "hand_graph_status_vectors_checked": sum(
            int(row["statuses_checked"]) for row in hand.values()
        ),
        "hand_graph_liveness_mismatches": sum(
            int(row["liveness_mismatches"]) for row in hand.values()
        ),
        "atlas": atlas_census(),
        "exact_probability_factorization": exact_probability_check(),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
