"""Rate, covering, spectral, and evaluator-transversal calculations."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, floor, log2
from typing import Iterable, Sequence

import numpy as np


NUMERIC_TOLERANCE = 1e-12


def unstable_eigenvalues(values: Sequence[complex | float]) -> np.ndarray:
    array = np.asarray(values, dtype=complex)
    return np.abs(array[np.abs(array) > 1.0 + NUMERIC_TOLERANCE]).astype(float)


def unstable_entropy_bits(values: Sequence[complex | float]) -> float:
    unstable = unstable_eigenvalues(values)
    return float(np.sum(np.log2(unstable))) if unstable.size else 0.0


def random_orthogonal(dimension: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    matrix = rng.normal(size=(dimension, dimension))
    q, r = np.linalg.qr(matrix)
    signs = np.sign(np.diag(r))
    signs[signs == 0] = 1.0
    q = q @ np.diag(signs)
    if np.linalg.det(q) < 0:
        q[:, 0] *= -1.0
    return q


def finite_horizon_volume_lower_bits(
    eigenvalues: Sequence[complex | float],
    horizon: int,
    initial_half_widths: Sequence[float],
    safe_half_widths: Sequence[float],
) -> int:
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    eigenvalues = np.asarray(eigenvalues, dtype=complex)
    initial = np.asarray(initial_half_widths, dtype=float)
    safe = np.asarray(safe_half_widths, dtype=float)
    if initial.shape != eigenvalues.shape or safe.shape != eigenvalues.shape:
        raise ValueError("widths must match the spectrum")
    if np.any(initial <= 0) or np.any(safe <= 0):
        raise ValueError("half-widths must be positive")
    unstable = np.abs(eigenvalues) > 1.0 + NUMERIC_TOLERANCE
    if not np.any(unstable):
        return 0
    log_volume_ratio = float(np.sum(np.log2(initial[unstable] / safe[unstable])))
    raw = horizon * unstable_entropy_bits(eigenvalues) + log_volume_ratio
    return max(0, int(ceil(raw - NUMERIC_TOLERANCE)))


def aligned_box_cover_counts(
    eigenvalues: Sequence[complex | float],
    horizon: int,
    initial_half_widths: Sequence[float],
    safe_half_widths: Sequence[float],
) -> tuple[int, ...]:
    eigenvalues = np.asarray(eigenvalues, dtype=complex)
    initial = np.asarray(initial_half_widths, dtype=float)
    safe = np.asarray(safe_half_widths, dtype=float)
    if initial.shape != eigenvalues.shape or safe.shape != eigenvalues.shape:
        raise ValueError("widths must match the spectrum")
    counts = []
    for eigenvalue, radius, limit in zip(np.abs(eigenvalues), initial, safe):
        required = (float(eigenvalue) ** horizon) * float(radius) / float(limit)
        counts.append(max(1, int(ceil(required - NUMERIC_TOLERANCE))))
    return tuple(counts)


def aligned_box_cover_bits(
    eigenvalues: Sequence[complex | float],
    horizon: int,
    initial_half_widths: Sequence[float],
    safe_half_widths: Sequence[float],
) -> int:
    product = int(
        np.prod(
            aligned_box_cover_counts(
                eigenvalues, horizon, initial_half_widths, safe_half_widths
            ),
            dtype=object,
        )
    )
    return 0 if product <= 1 else int(ceil(log2(product) - NUMERIC_TOLERANCE))


def cumulative_rate_bits(rate: float, step: int) -> int:
    if rate < 0 or step < 0:
        raise ValueError("rate and step must be nonnegative")
    return int(floor(rate * step + NUMERIC_TOLERANCE))


def classify_split_rate(
    eigenvalues: Sequence[complex | float],
    read_rate: float,
    write_rate: float,
    horizon: int,
    initial_half_widths: Sequence[float],
    safe_half_widths: Sequence[float],
) -> dict[str, object]:
    """Separate a universal volume obstruction from an explicit box construction."""

    prefixes = []
    lower_failure = None
    constructive_failure = None
    for step in range(1, horizon + 1):
        lower = finite_horizon_volume_lower_bits(
            eigenvalues, step, initial_half_widths, safe_half_widths
        )
        cover = aligned_box_cover_bits(
            eigenvalues, step, initial_half_widths, safe_half_widths
        )
        read_bits = cumulative_rate_bits(read_rate, step)
        write_bits = cumulative_rate_bits(write_rate, step)
        if lower_failure is None and (read_bits < lower or write_bits < lower):
            lower_failure = step
        if constructive_failure is None and (read_bits < cover or write_bits < cover):
            constructive_failure = step
        prefixes.append(
            {
                "step": step,
                "read_bits": read_bits,
                "write_bits": write_bits,
                "universal_lower_bits": lower,
                "constructive_cover_bits": cover,
            }
        )
    if lower_failure is not None:
        classification = "certified_infeasible"
        evidence = "universal_volume_lower_bound"
    elif constructive_failure is None:
        classification = "constructive_feasible"
        evidence = "aligned_box_cover"
    else:
        classification = "undetermined"
        evidence = "lower_construction_gap"
    final = prefixes[-1]
    return {
        "classification": classification,
        "evidence": evidence,
        "first_universal_failure_step": lower_failure,
        "first_constructive_failure_step": constructive_failure,
        "universal_margin_bits": min(
            final["read_bits"], final["write_bits"]
        )
        - final["universal_lower_bits"],
        "constructive_margin_bits": min(
            final["read_bits"], final["write_bits"]
        )
        - final["constructive_cover_bits"],
        "prefixes": prefixes,
    }


def critical_constructive_rate(
    eigenvalues: Sequence[complex | float],
    horizon: int,
    initial_half_widths: Sequence[float],
    safe_half_widths: Sequence[float],
    *,
    block_length: int,
) -> float:
    if block_length < 1:
        raise ValueError("block_length must be positive")
    required = max(
        aligned_box_cover_bits(eigenvalues, step, initial_half_widths, safe_half_widths)
        / step
        for step in range(1, horizon + 1)
    )
    return ceil(required * block_length - NUMERIC_TOLERANCE) / block_length


def port_staircase(entropy_bits: float, precision_bits: int) -> int:
    if precision_bits < 1:
        raise ValueError("precision_bits must be positive")
    return int(ceil(entropy_bits / precision_bits - NUMERIC_TOLERANCE))


@dataclass(frozen=True)
class RelevantModeSummary:
    local_entropy: float
    evaluator_entropy: float
    local_unstable_index: int
    evaluator_unstable_index: int
    mode_observabilities: tuple[float, ...]


def evaluator_relevant_modes(
    A: np.ndarray,
    evaluator_normal: Sequence[float],
    *,
    tolerance: float = 1e-9,
) -> RelevantModeSummary:
    matrix = np.asarray(A, dtype=float)
    normal = np.asarray(evaluator_normal, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("A must be square")
    if normal.shape != (matrix.shape[0],):
        raise ValueError("evaluator normal has wrong dimension")
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    local = []
    relevant = []
    observabilities = []
    for index, eigenvalue in enumerate(eigenvalues):
        magnitude = abs(eigenvalue)
        if magnitude <= 1.0 + NUMERIC_TOLERANCE:
            continue
        vector = eigenvectors[:, index]
        vector = vector / np.linalg.norm(vector)
        visibility = float(abs(np.vdot(normal, vector)))
        local.append(magnitude)
        observabilities.append(visibility)
        if visibility > tolerance:
            relevant.append(magnitude)
    return RelevantModeSummary(
        local_entropy=unstable_entropy_bits(local),
        evaluator_entropy=unstable_entropy_bits(relevant),
        local_unstable_index=len(local),
        evaluator_unstable_index=len(relevant),
        mode_observabilities=tuple(observabilities),
    )


def observability_matrix(A: np.ndarray, normal: Sequence[float], horizon: int) -> np.ndarray:
    matrix = np.asarray(A, dtype=float)
    row = np.asarray(normal, dtype=float).reshape(1, -1)
    blocks = []
    power = np.eye(matrix.shape[0])
    for _ in range(horizon):
        blocks.append(row @ power)
        power = power @ matrix
    return np.vstack(blocks)


def finite_horizon_relevant_entropy(
    A: np.ndarray,
    evaluator_normal: Sequence[float],
    horizon: int,
    *,
    sensitivity_floor: float,
) -> dict[str, object]:
    matrix = np.asarray(A, dtype=float)
    normal = np.asarray(evaluator_normal, dtype=float)
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    visible_values = []
    sensitivities = []
    for index, eigenvalue in enumerate(eigenvalues):
        if abs(eigenvalue) <= 1.0 + NUMERIC_TOLERANCE:
            continue
        vector = eigenvectors[:, index]
        vector = vector / np.linalg.norm(vector)
        sensitivity = max(
            float(abs(np.vdot(normal, np.linalg.matrix_power(matrix, step) @ vector)))
            for step in range(horizon + 1)
        )
        sensitivities.append(sensitivity)
        if sensitivity >= sensitivity_floor:
            visible_values.append(abs(eigenvalue))
    observability = observability_matrix(matrix, normal, horizon)
    singular = np.linalg.svd(observability, compute_uv=False)
    return {
        "finite_horizon_entropy": unstable_entropy_bits(visible_values),
        "finite_horizon_index": len(visible_values),
        "mode_sensitivities": sensitivities,
        "observability_rank": int(np.linalg.matrix_rank(observability)),
        "observability_min_nonzero_singular": float(
            min((value for value in singular if value > NUMERIC_TOLERANCE), default=0.0)
        ),
    }
