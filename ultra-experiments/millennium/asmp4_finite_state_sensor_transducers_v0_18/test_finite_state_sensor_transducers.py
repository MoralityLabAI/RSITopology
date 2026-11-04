"""Focused tests for ASMP-4 v0.18 finite-state sensor transducers."""

from __future__ import annotations

import math

from finite_state_sensor_transducers import (
    claim_exactness_report,
    contract_exactness_report,
    finite_margin_report,
    finite_state_sensor_report,
    fixture_theorem_report,
    mutation_report,
    predecessor_inventory_report,
    resource_integrity_report,
    two_state_binary_census_report,
    verification_gates,
)
from verify_finite_state_sensor_transducers import (
    document_sentinels,
    independent_contract_and_claim,
    independent_fixture_theorem,
    independent_integrity,
    independent_inventory,
    independent_rate_and_margin,
    independent_report,
    independent_small_census,
)


def test_two_resource_seals_and_contract_match() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert contract_exactness_report()["pass"]


def test_reachable_subset_observer_criterion_holds_twice() -> None:
    central = fixture_theorem_report()
    independent = independent_fixture_theorem()
    assert central["pass"]
    assert independent["pass"]
    assert sum(row["feasible"] for row in central["rows"]) == 4


def test_golden_language_and_spectral_threshold_are_exact() -> None:
    report = fixture_theorem_report()
    golden = next(row for row in report["rows"] if row["name"] == "golden_refinement")
    phi = (1 + math.sqrt(5)) / 2
    assert golden["word_counts"][:5] == [4, 12, 40, 128, 416]
    assert math.isclose(golden["spectral_radius"], 2 * phi)
    assert math.isclose(golden["read_threshold"], 2 + math.log2(phi))


def test_history_overlap_is_feasible_but_one_symbol_overlap_is_not() -> None:
    checks = fixture_theorem_report()["checks"]
    assert checks["toggle_global_overlap_but_history_decodable"]
    assert checks["bad_fixture_has_mixed_q_violation"]


def test_all_256_small_transducers_match_independent_census() -> None:
    central = two_state_binary_census_report()
    independent = independent_small_census()
    assert central["pass"]
    assert independent["pass"]
    assert central["census"]["feasible"] == 80
    assert central["census"]["history_essential"] == 48


def test_exact_finite_margin_products_hold_twice() -> None:
    central = finite_margin_report()
    assert central["pass"]
    assert central["formula"]["read"] == "L_T ceil(rho*2^T)"
    assert independent_rate_and_margin()["pass"]


def test_five_transducer_mutations_are_rejected() -> None:
    report = mutation_report()
    assert report["pass"]
    assert report["cases"] == report["rejected"] == 5


def test_claim_inventory_and_documents_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    separate_inventory = independent_inventory()
    assert central_inventory["pass"]
    assert separate_inventory["pass"]
    assert central_inventory["tests"] == separate_inventory["tests"] == 214
    assert claim_exactness_report()["pass"]
    assert independent_contract_and_claim()["pass"]
    assert document_sentinels()["pass"]


def test_seven_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 7


def test_complete_v018_report_passes_all_ten_gates() -> None:
    report = finite_state_sensor_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
