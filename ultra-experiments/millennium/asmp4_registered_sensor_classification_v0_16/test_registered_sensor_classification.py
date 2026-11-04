"""Focused tests for the ASMP-4 v0.16 registered sensor theorem."""

from __future__ import annotations

from registered_sensor_classification import (
    claim_exactness_report,
    contract_exactness_report,
    feasible_language_report,
    finite_margin_report,
    infeasible_partition_report,
    lattice_monotonicity_report,
    mutation_report,
    partition_census_report,
    predecessor_inventory_report,
    registered_sensor_classification_report,
    resource_integrity_report,
    verification_gates,
)
from verify_registered_sensor_classification import (
    document_sentinels,
    independent_contract_and_claim,
    independent_feasible_languages,
    independent_finite_margin,
    independent_infeasibility,
    independent_integrity,
    independent_inventory,
    independent_partition_census,
    independent_report,
)


def test_two_resource_seals_and_contract_match() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert contract_exactness_report()["pass"]


def test_all_fifteen_partitions_have_exact_feasibility_labels() -> None:
    central = partition_census_report()
    independent = independent_partition_census()
    assert central["pass"]
    assert independent["pass"]
    assert len(central["rows"]) == 15
    assert central["feasible_histogram"] == {2: 1, 3: 2, 4: 1}


def test_four_feasible_partition_languages_have_exact_counts() -> None:
    assert feasible_language_report()["pass"]
    assert independent_feasible_languages()["pass"]


def test_eleven_nonrefining_partitions_fail_at_first_step() -> None:
    central = infeasible_partition_report()
    assert central["pass"]
    assert len(central["rows"]) == 11
    assert independent_infeasibility()["pass"]


def test_exact_finite_margin_formulas_hold_twice() -> None:
    central = finite_margin_report()
    assert central["pass"]
    assert central["formula"]["read"] == "k^T ceil(rho*2^T)"
    assert independent_finite_margin()["pass"]


def test_feasible_partition_lattice_is_monotone() -> None:
    report = lattice_monotonicity_report()
    assert report["pass"]
    assert len(report["edges"]) == 4


def test_five_contract_mutations_are_rejected() -> None:
    report = mutation_report()
    assert report["pass"]
    assert report["cases"] == report["rejected"] == 5


def test_claim_inventory_and_documents_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    independent_inventory_report = independent_inventory()
    assert central_inventory["pass"]
    assert independent_inventory_report["pass"]
    assert central_inventory["tests"] == independent_inventory_report["tests"] == 194
    assert claim_exactness_report()["pass"]
    assert independent_contract_and_claim()["pass"]
    assert document_sentinels()["pass"]


def test_eight_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 8


def test_complete_v016_report_passes_all_ten_gates() -> None:
    report = registered_sensor_classification_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
