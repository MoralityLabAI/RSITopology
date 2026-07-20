from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import run


HERE = Path(__file__).resolve().parent
PROTOCOL = json.loads((HERE / "protocol_v0_1.json").read_text(encoding="utf-8"))


def test_matched_kl_policies() -> None:
    reference = np.full(6, 1 / 6)
    proxy = run.normalize_centered(np.asarray([-5, -3, -1, 1, 3, 5], dtype=float), reference)
    target = 0.5 * math.log(6)
    for builder in (run.gibbs_policy, run.spike_policy):
        policy = builder(proxy, reference, target)
        assert np.all(policy >= 0)
        assert abs(float(np.sum(policy)) - 1.0) < 1e-12
        assert abs(run.kl_divergence(policy, reference) - target) < 1e-10


def test_best_of_n_distribution() -> None:
    proxy = np.asarray([-2, -1, 0, 1], dtype=float)
    policy = run.best_of_n_policy(proxy, 3)
    expected = np.asarray([(1 / 4) ** 3, (2 / 4) ** 3 - (1 / 4) ** 3, (3 / 4) ** 3 - (2 / 4) ** 3, 1 - (3 / 4) ** 3])
    assert np.allclose(policy, expected)
    assert abs(float(np.sum(policy)) - 1.0) < 1e-12


def test_controls_have_registered_polarity() -> None:
    supnorm = run.supnorm_positive_control(PROTOCOL)
    rare = run.rare_l2_negative_control(PROTOCOL)
    assert supnorm["pass"]
    assert supnorm["maximum_regret"] <= 2 * supnorm["epsilon"] + 1e-12
    assert rare["pass"]
    assert rare["reference_l2_error"] < 0.01
    assert rare["optimized_true_regret"] >= 0.9


def test_census_cardinality_without_reading_primary_outcome() -> None:
    raw, normalized = run.enumerate_true_rewards(PROTOCOL)
    assert raw.shape == (15620, 6)
    assert normalized.shape == (15620, 6)
    assert np.allclose(np.mean(normalized, axis=1), 0.0, atol=1e-12)
    assert np.allclose(np.mean(normalized * normalized, axis=1), 1.0, atol=1e-12)
