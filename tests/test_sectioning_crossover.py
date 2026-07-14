from __future__ import annotations

import numpy as np
import pytest

from rsi_topology.sectioning import section_edits
from rsi_topology.sectioning_crossover import (
    _analytic_terms,
    _ordered_cells,
    _patch_indices,
    _simulate_cell,
    _truth_angles,
    run_sectioning_crossover_v03,
)
from rsi_topology.sectioning_synthetic import build_sectioning_fixture


def fixture_parts():
    plan = section_edits(build_sectioning_fixture("mixed_curvature"), 0.05)
    cells = _ordered_cells(plan)
    return cells, _patch_indices(plan, cells)


def test_recoupled_bias_is_zero_and_decoupled_bias_is_positive():
    cells, patches = fixture_parts()
    assert _analytic_terms(_truth_angles(len(cells), 0), patches)["patch_bias_squared"] == 0.0
    assert _analytic_terms(_truth_angles(len(cells), 1), patches)["patch_bias_squared"] > 0.0


def test_analytic_patch_independent_formula_is_exact_at_zero_noise():
    cells, patches = fixture_parts()
    truth = _truth_angles(len(cells), 1)
    result = _simulate_cell(truth, patches, sigma=0.0, observations=1, replicates=8, seed=1)
    assert result["empirical_patch_minus_independent"] == pytest.approx(
        result["analytic_patch_minus_independent"], abs=1e-12
    )


def test_registered_crossover_gates_and_connector_pass():
    result = run_sectioning_crossover_v03(replicates=128)
    assert result["gates"]["recoupled_regression"]
    assert result["gates"]["all_decoupled_defect_regimes"]
    assert result["gates"]["connector_audit"]
    assert result["capacity_accounting"]["maximum_norm_error"] < 1e-12
