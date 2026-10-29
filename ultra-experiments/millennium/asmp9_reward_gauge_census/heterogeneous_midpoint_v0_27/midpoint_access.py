from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from math import atan, ceil, exp, log2, pi, sqrt
from typing import Iterable, Sequence

import numpy as np


Edge = tuple[int, int]


@dataclass(frozen=True)
class Factorization:
    consistent: bool
    item_values: tuple[Fraction, ...]
    context_values: tuple[Fraction, ...]
    component_count: int
    cycle_rank: int
    conflict_edge: Edge | None


def as_fraction(value: int | float | str | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        return value
    return Fraction(str(value))


def validate_graph(
    num_items: int, num_contexts: int, edges: Sequence[Edge]
) -> None:
    if num_items <= 0 or num_contexts <= 0:
        raise ValueError("both bipartition classes must be nonempty")
    if len(set(edges)) != len(edges):
        raise ValueError("duplicate item-context edge")
    for item, context in edges:
        if not 0 <= item < num_items:
            raise ValueError(f"invalid item index: {item}")
        if not 0 <= context < num_contexts:
            raise ValueError(f"invalid context index: {context}")


def _node_item(item: int) -> int:
    return item


def _node_context(num_items: int, context: int) -> int:
    return num_items + context


def component_labels(
    num_items: int, num_contexts: int, edges: Sequence[Edge]
) -> tuple[int, ...]:
    validate_graph(num_items, num_contexts, edges)
    node_count = num_items + num_contexts
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for item, context in edges:
        left = _node_item(item)
        right = _node_context(num_items, context)
        adjacency[left].append(right)
        adjacency[right].append(left)
    labels = [-1] * node_count
    component = 0
    for start in range(node_count):
        if labels[start] >= 0:
            continue
        labels[start] = component
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor in adjacency[node]:
                if labels[neighbor] < 0:
                    labels[neighbor] = component
                    queue.append(neighbor)
        component += 1
    return tuple(labels)


def graph_invariants(
    num_items: int, num_contexts: int, edges: Sequence[Edge]
) -> dict[str, int]:
    labels = component_labels(num_items, num_contexts, edges)
    components = len(set(labels))
    vertices = num_items + num_contexts
    return {
        "vertices": vertices,
        "edges": len(edges),
        "components": components,
        "incidence_rank": vertices - components,
        "cycle_rank": len(edges) - vertices + components,
    }


def incidence_matrix(
    num_items: int, num_contexts: int, edges: Sequence[Edge]
) -> np.ndarray:
    validate_graph(num_items, num_contexts, edges)
    matrix = np.zeros((len(edges), num_items + num_contexts), dtype=float)
    for row, (item, context) in enumerate(edges):
        matrix[row, _node_item(item)] = 1.0
        matrix[row, _node_context(num_items, context)] = -1.0
    return matrix


def factorize_thresholds(
    num_items: int,
    num_contexts: int,
    edges: Sequence[Edge],
    thresholds: Sequence[int | float | str | Fraction],
) -> Factorization:
    validate_graph(num_items, num_contexts, edges)
    if len(thresholds) != len(edges):
        raise ValueError("one threshold is required per edge")
    values = tuple(as_fraction(value) for value in thresholds)
    node_count = num_items + num_contexts
    adjacency: list[list[tuple[int, Fraction, Edge]]] = [
        [] for _ in range(node_count)
    ]
    for edge, value in zip(edges, values):
        item, context = edge
        left = _node_item(item)
        right = _node_context(num_items, context)
        # z_(i,c) = d_i - b_c.
        adjacency[left].append((right, -value, edge))
        adjacency[right].append((left, value, edge))

    potentials: list[Fraction | None] = [None] * node_count
    components = 0
    conflict: Edge | None = None
    for start in range(node_count):
        if potentials[start] is not None:
            continue
        components += 1
        potentials[start] = Fraction(0)
        queue = deque([start])
        while queue:
            node = queue.popleft()
            assert potentials[node] is not None
            for neighbor, increment, edge in adjacency[node]:
                proposed = potentials[node] + increment
                if potentials[neighbor] is None:
                    potentials[neighbor] = proposed
                    queue.append(neighbor)
                elif potentials[neighbor] != proposed and conflict is None:
                    conflict = edge
    concrete = tuple(
        value if value is not None else Fraction(0) for value in potentials
    )
    return Factorization(
        consistent=conflict is None,
        item_values=concrete[:num_items],
        context_values=concrete[num_items:],
        component_count=components,
        cycle_rank=len(edges) - node_count + components,
        conflict_edge=conflict,
    )


def spanning_forest_partition(
    num_items: int, num_contexts: int, edges: Sequence[Edge]
) -> tuple[tuple[Edge, ...], tuple[Edge, ...]]:
    validate_graph(num_items, num_contexts, edges)
    parent = list(range(num_items + num_contexts))
    rank = [0] * len(parent)

    def find(node: int) -> int:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(left: int, right: int) -> bool:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return False
        if rank[left_root] < rank[right_root]:
            left_root, right_root = right_root, left_root
        parent[right_root] = left_root
        if rank[left_root] == rank[right_root]:
            rank[left_root] += 1
        return True

    forest: list[Edge] = []
    chords: list[Edge] = []
    for edge in edges:
        item, context = edge
        if union(_node_item(item), _node_context(num_items, context)):
            forest.append(edge)
        else:
            chords.append(edge)
    return tuple(forest), tuple(chords)


def population_bisect(
    target: int | float | str | Fraction,
    radius: int | float | str | Fraction,
    tolerance: int | float | str | Fraction,
) -> tuple[Fraction, int]:
    target_q = as_fraction(target)
    radius_q = as_fraction(radius)
    tolerance_q = as_fraction(tolerance)
    if radius_q <= 0 or tolerance_q <= 0:
        raise ValueError("radius and tolerance must be positive")
    if abs(target_q) > radius_q:
        raise ValueError("target lies outside offset coverage")
    rounds = max(0, ceil(log2(float(radius_q / tolerance_q))))
    low, high = -radius_q, radius_q
    for step in range(rounds):
        midpoint = (low + high) / 2
        # Query offset -midpoint; every strictly increasing link with midpoint
        # zero returns the sign of target-midpoint.
        difference = target_q - midpoint
        if difference == 0:
            return midpoint, step + 1
        if difference > 0:
            low = midpoint
        else:
            high = midpoint
    return (low + high) / 2, rounds


def reparameterize_arbitrary_midpoints(
    item_values: Sequence[int | float | str | Fraction],
    alternative_items: Sequence[int | float | str | Fraction],
    edges: Sequence[Edge],
    midpoint_biases: Sequence[int | float | str | Fraction],
) -> tuple[Fraction, ...]:
    if len(item_values) != len(alternative_items):
        raise ValueError("item vectors must have the same length")
    if len(edges) != len(midpoint_biases):
        raise ValueError("one midpoint bias is required per edge")
    original = tuple(as_fraction(value) for value in item_values)
    alternative = tuple(as_fraction(value) for value in alternative_items)
    biases = tuple(as_fraction(value) for value in midpoint_biases)
    return tuple(
        bias + alternative[item] - original[item]
        for (item, _), bias in zip(edges, biases)
    )


def effective_thresholds(
    item_values: Sequence[int | float | str | Fraction],
    edges: Sequence[Edge],
    midpoint_biases: Sequence[int | float | str | Fraction],
) -> tuple[Fraction, ...]:
    items = tuple(as_fraction(value) for value in item_values)
    biases = tuple(as_fraction(value) for value in midpoint_biases)
    if len(edges) != len(biases):
        raise ValueError("one midpoint bias is required per edge")
    return tuple(items[item] - bias for (item, _), bias in zip(edges, biases))


def projection_diagnostics(
    num_items: int,
    num_contexts: int,
    edges: Sequence[Edge],
    observations: Sequence[float],
) -> dict[str, object]:
    matrix = incidence_matrix(num_items, num_contexts, edges)
    vector = np.asarray(observations, dtype=float)
    if vector.shape != (len(edges),):
        raise ValueError("observation shape mismatch")
    estimate = np.linalg.pinv(matrix) @ vector
    projection = matrix @ estimate
    residual = vector - projection
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    positive = singular_values[singular_values > 1e-12]
    sigma_min = float(np.min(positive)) if positive.size else 0.0
    amplification = float("inf") if sigma_min == 0.0 else 1.0 / sigma_min
    return {
        "estimate": estimate,
        "projection": projection,
        "residual": residual,
        "residual_norm": float(np.linalg.norm(residual)),
        "sigma_min_positive": sigma_min,
        "quotient_amplification": amplification,
    }


def robust_reconstruction_check(
    num_items: int,
    num_contexts: int,
    edges: Sequence[Edge],
    true_parameters: Sequence[float],
    edge_error: Sequence[float],
) -> dict[str, float | bool]:
    matrix = incidence_matrix(num_items, num_contexts, edges)
    parameters = np.asarray(true_parameters, dtype=float)
    error = np.asarray(edge_error, dtype=float)
    if parameters.shape != (num_items + num_contexts,):
        raise ValueError("parameter shape mismatch")
    if error.shape != (len(edges),):
        raise ValueError("edge-error shape mismatch")
    truth = matrix @ parameters
    observed = truth + error
    diagnostics = projection_diagnostics(
        num_items, num_contexts, edges, observed
    )
    estimate = np.asarray(diagnostics["estimate"])
    truth_gauge_fixed = np.linalg.pinv(matrix) @ truth
    quotient_error = float(np.linalg.norm(estimate - truth_gauge_fixed))
    noise_norm = float(np.linalg.norm(error))
    bound = float(diagnostics["quotient_amplification"]) * noise_norm
    return {
        "noise_norm": noise_norm,
        "quotient_error": quotient_error,
        "registered_bound": bound,
        "pass": quotient_error <= bound + 1e-10,
    }


def maximum_bisection_error(
    targets: Iterable[Fraction], radius: Fraction, tolerance: Fraction
) -> tuple[Fraction, int]:
    maximum = Fraction(0)
    maximum_queries = 0
    for target in targets:
        estimate, queries = population_bisect(target, radius, tolerance)
        maximum = max(maximum, abs(estimate - target))
        maximum_queries = max(maximum_queries, queries)
    return maximum, maximum_queries


def expected_rounds(radius: Fraction, tolerance: Fraction) -> int:
    return max(0, ceil(log2(float(radius / tolerance))))


def link_probability(shape: str, value: float, scale: float) -> float:
    if scale <= 0:
        raise ValueError("link scale must be positive")
    argument = scale * value
    if shape == "logistic":
        if argument >= 0:
            return 1.0 / (1.0 + exp(-argument))
        exponential = exp(argument)
        return exponential / (1.0 + exponential)
    if shape == "atan":
        return 0.5 + atan(argument) / pi
    if shape == "rational":
        return 0.5 + 0.5 * argument / (1.0 + abs(argument))
    raise ValueError(f"unknown link shape: {shape}")


def spectral_bound_from_laplacian(
    num_items: int, num_contexts: int, edges: Sequence[Edge]
) -> float:
    matrix = incidence_matrix(num_items, num_contexts, edges)
    laplacian = matrix.T @ matrix
    eigenvalues = np.linalg.eigvalsh(laplacian)
    positive = eigenvalues[eigenvalues > 1e-12]
    if not positive.size:
        return float("inf")
    return 1.0 / sqrt(float(np.min(positive)))
