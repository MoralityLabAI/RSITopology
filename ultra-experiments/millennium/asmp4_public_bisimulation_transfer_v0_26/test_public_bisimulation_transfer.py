"""Focused tests for ASMP-4 v0.26 public bisimulation transfer."""

from __future__ import annotations

from public_bisimulation_transfer import (
    alternating_fixture_report,
    claim_exactness_report,
    contract_exactness_report,
    decorated_cover_transfer_report,
    finite_quotient_boundary_report,
    mutation_report,
    predecessor_inventory_report,
    public_bisimulation_report,
    resource_integrity_report,
    thue_morse_report,
    verification_gates,
)
from verify_public_bisimulation_transfer import (
    document_sentinels,
    independent_alternating_boundary,
    independent_contract_and_claim,
    independent_decorated_transfer,
    independent_integrity,
    independent_inventory,
    independent_mutations,
    independent_report,
    independent_thue_morse_boundary,
)


def test_three_resource_seals_and_public_contract_match() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert contract_exactness_report()["pass"]
    assert independent_contract_and_claim()["pass"]


def test_decorated_covers_transfer_vector_frontiers() -> None:
    report = decorated_cover_transfer_report()
    assert report["pass"]
    assert report["failures"] == 0
    assert len(report["rows"]) == 256


def test_independent_weighted_transfer_scales_to_ninety_six_states() -> None:
    report = independent_decorated_transfer()
    assert report["pass"]
    assert report["rows"] == 2400


def test_alternating_back_and_forth_rejects_three_breaks() -> None:
    assert alternating_fixture_report()["pass"]
    assert independent_alternating_boundary()["pass"]


def test_thue_morse_has_half_rate_and_no_finite_exact_quotient() -> None:
    central = thue_morse_report()
    separate = independent_thue_morse_boundary()
    assert central["pass"]
    assert separate["pass"]
    assert central["ones"] == 2048


def test_finite_quotient_is_sufficient_but_not_necessary() -> None:
    report = finite_quotient_boundary_report()
    assert report["pass"]
    assert report["checks"]["finite_quotient_sufficient_not_necessary"]


def test_five_transfer_mutations_are_rejected_twice() -> None:
    central = mutation_report()
    assert central["pass"]
    assert central["cases"] == central["rejected"] == 5
    assert independent_mutations()["pass"]


def test_claim_inventory_and_documents_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    separate_inventory = independent_inventory()
    assert central_inventory["pass"]
    assert separate_inventory["pass"]
    assert central_inventory["tests"] == separate_inventory["tests"] == 294
    assert claim_exactness_report()["pass"]
    assert document_sentinels()["pass"]


def test_seven_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 7


def test_complete_v026_report_passes_all_ten_gates() -> None:
    report = public_bisimulation_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
