from __future__ import annotations

import numpy as np
import pytest

from HarmonicConsciousness.probe import (
    circular_shift_null,
    effective_rank,
    localized_time_average,
    phase_locking,
    sampled_time_average,
)


def test_finite_wave_analytic_identity_matches_independent_quadrature() -> None:
    w = np.array([0.5, 1.25, 2.5])
    q = np.eye(3)
    a = np.array([1.0, 0.4 + 0.2j, 0.3j])
    b = np.array([[1.0, 2.0, 0.5]])
    analytic = localized_time_average(w, q, a, b, 16.0)
    numeric = sampled_time_average(w, q, a, b, 16.0, 20001)
    assert abs(analytic["time_average"] - numeric) < 1e-6
    assert abs(analytic["interference"]) <= analytic["interference_bound"] + 1e-12
    assert analytic["distinct_frequency_count"] == 3


def test_interference_bound_decreases_with_duration() -> None:
    w = np.array([0.5, 1.25, 2.5])
    q = np.eye(3)
    a = np.ones(3)
    b = np.ones((1, 3))
    short = localized_time_average(w, q, a, b, 16.0)
    long = localized_time_average(w, q, a, b, 128.0)
    assert long["interference_bound"] < short["interference_bound"]
    assert abs(long["interference"]) <= long["interference_bound"] + 1e-12


def test_degenerate_mode_basis_rotation_preserves_energy() -> None:
    w = np.array([1.0, 1.0, 2.0])
    q = np.eye(3)
    a = np.array([1 + 1j, 0.2 - 0.4j, 0.7])
    b = np.array([[1.0, -2.0, 0.4], [0.2, 1.0, -0.5]])
    rotation = np.array([[np.cos(0.7), -np.sin(0.7)], [np.sin(0.7), np.cos(0.7)]])
    reframe = np.eye(3)
    reframe[:2, :2] = rotation
    rotated = localized_time_average(w, q @ reframe, reframe.T @ a, b, 8.0)
    original = localized_time_average(w, q, a, b, 8.0)
    assert rotated["distinct_frequency_count"] == 2
    for key in ("time_average", "incoherent_energy", "interference_bound"):
        assert abs(rotated[key] - original[key]) < 1e-12


def test_concentration_is_short_lived_in_example_without_claiming_local_smoothing() -> None:
    w = np.array([1.0, 2.0, 4.0])
    a = np.ones(3)
    b = np.ones((1, 3))
    at_zero = abs((b @ a)[0]) ** 2
    result = localized_time_average(w, np.eye(3), a, b, 50.0)
    assert at_zero == 9.0
    assert result["time_average"] < 3.2
    assert abs(result["interference"]) <= result["interference_bound"] + 1e-12


def test_effective_rank_and_invalid_covariance() -> None:
    assert effective_rank(np.eye(4)) == pytest.approx(4.0)
    assert effective_rank(np.diag([1, 0, 0])) == pytest.approx(1.0)
    assert effective_rank(np.zeros((2, 2))) == 0.0
    with pytest.raises(ValueError):
        effective_rank(np.diag([1.0, -0.2]))


def test_harmonic_phase_locking_constant_offset_invariant() -> None:
    t = np.linspace(0, 10, 1000)
    a = 2 * t
    b = t + 0.32
    assert phase_locking(a, b, 1, 2) == pytest.approx(1.0)
    assert phase_locking(a + 0.7, b - 1.2, 1, 2) == pytest.approx(1.0)


def test_shared_phase_jitter_beats_stationary_shift_null() -> None:
    rng = np.random.default_rng(20261027)
    length = 1600
    base = np.linspace(0, 32 * np.pi, length)
    drift = np.cumsum(rng.normal(0, 0.15, length))
    a = base + drift + rng.normal(0, 0.05, length)
    b = base + drift + 0.3 + rng.normal(0, 0.05, length)
    outcome = circular_shift_null(a, b, seed=17, minimum_shift=200, replicates=199)
    assert outcome["observed"] > 0.99
    assert outcome["observed"] > outcome["surrogate_mean"]
    assert outcome["p_upper_tail"] <= 0.05


def test_pure_tone_null_is_uninformative() -> None:
    t = np.arange(1000)
    a = 2 * np.pi * t / 100
    b = a + 0.2
    output = circular_shift_null(a, b, seed=44, minimum_shift=50, replicates=30)
    assert output["observed"] == pytest.approx(1.0)
    assert output["surrogate_mean"] == pytest.approx(1.0)


def test_invalid_wave_frames_and_horizon_raise() -> None:
    args = (np.array([1.0, 2.0]), np.array([[1.0, 1.0], [0.0, 1.0]]), np.ones(2), np.eye(2))
    with pytest.raises(ValueError):
        localized_time_average(*args, 10.0)
    with pytest.raises(ValueError):
        localized_time_average(np.array([1.0]), np.eye(1), np.ones(1), np.eye(1), 0.0)
