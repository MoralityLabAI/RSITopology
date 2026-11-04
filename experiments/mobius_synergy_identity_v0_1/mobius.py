"""Gauge-invariant subspace statistics for product-poset Möbius interactions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class GridEvaluation:
    """Rank receipts for one runtime × site × behavior-family grid."""

    receipts: tuple[dict[str, object], ...]
    observed_bases: dict[int, tuple[np.ndarray, np.ndarray]]
    unit_count: int
    plaquettes_per_shard: int


def mobius_coefficients(cells: np.ndarray) -> np.ndarray:
    """Return adjacent product-poset mixed differences for one factor grid.

    ``cells`` has shape ``(axis_a, axis_b, ambient_dimension)``. The result is
    ordered lexicographically by the upper-right plaquette coordinate.
    """

    value = np.asarray(cells, dtype=np.float64)
    if value.ndim != 3 or value.shape[0] < 2 or value.shape[1] < 2:
        raise ValueError("cells must have shape (a>=2, b>=2, ambient_dimension)")
    if not np.all(np.isfinite(value)):
        raise ValueError("cells contain non-finite values")
    mixed = (
        value[1:, 1:]
        - value[:-1, 1:]
        - value[1:, :-1]
        + value[:-1, :-1]
    )
    return mixed.reshape(-1, value.shape[-1])


def mobius_units(cells_by_shard: np.ndarray) -> np.ndarray:
    """Return one row per context-shard × adjacent plaquette unit."""

    value = np.asarray(cells_by_shard, dtype=np.float64)
    if value.ndim != 4 or value.shape[0] < 1:
        raise ValueError(
            "cells_by_shard must have shape (shard, axis_a, axis_b, ambient)"
        )
    return np.concatenate([mobius_coefficients(grid) for grid in value], axis=0)


def numerical_rank(rows: np.ndarray, relative_tolerance: float = 1e-10) -> int:
    value = np.asarray(rows, dtype=np.float64)
    if value.ndim != 2 or not len(value):
        return 0
    singular = np.linalg.svd(value, compute_uv=False, full_matrices=False)
    if not len(singular) or singular[0] <= 0:
        return 0
    return int(np.sum(singular > singular[0] * relative_tolerance))


def _decompose_rows(
    rows: np.ndarray, relative_tolerance: float = 1e-10
) -> tuple[np.ndarray, np.ndarray, int]:
    value = np.asarray(rows, dtype=np.float64)
    if value.ndim != 2 or not len(value):
        raise ValueError("rows must be a nonempty matrix")
    _, singular, right = np.linalg.svd(value, full_matrices=False)
    available = 0
    if len(singular) and singular[0] > 0:
        available = int(np.sum(singular > singular[0] * relative_tolerance))
    return right.T.copy(), singular.copy(), available


def basis_from_rows(rows: np.ndarray, rank: int) -> tuple[np.ndarray, np.ndarray]:
    """Return an ambient-space orthonormal basis and its singular values."""

    value = np.asarray(rows, dtype=np.float64)
    if value.ndim != 2 or rank < 1:
        raise ValueError("rows must be a matrix and rank must be positive")
    right, singular, available = _decompose_rows(value)
    if rank > available:
        raise ValueError(f"requested rank {rank} exceeds numerical rank {available}")
    return right[:, :rank].copy(), singular[:rank].copy()


def worst_principal_retention(reference: np.ndarray, current: np.ndarray) -> float:
    """Smallest principal cosine between equal-rank subspaces."""

    left = np.asarray(reference, dtype=np.float64)
    right = np.asarray(current, dtype=np.float64)
    if (
        left.ndim != 2
        or right.ndim != 2
        or left.shape != right.shape
        or left.shape[1] < 1
    ):
        raise ValueError("bases must have the same positive rank and ambient dimension")
    singular = np.linalg.svd(left.T @ right, compute_uv=False)
    return float(np.clip(np.min(singular), 0.0, 1.0))


def _permuted_axis_b(cells: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Independently permute factor-B labels within each shard and A row."""

    value = np.asarray(cells, dtype=np.float64)
    if value.ndim != 4:
        raise ValueError("permutation input must be a shard-indexed cell tensor")
    result = np.empty_like(value)
    for shard in range(value.shape[0]):
        for axis_a in range(value.shape[1]):
            order = rng.permutation(value.shape[2])
            result[shard, axis_a] = value[shard, axis_a, order]
    return result


def _retention_from_decompositions(
    left_basis: np.ndarray,
    left_available: int,
    right_basis: np.ndarray,
    right_available: int,
    rank: int,
) -> float:
    if rank > left_available or rank > right_available:
        return 0.0
    return worst_principal_retention(left_basis[:, :rank], right_basis[:, :rank])


def evaluate_grid(
    construction_cells: np.ndarray,
    validation_cells: np.ndarray,
    *,
    ranks: Iterable[int],
    bootstrap_replicates: int,
    permutation_replicates: int,
    lower_quantile: float,
    upper_quantile: float,
    minimum_strict_margin: float,
    seed: int,
) -> GridEvaluation:
    """Evaluate one cross-fitted interaction object against its registered null."""

    construction = np.asarray(construction_cells, dtype=np.float64)
    validation = np.asarray(validation_cells, dtype=np.float64)
    if construction.shape != validation.shape or construction.ndim != 4:
        raise ValueError("construction and validation cell tensors must match")
    if bootstrap_replicates < 1 or permutation_replicates < 1:
        raise ValueError("replicate counts must be positive")
    requested_ranks = tuple(sorted({int(rank) for rank in ranks if int(rank) > 0}))
    if not requested_ranks:
        raise ValueError("at least one positive rank is required")

    q_construction = mobius_units(construction)
    q_validation = mobius_units(validation)
    left_all, left_singular_all, left_available = _decompose_rows(q_construction)
    right_all, right_singular_all, right_available = _decompose_rows(q_validation)
    available = min(left_available, right_available)
    eligible_ranks = tuple(rank for rank in requested_ranks if rank <= available)
    rng = np.random.default_rng(seed)

    observed: dict[int, float] = {}
    bases: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    singular_by_rank: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for rank in eligible_ranks:
        left_basis = left_all[:, :rank]
        right_basis = right_all[:, :rank]
        left_singular = left_singular_all[:rank]
        right_singular = right_singular_all[:rank]
        observed[rank] = worst_principal_retention(left_basis, right_basis)
        bases[rank] = (left_basis, right_basis)
        singular_by_rank[rank] = (left_singular, right_singular)

    bootstrap: dict[int, list[float]] = {rank: [] for rank in eligible_ranks}
    unit_count = len(q_construction)
    for _ in range(bootstrap_replicates):
        indices = rng.integers(0, unit_count, size=unit_count)
        left_rows = q_construction[indices]
        right_rows = q_validation[indices]
        left_basis, _, left_available = _decompose_rows(left_rows)
        right_basis, _, right_available = _decompose_rows(right_rows)
        for rank in eligible_ranks:
            bootstrap[rank].append(
                _retention_from_decompositions(
                    left_basis,
                    left_available,
                    right_basis,
                    right_available,
                    rank,
                )
            )

    null_maxima: list[float] = []
    for _ in range(permutation_replicates):
        left_null = mobius_units(_permuted_axis_b(construction, rng))
        right_null = mobius_units(_permuted_axis_b(validation, rng))
        left_basis, _, left_available = _decompose_rows(left_null)
        right_basis, _, right_available = _decompose_rows(right_null)
        null_values = [
            _retention_from_decompositions(
                left_basis,
                left_available,
                right_basis,
                right_available,
                rank,
            )
            for rank in eligible_ranks
        ]
        null_maxima.append(max(null_values, default=1.0))
    null_upper = float(np.quantile(null_maxima, upper_quantile))

    receipts: list[dict[str, object]] = []
    for rank in requested_ranks:
        if rank not in eligible_ranks:
            receipts.append(
                {
                    "rank": rank,
                    "status": "unavailable_above_split_numerical_rank",
                    "available_rank": available,
                    "passed": False,
                }
            )
            continue
        lower = float(np.quantile(bootstrap[rank], lower_quantile))
        margin = lower - null_upper
        left_singular, right_singular = singular_by_rank[rank]
        receipts.append(
            {
                "rank": rank,
                "status": "evaluated",
                "available_rank": available,
                "observed_retention": observed[rank],
                "bootstrap_retention_lower_95": lower,
                "permutation_max_retention_upper_95": null_upper,
                "strict_margin": margin,
                "minimum_strict_margin": minimum_strict_margin,
                "passed": bool(margin > minimum_strict_margin),
                "construction_singular_values": left_singular.tolist(),
                "validation_singular_values": right_singular.tolist(),
            }
        )
    plaquettes = (construction.shape[1] - 1) * (construction.shape[2] - 1)
    return GridEvaluation(
        receipts=tuple(receipts),
        observed_bases=bases,
        unit_count=unit_count,
        plaquettes_per_shard=plaquettes,
    )
