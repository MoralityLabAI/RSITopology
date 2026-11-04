from __future__ import annotations

import adversarial_mean_payoff as central
import verify_adversarial_mean_payoff as independent


def test_three_resource_seals_and_frozen_payloads_match() -> None:
    assert central.resource_integrity_report()["pass"]
    assert central._load(central.CONTRACT) == central.expected_contract_payload()
    assert central._load(central.CLAIM) == central.expected_claim_payload()


def test_adversarial_fork_requires_universal_policy_intersection() -> None:
    report = central.adversarial_fork_report()
    assert report["pass"]
    assert report["rows"]["corner"]["pass"]
    assert not report["rows"]["convex_midpoint"]["pass"]


def test_controller_fork_preserves_component_disjunction() -> None:
    report = central.controller_fork_report()
    assert report["pass"]
    assert not report["rows"]["midpoint"]["pass"]


def test_connector_mixture_attains_closed_boundary_with_multicycle() -> None:
    report = central.connector_mixture_report()
    assert report["pass"]
    assert report["budget"] == (central.q(1), central.q(1))


def test_finite_memory_approximates_but_does_not_attain_boundary() -> None:
    periodic = central.finite_memory_approximation_report()
    increasing = central.increasing_memory_report()
    assert periodic["pass"]
    assert periodic["rows"][-1]["slack"] == central.q("1/65")
    assert increasing["pass"]


def test_limsup_cost_polarity_and_eight_mutations_are_load_bearing() -> None:
    assert central.burst_polarity_report()["pass"]
    assert central.mutation_report()["pass"]


def test_central_exhaustive_two_state_census() -> None:
    report = central.exhaustive_two_state_report()
    assert report["pass"]
    assert report["decisions"] == 2304
    assert report["winning"] == 1202
    assert report["losing"] == 1102


def test_independent_two_state_census_and_boundaries() -> None:
    census = independent.independent_two_state_census()
    assert census["pass"]
    assert census["decisions"] == 1296
    assert census["winners"] == 776
    assert census["losers"] == 520
    assert independent.independent_boundaries()["pass"]


def test_independent_polarity_documents_contract_and_inventory() -> None:
    assert independent.independent_polarity_boundary()["pass"]
    assert independent.independent_mutations()["pass"]
    assert independent.independent_contract_claim()["pass"]
    assert independent.document_sentinels()["pass"]
    assert independent.independent_inventory()["pass"]


def test_complete_v031_report_passes_all_ten_gates() -> None:
    report = central.adversarial_mean_payoff_report()
    gates = central.verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
