from __future__ import annotations

import numpy as np
import pytest

from rsi_topology.confinement_experiments.linear import (
    aligned_box_cover_bits,
    classify_split_rate,
    evaluator_relevant_modes,
    finite_horizon_volume_lower_bits,
    unstable_entropy_bits,
)
from rsi_topology.confinement_experiments.sufficiency import (
    log_spherical_cap_probability,
    random_probe_budget_95,
    spherical_cap_probability,
)


def test_unstable_entropy_tracks_spectrum_not_mode_count():
    spectra = ([2.0], [np.sqrt(2.0), np.sqrt(2.0)], [2.0 ** 0.25] * 4)
    assert [unstable_entropy_bits(values) for values in spectra] == pytest.approx(
        [1.0, 1.0, 1.0]
    )


def test_scalar_finite_horizon_cover_matches_margin_correction():
    for horizon, expected in ((1, 0), (2, 0), (3, 1), (5, 3)):
        assert finite_horizon_volume_lower_bits([2.0], horizon, [0.25], [1.0]) == expected
        assert aligned_box_cover_bits([2.0], horizon, [0.25], [1.0]) == expected


def test_split_channels_cannot_trade_read_bits_for_write_bits():
    failed = classify_split_rate([2.0], 0.5, 1.5, 8, [0.25], [1.0])
    passed = classify_split_rate([2.0], 1.0, 1.0, 8, [0.25], [1.0])
    assert failed["classification"] == "certified_infeasible"
    assert passed["classification"] == "constructive_feasible"


def test_stable_plant_is_zero_rate_constructively_feasible():
    result = classify_split_rate([0.8, 0.9], 0.0, 0.0, 50, [0.5, 0.5], [1, 1])
    assert result["classification"] == "constructive_feasible"


def test_tangent_modes_become_evaluator_relevant_only_with_top_right_coupling():
    normal = np.array([1.0, 0.0, 0.0])
    uncoupled = np.diag([1.2, 1.1, 1.3])
    coupled = uncoupled.copy()
    coupled[0, 1:] = [0.1, 0.1]
    base = evaluator_relevant_modes(uncoupled, normal)
    mixed = evaluator_relevant_modes(coupled, normal)
    assert base.evaluator_unstable_index == 1
    assert mixed.evaluator_unstable_index == 3
    assert mixed.local_entropy == pytest.approx(base.local_entropy)


def test_spherical_cap_budget_formula_has_correct_ratio_orientation():
    assert spherical_cap_probability(3, -1.0) == 1.0
    assert spherical_cap_probability(3, 0.0) == pytest.approx(0.5)
    assert spherical_cap_probability(3, 1.0) == 0.0
    assert random_probe_budget_95(0.5) == 5
    probability = spherical_cap_probability(16, 0.7)
    budget = random_probe_budget_95(probability)
    assert 1.0 - (1.0 - probability) ** budget >= 0.95
    assert 1.0 - (1.0 - probability) ** (budget - 1) < 0.95
    assert random_probe_budget_95(1e-30) > 10**29
    assert log_spherical_cap_probability(1024, 0.9) < -745
    assert spherical_cap_probability(1024, 0.9) == 0.0
