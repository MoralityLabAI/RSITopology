from __future__ import annotations

from fractions import Fraction
from typing import Sequence

import numpy as np


def q(value) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def rational_link(value: Fraction) -> Fraction:
    """Strictly increasing symmetric link with exact rational values."""
    value = q(value)
    return Fraction(1, 2) + value / (2 * (1 + abs(value)))


def rescaled_rational_link(value: Fraction, alpha: Fraction) -> Fraction:
    alpha = q(alpha)
    if alpha <= 0:
        raise ValueError("scale must be positive")
    return rational_link(q(value) / alpha)


def dot(row: Sequence, vector: Sequence) -> Fraction:
    if len(row) != len(vector):
        raise ValueError("dimension mismatch")
    return sum((q(a) * q(b) for a, b in zip(row, vector)), Fraction(0))


def population_law(matrix: Sequence[Sequence], reward: Sequence):
    return tuple(rational_link(dot(row, reward)) for row in matrix)


def scaled_population_law(
    matrix: Sequence[Sequence], reward: Sequence, alpha
):
    alpha = q(alpha)
    scaled_reward = tuple(alpha * q(value) for value in reward)
    return tuple(
        rescaled_rational_link(dot(row, scaled_reward), alpha)
        for row in matrix
    )


def unknown_numeraire_law(
    matrix: Sequence[Sequence],
    reward: Sequence,
    offsets: Sequence,
    coefficient,
):
    if len(matrix) != len(offsets):
        raise ValueError("one offset per row is required")
    coefficient = q(coefficient)
    return tuple(
        rational_link(dot(row, reward) + q(offset) * coefficient)
        for row, offset in zip(matrix, offsets)
    )


def scaled_unknown_numeraire_law(
    matrix: Sequence[Sequence],
    reward: Sequence,
    offsets: Sequence,
    coefficient,
    alpha,
):
    alpha = q(alpha)
    scaled_reward = tuple(alpha * q(value) for value in reward)
    scaled_coefficient = alpha * q(coefficient)
    return tuple(
        rescaled_rational_link(
            dot(row, scaled_reward) + q(offset) * scaled_coefficient,
            alpha,
        )
        for row, offset in zip(matrix, offsets)
    )


def known_numeraire_law(
    matrix: Sequence[Sequence], reward: Sequence, offsets: Sequence
):
    if len(matrix) != len(offsets):
        raise ValueError("one offset per row is required")
    return tuple(
        rational_link(dot(row, reward) + q(offset))
        for row, offset in zip(matrix, offsets)
    )


def scaled_reward_known_numeraire_law(
    matrix: Sequence[Sequence], reward: Sequence, offsets: Sequence, alpha
):
    if len(matrix) != len(offsets):
        raise ValueError("one offset per row is required")
    alpha = q(alpha)
    scaled_reward = tuple(alpha * q(value) for value in reward)
    return tuple(
        rescaled_rational_link(dot(row, scaled_reward) + q(offset), alpha)
        for row, offset in zip(matrix, offsets)
    )


def rational_rank(matrix: Sequence[Sequence]) -> int:
    rows = [list(map(q, row)) for row in matrix]
    if not rows:
        return 0
    columns = len(rows[0])
    if any(len(row) != columns for row in rows):
        raise ValueError("ragged matrix")
    rank = 0
    for column in range(columns):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][column]
        rows[rank] = [value / pivot_value for value in rows[rank]]
        for index, row in enumerate(rows):
            if index == rank or row[column] == 0:
                continue
            multiplier = row[column]
            rows[index] = [
                value - multiplier * pivot_entry
                for value, pivot_entry in zip(row, rows[rank])
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def quotient_identifiable(
    measurement: Sequence[Sequence], gauge_basis: Sequence[Sequence]
) -> dict[str, int | bool]:
    if not measurement:
        raise ValueError("measurement matrix must be nonempty")
    parameter_dim = len(measurement[0])
    measurement_rank = rational_rank(measurement)
    gauge_rank = rational_rank(gauge_basis)
    annihilates = all(
        dot(row, gauge) == 0 for row in measurement for gauge in gauge_basis
    )
    exact = annihilates and measurement_rank == parameter_dim - gauge_rank
    return {
        "parameter_dim": parameter_dim,
        "measurement_rank": measurement_rank,
        "gauge_rank": gauge_rank,
        "annihilates_gauge": annihilates,
        "identifiable_modulo_gauge": exact,
    }


def quotient_stability(
    measurement: Sequence[Sequence], quotient_basis: Sequence[Sequence]
) -> dict[str, float | int]:
    matrix = np.asarray(measurement, dtype=float)
    basis = np.asarray(quotient_basis, dtype=float).T
    design = matrix @ basis
    singular = np.linalg.svd(design, compute_uv=False)
    positive = singular[singular > 1e-12]
    sigma_min = float(np.min(positive)) if positive.size else 0.0
    return {
        "quotient_dimension": int(basis.shape[1]),
        "design_rank": int(np.linalg.matrix_rank(design)),
        "sigma_min": sigma_min,
        "amplification": (
            float("inf") if sigma_min == 0.0 else 1.0 / sigma_min
        ),
    }
