"""Focused tests for the consolidated ASMP-4 v0.9 atlas."""

from __future__ import annotations

import json
from pathlib import Path

from completion_atlas import (
    canonical_requirements_report,
    claim_chain_report,
    completion_atlas_report,
    model_completion_atlas,
    mutation_selector_audit,
    requirement_evidence_atlas,
    resource_integrity_report,
    source_gap_report,
    stopping_certificate,
    test_inventory_report as predecessor_test_inventory_report,
    underdetermination_certificate,
    verification_gates,
)
from verify_completion_atlas import (
    claim_exactness,
    document_sentinels,
    independent_integrity,
    independent_model_atlas,
    independent_report,
    independent_requirements,
    independent_source_gaps,
    independent_test_inventory,
)

HERE = Path(__file__).resolve().parent


def test_eight_source_and_claim_resources_match_seals() -> None:
    central = resource_integrity_report()
    independent = independent_integrity()
    assert central["pass"]
    assert independent["pass"]
    assert central["resources"] == 8
    assert len(independent["rows"]) == 8


def test_two_parsers_extract_five_canonical_requirements() -> None:
    central = canonical_requirements_report()
    independent = independent_requirements()
    assert central["pass"]
    assert independent["pass"]
    assert central["count"] == independent["count"] == 5
    assert [row["text"] for row in central["requirements"]] == independent[
        "requirements"
    ]


def test_seven_predecessor_claim_schemas_and_discriminators_are_exact() -> None:
    report = claim_chain_report()
    assert report["pass"]
    assert report["claim_count"] == 7
    assert all(report["exact_checks"].values())


def test_normative_source_has_two_independent_gaps() -> None:
    central = source_gap_report()
    independent = independent_source_gaps()
    assert central["pass"]
    assert independent["pass"]
    assert central["missing_dimensions"] == [
        "registered sensor/computation domain",
        "randomness/disturbance quantifier order",
    ]


def test_machine_index_cannot_normatively_repair_source() -> None:
    report = source_gap_report()
    assert report["checks"]["index_is_non_normative"]
    assert report["checks"]["graduation_unsatisfied"]
    assert report["checks"]["index_has_no_sensor_grammar"]
    assert report["machine_index_status"] == "proposed_candidate_definition_draft"


def test_all_five_requirements_have_only_conditional_coverage() -> None:
    report = requirement_evidence_atlas()
    assert report["pass"]
    assert report["conditional_coverage_count"] == 5
    assert report["canonical_completion_count"] == 0
    assert all(row["evidence_packages"] for row in report["rows"])


def test_sensor_completions_have_three_distinct_targets() -> None:
    central = model_completion_atlas()
    independent = independent_model_atlas()
    assert central["pass"]
    assert independent["pass"]
    assert central["sensor_model_count"] == 3
    assert central["sensor_distinct_targets"] == 3
    assert independent["sensor_distinct"] == 3


def test_stochastic_completions_have_two_distinct_outcomes() -> None:
    central = model_completion_atlas()
    independent = independent_model_atlas()
    assert central["stochastic_model_count"] == 3
    assert central["stochastic_distinct_targets"] == 2
    assert independent["stochastic_distinct"] == 2


def test_semantic_underdetermination_theorem_obligations_hold() -> None:
    report = underdetermination_certificate()
    assert report["pass"]
    assert all(report["obligations"].values())
    assert report["decision"] == "canonical_asmp4_target_not_semantically_determinate"


def test_selector_mutations_resolve_corresponding_gap() -> None:
    report = mutation_selector_audit()
    assert report["pass"]
    assert report["classifications"]["base"] == {
        "sensor_selected": False,
        "randomness_selected": False,
    }
    assert report["classifications"]["computed"]["sensor_selected"]
    assert report["classifications"]["support"]["randomness_selected"]


def test_predecessor_test_inventory_is_exact() -> None:
    central = predecessor_test_inventory_report()
    independent = independent_test_inventory()
    assert central["pass"]
    assert independent["pass"]
    assert central["packages"] == independent["packages"] == 9
    assert central["predecessor_tests"] == independent["tests"] == 112


def test_stopping_certificate_has_four_reopening_conditions() -> None:
    report = stopping_certificate()
    assert report["pass"]
    assert report["conditional_requirement_coverage"] == 5
    assert report["canonical_requirement_completion"] == 0
    assert len(report["reopening_conditions"]) == 4
    assert (
        report["decision"]
        == "stop_local_enumeration_and_request_normative_registration"
    )


def test_frozen_v09_claim_matches_atlas() -> None:
    claim = json.loads(
        (HERE / "completion_atlas_claim_v0_9.json").read_text(encoding="utf-8")
    )
    assert claim["sealed_resources"]["count"] == 8
    assert claim["canonical_requirements"] == {
        "count": 5,
        "conditional_evidence_coverage": 5,
        "canonical_completion_proven": 0,
    }
    assert claim_exactness()["pass"]


def test_document_sentinels_and_independent_atlas_pass() -> None:
    assert document_sentinels()["pass"]
    independent = independent_report()
    assert independent["pass"]
    assert len(independent["checks"]) == 8


def test_complete_atlas_passes_all_eleven_gates() -> None:
    report = completion_atlas_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 11
    assert all(gates.values())
