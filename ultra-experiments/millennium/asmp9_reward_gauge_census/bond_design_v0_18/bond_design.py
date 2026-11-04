from __future__ import annotations

import itertools
from collections import defaultdict
from fractions import Fraction
from typing import Iterable, Sequence


Edge = tuple[int, int]


def validate_graph(node_count: int, edges: Sequence[Edge]) -> None:
    if node_count < 1:
        raise ValueError("node_count must be positive")
    if not edges:
        raise ValueError("at least one edge is required")
    seen: set[frozenset[int]] = set()
    for source, target in edges:
        if not (0 <= source < node_count and 0 <= target < node_count):
            raise ValueError("edge endpoint outside node universe")
        if source == target:
            raise ValueError("self loops are not supported")
        key = frozenset((source, target))
        if key in seen:
            raise ValueError("parallel undirected edges are not supported")
        seen.add(key)


def _component_count(
    node_count: int,
    edges: Sequence[Edge],
    excluded_edge: int | None = None,
) -> int:
    adjacency = [[] for _ in range(node_count)]
    for index, (source, target) in enumerate(edges):
        if index == excluded_edge:
            continue
        adjacency[source].append(target)
        adjacency[target].append(source)
    seen: set[int] = set()
    count = 0
    for root in range(node_count):
        if root in seen:
            continue
        count += 1
        seen.add(root)
        stack = [root]
        while stack:
            node = stack.pop()
            for neighbor in adjacency[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return count


def bridge_indices(
    node_count: int, edges: Sequence[Edge]
) -> tuple[int, ...]:
    validate_graph(node_count, edges)
    base = _component_count(node_count, edges)
    return tuple(
        index
        for index in range(len(edges))
        if _component_count(node_count, edges, index) > base
    )


def cyclic_core_components(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    """Return (vertices, original_edge_indices) after deleting bridges."""

    validate_graph(node_count, edges)
    bridges = set(bridge_indices(node_count, edges))
    adjacency: list[list[tuple[int, int]]] = [
        [] for _ in range(node_count)
    ]
    for index, (source, target) in enumerate(edges):
        if index in bridges:
            continue
        adjacency[source].append((target, index))
        adjacency[target].append((source, index))

    seen: set[int] = set()
    components: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    for root in range(node_count):
        if root in seen or not adjacency[root]:
            continue
        vertices: set[int] = {root}
        edge_ids: set[int] = set()
        seen.add(root)
        stack = [root]
        while stack:
            node = stack.pop()
            for neighbor, edge_id in adjacency[node]:
                edge_ids.add(edge_id)
                vertices.add(neighbor)
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(
            (tuple(sorted(vertices)), tuple(sorted(edge_ids)))
        )
    return tuple(
        sorted(components, key=lambda item: (item[0], item[1]))
    )


def _induced_connected(
    vertices: frozenset[int],
    edges: Sequence[Edge],
    edge_ids: Sequence[int],
) -> bool:
    if not vertices:
        return False
    root = min(vertices)
    adjacency: dict[int, list[int]] = {vertex: [] for vertex in vertices}
    for edge_id in edge_ids:
        source, target = edges[edge_id]
        if source in vertices and target in vertices:
            adjacency[source].append(target)
            adjacency[target].append(source)
    seen = {root}
    stack = [root]
    while stack:
        node = stack.pop()
        for neighbor in adjacency[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return seen == set(vertices)


def component_bonds(
    edges: Sequence[Edge],
    vertices: Sequence[int],
    edge_ids: Sequence[int],
) -> tuple[tuple[int, ...], ...]:
    """Enumerate each bond once using the side containing the least vertex."""

    vertex_tuple = tuple(sorted(vertices))
    if len(vertex_tuple) < 2:
        return ()
    root = vertex_tuple[0]
    remaining = vertex_tuple[1:]
    universe = frozenset(vertex_tuple)
    bonds: set[tuple[int, ...]] = set()
    for mask in range(1 << len(remaining)):
        side = frozenset(
            (root,)
            + tuple(
                vertex
                for offset, vertex in enumerate(remaining)
                if mask & (1 << offset)
            )
        )
        if side == universe:
            continue
        complement = universe - side
        if not _induced_connected(side, edges, edge_ids):
            continue
        if not _induced_connected(complement, edges, edge_ids):
            continue
        cut = tuple(
            sorted(
                edge_id
                for edge_id in edge_ids
                if (edges[edge_id][0] in side)
                != (edges[edge_id][1] in side)
            )
        )
        if not cut:
            raise AssertionError("connected component produced empty cut")
        bonds.add(cut)
    return tuple(sorted(bonds, key=lambda item: (len(item), item)))


def cyclic_core_bonds(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    bonds: set[tuple[int, ...]] = set()
    for vertices, edge_ids in cyclic_core_components(node_count, edges):
        bonds.update(component_bonds(edges, vertices, edge_ids))
    return tuple(sorted(bonds, key=lambda item: (len(item), item)))


def simple_cycle_edge_sets(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    """Exact small-graph cycle enumerator used only for cactus controls."""

    validate_graph(node_count, edges)
    cycles: set[tuple[int, ...]] = set()
    for size in range(3, len(edges) + 1):
        for edge_ids in itertools.combinations(range(len(edges)), size):
            degree: dict[int, int] = defaultdict(int)
            vertices: set[int] = set()
            for edge_id in edge_ids:
                source, target = edges[edge_id]
                degree[source] += 1
                degree[target] += 1
                vertices.update((source, target))
            if len(vertices) != size:
                continue
            if any(degree[vertex] != 2 for vertex in vertices):
                continue
            if _induced_connected(
                frozenset(vertices), edges, edge_ids
            ):
                cycles.add(tuple(edge_ids))
    return tuple(sorted(cycles, key=lambda item: (len(item), item)))


def cactus_closed_form(
    node_count: int, edges: Sequence[Edge]
) -> dict[str, object]:
    bridges = set(bridge_indices(node_count, edges))
    cyclic_edges = tuple(
        index for index in range(len(edges)) if index not in bridges
    )
    if not cyclic_edges:
        raise ValueError("cactus control requires at least one cycle")
    cycles = simple_cycle_edge_sets(node_count, edges)
    memberships = {
        edge: sum(edge in cycle for cycle in cycles)
        for edge in cyclic_edges
    }
    if any(count != 1 for count in memberships.values()):
        raise ValueError(
            "nonbridge edges do not form a cactus cycle system"
        )
    edge_count = len(cyclic_edges)
    weights = tuple(
        Fraction(0) if index in bridges else Fraction(1, edge_count)
        for index in range(len(edges))
    )
    return {
        "threshold": Fraction(2, edge_count),
        "weights": weights,
        "cycles": cycles,
        "cyclic_edge_count": edge_count,
    }


def all_simple_graphs(
    node_count: int,
) -> Iterable[tuple[Edge, ...]]:
    universe = tuple(itertools.combinations(range(node_count), 2))
    for mask in range(1, 1 << len(universe)):
        yield tuple(
            edge
            for index, edge in enumerate(universe)
            if mask & (1 << index)
        )
