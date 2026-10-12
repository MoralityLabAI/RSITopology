"""Discounted potential shaping as a gain-graph incidence operator."""

from __future__ import annotations

import itertools
from collections import deque
from fractions import Fraction
from typing import Iterable, Sequence


Edge = tuple[int, int]


def weak_components(vertex_count: int, edges: Sequence[Edge]) -> list[list[int]]:
    adjacency = [[] for _ in range(vertex_count)]
    for source, target in edges:
        adjacency[source].append(target)
        adjacency[target].append(source)
    unseen = set(range(vertex_count))
    components: list[list[int]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        component = [root]
        queue = deque([root])
        while queue:
            vertex = queue.popleft()
            for neighbor in adjacency[vertex]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    component.append(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return components


def component_heights(
    component: Sequence[int], edges: Sequence[Edge]
) -> dict[int, int] | None:
    """Return a unit-increasing height or None when the component is unbalanced."""
    vertices = set(component)
    constraints: list[list[tuple[int, int]]] = [
        [] for _ in range(max(vertices, default=-1) + 1)
    ]
    for source, target in edges:
        if source in vertices:
            constraints[source].append((target, 1))
            constraints[target].append((source, -1))
    root = min(component)
    heights = {root: 0}
    queue = deque([root])
    while queue:
        vertex = queue.popleft()
        for neighbor, delta in constraints[vertex]:
            proposed = heights[vertex] + delta
            if neighbor in heights:
                if heights[neighbor] != proposed:
                    return None
            else:
                heights[neighbor] = proposed
                queue.append(neighbor)
    return heights


def balanced_component_count(
    vertex_count: int, edges: Sequence[Edge]
) -> int:
    return sum(
        component_heights(component, edges) is not None
        for component in weak_components(vertex_count, edges)
    )


def twisted_incidence(
    vertex_count: int,
    edges: Sequence[Edge],
    gamma: Fraction,
) -> list[list[Fraction]]:
    if not (Fraction(0) <= gamma <= Fraction(1)):
        raise ValueError("gamma must lie in [0,1]")
    matrix: list[list[Fraction]] = []
    for source, target in edges:
        row = [Fraction(0) for _ in range(vertex_count)]
        row[source] -= 1
        row[target] += gamma
        matrix.append(row)
    return matrix


def rational_rank(matrix: Sequence[Sequence[Fraction]]) -> int:
    if not matrix:
        return 0
    work = [list(map(Fraction, row)) for row in matrix]
    row_count = len(work)
    column_count = len(work[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (
                row
                for row in range(pivot_row, row_count)
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or not work[row][column]:
                continue
            multiplier = work[row][column]
            work[row] = [
                left - multiplier * right
                for left, right in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def predicted_rank(
    vertex_count: int, edges: Sequence[Edge], gamma: Fraction
) -> int:
    if gamma == 0:
        return len({source for source, _ in edges})
    if gamma == 1:
        return vertex_count - len(weak_components(vertex_count, edges))
    return vertex_count - balanced_component_count(vertex_count, edges)


def quotient_dimension(
    vertex_count: int, edges: Sequence[Edge], gamma: Fraction
) -> int:
    return len(edges) - predicted_rank(vertex_count, edges, gamma)


def enumerate_oriented_simple_graphs(
    vertex_count: int,
) -> Iterable[tuple[Edge, ...]]:
    pairs = list(itertools.combinations(range(vertex_count), 2))
    for states in itertools.product((0, 1, 2), repeat=len(pairs)):
        edges: list[Edge] = []
        for state, (left, right) in zip(states, pairs):
            if state == 1:
                edges.append((left, right))
            elif state == 2:
                edges.append((right, left))
        yield tuple(edges)


def discounted_occupancy(
    trajectory: Sequence[int], gamma: Fraction
) -> dict[Edge, Fraction]:
    if len(trajectory) < 1:
        raise ValueError("trajectory must contain at least one state")
    occupancy: dict[Edge, Fraction] = {}
    for time, edge in enumerate(itertools.pairwise(trajectory)):
        occupancy[edge] = occupancy.get(edge, Fraction(0)) + gamma**time
    return occupancy


def boundary_signature(
    trajectory: Sequence[int], vertex_count: int, gamma: Fraction
) -> tuple[Fraction, ...]:
    if len(trajectory) < 1:
        raise ValueError("trajectory must contain at least one state")
    signature = [Fraction(0) for _ in range(vertex_count)]
    signature[trajectory[0]] -= 1
    signature[trajectory[-1]] += gamma ** (len(trajectory) - 1)
    return tuple(signature)


def shaping_pairing(
    trajectory: Sequence[int],
    potential: Sequence[Fraction],
    gamma: Fraction,
) -> Fraction:
    occupancy = discounted_occupancy(trajectory, gamma)
    total = Fraction(0)
    for (source, target), weight in occupancy.items():
        total += weight * (
            gamma * potential[target] - potential[source]
        )
    return total
