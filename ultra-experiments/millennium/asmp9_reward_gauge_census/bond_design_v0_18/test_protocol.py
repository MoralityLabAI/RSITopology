from __future__ import annotations

import json
from pathlib import Path

from bond_design import cactus_closed_form, cyclic_core_bonds
from run_verification import brute_minimal_bad_supports


HERE = Path(__file__).resolve().parent


def protocol() -> dict:
    return json.loads(
        (HERE / "protocol_v0_18.json").read_text(encoding="utf-8")
    )


def test_gate_registry_is_total() -> None:
    value = protocol()
    assert value["gate_ids"] == [
        "G0_registration_binding",
        "G1_fresh_graph_registry",
        "G2_scc_bad_supports_equal_bonds",
        "G3_bridge_exclusion_and_cut_completeness",
        "G4_primal_dual_cut_design_certificates",
        "G5_cactus_closed_form",
        "G6_structural_search_reduction",
        "G7_resource_and_scope",
    ]


def test_scientific_registry_schema_without_execution() -> None:
    value = protocol()
    assert set(value["graphs"]) == {
        "cactus_square_hexagon_bridge",
        "complete_bipartite_2_5",
        "complete_bipartite_3_4",
        "cube",
    }
    for raw in value["graphs"].values():
        certificate = raw["design_certificate"]
        assert len(raw["edges"]) == len(certificate["primal_weights"])
        assert certificate["dual_distribution"]
        assert "/" in certificate["threshold"]


def test_burned_cactus_and_scc_instrument_only() -> None:
    raw = protocol()["development_registry"]["extra_cactus"]
    edges = tuple(tuple(edge) for edge in raw["edges"])
    assert brute_minimal_bad_supports(
        int(raw["node_count"]), edges
    ) == cyclic_core_bonds(int(raw["node_count"]), edges)
    assert str(
        cactus_closed_form(int(raw["node_count"]), edges)["threshold"]
    ) == "2/7"


def test_premature_cells_remain_explicitly_burned() -> None:
    assert set(
        protocol()["development_registry"]["premature_v0_18_cells"]
    ) == {
        "cactus_triangle_pentagon_bridge",
        "complete_bipartite_2_4",
        "complete_bipartite_3_3",
        "triangular_prism",
    }


def test_claim_boundary_retains_resolution_exclusions() -> None:
    boundary = protocol()["claim_boundary"]
    for phrase in (
        "Not a novelty claim",
        "adaptive allocation",
        "behavioral reward-identification",
        "general IRL",
        "ASMP-9 resolution",
    ):
        assert phrase in boundary
