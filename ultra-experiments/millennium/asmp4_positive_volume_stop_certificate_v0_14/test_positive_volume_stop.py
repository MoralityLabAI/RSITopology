"""Focused tests for the ASMP-4 v0.14 harness stop certificate."""

from __future__ import annotations

import json

from positive_volume_stop_certificate import (
    bounded_work_exhaustion_report,
    claim_exactness_report,
    nondegenerate_fork_report,
    positive_volume_stop_report,
    predecessor_inventory_report,
    prior_stop_lift_report,
    resource_integrity_report,
    selector_counterfactual_report,
    source_selector_audit,
    verification_gates,
)
from verify_positive_volume_stop import (
    document_sentinels,
    independent_claim_audit,
    independent_fork_replay,
    independent_integrity,
    independent_inventory,
    independent_lift_audit,
    independent_report,
    independent_selector_mutations,
    independent_source_audit,
)


def test_three_sealed_resources_match_independently() -> None:
    central = resource_integrity_report()
    independent = independent_integrity()
    assert central["pass"]
    assert independent["pass"]
    assert central["resources"] == len(independent["rows"]) == 3


def test_source_has_obligations_but_no_sensor_selector() -> None:
    assert source_selector_audit()["pass"]
    assert independent_source_audit()["pass"]


def test_nondegenerate_fork_replays_for_all_checked_horizons() -> None:
    central = nondegenerate_fork_report()
    independent = independent_fork_replay()
    assert central["pass"]
    assert independent["pass"]
    assert len(central["rows"]) == 10
    assert len(independent["rows"]) == 12


def test_prior_stop_is_lifted_after_geometry_repairs() -> None:
    assert prior_stop_lift_report()["pass"]
    assert independent_lift_audit()["pass"]


def test_five_selector_additions_produce_two_regions() -> None:
    central = selector_counterfactual_report()
    independent = independent_selector_mutations()
    assert central["pass"]
    assert independent["pass"]
    assert len(central["rows"]) == len(independent["rows"]) == 5


def test_bounded_work_exhaustion_has_four_reopening_conditions() -> None:
    report = bounded_work_exhaustion_report()
    assert report["pass"]
    assert report["checks"]["reopening_conditions_are_external_or_falsifying"]


def test_claim_and_predecessor_inventory_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    independent_inventory_report = independent_inventory()
    assert central_inventory["pass"]
    assert independent_inventory_report["pass"]
    assert central_inventory["tests"] == independent_inventory_report["tests"] == 174
    assert claim_exactness_report()["pass"]
    assert independent_claim_audit()["pass"]


def test_documents_state_stop_boundary_and_nonclaim() -> None:
    assert document_sentinels()["pass"]


def test_eight_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 8


def test_complete_v014_report_passes_all_ten_gates() -> None:
    report = positive_volume_stop_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
    assert json.loads(json.dumps({"report": report, "gates": gates}))["report"]["pass"]
