"""Exact common-chain and ordering-gauge certificates.

Development-only ASMP-9 v0.49 instrument.  The functions operate on arbitrary
finite subset-bound tables; they do not assume that a table came from a valid
statistical experiment.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from math import factorial
from typing import Sequence


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def _validated(
    bounds: Sequence[object],
    weights: Sequence[object],
) -> tuple[tuple[Q, ...], tuple[Q, ...]]:
    bounds = tuple(q(value) for value in bounds)
    weights = tuple(q(value) for value in weights)
    width = len(weights)
    if not weights or width > 20:
        raise ValueError("outcome width must be in [1,20]")
    if any(value <= 0 for value in weights):
        raise ValueError("reference weights must be positive")
    if len(bounds) != 1 << width:
        raise ValueError("subset-bound table has wrong width")
    return bounds, weights


def finite_buehler_subset_bounds(
    risks: Sequence[object],
    probability_rows: Sequence[Sequence[object]],
    alpha: object,
) -> tuple[Q, ...]:
    """Construct an exact finite Buehler subset table."""

    risks = tuple(q(value) for value in risks)
    rows = tuple(
        tuple(q(value) for value in row)
        for row in probability_rows
    )
    alpha = q(alpha)
    if not risks or len(risks) != len(rows):
        raise ValueError("risk and parameter rows differ")
    widths = {len(row) for row in rows}
    if len(widths) != 1:
        raise ValueError("probability rows have different widths")
    width = next(iter(widths))
    if not 0 < alpha < 1 or not 1 <= width <= 20:
        raise ValueError("invalid alpha or outcome width")
    if any(
        any(value < 0 for value in row) or sum(row, Q(0)) != 1
        for row in rows
    ):
        raise ValueError("invalid probability row")
    result = []
    for mask in range(1 << width):
        eligible = []
        for risk, row in zip(risks, rows):
            probability = sum(
                (
                    row[index]
                    for index in range(width)
                    if mask & (1 << index)
                ),
                Q(0),
            )
            if probability > alpha:
                eligible.append(risk)
        result.append(max(eligible, default=Q(0)))
    return tuple(result)


@dataclass(frozen=True)
class TightDAG:
    values: tuple[Q, ...]
    predecessor_bits: tuple[tuple[int, ...], ...]
    optimizer_counts: tuple[int, ...]


def tight_predecessor_dag(
    bounds: Sequence[object],
    weights: Sequence[object],
) -> TightDAG:
    """Return exact Bellman values and all tight predecessor choices."""

    bounds, weights = _validated(bounds, weights)
    size = len(bounds)
    values = [Q(0)] * size
    predecessors: list[tuple[int, ...]] = [tuple()] * size
    counts = [0] * size
    counts[0] = 1
    for mask in range(1, size):
        candidates: list[tuple[Q, int]] = []
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            index = bit.bit_length() - 1
            previous = mask ^ bit
            value = values[previous] + weights[index] * bounds[mask]
            candidates.append((value, bit))
            remaining ^= bit
        best = min(value for value, _ in candidates)
        tight = tuple(
            bit for value, bit in candidates if value == best
        )
        values[mask] = best
        predecessors[mask] = tight
        counts[mask] = sum(counts[mask ^ bit] for bit in tight)
    return TightDAG(
        values=tuple(values),
        predecessor_bits=tuple(predecessors),
        optimizer_counts=tuple(counts),
    )


@dataclass(frozen=True)
class CommonChainCertificate:
    outcome_count: int
    order_count: int
    first_optimizer_count: int
    second_optimizer_count: int
    common_optimizer_count: int
    common_optimizer_exists: bool
    lexicographic_common_order: tuple[int, ...] | None
    reachable_masks: tuple[int, ...]
    boundary: tuple[dict[str, object], ...]


def common_chain_certificate(
    first_bounds: Sequence[object],
    second_bounds: Sequence[object],
    weights: Sequence[object],
) -> CommonChainCertificate:
    """Characterize common optimality by intersecting tight DAGs."""

    first_bounds, weights = _validated(first_bounds, weights)
    second_bounds, second_weights = _validated(second_bounds, weights)
    if weights != second_weights:
        raise AssertionError("weight validation changed values")
    first = tight_predecessor_dag(first_bounds, weights)
    second = tight_predecessor_dag(second_bounds, weights)
    size = len(first_bounds)
    reachable = [False] * size
    counts = [0] * size
    lex: list[tuple[int, ...] | None] = [None] * size
    reachable[0] = True
    counts[0] = 1
    lex[0] = tuple()
    for mask in range(1, size):
        common_bits = set(
            first.predecessor_bits[mask]
        ).intersection(second.predecessor_bits[mask])
        candidates = []
        for bit in common_bits:
            previous = mask ^ bit
            if not reachable[previous]:
                continue
            index = bit.bit_length() - 1
            prior = lex[previous]
            if prior is None:
                raise AssertionError("reachable prefix lacks an order")
            candidates.append(prior + (index,))
            counts[mask] += counts[previous]
        if candidates:
            reachable[mask] = True
            lex[mask] = min(candidates)

    boundary = []
    for previous in range(size):
        if not reachable[previous]:
            continue
        for index in range(len(weights)):
            bit = 1 << index
            if previous & bit:
                continue
            mask = previous | bit
            if reachable[mask]:
                continue
            blocked = []
            if bit not in first.predecessor_bits[mask]:
                blocked.append("first")
            if bit not in second.predecessor_bits[mask]:
                blocked.append("second")
            if not blocked:
                raise AssertionError(
                    "common-tight edge failed reachability"
                )
            boundary.append(
                {
                    "from_mask": previous,
                    "to_mask": mask,
                    "added_index": index,
                    "blocked_by": tuple(blocked),
                }
            )

    full = size - 1
    return CommonChainCertificate(
        outcome_count=len(weights),
        order_count=factorial(len(weights)),
        first_optimizer_count=first.optimizer_counts[full],
        second_optimizer_count=second.optimizer_counts[full],
        common_optimizer_count=counts[full],
        common_optimizer_exists=reachable[full],
        lexicographic_common_order=lex[full],
        reachable_masks=tuple(
            mask for mask, value in enumerate(reachable) if value
        ),
        boundary=tuple(boundary),
    )


def square_curls(
    perturbation: Sequence[object],
    weights: Sequence[object],
) -> tuple[dict[str, object], ...]:
    """Return every nonzero square curl of the induced edge one-form."""

    perturbation, weights = _validated(perturbation, weights)
    width = len(weights)
    result = []
    for base in range(1 << width):
        missing = [
            index
            for index in range(width)
            if not base & (1 << index)
        ]
        for offset, first in enumerate(missing):
            for second in missing[offset + 1 :]:
                first_bit = 1 << first
                second_bit = 1 << second
                first_mask = base | first_bit
                second_mask = base | second_bit
                joint = first_mask | second_bit
                curl = (
                    weights[first] * perturbation[first_mask]
                    + weights[second] * perturbation[joint]
                    - weights[second] * perturbation[second_mask]
                    - weights[first] * perturbation[joint]
                )
                if curl:
                    result.append(
                        {
                            "base_mask": base,
                            "first_index": first,
                            "second_index": second,
                            "curl": curl,
                        }
                    )
    return tuple(result)


@dataclass(frozen=True)
class OrderingGaugeCertificate:
    scale: Q
    valid: bool
    potential: tuple[Q, ...] | None
    additive_constant: Q | None
    nonzero_curls: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class GaugeScaleCompatibility:
    status: str
    unique_scale: Q | None
    distinct_required_scales: tuple[Q, ...]
    zero_denominator_conflicts: int


def ordering_gauge_scale_compatibility(
    first_bounds: Sequence[object],
    second_bounds: Sequence[object],
    weights: Sequence[object],
) -> GaugeScaleCompatibility:
    """Decide whether any positive scale can make the difference exact."""

    first_bounds, weights = _validated(first_bounds, weights)
    second_bounds, _ = _validated(second_bounds, weights)
    width = len(weights)
    ratios = set()
    conflicts = 0
    for base in range(1 << width):
        missing = [
            index
            for index in range(width)
            if not base & (1 << index)
        ]
        for offset, first in enumerate(missing):
            for second in missing[offset + 1 :]:
                first_bit = 1 << first
                second_bit = 1 << second
                first_mask = base | first_bit
                second_mask = base | second_bit
                joint = first_mask | second_bit

                def curl(table: tuple[Q, ...]) -> Q:
                    return (
                        weights[first] * table[first_mask]
                        + weights[second] * table[joint]
                        - weights[second] * table[second_mask]
                        - weights[first] * table[joint]
                    )

                first_curl = curl(first_bounds)
                second_curl = curl(second_bounds)
                if not first_curl:
                    if second_curl:
                        conflicts += 1
                else:
                    ratios.add(second_curl / first_curl)
    ordered = tuple(sorted(ratios))
    if conflicts:
        status = "no_positive_scale"
        scale = None
    elif not ordered:
        status = "every_positive_scale"
        scale = None
    elif len(ordered) == 1 and ordered[0] > 0:
        status = "unique_positive_scale"
        scale = ordered[0]
    else:
        status = "no_positive_scale"
        scale = None
    return GaugeScaleCompatibility(
        status=status,
        unique_scale=scale,
        distinct_required_scales=ordered,
        zero_denominator_conflicts=conflicts,
    )


def ordering_gauge_certificate(
    first_bounds: Sequence[object],
    second_bounds: Sequence[object],
    weights: Sequence[object],
    scale: object,
) -> OrderingGaugeCertificate:
    """Certify affine equality of every ordering cost."""

    first_bounds, weights = _validated(first_bounds, weights)
    second_bounds, _ = _validated(second_bounds, weights)
    scale = q(scale)
    if scale <= 0:
        raise ValueError("scale must be positive")
    perturbation = tuple(
        second - scale * first
        for first, second in zip(first_bounds, second_bounds)
    )
    curls = square_curls(perturbation, weights)
    if curls:
        return OrderingGaugeCertificate(
            scale=scale,
            valid=False,
            potential=None,
            additive_constant=None,
            nonzero_curls=curls,
        )

    potential = [Q(0)] * len(perturbation)
    for mask in range(1, len(perturbation)):
        bit = mask & -mask
        index = bit.bit_length() - 1
        previous = mask ^ bit
        potential[mask] = (
            potential[previous]
            + weights[index] * perturbation[mask]
        )
        remaining = mask
        while remaining:
            check_bit = remaining & -remaining
            check_index = check_bit.bit_length() - 1
            check_previous = mask ^ check_bit
            expected = (
                potential[check_previous]
                + weights[check_index] * perturbation[mask]
            )
            if expected != potential[mask]:
                raise AssertionError("zero curl failed path independence")
            remaining ^= check_bit
    return OrderingGaugeCertificate(
        scale=scale,
        valid=True,
        potential=tuple(potential),
        additive_constant=potential[-1],
        nonzero_curls=tuple(),
    )
