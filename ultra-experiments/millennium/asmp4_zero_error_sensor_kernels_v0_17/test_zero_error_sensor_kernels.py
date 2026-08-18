"""Focused tests for ASMP-4 v0.17 support-zero-error kernels."""

from __future__ import annotations

from verify_zero_error_sensor_kernels import (
    document_sentinels,
    independent_combinatorial_census,
    independent_contract_and_claim,
    independent_integrity,
    independent_inventory,
    independent_rate_and_margin,
    independent_report,
    independent_support_theorem,
)
from zero_error_sensor_kernels import (
    claim_exactness_report,
    contract_exactness_report,
    deterministic_embedding_report,
    finite_margin_report,
    mutation_report,
    predecessor_inventory_report,
    representative_language_report,
    resource_integrity_report,
    support_census_report,
    support_feasibility_theorem_report,
    verification_gates,
    zero_error_sensor_kernel_report,
)


def test_two_resource_seals_and_contract_match() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert contract_exactness_report()["pass"]


def test_all_53108_support_relations_match_combinatorial_census() -> None:
    central = support_census_report()
    independent = independent_combinatorial_census()
    assert central["pass"]
    assert independent["pass"]
    assert central["combined"]["feasible"] == 724
    assert central["combined"]["infeasible"] == 52384


def test_support_disjointness_is_exact_feasibility_criterion() -> None:
    assert support_feasibility_theorem_report()["pass"]
    assert independent_support_theorem()["pass"]


def test_randomized_representatives_have_exact_languages() -> None:
    report = representative_language_report()
    assert report["pass"]
    assert {row["active_outputs"] for row in report["rows"]} == {2, 3, 4}


def test_exact_finite_margin_formulas_hold_twice() -> None:
    central = finite_margin_report()
    assert central["pass"]
    assert central["formula"]["read"] == "a^T ceil(rho*2^T)"
    assert independent_rate_and_margin()["pass"]


def test_v016_deterministic_partition_theorem_is_recovered() -> None:
    report = deterministic_embedding_report()
    assert report["pass"]
    assert report["checks"]["four_unlabeled_partitions"]


def test_five_kernel_mutations_are_rejected() -> None:
    report = mutation_report()
    assert report["pass"]
    assert report["cases"] == report["rejected"] == 5


def test_claim_inventory_and_documents_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    independent_inventory_report = independent_inventory()
    assert central_inventory["pass"]
    assert independent_inventory_report["pass"]
    assert central_inventory["tests"] == independent_inventory_report["tests"] == 204
    assert claim_exactness_report()["pass"]
    assert independent_contract_and_claim()["pass"]
    assert document_sentinels()["pass"]


def test_seven_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 7


def test_complete_v017_report_passes_all_ten_gates() -> None:
    report = zero_error_sensor_kernel_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
