"""Exact context/order nuisance quotient for ASMP-9 response measurements.

The quotient in this module is a measurement-nuisance quotient.  It is not a
reward-shaping quotient and it does not turn response effects into values.
All arithmetic is exact ``fractions.Fraction`` arithmetic.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Iterable, Sequence


Scalar = int | str | Fraction


def as_fraction(value: Scalar) -> Fraction:
    if isinstance(value, Fraction):
        return value
    return Fraction(value)


def _matrix(values: Sequence[Sequence[Scalar]]) -> tuple[tuple[Fraction, ...], ...]:
    if not values:
        raise ValueError("at least one nuisance block is required")
    width = len(values[0])
    if width < 2:
        raise ValueError("each block requires a reference and at least one arm")
    result: list[tuple[Fraction, ...]] = []
    for row in values:
        if len(row) != width:
            raise ValueError("measurement matrix must be rectangular")
        result.append(tuple(as_fraction(value) for value in row))
    return tuple(result)


def gauge_shift(
    values: Sequence[Sequence[Scalar]], offsets: Sequence[Scalar]
) -> tuple[tuple[Fraction, ...], ...]:
    """Add an arbitrary common offset to every arm within each block."""

    matrix = _matrix(values)
    if len(offsets) != len(matrix):
        raise ValueError("one offset is required per block")
    return tuple(
        tuple(value + as_fraction(offsets[index]) for value in row)
        for index, row in enumerate(matrix)
    )


def within_reference_quotient(
    values: Sequence[Sequence[Scalar]], reference_index: int = 0
) -> tuple[tuple[Fraction, ...], ...]:
    """Return maximal-invariant within-block contrasts to one reference arm."""

    matrix = _matrix(values)
    width = len(matrix[0])
    if not 0 <= reference_index < width:
        raise ValueError("reference index is out of range")
    return tuple(
        tuple(
            value - row[reference_index]
            for index, value in enumerate(row)
            if index != reference_index
        )
        for row in matrix
    )


def same_gauge_orbit(
    left: Sequence[Sequence[Scalar]], right: Sequence[Sequence[Scalar]]
) -> bool:
    """Decide exact equality modulo arbitrary blockwise common offsets."""

    left_matrix = _matrix(left)
    right_matrix = _matrix(right)
    if len(left_matrix) != len(right_matrix):
        return False
    if len(left_matrix[0]) != len(right_matrix[0]):
        return False
    return within_reference_quotient(left_matrix) == within_reference_quotient(
        right_matrix
    )


def invariant_linear_estimand(coefficients: Sequence[Sequence[Scalar]]) -> bool:
    """A linear estimand is invariant iff coefficients sum to zero per block."""

    matrix = _matrix(coefficients)
    return all(sum(row, Fraction(0)) == 0 for row in matrix)


def evaluate_linear_estimand(
    coefficients: Sequence[Sequence[Scalar]],
    values: Sequence[Sequence[Scalar]],
) -> Fraction:
    coefficient_matrix = _matrix(coefficients)
    value_matrix = _matrix(values)
    if (
        len(coefficient_matrix) != len(value_matrix)
        or len(coefficient_matrix[0]) != len(value_matrix[0])
    ):
        raise ValueError("coefficient and value matrices must have equal shape")
    return sum(
        (
            coefficient * value
            for coefficient_row, value_row in zip(
                coefficient_matrix, value_matrix, strict=True
            )
            for coefficient, value in zip(
                coefficient_row, value_row, strict=True
            )
        ),
        Fraction(0),
    )


def shared_effect_intersection(
    intervals: Iterable[tuple[Scalar, Scalar]],
) -> dict[str, Fraction | str | int]:
    """Test whether context-local effect intervals admit one shared effect.

    A nonnegative margin is necessary and sufficient because closed intervals
    on the real line have Helly number two.
    """

    normalized = [
        (as_fraction(lower), as_fraction(upper)) for lower, upper in intervals
    ]
    if not normalized:
        raise ValueError("at least one interval is required")
    if any(lower > upper for lower, upper in normalized):
        raise ValueError("interval lower bound exceeds upper bound")
    lower = max(item[0] for item in normalized)
    upper = min(item[1] for item in normalized)
    margin = upper - lower
    return {
        "status": (
            "shared_effect_compatible"
            if margin >= 0
            else "context_conditioning_required"
        ),
        "intersection_lower": lower,
        "intersection_upper": upper,
        "intersection_margin": margin,
        "context_count": len(normalized),
    }


def exhaustive_small_audit() -> dict[str, int]:
    """Exhaustively audit the two-block, three-arm exact theorem cell."""

    matrices = [
        (row[:3], row[3:])
        for row in product((-1, 0, 1), repeat=6)
    ]
    offsets = list(product((-2, -1, 0, 1, 2), repeat=2))
    invariance_checks = 0
    for matrix in matrices:
        quotient = within_reference_quotient(matrix)
        for offset in offsets:
            shifted = gauge_shift(matrix, offset)
            if within_reference_quotient(shifted) != quotient:
                raise AssertionError("quotient invariance failed")
            if not same_gauge_orbit(matrix, shifted):
                raise AssertionError("orbit completeness failed")
            invariance_checks += 1

    maximality_checks = 0
    representatives: dict[
        tuple[tuple[Fraction, ...], ...], tuple[tuple[int, ...], ...]
    ] = {}
    for matrix in matrices:
        quotient = within_reference_quotient(matrix)
        if quotient in representatives and not same_gauge_orbit(
            matrix, representatives[quotient]
        ):
            raise AssertionError("equal quotient failed maximality")
        representatives.setdefault(quotient, matrix)
        maximality_checks += 1

    estimand_checks = 0
    witness_values = ((0, 0, 0), (0, 0, 0))
    for coefficient_tuple in product((-1, 0, 1), repeat=6):
        coefficients = (coefficient_tuple[:3], coefficient_tuple[3:])
        declared = invariant_linear_estimand(coefficients)
        unchanged = all(
            evaluate_linear_estimand(
                coefficients, gauge_shift(witness_values, offset)
            )
            == 0
            for offset in offsets
        )
        if declared != unchanged:
            raise AssertionError("linear-invariance criterion failed")
        estimand_checks += 1

    return {
        "measurement_matrices": len(matrices),
        "offset_vectors": len(offsets),
        "quotient_invariance_checks": invariance_checks,
        "maximality_checks": maximality_checks,
        "linear_estimand_checks": estimand_checks,
    }
