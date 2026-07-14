from __future__ import annotations

import numpy as np
from scipy.linalg import expm

from rsi_topology.holonomy import (
    build_grassmann_loop,
    canonical_rotation_angles_degrees,
    evaluate_grassmann_loop,
    evaluate_perimeter_area_control,
    holonomy_phase_degrees,
    holonomy_orientation_receipt,
    holonomy_score,
    loop_holonomy,
)


def _rotation(angle: float) -> np.ndarray:
    cosine, sine = np.cos(angle), np.sin(angle)
    return np.array([[cosine, -sine], [sine, cosine]], dtype=np.float64)


def test_flat_and_curved_loops_match_local_lineage_but_not_holonomy() -> None:
    flat = evaluate_grassmann_loop("flat")
    curved = evaluate_grassmann_loop("curved")

    assert flat["minimum_edge_worst_direction_retention"] >= 0.99
    assert curved["minimum_edge_worst_direction_retention"] >= 0.99
    assert abs(
        flat["minimum_edge_worst_direction_retention"]
        - curved["minimum_edge_worst_direction_retention"]
    ) < 1e-12
    assert flat["holonomy_determinant"] > 0.0
    assert curved["holonomy_determinant"] > 0.0
    assert not flat["orientation_reversal_flag"]
    assert not curved["orientation_reversal_flag"]
    assert abs(flat["holonomy_phase_degrees"]) < 1e-9
    assert abs(curved["holonomy_phase_degrees"]) > 45.0
    assert curved["mean_signed_monitor_return"] < 0.60
    assert abs(flat["block_energy_return"] - 1.0) < 1e-12
    assert abs(curved["block_energy_return"] - 1.0) < 1e-12


def test_holonomy_trace_is_invariant_under_local_frame_gauges() -> None:
    fixture = build_grassmann_loop("curved", steps=6, step_size=0.08)
    original = loop_holonomy(fixture.frames)
    gauges = tuple(_rotation(0.19 * index) for index in range(len(fixture.frames)))
    reframed = tuple(
        frame @ gauge for frame, gauge in zip(fixture.frames, gauges)
    )
    transformed = loop_holonomy(reframed)

    expected = gauges[0].T @ original.matrix @ gauges[0]
    assert np.allclose(transformed.matrix, expected, atol=1e-10)
    assert abs(transformed.identity_loss - original.identity_loss) < 1e-12
    assert abs(
        holonomy_phase_degrees(transformed.matrix)
        - holonomy_phase_degrees(original.matrix)
    ) < 1e-10


def test_reversing_loop_inverts_holonomy() -> None:
    frames = build_grassmann_loop("curved", steps=5, step_size=0.1).frames
    forward = loop_holonomy(frames).matrix
    reversed_from_same_base = (frames[0], *reversed(frames[1:]))
    backward = loop_holonomy(reversed_from_same_base).matrix

    assert np.allclose(backward, forward.T, atol=1e-10)


def test_small_curved_plaquette_phase_scales_with_area() -> None:
    small = loop_holonomy(
        build_grassmann_loop("curved", steps=1, step_size=0.02).frames
    )
    large = loop_holonomy(
        build_grassmann_loop("curved", steps=1, step_size=0.04).frames
    )
    small_phase = abs(holonomy_phase_degrees(small.matrix))
    large_phase = abs(holonomy_phase_degrees(large.matrix))

    assert 3.95 < large_phase / small_phase < 4.05


def test_holonomy_score_is_average_signed_identity_loss() -> None:
    angle = np.deg2rad(60.0)
    matrix = _rotation(angle)

    assert abs(holonomy_score(matrix) - (1.0 - np.cos(angle))) < 1e-12


def test_orientation_reversal_supersedes_canonical_angle_summary() -> None:
    reflection = np.diag([-1.0, 1.0])
    receipt = holonomy_orientation_receipt(reflection)

    assert receipt["holonomy_determinant"] == -1.0
    assert receipt["orientation_reversal_flag"]
    assert receipt["canonical_angle_status"] == "superseded_by_orientation_reversal"
    with np.testing.assert_raises(ValueError):
        canonical_rotation_angles_degrees(reflection)


def _haar_special_orthogonal(rank: int, rng: np.random.Generator) -> np.ndarray:
    value, _ = np.linalg.qr(rng.normal(size=(rank, rank)))
    if np.linalg.det(value) < 0.0:
        value[:, 0] *= -1.0
    return value


def test_rank_six_haar_reframing_preserves_holonomy_conjugacy_class() -> None:
    rng = np.random.default_rng(20260711)
    ambient = 10
    rank = 6
    base, _ = np.linalg.qr(rng.normal(size=(ambient, rank)), mode="reduced")
    frames = []
    for _ in range(7):
        raw = rng.normal(size=(ambient, ambient))
        skew = raw - raw.T
        frames.append(expm(0.025 * skew) @ base)
    original = loop_holonomy(frames)
    gauges = tuple(_haar_special_orthogonal(rank, rng) for _ in frames)
    reframed = tuple(frame @ gauge for frame, gauge in zip(frames, gauges))
    transformed = loop_holonomy(reframed)

    expected = gauges[0].T @ original.matrix @ gauges[0]
    original_angles = canonical_rotation_angles_degrees(original.matrix)
    transformed_angles = canonical_rotation_angles_degrees(transformed.matrix)
    assert np.allclose(transformed.matrix, expected, atol=1e-10)
    assert np.allclose(transformed_angles, original_angles, atol=1e-9)
    assert len(original_angles) == 3


def test_registered_noise_null_separates_perimeter_and_area_scaling() -> None:
    result = evaluate_perimeter_area_control()

    assert result["reference_worst_direction_retention_absolute_error"] < 0.002
    assert result["noise_variance_vs_perimeter_fit"]["slope"] > 0.0
    assert result["noise_variance_vs_perimeter_fit"]["r_squared"] > 0.90
    assert result["curvature_phase_vs_area_fit"]["slope"] > 0.0
    assert result["curvature_phase_vs_area_fit"]["r_squared"] > 0.995
    analytic = result["analytic_origin_curvature"]
    assert abs(
        analytic["maximum_canonical_rotation_rate_degrees_per_unit_area"]
        - 85.37071147449267
    ) < 1e-10
    assert result["curvature_fit_slope_relative_error_from_analytic_origin"] < 0.03
