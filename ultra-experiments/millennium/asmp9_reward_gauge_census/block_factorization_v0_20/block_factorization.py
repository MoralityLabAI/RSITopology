"""Exact block decomposition for the ASMP-9 residual-liveness object.

Development-only until a versioned protocol is frozen.
"""

from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Iterable, Sequence


Edge = tuple[int, int]
Status = int
ZERO = 0
INTERIOR = 1
FULL = 2


def validate_graph(node_count: int, edges: Sequence[Edge]) -> None:
    if node_count < 1:
        raise ValueError("node_count must be positive")
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


def biconnected_edge_blocks(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    """Return Tarjan edge blocks, including singleton bridge blocks."""

    validate_graph(node_count, edges)
    adjacency: list[list[tuple[int, int]]] = [
        [] for _ in range(node_count)
    ]
    for edge_id, (source, target) in enumerate(edges):
        adjacency[source].append((target, edge_id))
        adjacency[target].append((source, edge_id))

    discovery = [-1] * node_count
    low = [-1] * node_count
    edge_stack: list[int] = []
    blocks: list[tuple[int, ...]] = []
    clock = 0

    def dfs(node: int, parent_edge: int | None) -> None:
        nonlocal clock
        discovery[node] = low[node] = clock
        clock += 1
        for neighbor, edge_id in adjacency[node]:
            if edge_id == parent_edge:
                continue
            if discovery[neighbor] == -1:
                edge_stack.append(edge_id)
                dfs(neighbor, edge_id)
                low[node] = min(low[node], low[neighbor])
                if low[neighbor] >= discovery[node]:
                    block: list[int] = []
                    while edge_stack:
                        popped = edge_stack.pop()
                        block.append(popped)
                        if popped == edge_id:
                            break
                    blocks.append(tuple(sorted(block)))
            elif discovery[neighbor] < discovery[node]:
                edge_stack.append(edge_id)
                low[node] = min(low[node], discovery[neighbor])

    for root in range(node_count):
        if discovery[root] == -1:
            dfs(root, None)
            if edge_stack:
                blocks.append(tuple(sorted(edge_stack)))
                edge_stack.clear()
    return tuple(sorted(blocks, key=lambda block: (min(block), block)))


def cyclic_blocks(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    """Return non-singleton biconnected edge blocks."""

    return tuple(
        block
        for block in biconnected_edge_blocks(node_count, edges)
        if len(block) > 1
    )


def _strongly_connected(adjacency: Sequence[Sequence[int]]) -> bool:
    if not adjacency:
        return True

    def reachable(graph: Sequence[Sequence[int]]) -> set[int]:
        seen = {0}
        stack = [0]
        while stack:
            node = stack.pop()
            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        return seen

    if len(reachable(adjacency)) != len(adjacency):
        return False
    reverse: list[list[int]] = [[] for _ in adjacency]
    for source, targets in enumerate(adjacency):
        for target in targets:
            reverse[target].append(source)
    return len(reachable(reverse)) == len(adjacency)


def block_available(
    edges: Sequence[Edge],
    statuses: Sequence[Status],
    edge_ids: Sequence[int],
) -> bool:
    vertices = sorted(
        {vertex for edge_id in edge_ids for vertex in edges[edge_id]}
    )
    local = {vertex: index for index, vertex in enumerate(vertices)}
    adjacency: list[list[int]] = [[] for _ in vertices]
    for edge_id in edge_ids:
        source, target = edges[edge_id]
        status = statuses[edge_id]
        if status in (ZERO, INTERIOR):
            adjacency[local[source]].append(local[target])
        if status in (INTERIOR, FULL):
            adjacency[local[target]].append(local[source])
        if status not in (ZERO, INTERIOR, FULL):
            raise ValueError("status must be ZERO, INTERIOR, or FULL")
    return _strongly_connected(adjacency)


def blockwise_available(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[Status],
) -> bool:
    if len(edges) != len(statuses):
        raise ValueError("edge/status dimensions differ")
    return all(
        block_available(edges, statuses, block)
        for block in cyclic_blocks(node_count, edges)
    )


def _component_count(
    node_count: int,
    edges: Sequence[Edge],
    excluded_edge: int | None = None,
) -> int:
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for edge_id, (source, target) in enumerate(edges):
        if edge_id == excluded_edge:
            continue
        adjacency[source].append(target)
        adjacency[target].append(source)
    count = 0
    seen: set[int] = set()
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


def direct_available(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[Status],
) -> bool:
    """Independent full-graph edge-on-directed-cycle definition."""

    validate_graph(node_count, edges)
    if len(edges) != len(statuses):
        raise ValueError("edge/status dimensions differ")
    base_components = _component_count(node_count, edges)
    bridges = {
        edge_id
        for edge_id in range(len(edges))
        if _component_count(node_count, edges, edge_id)
        > base_components
    }
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for edge_id, ((source, target), status) in enumerate(
        zip(edges, statuses, strict=True)
    ):
        if status in (ZERO, INTERIOR):
            adjacency[source].append(target)
        if status in (INTERIOR, FULL):
            adjacency[target].append(source)
        if status not in (ZERO, INTERIOR, FULL):
            raise ValueError("status must be ZERO, INTERIOR, or FULL")

    # Compute SCC labels by mutual reachability; development graphs are small.
    reach: list[set[int]] = []
    for root in range(node_count):
        seen = {root}
        stack = [root]
        while stack:
            node = stack.pop()
            for neighbor in adjacency[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        reach.append(seen)
    return all(
        edge_id in bridges
        or (target in reach[source] and source in reach[target])
        for edge_id, (source, target) in enumerate(edges)
    )


def status_probabilities(
    count: int, probability: Fraction
) -> tuple[Fraction, Fraction, Fraction]:
    if count < 1:
        raise ValueError("counts must be positive")
    if not Fraction(0) <= probability <= Fraction(1):
        raise ValueError("probability outside [0,1]")
    zero = (1 - probability) ** count
    full = probability**count
    return zero, 1 - zero - full, full


def availability(
    node_count: int,
    edges: Sequence[Edge],
    counts: Sequence[int],
    probabilities: Sequence[Fraction],
    *,
    blockwise: bool,
) -> Fraction:
    if len(edges) != len(counts) or len(edges) != len(probabilities):
        raise ValueError("edge/count/probability dimensions differ")
    laws = [
        status_probabilities(count, probability)
        for count, probability in zip(
            counts, probabilities, strict=True
        )
    ]
    predicate = blockwise_available if blockwise else direct_available
    result = Fraction(0)
    for statuses in itertools.product(
        (ZERO, INTERIOR, FULL), repeat=len(edges)
    ):
        if not predicate(node_count, edges, statuses):
            continue
        mass = Fraction(1)
        for law, status in zip(laws, statuses, strict=True):
            mass *= law[status]
        result += mass
    return result


def block_product_availability(
    node_count: int,
    edges: Sequence[Edge],
    counts: Sequence[int],
    probabilities: Sequence[Fraction],
) -> Fraction:
    result = Fraction(1)
    for block in cyclic_blocks(node_count, edges):
        vertices = sorted(
            {vertex for edge_id in block for vertex in edges[edge_id]}
        )
        local = {vertex: index for index, vertex in enumerate(vertices)}
        local_edges = tuple(
            (
                local[edges[edge_id][0]],
                local[edges[edge_id][1]],
            )
            for edge_id in block
        )
        result *= availability(
            len(vertices),
            local_edges,
            tuple(counts[edge_id] for edge_id in block),
            tuple(probabilities[edge_id] for edge_id in block),
            blockwise=False,
        )
    return result


def all_statuses(edge_count: int) -> Iterable[tuple[Status, ...]]:
    return itertools.product((ZERO, INTERIOR, FULL), repeat=edge_count)
