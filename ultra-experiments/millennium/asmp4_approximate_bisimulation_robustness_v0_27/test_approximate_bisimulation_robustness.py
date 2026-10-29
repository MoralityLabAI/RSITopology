from __future__ import annotations

import approximate_bisimulation_robustness as central
import verify_approximate_bisimulation_robustness as independent


def test_three_resource_seals_and_frozen_payloads_match() -> None:
    assert central.resource_integrity_report()["pass"]
    assert central._load(central.CONTRACT) == central.expected_contract_payload()
    assert central._load(central.CLAIM) == central.expected_claim_payload()


def test_decorated_vector_frontiers_transfer_with_T_epsilon_slack() -> None:
    report = central.decorated_transfer_report()
    assert report["pass"]
    assert len(report["rows"]) == 256
    assert not report["failures"]


def test_adversarial_successor_frontiers_transfer_in_both_directions() -> None:
    report = central.adversarial_transfer_report()
    assert report["pass"]
    assert len(report["rows"]) == 8


def test_cost_error_constant_is_attained_at_every_registered_horizon() -> None:
    report = central.cost_sharpness_report()
    assert report["pass"]
    assert all(row["exact"] for row in report["rows"])


def test_strict_safety_margin_is_sufficient_and_sharp() -> None:
    report = central.safety_margin_boundary_report()
    assert report["pass"]
    assert len(report["rows"]) == 128


def test_seven_definition_mutations_are_rejected_centrally() -> None:
    report = central.mutation_report()
    assert report["pass"]
    assert report["rejected"] == 7


def test_independent_weighted_minimax_transfer_scales_to_ninety_six_states() -> None:
    report = independent.independent_weighted_transfer()
    assert report["pass"]
    assert report["comparisons"] == 2400


def test_independent_alternating_and_sharp_boundaries_pass() -> None:
    assert independent.independent_alternating_boundary()["pass"]
    assert independent.independent_sharp_boundaries()["pass"]
    assert independent.independent_mutations()["pass"]


def test_inventory_documents_and_complete_payload_are_exact() -> None:
    assert central.predecessor_inventory_report()["pass"]
    assert independent.independent_inventory()["pass"]
    assert independent.document_sentinels()["pass"]
    assert central.payload_report()["pass"]


def test_complete_v027_report_passes_all_ten_gates() -> None:
    report = central.robustness_report()
    gates = central.verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
