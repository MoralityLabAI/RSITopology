from __future__ import annotations

import causal_branch_fiber as central
import verify_causal_branch_fiber as independent


def test_three_resource_seals_and_frozen_payloads_match() -> None:
    assert central.resource_integrity_report()["pass"]
    assert central._load(central.CONTRACT) == central.expected_contract_payload()
    assert central._load(central.CLAIM) == central.expected_claim_payload()


def test_terminal_injective_disclosure_bound_is_tight() -> None:
    report = central.disclosure_report()
    assert report["pass"]
    assert report["terminal_fiber"] == 1
    assert report["branch_gap"] == report["fiber_bits"] == 1


def test_repeated_disclosure_has_one_third_bit_branch_gap() -> None:
    report = central.repeated_disclosure_report()
    assert report["pass"]
    assert report["rows"][-1]["leaves"] == 16_384


def test_all_binary_causal_morphisms_obey_local_fiber_bound() -> None:
    report = central.exhaustive_binary_morphism_report()
    assert report["pass"]
    assert report["checked"] == 332_928
    assert not report["failures"]


def test_full_local_clone_family_attains_bound() -> None:
    report = central.clone_sharpness_report()
    assert report["pass"]
    assert len(report["rows"]) == 256


def test_sparse_local_fibers_are_unbounded_with_zero_rate() -> None:
    report = central.sparse_local_fiber_report()
    assert report["pass"]
    assert len(report["rows"]) == 8192


def test_maximum_and_limsup_are_load_bearing() -> None:
    assert central.concentrated_local_fiber_report()["pass"]
    assert central.burst_limsup_report()["pass"]
    assert central.mutation_report()["pass"]


def test_independent_ternary_output_morphisms_obey_bound() -> None:
    report = independent.independent_ternary_morphism_census()
    assert report["pass"]
    assert report["checked"] == 2115


def test_independent_boundaries_documents_and_inventory_pass() -> None:
    assert independent.independent_disclosure_report()["pass"]
    assert independent.independent_sparse_boundary()["pass"]
    assert independent.independent_max_limsup_boundaries()["pass"]
    assert independent.independent_mutations()["pass"]
    assert independent.document_sentinels()["pass"]
    assert independent.independent_inventory()["pass"]


def test_complete_v029_report_passes_all_ten_gates() -> None:
    report = central.causal_branch_report()
    gates = central.verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
