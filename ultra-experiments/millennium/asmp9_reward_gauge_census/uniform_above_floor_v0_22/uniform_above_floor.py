"""Weighted partial-orientation tools for ASMP-9 v0.22 development."""

from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Sequence


Edge = tuple[int, int]
ZERO = 0
INTERIOR = 1
FULL = 2


def validate_connected_simple_graph(
    node_count: int, edges: Sequence[Edge]
) -> None:
    if node_count < 1:
        raise ValueError("node_count must be positive")
    seen_edges: set[frozenset[int]] = set()
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for source, target in edges:
        if not (0 <= source < node_count and 0 <= target < node_count):
            raise ValueError("edge endpoint outside node universe")
        if source == target:
            raise ValueError("graph must be loopless")
        key = frozenset((source, target))
        if key in seen_edges:
            raise ValueError("graph must be simple")
        seen_edges.add(key)
        adjacency[source].append(target)
        adjacency[target].append(source)
    reached = {0}
    stack = [0]
    while stack:
        node = stack.pop()
        for neighbor in adjacency[node]:
            if neighbor not in reached:
                reached.add(neighbor)
                stack.append(neighbor)
    if len(reached) != node_count:
        raise ValueError("graph must be connected")


def _component_count(
    node_count: int,
    edges: Sequence[Edge],
    selected: Sequence[bool] | None = None,
) -> int:
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for index, (source, target) in enumerate(edges):
        if selected is not None and not selected[index]:
            continue
        adjacency[source].append(target)
        adjacency[target].append(source)
    seen: set[int] = set()
    components = 0
    for root in range(node_count):
        if root in seen:
            continue
        components += 1
        seen.add(root)
        stack = [root]
        while stack:
            node = stack.pop()
            for neighbor in adjacency[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return components


def tutte_subset_evaluation(
    node_count: int,
    edges: Sequence[Edge],
    x_value: Fraction,
    y_value: Fraction,
) -> Fraction:
    """Exact spanning-subgraph definition of the Tutte polynomial."""

    validate_connected_simple_graph(node_count, edges)
    graph_components = _component_count(node_count, edges)
    result = Fraction(0)
    for selected in itertools.product((False, True), repeat=len(edges)):
        selected_count = sum(selected)
        components = _component_count(node_count, edges, selected)
        result += (x_value - 1) ** (
            components - graph_components
        ) * (y_value - 1) ** (
            selected_count - node_count + components
        )
    return result


def backman_parameters(
    trial_count: int,
) -> tuple[Fraction, Fraction, Fraction]:
    if trial_count < 1:
        raise ValueError("trial_count must be positive")
    z = Fraction(1, 2**trial_count)
    x_value = (1 - 2 * z) / (1 - z)
    y_value = 1 / z
    return z, x_value, y_value


def _strongly_connected(
    node_count: int, adjacency: Sequence[Sequence[int]]
) -> bool:
    def reached(
        graph: Sequence[Sequence[int]], root: int
    ) -> set[int]:
        seen = {root}
        stack = [root]
        while stack:
            node = stack.pop()
            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        return seen

    forward = reached(adjacency, 0)
    if len(forward) != node_count:
        return False
    reverse: list[list[int]] = [[] for _ in range(node_count)]
    for source, targets in enumerate(adjacency):
        for target in targets:
            reverse[target].append(source)
    return len(reached(reverse, 0)) == node_count


def status_is_strong(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[int],
) -> bool:
    if len(edges) != len(statuses):
        raise ValueError("edge/status dimensions differ")
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for (source, target), status in zip(
        edges, statuses, strict=True
    ):
        if status not in (ZERO, INTERIOR, FULL):
            raise ValueError("invalid status")
        if status in (ZERO, INTERIOR):
            adjacency[source].append(target)
        if status in (INTERIOR, FULL):
            adjacency[target].append(source)
    return _strongly_connected(node_count, adjacency)


def weighted_availability_exhaustive(
    node_count: int,
    edges: Sequence[Edge],
    trial_count: int,
) -> Fraction:
    """Exact ASMP availability under uniform counts and epsilon=1/2."""

    validate_connected_simple_graph(node_count, edges)
    z, _, _ = backman_parameters(trial_count)
    law = (z, 1 - 2 * z, z)
    result = Fraction(0)
    for statuses in itertools.product(
        (ZERO, INTERIOR, FULL), repeat=len(edges)
    ):
        if not status_is_strong(node_count, edges, statuses):
            continue
        mass = Fraction(1)
        for status in statuses:
            mass *= law[status]
        result += mass
    return result


def backman_tutte_availability(
    node_count: int,
    edges: Sequence[Edge],
    trial_count: int,
) -> Fraction:
    """Evaluate the weighted partial-orientation Tutte specialization."""

    validate_connected_simple_graph(node_count, edges)
    z, x_value, y_value = backman_parameters(trial_count)
    genus = len(edges) - node_count + 1
    return (
        (1 - z) ** (node_count - 1)
        * z**genus
        * tutte_subset_evaluation(
            node_count, edges, x_value, y_value
        )
    )


def microtrial_availability(
    node_count: int,
    edges: Sequence[Edge],
    trial_count: int,
) -> Fraction:
    """Directly enumerate fair binary trial matrices for tiny controls."""

    validate_connected_simple_graph(node_count, edges)
    bit_count = len(edges) * trial_count
    successes = 0
    for bits in itertools.product((0, 1), repeat=bit_count):
        statuses: list[int] = []
        for edge_index in range(len(edges)):
            start = edge_index * trial_count
            edge_bits = bits[start : start + trial_count]
            if all(bit == 0 for bit in edge_bits):
                statuses.append(ZERO)
            elif all(bit == 1 for bit in edge_bits):
                statuses.append(FULL)
            else:
                statuses.append(INTERIOR)
        successes += status_is_strong(node_count, edges, statuses)
    return Fraction(successes, 2**bit_count)

