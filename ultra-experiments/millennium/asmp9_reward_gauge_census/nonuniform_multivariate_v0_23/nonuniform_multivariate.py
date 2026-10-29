"""Exact nonuniform local-design tools for ASMP-9 v0.23.

The probability model is the maximally noisy comparison channel.  Edge ``e``
receives ``n_e >= 1`` independent fair trials.  Its compressed state is

* ``ZERO`` with probability ``2**(-n_e)``;
* ``FULL`` with probability ``2**(-n_e)``; and
* ``INTERIOR`` with probability ``1 - 2**(1-n_e)``.

On a bridgeless comparison block, quotient liveness is strong connectivity of
the directed residual graph in which ``INTERIOR`` supplies both directions.
All arithmetic in this module is exact.
"""

from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Iterable, Sequence


Edge = tuple[int, int]
ZERO = 0
INTERIOR = 1
FULL = 2

K4_EDGES: tuple[Edge, ...] = (
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 3),
    (2, 3),
)
K4_LOW_EDGES = frozenset((0, 5))
K4_MIDDLE_EDGES = frozenset((1, 4))
K4_HIGH_EDGES = frozenset((2, 3))


def validate_connected_simple_graph(
    node_count: int, edges: Sequence[Edge]
) -> None:
    if node_count < 1:
        raise ValueError("node_count must be positive")
    if not edges:
        raise ValueError("at least one edge is required")
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
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


def validate_counts(edges: Sequence[Edge], counts: Sequence[int]) -> None:
    if len(edges) != len(counts):
        raise ValueError("edge/count dimensions differ")
    if any(not isinstance(count, int) or count < 1 for count in counts):
        raise ValueError("each trial count must be a positive integer")


def component_count(
    node_count: int,
    edges: Sequence[Edge],
    selected_indices: Iterable[int],
) -> int:
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for index in selected_indices:
        source, target = edges[index]
        adjacency[source].append(target)
        adjacency[target].append(source)
    seen: set[int] = set()
    result = 0
    for root in range(node_count):
        if root in seen:
            continue
        result += 1
        seen.add(root)
        stack = [root]
        while stack:
            node = stack.pop()
            for target in adjacency[node]:
                if target not in seen:
                    seen.add(target)
                    stack.append(target)
    return result


def multivariate_random_cluster(
    node_count: int,
    edges: Sequence[Edge],
    q: int | Fraction,
    edge_weights: Sequence[int | Fraction],
) -> Fraction:
    """Return ``Z_G(q,{v_e}) = sum_A q^k(A) prod_{e in A} v_e``."""

    validate_connected_simple_graph(node_count, edges)
    if len(edges) != len(edge_weights):
        raise ValueError("edge/weight dimensions differ")
    weights = tuple(Fraction(weight) for weight in edge_weights)
    q_value = Fraction(q)
    result = Fraction(0)
    for mask in range(1 << len(edges)):
        selected = tuple(
            index
            for index in range(len(edges))
            if (mask >> index) & 1
        )
        term = q_value ** component_count(
            node_count, edges, selected
        )
        for index in selected:
            term *= weights[index]
        result += term
    return result


def _reaches_all(
    adjacency: Sequence[Sequence[int]], root: int
) -> bool:
    reached = {root}
    stack = [root]
    while stack:
        node = stack.pop()
        for target in adjacency[node]:
            if target not in reached:
                reached.add(target)
                stack.append(target)
    return len(reached) == len(adjacency)


def status_is_strong(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[int],
) -> bool:
    if len(edges) != len(statuses):
        raise ValueError("edge/status dimensions differ")
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    reverse: list[list[int]] = [[] for _ in range(node_count)]
    for (source, target), status in zip(
        edges, statuses, strict=True
    ):
        if status not in (ZERO, INTERIOR, FULL):
            raise ValueError("invalid edge status")
        if status in (ZERO, INTERIOR):
            adjacency[source].append(target)
            reverse[target].append(source)
        if status in (INTERIOR, FULL):
            adjacency[target].append(source)
            reverse[source].append(target)
    return _reaches_all(adjacency, 0) and _reaches_all(reverse, 0)


def direct_nonuniform_availability(
    node_count: int,
    edges: Sequence[Edge],
    counts: Sequence[int],
) -> Fraction:
    """Enumerate all ternary edge states under heterogeneous counts."""

    validate_connected_simple_graph(node_count, edges)
    validate_counts(edges, counts)
    laws = tuple(
        (
            Fraction(1, 2**count),
            Fraction(1) - Fraction(2, 2**count),
            Fraction(1, 2**count),
        )
        for count in counts
    )
    result = Fraction(0)
    for statuses in itertools.product(
        (ZERO, INTERIOR, FULL), repeat=len(edges)
    ):
        if not status_is_strong(node_count, edges, statuses):
            continue
        mass = Fraction(1)
        for law, status in zip(laws, statuses, strict=True):
            mass *= law[status]
        result += mass
    return result


def multivariate_tutte_availability(
    node_count: int,
    edges: Sequence[Edge],
    counts: Sequence[int],
) -> Fraction:
    """Evaluate the edge-multivariate ``q=-1`` specialization.

    For ``z_e = 2**(-n_e)`` this returns

        -prod_e z_e * Z_G(-1, {z_e**(-1) - 1}).

    The identity is intended for connected bridgeless blocks.  Callers that
    need quotient treatment of bridges must factor the graph first, as in
    ASMP-9 v0.20.
    """

    validate_connected_simple_graph(node_count, edges)
    validate_counts(edges, counts)
    z_values = tuple(Fraction(1, 2**count) for count in counts)
    prefactor = Fraction(-1)
    for value in z_values:
        prefactor *= value
    return prefactor * multivariate_random_cluster(
        node_count,
        edges,
        -1,
        tuple(Fraction(1, value) - 1 for value in z_values),
    )


def oriented_completion_count(
    node_count: int,
    edges: Sequence[Edge],
    interior_edges: Iterable[int],
) -> int:
    """Count strong completions after fixing the INTERIOR edge set."""

    validate_connected_simple_graph(node_count, edges)
    interior = frozenset(interior_edges)
    if any(index < 0 or index >= len(edges) for index in interior):
        raise ValueError("interior edge outside edge universe")
    oriented = tuple(
        index for index in range(len(edges)) if index not in interior
    )
    result = 0
    for directions in itertools.product((ZERO, FULL), repeat=len(oriented)):
        statuses = [INTERIOR] * len(edges)
        for index, direction in zip(
            oriented, directions, strict=True
        ):
            statuses[index] = direction
        result += status_is_strong(node_count, edges, statuses)
    return result


def multivariate_coefficient(
    node_count: int,
    edges: Sequence[Edge],
    interior_edges: Iterable[int],
) -> int:
    """Coefficient from the spanning-subgraph expansion.

    In

        -prod_e k_e Z_G(-1,{1+l_e/k_e}),

    the coefficient of ``prod_{e in B} l_e prod_{e not in B} k_e`` is

        -sum_{A superset B} (-1)^k(A).

    It equals the number of strong oriented completions with precisely the
    edges in ``B`` bidirected.
    """

    validate_connected_simple_graph(node_count, edges)
    interior = frozenset(interior_edges)
    if any(index < 0 or index >= len(edges) for index in interior):
        raise ValueError("interior edge outside edge universe")
    result = 0
    for mask in range(1 << len(edges)):
        selected = frozenset(
            index
            for index in range(len(edges))
            if (mask >> index) & 1
        )
        if not interior.issubset(selected):
            continue
        result -= (-1) ** component_count(
            node_count, edges, selected
        )
    return result


def uniform_backman_availability(
    node_count: int,
    edges: Sequence[Edge],
    trial_count: int,
) -> Fraction:
    """Uniform specialization written with the ordinary Tutte polynomial."""

    if trial_count < 1:
        raise ValueError("trial_count must be positive")
    validate_connected_simple_graph(node_count, edges)
    z = Fraction(1, 2**trial_count)
    x_value = (1 - 2 * z) / (1 - z)
    y_value = 1 / z
    genus = len(edges) - node_count + 1
    graph_components = 1
    tutte = Fraction(0)
    for mask in range(1 << len(edges)):
        selected = tuple(
            index
            for index in range(len(edges))
            if (mask >> index) & 1
        )
        components = component_count(node_count, edges, selected)
        selected_count = len(selected)
        tutte += (x_value - 1) ** (
            components - graph_components
        ) * (y_value - 1) ** (
            selected_count - node_count + components
        )
    return (1 - z) ** (node_count - 1) * z**genus * tutte


def trial_numerator(
    node_count: int,
    edges: Sequence[Edge],
    counts: Sequence[int],
) -> int:
    """Return the integer numerator over the common denominator ``2^N``."""

    value = multivariate_tutte_availability(
        node_count, edges, counts
    )
    denominator = 2 ** sum(counts)
    scaled = value * denominator
    if scaled.denominator != 1:
        raise AssertionError("common-denominator numerator is not integral")
    return scaled.numerator


def one_unit_exchange_neighbors(
    counts: Sequence[int], floor: int = 1
) -> tuple[tuple[int, int, tuple[int, ...]], ...]:
    """Enumerate ordered donor/recipient exchanges at fixed total count."""

    if floor < 0:
        raise ValueError("floor must be nonnegative")
    if any(count < floor for count in counts):
        raise ValueError("count below floor")
    result: list[tuple[int, int, tuple[int, ...]]] = []
    for donor in range(len(counts)):
        if counts[donor] <= floor:
            continue
        for recipient in range(len(counts)):
            if recipient == donor:
                continue
            neighbor = list(counts)
            neighbor[donor] -= 1
            neighbor[recipient] += 1
            result.append((donor, recipient, tuple(neighbor)))
    return tuple(result)


def k4_trap_counts(s: int) -> tuple[int, ...]:
    """The K4 strict-local/suboptimal family at total count ``6s``."""

    if s < 2:
        raise ValueError("s must be at least 2")
    return (s - 1, s, s + 1, s + 1, s, s - 1)


def k4_balanced_counts(s: int) -> tuple[int, ...]:
    if s < 1:
        raise ValueError("s must be positive")
    return (s,) * len(K4_EDGES)


def k4_opposite_pair_numerator(x: int, y: int, w: int) -> int:
    """Closed form when the three opposite K4 edge pairs share powers.

    ``x``, ``y``, and ``w`` are the values ``2**n`` on the edge pairs
    ``(01,23)``, ``(02,13)``, and ``(03,12)`` respectively.
    """

    if min(x, y, w) < 1:
        raise ValueError("edge powers must be positive")
    return (
        (x * y * w) ** 2
        - 2 * (x * x + y * y + w * w)
        - 8 * x * y * w
        + 12 * (x + y + w)
        - 24
    )


def k4_trap_closed_form(t: int) -> int:
    if t % 2 or t < 4:
        raise ValueError("t must be an even integer at least 4")
    return (
        2 * t**6 - 16 * t**3 - 21 * t**2 + 84 * t - 48
    ) // 2


def k4_balanced_closed_form(t: int) -> int:
    if t < 2:
        raise ValueError("t must be at least 2")
    return t**6 - 8 * t**3 - 6 * t**2 + 36 * t - 24


def k4_balanced_minus_trap_gap(t: int) -> int:
    if t % 2 or t < 4:
        raise ValueError("t must be an even integer at least 4")
    return 3 * t * (3 * t - 4) // 2


def _k4_level(edge_index: int) -> str:
    if edge_index in K4_LOW_EDGES:
        return "low"
    if edge_index in K4_MIDDLE_EDGES:
        return "middle"
    if edge_index in K4_HIGH_EDGES:
        return "high"
    raise ValueError("edge index outside K4")


def k4_neighbor_gap_certificate(
    donor: int, recipient: int, t: int
) -> tuple[str, int]:
    """Return the factor class and certified trap-minus-neighbor gap."""

    if donor == recipient:
        raise ValueError("donor and recipient must differ")
    if t % 4 or t < 4:
        raise ValueError("t must be divisible by 4 and at least 4")
    pair = (_k4_level(donor), _k4_level(recipient))
    values = {
        ("low", "middle"): t * (4 * t**2 + 7 * t - 18) // 4,
        ("low", "high"): t * (4 * t**2 + 31 * t - 42) // 4,
        ("low", "low"): t * (4 * t**2 - 3) // 2,
        ("middle", "low"): t**2 * (2 * t - 1) // 2,
        ("middle", "high"): t * (t**2 + 7 * t - 9),
        ("middle", "middle"): t * (2 * t**2 - 3),
        ("high", "low"): t * (t - 2) * (2 * t - 3) // 2,
        ("high", "middle"): t**2 * (t - 2),
        ("high", "high"): 2 * t * (t**2 - 3),
    }
    return f"{pair[0]}_to_{pair[1]}", values[pair]


def k4_m_concavity_deficit(t: int) -> int:
    """Positive deficit in the M-concavity exchange axiom.

    Take ``x`` to be the trap, ``y`` to be the balanced allocation, choose
    a high edge ``i`` with ``x_i > y_i`` and either low edge ``j`` with
    ``x_j < y_j``.  M-concavity would require at least one exchange with

        f(x)+f(y) <= f(x-e_i+e_j)+f(y+e_i-e_j).

    The returned quantity is the left side minus the right side, and is
    strictly positive for every ``t=2**s``, ``s>=2``.
    """

    if t % 2 or t < 4:
        raise ValueError("t must be an even integer at least 4")
    return t**2 * (4 * t - 5) // 2
