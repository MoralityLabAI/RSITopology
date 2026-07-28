from __future__ import annotations

import itertools
from fractions import Fraction
from functools import lru_cache
from typing import Iterable, Sequence


Edge = tuple[int, int]
Status = int
ZERO = 0
INTERIOR = 1
FULL = 2


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


def connected_component_count(
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
    components = 0
    for root in range(node_count):
        if root in seen:
            continue
        components += 1
        stack = [root]
        seen.add(root)
        while stack:
            node = stack.pop()
            for neighbor in adjacency[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return components


def graph_cycle_rank(node_count: int, edges: Sequence[Edge]) -> int:
    validate_graph(node_count, edges)
    return (
        len(edges)
        - node_count
        + connected_component_count(node_count, edges)
    )


def bridge_mask(node_count: int, edges: Sequence[Edge]) -> tuple[bool, ...]:
    base_components = connected_component_count(node_count, edges)
    return tuple(
        connected_component_count(node_count, edges, index)
        > base_components
        for index in range(len(edges))
    )


def residual_adjacency(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[Status],
) -> list[list[int]]:
    if len(edges) != len(statuses):
        raise ValueError("edge/status dimensions differ")
    adjacency = [[] for _ in range(node_count)]
    for (source, target), status in zip(edges, statuses, strict=True):
        if status in (ZERO, INTERIOR):
            adjacency[source].append(target)
        if status in (INTERIOR, FULL):
            adjacency[target].append(source)
        if status not in (ZERO, INTERIOR, FULL):
            raise ValueError("status must be ZERO, INTERIOR, or FULL")
    return adjacency


def strongly_connected_components(
    adjacency: Sequence[Sequence[int]],
) -> tuple[int, ...]:
    node_count = len(adjacency)
    reverse = [[] for _ in range(node_count)]
    for source, targets in enumerate(adjacency):
        for target in targets:
            reverse[target].append(source)

    seen: set[int] = set()
    order: list[int] = []
    for root in range(node_count):
        if root in seen:
            continue
        stack: list[tuple[int, bool]] = [(root, False)]
        while stack:
            node, exiting = stack.pop()
            if exiting:
                order.append(node)
                continue
            if node in seen:
                continue
            seen.add(node)
            stack.append((node, True))
            for target in adjacency[node]:
                if target not in seen:
                    stack.append((target, False))

    component = [-1] * node_count
    identifier = 0
    for root in reversed(order):
        if component[root] != -1:
            continue
        component[root] = identifier
        stack = [root]
        while stack:
            node = stack.pop()
            for target in reverse[node]:
                if component[target] == -1:
                    component[target] = identifier
                    stack.append(target)
        identifier += 1
    return tuple(component)


def residual_cycle_edge_mask(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[Status],
) -> tuple[bool, ...]:
    components = strongly_connected_components(
        residual_adjacency(node_count, edges, statuses)
    )
    return tuple(
        components[source] == components[target]
        for source, target in edges
    )


def full_quotient_available(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[Status],
) -> bool:
    bridges = bridge_mask(node_count, edges)
    residual_cycles = residual_cycle_edge_mask(
        node_count, edges, statuses
    )
    return all(
        is_bridge or is_residual_cycle
        for is_bridge, is_residual_cycle in zip(
            bridges, residual_cycles, strict=True
        )
    )


def minimal_bad_boundary_supports(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    validate_graph(node_count, edges)
    bad_supports: set[frozenset[int]] = set()
    edge_count = len(edges)
    for statuses in itertools.product(
        (ZERO, INTERIOR, FULL), repeat=edge_count
    ):
        if full_quotient_available(node_count, edges, statuses):
            continue
        support = frozenset(
            index
            for index, status in enumerate(statuses)
            if status != INTERIOR
        )
        bad_supports.add(support)
    minimal = [
        support
        for support in bad_supports
        if not any(
            other < support for other in bad_supports
        )
    ]
    return tuple(
        sorted(
            (tuple(sorted(support)) for support in minimal),
            key=lambda support: (len(support), support),
        )
    )


def _solve_square(
    matrix: Sequence[Sequence[Fraction]],
    vector: Sequence[Fraction],
) -> tuple[Fraction, ...] | None:
    size = len(matrix)
    if size == 0 or len(vector) != size:
        raise ValueError("square system dimensions differ")
    work = [
        [Fraction(value) for value in row]
        + [Fraction(vector[index])]
        for index, row in enumerate(matrix)
    ]
    if any(len(row) != size + 1 for row in work):
        raise ValueError("matrix must be square")
    for column in range(size):
        pivot = next(
            (
                row
                for row in range(column, size)
                if work[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            return None
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    work[row][entry]
                    - factor * work[column][entry]
                    for entry in range(size + 1)
                ]
    return tuple(work[row][-1] for row in range(size))


def fractional_bad_support_design(
    edge_count: int,
    supports: Sequence[Sequence[int]],
) -> dict[str, object]:
    normalized = tuple(
        tuple(sorted(set(int(edge) for edge in support)))
        for support in supports
    )
    if edge_count < 1 or not normalized:
        raise ValueError("edge universe and supports must be nonempty")
    if any(
        not support
        or any(not 0 <= edge < edge_count for edge in support)
        for support in normalized
    ):
        raise ValueError("support outside edge universe")

    active_constraints: list[
        tuple[str, int, tuple[Fraction, ...], Fraction]
    ] = []
    for index, support in enumerate(normalized):
        active_constraints.append(
            (
                "support",
                index,
                tuple(
                    Fraction(int(edge in support))
                    for edge in range(edge_count)
                )
                + (Fraction(-1),),
                Fraction(0),
            )
        )
    for edge in range(edge_count):
        active_constraints.append(
            (
                "zero",
                edge,
                tuple(
                    Fraction(int(index == edge))
                    for index in range(edge_count)
                )
                + (Fraction(0),),
                Fraction(0),
            )
        )

    equality = (Fraction(1),) * edge_count + (Fraction(0),)
    candidates: list[
        tuple[
            Fraction,
            tuple[Fraction, ...],
            tuple[tuple[str, int], ...],
        ]
    ] = []
    for selected in itertools.combinations(
        active_constraints, edge_count
    ):
        solution = _solve_square(
            [equality] + [constraint[2] for constraint in selected],
            [Fraction(1)]
            + [constraint[3] for constraint in selected],
        )
        if solution is None:
            continue
        weights = solution[:edge_count]
        threshold = solution[-1]
        if any(weight < 0 for weight in weights):
            continue
        if any(
            sum(weights[edge] for edge in support) < threshold
            for support in normalized
        ):
            continue
        candidates.append(
            (
                threshold,
                weights,
                tuple(
                    (constraint[0], constraint[1])
                    for constraint in selected
                ),
            )
        )
    if not candidates:
        raise AssertionError("fractional design LP has no vertex")
    optimum = max(candidate[0] for candidate in candidates)
    optimal_vertices = sorted(
        {
            candidate[1]
            for candidate in candidates
            if candidate[0] == optimum
        }
    )
    return {
        "threshold": optimum,
        "optimal_vertices": optimal_vertices,
        "support_count": len(normalized),
        "vertex_certificate_count": sum(
            candidate[0] == optimum for candidate in candidates
        ),
    }
@lru_cache(maxsize=None)
def live_status_vectors(
    node_count: int, edges: tuple[Edge, ...]
) -> tuple[tuple[Status, ...], ...]:
    validate_graph(node_count, edges)
    return tuple(
        statuses
        for statuses in itertools.product(
            (ZERO, INTERIOR, FULL), repeat=len(edges)
        )
        if full_quotient_available(node_count, edges, statuses)
    )


def status_probabilities(
    count: int, probability: Fraction
) -> tuple[Fraction, Fraction, Fraction]:
    if count < 1:
        raise ValueError("counts must be positive")
    if not 0 <= probability <= 1:
        raise ValueError("probability must lie in [0,1]")
    zero = (1 - probability) ** count
    full = probability**count
    return zero, 1 - zero - full, full


def full_quotient_availability(
    node_count: int,
    edges: Sequence[Edge],
    counts: Sequence[int],
    probabilities: Sequence[Fraction],
) -> Fraction:
    validate_graph(node_count, edges)
    if len(edges) != len(counts) or len(edges) != len(probabilities):
        raise ValueError("edge/count/probability dimensions differ")
    status_laws = [
        status_probabilities(count, probability)
        for count, probability in zip(
            counts, probabilities, strict=True
        )
    ]
    result = Fraction(0)
    for statuses in live_status_vectors(node_count, tuple(edges)):
        mass = Fraction(1)
        for law, status in zip(status_laws, statuses, strict=True):
            mass *= law[status]
        result += mass
    return result


def worst_endpoint_availability(
    node_count: int,
    edges: Sequence[Edge],
    counts: Sequence[int],
    epsilon: Fraction,
) -> tuple[Fraction, list[tuple[int, ...]]]:
    if not 0 <= epsilon <= Fraction(1, 2):
        raise ValueError("epsilon must lie in [0,1/2]")
    minimum: Fraction | None = None
    witnesses: list[tuple[int, ...]] = []
    for labels in itertools.product((0, 1), repeat=len(edges)):
        probabilities = tuple(
            epsilon if label == 0 else 1 - epsilon
            for label in labels
        )
        value = full_quotient_availability(
            node_count, edges, counts, probabilities
        )
        if minimum is None or value < minimum:
            minimum = value
            witnesses = [labels]
        elif value == minimum:
            witnesses.append(labels)
    if minimum is None:
        raise AssertionError("empty endpoint universe")
    return minimum, witnesses


def theta_availability(
    paths: Sequence[Sequence[int]],
    counts: Sequence[int],
    probabilities: Sequence[Fraction],
) -> Fraction:
    edge_count = len(counts)
    flattened = [edge for path in paths for edge in path]
    if sorted(flattened) != list(range(edge_count)):
        raise ValueError(
            "theta paths must partition the registered edge indices"
        )
    if len(paths) < 2:
        raise ValueError("a theta graph needs at least two paths")
    laws = [
        status_probabilities(count, probability)
        for count, probability in zip(
            counts, probabilities, strict=True
        )
    ]
    path_terms = []
    for path in paths:
        forward = Fraction(1)
        reverse = Fraction(1)
        both = Fraction(1)
        for edge in path:
            zero, interior, full = laws[edge]
            forward *= 1 - full
            reverse *= 1 - zero
            both *= interior
        usable = forward + reverse - both
        path_terms.append((forward, reverse, both, usable))

    all_usable = Fraction(1)
    all_forward_only = Fraction(1)
    all_reverse_only = Fraction(1)
    for forward, reverse, both, usable in path_terms:
        all_usable *= usable
        all_forward_only *= forward - both
        all_reverse_only *= reverse - both
    return all_usable - all_forward_only - all_reverse_only


def theta_worst_endpoint_availability(
    paths: Sequence[Sequence[int]],
    counts: Sequence[int],
    epsilon: Fraction,
) -> tuple[Fraction, list[tuple[int, ...]]]:
    minimum: Fraction | None = None
    witnesses: list[tuple[int, ...]] = []
    for labels in itertools.product((0, 1), repeat=len(counts)):
        probabilities = tuple(
            epsilon if label == 0 else 1 - epsilon
            for label in labels
        )
        value = theta_availability(paths, counts, probabilities)
        if minimum is None or value < minimum:
            minimum = value
            witnesses = [labels]
        elif value == minimum:
            witnesses.append(labels)
    if minimum is None:
        raise AssertionError("empty endpoint universe")
    return minimum, witnesses


def theta_allocation_census(
    paths: Sequence[Sequence[int]],
    total: int,
    epsilon: Fraction,
) -> dict[str, object]:
    edge_count = sum(len(path) for path in paths)
    records = []
    for counts in positive_allocations(total, edge_count):
        value, witnesses = theta_worst_endpoint_availability(
            paths, counts, epsilon
        )
        records.append((value, counts, witnesses))
    optimum = max(value for value, _, _ in records)
    optimizers = [
        counts for value, counts, _ in records if value == optimum
    ]
    return {
        "path_lengths": [len(path) for path in paths],
        "total_trials": total,
        "epsilon": f"{epsilon.numerator}/{epsilon.denominator}",
        "allocation_count": len(records),
        "optimum": optimum,
        "optimizers": optimizers,
        "balanced_optimizer_count": sum(
            max(counts) - min(counts) <= 1
            for counts in optimizers
        ),
    }


def positive_allocations(
    total: int, edge_count: int
) -> Iterable[tuple[int, ...]]:
    if edge_count == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total - edge_count + 2):
        for rest in positive_allocations(
            total - first, edge_count - 1
        ):
            yield (first, *rest)


def allocation_census(
    node_count: int,
    edges: Sequence[Edge],
    total: int,
    epsilon: Fraction,
) -> dict[str, object]:
    records = []
    for counts in positive_allocations(total, len(edges)):
        value, witnesses = worst_endpoint_availability(
            node_count, edges, counts, epsilon
        )
        records.append((value, counts, witnesses))
    optimum = max(value for value, _, _ in records)
    optimizers = [
        counts for value, counts, _ in records if value == optimum
    ]
    return {
        "node_count": node_count,
        "edges": [list(edge) for edge in edges],
        "cycle_rank": graph_cycle_rank(node_count, edges),
        "total_trials": total,
        "epsilon": f"{epsilon.numerator}/{epsilon.denominator}",
        "allocation_count": len(records),
        "optimum": optimum,
        "optimizers": optimizers,
        "balanced_optimizer_count": sum(
            max(counts) - min(counts) <= 1
            for counts in optimizers
        ),
    }
