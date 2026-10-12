"""Exact count-floor tools for the ASMP-9 local-block problem.

This module is development-only until a versioned protocol is frozen.

At epsilon = 1/2 and total budget N = |E|, positive integer allocation
forces one comparison per edge.  On a bridgeless graph the ASMP residual
status is then a uniformly random total orientation, and quotient liveness
is exactly total cyclicity.  Hence the availability numerator is T_G(0, 2).
"""

from __future__ import annotations

import itertools
from fractions import Fraction
from functools import lru_cache
from typing import Iterable, Sequence


Edge = tuple[int, int]
MultiEdge = tuple[int, int]


def validate_simple_graph(
    node_count: int, edges: Sequence[Edge]
) -> None:
    if node_count < 1:
        raise ValueError("node_count must be positive")
    seen: set[frozenset[int]] = set()
    for source, target in edges:
        if not (0 <= source < node_count and 0 <= target < node_count):
            raise ValueError("edge endpoint outside node universe")
        if source == target:
            raise ValueError("input graph must be loopless")
        key = frozenset((source, target))
        if key in seen:
            raise ValueError("input graph must be simple")
        seen.add(key)


def _canonical_multigraph(
    edges: Iterable[MultiEdge],
) -> tuple[MultiEdge, ...]:
    """Compress vertex labels and retain loops and edge multiplicity."""

    frozen = [(min(a, b), max(a, b)) for a, b in edges]
    if not frozen:
        return ()
    vertices = sorted({vertex for edge in frozen for vertex in edge})
    relabel = {vertex: index for index, vertex in enumerate(vertices)}
    return tuple(
        sorted((relabel[a], relabel[b]) for a, b in frozen)
    )


def _edge_has_alternative_path(
    edges: Sequence[MultiEdge], edge_index: int
) -> bool:
    source, target = edges[edge_index]
    if source == target:
        return True
    adjacency: dict[int, list[int]] = {}
    for index, (left, right) in enumerate(edges):
        if index == edge_index or left == right:
            continue
        adjacency.setdefault(left, []).append(right)
        adjacency.setdefault(right, []).append(left)
    seen = {source}
    stack = [source]
    while stack:
        node = stack.pop()
        for neighbor in adjacency.get(node, ()):
            if neighbor == target:
                return True
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return False


def _delete_edge(
    edges: Sequence[MultiEdge], edge_index: int
) -> tuple[MultiEdge, ...]:
    return _canonical_multigraph(
        edge for index, edge in enumerate(edges) if index != edge_index
    )


def _contract_edge(
    edges: Sequence[MultiEdge], edge_index: int
) -> tuple[MultiEdge, ...]:
    source, target = edges[edge_index]
    if source == target:
        raise ValueError("cannot contract a loop in this recurrence")

    contracted: list[MultiEdge] = []
    for index, (left, right) in enumerate(edges):
        if index == edge_index:
            continue
        mapped_left = source if left == target else left
        mapped_right = source if right == target else right
        contracted.append((mapped_left, mapped_right))
    return _canonical_multigraph(contracted)


@lru_cache(maxsize=None)
def _tutte_02_cached(edges: tuple[MultiEdge, ...]) -> int:
    if not edges:
        return 1

    for index, (source, target) in enumerate(edges):
        if source == target:
            # A loop contributes the y factor; y = 2.
            return 2 * _tutte_02_cached(_delete_edge(edges, index))

    edge_index = 0
    if not _edge_has_alternative_path(edges, edge_index):
        # A bridge contributes the x factor; x = 0.
        return 0

    return _tutte_02_cached(
        _delete_edge(edges, edge_index)
    ) + _tutte_02_cached(_contract_edge(edges, edge_index))


def tutte_02_deletion_contraction(
    node_count: int, edges: Sequence[Edge]
) -> int:
    """Evaluate T_G(0, 2) with an exact multigraph recurrence."""

    validate_simple_graph(node_count, edges)
    return _tutte_02_cached(_canonical_multigraph(edges))


def _reachability(
    node_count: int, directed_edges: Sequence[Edge]
) -> tuple[frozenset[int], ...]:
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for source, target in directed_edges:
        adjacency[source].append(target)
    result: list[frozenset[int]] = []
    for root in range(node_count):
        seen = {root}
        stack = [root]
        while stack:
            node = stack.pop()
            for neighbor in adjacency[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        result.append(frozenset(seen))
    return tuple(result)


def orientation_from_bits(
    edges: Sequence[Edge], bits: Sequence[int]
) -> tuple[Edge, ...]:
    if len(edges) != len(bits):
        raise ValueError("edge/orientation dimensions differ")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("orientation bits must be binary")
    return tuple(
        (source, target) if bit == 0 else (target, source)
        for (source, target), bit in zip(edges, bits, strict=True)
    )


def orientation_is_totally_cyclic(
    node_count: int,
    edges: Sequence[Edge],
    bits: Sequence[int],
) -> bool:
    """Every oriented edge must lie on a directed cycle."""

    validate_simple_graph(node_count, edges)
    directed = orientation_from_bits(edges, bits)
    reach = _reachability(node_count, directed)
    return all(
        source in reach[target] and target in reach[source]
        for source, target in directed
    )


def count_totally_cyclic_orientations(
    node_count: int, edges: Sequence[Edge]
) -> int:
    """Independent exhaustive orientation count."""

    validate_simple_graph(node_count, edges)
    return sum(
        orientation_is_totally_cyclic(node_count, edges, bits)
        for bits in itertools.product((0, 1), repeat=len(edges))
    )


def bridge_indices(
    node_count: int, edges: Sequence[Edge]
) -> frozenset[int]:
    validate_simple_graph(node_count, edges)
    frozen = tuple((min(a, b), max(a, b)) for a, b in edges)
    return frozenset(
        index
        for index in range(len(frozen))
        if not _edge_has_alternative_path(frozen, index)
    )


def orientation_is_asmp_quotient_live(
    node_count: int,
    edges: Sequence[Edge],
    bits: Sequence[int],
) -> bool:
    """ASMP event: only original nonbridge edges require return paths."""

    validate_simple_graph(node_count, edges)
    directed = orientation_from_bits(edges, bits)
    reach = _reachability(node_count, directed)
    bridges = bridge_indices(node_count, edges)
    return all(
        edge_index in bridges
        or (source in reach[target] and target in reach[source])
        for edge_index, (source, target) in enumerate(directed)
    )


def asmp_count_floor_numerator(
    node_count: int, edges: Sequence[Edge]
) -> int:
    """Count quotient-live total orientations at the count floor."""

    validate_simple_graph(node_count, edges)
    return sum(
        orientation_is_asmp_quotient_live(
            node_count, edges, bits
        )
        for bits in itertools.product((0, 1), repeat=len(edges))
    )


def asmp_count_floor_availability(
    node_count: int, edges: Sequence[Edge]
) -> Fraction:
    return Fraction(
        asmp_count_floor_numerator(node_count, edges),
        2 ** len(edges),
    )


def count_floor_allocation(
    edge_count: int, total_budget: int
) -> tuple[int, ...]:
    """Return the unique positive allocation when N = |E|."""

    if edge_count < 0:
        raise ValueError("edge_count must be nonnegative")
    if total_budget < edge_count:
        raise ValueError("positive allocation is infeasible")
    if total_budget != edge_count:
        raise ValueError("allocation is not unique above the count floor")
    return (1,) * edge_count


def biconnected_edge_blocks(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    """Tarjan edge blocks, including singleton bridge blocks."""

    validate_simple_graph(node_count, edges)
    adjacency: list[list[tuple[int, int]]] = [
        [] for _ in range(node_count)
    ]
    for edge_id, (source, target) in enumerate(edges):
        adjacency[source].append((target, edge_id))
        adjacency[target].append((source, edge_id))

    discovery = [-1] * node_count
    low = [-1] * node_count
    stack: list[int] = []
    blocks: list[tuple[int, ...]] = []
    clock = 0

    def visit(node: int, parent_edge: int | None) -> None:
        nonlocal clock
        discovery[node] = low[node] = clock
        clock += 1
        for neighbor, edge_id in adjacency[node]:
            if edge_id == parent_edge:
                continue
            if discovery[neighbor] == -1:
                stack.append(edge_id)
                visit(neighbor, edge_id)
                low[node] = min(low[node], low[neighbor])
                if low[neighbor] >= discovery[node]:
                    block: list[int] = []
                    while stack:
                        popped = stack.pop()
                        block.append(popped)
                        if popped == edge_id:
                            break
                    blocks.append(tuple(sorted(block)))
            elif discovery[neighbor] < discovery[node]:
                stack.append(edge_id)
                low[node] = min(low[node], discovery[neighbor])

    for root in range(node_count):
        if discovery[root] == -1:
            visit(root, None)
            if stack:
                blocks.append(tuple(sorted(stack)))
                stack.clear()
    return tuple(sorted(blocks, key=lambda block: (min(block), block)))


def tutte_02_block_product(
    node_count: int, edges: Sequence[Edge]
) -> int:
    """Multiply T_B(0,2) over nontrivial edge blocks.

    A singleton bridge makes T_G(0,2) zero.  Isolated vertices contribute one.
    """

    result = 1
    for block in biconnected_edge_blocks(node_count, edges):
        if len(block) == 1:
            return 0
        vertices = sorted(
            {vertex for index in block for vertex in edges[index]}
        )
        local = {vertex: index for index, vertex in enumerate(vertices)}
        local_edges = tuple(
            (
                local[edges[index][0]],
                local[edges[index][1]],
            )
            for index in block
        )
        result *= tutte_02_deletion_contraction(
            len(vertices), local_edges
        )
    return result

