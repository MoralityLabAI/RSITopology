from __future__ import annotations

import numpy as np
import pytest

from rsi_topology.confinement_experiments.spin_glass import generate_field, run_sampler_cell


def test_cubic_gradient_and_hessian_match_finite_differences():
    field = generate_field(5, 7, quadratic_weight=0.2)
    rng = np.random.default_rng(8)
    x = rng.normal(size=5)
    direction = rng.normal(size=5)
    epsilon = 1e-6
    value_difference = (
        field.value(x + epsilon * direction) - field.value(x - epsilon * direction)
    ) / (2 * epsilon)
    assert value_difference == pytest.approx(field.gradient(x) @ direction, rel=1e-6, abs=1e-6)
    gradient_difference = (
        field.gradient(x + epsilon * direction)
        - field.gradient(x - epsilon * direction)
    ) / (2 * epsilon)
    assert gradient_difference == pytest.approx(field.hessian(x) @ direction, rel=1e-5, abs=1e-5)


def test_tiny_sampler_reports_basin_weighted_boundary():
    result = run_sampler_cell(
        dimension=6,
        tau=0.0,
        disorder_seed=11,
        starts=4,
        sampler="newton_random",
    )
    assert result["evidence_label"] == "basin_weighted_newton_empirical"
    assert 0 <= result["converged_starts"] <= 4
    assert 0.0 <= result["convergence_rate"] <= 1.0
