from __future__ import annotations

from dataclasses import replace

import pytest

from rsi_topology.attestation import AnchorRegistry
from rsi_topology.sectioning import authorize_patch, persistence_curve, rank_audit_placements, section_edits
from rsi_topology.sectioning_synthetic import build_sectioning_fixture, run_frozen_sectioning_gates
from test_attestation import make_record


def test_mixed_curvature_sections_into_two_maximal_patches():
    fixture = build_sectioning_fixture("mixed_curvature")
    plan = section_edits(fixture, 0.05)
    assert plan["status"] == "multi_patch_section"
    assert plan["edit_count"] == 2
    assert [len(item["plaquette_ids"]) for item in plan["patches"]] == [4, 4]
    assert all(item["holonomy_margin"] == pytest.approx(0.038) for item in plan["patches"])
    assert all(item["required_certification"] == "holonomy_clean" for item in plan["patches"])


def test_uniform_curvature_refuses_to_manufacture_patches():
    plan = section_edits(build_sectioning_fixture("uniformly_curved"), 0.05)
    assert plan["status"] == "no_admissible_multi_patch_section"
    assert plan["edit_count"] == 0


def test_persistence_emits_birth_and_merge_death_receipts():
    result = persistence_curve(build_sectioning_fixture("mixed_curvature"), [0.0, 0.012, 0.05, 0.202])
    assert [row["edit_count"] for row in result["curve"]] == [0, 2, 2, 1]
    deaths = [row for row in result["component_birth_death_receipts"] if row["death_budget"] is not None]
    assert len(deaths) == 1
    assert deaths[0]["death_budget"] == pytest.approx(0.202)
    assert deaths[0]["merged_into"] is not None


def test_audit_module_ranks_only_unmeasured_loops():
    result = rank_audit_placements(build_sectioning_fixture("audit_incomplete"), 0.05)
    ids = [row["plaquette_id"] for row in result["audit_ranking"]]
    assert ids == ["p-3", "p-5", "p-4"]
    assert all(row["audit_rank"] == index for index, row in enumerate(result["audit_ranking"], 1))


def test_patch_authorization_delegates_to_existing_certify_api():
    plan = section_edits(build_sectioning_fixture("mixed_curvature"), 0.05)
    registry = AnchorRegistry(records=[make_record()])
    mapping = {node: "layer.12.mlp" for node in plan["patches"][0]["node_ids"]}
    decision = authorize_patch(plan["patches"][0], registry, mapping)
    assert decision["authorized"]
    lineage_only = AnchorRegistry(records=[make_record(angle=8.0)])
    assert not authorize_patch(plan["patches"][0], lineage_only, mapping)["authorized"]


def test_frozen_cpu_gates_pass_and_norms_are_matched():
    result = run_frozen_sectioning_gates()
    assert result["all_gates_pass"]
    utility = result["gates"]["utility"]
    assert utility["matched_total_rank"] == {
        "patch_plan": 8,
        "one_global_edit": 8,
        "per_context_independent": 8,
        "patch_padding_rule": "allocate total rank across patches proportional to cell count; only the registered signed coordinate is active",
    }
    assert utility["maximum_observed_norm_error"] < 1e-12
    assert result["gates"]["estimation_noise_stability"]["patch_count_exceedance_band"] == [2, 2]


def test_orientation_reversing_cell_is_never_admitted():
    fixture = build_sectioning_fixture("mixed_curvature")
    cells = list(fixture.plaquettes)
    cells[0] = replace(
        cells[0],
        det_h_flag=True,
        identity_loss=1.0,
        identity_loss_lower_bound=1.0,
        identity_loss_upper_bound=1.0,
    )
    edges = list(fixture.edges)
    edges[0] = replace(edges[0], transport_matrix=((-1.0, 0.0), (0.0, 1.0)))
    plan = section_edits(replace(fixture, edges=tuple(edges), plaquettes=tuple(cells)), 0.05)
    excluded = {row["plaquette_id"]: row["reason"] for row in plan["excluded_plaquettes"]}
    assert excluded["p-0"] == "orientation_reversal"


def test_low_lineage_edge_breaks_patch_admission():
    fixture = build_sectioning_fixture("mixed_curvature")
    edges = list(fixture.edges)
    edges[0] = replace(edges[0], minimum_edge_worst_direction_retention=0.5)
    plan = section_edits(replace(fixture, edges=tuple(edges)), 0.05)
    excluded = {row["plaquette_id"]: row["reason"] for row in plan["excluded_plaquettes"]}
    assert excluded["p-0"] == "edge_lineage_below_threshold"


def test_plaquette_scalar_must_match_interval_and_boundary_holonomy():
    fixture = build_sectioning_fixture("mixed_curvature")
    cells = list(fixture.plaquettes)
    cells[0] = replace(
        cells[0],
        identity_loss=0.01,
        identity_loss_lower_bound=0.0,
        identity_loss_upper_bound=0.02,
    )
    edges = list(fixture.edges)
    edges[0] = replace(edges[0], transport_matrix=((0.0, -1.0), (1.0, 0.0)))
    with pytest.raises(ValueError, match="loss disagrees"):
        section_edits(replace(fixture, edges=tuple(edges), plaquettes=tuple(cells)), 0.05)
