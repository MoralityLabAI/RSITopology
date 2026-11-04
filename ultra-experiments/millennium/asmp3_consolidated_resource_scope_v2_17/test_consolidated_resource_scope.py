from __future__ import annotations

import json

from consolidated_resource_scope import ARTIFACT_PATH, build_artifact, package_rows
from verify_consolidated_resource_scope import verify


def test_all_fifteen_decisive_packages_are_sealed() -> None:
    rows = package_rows()
    assert len(rows) == 15
    assert all(row["manifest_valid"] for row in rows)
    assert all(row["producer_certified"] for row in rows)
    assert all(row["independent_verifier_passed"] for row in rows)
    assert all(row["certified"] for row in rows)


def test_literal_and_online_dispositions_are_preserved() -> None:
    artifact = build_artifact()
    by_id = {row["id"]: row for row in artifact["requirement_rows"]}
    assert by_id["N2"]["status"] == "refuted_exact_both_readings"
    assert by_id["R0"]["status"].endswith("unrestricted_open")
    assert by_id["R3"]["status"].startswith("exact_for_declared_online_subclass")


def test_R2_is_strengthened_by_v2_15_and_v2_16() -> None:
    by_id = {row["id"]: row for row in build_artifact()["requirement_rows"]}
    assert by_id["R2"]["status"] == "exact_arbitrary_round_public_coin_bounded_soundness_marker_family_cross_task_open"
    assert "v2.15" in by_id["R2"]["evidence"]
    assert "v2.16" in by_id["R2"]["evidence"]


def test_five_old_marker_interface_firewalls_are_cleared() -> None:
    progress = build_artifact()["resource_progress"]
    assert len(progress["cleared_firewalls"]) == 5
    assert progress["exact_marker_frontier"] == "min(1,K*q/N)"
    assert progress["exact_bounded_soundness_frontier"] == "C*=s+(1-s)*min(1,K*q/N)"
    assert progress["certified"]


def test_cross_task_resource_requirement_is_not_falsely_cleared() -> None:
    artifact = build_artifact()
    assert artifact["resource_progress"]["fully_cleared"] is False
    assert artifact["disposition"]["cross_task_resource_classification"] == "not_well_posed_until_formal_class_is_frozen"


def test_all_requirement_rows_have_direct_evidence() -> None:
    rows = build_artifact()["requirement_rows"]
    assert len(rows) == 18
    assert len({row["id"] for row in rows}) == 18
    assert all(row["evidence_check"] for row in rows)


def test_remaining_resource_blocker_is_definition_dependent() -> None:
    blocker = build_artifact()["remaining_blockers"][2]
    assert blocker["id"] == "B2_cross_task_resources"
    assert blocker["category"] == "definition_dependent_theorem"
    assert "unspecified task/protocol class" in blocker["why_current_harness_cannot_clear_it"]


def test_exactly_four_non_grid_blockers_remain() -> None:
    artifact = build_artifact()
    assert len(artifact["remaining_blockers"]) == 4
    assert artifact["totals"]["remaining_blockers"] == 4


def test_external_gate_remains_zero_of_two() -> None:
    by_id = {row["id"]: row for row in build_artifact()["requirement_rows"]}
    assert by_id["A2"]["status"] == "missing_external_0_of_2"


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
