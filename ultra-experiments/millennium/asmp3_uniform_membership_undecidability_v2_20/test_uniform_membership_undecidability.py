from __future__ import annotations

import json

from uniform_membership_undecidability import (
    ACTIVE_GAP,
    ARTIFACT_PATH,
    active_at_depth,
    build_artifact,
    fixed_game_specification,
    macro_firewall_rows,
    prior_exact_boundary_audit,
    reduction_audit,
    resource_rows,
    source_and_class_audit,
    transition_rows,
    vector_pair_audit,
)
from verify_uniform_membership_undecidability import verify


def test_source_registers_computability_boundary_and_strict_FIX_class() -> None:
    audit = source_and_class_audit()
    assert audit["certified"]
    assert audit["class_definition"]["name"] == "WV-FIX-UCOMP"
    assert audit["class_definition"]["interface_quantifier"] == "G_d fixed before protocol algorithms"


def test_interface_is_fixed_and_noise_is_nonzero_and_complete() -> None:
    spec = fixed_game_specification()
    assert spec["interface_selected_at_protocol_time"] is False
    assert spec["query_budget"] == 1
    assert "BSC(1/5)" in spec["noise"]
    assert "but not z" in spec["verifier_information"]
    assert "fixed one-round vector interface" in spec["legal_protocol_scope"]
    assert spec["abstention_allowed"] is False


def test_every_coordinate_atom_passes_full_answer_firewall() -> None:
    rows = macro_firewall_rows()
    assert len(rows) == 63
    assert all(row["one_coordinate_never_determines_parity"] for row in rows)
    assert not any(row["full_answer_atomic_query_present"] for row in rows)
    assert all(row["certified"] for row in rows)


def test_all_registered_resources_are_polylogarithmic_in_T() -> None:
    rows = resource_rows()
    assert len(rows) == 63
    assert all(row["semantic_queries"] == 1 for row in rows)
    assert all(row["all_resources_polylog_T"] for row in rows)


def test_active_vector_game_has_exact_gap_three_fifths() -> None:
    for depth in range(2, 10):
        row = vector_pair_audit(depth, True)
        assert row["exact_optimal_gap"] == str(ACTIVE_GAP)
        assert row["every_opposite_parity_pair_differs"]
        assert row["certified"]


def test_inactive_vector_game_has_exact_gap_zero() -> None:
    for depth in range(2, 10):
        row = vector_pair_audit(depth, False)
        assert row["exact_optimal_gap"] == "0"
        assert row["certified"]


def test_halting_machine_has_eventually_zero_gap() -> None:
    for halt_time in (1, 2, 5, 17, 64):
        assert all(not active_at_depth(halt_time, depth) for depth in range(max(2, halt_time), halt_time + 20))


def test_nonhalting_machine_has_gap_three_fifths_at_every_depth() -> None:
    assert all(active_at_depth(None, depth) for depth in range(2, 1000))
    rows = [row for row in transition_rows() if row["machine_fixture"] == "NEVER"]
    assert len(rows) == 72
    assert all(row["exact_gap"] == "3/5" for row in rows)


def test_NONHALT_reduction_and_index_set_consequences_are_recorded() -> None:
    audit = reduction_audit(transition_rows())
    assert audit["certified"]
    assert all(audit["proof_obligations"].values())
    assert audit["consequences"]["WV_FIX_UCOMP_index_set_decidable"] is False
    assert audit["consequences"]["WV_FIX_UCOMP_positive_index_set_recursively_enumerable"] is False


def test_finite_explicit_boundary_remains_exact() -> None:
    audit = prior_exact_boundary_audit()
    assert audit["certified"]
    assert all(audit["checks"].values())


def test_all_ten_producer_gates_pass_without_parent_resolution_overclaim() -> None:
    artifact = build_artifact()
    assert artifact["certified"]
    assert len(artifact["gates"]) == 10
    assert all(artifact["gates"].values())
    assert artifact["resolution_effect"]["unconditional_parent_resolution"] is False


def test_written_artifact_and_clean_room_verifier_match() -> None:
    assert json.loads(ARTIFACT_PATH.read_text(encoding="utf-8")) == build_artifact()
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 10
