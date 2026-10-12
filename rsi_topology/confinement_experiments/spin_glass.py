"""Small CPU spherical 3-spin boundary-critical-point sampler.

The sampler is deliberately explicit about basin weighting. It is an
instrument-robustness experiment, not a Kac-Rice sampler.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from scipy.linalg import null_space


@dataclass(frozen=True)
class CubicField:
    tensor: np.ndarray
    quadratic: np.ndarray | None = None
    cubic_weight: float = 1.0
    quadratic_weight: float = 0.0

    def __post_init__(self) -> None:
        tensor = np.asarray(self.tensor, dtype=float)
        if tensor.ndim != 3 or len(set(tensor.shape)) != 1:
            raise ValueError("cubic tensor must have shape (N, N, N)")
        object.__setattr__(self, "tensor", tensor)
        if self.quadratic is not None:
            quadratic = np.asarray(self.quadratic, dtype=float)
            if quadratic.shape != tensor.shape[:2]:
                raise ValueError("quadratic matrix has wrong shape")
            object.__setattr__(self, "quadratic", 0.5 * (quadratic + quadratic.T))

    @property
    def dimension(self) -> int:
        return self.tensor.shape[0]

    @property
    def cubic_scale(self) -> float:
        # Gives Var(H(x)) of order N on the radius-sqrt(N) sphere.
        return float(self.cubic_weight / (np.sqrt(2.0) * self.dimension))

    def value(self, x: np.ndarray) -> float:
        vector = np.asarray(x, dtype=float)
        cubic = self.cubic_scale * np.einsum(
            "ijk,i,j,k->", self.tensor, vector, vector, vector, optimize=True
        )
        quadratic = 0.0
        if self.quadratic is not None and self.quadratic_weight:
            quadratic = (
                self.quadratic_weight
                * float(vector @ self.quadratic @ vector)
                / np.sqrt(2.0 * self.dimension)
            )
        return float(cubic + quadratic)

    def gradient(self, x: np.ndarray) -> np.ndarray:
        vector = np.asarray(x, dtype=float)
        J = self.tensor
        gradient = self.cubic_scale * (
            np.einsum("ljk,j,k->l", J, vector, vector, optimize=True)
            + np.einsum("ilk,i,k->l", J, vector, vector, optimize=True)
            + np.einsum("ijl,i,j->l", J, vector, vector, optimize=True)
        )
        if self.quadratic is not None and self.quadratic_weight:
            gradient = gradient + (
                2.0
                * self.quadratic_weight
                * (self.quadratic @ vector)
                / np.sqrt(2.0 * self.dimension)
            )
        return gradient

    def hessian(self, x: np.ndarray) -> np.ndarray:
        vector = np.asarray(x, dtype=float)
        J = self.tensor
        hessian = self.cubic_scale * (
            np.einsum("abk,k->ab", J, vector, optimize=True)
            + np.einsum("akb,k->ab", J, vector, optimize=True)
            + np.einsum("bak,k->ab", J, vector, optimize=True)
            + np.einsum("kab,k->ab", J, vector, optimize=True)
            + np.einsum("bka,k->ab", J, vector, optimize=True)
            + np.einsum("kba,k->ab", J, vector, optimize=True)
        )
        if self.quadratic is not None and self.quadratic_weight:
            hessian = hessian + (
                2.0
                * self.quadratic_weight
                * self.quadratic
                / np.sqrt(2.0 * self.dimension)
            )
        return 0.5 * (hessian + hessian.T)


def generate_field(
    dimension: int,
    seed: int,
    *,
    quadratic_weight: float = 0.0,
) -> CubicField:
    rng = np.random.default_rng(seed)
    tensor = rng.normal(size=(dimension, dimension, dimension))
    quadratic = None
    if quadratic_weight:
        raw = rng.normal(size=(dimension, dimension))
        quadratic = (raw + raw.T) / np.sqrt(2.0 * dimension)
    return CubicField(tensor, quadratic, 1.0, quadratic_weight)


def evaluator_direction(dimension: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    value = rng.normal(size=dimension)
    return value / np.linalg.norm(value)


def constrained_random_point(
    rng: np.random.Generator,
    evaluator: np.ndarray,
    tau: float,
) -> np.ndarray:
    dimension = evaluator.size
    if abs(tau) >= 1.0:
        raise ValueError("linear evaluator level must satisfy abs(tau) < 1")
    tangent = rng.normal(size=dimension)
    tangent = tangent - evaluator * float(evaluator @ tangent)
    tangent /= np.linalg.norm(tangent)
    return np.sqrt(dimension) * (
        tau * evaluator + np.sqrt(1.0 - tau**2) * tangent
    )


def project_to_constraints(x: np.ndarray, evaluator: np.ndarray, tau: float) -> np.ndarray:
    dimension = evaluator.size
    tangent = x - evaluator * float(evaluator @ x)
    norm = np.linalg.norm(tangent)
    if norm < 1e-14:
        tangent = np.zeros_like(x)
        tangent[int(np.argmin(np.abs(evaluator)))] = 1.0
        tangent -= evaluator * float(evaluator @ tangent)
        norm = np.linalg.norm(tangent)
    tangent /= norm
    return np.sqrt(dimension) * (
        tau * evaluator + np.sqrt(1.0 - tau**2) * tangent
    )


def seed_by_projected_flow(
    field: CubicField,
    x: np.ndarray,
    evaluator: np.ndarray,
    tau: float,
    *,
    direction: float,
    steps: int = 8,
    step_size: float = 0.05,
) -> np.ndarray:
    value = x.copy()
    for _ in range(steps):
        basis = null_space(np.vstack([value, evaluator]))
        projected = basis @ (basis.T @ field.gradient(value))
        value = project_to_constraints(
            value + direction * step_size * projected,
            evaluator,
            tau,
        )
    return value


@dataclass(frozen=True)
class CriticalPoint:
    x: np.ndarray
    lagrange_sphere: float
    lagrange_evaluator: float
    residual: float
    iterations: int
    index: int
    tangent_dimension: int
    energy_density: float


def _residual_and_jacobian(
    field: CubicField,
    evaluator: np.ndarray,
    tau: float,
    state: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    dimension = field.dimension
    x = state[:dimension]
    sphere_multiplier = state[dimension]
    evaluator_multiplier = state[dimension + 1]
    gradient = field.gradient(x)
    hessian = field.hessian(x)
    residual = np.concatenate(
        [
            gradient - sphere_multiplier * x - evaluator_multiplier * evaluator,
            [0.5 * (float(x @ x) - dimension)],
            [float(evaluator @ x) / np.sqrt(dimension) - tau],
        ]
    )
    jacobian = np.zeros((dimension + 2, dimension + 2))
    jacobian[:dimension, :dimension] = hessian - sphere_multiplier * np.eye(dimension)
    jacobian[:dimension, dimension] = -x
    jacobian[:dimension, dimension + 1] = -evaluator
    jacobian[dimension, :dimension] = x
    jacobian[dimension + 1, :dimension] = evaluator / np.sqrt(dimension)
    return residual, jacobian


def refine_boundary_critical_point(
    field: CubicField,
    evaluator: np.ndarray,
    tau: float,
    initial: np.ndarray,
    *,
    tolerance: float = 1e-8,
    max_iterations: int = 60,
) -> CriticalPoint | None:
    dimension = field.dimension
    x = project_to_constraints(initial, evaluator, tau)
    gradient = field.gradient(x)
    sphere_multiplier = float(x @ gradient) / dimension
    evaluator_multiplier = float(evaluator @ (gradient - sphere_multiplier * x))
    state = np.concatenate([x, [sphere_multiplier, evaluator_multiplier]])
    residual_norm = float("inf")
    for iteration in range(1, max_iterations + 1):
        residual, jacobian = _residual_and_jacobian(field, evaluator, tau, state)
        residual_norm = float(np.linalg.norm(residual))
        if residual_norm <= tolerance:
            break
        try:
            update = np.linalg.solve(jacobian, -residual)
        except np.linalg.LinAlgError:
            update = np.linalg.lstsq(jacobian, -residual, rcond=1e-10)[0]
        accepted = False
        for power in range(12):
            factor = 0.5**power
            candidate = state + factor * update
            candidate_residual, _ = _residual_and_jacobian(
                field, evaluator, tau, candidate
            )
            if np.linalg.norm(candidate_residual) < residual_norm:
                state = candidate
                accepted = True
                break
        if not accepted:
            return None
    if residual_norm > tolerance:
        return None
    x = project_to_constraints(state[:dimension], evaluator, tau)
    # Refit multipliers after the tiny constraint projection.
    gradient = field.gradient(x)
    design = np.column_stack([x, evaluator])
    multipliers = np.linalg.lstsq(design, gradient, rcond=None)[0]
    sphere_multiplier, evaluator_multiplier = map(float, multipliers)
    state = np.concatenate([x, multipliers])
    residual, _ = _residual_and_jacobian(field, evaluator, tau, state)
    residual_norm = float(np.linalg.norm(residual))
    if residual_norm > max(10 * tolerance, 1e-7):
        return None
    tangent = null_space(np.vstack([x, evaluator]))
    constrained = tangent.T @ (
        field.hessian(x) - sphere_multiplier * np.eye(dimension)
    ) @ tangent
    eigenvalues = np.linalg.eigvalsh(0.5 * (constrained + constrained.T))
    index = int(np.sum(eigenvalues < -1e-8))
    return CriticalPoint(
        x=x,
        lagrange_sphere=sphere_multiplier,
        lagrange_evaluator=evaluator_multiplier,
        residual=residual_norm,
        iterations=iteration,
        index=index,
        tangent_dimension=tangent.shape[1],
        energy_density=field.value(x) / dimension,
    )


def _deduplicate(points: Iterable[CriticalPoint], tolerance: float = 1e-5) -> list[dict[str, object]]:
    unique: list[dict[str, object]] = []
    for point in points:
        matched = None
        for item in unique:
            if np.linalg.norm(point.x - item["point"].x) <= tolerance:
                matched = item
                break
        if matched is None:
            unique.append({"point": point, "rediscoveries": 1})
        else:
            matched["rediscoveries"] += 1
    return unique


def run_sampler_cell(
    *,
    dimension: int,
    tau: float,
    disorder_seed: int,
    starts: int,
    sampler: str,
    quadratic_weight: float = 0.0,
) -> dict[str, object]:
    field = generate_field(dimension, disorder_seed, quadratic_weight=quadratic_weight)
    evaluator = evaluator_direction(dimension, disorder_seed ^ 0xA5A5A5A5)
    rng = np.random.default_rng(disorder_seed ^ 0x5A5A5A5A)
    points = []
    for _ in range(starts):
        initial = constrained_random_point(rng, evaluator, tau)
        if sampler == "descent_seeded":
            initial = seed_by_projected_flow(
                field, initial, evaluator, tau, direction=-1.0
            )
        elif sampler == "ascent_seeded":
            initial = seed_by_projected_flow(
                field, initial, evaluator, tau, direction=1.0
            )
        elif sampler != "newton_random":
            raise ValueError(f"unknown spin-glass sampler: {sampler}")
        point = refine_boundary_critical_point(field, evaluator, tau, initial)
        if point is not None:
            points.append(point)
    unique = _deduplicate(points)
    indices = np.array([item["point"].index for item in unique], dtype=float)
    fractions = np.array(
        [item["point"].index / max(1, item["point"].tangent_dimension) for item in unique],
        dtype=float,
    )
    rediscoveries = np.array([item["rediscoveries"] for item in unique], dtype=float)
    inverse_weights = 1.0 / rediscoveries if rediscoveries.size else rediscoveries
    weighted_fraction = (
        float(np.average(fractions, weights=inverse_weights)) if fractions.size else None
    )
    return {
        "dimension": dimension,
        "tau": tau,
        "disorder_seed": disorder_seed,
        "starts": starts,
        "sampler": sampler,
        "quadratic_weight": quadratic_weight,
        "converged_starts": len(points),
        "unique_critical_points": len(unique),
        "convergence_rate": len(points) / starts,
        "mean_index": float(np.mean(indices)) if indices.size else None,
        "mean_index_fraction": float(np.mean(fractions)) if fractions.size else None,
        "inverse_rediscovery_weighted_index_fraction": weighted_fraction,
        "minimum_index_fraction": float(np.min(fractions)) if fractions.size else None,
        "maximum_index_fraction": float(np.max(fractions)) if fractions.size else None,
        "mean_rediscoveries": float(np.mean(rediscoveries)) if rediscoveries.size else None,
        "evidence_label": "basin_weighted_newton_empirical",
    }
