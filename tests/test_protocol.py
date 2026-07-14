from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str) -> dict:
    return json.loads((ROOT / "protocols" / name).read_text(encoding="utf-8"))


def test_v0_2_1_preserves_v0_2_primary_gates() -> None:
    old = load("spectral_bundle_discovery_v0_2.json")
    new = load("spectral_bundle_discovery_v0_2_1.json")

    assert new["amends"] == old["protocol_id"]
    assert new["primary_gates_unchanged"] is True
    assert new["geometry_gate"]["minimum_consensus_occupancy"] == old[
        "geometry_gate"
    ]["minimum_consensus_occupancy"]
    assert new["geometry_gate"]["minimum_consensus_rank"] == old["geometry_gate"][
        "minimum_consensus_rank"
    ]
    assert new["policy_gate"]["maximum_kl_from_uniform"] == old["policy_gate"][
        "maximum_kl_from_uniform"
    ]
    assert new["policy_gate"]["minimum_relative_mse_improvement"] == old[
        "policy_gate"
    ]["minimum_relative_mse_improvement"]
    assert new["policy_gate"]["minimum_standardized_heldout_return_uplift"] == old[
        "policy_gate"
    ]["minimum_standardized_heldout_return_uplift"]
    assert new["direct_edit_gate"] == old["direct_edit_gate"]
    assert "descriptive" in new["policy_gate"]["realized_ic"]
    assert "smallest positive" in new["standing_controls"][
        "sparse_geometry_noise"
    ]["rng_stream_note"]


def test_lineage_followup_is_proposal_only_and_preserves_parent() -> None:
    followup = load("spectral_bundle_lineage_followup_v0_1.json")

    assert followup["parent_protocol"] == "rsi-topology-spectral-bundle-v0.2.1"
    assert followup["status"] == "proposal_only_target_blind_diagnostic"
    assert followup["primary_parent_gates_unchanged"] is True
    assert "smallest strictly positive" in followup["reference_rule"][
        "synthetic_sweeps"
    ]
    assert "feature_table_sha256" in followup["sealing"][
        "required_receipt_fields"
    ]
    assert "descriptive" in followup["evaluation"]["status_rule"]


def test_v0_2_2_adds_band_attribution_without_gate_changes() -> None:
    old = load("spectral_bundle_discovery_v0_2_1.json")
    new = load("spectral_bundle_discovery_v0_2_2.json")

    assert new["amends"] == old["protocol_id"]
    assert new["primary_gates_unchanged"] is True
    assert new["geometry_gate"] == old["geometry_gate"]
    for key in (
        "maximum_kl_from_uniform",
        "minimum_relative_mse_improvement",
        "minimum_standardized_heldout_return_uplift",
    ):
        assert new["policy_gate"][key] == old["policy_gate"][key]
    assert new["direct_edit_gate"] == old["direct_edit_gate"]
    assert new["band_attribution"]["sweep_grouping_key"] == "selected_band"


def test_lineage_v0_1_1_requires_within_band_incremental_value() -> None:
    amendment = load("spectral_bundle_lineage_followup_v0_1_1.json")

    assert amendment["amends"] == (
        "rsi-topology-spectral-bundle-lineage-followup-v0.1"
    )
    assert amendment["parent_protocol"] == (
        "rsi-topology-spectral-bundle-v0.2.2"
    )
    assert amendment["primary_parent_gates_unchanged"] is True
    assert "Within selected-band strata" in amendment["evaluation"][
        "primary_question"
    ]
    assert "complete_consensus_occupancy_spectrum" in amendment[
        "load_bearing_control"
    ]["held_fixed"]


def test_lineage_angle_calibration_has_complete_grid_and_no_new_threshold() -> None:
    calibration = load("lineage_angle_calibration_v0_1.json")

    assert calibration["fixture"]["seeds"] == [20260711, 20260712, 20260713]
    assert calibration["fixture"]["rotation_degrees"] == list(range(0, 91, 5))
    assert calibration["execution"]["hard_cap_wrapper_required"] is True
    assert calibration["execution"]["outcome_tuned_gate_changes"] == "prohibited"
    assert "prohibited as thresholds" in calibration["shape_diagnostics"][
        "policy_and_edit_flip_locations"
    ]
