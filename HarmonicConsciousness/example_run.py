"""Deterministic synthetic example; prints a machine-readable evidence receipt."""
from __future__ import annotations

import json

import numpy as np

from HarmonicConsciousness.probe import (
    circular_shift_null,
    effective_rank,
    localized_time_average,
    sampled_time_average,
)


def run() -> dict:
    w = np.array([0.5, 1.25, 2.5, 3.0])
    q = np.eye(4)
    a = np.array([1.0, 0.4 + 0.2j, 0.3j, 0.6])
    b = np.array([[1.0, 0.6, 0.3, -0.1]])
    result = localized_time_average(w, q, a, b, 32.0)
    numerical = sampled_time_average(w, q, a, b, 32.0, samples=20001)
    rng = np.random.default_rng(20261027)
    length = 1600
    base = np.linspace(0, 32 * np.pi, length)
    drift = np.cumsum(rng.normal(0.0, 0.15, length))
    first = base + drift + rng.normal(0.0, 0.05, length)
    second = base + drift + 0.3 + rng.normal(0.0, 0.05, length)
    return {
        "status": "synthetic_only",
        "awareness_inference": "none",
        "seed": 20261027,
        "finite_wave": {
            **result,
            "sampled_time_average": numerical,
            "analytic_quadrature_absolute_error": abs(result["time_average"] - numerical),
            "bound_holds": abs(result["interference"]) <= result["interference_bound"] + 1e-12,
        },
        "temporal_phase": circular_shift_null(first, second, seed=17, minimum_shift=200),
        "effective_rank_identity_4d": effective_rank(np.eye(4)),
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
