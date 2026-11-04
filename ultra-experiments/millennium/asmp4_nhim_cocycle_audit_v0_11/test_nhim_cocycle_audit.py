"""Focused tests for the ASMP-4 v0.11 cocycle and local-control repair."""

from __future__ import annotations

from nhim_cocycle_audit import (
    bounded_authority_report,
    causal_timing_report,
    claim_exactness_report,
    cocycle_nhim_report,
    definition_mutation_report,
    exact_region_report,
    nhim_cocycle_audit_report,
    predecessor_inventory_report,
    primary_definition_report,
    repair_consequence_report,
    resource_integrity_report,
    verification_gates,
)
from verify_nhim_cocycle_audit import (
    document_sentinels,
    independent_authority_reachability,
    independent_claim_audit,
    independent_cocycle_nhim,
    independent_definition_mutations,
    independent_exact_regions,
    independent_integrity,
    independent_inventory,
    independent_report,
    independent_source_definition_audit,
)


def test_three_sealed_resources_match_in_both_implementations() -> None:
    central = resource_integrity_report()
    independent = independent_integrity()
    assert central["pass"]
    assert independent["pass"]
    assert central["resources"] == len(independent["rows"]) == 3


def test_primary_random_nhim_definition_is_mapped_and_scope_limited() -> None:
    assert primary_definition_report()["pass"]
    assert independent_source_definition_audit()["pass"]


def test_bounded_interval_authority_supplies_uniform_local_reachability() -> None:
    central = bounded_authority_report()
    independent = independent_authority_reachability()
    assert central["pass"]
    assert independent["pass"]
    assert central["checks"]["both_safe_controls_are_interior"]
    assert central["checks"]["local_box_fits_by_exact_margin"]


def test_full_shift_closed_loop_satisfies_cocycle_nhim_conditions() -> None:
    central = cocycle_nhim_report()
    independent = independent_cocycle_nhim()
    assert central["pass"]
    assert independent["pass"]
    assert central["splitting"] == {"E_u": "R", "E_c": "{0}", "E_s": "{0}"}
    assert central["holds_for"] == "every omega, not merely almost every omega"


def test_universal_mode_word_replay_has_no_failures() -> None:
    central = cocycle_nhim_report()
    independent = independent_cocycle_nhim()
    assert central["enumerated_mode_words"] == independent["enumerated_words"] == 5460
    assert all(row["all_safe"] for row in central["word_rows"])


def test_zero_delay_schedule_is_causal_and_uses_no_lookahead() -> None:
    report = causal_timing_report()
    assert report["pass"]
    assert report["checks"]["no_future_disturbance_lookahead"]
    assert report["checks"]["one_step_stale_controller_is_infeasible_at_t_zero"]


def test_continuous_authority_preserves_both_exact_regions() -> None:
    central = exact_region_report()
    independent = independent_exact_regions()
    assert central["pass"]
    assert independent["pass"]
    assert central["computed_region"] == independent["computed_region"]
    assert central["raw_region"] == independent["raw_region"]


def test_discrete_derivative_category_gap_is_repaired() -> None:
    report = repair_consequence_report()
    assert report["pass"]
    assert report["checks"]["v06_used_binary_action_set"]
    assert report["checks"]["interval_authority_repairs_local_reachability"]
    assert report["checks"]["full_shift_cocycle_repairs_nhim_category"]
    central_mutations = definition_mutation_report()
    independent_mutations = independent_definition_mutations()
    assert central_mutations["pass"]
    assert independent_mutations["pass"]
    assert central_mutations["cases"] == independent_mutations["cases"] == 5


def test_claim_documents_inventory_and_independent_report_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    independent_inventory_report = independent_inventory()
    assert central_inventory["pass"]
    assert independent_inventory_report["pass"]
    assert central_inventory["tests"] == independent_inventory_report["tests"] == 145
    assert claim_exactness_report()["pass"]
    assert independent_claim_audit()["pass"]
    assert document_sentinels()["pass"]
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 11


def test_complete_v011_report_passes_all_twelve_gates() -> None:
    report = nhim_cocycle_audit_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 12
    assert all(gates.values())
