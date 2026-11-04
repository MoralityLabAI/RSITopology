"""Exact finite-budget design on cactus comparison graphs.

This module is development-only until a v0.19 registration binds it.  It
inherits the independent Bernoulli comparison model and conditional-fiber
availability event from ASMP-9 v0.16-v0.18.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Iterable, Iterator, Sequence


def product_fraction(values: Iterable[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def fraction_record(value: Fraction) -> dict[str, object]:
    return {
        "fraction": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
    }


def xyz(count: int, epsilon: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    if count < 1:
        raise ValueError("every registered edge count must be positive")
    if not Fraction(0) < epsilon <= Fraction(1, 2):
        raise ValueError("epsilon must lie in (0,1/2]")
    low = epsilon
    high = 1 - epsilon
    return (
        1 - high**count,
        1 - low**count,
        1 - high**count - low**count,
    )


def balanced_allocation(total: int, length: int) -> tuple[int, ...]:
    if length < 3:
        raise ValueError("cycle length must be at least three")
    if total < length:
        raise ValueError("positive allocation requires total >= length")
    quotient, remainder = divmod(total, length)
    return (
        (quotient,) * (length - remainder)
        + (quotient + 1,) * remainder
    )


def cycle_availability_for_labels(
    counts: Sequence[int],
    epsilon: Fraction,
    labels: Sequence[int],
) -> Fraction:
    """Return cycle liveness for one endpoint-label assignment.

    ``label=0`` means ``p=epsilon`` and ``label=1`` means
    ``p=1-epsilon``.  Reference edge orientations are assumed to trace one
    consistently oriented cycle.
    """

    if len(counts) < 3 or len(labels) != len(counts):
        raise ValueError("counts and labels must describe one cycle")
    no_zero: list[Fraction] = []
    no_full: list[Fraction] = []
    interior: list[Fraction] = []
    for count, label in zip(counts, labels, strict=True):
        if label not in (0, 1):
            raise ValueError("endpoint labels must be zero or one")
        x_value, y_value, z_value = xyz(count, epsilon)
        if label == 0:
            no_zero.append(x_value)
            no_full.append(y_value)
        else:
            no_zero.append(y_value)
            no_full.append(x_value)
        interior.append(z_value)
    return (
        product_fraction(no_zero)
        + product_fraction(no_full)
        - product_fraction(interior)
    )


def cycle_worst_direct(
    counts: Sequence[int], epsilon: Fraction
) -> tuple[Fraction, tuple[tuple[int, ...], ...]]:
    rows = [
        (
            cycle_availability_for_labels(counts, epsilon, labels),
            labels,
        )
        for labels in product((0, 1), repeat=len(counts))
    ]
    minimum = min(value for value, _ in rows)
    witnesses = tuple(labels for value, labels in rows if value == minimum)
    return minimum, witnesses


def balanced_cycle_value(
    length: int, total: int, epsilon: Fraction
) -> tuple[Fraction, tuple[tuple[int, int], ...]]:
    """Compact exact v0.16 optimum for one cycle."""

    counts = balanced_allocation(total, length)
    lower = counts[0]
    upper = counts[-1]
    upper_count = total - lower * length
    lower_count = length - upper_count
    x_lower, y_lower, z_lower = xyz(lower, epsilon)
    x_upper, y_upper, z_upper = xyz(upper, epsilon)
    rows: list[tuple[Fraction, tuple[int, int]]] = []
    for low_labels_lower in range(lower_count + 1):
        for low_labels_upper in range(upper_count + 1):
            first = (
                x_lower**low_labels_lower
                * y_lower ** (lower_count - low_labels_lower)
                * x_upper**low_labels_upper
                * y_upper ** (upper_count - low_labels_upper)
            )
            second = (
                y_lower**low_labels_lower
                * x_lower ** (lower_count - low_labels_lower)
                * y_upper**low_labels_upper
                * x_upper ** (upper_count - low_labels_upper)
            )
            value = (
                first
                + second
                - z_lower**lower_count * z_upper**upper_count
            )
            rows.append((value, (low_labels_lower, low_labels_upper)))
    minimum = min(value for value, _ in rows)
    return minimum, tuple(
        witness for value, witness in rows if value == minimum
    )


def bounded_compositions(
    total: int, lower_bounds: Sequence[int]
) -> Iterator[tuple[int, ...]]:
    """Enumerate integer vectors summing to total above componentwise floors."""

    floors = tuple(int(value) for value in lower_bounds)
    if any(value < 0 for value in floors):
        raise ValueError("lower bounds must be nonnegative")
    slack = total - sum(floors)
    if slack < 0:
        return

    def recurse(index: int, remaining: int, prefix: tuple[int, ...]):
        if index == len(floors) - 1:
            yield prefix + (floors[index] + remaining,)
            return
        for assigned in range(remaining + 1):
            yield from recurse(
                index + 1,
                remaining - assigned,
                prefix + (floors[index] + assigned,),
            )

    if not floors:
        if total == 0:
            yield ()
        return
    yield from recurse(0, slack, ())


@dataclass(frozen=True)
class Edge:
    edge_id: str
    source: int
    target: int


@dataclass(frozen=True)
class CactusGraph:
    edges: tuple[Edge, ...]
    cycle_blocks: tuple[tuple[int, ...], ...]
    bridge_indices: tuple[int, ...]

    @property
    def vertices(self) -> tuple[int, ...]:
        return tuple(
            sorted(
                {
                    vertex
                    for edge in self.edges
                    for vertex in (edge.source, edge.target)
                }
            )
        )


def bouquet_cactus(
    cycle_lengths: Sequence[int], bridge_count: int = 0
) -> CactusGraph:
    """Construct edge-disjoint cycles sharing one articulation vertex."""

    if not cycle_lengths or any(length < 3 for length in cycle_lengths):
        raise ValueError("a cactus requires cycle lengths of at least three")
    if bridge_count < 0:
        raise ValueError("bridge_count must be nonnegative")
    edges: list[Edge] = []
    blocks: list[tuple[int, ...]] = []
    next_vertex = 1
    for block_index, length in enumerate(cycle_lengths):
        vertices = (0,) + tuple(range(next_vertex, next_vertex + length - 1))
        next_vertex += length - 1
        block: list[int] = []
        for offset in range(length):
            source = vertices[offset]
            target = vertices[(offset + 1) % length]
            block.append(len(edges))
            edges.append(
                Edge(
                    edge_id=f"c{block_index}_e{offset}",
                    source=source,
                    target=target,
                )
            )
        blocks.append(tuple(block))
    bridges: list[int] = []
    previous = 0
    for index in range(bridge_count):
        current = next_vertex
        next_vertex += 1
        bridges.append(len(edges))
        edges.append(
            Edge(
                edge_id=f"bridge_{index}",
                source=previous,
                target=current,
            )
        )
        previous = current
    return CactusGraph(
        edges=tuple(edges),
        cycle_blocks=tuple(blocks),
        bridge_indices=tuple(bridges),
    )


def validate_cactus(graph: CactusGraph) -> None:
    if not graph.edges:
        raise ValueError("graph must contain edges")
    all_indices = set(range(len(graph.edges)))
    cycle_indices = [
        index for block in graph.cycle_blocks for index in block
    ]
    if len(cycle_indices) != len(set(cycle_indices)):
        raise ValueError("cycle blocks must be edge-disjoint")
    if set(cycle_indices) | set(graph.bridge_indices) != all_indices:
        raise ValueError("cycle and bridge indices must partition the edges")
    if set(cycle_indices) & set(graph.bridge_indices):
        raise ValueError("a bridge cannot be a cycle edge")
    if len(graph.bridge_indices) != len(set(graph.bridge_indices)):
        raise ValueError("bridge indices must be unique")

    vertices = set(graph.vertices)
    undirected = {vertex: set() for vertex in vertices}
    for edge in graph.edges:
        undirected[edge.source].add(edge.target)
        undirected[edge.target].add(edge.source)
    reached = {next(iter(vertices))}
    frontier = list(reached)
    while frontier:
        vertex = frontier.pop()
        for neighbor in undirected[vertex]:
            if neighbor not in reached:
                reached.add(neighbor)
                frontier.append(neighbor)
    if reached != vertices:
        raise ValueError("registered cactus graph must be connected")

    actual_bridges: set[int] = set()
    for removed, edge in enumerate(graph.edges):
        reached_without = {edge.source}
        frontier_without = [edge.source]
        while frontier_without:
            vertex = frontier_without.pop()
            for index, candidate in enumerate(graph.edges):
                if index == removed:
                    continue
                if candidate.source == vertex:
                    neighbor = candidate.target
                elif candidate.target == vertex:
                    neighbor = candidate.source
                else:
                    continue
                if neighbor not in reached_without:
                    reached_without.add(neighbor)
                    frontier_without.append(neighbor)
        if edge.target not in reached_without:
            actual_bridges.add(removed)
    if actual_bridges != set(graph.bridge_indices):
        raise ValueError(
            "registered bridge indices do not match graph-theoretic bridges"
        )

    block_vertices: list[set[int]] = []
    for block in graph.cycle_blocks:
        if len(block) < 3:
            raise ValueError("cycle blocks must have at least three edges")
        edges = [graph.edges[index] for index in block]
        for left, right in zip(edges, edges[1:] + edges[:1], strict=True):
            if left.target != right.source:
                raise ValueError(
                    "cycle block edges must trace a directed simple cycle"
                )
        vertices = {edge.source for edge in edges}
        if len(vertices) != len(edges):
            raise ValueError("cycle block must be simple")
        block_vertices.append(vertices)
    for left_index, left in enumerate(block_vertices):
        for right in block_vertices[left_index + 1 :]:
            if len(left & right) > 1:
                raise ValueError(
                    "distinct cactus cycles may share at most one vertex"
                )


def _strong_components(
    vertices: Sequence[int], arcs: Sequence[tuple[int, int]]
) -> dict[int, int]:
    adjacency = {vertex: [] for vertex in vertices}
    reverse = {vertex: [] for vertex in vertices}
    for source, target in arcs:
        adjacency[source].append(target)
        reverse[target].append(source)

    seen: set[int] = set()
    order: list[int] = []

    def visit(vertex: int) -> None:
        seen.add(vertex)
        for target in adjacency[vertex]:
            if target not in seen:
                visit(target)
        order.append(vertex)

    for vertex in vertices:
        if vertex not in seen:
            visit(vertex)

    components: dict[int, int] = {}

    def assign(vertex: int, component: int) -> None:
        components[vertex] = component
        for source in reverse[vertex]:
            if source not in components:
                assign(source, component)

    component = 0
    for vertex in reversed(order):
        if vertex not in components:
            assign(vertex, component)
            component += 1
    return components


def _residual_full_liveness_validated(
    graph: CactusGraph, statuses: Sequence[str]
) -> bool:
    if len(statuses) != len(graph.edges):
        raise ValueError("one residual status is required per edge")
    arcs: list[tuple[int, int]] = []
    for edge, status in zip(graph.edges, statuses, strict=True):
        if status not in {"Z", "I", "F"}:
            raise ValueError("status must be Z, I, or F")
        if status in {"Z", "I"}:
            arcs.append((edge.source, edge.target))
        if status in {"F", "I"}:
            arcs.append((edge.target, edge.source))
    components = _strong_components(graph.vertices, arcs)
    for block in graph.cycle_blocks:
        for edge_index in block:
            edge = graph.edges[edge_index]
            if components[edge.source] != components[edge.target]:
                return False
    return True


def residual_full_liveness(
    graph: CactusGraph, statuses: Sequence[str]
) -> bool:
    validate_cactus(graph)
    return _residual_full_liveness_validated(graph, statuses)


def status_probabilities(
    count: int, epsilon: Fraction, label: int
) -> dict[str, Fraction]:
    if label not in (0, 1):
        raise ValueError("endpoint labels must be zero or one")
    probability = epsilon if label == 0 else 1 - epsilon
    return {
        "Z": (1 - probability) ** count,
        "F": probability**count,
        "I": 1 - (1 - probability) ** count - probability**count,
    }


def graph_availability_direct(
    graph: CactusGraph,
    counts: Sequence[int],
    epsilon: Fraction,
    labels: Sequence[int],
) -> Fraction:
    """Enumerate all ternary residual states for one endpoint-label vector."""

    validate_cactus(graph)
    if len(counts) != len(graph.edges) or len(labels) != len(graph.edges):
        raise ValueError("counts and labels must cover every graph edge")
    probabilities = [
        status_probabilities(count, epsilon, label)
        for count, label in zip(counts, labels, strict=True)
    ]
    total = Fraction(0)
    for statuses in product(("Z", "I", "F"), repeat=len(graph.edges)):
        if _residual_full_liveness_validated(graph, statuses):
            total += product_fraction(
                probabilities[index][status]
                for index, status in enumerate(statuses)
            )
    return total


def cactus_availability_factorized(
    graph: CactusGraph,
    counts: Sequence[int],
    epsilon: Fraction,
    labels: Sequence[int],
) -> Fraction:
    validate_cactus(graph)
    if len(counts) != len(graph.edges) or len(labels) != len(graph.edges):
        raise ValueError("counts and labels must cover every graph edge")
    return product_fraction(
        cycle_availability_for_labels(
            tuple(counts[index] for index in block),
            epsilon,
            tuple(labels[index] for index in block),
        )
        for block in graph.cycle_blocks
    )


def cactus_worst_for_edge_counts(
    graph: CactusGraph,
    counts: Sequence[int],
    epsilon: Fraction,
) -> Fraction:
    validate_cactus(graph)
    if len(counts) != len(graph.edges):
        raise ValueError("one count is required per edge")
    return product_fraction(
        cycle_worst_direct(
            tuple(counts[index] for index in block), epsilon
        )[0]
        for block in graph.cycle_blocks
    )


@dataclass(frozen=True)
class AllocationResult:
    value: Fraction
    cycle_totals: tuple[tuple[int, ...], ...]
    transitions_evaluated: int


def optimize_cactus_dp(
    cycle_lengths: Sequence[int],
    total_budget: int,
    epsilon: Fraction,
    bridge_count: int = 0,
) -> AllocationResult:
    """Exact Bellman recursion over per-cycle totals."""

    lengths = tuple(int(length) for length in cycle_lengths)
    if not lengths or any(length < 3 for length in lengths):
        raise ValueError("cycle lengths must all be at least three")
    if bridge_count < 0:
        raise ValueError("bridge_count must be nonnegative")
    cycle_budget = total_budget - bridge_count
    if cycle_budget < sum(lengths):
        raise ValueError("budget cannot supply one trial to every edge")

    # used budget -> (best product, all attaining cycle-total prefixes)
    states: dict[int, tuple[Fraction, set[tuple[int, ...]]]] = {
        0: (Fraction(1), {()})
    }
    transitions = 0
    for block_index, length in enumerate(lengths):
        remaining_floor = sum(lengths[block_index + 1 :])
        next_states: dict[
            int, tuple[Fraction, set[tuple[int, ...]]]
        ] = {}
        for used, (prefix_value, prefixes) in states.items():
            maximum = cycle_budget - used - remaining_floor
            for assigned in range(length, maximum + 1):
                transitions += 1
                cycle_value = balanced_cycle_value(
                    length, assigned, epsilon
                )[0]
                candidate = prefix_value * cycle_value
                target_used = used + assigned
                candidate_prefixes = {
                    prefix + (assigned,) for prefix in prefixes
                }
                incumbent = next_states.get(target_used)
                if incumbent is None or candidate > incumbent[0]:
                    next_states[target_used] = (
                        candidate,
                        candidate_prefixes,
                    )
                elif candidate == incumbent[0]:
                    incumbent[1].update(candidate_prefixes)
        states = next_states
    value, optimizers = states[cycle_budget]
    return AllocationResult(
        value=value,
        cycle_totals=tuple(sorted(optimizers)),
        transitions_evaluated=transitions,
    )


def optimize_cycle_totals_exhaustive(
    cycle_lengths: Sequence[int],
    total_budget: int,
    epsilon: Fraction,
    bridge_count: int = 0,
) -> AllocationResult:
    """Independent exact enumeration using direct endpoint-label minima."""

    lengths = tuple(int(length) for length in cycle_lengths)
    cycle_budget = total_budget - bridge_count
    rows: list[tuple[Fraction, tuple[int, ...]]] = []
    for totals in bounded_compositions(cycle_budget, lengths):
        value = product_fraction(
            cycle_worst_direct(
                balanced_allocation(total, length), epsilon
            )[0]
            for length, total in zip(lengths, totals, strict=True)
        )
        rows.append((value, totals))
    if not rows:
        raise ValueError("no feasible allocation")
    maximum = max(value for value, _ in rows)
    return AllocationResult(
        value=maximum,
        cycle_totals=tuple(
            totals for value, totals in rows if value == maximum
        ),
        transitions_evaluated=len(rows),
    )


def optimize_all_edges_exhaustive(
    graph: CactusGraph,
    total_budget: int,
    epsilon: Fraction,
) -> tuple[Fraction, tuple[tuple[int, ...], ...]]:
    """Exhaust all positive labelled edge allocations on a small cactus."""

    validate_cactus(graph)
    rows: list[tuple[Fraction, tuple[int, ...]]] = []
    for counts in bounded_compositions(
        total_budget, (1,) * len(graph.edges)
    ):
        rows.append(
            (cactus_worst_for_edge_counts(graph, counts, epsilon), counts)
        )
    if not rows:
        raise ValueError("no feasible edge allocation")
    maximum = max(value for value, _ in rows)
    return maximum, tuple(
        counts for value, counts in rows if value == maximum
    )


def marginal_greedy_endpoints(
    cycle_lengths: Sequence[int],
    total_budget: int,
    epsilon: Fraction,
) -> tuple[tuple[int, ...], ...]:
    """All endpoints of the maximum-one-step-ratio greedy rule.

    Enumerating every tie branch makes a greedy counterexample independent of
    arbitrary tie breaking.
    """

    lengths = tuple(int(length) for length in cycle_lengths)
    if total_budget < sum(lengths):
        raise ValueError("infeasible budget")
    states = {lengths}
    while sum(next(iter(states))) < total_budget:
        next_states: set[tuple[int, ...]] = set()
        for totals in states:
            ratios = [
                balanced_cycle_value(length, total + 1, epsilon)[0]
                / balanced_cycle_value(length, total, epsilon)[0]
                for length, total in zip(lengths, totals, strict=True)
            ]
            maximum = max(ratios)
            for index, ratio in enumerate(ratios):
                if ratio == maximum:
                    updated = list(totals)
                    updated[index] += 1
                    next_states.add(tuple(updated))
        states = next_states
    return tuple(sorted(states))


def allocation_value(
    cycle_lengths: Sequence[int],
    cycle_totals: Sequence[int],
    epsilon: Fraction,
) -> Fraction:
    if len(cycle_lengths) != len(cycle_totals):
        raise ValueError("length and total vectors must align")
    return product_fraction(
        balanced_cycle_value(length, total, epsilon)[0]
        for length, total in zip(
            cycle_lengths, cycle_totals, strict=True
        )
    )


def globally_balanced_cycle_totals(
    cycle_lengths: Sequence[int], total_budget: int
) -> tuple[tuple[int, ...], ...]:
    """Cycle totals induced by counts differing by at most one globally."""

    lengths = tuple(int(length) for length in cycle_lengths)
    edge_count = sum(lengths)
    if total_budget < edge_count:
        raise ValueError("infeasible budget")
    lower, high_count = divmod(total_budget, edge_count)
    totals: set[tuple[int, ...]] = set()
    for highs_by_cycle in bounded_compositions(
        high_count, (0,) * len(lengths)
    ):
        if all(
            highs <= length
            for highs, length in zip(
                highs_by_cycle, lengths, strict=True
            )
        ):
            totals.add(
                tuple(
                    lower * length + highs
                    for highs, length in zip(
                        highs_by_cycle, lengths, strict=True
                    )
                )
            )
    return tuple(sorted(totals))
