"""Finite-horizon amplification of stable, possibly non-normal operators.

The core result is elementary but useful as a control gate.  For

    x[t + 1] = A x[t]

and the norm induced by a positive-definite matrix ``M``, define

    G_T(A; M) = max_{0 <= t <= T} ||M^(1/2) A^t M^(-1/2)||_2.

Every initial condition with ``||x[0]||_M <= delta`` remains inside the ball of
radius ``boundary`` through time ``T`` exactly when
``delta * G_T(A; M) <= boundary``.  This module evaluates the finite set of
matrix powers directly and returns the singular-vector witness.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb
from typing import Iterable

import numpy as np


NUMERIC_TOLERANCE = 1e-12


@dataclass(frozen=True)
class FiniteHorizonGain:
    """Exact-over-the-registered-times finite-horizon operator gain."""

    gain: float
    maximizing_time: int
    gains_by_time: tuple[float, ...]
    whitened_right_vector: np.ndarray
    state_right_vector: np.ndarray
    whitened_left_vector: np.ndarray


@dataclass(frozen=True)
class JordanGainBounds:
    """Rigorous rational bounds for the registered nonnegative Jordan family."""

    lower_gain_squared: Fraction
    upper_gain: Fraction
    lower_maximizing_time: int
    upper_maximizing_time: int


def _as_square(matrix: np.ndarray | Iterable[Iterable[float]], name: str) -> np.ndarray:
    value = np.asarray(matrix, dtype=float)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.all(np.isfinite(value)):
        raise ValueError(f"{name} must contain only finite values")
    return value


def _metric_factors(
    metric: np.ndarray | None,
    dimension: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if metric is None:
        identity = np.eye(dimension)
        return identity, identity, identity
    value = _as_square(metric, "metric")
    if value.shape != (dimension, dimension):
        raise ValueError("metric dimension must match the operator")
    if not np.allclose(value, value.T, atol=1e-12, rtol=1e-12):
        raise ValueError("metric must be symmetric")
    eigenvalues, eigenvectors = np.linalg.eigh(value)
    if float(np.min(eigenvalues)) <= NUMERIC_TOLERANCE:
        raise ValueError("metric must be positive definite")
    square_root = (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.T
    inverse_square_root = (eigenvectors * (1.0 / np.sqrt(eigenvalues))) @ eigenvectors.T
    return value, square_root, inverse_square_root


def metric_norm(vector: np.ndarray, metric: np.ndarray | None = None) -> float:
    value = np.asarray(vector, dtype=float)
    if value.ndim != 1:
        raise ValueError("vector must be one-dimensional")
    matrix, _, _ = _metric_factors(metric, value.size)
    squared = float(value @ matrix @ value)
    return float(np.sqrt(max(0.0, squared)))


def spectral_radius(operator: np.ndarray) -> float:
    matrix = _as_square(operator, "operator")
    return float(np.max(np.abs(np.linalg.eigvals(matrix))))


def departure_from_normality(operator: np.ndarray) -> float:
    """Frobenius norm of ``A^T A - A A^T`` in the supplied coordinates."""

    matrix = _as_square(operator, "operator")
    commutator = matrix.T @ matrix - matrix @ matrix.T
    return float(np.linalg.norm(commutator, ord="fro"))


def finite_horizon_gain(
    operator: np.ndarray,
    horizon: int,
    *,
    metric: np.ndarray | None = None,
) -> FiniteHorizonGain:
    """Compute ``G_T`` and a worst-case initial direction.

    The time universe is the finite registered set ``{0, ..., horizon}``.
    Matrix powers and singular values are evaluated in float64; the result is a
    numerical evaluation of an exact finite-dimensional formula, not an
    interval-certified theorem.
    """

    matrix = _as_square(operator, "operator")
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    _, square_root, inverse_square_root = _metric_factors(metric, matrix.shape[0])

    gains: list[float] = []
    best_gain = -np.inf
    best_time = 0
    best_right: np.ndarray | None = None
    best_left: np.ndarray | None = None
    power = np.eye(matrix.shape[0])
    for time in range(horizon + 1):
        whitened = square_root @ power @ inverse_square_root
        left, singular, right_transpose = np.linalg.svd(whitened, full_matrices=False)
        gain = float(singular[0])
        gains.append(gain)
        if gain > best_gain:
            best_gain = gain
            best_time = time
            best_right = right_transpose[0].copy()
            best_left = left[:, 0].copy()
        power = matrix @ power

    assert best_right is not None and best_left is not None
    state_right = inverse_square_root @ best_right
    # Numerical normalization makes the witness robust to eigensolver drift in
    # non-identity metrics.
    state_right /= metric_norm(state_right, metric)
    return FiniteHorizonGain(
        gain=best_gain,
        maximizing_time=best_time,
        gains_by_time=tuple(gains),
        whitened_right_vector=best_right,
        state_right_vector=state_right,
        whitened_left_vector=best_left,
    )


def worst_case_trajectory(
    operator: np.ndarray,
    gain: FiniteHorizonGain,
    *,
    initial_radius: float,
) -> np.ndarray:
    matrix = _as_square(operator, "operator")
    if initial_radius < 0:
        raise ValueError("initial_radius must be nonnegative")
    states = [initial_radius * gain.state_right_vector]
    for _ in range(gain.maximizing_time):
        states.append(matrix @ states[-1])
    return np.stack(states)


def boundary_decision(
    gain: float,
    *,
    initial_radius: float,
    safety_radius: float,
    tolerance: float = 1e-12,
) -> bool:
    """Return true exactly when the closed-ball finite-horizon gate passes."""

    if gain < 0 or initial_radius < 0 or safety_radius < 0:
        raise ValueError("gain and radii must be nonnegative")
    return initial_radius * gain <= safety_radius + tolerance


def normal_control(dimension: int, decay: float) -> np.ndarray:
    if dimension < 1:
        raise ValueError("dimension must be positive")
    if not np.isfinite(decay):
        raise ValueError("decay must be finite")
    return float(decay) * np.eye(dimension)


def jordan_chain(dimension: int, decay: float, coupling: float) -> np.ndarray:
    """Upper-bidiagonal matched-spectrum non-normal fixture."""

    if dimension < 1:
        raise ValueError("dimension must be positive")
    if not np.isfinite(decay) or not np.isfinite(coupling):
        raise ValueError("decay and coupling must be finite")
    matrix = float(decay) * np.eye(dimension)
    if dimension > 1:
        matrix += float(coupling) * np.diag(np.ones(dimension - 1), k=1)
    return matrix


def jordan_exact_gain_bounds(
    dimension: int,
    decay: Fraction,
    coupling: Fraction,
    horizon: int,
) -> JordanGainBounds:
    """Bound the 2-norm of powers using exact rational arithmetic.

    For ``A=decay*I+coupling*N`` with the first-superdiagonal nilpotent shift,
    the entries of ``A^t`` on superdiagonal ``j`` are

    ``comb(t,j) * decay**(t-j) * coupling**j``.

    The Euclidean norm of the last column is a lower bound on ``||A^t||_2``.
    Since all coefficients are nonnegative and Toeplitz triangular, the maximum
    row and column sums both equal their total, which is an upper bound on the
    2-norm.  Both comparisons are therefore exact rationals before the final
    square root is avoided by comparing squared quantities.
    """

    if dimension < 1:
        raise ValueError("dimension must be positive")
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    if decay < 0 or coupling < 0:
        raise ValueError("exact registered bounds require nonnegative coefficients")

    best_lower_squared = Fraction(-1, 1)
    best_upper = Fraction(-1, 1)
    lower_time = 0
    upper_time = 0
    for time in range(horizon + 1):
        coefficients = [
            Fraction(comb(time, offset), 1)
            * decay ** (time - offset)
            * coupling**offset
            for offset in range(min(time, dimension - 1) + 1)
        ]
        lower_squared = sum((value * value for value in coefficients), Fraction(0, 1))
        upper = sum(coefficients, Fraction(0, 1))
        if lower_squared > best_lower_squared:
            best_lower_squared = lower_squared
            lower_time = time
        if upper > best_upper:
            best_upper = upper
            upper_time = time
    return JordanGainBounds(
        lower_gain_squared=best_lower_squared,
        upper_gain=best_upper,
        lower_maximizing_time=lower_time,
        upper_maximizing_time=upper_time,
    )


def classify_jordan_radius(
    bounds: JordanGainBounds,
    *,
    initial_radius: Fraction,
    safety_radius: Fraction,
) -> str:
    """Return a rigorous pass/fail/indeterminate decision from rational bounds."""

    if initial_radius < 0 or safety_radius < 0:
        raise ValueError("radii must be nonnegative")
    if initial_radius * bounds.upper_gain <= safety_radius:
        return "pass"
    if initial_radius**2 * bounds.lower_gain_squared > safety_radius**2:
        return "fail"
    return "numerically_indeterminate"


def reframe_operator(
    operator: np.ndarray,
    metric: np.ndarray,
    coordinate_map: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Change coordinates while preserving the physical metric.

    With old coordinates ``x = R z``, the returned objects are
    ``A_z = R^-1 A R`` and ``M_z = R^T M R``.
    """

    matrix = _as_square(operator, "operator")
    metric_value, _, _ = _metric_factors(metric, matrix.shape[0])
    transform = _as_square(coordinate_map, "coordinate_map")
    if transform.shape != matrix.shape:
        raise ValueError("coordinate_map dimension must match the operator")
    condition = float(np.linalg.cond(transform))
    if not np.isfinite(condition):
        raise ValueError("coordinate_map must be invertible")
    inverse = np.linalg.inv(transform)
    return inverse @ matrix @ transform, transform.T @ metric_value @ transform


def sample_metric_unit_directions(
    dimension: int,
    count: int,
    *,
    seed: int,
    metric: np.ndarray | None = None,
) -> np.ndarray:
    """Sample normalized Gaussian directions uniformly on the metric sphere."""

    if dimension < 1 or count < 1:
        raise ValueError("dimension and count must be positive")
    _, _, inverse_square_root = _metric_factors(metric, dimension)
    rng = np.random.default_rng(seed)
    whitened = rng.normal(size=(count, dimension))
    whitened /= np.linalg.norm(whitened, axis=1, keepdims=True)
    return whitened @ inverse_square_root.T


def maximum_sampled_gain(
    operator: np.ndarray,
    directions: np.ndarray,
    horizon: int,
    *,
    metric: np.ndarray | None = None,
) -> tuple[float, int, int]:
    """Return the largest observed gain over a finite probe set.

    This is a lower bound on ``G_T`` and is never a universal certificate.
    """

    matrix = _as_square(operator, "operator")
    vectors = np.asarray(directions, dtype=float)
    if vectors.ndim != 2 or vectors.shape[1] != matrix.shape[0]:
        raise ValueError("directions must have shape (count, dimension)")
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    metric_value, _, _ = _metric_factors(metric, matrix.shape[0])
    denominators = np.sqrt(np.einsum("ni,ij,nj->n", vectors, metric_value, vectors))
    if np.any(denominators <= NUMERIC_TOLERANCE):
        raise ValueError("directions must be nonzero")
    states = vectors.copy()
    best_gain = -np.inf
    best_time = 0
    best_index = 0
    for time in range(horizon + 1):
        numerators = np.sqrt(np.einsum("ni,ij,nj->n", states, metric_value, states))
        gains = numerators / denominators
        index = int(np.argmax(gains))
        if float(gains[index]) > best_gain:
            best_gain = float(gains[index])
            best_time = time
            best_index = index
        states = states @ matrix.T
    return best_gain, best_time, best_index
