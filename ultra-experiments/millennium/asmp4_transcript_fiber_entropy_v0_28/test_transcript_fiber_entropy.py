from __future__ import annotations

import transcript_fiber_entropy as central
import verify_transcript_fiber_entropy as independent


def test_three_resource_seals_and_frozen_payloads_match() -> None:
    assert central.resource_integrity_report()["pass"]
    assert central._load(central.CONTRACT) == central.expected_contract_payload()
    assert central._load(central.CLAIM) == central.expected_claim_payload()


def test_exponential_clone_family_attains_port_specific_fiber_bounds() -> None:
    report = central.clone_family_report()
    assert report["pass"]
    assert len(report["rows"]) == 2048


def test_explicit_languages_have_exact_maximum_fibers() -> None:
    report = central.explicit_language_report()
    assert report["pass"]
    assert max(row["enumerated"] for row in report["rows"]) == 15_625


def test_unbounded_sparse_fibers_have_zero_entropy_rate() -> None:
    report = central.sparse_subexponential_report()
    assert report["pass"]
    assert len(report["rows"]) == 4096


def test_limsup_and_maximum_fiber_are_load_bearing() -> None:
    assert central.burst_limsup_report()["pass"]
    assert central.concentrated_fiber_report()["pass"]


def test_finite_state_class_and_one_way_factor_do_not_bound_history_entropy() -> None:
    report = central.directional_and_class_boundary_report()
    assert report["pass"]
    assert report["checks"]["positive_relative_entropy"]


def test_eight_definition_mutations_are_rejected_centrally() -> None:
    report = central.mutation_report()
    assert report["pass"]
    assert report["rejected"] == 8


def test_independent_tries_and_schedule_census_match_exact_counts() -> None:
    trie = independent.independent_trie_census()
    schedules = independent.independent_schedule_census()
    assert trie["pass"] and schedules["pass"]
    assert len(trie["rows"]) == 35
    assert len(schedules["rows"]) == 6561


def test_independent_boundaries_documents_and_inventory_pass() -> None:
    assert independent.independent_sparse_boundary()["pass"]
    assert independent.independent_burst_boundary()["pass"]
    assert independent.independent_directional_max_boundary()["pass"]
    assert independent.independent_mutations()["pass"]
    assert independent.document_sentinels()["pass"]
    assert independent.independent_inventory()["pass"]


def test_complete_v028_report_passes_all_ten_gates() -> None:
    report = central.transcript_fiber_report()
    gates = central.verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
