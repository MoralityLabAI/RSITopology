"""Focused tests for the ASMP-4 v0.12 positive-dimensional NHIM."""

from __future__ import annotations

from positive_dimensional_nhim import (
    adversarial_mutation_report,
    capacity_and_causality_report,
    circle_nhim_report,
    claim_exactness_report,
    local_control_report,
    positive_dimensional_nhim_report,
    predecessor_inventory_report,
    primary_definition_report,
    resource_integrity_report,
    verification_gates,
)
from verify_positive_dimensional_nhim import (
    document_sentinels,
    independent_circle_nhim,
    independent_claim_audit,
    independent_control_capacity,
    independent_definition_audit,
    independent_integrity,
    independent_inventory,
    independent_mutations,
    independent_report,
)


def test_two_resource_seals_match_independently() -> None:
    central = resource_integrity_report()
    independent = independent_integrity()
    assert central["pass"]
    assert independent["pass"]
    assert central["resources"] == len(independent["rows"]) == 2


def test_primary_classical_nhim_definition_is_mapped() -> None:
    assert primary_definition_report()["pass"]
    assert independent_definition_audit()["pass"]


def test_circle_is_positive_dimensional_compact_classical_nhim() -> None:
    central = circle_nhim_report()
    independent = independent_circle_nhim()
    assert central["pass"]
    assert independent["pass"]
    assert central["dimension"] == 1
    assert central["norms"] == {
        "tangent": "1",
        "unstable_inverse": "2/3",
        "lambda": "3/4",
    }


def test_bounded_authority_preserves_local_control() -> None:
    assert local_control_report()["pass"]
    assert independent_control_capacity()["pass"]


def test_tangent_rotation_adds_no_rate_and_regions_remain_distinct() -> None:
    report = capacity_and_causality_report()
    assert report["pass"]
    assert report["computed_region"] == "[1,infinity) x [1,infinity)"
    assert report["raw_region"] == "[2,infinity) x [1,infinity)"
    assert report["checks"]["tangent_phase_adds_no_transcript_symbols"]


def test_current_control_uses_no_future_mode() -> None:
    report = capacity_and_causality_report()
    assert report["checks"]["no_future_mode_lookahead"]
    assert report["checks"]["zero_delay_order_is_observe_read_write_control_reset"]


def test_five_adversarial_mutations_are_rejected_twice() -> None:
    central = adversarial_mutation_report()
    independent = independent_mutations()
    assert central["pass"]
    assert independent["pass"]
    assert central["cases"] == independent["cases"] == 5


def test_claim_inventory_documents_and_independent_report_pass() -> None:
    central_inventory = predecessor_inventory_report()
    independent_inventory_report = independent_inventory()
    assert central_inventory["pass"]
    assert independent_inventory_report["pass"]
    assert central_inventory["tests"] == independent_inventory_report["tests"] == 155
    assert claim_exactness_report()["pass"]
    assert independent_claim_audit()["pass"]
    assert document_sentinels()["pass"]
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 8


def test_complete_v012_report_passes_all_nine_gates() -> None:
    report = positive_dimensional_nhim_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 9
    assert all(gates.values())
