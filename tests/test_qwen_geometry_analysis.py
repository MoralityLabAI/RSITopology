from __future__ import annotations

import json
from pathlib import Path

import pytest

from rsi_topology.qwen_geometry_analysis import (
    load_analysis_protocol,
    pair_analysis_protocol,
    pair_slug,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "protocols" / "qwen08_holonomy_geometry_analysis_v0_1.json"
DENSE_REGISTRATION = (
    ROOT / "protocols" / "qwen08_dense_local_holonomy_analysis_v0_1.json"
)


def test_registration_is_pairwise_target_blind_and_binds_captures():
    value = load_analysis_protocol(REGISTRATION)
    assert value["outcomes_consumed"] is False
    assert value["weight_mutation_performed"] is False
    assert value["new_invariant_levels"] is False
    assert value["primary_object"]["bootstrap_replicates"] == 128
    assert value["graph"]["lineage_floor"] == pytest.approx(0.90)
    assert len(value["state_capture_indices"]) == 4
    assert len(value["state_pairs"]) == 3
    assert all(pair[0] == "base" for pair in value["state_pairs"])


def test_pair_protocol_exposes_exactly_two_states_and_existing_levels():
    value = load_analysis_protocol(REGISTRATION)
    pair = ("base", "naive_qlora")
    view = pair_analysis_protocol(value, pair)
    assert view["runtime_precisions"] == list(pair)
    assert view["candidate_sites"] == [
        "model.layers.11",
        "model.layers.15",
        "model.layers.19",
        "model.layers.23",
    ]
    assert pair_slug(pair) == "base--vs--naive_qlora"
    with pytest.raises(ValueError, match="not registered"):
        pair_analysis_protocol(value, ("naive_qlora", "base"))


def test_bound_paths_and_hashes_have_canonical_shape():
    value = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    for entry in value["state_capture_indices"].values():
        assert Path(entry["path"]).is_absolute()
        assert len(entry["sha256"]) == 64


def test_dense_registration_binds_two_states_and_the_scientific_protocol():
    value = load_analysis_protocol(DENSE_REGISTRATION)
    assert value["status"] == "frozen_after_target_blind_capture_before_geometry_read"
    assert value["scientific_protocol"]["sha256"] == (
        "964d979372dac37b65746c9018d1629b9bb3223a045c26eb82d3967c189d1518"
    )
    assert set(value["state_capture_indices"]) == {"base", "naive_qlora"}
    assert value["state_pairs"] == [["base", "naive_qlora"]]
    assert value["graph"]["expected_beta_1_if_fully_connected"] == 3
    assert value["new_invariant_levels"] is False
