"""Focused tests for the ASMP-4 v0.13 positive-volume collar."""

from __future__ import annotations

from positive_volume_collar import (
    adversarial_mutation_report,
    canonical_requirement_report,
    claim_exactness_report,
    converse_report,
    finite_margin_report,
    full_collar_construction_report,
    positive_volume_and_nhim_report,
    positive_volume_collar_report,
    predecessor_inventory_report,
    resource_integrity_report,
    verification_gates,
)
from verify_positive_volume_collar import (
    document_sentinels,
    independent_claim_audit,
    independent_converse,
    independent_finite_margin,
    independent_full_collar,
    independent_geometry,
    independent_integrity,
    independent_inventory,
    independent_mutations,
    independent_report,
    independent_source_requirements,
)


def test_two_resource_seals_match_independently() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]


def test_canonical_positive_volume_and_margin_requirements_are_present() -> None:
    assert canonical_requirement_report()["pass"]
    assert independent_source_requirements()["pass"]


def test_positive_volume_collar_contains_positive_dimensional_nhim() -> None:
    central = positive_volume_and_nhim_report()
    assert central["pass"]
    assert central["normalized_collar_volume"] == "2"
    assert independent_geometry()["pass"]


def test_full_collar_construction_has_exact_transcript_counts() -> None:
    central = full_collar_construction_report()
    independent = independent_full_collar()
    assert central["pass"]
    assert independent["pass"]
    assert central["computed_region"] == "[2,infinity) x [2,infinity)"
    assert central["raw_region"] == "[3,infinity) x [2,infinity)"


def test_matching_interval_and_mode_separation_converses_hold() -> None:
    assert converse_report()["pass"]
    assert independent_converse()["pass"]


def test_exact_finite_margin_formula_includes_nondyadic_radii() -> None:
    central = finite_margin_report()
    independent = independent_finite_margin()
    assert central["pass"]
    assert central["formula"] == "N_T(rho)=ceil(rho*2^T)"
    assert independent["pass"]
    assert independent["checks"]["nondyadic_radii_checked"]


def test_five_adversarial_mutations_are_rejected_twice() -> None:
    central = adversarial_mutation_report()
    independent = independent_mutations()
    assert central["pass"]
    assert independent["pass"]
    assert central["cases"] == independent["cases"] == 5


def test_claim_and_predecessor_inventory_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    independent_inventory_report = independent_inventory()
    assert central_inventory["pass"]
    assert independent_inventory_report["pass"]
    assert central_inventory["tests"] == independent_inventory_report["tests"] == 164
    assert claim_exactness_report()["pass"]
    assert independent_claim_audit()["pass"]


def test_documents_and_ten_independent_checks_pass() -> None:
    assert document_sentinels()["pass"]
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 10


def test_complete_v013_report_passes_all_ten_gates() -> None:
    report = positive_volume_collar_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
