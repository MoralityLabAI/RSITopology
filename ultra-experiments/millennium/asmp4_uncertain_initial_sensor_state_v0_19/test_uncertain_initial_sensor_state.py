"""Focused tests for ASMP-4 v0.19 uncertain initial sensor state."""

from __future__ import annotations

from uncertain_initial_sensor_state import (
    claim_exactness_report,
    contract_exactness_report,
    finite_margin_report,
    fixture_theorem_report,
    mutation_report,
    predecessor_inventory_report,
    resource_integrity_report,
    uncertain_initial_census_report,
    uncertain_initial_report,
    verification_gates,
)
from verify_uncertain_initial_sensor_state import (
    document_sentinels,
    independent_census,
    independent_contract_and_claim,
    independent_fixtures,
    independent_integrity,
    independent_inventory,
    independent_rate_and_margin,
    independent_report,
)


def test_two_resource_seals_and_contract_match() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert contract_exactness_report()["pass"]


def test_start_belief_theorem_fixtures_hold_twice() -> None:
    assert fixture_theorem_report()["pass"]
    assert independent_fixtures()["pass"]


def test_unknown_initial_state_breaks_history_toggle() -> None:
    checks = fixture_theorem_report()["checks"]
    assert checks["known_toggle_feasible"]
    assert checks["uncertain_toggle_infeasible"]
    assert checks["uncertain_toggle_first_step_mixed"]


def test_transient_and_rate_inflation_languages_are_exact() -> None:
    report = fixture_theorem_report()
    rows = {row["name"]: row for row in report["rows"]}
    assert rows["synchronizing_transient"]["word_counts"][:4] == [4, 8, 16, 32]
    assert rows["synchronizing_transient"]["read_threshold"] == 2
    assert rows["union_dominant"]["word_counts"][:4] == [4, 16, 64, 256]
    assert rows["union_dominant"]["read_threshold"] == 3


def test_all_768_registered_pairs_match_independent_census() -> None:
    central = uncertain_initial_census_report()
    separate = independent_census()
    assert central["pass"]
    assert separate["pass"]
    assert central["census"]["feasible"] == 192
    assert central["census"]["infeasible"] == 576
    assert central["census"]["signature_histogram"]["110"] == 32


def test_exact_finite_margin_products_hold_twice() -> None:
    central = finite_margin_report()
    assert central["pass"]
    assert central["formula"]["read"] == "L_T(I) ceil(rho*2^T)"
    assert independent_rate_and_margin()["pass"]


def test_five_initial_state_mutations_are_rejected() -> None:
    report = mutation_report()
    assert report["pass"]
    assert report["cases"] == report["rejected"] == 5


def test_claim_inventory_and_documents_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    separate_inventory = independent_inventory()
    assert central_inventory["pass"]
    assert separate_inventory["pass"]
    assert central_inventory["tests"] == separate_inventory["tests"] == 224
    assert claim_exactness_report()["pass"]
    assert independent_contract_and_claim()["pass"]
    assert document_sentinels()["pass"]


def test_seven_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 7


def test_complete_v019_report_passes_all_ten_gates() -> None:
    report = uncertain_initial_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
