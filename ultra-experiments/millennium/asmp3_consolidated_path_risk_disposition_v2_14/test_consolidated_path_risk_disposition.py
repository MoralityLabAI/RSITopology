from __future__ import annotations

import json

from consolidated_path_risk_disposition import ARTIFACT_PATH, build_artifact, package_rows
from verify_consolidated_path_risk_disposition import verify


def test_all_thirteen_decisive_packages_are_sealed() -> None:
    rows = package_rows()
    assert len(rows) == 13
    assert all(row["manifest_valid"] for row in rows)
    assert all(row["producer_certified"] for row in rows)
    assert all(row["independent_verifier_passed"] for row in rows)
    assert all(row["certified"] for row in rows)


def test_literal_conjecture_remains_separate_from_full_classification() -> None:
    disposition = build_artifact()["disposition"]
    assert disposition["literal_v0_1_named_conjecture"].startswith("refuted")
    assert disposition["unrestricted_asmp3_classification"] == "not_established"


def test_online_subclass_preserves_characterization_and_minimality() -> None:
    status = build_artifact()["disposition"]["repaired_online_contract_subclass"]
    assert "characterized" in status
    assert "black_box_minimal" in status


def test_correlated_noise_block_is_cleared_only_for_online_subclass() -> None:
    artifact = build_artifact()
    assert artifact["resolved_resume_triggers"] == [
        {
            "id": "T3_correlated_noise_path_theorem",
            "former_blocker": "v2.12 B3_noise_scope",
            "clearing_event": "broader correlated-noise hypothesis with a path theorem or sharp impossibility",
            "evidence": "v2.13 dependence-agnostic selected-path law plus fixed-marginal selection counterexample",
            "scope": "declared six-clause online subclass",
            "cleared": True,
        }
    ]
    assert "six-clause online subclass" in artifact["claim_boundary"]


def test_r3_records_exact_selected_path_law_and_unrestricted_boundary() -> None:
    by_id = {row["id"]: row for row in build_artifact()["requirement_rows"]}
    assert by_id["R3"]["status"] == (
        "exact_for_declared_online_subclass_via_selected_path_risk_unrestricted_open"
    )
    assert "marginal-only firewall" in by_id["R3"]["evidence"]


def test_all_requirement_rows_have_direct_evidence() -> None:
    rows = build_artifact()["requirement_rows"]
    assert len(rows) == 18
    assert len({row["id"] for row in rows}) == 18
    assert all(row["evidence_check"] for row in rows)


def test_noise_blocker_count_drops_from_five_to_four() -> None:
    artifact = build_artifact()
    blockers = artifact["remaining_blockers"]
    assert len(blockers) == 4
    assert not any("noise" in row["id"] for row in blockers)
    assert artifact["totals"]["remaining_blockers"] == 4


def test_remaining_blockers_require_non_grid_events() -> None:
    blockers = build_artifact()["remaining_blockers"]
    assert all(row["clearing_event"] for row in blockers)
    assert all(row["why_current_harness_cannot_clear_it"] for row in blockers)
    assert {row["category"] for row in blockers} == {
        "definition_authority",
        "new_mathematical_theory",
        "external_evidence",
    }


def test_external_gate_remains_zero_of_two() -> None:
    by_id = {row["id"]: row for row in build_artifact()["requirement_rows"]}
    assert by_id["A2"]["status"] == "missing_external_0_of_2"


def test_all_producer_gates_pass() -> None:
    artifact = build_artifact()
    assert artifact["certified"]
    assert len(artifact["gates"]) == 10
    assert all(artifact["gates"].values())


def test_written_artifact_and_clean_room_checker_match() -> None:
    assert json.loads(ARTIFACT_PATH.read_text(encoding="utf-8")) == build_artifact()
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 10
