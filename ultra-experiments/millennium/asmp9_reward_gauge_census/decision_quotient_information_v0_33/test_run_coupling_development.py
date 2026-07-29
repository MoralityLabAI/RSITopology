from __future__ import annotations

from .run_coupling_development import build_report


def test_coupling_report_binds_actual_objects_and_claim_boundary() -> None:
    report = build_report()
    assert report["claim_status"] == "development_only_unregistered"
    assert len(report["source_hashes"]) == 5
    assert report["actual_objects"] == {
        "analysis_map_shape": [3, 8],
        "policy_matrix_shape": [6, 3],
        "semantic_operator_shape": [6, 12],
        "coupling_shape": [8, 6],
    }
    full = report["full_policy_family"]
    assert full["raw_coupling_dimension"] == 48
    assert full["decision_relevant_dimension"] == 18
    assert full["decision_null_gauge_dimension"] == 30
    assert len(full["independent_canonical_row_indices"]) == 18
    restricted = report["restricted_two_policy_control"]
    assert restricted["decision_relevant_dimension"] == 6
    assert restricted["decision_null_gauge_dimension"] == 42
    witnesses = report["witnesses"]
    assert witnesses["nonzero_decision_null_coupling"]["coupling_entries"]
    assert not witnesses["nonzero_decision_null_coupling"]["effect_entries"]
    assert witnesses["decision_changing_coordinate_coupling"]["effect_entries"]
    assert not any(report["claim_boundary"].values())
