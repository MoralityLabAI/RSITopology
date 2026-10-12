"""Focused tests for ASMP-4 v0.25 periodic block completeness."""

from __future__ import annotations

from periodic_block_completeness import (
    claim_exactness_report,
    component_cycle_theorem_report,
    contract_exactness_report,
    mutation_report,
    nonconvex_fork_report,
    periodic_approximation_report,
    periodic_completeness_report,
    predecessor_inventory_report,
    resource_integrity_report,
    state_relabel_invariance_report,
    two_state_graph_census_report,
    verification_gates,
)
from verify_periodic_block_completeness import (
    document_sentinels,
    independent_closed_walk_decomposition,
    independent_connector_and_fork,
    independent_contract_and_claim,
    independent_integrity,
    independent_inventory,
    independent_mutations,
    independent_periodic_approximation,
    independent_report,
    independent_three_state_graph_census,
)


def test_three_resource_seals_and_contract_match() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert contract_exactness_report()["pass"]
    assert independent_contract_and_claim()["pass"]


def test_strong_component_cycle_polytope_is_exact() -> None:
    assert component_cycle_theorem_report()["pass"]
    assert independent_connector_and_fork()["pass"]


def test_periodic_closed_walks_approach_the_midpoint_twice() -> None:
    central = periodic_approximation_report()
    separate = independent_periodic_approximation()
    assert central["pass"]
    assert separate["pass"]
    assert len(central["rows"]) == 64


def test_irreversible_fork_is_nonconvex_and_component_indexed() -> None:
    report = nonconvex_fork_report()
    assert report["pass"]
    assert report["checks"]["midpoint_not_in_true_union"]
    assert report["checks"]["midpoint_in_global_support_convexification"]


def test_complete_small_graph_censuses_hold_independently() -> None:
    assert two_state_graph_census_report()["pass"]
    separate = independent_three_state_graph_census()
    assert separate["pass"]
    assert len(separate["rows"]) == 511


def test_every_enumerated_closed_walk_obeys_simple_cycle_supports() -> None:
    report = independent_closed_walk_decomposition()
    assert report["pass"]
    assert report["audited_walks"] > 1000


def test_state_relabel_and_five_mutations_are_rejected_twice() -> None:
    assert state_relabel_invariance_report()["pass"]
    central = mutation_report()
    assert central["pass"]
    assert central["cases"] == central["rejected"] == 5
    assert independent_mutations()["pass"]


def test_claim_inventory_and_documents_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    separate_inventory = independent_inventory()
    assert central_inventory["pass"]
    assert separate_inventory["pass"]
    assert central_inventory["tests"] == separate_inventory["tests"] == 284
    assert claim_exactness_report()["pass"]
    assert document_sentinels()["pass"]


def test_seven_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 7


def test_complete_v025_report_passes_all_ten_gates() -> None:
    report = periodic_completeness_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
