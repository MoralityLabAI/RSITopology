"""Offset-calibrated preference access for the ASMP-9 v0.26 theorem seed."""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Iterable, Sequence


def _sign(value: Fraction) -> int:
    return (value > 0) - (value < 0)


def ceil_log2_fraction(value: Fraction) -> int:
    """Return ceil(log2(value)) for a positive rational, clipped below at zero."""
    value = Fraction(value)
    if value <= 0:
        raise ValueError("value must be positive")
    if value <= 1:
        return 0
    power = Fraction(1)
    exponent = 0
    while power < value:
        power *= 2
        exponent += 1
    return exponent


def midpoint_sign(gap: Fraction, offset: Fraction) -> int:
    """Population sign of P(prefer shifted item)-1/2 for any admissible link."""
    return _sign(Fraction(gap) + Fraction(offset))


@dataclass(frozen=True)
class BisectionReceipt:
    gap: Fraction
    estimate: Fraction
    lower: Fraction
    upper: Fraction
    query_count: int
    transcript: tuple[tuple[Fraction, int], ...]

    @property
    def absolute_error(self) -> Fraction:
        return abs(self.estimate - self.gap)


def population_bisection(
    gap: Fraction,
    radius: Fraction,
    tolerance: Fraction,
) -> BisectionReceipt:
    """Recover one anchored utility gap from exact midpoint-sign queries."""
    gap = Fraction(gap)
    radius = Fraction(radius)
    tolerance = Fraction(tolerance)
    if radius <= 0 or tolerance <= 0:
        raise ValueError("radius and tolerance must be positive")
    if not -radius <= gap <= radius:
        raise ValueError("gap lies outside the registered radius")

    rounds = ceil_log2_fraction(radius / tolerance)
    lower, upper = -radius, radius
    transcript: list[tuple[Fraction, int]] = []
    for _ in range(rounds):
        midpoint = (lower + upper) / 2
        offset = -midpoint
        outcome = midpoint_sign(gap, offset)
        transcript.append((offset, outcome))
        if outcome == 0:
            lower = upper = midpoint
            break
        if outcome > 0:
            lower = midpoint
        else:
            upper = midpoint

    estimate = (lower + upper) / 2
    return BisectionReceipt(
        gap=gap,
        estimate=estimate,
        lower=lower,
        upper=upper,
        query_count=len(transcript),
        transcript=tuple(transcript),
    )


def reconstruct_anchored_utility(
    gaps: Sequence[Fraction],
    radius: Fraction,
    tolerance: Fraction,
) -> tuple[BisectionReceipt, ...]:
    """Recover u_i-u_0 independently using a star rooted at item zero."""
    return tuple(
        population_bisection(gap, radius, tolerance) for gap in gaps
    )


def population_query_upper_bound(
    dimension: int,
    radius: Fraction,
    tolerance: Fraction,
) -> int:
    if dimension < 0:
        raise ValueError("dimension must be nonnegative")
    return dimension * ceil_log2_fraction(Fraction(radius) / tolerance)


def volume_query_lower_bound(
    dimension: int,
    radius: Fraction,
    tolerance: Fraction,
) -> int:
    """Metric-entropy lower bound for coordinate-threshold access.

    Tie leaves have zero volume and cannot improve a uniform continuum
    guarantee. Every non-tie query contributes one binary split.
    """
    if dimension < 0:
        raise ValueError("dimension must be nonnegative")
    ratio = Fraction(radius) / Fraction(tolerance)
    if ratio <= 0:
        raise ValueError("radius and tolerance must be positive")
    return ceil_log2_fraction(ratio**dimension)


def restricted_offset_witness(
    radius: Fraction,
    maximum_offset: Fraction,
) -> tuple[Fraction, Fraction]:
    """Two separated gaps indistinguishable under |offset| <= maximum_offset."""
    radius = Fraction(radius)
    maximum_offset = Fraction(maximum_offset)
    if not 0 <= maximum_offset < radius:
        raise ValueError("require 0 <= maximum_offset < radius")
    first = (radius + maximum_offset) / 2
    second = radius
    return first, second


def restricted_transcript(
    gap: Fraction,
    offsets: Iterable[Fraction],
) -> tuple[int, ...]:
    return tuple(midpoint_sign(gap, offset) for offset in offsets)


def rational_symmetric_link(value: Fraction) -> Fraction:
    """Strictly increasing symmetric link with exact rational evaluations."""
    value = Fraction(value)
    if value < 0:
        return 1 - rational_symmetric_link(-value)
    return Fraction(1, 2) + value / (2 * (1 + value))


def rational_link_margin_constant(radius: Fraction) -> Fraction:
    """Linear margin constant valid for arguments in [-2*radius, 2*radius]."""
    radius = Fraction(radius)
    if radius <= 0:
        raise ValueError("radius must be positive")
    return Fraction(1, 2 * (1 + 2 * radius))


def flat_link_sup_deviation(radius: Fraction, scale: Fraction) -> Fraction:
    """Sup |F_scale(x)-1/2| on x in [-2B,2B] for the scaled rational link."""
    radius = Fraction(radius)
    scale = Fraction(scale)
    if radius <= 0 or scale <= 0:
        raise ValueError("radius and scale must be positive")
    return scale * radius / (1 + 2 * scale * radius)


@dataclass(frozen=True)
class RobustBisectionReceipt:
    gap: Fraction
    estimate: Fraction
    query_count: int
    stopped_in_indifference_zone: bool
    absolute_error: Fraction


def robust_bisection_with_bounded_probability_error(
    gap: Fraction,
    radius: Fraction,
    tolerance: Fraction,
    errors: Sequence[Fraction],
) -> RobustBisectionReceipt:
    """Bisection under a deterministic uniform probability-estimation event.

    The exact link is the rational symmetric link. The decision rule is the
    generic margin-based rule used by the theorem: decide only when the
    estimated probability clears 1/2 by more than the registered estimation
    error; otherwise return the midpoint as an eta-accurate estimate.
    """
    gap = Fraction(gap)
    radius = Fraction(radius)
    tolerance = Fraction(tolerance)
    if not -radius <= gap <= radius:
        raise ValueError("gap lies outside the registered radius")
    rounds = ceil_log2_fraction(radius / tolerance)
    if len(errors) < rounds:
        raise ValueError("one bounded error is required for every round")

    kappa = rational_link_margin_constant(radius)
    error_bound = kappa * tolerance / 2
    lower, upper = -radius, radius
    used = 0
    stopped = False
    for error in errors[:rounds]:
        error = Fraction(error)
        if abs(error) > error_bound:
            raise ValueError("probability error exceeds registered bound")
        midpoint = (lower + upper) / 2
        probability = rational_symmetric_link(gap - midpoint)
        estimate = probability + error
        used += 1
        if estimate > Fraction(1, 2) + error_bound:
            lower = midpoint
        elif estimate < Fraction(1, 2) - error_bound:
            upper = midpoint
        else:
            lower = upper = midpoint
            stopped = True
            break

    point = (lower + upper) / 2
    return RobustBisectionReceipt(
        gap=gap,
        estimate=point,
        query_count=used,
        stopped_in_indifference_zone=stopped,
        absolute_error=abs(point - gap),
    )


def bounded_error_patterns(rounds: int, bound: Fraction):
    """Enumerate extremal and central errors for finite theorem checks."""
    bound = Fraction(bound)
    yield from product((-bound, Fraction(0), bound), repeat=rounds)


def hoeffding_samples_per_query(
    kappa: float,
    tolerance: float,
    exponent: float,
    failure_probability: float,
    total_queries: int,
) -> int:
    """Registered sufficient repeats per query under a margin envelope."""
    if not kappa > 0 or not tolerance > 0 or not exponent > 0:
        raise ValueError("kappa, tolerance, and exponent must be positive")
    if not 0 < failure_probability < 1:
        raise ValueError("failure_probability must lie in (0,1)")
    if total_queries <= 0:
        raise ValueError("total_queries must be positive")
    estimation_error = kappa * tolerance**exponent / 2
    return math.ceil(
        math.log(2 * total_queries / failure_probability)
        / (2 * estimation_error**2)
    )


def no_offset_nonaffine_witness() -> dict[str, tuple[Fraction, ...]]:
    """The v0.8 three-item population-law obstruction."""
    return {
        "source": (Fraction(0), Fraction(1), Fraction(3)),
        "target": (Fraction(0), Fraction(1), Fraction(4)),
    }


def no_offset_matching_laws() -> dict[str, object]:
    """Reproduce the exact v0.8 law equality on all positive labelled gaps."""
    witness = no_offset_nonaffine_witness()
    source = witness["source"]
    target = witness["target"]
    source_law = {
        (left, right): rational_symmetric_link(source[right] - source[left])
        for left in range(3)
        for right in range(left + 1, 3)
    }
    target_probability_by_gap = {
        Fraction(1): Fraction(3, 4),
        Fraction(3): Fraction(5, 6),
        Fraction(4): Fraction(7, 8),
    }
    target_law = {
        (left, right): target_probability_by_gap[target[right] - target[left]]
        for left in range(3)
        for right in range(left + 1, 3)
    }
    knots = tuple(sorted(target_probability_by_gap.items()))
    admissible_target_knots = all(
        left_gap < right_gap and left_probability < right_probability
        for (left_gap, left_probability), (right_gap, right_probability) in zip(
            knots, knots[1:]
        )
    )
    return {
        "source_law": source_law,
        "target_law": target_law,
        "same_law": source_law == target_law,
        "admissible_target_knots": admissible_target_knots,
    }
