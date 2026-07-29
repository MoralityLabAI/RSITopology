"""Exact reference-weight robustness for finite evidence orderings.

Development-only ASMP-9 v0.50 instrument.  A reference-law family is supplied
by rational probability vectors whose convex hull is the uncertainty
polytope.  Every certificate is exact.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import permutations
from math import factorial
from typing import Sequence


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def _validate_tables(
    bound_tables: Sequence[Sequence[object]],
) -> tuple[tuple[Q, ...], ...]:
    tables = tuple(
        tuple(q(value) for value in table)
        for table in bound_tables
    )
    if not tables:
        raise ValueError("at least one decision objective is required")
    sizes = {len(table) for table in tables}
    if len(sizes) != 1:
        raise ValueError("bound tables have different sizes")
    size = next(iter(sizes))
    if size < 2 or size & (size - 1):
        raise ValueError("bound-table size must be a power of two")
    width = size.bit_length() - 1
    if width > 20:
        raise ValueError("outcome width exceeds exact DP cap")
    return tables


def _validate_vertices(
    vertices: Sequence[Sequence[object]],
    width: int,
) -> tuple[tuple[Q, ...], ...]:
    result = tuple(
        tuple(q(value) for value in vertex)
        for vertex in vertices
    )
    if not result:
        raise ValueError("at least one reference vertex is required")
    for vertex in result:
        if len(vertex) != width:
            raise ValueError("reference vertex has wrong width")
        if any(value <= 0 for value in vertex):
            raise ValueError("reference weights must be strictly positive")
        if sum(vertex, Q(0)) != 1:
            raise ValueError("reference weights must sum to one")
    return result


def ordering_feature_vector(
    ordering: Sequence[int],
    bounds: Sequence[object],
) -> tuple[Q, ...]:
    """Coefficient of each reference weight in one ordering cost."""

    bounds = tuple(q(value) for value in bounds)
    ordering = tuple(int(index) for index in ordering)
    width = len(ordering)
    if sorted(ordering) != list(range(width)):
        raise ValueError("ordering is not a permutation")
    if len(bounds) != 1 << width:
        raise ValueError("bound table has wrong width")
    result = [Q(0)] * width
    mask = 0
    for index in ordering:
        mask |= 1 << index
        result[index] = bounds[mask]
    return tuple(result)


def ordering_cost(
    ordering: Sequence[int],
    bounds: Sequence[object],
    weights: Sequence[object],
) -> Q:
    feature = ordering_feature_vector(ordering, bounds)
    weights = tuple(q(value) for value in weights)
    if len(feature) != len(weights):
        raise ValueError("weight vector has wrong width")
    return sum(
        (weight * value for weight, value in zip(weights, feature)),
        Q(0),
    )


@dataclass(frozen=True)
class _TightDAG:
    value: Q
    predecessor_bits: tuple[tuple[int, ...], ...]
    optimizer_count: int


def _tight_dag(
    bounds: tuple[Q, ...],
    weights: tuple[Q, ...],
) -> _TightDAG:
    values = [Q(0)] * len(bounds)
    predecessors: list[tuple[int, ...]] = [tuple()] * len(bounds)
    counts = [0] * len(bounds)
    counts[0] = 1
    for mask in range(1, len(bounds)):
        candidates = []
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            index = bit.bit_length() - 1
            previous = mask ^ bit
            candidates.append(
                (
                    values[previous] + weights[index] * bounds[mask],
                    bit,
                )
            )
            remaining ^= bit
        best = min(value for value, _ in candidates)
        tight = tuple(
            bit for value, bit in candidates if value == best
        )
        values[mask] = best
        predecessors[mask] = tight
        counts[mask] = sum(counts[mask ^ bit] for bit in tight)
    return _TightDAG(
        value=values[-1],
        predecessor_bits=tuple(predecessors),
        optimizer_count=counts[-1],
    )


@dataclass(frozen=True)
class RobustChainCertificate:
    objective_count: int
    reference_vertex_count: int
    outcome_count: int
    order_count: int
    scenario_optimizer_counts: tuple[tuple[int, ...], ...]
    robust_optimizer_count: int
    robust_optimizer_exists: bool
    lexicographic_robust_order: tuple[int, ...] | None
    reachable_masks: tuple[int, ...]
    boundary: tuple[dict[str, object], ...]


def robust_chain_certificate(
    bound_tables: Sequence[Sequence[object]],
    reference_vertices: Sequence[Sequence[object]],
) -> RobustChainCertificate:
    """Intersect tight DAGs over all objectives and reference vertices."""

    tables = _validate_tables(bound_tables)
    width = len(tables[0]).bit_length() - 1
    vertices = _validate_vertices(reference_vertices, width)
    dags = tuple(
        tuple(_tight_dag(table, vertex) for vertex in vertices)
        for table in tables
    )
    size = len(tables[0])
    reachable = [False] * size
    counts = [0] * size
    lex: list[tuple[int, ...] | None] = [None] * size
    reachable[0] = True
    counts[0] = 1
    lex[0] = tuple()

    for mask in range(1, size):
        common_bits: set[int] | None = None
        for objective_dags in dags:
            for dag in objective_dags:
                bits = set(dag.predecessor_bits[mask])
                common_bits = (
                    bits
                    if common_bits is None
                    else common_bits.intersection(bits)
                )
        candidates = []
        for bit in common_bits or set():
            previous = mask ^ bit
            if not reachable[previous]:
                continue
            prior = lex[previous]
            if prior is None:
                raise AssertionError("reachable prefix lacks an order")
            index = bit.bit_length() - 1
            candidates.append(prior + (index,))
            counts[mask] += counts[previous]
        if candidates:
            reachable[mask] = True
            lex[mask] = min(candidates)

    boundary = []
    for previous in range(size):
        if not reachable[previous]:
            continue
        for index in range(width):
            bit = 1 << index
            if previous & bit:
                continue
            mask = previous | bit
            if reachable[mask]:
                continue
            blocked = []
            for objective_index, objective_dags in enumerate(dags):
                for vertex_index, dag in enumerate(objective_dags):
                    if bit not in dag.predecessor_bits[mask]:
                        blocked.append((objective_index, vertex_index))
            if not blocked:
                raise AssertionError(
                    "common-tight edge failed reachability"
                )
            boundary.append(
                {
                    "from_mask": previous,
                    "to_mask": mask,
                    "added_index": index,
                    "blocked_scenarios": tuple(blocked),
                }
            )

    full = size - 1
    return RobustChainCertificate(
        objective_count=len(tables),
        reference_vertex_count=len(vertices),
        outcome_count=width,
        order_count=factorial(width),
        scenario_optimizer_counts=tuple(
            tuple(dag.optimizer_count for dag in objective_dags)
            for objective_dags in dags
        ),
        robust_optimizer_count=counts[full],
        robust_optimizer_exists=reachable[full],
        lexicographic_robust_order=lex[full],
        reachable_masks=tuple(
            mask for mask, value in enumerate(reachable) if value
        ),
        boundary=tuple(boundary),
    )


@dataclass(frozen=True)
class WeightHalfspace:
    objective_index: int
    competitor_order: tuple[int, ...]
    coefficients: tuple[Q, ...]


@dataclass(frozen=True)
class OrderingWeightRegion:
    ordering: tuple[int, ...]
    halfspaces: tuple[WeightHalfspace, ...]


def ordering_weight_region(
    ordering: Sequence[int],
    bound_tables: Sequence[Sequence[object]],
) -> OrderingWeightRegion:
    """Return exact halfspaces where one ordering is jointly optimal.

    The region is intersected with the positive probability simplex by the
    caller.  Exhaustive inequality generation is capped at nine outcomes.
    """

    tables = _validate_tables(bound_tables)
    ordering = tuple(int(index) for index in ordering)
    width = len(tables[0]).bit_length() - 1
    if sorted(ordering) != list(range(width)):
        raise ValueError("ordering is not a permutation")
    if width > 9:
        raise ValueError("explicit region enumeration is capped at width 9")

    rows = []
    seen = set()
    for objective_index, table in enumerate(tables):
        chosen = ordering_feature_vector(ordering, table)
        for competitor in permutations(range(width)):
            if competitor == ordering:
                continue
            other = ordering_feature_vector(competitor, table)
            coefficients = tuple(
                left - right for left, right in zip(chosen, other)
            )
            key = (objective_index, coefficients)
            if not any(coefficients) or key in seen:
                continue
            seen.add(key)
            rows.append(
                WeightHalfspace(
                    objective_index=objective_index,
                    competitor_order=competitor,
                    coefficients=coefficients,
                )
            )
    return OrderingWeightRegion(
        ordering=ordering,
        halfspaces=tuple(rows),
    )


def weight_region_contains(
    region: OrderingWeightRegion,
    weights: Sequence[object],
) -> bool:
    weights = tuple(q(value) for value in weights)
    if len(weights) != len(region.ordering):
        raise ValueError("weight vector has wrong width")
    return all(
        sum(
            (
                coefficient * weight
                for coefficient, weight in zip(
                    row.coefficients, weights
                )
            ),
            Q(0),
        )
        <= 0
        for row in region.halfspaces
    )


@dataclass(frozen=True)
class MinimaxRegretCertificate:
    optimum: Q
    optimizer_count: int
    lexicographic_order: tuple[int, ...]
    witness_objective: int
    witness_vertex: int
    witness_competitor: tuple[int, ...]


def minimax_regret_certificate(
    bound_tables: Sequence[Sequence[object]],
    reference_vertices: Sequence[Sequence[object]],
) -> MinimaxRegretCertificate:
    """Minimize worst objective/vertex regret by exhaustive ordering.

    This companion diagnostic is intentionally capped at nine outcomes.  The
    zero-regret existence question is handled without permutation enumeration
    by :func:`robust_chain_certificate`.
    """

    tables = _validate_tables(bound_tables)
    width = len(tables[0]).bit_length() - 1
    vertices = _validate_vertices(reference_vertices, width)
    if width > 9:
        raise ValueError("minimax regret enumeration is capped at width 9")
    orders = tuple(permutations(range(width)))
    scenario_optima = {}
    for objective_index, table in enumerate(tables):
        for vertex_index, vertex in enumerate(vertices):
            scenario_optima[(objective_index, vertex_index)] = min(
                ordering_cost(order, table, vertex) for order in orders
            )

    rows = []
    for order in orders:
        regret_rows = []
        for objective_index, table in enumerate(tables):
            for vertex_index, vertex in enumerate(vertices):
                optimum = scenario_optima[
                    (objective_index, vertex_index)
                ]
                value = ordering_cost(order, table, vertex)
                regret = value - optimum
                competitors = tuple(
                    candidate
                    for candidate in orders
                    if ordering_cost(candidate, table, vertex) == optimum
                )
                regret_rows.append(
                    (
                        regret,
                        objective_index,
                        vertex_index,
                        min(competitors),
                    )
                )
        worst = max(regret_rows)
        rows.append((worst[0], order, worst))
    optimum = min(value for value, _, _ in rows)
    optimizers = [row for row in rows if row[0] == optimum]
    _, order, worst = min(optimizers, key=lambda row: row[1])
    return MinimaxRegretCertificate(
        optimum=optimum,
        optimizer_count=len(optimizers),
        lexicographic_order=order,
        witness_objective=worst[1],
        witness_vertex=worst[2],
        witness_competitor=worst[3],
    )


def minimal_reference_switch_witness() -> dict[str, object]:
    """Smallest one-objective reference-law sensitivity witness."""

    bounds = (Q(0), Q(0), Q(0), Q(1))
    vertices = (
        (Q(3, 4), Q(1, 4)),
        (Q(1, 4), Q(3, 4)),
    )
    robust = robust_chain_certificate((bounds,), vertices)
    regret = minimax_regret_certificate((bounds,), vertices)
    return {
        "bounds": bounds,
        "vertices": vertices,
        "robust_optimizer_count": robust.robust_optimizer_count,
        "boundary": robust.boundary,
        "minimax_regret": regret.optimum,
        "minimax_optimizer_count": regret.optimizer_count,
    }
