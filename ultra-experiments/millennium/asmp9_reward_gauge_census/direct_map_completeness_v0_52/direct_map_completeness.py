"""Exact finite direct-map completeness for Buehler upper bounds.

This module is an ASMP-9 v0.52 development instrument.  It treats a monotone
subset-bound table as the primitive object.  For a finite outcome set X,
``bounds[S]`` is the largest registered risk level whose probability on S can
exceed alpha.  A direct report ``u`` is valid exactly when

    bounds[{x : u(x) < r}] < r

for every positive registered risk level r.

All calculations are finite and exact.  The central dominance result is a
classical Buehler-optimality corollary, not a novelty claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import permutations, product
from typing import Iterable, Sequence


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def _width_from_table(table: Sequence[object]) -> int:
    size = len(table)
    if size < 2 or size & (size - 1):
        raise ValueError("subset-bound table size must be a power of two")
    return size.bit_length() - 1


def validate_subset_bounds(
    table: Sequence[object],
) -> tuple[Q, ...]:
    """Validate a normalized monotone subset-bound table."""

    result = tuple(q(value) for value in table)
    width = _width_from_table(result)
    if result[0] != 0:
        raise ValueError("empty-set bound must equal zero")
    if any(value < 0 for value in result):
        raise ValueError("subset bounds must be nonnegative")
    for mask in range(1 << width):
        for index in range(width):
            bit = 1 << index
            if not mask & bit and result[mask] > result[mask | bit]:
                raise ValueError("subset-bound table is not monotone")
    return result


def monotone_tables(
    width: int,
    level_count: int,
) -> tuple[tuple[Q, ...], ...]:
    """Enumerate normalized monotone maps B_width -> {0,...,level_count-1}."""

    if not 1 <= width <= 4:
        raise ValueError("development enumeration width must be in [1,4]")
    if not 2 <= level_count <= 5:
        raise ValueError("development level count must be in [2,5]")
    size = 1 << width
    rows = []
    for tail in product(range(level_count), repeat=size - 1):
        table = (Q(0),) + tuple(Q(value) for value in tail)
        try:
            validate_subset_bounds(table)
        except ValueError:
            continue
        rows.append(table)
    return tuple(rows)


def direct_map_valid(
    table: Sequence[object],
    reports: Sequence[object],
    risk_levels: Sequence[object],
) -> bool:
    """Return whether a deterministic direct upper map has uniform coverage."""

    bounds = validate_subset_bounds(table)
    reports = tuple(q(value) for value in reports)
    levels = tuple(sorted(set(q(value) for value in risk_levels)))
    width = _width_from_table(bounds)
    if len(reports) != width:
        raise ValueError("report vector has wrong width")
    if not levels or levels[0] != 0:
        raise ValueError("risk levels must include zero")
    if any(value < 0 for value in reports):
        raise ValueError("reports must be nonnegative")

    for level in levels:
        if level <= 0:
            continue
        failure_mask = 0
        for index, report in enumerate(reports):
            if report < level:
                failure_mask |= 1 << index
        if bounds[failure_mask] >= level:
            return False
    return True


def consistent_orders(
    reports: Sequence[object],
) -> tuple[tuple[int, ...], ...]:
    """Return every total-order refinement of nondecreasing report value."""

    values = tuple(q(value) for value in reports)
    result = []
    for order in permutations(range(len(values))):
        if all(
            values[order[index]] <= values[order[index + 1]]
            for index in range(len(values) - 1)
        ):
            result.append(order)
    return tuple(result)


def buehler_map(
    table: Sequence[object],
    order: Sequence[int],
) -> tuple[Q, ...]:
    """Construct the direct Buehler map for one total outcome order."""

    bounds = validate_subset_bounds(table)
    width = _width_from_table(bounds)
    order = tuple(int(index) for index in order)
    if sorted(order) != list(range(width)):
        raise ValueError("order is not a permutation")
    result = [Q(0)] * width
    mask = 0
    for index in order:
        mask |= 1 << index
        result[index] = bounds[mask]
    return tuple(result)


@dataclass(frozen=True)
class DominanceCertificate:
    reports: tuple[Q, ...]
    order: tuple[int, ...]
    buehler_reports: tuple[Q, ...]
    input_valid: bool
    buehler_valid: bool
    pointwise_dominates: bool
    strict_coordinates: tuple[int, ...]


def dominance_certificate(
    table: Sequence[object],
    reports: Sequence[object],
    risk_levels: Sequence[object],
    order: Sequence[int],
) -> DominanceCertificate:
    """Certify Buehlerization of one report-sorted total order."""

    reports = tuple(q(value) for value in reports)
    order = tuple(int(index) for index in order)
    if order not in consistent_orders(reports):
        raise ValueError("order is not nondecreasing in report value")
    input_valid = direct_map_valid(table, reports, risk_levels)
    candidate = buehler_map(table, order)
    buehler_valid = direct_map_valid(table, candidate, risk_levels)
    pointwise = all(
        left <= right for left, right in zip(candidate, reports)
    )
    strict = tuple(
        index
        for index, (left, right) in enumerate(
            zip(candidate, reports)
        )
        if left < right
    )
    return DominanceCertificate(
        reports=reports,
        order=order,
        buehler_reports=candidate,
        input_valid=input_valid,
        buehler_valid=buehler_valid,
        pointwise_dominates=pointwise,
        strict_coordinates=strict,
    )


def weighted_cost(
    reports: Sequence[object],
    weights: Sequence[object],
) -> Q:
    reports = tuple(q(value) for value in reports)
    weights = tuple(q(value) for value in weights)
    if len(reports) != len(weights):
        raise ValueError("weights have wrong width")
    if any(value <= 0 for value in weights):
        raise ValueError("weights must be strictly positive")
    return sum(
        (report * weight for report, weight in zip(reports, weights)),
        Q(0),
    )


@dataclass(frozen=True)
class OptimumComparison:
    direct_value: Q
    buehler_value: Q
    direct_optimizers: tuple[tuple[Q, ...], ...]
    buehler_optimizers: tuple[tuple[Q, ...], ...]


def compare_global_optima(
    table: Sequence[object],
    report_alphabet: Sequence[object],
    risk_levels: Sequence[object],
    weights: Sequence[object],
) -> OptimumComparison:
    """Compare all valid direct maps with all outcome-order Buehler maps."""

    bounds = validate_subset_bounds(table)
    width = _width_from_table(bounds)
    alphabet = tuple(q(value) for value in report_alphabet)
    direct = tuple(
        tuple(values)
        for values in product(alphabet, repeat=width)
        if direct_map_valid(bounds, values, risk_levels)
    )
    if not direct:
        raise AssertionError("no valid direct map")
    buehler = tuple(
        dict.fromkeys(
            buehler_map(bounds, order)
            for order in permutations(range(width))
        )
    )
    direct_costs = {
        reports: weighted_cost(reports, weights)
        for reports in direct
    }
    buehler_costs = {
        reports: weighted_cost(reports, weights)
        for reports in buehler
    }
    direct_value = min(direct_costs.values())
    buehler_value = min(buehler_costs.values())
    return OptimumComparison(
        direct_value=direct_value,
        buehler_value=buehler_value,
        direct_optimizers=tuple(
            sorted(
                reports
                for reports, value in direct_costs.items()
                if value == direct_value
            )
        ),
        buehler_optimizers=tuple(
            sorted(
                reports
                for reports, value in buehler_costs.items()
                if value == buehler_value
            )
        ),
    )


def all_direct_maps(
    width: int,
    alphabet: Sequence[object],
) -> Iterable[tuple[Q, ...]]:
    values = tuple(q(value) for value in alphabet)
    return (
        tuple(row)
        for row in product(values, repeat=width)
    )


def minimal_controls() -> dict[str, object]:
    """Return an equality and a strict-dominance two-outcome control."""

    table = (Q(0), Q(1), Q(1), Q(2))
    levels = (Q(0), Q(1), Q(2))
    equality = dominance_certificate(
        table, (Q(1), Q(2)), levels, (0, 1)
    )
    strict = dominance_certificate(
        table, (Q(2), Q(2)), levels, (0, 1)
    )
    return {
        "table": table,
        "equality": equality,
        "strict": strict,
    }
