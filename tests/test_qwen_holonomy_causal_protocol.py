from __future__ import annotations

import json
from pathlib import Path

import pytest

from rsi_topology.qwen_holonomy_causal import (
    generate_causal_outer_manifest,
    validate_causal_outer_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
GEOMETRY_PATH = ROOT / "protocols" / "godel_globes_prompt_manifest_v0_1.json"
PROTOCOL_PATH = ROOT / "protocols" / "qwen_holonomy_causal_transfer_v0_1.json"


def test_outer_manifest_is_balanced_audited_and_byte_disjoint():
    geometry = json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
    value = generate_causal_outer_manifest(
        protocol_sha256="a" * 64,
        geometry_manifest_sha256="b" * 64,
    )
    validate_causal_outer_manifest(value, geometry_manifest=geometry)

    assert value["prompt_count"] == 576
    assert len({row["prompt_id"] for row in value["rows"]}) == 576
    assert {row["half"] for row in value["rows"]} == {"causal_outer"}
    assert not (
        {row["prompt"] for row in value["rows"]}
        & {row["prompt"] for row in geometry["rows"]}
    )
    graph_answers = {
        row["expected_answer"]
        for row in value["rows"]
        if row["behavior_family"] == "graph_reachability"
    }
    assert graph_answers == {"YES", "NO"}


def test_outer_manifest_rejects_geometry_prompt_reuse():
    geometry = json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
    value = generate_causal_outer_manifest(
        protocol_sha256="a" * 64,
        geometry_manifest_sha256="b" * 64,
    )
    value["rows"][0]["prompt"] = geometry["rows"][0]["prompt"]
    with pytest.raises(ValueError, match="overlap"):
        validate_causal_outer_manifest(value, geometry_manifest=geometry)


def test_protocol_has_fail_closed_geometry_and_causal_boundaries():
    value = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    assert value["new_invariant_levels"] is False
    assert value["development_model"]["ambient_dimension"] == 1024
    assert len(value["development_model"]["states"]) == 4
    assert value["stage_1_geometry"]["primary_lineage_floor"] == 0.9
    assert value["stage_1_geometry"]["stop_states"]["beta_1_zero"] == (
        "report holonomy_unavailable"
    )
    assert value["stage_2_prereveal_candidate_table"]["entry_condition"].startswith(
        "At least one"
    )
    assert value["resource_contract"]["local_uncapped_execution_prohibited"] is True
    assert value["vpd_handoff"]["condition"] == (
        "Only after confirmatory causal_holonomy_supported"
    )
