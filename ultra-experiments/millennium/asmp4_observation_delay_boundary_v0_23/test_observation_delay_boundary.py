"""Focused tests for ASMP-4 v0.23 observation-delay boundary."""

from __future__ import annotations

from observation_delay_boundary import (
    claim_exactness_report,
    contract_exactness_report,
    delay_boundary_report,
    delayed_adversary_tree_report,
    finite_counts_report,
    interval_impossibility_report,
    mutation_report,
    predecessor_inventory_report,
    resource_integrity_report,
    timing_boundary_report,
    verification_gates,
)
from verify_observation_delay_boundary import (
    document_sentinels,
    independent_contract_and_claim,
    independent_finite_counts,
    independent_history_adversary,
    independent_integrity,
    independent_interval_boundary,
    independent_inventory,
    independent_mutations,
    independent_report,
    independent_restoration,
)


def test_two_resource_seals_and_timing_contract_match() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert contract_exactness_report()["pass"]


def test_safe_intervals_have_an_exact_constant_gap_of_six() -> None:
    central = interval_impossibility_report()
    assert central["pass"]
    assert central["checks"]["affine_gap_identity"]
    assert central["checks"]["all_disjoint"]
    assert independent_interval_boundary()["pass"]


def test_every_positive_delay_has_a_common_history_collision() -> None:
    central = delayed_adversary_tree_report()
    separate = independent_history_adversary()
    assert central["pass"]
    assert len(central["rows"]) == 84
    assert separate["pass"]


def test_delay_zero_and_positive_delay_regions_are_sharp() -> None:
    report = timing_boundary_report()
    assert report["pass"]
    assert report["rows"][0]["region"] == "[2,infinity) x [2,infinity)"
    assert report["rows"][1]["region"] == "empty"


def test_preview_and_predictability_restore_liveness() -> None:
    report = timing_boundary_report()
    assert report["rows"][2]["region"] == "[2,infinity) x [2,infinity)"
    assert report["rows"][3]["region"] == "[1,infinity) x [1,infinity)"
    assert independent_restoration()["pass"]


def test_exact_finite_counts_and_collar_margin_hold_twice() -> None:
    central = finite_counts_report()
    assert central["pass"]
    assert central["formula"]["positive_delay_no_preview"] == "empty"
    assert independent_finite_counts()["pass"]


def test_five_delay_boundary_mutations_are_rejected_twice() -> None:
    central = mutation_report()
    assert central["pass"]
    assert central["cases"] == central["rejected"] == 5
    assert independent_mutations()["pass"]


def test_claim_inventory_and_documents_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    separate_inventory = independent_inventory()
    assert central_inventory["pass"]
    assert separate_inventory["pass"]
    assert central_inventory["tests"] == separate_inventory["tests"] == 264
    assert claim_exactness_report()["pass"]
    assert independent_contract_and_claim()["pass"]
    assert document_sentinels()["pass"]


def test_seven_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 7


def test_complete_v023_report_passes_all_ten_gates() -> None:
    report = delay_boundary_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
