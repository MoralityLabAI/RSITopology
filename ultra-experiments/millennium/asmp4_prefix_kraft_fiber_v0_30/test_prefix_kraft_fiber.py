from __future__ import annotations

import prefix_kraft_fiber as central
import verify_prefix_kraft_fiber as independent


def test_three_resource_seals_and_frozen_payloads_match() -> None:
    assert central.resource_integrity_report()["pass"]
    assert central._load(central.CONTRACT) == central.expected_contract_payload()
    assert central._load(central.CLAIM) == central.expected_claim_payload()


def test_terminal_bijective_disclosure_bound_is_tight() -> None:
    report = central.disclosure_report()
    assert report["pass"]
    assert report["terminal_fiber"] == 1
    assert report["gap"] == report["rounded_local_cost"] == 1


def test_repeated_disclosure_has_one_third_bit_prefix_gap() -> None:
    report = central.repeated_disclosure_report()
    assert report["pass"]
    assert report["rows"][-1]["leaves"] == 16_384


def test_all_binary_causal_morphisms_obey_rounded_kraft_bound() -> None:
    report = central.exhaustive_binary_morphism_report()
    assert report["pass"]
    assert report["checked"] == 332_928
    assert not report["failures"]


def test_regular_clones_and_mixed_schedules_need_sequential_rounding() -> None:
    assert central.regular_clone_report()["pass"]
    assert central.mixed_schedule_report()["pass"]


def test_sublinear_maximum_limsup_and_mutations_are_load_bearing() -> None:
    assert central.sparse_rounding_report()["pass"]
    assert central.concentrated_and_burst_report()["pass"]
    assert central.mutation_report()["pass"]


def test_independent_full_ternary_binary_output_census() -> None:
    report = independent.independent_ternary_binary_map_census()
    assert report["pass"]
    assert report["checked"] == 4096


def test_independent_explicit_trees_and_mixed_recurrences() -> None:
    explicit = independent.independent_explicit_regular_trees()
    mixed = independent.independent_mixed_schedules()
    assert explicit["pass"]
    assert len(explicit["rows"]) == 30
    assert mixed["pass"]
    assert len(mixed["rows"]) == 15_625


def test_independent_boundaries_documents_and_inventory_pass() -> None:
    assert independent.independent_disclosure_report()["pass"]
    assert independent.independent_sparse_boundary()["pass"]
    assert independent.independent_max_limsup_boundaries()["pass"]
    assert independent.independent_mutations()["pass"]
    assert independent.independent_contract_claim()["pass"]
    assert independent.document_sentinels()["pass"]
    assert independent.independent_inventory()["pass"]


def test_complete_v030_report_passes_all_ten_gates() -> None:
    report = central.prefix_kraft_report()
    gates = central.verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
