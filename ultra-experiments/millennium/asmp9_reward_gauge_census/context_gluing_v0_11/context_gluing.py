"""Exact context-local versus shared-scalar preference geometry."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Sequence


Edge = tuple[int, int]
Matrix = tuple[tuple[Fraction, ...], ...]
Vector = tuple[Fraction, ...]


@dataclass(frozen=True)
class ContextGraph:
    name: str
    edges: tuple[Edge, ...]


class DisjointSet:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.component_count = size

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> bool:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return False
        self.parent[right_root] = left_root
        self.component_count -= 1
        return True


def validate_contexts(item_count: int, contexts: Sequence[ContextGraph]) -> None:
    if item_count < 1:
        raise ValueError("item_count must be positive")
    if not contexts:
        raise ValueError("at least one context is required")
    names = [context.name for context in contexts]
    if len(names) != len(set(names)):
        raise ValueError("context names must be unique")
    for context in contexts:
        if len(context.edges) != len(set(context.edges)):
            raise ValueError("duplicate edge within one context")
        for left, right in context.edges:
            if not (0 <= left < item_count and 0 <= right < item_count):
                raise ValueError("edge endpoint outside item universe")
            if left == right:
                raise ValueError("self-comparisons are not permitted")


def matrix_rank(matrix: Sequence[Sequence[object]]) -> int:
    work = [list(map(Fraction, row)) for row in matrix]
    if not work:
        return 0
    width = len(work[0])
    if any(len(row) != width for row in work):
        raise ValueError("ragged matrix")
    rank = 0
    for column in range(width):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        divisor = work[rank][column]
        work[rank] = [value / divisor for value in work[rank]]
        for row in range(len(work)):
            if row == rank or work[row][column] == 0:
                continue
            multiplier = work[row][column]
            work[row] = [
                left - multiplier * right for left, right in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == len(work):
            break
    return rank


def incidence_matrix(item_count: int, edges: Sequence[Edge]) -> Matrix:
    rows = []
    for left, right in edges:
        row = [Fraction(0) for _ in range(item_count)]
        row[left] = Fraction(-1)
        row[right] = Fraction(1)
        rows.append(tuple(row))
    return tuple(rows)


def component_count(item_count: int, edges: Iterable[Edge]) -> int:
    disjoint = DisjointSet(item_count)
    for left, right in edges:
        disjoint.union(left, right)
    return disjoint.component_count


def cycle_rank(item_count: int, edges: Sequence[Edge]) -> int:
    return len(edges) - item_count + component_count(item_count, edges)


def labelled_edges(
    contexts: Sequence[ContextGraph],
) -> tuple[tuple[int, Edge], ...]:
    return tuple(
        (context_index, edge)
        for context_index, context in enumerate(contexts)
        for edge in context.edges
    )


def local_incidence_matrix(item_count: int, contexts: Sequence[ContextGraph]) -> Matrix:
    width = item_count * len(contexts)
    rows = []
    for context_index, edge in labelled_edges(contexts):
        left, right = edge
        row = [Fraction(0) for _ in range(width)]
        row[context_index * item_count + left] = Fraction(-1)
        row[context_index * item_count + right] = Fraction(1)
        rows.append(tuple(row))
    return tuple(rows)


def global_incidence_matrix(
    item_count: int, contexts: Sequence[ContextGraph]
) -> Matrix:
    return incidence_matrix(
        item_count, tuple(edge for _, edge in labelled_edges(contexts))
    )


def obstruction_dimensions(
    item_count: int, contexts: Sequence[ContextGraph]
) -> dict[str, int]:
    validate_contexts(item_count, contexts)
    union_edges = tuple(edge for _, edge in labelled_edges(contexts))
    local_cycle_rank = sum(
        cycle_rank(item_count, context.edges) for context in contexts
    )
    union_cycle_rank = cycle_rank(item_count, union_edges)
    local_rank = matrix_rank(local_incidence_matrix(item_count, contexts))
    global_rank = matrix_rank(global_incidence_matrix(item_count, contexts))
    return {
        "local_rank": local_rank,
        "global_rank": global_rank,
        "rank_difference": local_rank - global_rank,
        "local_cycle_rank": local_cycle_rank,
        "union_cycle_rank": union_cycle_rank,
        "mixed_cycle_rank": union_cycle_rank - local_cycle_rank,
        "union_component_count": component_count(item_count, union_edges),
    }


def apply_matrix(matrix: Matrix, vector: Sequence[object]) -> Vector:
    values = tuple(map(Fraction, vector))
    return tuple(
        sum(coefficient * value for coefficient, value in zip(row, values))
        for row in matrix
    )


def is_in_column_image(matrix: Matrix, vector: Sequence[object]) -> bool:
    values = tuple(map(Fraction, vector))
    if len(values) != len(matrix):
        raise ValueError("vector dimension differs from matrix codomain")
    augmented = tuple(tuple(row) + (value,) for row, value in zip(matrix, values))
    return matrix_rank(augmented) == matrix_rank(matrix)


def is_locally_scalar(
    item_count: int,
    contexts: Sequence[ContextGraph],
    flow: Sequence[object],
) -> bool:
    validate_contexts(item_count, contexts)
    return is_in_column_image(local_incidence_matrix(item_count, contexts), flow)


def has_shared_scalar(
    item_count: int,
    contexts: Sequence[ContextGraph],
    flow: Sequence[object],
) -> bool:
    validate_contexts(item_count, contexts)
    return is_in_column_image(global_incidence_matrix(item_count, contexts), flow)


def local_flow(
    item_count: int,
    contexts: Sequence[ContextGraph],
    context_utilities: Sequence[Sequence[object]],
) -> Vector:
    if len(context_utilities) != len(contexts):
        raise ValueError("one utility vector is required per context")
    flat = []
    for utilities in context_utilities:
        if len(utilities) != item_count:
            raise ValueError("utility vector has wrong item count")
        flat.extend(map(Fraction, utilities))
    return apply_matrix(local_incidence_matrix(item_count, contexts), tuple(flat))


def global_flow(
    item_count: int,
    contexts: Sequence[ContextGraph],
    utility: Sequence[object],
) -> Vector:
    if len(utility) != item_count:
        raise ValueError("utility vector has wrong item count")
    return apply_matrix(global_incidence_matrix(item_count, contexts), utility)


def non_gluing_witness(
    item_count: int, contexts: Sequence[ContextGraph]
) -> Vector | None:
    """Return a locally scalar flow outside the shared-scalar image."""
    local_matrix = local_incidence_matrix(item_count, contexts)
    global_matrix = global_incidence_matrix(item_count, contexts)
    if not local_matrix:
        return None
    local_width = len(local_matrix[0])
    for column in range(local_width):
        basis = tuple(Fraction(int(index == column)) for index in range(local_width))
        candidate = apply_matrix(local_matrix, basis)
        if not is_in_column_image(global_matrix, candidate):
            return candidate
    return None


def minimum_mixed_checks(item_count: int, contexts: Sequence[ContextGraph]) -> int:
    """Sharp number of independent checks conditional on local exactness."""
    return obstruction_dimensions(item_count, contexts)["mixed_cycle_rank"]


def fundamental_cycle_basis(
    item_count: int, edges: Sequence[Edge]
) -> tuple[Vector, ...]:
    """Return signed fundamental cycles in the supplied edge coordinates."""
    disjoint = DisjointSet(item_count)
    forest: list[list[tuple[int, int, int]]] = [[] for _ in range(item_count)]
    cycles = []
    for edge_index, (left, right) in enumerate(edges):
        if disjoint.union(left, right):
            # Sign +1 means traversal in the registered edge orientation.
            forest[left].append((right, edge_index, 1))
            forest[right].append((left, edge_index, -1))
            continue
        parents: dict[int, tuple[int, int, int] | None] = {right: None}
        queue = deque((right,))
        while queue and left not in parents:
            current = queue.popleft()
            for neighbor, tree_edge, sign in forest[current]:
                if neighbor in parents:
                    continue
                parents[neighbor] = (current, tree_edge, sign)
                queue.append(neighbor)
        if left not in parents:
            raise AssertionError("non-tree edge endpoints lack a forest path")
        cycle = [Fraction(0) for _ in edges]
        # Traverse the non-tree edge opposite its registered direction, then
        # follow the parent chain from left back to the root at right.
        cycle[edge_index] = Fraction(-1)
        current = left
        while current != right:
            parent = parents[current]
            if parent is None:
                raise AssertionError("broken parent chain")
            previous, tree_edge, sign_from_previous = parent
            # The recorded traversal is previous -> current; the cycle
            # returns current -> previous.
            cycle[tree_edge] = Fraction(-sign_from_previous)
            current = previous
        cycles.append(tuple(cycle))
    return tuple(cycles)


def local_cycle_basis(
    item_count: int, contexts: Sequence[ContextGraph]
) -> tuple[Vector, ...]:
    total_edges = sum(len(context.edges) for context in contexts)
    result = []
    offset = 0
    for context in contexts:
        for local_cycle in fundamental_cycle_basis(item_count, context.edges):
            embedded = [Fraction(0) for _ in range(total_edges)]
            embedded[offset : offset + len(context.edges)] = local_cycle
            result.append(tuple(embedded))
        offset += len(context.edges)
    return tuple(result)


def mixed_cycle_basis(
    item_count: int, contexts: Sequence[ContextGraph]
) -> tuple[Vector, ...]:
    """Extend local cycles to a basis of all labelled-union cycles."""
    validate_contexts(item_count, contexts)
    union_edges = tuple(edge for _, edge in labelled_edges(contexts))
    selected = list(local_cycle_basis(item_count, contexts))
    current_rank = matrix_rank(selected)
    mixed = []
    for cycle in fundamental_cycle_basis(item_count, union_edges):
        candidate_rank = matrix_rank((*selected, cycle))
        if candidate_rank > current_rank:
            selected.append(cycle)
            mixed.append(cycle)
            current_rank = candidate_rank
    expected = minimum_mixed_checks(item_count, contexts)
    if len(mixed) != expected:
        raise AssertionError(f"mixed basis has {len(mixed)} rows, expected {expected}")
    return tuple(mixed)


def cycle_circulations(
    flow: Sequence[object], cycles: Sequence[Sequence[object]]
) -> Vector:
    values = tuple(map(Fraction, flow))
    if any(len(cycle) != len(values) for cycle in cycles):
        raise ValueError("cycle and flow dimensions differ")
    return tuple(
        sum(Fraction(coefficient) * value for coefficient, value in zip(cycle, values))
        for cycle in cycles
    )


def shared_scalar_status(
    item_count: int,
    contexts: Sequence[ContextGraph],
    flow: Sequence[object],
) -> dict[str, object]:
    if not is_locally_scalar(item_count, contexts, flow):
        return {
            "status": "local_scalar_failed",
            "mixed_cycle_rank": minimum_mixed_checks(item_count, contexts),
            "mixed_circulations": (),
        }
    cycles = mixed_cycle_basis(item_count, contexts)
    circulations = cycle_circulations(flow, cycles)
    if not cycles:
        status = "shared_scalar_forced_by_design"
    elif any(value != 0 for value in circulations):
        status = "shared_scalar_refuted"
    else:
        status = "shared_scalar_verified"
    if (status != "shared_scalar_refuted") != has_shared_scalar(
        item_count, contexts, flow
    ):
        raise AssertionError("cycle decision and direct rank decision disagree")
    return {
        "status": status,
        "mixed_cycle_rank": len(cycles),
        "mixed_circulations": tuple(str(value) for value in circulations),
    }


def minimal_parallel_edge_witness() -> dict[str, object]:
    contexts = (
        ContextGraph("history_0", ((0, 1),)),
        ContextGraph("history_1", ((0, 1),)),
    )
    flow = (Fraction(0), Fraction(1))
    return {
        "item_count": 2,
        "contexts": contexts,
        "flow": flow,
        "locally_scalar": is_locally_scalar(2, contexts, flow),
        "shared_scalar": has_shared_scalar(2, contexts, flow),
        "dimensions": obstruction_dimensions(2, contexts),
    }
