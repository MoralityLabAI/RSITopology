"""Target-blind localization diagnostics for functional-lineage failures.

The registered construction uses the minimum held-out retention as its safety
gate.  This module does not replace that rule.  It decomposes a failed gate so
that a later, separately registered estimator can address the observed source
of instability without retrospectively relaxing the original threshold.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import numpy as np


def spectral_endpoint(
    singular_values: np.ndarray,
    *,
    rank: int,
    relative_floor: float,
    minimum_boundary_gap_ratio: float,
) -> dict[str, Any]:
    """Classify a local spectral endpoint using the registered v2 rules."""

    values = np.asarray(singular_values, dtype=np.float64)
    if values.ndim != 1 or not np.isfinite(values).all() or len(values) == 0:
        raise ValueError("singular values must be a finite nonempty vector")
    if rank < 1 or rank > len(values):
        raise ValueError("rank is outside the singular-value vector")
    maximum = float(values[0])
    spectral_ratio = (
        float(values[rank - 1] / maximum) if maximum > 0.0 else 0.0
    )
    boundary_gap = (
        float("inf")
        if rank == len(values)
        else float(values[rank - 1] / max(values[rank], np.finfo(float).tiny))
    )
    if maximum <= 0.0 or spectral_ratio < relative_floor:
        status = "below_spectral_floor"
    elif boundary_gap < minimum_boundary_gap_ratio:
        status = "unresolved_boundary"
    else:
        status = "local_endpoint_pass"
    return {
        "status": status,
        "eligible": status == "local_endpoint_pass",
        "spectral_ratio": spectral_ratio,
        "boundary_gap_ratio": boundary_gap,
    }


def projector_from_signature(signature: np.ndarray, rank: int) -> np.ndarray:
    """Return the gauge-invariant top-rank left-singular projector."""

    matrix = np.asarray(signature, dtype=np.float64)
    if matrix.ndim != 2 or not np.isfinite(matrix).all():
        raise ValueError("signature must be a finite matrix")
    if rank < 1 or rank > min(matrix.shape):
        raise ValueError("rank is outside the signature dimensions")
    left, _values, _right = np.linalg.svd(matrix, full_matrices=False)
    basis = left[:, :rank]
    return basis @ basis.T


def consensus_basis(
    projectors: Mapping[Any, np.ndarray],
    fit_cells: Sequence[Any],
    *,
    rank: int,
    minimum_consensus_gap_ratio: float,
) -> tuple[np.ndarray, float]:
    """Fit the registered consensus basis and return its boundary gap."""

    if not fit_cells:
        raise ValueError("fit cells must be nonempty")
    matrices = [np.asarray(projectors[cell], dtype=np.float64) for cell in fit_cells]
    consensus = np.mean(matrices, axis=0)
    values, vectors = np.linalg.eigh((consensus + consensus.T) / 2.0)
    order = np.argsort(values)[::-1]
    values = values[order]
    vectors = vectors[:, order]
    if rank > len(values):
        raise ValueError("consensus rank exceeds ambient dimension")
    gap = (
        float("inf")
        if rank == len(values)
        else float(values[rank - 1] / max(values[rank], np.finfo(float).tiny))
    )
    if gap < minimum_consensus_gap_ratio:
        raise ValueError("consensus rank cuts through an unresolved spectral band")
    return vectors[:, :rank], gap


def heldout_retention_rows(
    projectors: Mapping[Any, np.ndarray],
    folds: Sequence[tuple[str, Sequence[Any], Sequence[Any]]],
    *,
    rank: int,
    minimum_consensus_gap_ratio: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Materialize one target-blind retention row for every evaluation cell."""

    rows: list[dict[str, Any]] = []
    fold_receipts: list[dict[str, Any]] = []
    seen: set[Any] = set()
    for name, fit_cells, evaluation_cells in folds:
        if not evaluation_cells:
            raise ValueError("evaluation cells must be nonempty")
        basis, gap = consensus_basis(
            projectors,
            fit_cells,
            rank=rank,
            minimum_consensus_gap_ratio=minimum_consensus_gap_ratio,
        )
        fold_worst: list[float] = []
        fold_mean: list[float] = []
        for cell in evaluation_cells:
            if cell in seen:
                raise ValueError("evaluation cells must occur in exactly one fold")
            seen.add(cell)
            overlap = basis.T @ np.asarray(projectors[cell]) @ basis
            overlap = (overlap + overlap.T) / 2.0
            eigenvalues = np.linalg.eigvalsh(overlap)
            worst = float(np.min(eigenvalues))
            energy = float(np.trace(overlap) / rank)
            fold_worst.append(worst)
            fold_mean.append(energy)
            rows.append(
                {
                    "fold": name,
                    "cell": cell,
                    "worst_direction_retention": worst,
                    "gauge_invariant_energy_retention": energy,
                }
            )
        fold_receipts.append(
            {
                "fold": name,
                "fit_cell_count": len(fit_cells),
                "evaluation_cell_count": len(evaluation_cells),
                "consensus_boundary_gap_ratio": gap,
                "worst_direction_retention": min(fold_worst),
                "mean_principal_retention": float(np.mean(fold_mean)),
            }
        )
    if seen != set(projectors):
        raise ValueError("the evaluation-fold union must equal the projector universe")
    return rows, fold_receipts


def quantile_receipt(values: Iterable[float]) -> dict[str, float]:
    array = np.asarray(tuple(values), dtype=np.float64)
    if array.ndim != 1 or len(array) == 0 or not np.isfinite(array).all():
        raise ValueError("quantiles require finite values")
    return {
        "minimum": float(np.min(array)),
        "q01": float(np.quantile(array, 0.01)),
        "q05": float(np.quantile(array, 0.05)),
        "q10": float(np.quantile(array, 0.10)),
        "q25": float(np.quantile(array, 0.25)),
        "median": float(np.median(array)),
        "mean": float(np.mean(array)),
        "q75": float(np.quantile(array, 0.75)),
        "maximum": float(np.max(array)),
    }


def fragility_curve(values: Iterable[float], threshold: float) -> dict[str, Any]:
    """Return the floor after excluding the x worst cells, for every x."""

    ordered = np.sort(np.asarray(tuple(values), dtype=np.float64))
    if ordered.ndim != 1 or len(ordered) == 0 or not np.isfinite(ordered).all():
        raise ValueError("fragility curve requires finite values")
    if not np.isfinite(threshold):
        raise ValueError("threshold must be finite")
    points = [
        {
            "excluded_worst_cells": excluded,
            "remaining_cells": int(len(ordered) - excluded),
            "retention_floor": float(ordered[excluded]),
            "margin_to_registered_null": float(ordered[excluded] - threshold),
        }
        for excluded in range(len(ordered))
    ]
    below_or_equal = int(np.sum(ordered <= threshold))
    return {
        "cell_count": int(len(ordered)),
        "cells_at_or_below_threshold": below_or_equal,
        "fraction_at_or_below_threshold": float(below_or_equal / len(ordered)),
        "exclusions_required_to_cross_threshold": (
            below_or_equal if below_or_equal < len(ordered) else None
        ),
        "remaining_fraction_at_crossing": (
            float((len(ordered) - below_or_equal) / len(ordered))
            if below_or_equal < len(ordered)
            else None
        ),
        "points": points,
    }


def balanced_axis_decomposition(
    rows: Sequence[Mapping[str, Any]],
    *,
    value_field: str,
    axes: Sequence[str],
) -> dict[str, Any]:
    """Orthogonal main-effect sums of squares for a balanced factorial table."""

    if not rows:
        raise ValueError("axis decomposition requires rows")
    y = np.asarray([float(row[value_field]) for row in rows], dtype=np.float64)
    if not np.isfinite(y).all():
        raise ValueError("axis decomposition values must be finite")
    grand = float(np.mean(y))
    total_ss = float(np.sum((y - grand) ** 2))
    result: dict[str, Any] = {
        "value_field": value_field,
        "grand_mean": grand,
        "total_sum_squares": total_ss,
        "axes": {},
    }
    explained = 0.0
    for axis in axes:
        levels = sorted({str(row[axis]) for row in rows})
        counts = {level: sum(str(row[axis]) == level for row in rows) for level in levels}
        if len(set(counts.values())) != 1:
            raise ValueError(f"axis {axis} is not balanced")
        level_means = {
            level: float(
                np.mean(
                    [float(row[value_field]) for row in rows if str(row[axis]) == level]
                )
            )
            for level in levels
        }
        per_level = next(iter(counts.values()))
        ss = float(
            per_level * sum((level_means[level] - grand) ** 2 for level in levels)
        )
        explained += ss
        result["axes"][axis] = {
            "sum_squares": ss,
            "fraction_total": float(ss / total_ss) if total_ss > 0.0 else 0.0,
            "level_means": level_means,
            "level_counts": counts,
            "mean_range": float(max(level_means.values()) - min(level_means.values())),
        }
    result["residual_sum_squares"] = max(0.0, total_ss - explained)
    result["residual_fraction_total"] = (
        float(max(0.0, total_ss - explained) / total_ss) if total_ss > 0.0 else 0.0
    )
    return result


def leave_one_level_out(
    rows: Sequence[Mapping[str, Any]],
    *,
    value_field: str,
    axis: str,
    threshold: float,
) -> list[dict[str, Any]]:
    """Diagnostic floor after excluding each complete level of an axis."""

    levels = sorted({str(row[axis]) for row in rows})
    result: list[dict[str, Any]] = []
    for level in levels:
        retained = [float(row[value_field]) for row in rows if str(row[axis]) != level]
        if not retained:
            raise ValueError("leave-one-level-out cannot remove every row")
        floor = float(np.min(retained))
        result.append(
            {
                "axis": axis,
                "excluded_level": level,
                "excluded_cell_count": int(len(rows) - len(retained)),
                "remaining_floor": floor,
                "margin_to_registered_null": float(floor - threshold),
            }
        )
    return result
