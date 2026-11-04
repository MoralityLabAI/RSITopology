"""Exact behavioral-access utilities for the ASMP-9 v0.7 development seed."""

from __future__ import annotations

from collections import deque
from fractions import Fraction
from typing import Sequence


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


def spanning_forest_indices(
    vertex_count: int, edges: Sequence[Edge]
) -> tuple[int, ...]:
    """Return deterministic edge indices for a weak spanning forest."""
    parent = list(range(vertex_count))

    def find(vertex: int) -> int:
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    chosen: list[int] = []
    for index, (source, target) in enumerate(edges):
        left, right = find(source), find(target)
        if left == right:
            continue
        parent[right] = left
        chosen.append(index)
    return tuple(chosen)


def bridge_indices(
    vertex_count: int, edges: Sequence[Edge]
) -> tuple[int, ...]:
    """Return weak-graph bridges, correctly handling loops and parallel edges."""
    baseline = len(weak_components(vertex_count, edges))
    bridges: list[int] = []
    for index in range(len(edges)):
        reduced = tuple(edge for position, edge in enumerate(edges) if position != index)
        if len(weak_components(vertex_count, reduced)) > baseline:
            bridges.append(index)
    return tuple(bridges)


def coherence_only_query_indices(
    vertex_count: int, edges: Sequence[Edge]
) -> tuple[int, ...]:
    bridges = set(bridge_indices(vertex_count, edges))
    return tuple(index for index in range(len(edges)) if index not in bridges)


def reconstruct_from_forest(
    vertex_count: int,
    edges: Sequence[Edge],
    scores: Sequence[Fraction],
    forest_indices: Sequence[int] | None = None,
) -> tuple[Fraction, ...]:
    """Reconstruct component-rooted utilities from coherent tree-edge scores."""
    if len(edges) != len(scores):
        raise ValueError("one score is required per edge")
    if forest_indices is None:
        forest_indices = spanning_forest_indices(vertex_count, edges)
    adjacency: list[list[tuple[int, Fraction]]] = [
        [] for _ in range(vertex_count)
    ]
    for index in forest_indices:
        source, target = edges[index]
        score = Fraction(scores[index])
        adjacency[source].append((target, score))
        adjacency[target].append((source, -score))
    utility: list[Fraction | None] = [None] * vertex_count
    for root in range(vertex_count):
        if utility[root] is not None:
            continue
        utility[root] = Fraction(0)
        queue = deque([root])
        while queue:
            vertex = queue.popleft()
            for neighbor, delta in adjacency[vertex]:
                proposed = utility[vertex] + delta
                if utility[neighbor] is None:
                    utility[neighbor] = proposed
                    queue.append(neighbor)
                elif utility[neighbor] != proposed:
                    raise ValueError("forest indices contain an inconsistent cycle")
    return tuple(value if value is not None else Fraction(0) for value in utility)


def gradient_scores(
    utility: Sequence[Fraction], edges: Sequence[Edge]
) -> tuple[Fraction, ...]:
    return tuple(
        Fraction(utility[target]) - Fraction(utility[source])
        for source, target in edges
    )


def fundamental_residuals(
    vertex_count: int,
    edges: Sequence[Edge],
    scores: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    """Return edge residuals after tree reconstruction.

    Tree-edge residuals are zero. Chord residuals are signed fundamental-cycle
    circulations and vanish exactly for a coherent scalar field.
    """
    forest = spanning_forest_indices(vertex_count, edges)
    utility = reconstruct_from_forest(
        vertex_count, edges, scores, forest
    )
    predicted = gradient_scores(utility, edges)
    return tuple(Fraction(left) - right for left, right in zip(scores, predicted))


def is_coherent(
    vertex_count: int,
    edges: Sequence[Edge],
    scores: Sequence[Fraction],
) -> bool:
    return all(
        residual == 0
        for residual in fundamental_residuals(vertex_count, edges, scores)
    )


def _solve_square(
    matrix: Sequence[Sequence[Fraction]], rhs: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    size = len(matrix)
    if size == 0:
        return ()
    work = [
        [Fraction(value) for value in row] + [Fraction(rhs[index])]
        for index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular system")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [value / divisor for value in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            multiplier = work[row][column]
            work[row] = [
                left - multiplier * right
                for left, right in zip(work[row], work[column])
            ]
    return tuple(work[row][-1] for row in range(size))


def least_squares_projection(
    vertex_count: int,
    edges: Sequence[Edge],
    scores: Sequence[Fraction],
) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...]]:
    """Exact unweighted Hodge projection, with one zero root per component."""
    if len(edges) != len(scores):
        raise ValueError("one score is required per edge")
    roots = {component[0] for component in weak_components(vertex_count, edges)}
    free = [vertex for vertex in range(vertex_count) if vertex not in roots]
    position = {vertex: index for index, vertex in enumerate(free)}
    normal = [
        [Fraction(0) for _ in free]
        for _ in free
    ]
    rhs = [Fraction(0) for _ in free]
    for (source, target), raw_score in zip(edges, scores):
        score = Fraction(raw_score)
        row: dict[int, Fraction] = {}
        if source in position:
            row[position[source]] = Fraction(-1)
        if target in position:
            row[position[target]] = row.get(position[target], Fraction(0)) + 1
        for left, left_value in row.items():
            rhs[left] += left_value * score
            for right, right_value in row.items():
                normal[left][right] += left_value * right_value
    solution = _solve_square(normal, rhs)
    utility = [Fraction(0) for _ in range(vertex_count)]
    for vertex, index in position.items():
        utility[vertex] = solution[index]
    predicted = gradient_scores(utility, edges)
    residual = tuple(
        Fraction(score) - fitted
        for score, fitted in zip(scores, predicted)
    )
    return tuple(utility), residual


def residual_is_orthogonal(
    vertex_count: int,
    edges: Sequence[Edge],
    residual: Sequence[Fraction],
) -> bool:
    divergence = [Fraction(0) for _ in range(vertex_count)]
    for (source, target), value in zip(edges, residual):
        divergence[source] -= Fraction(value)
        divergence[target] += Fraction(value)
    return all(value == 0 for value in divergence)


def adaptive_interval(
    theta: Fraction, query_count: int
) -> tuple[Fraction, Fraction]:
    """Binary-search ambiguity interval for theta in [0,1]."""
    if not Fraction(0) <= theta <= Fraction(1):
        raise ValueError("theta must lie in [0,1]")
    lower, upper = Fraction(0), Fraction(1)
    for _ in range(query_count):
        threshold = (lower + upper) / 2
        if theta > threshold:
            lower = threshold
        elif theta < threshold:
            upper = threshold
        else:
            return theta, theta
    return lower, upper


def nonadaptive_cells(
    thresholds: Sequence[Fraction],
) -> tuple[tuple[Fraction, Fraction], ...]:
    ordered = tuple(sorted({Fraction(value) for value in thresholds}))
    if any(value <= 0 or value >= 1 for value in ordered):
        raise ValueError("thresholds must lie strictly inside [0,1]")
    points = (Fraction(0),) + ordered + (Fraction(1),)
    return tuple(zip(points, points[1:]))


def optimal_nonadaptive_thresholds(query_count: int) -> tuple[Fraction, ...]:
    return tuple(
        Fraction(index, query_count + 1)
        for index in range(1, query_count + 1)
    )


def worst_cell_width(
    cells: Sequence[tuple[Fraction, Fraction]],
) -> Fraction:
    return max((right - left for left, right in cells), default=Fraction(0))
