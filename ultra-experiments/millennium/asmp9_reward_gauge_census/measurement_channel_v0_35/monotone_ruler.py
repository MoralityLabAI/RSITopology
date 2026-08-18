"""Nonparametric monotone-ruler certificates for ASMP-9."""

from __future__ import annotations

from collections.abc import Sequence
import math


def _finite(values: Sequence[float]) -> tuple[float, ...]:
    output = tuple(float(value) for value in values)
    if len(output) < 2:
        raise ValueError("at least two ordered ruler values are required")
    if not all(math.isfinite(value) for value in output):
        raise ValueError("ruler values must be finite")
    return output


def monotone_linf_radius(values: Sequence[float]) -> float:
    """Return the exact L-infinity distance to nonincreasing sequences.

    For y_0,...,y_m, the distance is

        1/2 * max_{i<j} (y_j - y_i)_+.

    This is not a fitted or asymptotic statistic.
    """
    y = _finite(values)
    violation = max(
        (y[j] - y[i] for i in range(len(y)) for j in range(i + 1, len(y))),
        default=0.0,
    )
    return 0.5 * max(0.0, violation)


def monotone_linf_witness(values: Sequence[float]) -> tuple[float, ...]:
    """Construct a nonincreasing sequence at the exact repair radius."""
    y = _finite(values)
    radius = monotone_linf_radius(y)
    witness = tuple(
        max(y[j] - radius for j in range(i, len(y)))
        for i in range(len(y))
    )
    if any(witness[i] < witness[i + 1] for i in range(len(witness) - 1)):
        raise AssertionError("constructed witness is not nonincreasing")
    if max(abs(left - right) for left, right in zip(y, witness)) > (
        radius + 1e-12
    ):
        raise AssertionError("constructed witness exceeds exact radius")
    return witness


def robust_zero_crossing(values: Sequence[float], radius: float) -> bool:
    """Certify that every radius-close curve crosses zero on the grid.

    The input sequence is ordered from the lowest to the highest comparator.
    If y_0 >= radius and y_m <= -radius, every pointwise perturbation within
    the radius has opposite-signed endpoints.
    """
    y = _finite(values)
    radius = float(radius)
    if not math.isfinite(radius) or radius < 0:
        raise ValueError("radius must be finite and nonnegative")
    return y[0] >= radius and y[-1] <= -radius


def curve_certificate(values: Sequence[float]) -> dict[str, object]:
    """Return the exact monotone-repair and robust-crossing certificate."""
    y = _finite(values)
    radius = monotone_linf_radius(y)
    witness = monotone_linf_witness(y)
    dynamic_range = max(y) - min(y)
    return {
        "monotone_linf_radius": radius,
        "monotone_witness": list(witness),
        "robust_zero_crossing_at_repair_radius": robust_zero_crossing(
            y, radius
        ),
        "left_endpoint": y[0],
        "right_endpoint": y[-1],
        "dynamic_range": dynamic_range,
        "normalized_repair_radius": (
            radius / dynamic_range if dynamic_range > 0 else None
        ),
    }
