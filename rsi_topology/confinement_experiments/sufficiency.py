"""Synthetic evaluator-sufficiency audit scaling on spherical fibers."""

from __future__ import annotations

from math import ceil, exp, expm1, log, log1p
from typing import Sequence

import numpy as np
from scipy.special import betaln, hyp2f1


def log_spherical_cap_probability(dimension: int, threshold: float) -> float:
    """Log probability of a spherical cap without high-dimensional underflow."""

    if dimension < 2:
        raise ValueError("fiber dimension must be at least two")
    if not -1.0 <= threshold <= 1.0:
        raise ValueError("threshold must lie in [-1, 1]")
    if threshold == 1.0:
        return float("-inf")
    if threshold == -1.0:
        return 0.0
    if threshold == 0:
        return log(0.5)
    if threshold > 0:
        # 0.5 * I_(1-c^2)((q-1)/2, 1/2), evaluated through the
        # hypergeometric incomplete-beta identity in log space.
        a = 0.5 * (dimension - 1)
        x = 1.0 - threshold**2
        hypergeometric = float(hyp2f1(a, 0.5, a + 1.0, x))
        if not np.isfinite(hypergeometric) or hypergeometric <= 0:
            raise FloatingPointError("spherical-cap hypergeometric evaluation failed")
        return float(
            log(0.5)
            + a * log(x)
            - log(a)
            + log(hypergeometric)
            - betaln(a, 0.5)
        )
    positive_log = log_spherical_cap_probability(dimension, -threshold)
    return log1p(-exp(positive_log))


def spherical_cap_probability(dimension: int, threshold: float) -> float:
    """Probability that w.T y >= threshold for y uniform on S^(q-1)."""

    log_probability = log_spherical_cap_probability(dimension, threshold)
    return 0.0 if log_probability < log(np.nextafter(0.0, 1.0)) else exp(log_probability)


def random_probe_budget_95(cap_probability: float) -> int:
    if not 0.0 < cap_probability <= 1.0:
        raise ValueError("cap probability must lie in (0, 1]")
    if cap_probability == 1.0:
        return 1
    return int(ceil(log(0.05) / log1p(-cap_probability)))


def sample_unit_vectors(rng: np.random.Generator, count: int, dimension: int) -> np.ndarray:
    values = rng.normal(size=(count, dimension))
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise RuntimeError("zero Gaussian direction sampled")
    return values / norms


def sparse_direction(rng: np.random.Generator, dimension: int, sparsity: int) -> np.ndarray:
    if not 1 <= sparsity <= dimension:
        raise ValueError("sparsity must lie in [1, dimension]")
    support = rng.choice(dimension, size=sparsity, replace=False)
    values = np.zeros(dimension)
    values[support] = rng.choice((-1.0, 1.0), size=sparsity)
    return values / np.linalg.norm(values)


def random_probe_trial(
    rng: np.random.Generator,
    *,
    dimension: int,
    threshold: float,
    probes: int,
    hidden_direction: np.ndarray | None = None,
) -> bool:
    direction = (
        sample_unit_vectors(rng, 1, dimension)[0]
        if hidden_direction is None
        else np.asarray(hidden_direction, dtype=float)
    )
    audit = sample_unit_vectors(rng, probes, dimension)
    return bool(np.any(audit @ direction >= threshold))


def coordinate_probe_detects(hidden_direction: Sequence[float], threshold: float) -> bool:
    direction = np.asarray(hidden_direction, dtype=float)
    # Both signs of every coordinate axis are included in this structured bank.
    return bool(np.max(np.abs(direction)) >= threshold)


def post_design_adversary_undetected(
    audit_vectors: np.ndarray,
    threshold: float,
    *,
    tolerance: float = 1e-10,
) -> bool:
    """Return whether a cap center can be chosen orthogonal to all frozen probes."""

    probes = np.asarray(audit_vectors, dtype=float)
    if probes.ndim != 2:
        raise ValueError("audit_vectors must be a matrix")
    rank = int(np.linalg.matrix_rank(probes, tol=tolerance))
    return bool(rank < probes.shape[1] and threshold > tolerance)


def evaluate_audit_cell(
    *,
    dimension: int,
    threshold: float,
    probes: int,
    sparsity: int,
    trials: int,
    seed: int,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    log_cap_probability = log_spherical_cap_probability(dimension, threshold)
    cap_probability = spherical_cap_probability(dimension, threshold)
    random_hits = sum(
        random_probe_trial(
            rng,
            dimension=dimension,
            threshold=threshold,
            probes=probes,
        )
        for _ in range(trials)
    )
    coordinate_hits = 0
    adversarial_undetected = 0
    for _ in range(trials):
        direction = sparse_direction(rng, dimension, sparsity)
        coordinate_hits += coordinate_probe_detects(direction, threshold)
        audit = sample_unit_vectors(rng, probes, dimension)
        adversarial_undetected += post_design_adversary_undetected(audit, threshold)
    if cap_probability > 0:
        analytic_detection = -expm1(probes * log1p(-cap_probability))
        k95: int | None = random_probe_budget_95(cap_probability)
        log10_k95 = log(k95) / log(10.0)
    else:
        log_detection = log(probes) + log_cap_probability
        analytic_detection = 0.0 if log_detection < -745.0 else exp(log_detection)
        k95 = None
        log10_k95 = (log(-log(0.05)) - log_cap_probability) / log(10.0)
    empirical_detection = random_hits / trials
    standard_error = np.sqrt(
        max(analytic_detection * (1.0 - analytic_detection), 1.0 / trials)
        / trials
    )
    return {
        "dimension": dimension,
        "threshold": threshold,
        "cap_probability": cap_probability,
        "log_cap_probability": log_cap_probability,
        "probes": probes,
        "sparsity": sparsity,
        "trials": trials,
        "analytic_random_detection": analytic_detection,
        "empirical_random_detection": empirical_detection,
        "random_detection_absolute_error": abs(empirical_detection - analytic_detection),
        "random_detection_standardized_error": abs(
            empirical_detection - analytic_detection
        )
        / standard_error,
        "coordinate_sparse_detection": coordinate_hits / trials,
        "oracle_known_direction_detection": 1.0,
        "post_design_adversary_undetected": adversarial_undetected / trials,
        "k95": k95,
        "log10_k95": log10_k95,
        "evidence_label": "monte_carlo_empirical_with_analytic_random_baseline",
    }
