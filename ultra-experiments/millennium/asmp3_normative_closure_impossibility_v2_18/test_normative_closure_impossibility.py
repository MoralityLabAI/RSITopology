from __future__ import annotations

import json

from normative_closure_impossibility import (
    ARTIFACT_PATH,
    authority_audit,
    authority_bit_audit,
    build_artifact,
    claim_boundary_audit,
    completion_models,
    material_fork_audit,
    mutation_audit,
    randomized_selector_audit,
    selector_audit,
    source_scope_audit,
)
from verify_normative_closure_impossibility import verify


def test_canonical_clause_inventory_is_complete() -> None:
    audit = source_scope_audit()
    assert audit["explicit_clause_count"] == 9
    assert audit["explicit_clause_checks_passed"] == 9
    assert all(audit["explicit_clause_checks"].values())


def test_canonical_source_has_no_unique_FIX_ADM_selector() -> None:
    audit = source_scope_audit()
    assert audit["selector_phrase_count"] == 0
    assert not any(audit["selector_phrase_presence"].values())
    assert audit["certified"]


def test_no_current_authoritative_channel_selects_a_mode() -> None:
    audit = authority_audit()
    assert audit["channel_count"] == 6
    assert audit["authoritative_channels"] == 1
    assert audit["authoritative_selecting_channels"] == 0
    assert audit["certified"]


def test_exactly_two_clause_preserving_completions_exist_in_the_audited_fork() -> None:
    models = completion_models()
    assert {row["mode"] for row in models} == {"FIX", "ADM"}
    assert all(row["clause_preserving_completion"] for row in models)
    assert all(row["all_explicit_obligations_satisfied"] for row in models)


def test_completion_models_share_substrate_but_change_material_outcome() -> None:
    audit = material_fork_audit(completion_models())
    assert audit["same_substrate"]
    assert audit["fixed_gap"] == "(3/5)^d -> 0"
    assert audit["admissible_gap"] == "3/5"
    assert audit["material_outcomes_differ"]
    assert audit["certified"]


def test_no_deterministic_source_only_action_is_sound_decisive_closure() -> None:
    audit = selector_audit(completion_models())
    rows = {row["selector_output"]: row for row in audit["rows"]}
    assert rows["ABSTAIN"]["action_kind"] == "no_claim"
    assert rows["ABSTAIN"]["excluded_clause_preserving_models"] == []
    assert rows["ABSTAIN"]["entailment_sound"] and not rows["ABSTAIN"]["decisive_singleton"]
    assert rows["BOTH"]["entailment_sound"] and not rows["BOTH"]["decisive_singleton"]
    assert not rows["FIX"]["entailment_sound"]
    assert not rows["ADM"]["entailment_sound"]
    assert audit["sound_decisive_selector_count"] == 0


def test_randomization_has_exact_one_half_minimax_error() -> None:
    audit = randomized_selector_audit()
    assert audit["denominators_audited"] == 64
    assert audit["global_minimum_worst_model_error"] == "1/2"
    assert audit["zero_error_randomized_selector_exists"] is False
    assert audit["denominators_attaining_global_minimum"] == list(range(2, 65, 2))


def test_one_external_normative_bit_is_necessary_and_sufficient() -> None:
    audit = authority_bit_audit(completion_models())
    assert audit["zero_external_bits_decisive"] is False
    assert audit["one_external_bit_decisive"] is True
    assert audit["minimum_external_normative_bits"] == 1


def test_scope_axiom_mutations_are_discriminating_and_dual_addition_is_inconsistent() -> None:
    rows = {row["mutation"]: row for row in mutation_audit()}
    assert rows["sealed_v0_1"]["surviving_completion_modes"] == ["ADM", "FIX"]
    assert rows["add_FIX_scope_axiom"]["surviving_completion_modes"] == ["FIX"]
    assert rows["add_ADM_scope_axiom"]["surviving_completion_modes"] == ["ADM"]
    assert rows["add_both_incompatible_scope_axioms"]["surviving_completion_modes"] == []
    assert all(row["matches"] for row in rows.values())


def test_claim_boundary_is_scoped_and_each_branch_is_repairable() -> None:
    audit = claim_boundary_audit(mutation_audit())
    assert audit["certified"]
    assert all(audit["checks"].values())
    assert "does not prove that normative choice is metaphysically impossible" in audit["statement"]


def test_all_ten_producer_gates_pass() -> None:
    artifact = build_artifact()
    assert artifact["certified"]
    assert len(artifact["gates"]) == 10
    assert all(artifact["gates"].values())


def test_written_artifact_and_clean_room_verifier_match() -> None:
    assert json.loads(ARTIFACT_PATH.read_text(encoding="utf-8")) == build_artifact()
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 10
