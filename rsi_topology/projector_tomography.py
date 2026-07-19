"""Pure utilities for rank-one projector interaction tomography."""

from __future__ import annotations

from itertools import combinations
from typing import Iterable, Mapping, Sequence

import numpy as np

from .discovery import _between_class_scatter_basis


def reconstruct_rank_one(
    activations: np.ndarray, labels: Sequence[str]
) -> tuple[np.ndarray, np.ndarray, float]:
    values = np.asarray(activations, dtype=np.float64)
    if values.ndim != 2 or len(values) != len(labels):
        raise ValueError("activations and labels must align")
    basis, eigenvalues = _between_class_scatter_basis(values, np.asarray(labels), 1)
    direction = basis[:, 0]
    # Preserve the exact SVD bytes used by the discovery receipt.  The vector
    # is already orthonormal; renormalizing would leave vv^T unchanged while
    # needlessly breaking receipt-level byte identity.
    if not np.isclose(np.linalg.norm(direction), 1.0, atol=1e-12):
        raise ValueError("discovery basis is not unit norm")
    center = np.mean(values, axis=0)
    return direction, center, float(eigenvalues[0])


def orthogonal_random_direction(
    selected: np.ndarray, *, seed: int
) -> np.ndarray:
    vector = np.asarray(selected, dtype=np.float64)
    if vector.ndim != 1 or not np.all(np.isfinite(vector)):
        raise ValueError("selected direction must be a finite vector")
    vector = vector / np.linalg.norm(vector)
    rng = np.random.default_rng(seed)
    random = rng.normal(size=len(vector))
    random -= vector * float(random @ vector)
    norm = np.linalg.norm(random)
    if norm <= 1e-12:
        raise ValueError("random control degenerated")
    return random / norm


def monomial_subsets(dimension: int, maximum_degree: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        subset
        for degree in range(1, maximum_degree + 1)
        for subset in combinations(range(dimension), degree)
    )


def design_matrix(bits: np.ndarray, maximum_degree: int) -> np.ndarray:
    values = np.asarray(bits, dtype=np.float64)
    if values.ndim != 2:
        raise ValueError("bits must be a matrix")
    terms = monomial_subsets(values.shape[1], maximum_degree)
    return np.column_stack([np.prod(values[:, subset], axis=1) for subset in terms])


def exact_boolean_coefficients(bits: np.ndarray, outcomes: np.ndarray) -> dict[tuple[int, ...], float]:
    values = np.asarray(bits, dtype=np.float64)
    target = np.asarray(outcomes, dtype=np.float64)
    if len(values) != len(target) or len(values) != 2 ** values.shape[1]:
        raise ValueError("a complete Boolean cube is required")
    columns = [np.ones(len(values))]
    terms: list[tuple[int, ...]] = [tuple()]
    for degree in range(1, values.shape[1] + 1):
        for subset in combinations(range(values.shape[1]), degree):
            terms.append(subset)
            columns.append(np.prod(values[:, subset], axis=1))
    matrix = np.column_stack(columns)
    coefficients = np.linalg.solve(matrix, target)
    return {term: float(value) for term, value in zip(terms, coefficients)}


def interaction_order_energy(coefficients: Mapping[tuple[int, ...], float]) -> dict[int, float]:
    result: dict[int, float] = {}
    for term, value in coefficients.items():
        if not term:
            continue
        result[len(term)] = result.get(len(term), 0.0) + float(value) ** 2
    return result


def relative_sse_reduction(y_true: np.ndarray, low: np.ndarray, high: np.ndarray) -> float:
    target = np.asarray(y_true, dtype=np.float64)
    low_sse = float(np.sum((target - np.asarray(low)) ** 2))
    high_sse = float(np.sum((target - np.asarray(high)) ** 2))
    if low_sse <= 1e-18:
        return 0.0
    return (low_sse - high_sse) / low_sse


__all__ = [
    "design_matrix",
    "exact_boolean_coefficients",
    "interaction_order_energy",
    "monomial_subsets",
    "orthogonal_random_direction",
    "reconstruct_rank_one",
    "relative_sse_reduction",
]
