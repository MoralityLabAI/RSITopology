"""Pure utilities for rank-one projector interaction tomography."""

from __future__ import annotations

from itertools import combinations
import math
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


def response_rms(cube: np.ndarray) -> float:
    """RMS causal response over every non-baseline mask and prompt."""

    values = np.asarray(cube, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != 16 or not np.all(np.isfinite(values)):
        raise ValueError("cube must be a finite prompts-by-16 matrix")
    deltas = values[:, 1:] - values[:, [0]]
    return float(np.sqrt(np.mean(deltas**2)))


def select_scale_matched_alpha(
    selected_scale: float,
    random_scales: Mapping[float, float],
    *,
    minimum_ratio: float = 0.8,
    maximum_ratio: float = 1.25,
) -> dict[str, float | bool]:
    """Apply the frozen nearest-log-scale rule with a lower-alpha tie break."""

    if not np.isfinite(selected_scale) or selected_scale <= 0.0:
        raise ValueError("selected scale must be finite and positive")
    if not random_scales:
        raise ValueError("random alpha grid is empty")
    rows = []
    for alpha, scale in random_scales.items():
        if not np.isfinite(alpha) or alpha <= 0.0 or not np.isfinite(scale) or scale <= 0.0:
            raise ValueError("alpha and scale values must be finite and positive")
        ratio = float(scale / selected_scale)
        rows.append((abs(math.log(ratio)), float(alpha), ratio))
    _, alpha, ratio = min(rows, key=lambda item: (item[0], item[1]))
    return {
        "alpha": alpha,
        "random_over_selected_ratio": ratio,
        "passed": bool(minimum_ratio <= ratio <= maximum_ratio),
    }


def fold_sign_decision(values: Iterable[float], *, required: int = 8) -> dict[str, int | float | str]:
    """Frozen success/failure decision for nine paired subcondition effects."""

    items = np.asarray(tuple(values), dtype=np.float64)
    if items.shape != (9,) or not np.all(np.isfinite(items)):
        raise ValueError("exactly nine finite fold effects are required")
    positive = int(np.sum(items > 0.0))
    negative = int(np.sum(items < 0.0))
    if positive >= required:
        decision = "pass"
        tail_count = positive
    elif negative >= required:
        decision = "fail"
        tail_count = negative
    else:
        decision = "inconclusive"
        tail_count = max(positive, negative)
    p_value = sum(math.comb(9, k) for k in range(tail_count, 10)) / 2**9
    return {
        "decision": decision,
        "positive": positive,
        "negative": negative,
        "ties": 9 - positive - negative,
        "one_sided_sign_p": float(p_value),
    }


__all__ = [
    "design_matrix",
    "exact_boolean_coefficients",
    "interaction_order_energy",
    "monomial_subsets",
    "orthogonal_random_direction",
    "reconstruct_rank_one",
    "relative_sse_reduction",
    "response_rms",
    "select_scale_matched_alpha",
    "fold_sign_decision",
]
