from __future__ import annotations

import json

from consolidated_resolution_disposition import (
    ARTIFACT_PATH,
    build_artifact,
    package_rows,
)
from verify_consolidated_resolution_disposition import verify


def test_all_twelve_decisive_packages_are_sealed() -> None:
    rows = package_rows()
    assert len(rows) == 12
    assert all(row["manifest_valid"] for row in rows)
    assert all(row["producer_certified"] for row in rows)
    assert all(row["independent_verifier_passed"] for row in rows)
    assert all(row["certified"] for row in rows)


def test_literal_conjecture_is_kept_separate_from_full_classification() -> None:
    disposition = build_artifact()["disposition"]
    assert disposition["literal_v0_1_named_conjecture"].startswith("refuted")
    assert disposition["unrestricted_asmp3_classification"] == "not_established"


def test_repaired_subclass_records_v2_10_and_v2_11_progress() -> None:
    disposition = build_artifact()["disposition"]
    assert disposition["repaired_online_contract_subclass"] == (
        "constructively_characterized_and_black_box_minimal"
    )


def test_all_requirement_rows_have_direct_evidence() -> None:
    rows = build_artifact()["requirement_rows"]
    assert len(rows) == 18
    assert len({row["id"] for row in rows}) == 18
    assert all(row["evidence_check"] for row in rows)


def test_complete_items_are_not_overclaimed() -> None:
    by_id = {row["id"]: row for row in build_artifact()["requirement_rows"]}
    assert by_id["R0"]["status"].endswith("unrestricted_open")
    assert by_id["R2"]["status"].startswith("partial_")
    assert by_id["R3"]["status"].startswith("partial_")


def test_external_gate_remains_zero_of_two() -> None:
    by_id = {row["id"]: row for row in build_artifact()["requirement_rows"]}
    assert by_id["A2"]["status"] == "missing_external_0_of_2"


def test_remaining_blockers_require_new_inputs_not_more_rows() -> None:
    blockers = build_artifact()["remaining_blockers"]
    assert len(blockers) == 5
    assert all(row["clearing_event"] for row in blockers)
    assert all(row["why_current_harness_cannot_clear_it"] for row in blockers)


def test_safe_public_label_has_all_three_layers() -> None:
    label = build_artifact()["disposition"]["safe_public_label"]
    assert "named iff refuted internally" in label
    assert "online subclass characterized" in label
    assert "unrestricted classification" in label


def test_all_producer_gates_pass() -> None:
    artifact = build_artifact()
    assert artifact["certified"]
    assert len(artifact["gates"]) == 10
    assert all(artifact["gates"].values())


def test_written_artifact_and_clean_room_verifier_match() -> None:
    assert json.loads(ARTIFACT_PATH.read_text(encoding="utf-8")) == build_artifact()
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 10
