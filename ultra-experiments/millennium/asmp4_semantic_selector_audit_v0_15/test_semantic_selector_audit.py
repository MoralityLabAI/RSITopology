"""Focused tests for the ASMP-4 v0.15 semantic selector audit."""

from __future__ import annotations

from semantic_selector_audit import (
    adjudication_queue_report,
    claim_exactness_report,
    clause_census_report,
    metric_robustness_report,
    predecessor_inventory_report,
    preflight_reliability_report,
    resource_integrity_report,
    semantic_selector_audit_report,
    v014_disposition_report,
    verification_gates,
)
from verify_semantic_selector_audit import (
    document_sentinels,
    independent_artifact_integrity,
    independent_adjudication,
    independent_claim_audit,
    independent_clause_census,
    independent_integrity,
    independent_inventory,
    independent_preflight,
    independent_report,
    independent_robustness,
)


def test_three_resource_seals_match_independently() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert independent_artifact_integrity()["pass"]


def test_all_twenty_three_canonical_units_are_covered_exactly() -> None:
    central = clause_census_report()
    independent = independent_clause_census()
    assert central["pass"]
    assert independent["pass"]
    assert len(central["rows"]) == 23


def test_conservative_census_blocks_semantic_no_selector_claim() -> None:
    report = clause_census_report()
    assert report["counts"]["no_selector"] == 15
    assert report["counts"]["ambiguous"] == 7
    assert report["counts"]["selects_parameterized"] == 1
    assert report["blocking_items"] == [
        "C03",
        "C04",
        "C06",
        "C07",
        "C08",
        "C11",
        "C19",
        "C22",
    ]
    assert report["primary_claim_supported"] is False


def test_failed_pairwise_preflight_is_preserved() -> None:
    assert preflight_reliability_report()["pass"]
    assert independent_preflight()["pass"]


def test_five_family_metric_robustness_passes_twice() -> None:
    assert metric_robustness_report()["pass"]
    assert independent_robustness()["pass"]


def test_v014_semantic_claim_is_qualified_not_silently_preserved() -> None:
    report = v014_disposition_report()
    assert report["pass"]
    assert "requires qualification" in report["claim_support"]
    assert adjudication_queue_report()["pass"]
    assert independent_adjudication()["pass"]


def test_claim_and_predecessor_inventory_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    independent_inventory_report = independent_inventory()
    assert central_inventory["pass"]
    assert independent_inventory_report["pass"]
    assert central_inventory["tests"] == independent_inventory_report["tests"] == 184
    assert claim_exactness_report()["pass"]
    assert independent_claim_audit()["pass"]


def test_documents_preserve_all_evaluation_layers() -> None:
    assert document_sentinels()["pass"]


def test_nine_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 9


def test_complete_v015_report_passes_all_ten_gates() -> None:
    report = semantic_selector_audit_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
