from __future__ import annotations

from fractions import Fraction

import numpy as np
import pytest

from rsi_topology.ultra.transient_amplification import (
    boundary_decision,
    classify_jordan_radius,
    finite_horizon_gain,
    jordan_chain,
    jordan_exact_gain_bounds,
    maximum_sampled_gain,
    metric_norm,
    normal_control,
    reframe_operator,
    sample_metric_unit_directions,
    spectral_radius,
    worst_case_trajectory,
)


def test_matched_spectrum_can_hide_transient_failure() -> None:
    normal = normal_control(8, 0.9)
    nonnormal = jordan_chain(8, 0.9, 0.2)
    assert np.allclose(
        np.sort_complex(np.linalg.eigvals(normal)),
        np.sort_complex(np.linalg.eigvals(nonnormal)),
        atol=1e-12,
    )
    assert spectral_radius(normal) == pytest.approx(0.9)
    assert spectral_radius(nonnormal) == pytest.approx(0.9)

    normal_gain = finite_horizon_gain(normal, 40)
    nonnormal_gain = finite_horizon_gain(nonnormal, 40)
    assert boundary_decision(normal_gain.gain, initial_radius=0.05, safety_radius=0.5)
    assert not boundary_decision(
        nonnormal_gain.gain, initial_radius=0.05, safety_radius=0.5
    )


def test_singular_vector_is_an_exact_registered_time_witness() -> None:
    operator = jordan_chain(8, 0.9, 0.2)
    result = finite_horizon_gain(operator, 40)
    trajectory = worst_case_trajectory(operator, result, initial_radius=0.05)
    observed = metric_norm(trajectory[-1])
    assert observed == pytest.approx(0.05 * result.gain, rel=1e-12, abs=1e-12)


def test_metric_covariance_under_joint_coordinate_change() -> None:
    operator = jordan_chain(6, 0.88, 0.19)
    metric = np.diag([0.7, 1.1, 1.3, 0.8, 1.6, 0.9])
    rng = np.random.default_rng(42)
    coordinate_map = rng.normal(size=(6, 6)) + 2.5 * np.eye(6)
    reframed, reframed_metric = reframe_operator(operator, metric, coordinate_map)
    original_gain = finite_horizon_gain(operator, 30, metric=metric)
    reframed_gain = finite_horizon_gain(reframed, 30, metric=reframed_metric)
    assert reframed_gain.gain == pytest.approx(original_gain.gain, rel=1e-10)


def test_random_probes_are_only_a_lower_bound() -> None:
    operator = jordan_chain(8, 0.9, 0.2)
    exact = finite_horizon_gain(operator, 40)
    directions = sample_metric_unit_directions(8, 512, seed=123)
    sampled, _, _ = maximum_sampled_gain(operator, directions, 40)
    assert sampled <= exact.gain + 1e-10


def test_invalid_metric_is_rejected() -> None:
    operator = normal_control(2, 0.9)
    with pytest.raises(ValueError, match="positive definite"):
        finite_horizon_gain(operator, 3, metric=np.diag([1.0, 0.0]))


def test_closed_boundary_passes_at_equality() -> None:
    assert boundary_decision(10.0, initial_radius=0.05, safety_radius=0.5)


def test_exact_rational_bounds_certify_registered_polarities() -> None:
    passing = jordan_exact_gain_bounds(8, Fraction(9, 10), Fraction(0, 1), 40)
    failing = jordan_exact_gain_bounds(8, Fraction(9, 10), Fraction(1, 5), 40)
    assert classify_jordan_radius(
        passing,
        initial_radius=Fraction(1, 20),
        safety_radius=Fraction(1, 2),
    ) == "pass"
    assert classify_jordan_radius(
        failing,
        initial_radius=Fraction(1, 20),
        safety_radius=Fraction(1, 2),
    ) == "fail"


def test_registered_alternative_metric_flips_the_decision() -> None:
    euclidean = jordan_exact_gain_bounds(8, Fraction(9, 10), Fraction(1, 5), 40)
    scaled = jordan_exact_gain_bounds(8, Fraction(9, 10), Fraction(3, 20), 40)
    radius = Fraction(1, 20)
    boundary = Fraction(1, 2)
    assert classify_jordan_radius(
        euclidean, initial_radius=radius, safety_radius=boundary
    ) == "fail"
    assert classify_jordan_radius(
        scaled, initial_radius=radius, safety_radius=boundary
    ) == "pass"
