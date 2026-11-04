from __future__ import annotations

import json

from normative_closure_reassessment import (
    ARTIFACT_PATH,
    authority_and_progress_audit,
    build_artifact,
    interface_delta_audit,
    prior_claim_audit,
    resolution_policy_audit,
    source_structure_audit,
    strict_fix_mathematical_audit,
)
from verify_normative_closure_reassessment import verify


def test_source_order_supports_FIX_only_as_conservative_reading() -> None:
    audit = source_structure_audit()
    assert audit["canonical_setting_precedes_protocol_admission"]
    assert audit["freeze_instruction_precedes_game_membership_and_conjecture"]
    assert audit["conservative_reading"] == "FIX"
    assert audit["formal_entailment_of_FIX_proved"] is False


def test_canonical_source_supplies_no_formal_FIX_or_ADM_scope_semantics() -> None:
    audit = source_structure_audit()
    assert audit["all_scope_definitions_missing"]
    assert all(audit["missing_scope_definitions"].values())


def test_ADM_adds_four_objects_not_declared_in_v0_1() -> None:
    audit = interface_delta_audit()
    assert audit["ADM_added_object_count"] == 4
    assert all(audit["ADM_added_objects"].values())
    assert audit["ADM_clause_preservation_status"] == "not_established"


def test_typed_successor_does_not_retroactively_amend_parent() -> None:
    audit = interface_delta_audit()
    assert audit["typed_successor_status_check"]
    assert audit["ADM_is_reasonable_successor_target"]
    assert audit["FIX_status"] == "conservative_natural_reading_not_formally_entailed"


def test_v2_18_survives_only_as_conditional_lemma() -> None:
    audit = prior_claim_audit()
    assert audit["conditional_lemma_survives"]
    assert audit["satisfaction_proof_field_count"] == 0
    assert audit["prior_goal_completion_withdrawn"]
    by_claim = {row["claim"]: row for row in audit["claim_rows"]}
    assert by_claim["conditional_no_singleton_selector_lemma"]["supported"]
    assert not by_claim["ADM_is_clause_preserving"]["supported"]


def test_strict_FIX_sufficiency_is_exactly_refuted() -> None:
    audit = strict_fix_mathematical_audit()
    assert audit["v0_7_exact_gap"] == "(3/5)^d -> 0"
    assert audit["displayed_sufficiency_direction"] == "exactly_refuted"


def test_literal_necessity_is_exactly_refuted() -> None:
    audit = strict_fix_mathematical_audit()
    assert audit["v2_5_nonbinding_rows"] == 6
    assert audit["displayed_necessity_direction"] == "exactly_refuted"
    assert audit["displayed_iff_status"] == "internally_refuted_in_both_directions"


def test_two_sided_iff_refutation_is_not_full_classification() -> None:
    audit = resolution_policy_audit()
    assert audit["complete_resolution_items_present"] == 5
    assert all(audit["canonical_policy_markers"].values())
    assert audit["literal_iff_refutation_is_full_resolution"] is False


def test_no_full_resolution_or_mathematical_impossibility_is_claimed() -> None:
    audit = build_artifact()
    assert audit["disposition"]["full_ASMP_3_classification"] == "not_established"
    assert audit["disposition"]["ASMP_3_mathematical_impossibility"] == "not_proved"
    assert audit["disposition"]["prize_grade_resolution"] == "not_established"


def test_stop_decision_is_lane_specific_not_global() -> None:
    stop = build_artifact()["stop_resume"]
    assert stop["current_source_only_impossibility_lane_should_stop"]
    assert not stop["all_internal_search_should_stop"]
    assert len(stop["continue_or_resume"]) == 5


def test_normative_and_external_gates_remain_open() -> None:
    audit = authority_and_progress_audit()
    assert audit["prior_normative_definition"] == "unclosed"
    assert audit["external_qualifying_teams"] == 0
    assert audit["external_required_teams"] == 2
    assert audit["external_completion_gate"] is False


def test_written_artifact_and_clean_room_verifier_match() -> None:
    assert json.loads(ARTIFACT_PATH.read_text(encoding="utf-8")) == build_artifact()
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 10
