from __future__ import annotations

import closure_stop_audit as central
import verify_closure_stop_audit as independent


def test_five_resource_seals_and_frozen_payloads_match() -> None:
    assert central.resource_integrity_report()["pass"]
    assert central._load(central.CONTRACT) == central.expected_contract_payload()
    assert central._load(central.CLAIM) == central.expected_claim_payload()


def test_both_parsers_recover_five_canonical_requirements() -> None:
    assert central.canonical_requirements_report()["pass"]
    assert independent.independent_requirement_parser()["pass"]


def test_claim_chain_supports_all_stop_premises() -> None:
    assert central.claim_semantics_report()["pass"]
    assert independent.independent_claim_chain()["pass"]


def test_requirement_ledger_keeps_full_scope_at_zero_of_five() -> None:
    report = central.requirement_coverage_report()
    assert report["pass"]
    assert sum(row["full_scope_proved"] for row in report["rows"]) == 0


def test_seven_conditional_layers_are_closed() -> None:
    report = central.finite_lane_closure_report()
    assert report["pass"]
    assert len(report["rows"]) == 7


def test_residual_dependency_root_and_stop_truth_table_pass() -> None:
    assert central.residual_dependency_report()["pass"]
    assert central.stop_logic_report()["pass"]
    assert independent.independent_dependency_audit()["pass"]
    assert independent.independent_stop_truth_table()["pass"]


def test_four_reopening_conditions_are_explicit() -> None:
    report = central.reopening_conditions_report()
    assert report["pass"]
    assert len(report["rows"]) == 4


def test_eight_overclaims_are_rejected_twice() -> None:
    assert central.mutation_report()["pass"]
    assert independent.independent_mutations()["pass"]


def test_independent_contract_documents_and_inventory_pass() -> None:
    assert independent.independent_contract_claim()["pass"]
    assert independent.document_sentinels()["pass"]
    assert central.predecessor_inventory_report()["pass"]
    assert independent.independent_inventory()["pass"]


def test_complete_v032_report_passes_all_ten_gates() -> None:
    report = central.closure_stop_report()
    gates = central.verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
