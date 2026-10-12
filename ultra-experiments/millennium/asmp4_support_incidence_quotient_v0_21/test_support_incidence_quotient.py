"""Focused tests for ASMP-4 v0.21 support-incidence quotient."""

from __future__ import annotations

from support_incidence_quotient import (
    claim_exactness_report,
    contract_exactness_report,
    deterministic_embedding_report,
    finite_margin_report,
    memoryless_semantic_census_report,
    mutation_report,
    predecessor_inventory_report,
    quotient_report,
    quotient_theorem_report,
    resource_integrity_report,
    verification_gates,
)
from verify_support_incidence_quotient import (
    document_sentinels,
    independent_column_census,
    independent_contract_and_claim,
    independent_embedding_and_margin,
    independent_integrity,
    independent_inventory,
    independent_quotient_theorem,
    independent_report,
)


def test_two_resource_seals_and_contract_match() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert contract_exactness_report()["pass"]


def test_exact_support_quotient_theorem_holds_twice() -> None:
    assert quotient_theorem_report()["pass"]
    assert independent_quotient_theorem()["pass"]


def test_duplicate_fixture_reduces_four_raw_symbols_to_two() -> None:
    report = quotient_theorem_report()
    row = next(
        item for item in report["rows"] if item["name"] == "duplicate_memoryless"
    )
    assert row["raw_active"] == 4
    assert row["semantic_classes"] == 2
    assert row["raw_counts"][:4] == [4, 16, 64, 256]
    assert row["semantic_counts"][:4] == [2, 4, 8, 16]


def test_renaming_and_all_clone_factors_leave_semantic_observer_fixed() -> None:
    report = quotient_theorem_report()
    assert all(row["checks"]["renaming_adjacency"] for row in report["rows"])
    assert len(report["clone_rows"]) == 24
    assert all(all(row["checks"].values()) for row in report["clone_rows"])


def test_all_53108_relations_match_independent_column_census() -> None:
    central = memoryless_semantic_census_report()
    separate = independent_column_census()
    assert central["pass"]
    assert separate["pass"]
    assert central["combined"]["feasible"] == 724
    assert central["combined"]["duplicates_removed"] == 260
    assert central["combined"]["semantic_class_histogram"] == {2: 64, 3: 396, 4: 264}


def test_deterministic_embedding_and_finite_margin_hold_twice() -> None:
    assert deterministic_embedding_report()["pass"]
    margin = finite_margin_report()
    assert margin["pass"]
    assert margin["formula"]["semantic_reads"] == "k^T ceil(rho*2^T)"
    assert independent_embedding_and_margin()["pass"]


def test_five_quotient_mutations_are_rejected() -> None:
    report = mutation_report()
    assert report["pass"]
    assert report["cases"] == report["rejected"] == 5


def test_claim_inventory_and_documents_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    separate_inventory = independent_inventory()
    assert central_inventory["pass"]
    assert separate_inventory["pass"]
    assert central_inventory["tests"] == separate_inventory["tests"] == 244
    assert claim_exactness_report()["pass"]
    assert independent_contract_and_claim()["pass"]
    assert document_sentinels()["pass"]


def test_seven_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 7


def test_complete_v021_report_passes_all_ten_gates() -> None:
    report = quotient_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
