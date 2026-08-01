"""Exact one-dimensional Lipschitz continuation certificates."""

from __future__ import annotations

import itertools
from fractions import Fraction


def validate_sources(
    sources: tuple[Fraction, ...],
    values: tuple[Fraction, ...],
    lipschitz: Fraction,
) -> None:
    if not sources or len(sources) != len(values):
        raise ValueError("matching nonempty sources and values are required")
    if tuple(sorted(set(sources))) != sources:
        raise ValueError("sources must be strictly increasing")
    if lipschitz < 0:
        raise ValueError("lipschitz constant must be nonnegative")
    for first, second in itertools.combinations(range(len(sources)), 2):
        if abs(values[first] - values[second]) > lipschitz * abs(
            sources[first] - sources[second]
        ):
            raise ValueError("source values violate the Lipschitz condition")


def upper_envelope(
    x: Fraction,
    sources: tuple[Fraction, ...],
    values: tuple[Fraction, ...],
    lipschitz: Fraction,
) -> Fraction:
    validate_sources(sources, values, lipschitz)
    return min(
        value + lipschitz * abs(x - source) for source, value in zip(sources, values)
    )


def lower_envelope(
    x: Fraction,
    sources: tuple[Fraction, ...],
    values: tuple[Fraction, ...],
    lipschitz: Fraction,
) -> Fraction:
    validate_sources(sources, values, lipschitz)
    return max(
        value - lipschitz * abs(x - source) for source, value in zip(sources, values)
    )


def fill_distance(
    left: Fraction, right: Fraction, sources: tuple[Fraction, ...]
) -> Fraction:
    if left > right or not sources or sources[0] < left or sources[-1] > right:
        raise ValueError("invalid interval or source set")
    candidates = [sources[0] - left, right - sources[-1]]
    candidates.extend(
        (sources[index + 1] - sources[index]) / 2 for index in range(len(sources) - 1)
    )
    return max(candidates)


def frozen_continuation_report() -> dict[str, object]:
    left, right = Fraction(-1), Fraction(1)
    endpoints = (left, right)
    covered = (left, Fraction(0), right)
    endpoint_values = (Fraction(7, 16), Fraction(7, 16))
    covered_values = (Fraction(7, 16),) * 3
    lipschitz = Fraction(1, 4)
    threshold = Fraction(9, 16)

    endpoint_h = fill_distance(left, right, endpoints)
    covered_h = fill_distance(left, right, covered)
    endpoint_worst = max(
        upper_envelope(x, endpoints, endpoint_values, lipschitz)
        for x in (left, Fraction(0), right)
    )
    covered_worst = max(
        upper_envelope(x, covered, covered_values, lipschitz)
        for x in (left, Fraction(-1, 2), Fraction(0), Fraction(1, 2), right)
    )
    return {
        "endpoint_fill_distance": f"{endpoint_h.numerator}/{endpoint_h.denominator}",
        "covered_fill_distance": f"{covered_h.numerator}/{covered_h.denominator}",
        "endpoint_worst_upper_envelope": (
            f"{endpoint_worst.numerator}/{endpoint_worst.denominator}"
        ),
        "covered_worst_upper_envelope": (
            f"{covered_worst.numerator}/{covered_worst.denominator}"
        ),
        "threshold": f"{threshold.numerator}/{threshold.denominator}",
        "endpoint_design_fails": endpoint_worst > threshold,
        "midpoint_addition_certifies": covered_worst <= threshold,
        "exact_margin_cover_identity": (
            threshold - Fraction(7, 16) == lipschitz * covered_h
        ),
    }
