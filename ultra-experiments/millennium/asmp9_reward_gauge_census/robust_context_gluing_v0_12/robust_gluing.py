"""Development utilities for robust contextual scalar gluing.

The module is intentionally independent of the sealed v0.11 implementation.
It accepts incidence matrices directly and treats the robust geometry as a
nested-subspace problem.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import inf
from typing import Iterable, Sequence

import numpy as np


Array = np.ndarray
Edge = tuple[int, int]


@dataclass(frozen=True)
class Decomposition:
    shared: Array
    gluing: Array
    local_residual: Array
    rho_glue: float
    rho_local: float
    rho_total: float
    pythagorean_residual: float
    obstruction_dimension: int


@dataclass(frozen=True)
class QueryDesign:
    indices: tuple[int, ...]
    rank: int
    singular_values: tuple[float, ...]
    sigma_min: float
    amplification: float
    total_support: int


@dataclass(frozen=True)
class CycleDesignCensus:
    candidate_count: int
    obstruction_dimension: int
    spanning_design_count: int
    minimum_total_support: int | None
    shortest_best: QueryDesign | None
    shortest_worst: QueryDesign | None
    e_optimal: QueryDesign | None


def incidence_matrix(item_count: int, edges: Sequence[Edge]) -> Array:
    matrix = np.zeros((len(edges), item_count), dtype=float)
    for index, (left, right) in enumerate(edges):
        if not (0 <= left < right < item_count):
            raise ValueError("edges must use canonical distinct endpoints")
        matrix[index, left] = -1.0
        matrix[index, right] = 1.0
    return matrix


def local_global_incidence(
    item_count: int, contexts: Sequence[Sequence[Edge]]
) -> tuple[Array, Array, tuple[tuple[int, Edge], ...]]:
    labelled = tuple(
        (context_index, edge)
        for context_index, context in enumerate(contexts)
        for edge in context
    )
    edge_count = len(labelled)
    local = np.zeros((edge_count, item_count * len(contexts)), dtype=float)
    shared = np.zeros((edge_count, item_count), dtype=float)
    for row, (context_index, (left, right)) in enumerate(labelled):
        if not (0 <= left < right < item_count):
            raise ValueError("edges must use canonical distinct endpoints")
        offset = context_index * item_count
        local[row, offset + left] = -1.0
        local[row, offset + right] = 1.0
        shared[row, left] = -1.0
        shared[row, right] = 1.0
    return local, shared, labelled


def _column_basis(matrix: Array, tolerance: float = 1e-10) -> Array:
    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2:
        raise ValueError("matrix must be two-dimensional")
    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        return np.zeros((matrix.shape[0], 0), dtype=float)
    left, singular, _ = np.linalg.svd(matrix, full_matrices=False)
    if not singular.size:
        return np.zeros((matrix.shape[0], 0), dtype=float)
    cutoff = tolerance * max(matrix.shape) * max(1.0, float(singular[0]))
    rank = int(np.sum(singular > cutoff))
    return left[:, :rank]


def projector(matrix: Array, tolerance: float = 1e-10) -> Array:
    basis = _column_basis(matrix, tolerance)
    return basis @ basis.T


def quotient_basis(
    local_matrix: Array,
    shared_matrix: Array,
    tolerance: float = 1e-10,
) -> Array:
    local = np.asarray(local_matrix, dtype=float)
    shared = np.asarray(shared_matrix, dtype=float)
    if local.shape[0] != shared.shape[0]:
        raise ValueError("local and shared matrices need the same codomain")
    p_local = projector(local, tolerance)
    p_shared = projector(shared, tolerance)
    nesting_error = float(np.linalg.norm((np.eye(local.shape[0]) - p_local) @ shared))
    if nesting_error > 100 * tolerance:
        raise ValueError("shared image is not contained in local image")
    p_quotient = (p_local - p_shared + (p_local - p_shared).T) / 2.0
    eigenvalues, eigenvectors = np.linalg.eigh(p_quotient)
    selected = eigenvalues > 0.5
    basis = eigenvectors[:, selected]
    for column in range(basis.shape[1]):
        nonzero = np.flatnonzero(np.abs(basis[:, column]) > tolerance)
        if nonzero.size and basis[nonzero[0], column] < 0:
            basis[:, column] *= -1
    return basis


def decompose(
    local_matrix: Array,
    shared_matrix: Array,
    observation: Sequence[float],
    tolerance: float = 1e-10,
) -> Decomposition:
    local = np.asarray(local_matrix, dtype=float)
    shared_matrix = np.asarray(shared_matrix, dtype=float)
    y = np.asarray(observation, dtype=float)
    if y.ndim != 1 or y.shape[0] != local.shape[0]:
        raise ValueError("observation has the wrong dimension")
    p_local = projector(local, tolerance)
    p_shared = projector(shared_matrix, tolerance)
    nesting_error = float(np.linalg.norm((np.eye(local.shape[0]) - p_local) @ shared_matrix))
    if nesting_error > 100 * tolerance:
        raise ValueError("shared image is not contained in local image")
    shared = p_shared @ y
    gluing = (p_local - p_shared) @ y
    residual = (np.eye(local.shape[0]) - p_local) @ y
    rho_glue = float(np.linalg.norm(gluing))
    rho_local = float(np.linalg.norm(residual))
    rho_total = float(np.linalg.norm(y - shared))
    pythagorean_residual = abs(
        rho_total**2 - rho_glue**2 - rho_local**2
    )
    q_basis = quotient_basis(local, shared_matrix, tolerance)
    return Decomposition(
        shared=shared,
        gluing=gluing,
        local_residual=residual,
        rho_glue=rho_glue,
        rho_local=rho_local,
        rho_total=rho_total,
        pythagorean_residual=pythagorean_residual,
        obstruction_dimension=q_basis.shape[1],
    )


def _is_connected_cycle(
    item_count: int, labelled_edges: Sequence[tuple[int, Edge]], indices: Sequence[int]
) -> bool:
    degree = [0] * item_count
    adjacency: list[list[int]] = [[] for _ in range(item_count)]
    for index in indices:
        _, (left, right) = labelled_edges[index]
        degree[left] += 1
        degree[right] += 1
        adjacency[left].append(right)
        adjacency[right].append(left)
    active = [vertex for vertex, value in enumerate(degree) if value]
    if not active or any(degree[vertex] != 2 for vertex in active):
        return False
    seen = {active[0]}
    stack = [active[0]]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == len(active)


def _signed_cycle(
    item_count: int,
    labelled_edges: Sequence[tuple[int, Edge]],
    indices: Sequence[int],
) -> Array:
    vector = np.zeros(len(labelled_edges), dtype=float)
    first = indices[0]
    vector[first] = 1.0
    incidence = incidence_matrix(
        item_count, tuple(labelled_edges[index][1] for index in indices)
    )
    local_index = {edge_index: position for position, edge_index in enumerate(indices)}
    incident: list[list[int]] = [[] for _ in range(item_count)]
    for edge_index in indices:
        _, (left, right) = labelled_edges[edge_index]
        incident[left].append(edge_index)
        incident[right].append(edge_index)
    changed = True
    while changed:
        changed = False
        for vertex in range(item_count):
            edges = incident[vertex]
            if len(edges) != 2:
                continue
            known = [edge for edge in edges if vector[edge] != 0]
            unknown = [edge for edge in edges if vector[edge] == 0]
            if len(known) == 1 and len(unknown) == 1:
                known_edge = known[0]
                unknown_edge = unknown[0]
                known_sign = incidence[local_index[known_edge], vertex]
                unknown_sign = incidence[local_index[unknown_edge], vertex]
                vector[unknown_edge] = (
                    -known_sign * vector[known_edge] / unknown_sign
                )
                changed = True
    if any(vector[index] == 0 for index in indices):
        raise AssertionError("cycle orientation propagation failed")
    full_incidence = incidence_matrix(
        item_count, tuple(edge for _, edge in labelled_edges)
    )
    if np.linalg.norm(full_incidence.T @ vector) > 1e-9:
        raise AssertionError("constructed vector is not a signed cycle")
    return vector


def simple_cycle_vectors(
    item_count: int,
    labelled_edges: Sequence[tuple[int, Edge]],
    maximum_edges: int = 16,
) -> tuple[Array, ...]:
    edge_count = len(labelled_edges)
    if edge_count > maximum_edges:
        raise ValueError("simple-cycle enumeration exceeds development cap")
    cycles = []
    for size in range(2, edge_count + 1):
        for indices in combinations(range(edge_count), size):
            if _is_connected_cycle(item_count, labelled_edges, indices):
                cycles.append(_signed_cycle(item_count, labelled_edges, indices))
    return tuple(cycles)


def query_design(
    cycles: Sequence[Array],
    quotient: Array,
    indices: Sequence[int],
    tolerance: float = 1e-10,
) -> QueryDesign:
    dimension = quotient.shape[1]
    rows = []
    total_support = 0
    for index in indices:
        cycle = np.asarray(cycles[index], dtype=float)
        norm = float(np.linalg.norm(cycle))
        if norm <= tolerance:
            raise ValueError("zero query is not admissible")
        rows.append((cycle / norm) @ quotient)
        total_support += int(np.count_nonzero(np.abs(cycle) > tolerance))
    matrix = np.asarray(rows, dtype=float).reshape(len(indices), dimension)
    singular = np.linalg.svd(matrix, compute_uv=False)
    rank = int(np.sum(singular > tolerance))
    sigma_min = (
        float(singular[dimension - 1])
        if len(indices) >= dimension and rank == dimension and dimension
        else 0.0
    )
    amplification = 1.0 / sigma_min if sigma_min > tolerance else inf
    return QueryDesign(
        indices=tuple(indices),
        rank=rank,
        singular_values=tuple(map(float, singular)),
        sigma_min=sigma_min,
        amplification=amplification,
        total_support=total_support,
    )


def cycle_design_census(
    cycles: Sequence[Array],
    quotient: Array,
    tolerance: float = 1e-10,
) -> CycleDesignCensus:
    dimension = quotient.shape[1]
    informative = tuple(
        index
        for index, cycle in enumerate(cycles)
        if np.linalg.norm(np.asarray(cycle) @ quotient) > tolerance
    )
    if dimension == 0:
        return CycleDesignCensus(
            candidate_count=len(informative),
            obstruction_dimension=0,
            spanning_design_count=1,
            minimum_total_support=0,
            shortest_best=QueryDesign((), 0, (), inf, 0.0, 0),
            shortest_worst=QueryDesign((), 0, (), inf, 0.0, 0),
            e_optimal=QueryDesign((), 0, (), inf, 0.0, 0),
        )
    spanning = []
    for indices in combinations(informative, dimension):
        design = query_design(cycles, quotient, indices, tolerance)
        if design.rank == dimension:
            spanning.append(design)
    if not spanning:
        return CycleDesignCensus(
            candidate_count=len(informative),
            obstruction_dimension=dimension,
            spanning_design_count=0,
            minimum_total_support=None,
            shortest_best=None,
            shortest_worst=None,
            e_optimal=None,
        )
    minimum_support = min(design.total_support for design in spanning)
    shortest = [
        design for design in spanning if design.total_support == minimum_support
    ]
    shortest_best = max(
        shortest, key=lambda design: (design.sigma_min, tuple(-i for i in design.indices))
    )
    shortest_worst = min(
        shortest, key=lambda design: (design.sigma_min, design.indices)
    )
    e_optimal = max(
        spanning,
        key=lambda design: (
            design.sigma_min,
            -design.total_support,
            tuple(-i for i in design.indices),
        ),
    )
    return CycleDesignCensus(
        candidate_count=len(informative),
        obstruction_dimension=dimension,
        spanning_design_count=len(spanning),
        minimum_total_support=minimum_support,
        shortest_best=shortest_best,
        shortest_worst=shortest_worst,
        e_optimal=e_optimal,
    )


def arbitrary_query_bound(matrix: Array, tolerance: float = 1e-10) -> dict[str, float | int]:
    matrix = np.asarray(matrix, dtype=float)
    singular = np.linalg.svd(matrix, compute_uv=False)
    rank = int(np.sum(singular > tolerance))
    dimension = matrix.shape[1]
    sigma_min = (
        float(singular[dimension - 1])
        if matrix.shape[0] >= dimension and rank == dimension and dimension
        else 0.0
    )
    return {
        "query_count": matrix.shape[0],
        "dimension": dimension,
        "rank": rank,
        "sigma_min": sigma_min,
        "amplification": 1.0 / sigma_min if sigma_min > tolerance else inf,
    }
