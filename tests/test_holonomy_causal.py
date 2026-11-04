from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from rsi_topology.holonomy_causal import (
    build_rank_four_loop,
    evaluate_causal_transfer,
    two_path_transports,
)
from rsi_topology.holonomy import canonical_rotation_angles_degrees


ROOT = Path(__file__).resolve().parents[1]


def test_rank_four_fixture_has_exposed_and_flat_rotation_planes() -> None:
    flat = build_rank_four_loop("flat_flat", steps=8, step_size=0.1)
    curved = build_rank_four_loop("curved_flat", steps=8, step_size=0.1)
    assert flat[0].shape == (8, 4)
    assert curved[0].shape == (8, 4)
    flat_pair = two_path_transports(flat)
    curved_pair = two_path_transports(curved)
    assert np.allclose(flat_pair.holonomy, np.eye(4), atol=1e-10)
    angles = canonical_rotation_angles_degrees(curved_pair.holonomy)
    assert len(angles) == 2
    assert angles[0] < 1e-8
    assert angles[1] > 30.0


def test_two_path_displacement_is_rooted_loop_displacement() -> None:
    frames = build_rank_four_loop("curved_flat", steps=6, step_size=0.08)
    pair = two_path_transports(frames)
    rng = np.random.default_rng(41)
    for _ in range(16):
        direction = rng.normal(size=4)
        direction /= np.linalg.norm(direction)
        direct = np.linalg.norm(pair.forward @ direction - pair.backward @ direction)
        loop = np.linalg.norm((pair.holonomy - np.eye(4)) @ direction)
        assert abs(direct - loop) < 1e-10


def test_small_causal_falsification_passes_all_registered_polarities() -> None:
    result = evaluate_causal_transfer(
        step_sizes=(0.12,),
        causal_map_replicates=6,
        edit_norms=(0.5, 1.0),
        bootstrap_draws=64,
    )
    assert result["decision"] == "pass"
    assert result["all_gates_pass"] is True
    assert result["metrics"]["false_authorization_count"] == 0
    assert result["metrics"]["maximum_bound_excess"] <= 1e-10
    assert result["prediction"]["relative_sse_reduction"] > 0.25
    assert (
        result["prediction"]["relative_sse_reduction"]
        > result["permuted_holonomy_prediction"]["relative_sse_reduction"]
    )
    assert result["gauge_preflight"]["maximum_discrepancy"] <= 1e-9
    assert result["orientation_control"]["authorized"] is False


def test_causal_protocol_preserves_invariant_ceiling_and_real_model_stop() -> None:
    value = json.loads(
        (ROOT / "protocols" / "holonomy_causal_transfer_falsification_v0_1.json")
        .read_text(encoding="utf-8")
    )
    assert value["status"] == "registered_before_canonical_run"
    assert value["new_invariant_levels"] is False
    assert value["invariant_levels"] == [
        "engineering_evidence",
        "lineage_certified",
        "holonomy_clean",
    ]
    handoff = value["real_model_handoff"]
    assert "causal_outer" in handoff["required_splits"]
    assert "beta_1>0" in handoff["entry_condition"]
    assert "holonomy_unavailable" in handoff["natural_collapse"]
