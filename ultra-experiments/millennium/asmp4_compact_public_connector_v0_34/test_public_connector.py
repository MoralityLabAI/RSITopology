from __future__ import annotations

from fractions import Fraction

import compact_public_connector as central
import verify_public_connector as independent


def test_contract_claim_and_payload_are_exact() -> None:
    assert central.contract_report()["pass"]
    assert central.claim_report()["pass"]
    assert central.payload_report()["pass"]


def test_all_six_vertex_overlap_graphs_are_classified_twice() -> None:
    central_report = central.graph_census()
    independent_report = independent.independent_graph_census()
    assert central_report["pass"]
    assert independent_report["pass"]
    assert central_report["connected"] == independent_report["connected"] == 26704
    assert central_report["pair_rows"] == independent_report["pair_rows"] == 961344


def test_compact_interval_cover_has_uniform_vector_connector() -> None:
    report = central.interval_cover_report()
    assert report["pass"]
    assert independent.independent_interval_cover()["pass"]
    assert report["uniform_bound"] == {"time": 11, "read": 8, "write": 10}


def test_exact_finite_horizon_connector_correction() -> None:
    bound = central.ConnectorBound(time=11, read_cost=8, write_cost=10)
    closed = central.finite_horizon_region_bound((2048, 2048), 4096, bound)
    assert closed == (Fraction(2056, 4107), Fraction(2058, 4107))
    assert closed[0] < Fraction(51, 100)
    assert closed[1] < Fraction(51, 100)


def test_noncompact_ladder_refutes_uniform_connector_inference() -> None:
    report = central.noncompact_ladder_report()
    assert report["pass"]
    assert report["final_return_cost"] == 4096


def test_public_hidden_mode_requires_charged_read_information() -> None:
    assert central.public_hidden_state_report()["pass"]
    assert independent.independent_boundaries()["pass"]


def test_safe_overlap_and_private_memory_reset_are_load_bearing() -> None:
    assert central.unsafe_overlap_report()["pass"]
    assert central.private_memory_report()["pass"]


def test_compact_public_connector_discharge_v33_safe_closing() -> None:
    assert central.v33_bridge_report()["pass"]
    assert independent.independent_contract_claim()["pass"]


def test_eight_hostile_mutations_are_rejected_twice() -> None:
    assert central.mutation_report()["pass"]
    assert independent.independent_mutations()["pass"]


def test_independent_documents_inventory_and_full_reports_pass() -> None:
    assert central.predecessor_inventory_report()["pass"]
    assert independent.independent_inventory()["pass"]
    assert independent.document_report()["pass"]
    assert central.full_report()["pass"]
    assert independent.independent_report()["pass"]
