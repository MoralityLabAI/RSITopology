from __future__ import annotations

import json
from pathlib import Path

from build_release_manifest import verify_manifest
from resolution_disposition import (
    CANONICAL_PATH,
    EVIDENCE_PACKAGES,
    REGISTRY_PATH,
    TYPED_PATH,
    build_result,
    evidence_package_rows,
    verify_manifest as verify_parent_manifest,
)
from verify_resolution_disposition import verify


HERE = Path(__file__).resolve().parent


def test_all_parent_manifests_are_current() -> None:
    for spec in EVIDENCE_PACKAGES:
        valid, count, size = verify_parent_manifest(
            CANONICAL_PATH.parent / spec["directory"] / spec["manifest"]
        )
        assert valid
        assert count > 0
        assert size > 0


def test_all_evidence_packages_have_independent_green_verifiers() -> None:
    rows = evidence_package_rows()
    assert len(rows) == 8
    assert all(row["producer_certified"] for row in rows)
    assert all(row["independent_verifier_passed"] for row in rows)
    assert all(row["certified"] for row in rows)


def test_authoritative_status_is_definition_draft_not_prize() -> None:
    canonical = CANONICAL_PATH.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    assert "research-agenda artifact" in canonical
    assert "ready for external definition review" in canonical
    assert registry["status"] == "proposed_candidate_definition_draft"
    assert registry["graduation_standard_satisfied"] is False
    assert registry["actual_prize_announced"] is False


def test_typed_successor_does_not_change_parent_or_adjudicate_intent() -> None:
    typed = TYPED_PATH.read_text(encoding="utf-8")
    assert "document_status = nonnormative_successor_draft" in typed
    assert "changes_parent_problem = false" in typed
    assert "does not decide v0.1 authorial intent" in typed


def test_named_conjecture_is_refuted_but_full_program_is_not_marked_complete() -> None:
    result = build_result()
    disposition = result["disposition"]
    assert disposition["named_weak_verifier_characterization_conjecture"].startswith(
        "refuted"
    )
    assert disposition["full_asmp3_v0_1_classification_program"].startswith(
        "not_resolved"
    )
    assert disposition["community_or_prize_style_acceptance"].startswith(
        "not_established"
    )


def test_registry_negative_route_math_is_satisfied_but_nonnormative() -> None:
    result = build_result()
    rows = {row["id"]: row for row in result["requirement_rows"]}
    assert rows["G0"]["status"] == "satisfied_internal"
    assert rows["G1"]["status"] == "satisfied_internal"
    assert rows["D2"]["status"] == "registry_is_nonnormative"


def test_complete_resolution_items_are_adjudicated_without_overclaim() -> None:
    rows = {row["id"]: row for row in build_result()["requirement_rows"]}
    assert rows["R0"]["status"] == "partial_subclass_only"
    assert rows["R1"]["status"] == "partial_subclass_only"
    assert rows["R2"]["status"] == "partial_family_only"
    assert rows["R3"]["status"] == "partial_noise_class_only"
    assert rows["R4"]["status"] == "satisfied_component"


def test_external_acceptance_gate_is_exactly_zero_of_two() -> None:
    status = build_result()["expert_review_status"]
    assert status["qualifying_teams"] == 0
    assert status["required_teams"] == 2
    assert status["qualifying_independent_team_checkers"] == 0
    assert status["required_independent_team_checkers"] == 1
    assert status["completion_gate_satisfied"] is False


def test_stopping_boundary_cannot_be_cleared_by_more_grid_rows() -> None:
    result = build_result()
    blockers = result["remaining_blockers"]
    assert len(blockers) == 4
    assert result["disposition"]["current_harness_architecture"] == "stop_further_grid_extension"
    assert all("cannot" in row["why_more_current_harness_rows_cannot_clear_it"] for row in blockers)
    assert {row["category"] for row in blockers} == {
        "normative_definition",
        "new_mathematical_theory",
        "external_review",
    }


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["requirement_rows"]) == 19
    assert len(result["gates"]) == 10
    assert result["certified"]
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 10
    assert all(result["checks"].values())


def test_written_disposition_matches_machine_boundary() -> None:
    disposition = (HERE / "RESOLUTION_DISPOSITION_v2_6.md").read_text(encoding="utf-8")
    matrix = (HERE / "REQUIREMENT_EVIDENCE_MATRIX_v2_6.md").read_text(encoding="utf-8")
    stopping = (HERE / "STOPPING_BOUNDARY_v2_6.md").read_text(encoding="utf-8")
    assert "Named conjecture" in disposition
    assert "not a full ASMP-3 resolution" in disposition
    assert "0/2" in matrix
    assert "Stop extending" in stopping


def test_release_manifest_matches() -> None:
    assert verify_manifest()
