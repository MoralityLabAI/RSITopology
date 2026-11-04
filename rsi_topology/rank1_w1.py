"""Rank-one sign holonomy and first Stiefel--Whitney diagnostics.

For a real line bundle, an orthogonal edge transport is a sign in O(1).  Node
frame flips change the edge-sign cochain by a coboundary, while the product
around a closed loop is invariant.  The resulting loop character is the first
Stiefel--Whitney class on the measured graph.

This module deliberately contains no new attestation level.  It supplies
diagnostics for rank-one objects already admitted by the lineage graph.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping, Sequence

import numpy as np
from scipy.stats import beta


Array = np.ndarray


@dataclass(frozen=True)
class LoopInterval:
    """A rectangular loop spanning context columns ``start`` through ``stop``."""

    start: int
    stop: int

    def __post_init__(self) -> None:
        if self.start < 0 or self.stop <= self.start:
            raise ValueError("loop interval must have 0 <= start < stop")

    @property
    def generator_vector(self) -> tuple[int, ...]:
        return tuple(1 for _ in range(self.start, self.stop))


def rank_one_between_class_basis(
    features: Array, labels: Array, *, dtype: np.dtype | type = np.float64
) -> Array:
    """Return a top between-class direction using the requested arithmetic."""

    kind = np.dtype(dtype)
    if kind not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise ValueError("rank-one analysis supports float32 or float64")
    values = np.asarray(features, dtype=kind)
    classes = np.asarray(labels)
    if values.ndim != 2 or len(values) != len(classes):
        raise ValueError("features must be a matrix with one label per row")
    unique = np.unique(classes)
    if len(unique) < 2 or not np.all(np.isfinite(values)):
        raise ValueError("rank-one between-class basis needs finite multi-class data")
    means = np.stack(
        [np.mean(values[classes == item], axis=0, dtype=kind) for item in unique]
    )
    means -= np.mean(means, axis=0, keepdims=True, dtype=kind)
    _, singular_values, right = np.linalg.svd(means, full_matrices=False)
    if not len(singular_values) or float(singular_values[0]) <= 0.0:
        raise ValueError("between-class scatter is degenerate")
    basis = np.asarray(right[0], dtype=kind)
    basis /= np.linalg.norm(basis)
    return basis


def edge_transport_sign(
    source: Array, target: Array, *, degeneracy_floor: float = 1e-8
) -> int:
    """Return the O(1) polar factor of the rank-one overlap."""

    left = np.asarray(source).reshape(-1)
    right = np.asarray(target).reshape(-1)
    if left.shape != right.shape:
        raise ValueError("rank-one frames must share an ambient dimension")
    overlap = float(np.dot(left, right))
    if not math.isfinite(overlap) or abs(overlap) <= degeneracy_floor:
        raise ValueError("rank-one overlap is sign-degenerate")
    return 1 if overlap > 0.0 else -1


def rectangular_loop_sign(
    bases: Mapping[tuple[str, int], Array],
    *,
    states: Sequence[str],
    interval: LoopInterval,
    degeneracy_floor: float = 1e-8,
) -> int:
    """Measure the sign around a two-state, contiguous-context rectangle."""

    if len(states) != 2:
        raise ValueError("a rectangular loop requires exactly two states")
    first, second = map(str, states)
    path = [(first, value) for value in range(interval.start, interval.stop + 1)]
    path.extend(
        (second, value) for value in range(interval.stop, interval.start - 1, -1)
    )
    sign = 1
    for source, target in zip(path, path[1:] + path[:1]):
        sign *= edge_transport_sign(
            bases[source], bases[target], degeneracy_floor=degeneracy_floor
        )
    return int(sign)


def predict_composite_sign(generator_signs: Sequence[int], interval: LoopInterval) -> int:
    """Evaluate a contiguous composite class from elementary generator signs."""

    if interval.stop > len(generator_signs):
        raise ValueError("composite interval exceeds generator universe")
    sign = 1
    for value in generator_signs[interval.start : interval.stop]:
        if value not in (-1, 1):
            raise ValueError("generator signs must lie in {-1, +1}")
        sign *= int(value)
    return sign


def gf2_rank(rows: Sequence[Sequence[int]]) -> int:
    """Compute exact row rank over GF(2)."""

    if not rows:
        return 0
    matrix = np.asarray(rows, dtype=np.uint8) % 2
    if matrix.ndim != 2:
        raise ValueError("GF(2) rows must form a matrix")
    rank = 0
    for column in range(matrix.shape[1]):
        pivots = np.flatnonzero(matrix[rank:, column])
        if not len(pivots):
            continue
        pivot = rank + int(pivots[0])
        matrix[[rank, pivot]] = matrix[[pivot, rank]]
        for row in range(matrix.shape[0]):
            if row != rank and matrix[row, column]:
                matrix[row] ^= matrix[rank]
        rank += 1
        if rank == matrix.shape[0]:
            break
    return rank


def exact_uniform_class_probability(constraint_rank: int) -> float:
    """Probability that a uniform Z/2 cohomology class satisfies all constraints."""

    if constraint_rank < 0:
        raise ValueError("constraint rank cannot be negative")
    return float(2.0 ** (-constraint_rank))


def clopper_pearson(
    successes: int, trials: int, *, confidence: float = 0.95
) -> tuple[float, float]:
    """Two-sided exact binomial interval."""

    if trials < 1 or successes < 0 or successes > trials:
        raise ValueError("invalid binomial counts")
    alpha = 1.0 - confidence
    lower = 0.0 if successes == 0 else float(beta.ppf(alpha / 2, successes, trials - successes + 1))
    upper = 1.0 if successes == trials else float(beta.ppf(1 - alpha / 2, successes + 1, trials - successes))
    return lower, upper


def bootstrap_rank_one_basis(
    features: Array,
    labels: Array,
    rng: np.random.Generator,
    *,
    dtype: np.dtype | type = np.float64,
) -> Array:
    """Stratified row bootstrap of a rank-one between-class direction."""

    class_values = np.asarray(labels)
    chosen: list[int] = []
    for item in np.unique(class_values):
        members = np.flatnonzero(class_values == item)
        chosen.extend(rng.choice(members, size=len(members), replace=True).tolist())
    selected = np.asarray(chosen, dtype=np.int64)
    return rank_one_between_class_basis(
        np.asarray(features)[selected], class_values[selected], dtype=dtype
    )


def permuted_rank_one_basis(
    features: Array,
    labels: Array,
    rng: np.random.Generator,
    *,
    dtype: np.dtype | type = np.float64,
) -> Array:
    """Matched label-permutation basis preserving label multiplicities."""

    permuted = np.asarray(labels).copy()
    rng.shuffle(permuted)
    return rank_one_between_class_basis(features, permuted, dtype=dtype)
