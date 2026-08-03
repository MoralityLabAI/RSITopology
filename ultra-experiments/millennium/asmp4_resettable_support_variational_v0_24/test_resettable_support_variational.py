"""Focused tests for ASMP-4 v0.24 resettable support theorem."""

from __future__ import annotations

import math

from resettable_support_variational import (
    claim_exactness_report,
    coordinate_invariance_report,
    exact_recoveries_report,
    mutation_report,
    predecessor_inventory_report,
    relational_schedule_report,
    resettable_support_report,
    resource_integrity_report,
    schema_exactness_report,
    verification_gates,
    weighted_variational_report,
)
from verify_resettable_support_variational import (
    document_sentinels,
    independent_boundary_recoveries,
    independent_coordinate_invariance,
    independent_integrity,
    independent_inventory,
    independent_mutations,
    independent_relational_wedge,
    independent_report,
    independent_schedule_frontiers,
    independent_schema_and_source,
    independent_support_reconstruction,
)


def test_four_resource_seals_and_parameterized_schema_match() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert schema_exactness_report()["pass"]
    assert independent_schema_and_source()["pass"]


def test_multiplicative_schedule_frontiers_hold_twice() -> None:
    central = relational_schedule_report()
    separate = independent_schedule_frontiers()
    assert central["pass"]
    assert separate["pass"]
    assert central["rows"][-1]["points"] == 9


def test_weighted_support_reconstructs_random_upper_convex_hulls() -> None:
    report = independent_support_reconstruction()
    assert report["pass"]
    assert len(report["fixtures"]) == 64


def test_relational_wedge_requires_the_joint_critical_normal() -> None:
    central = weighted_variational_report()
    separate = independent_relational_wedge()
    assert central["pass"]
    assert separate["pass"]
    assert math.isclose(central["theta"], math.log2(1.5))
    assert central["checks"]["coordinate_corner_rejected"]


def test_rectangles_clone_family_and_empty_region_are_recovered() -> None:
    assert exact_recoveries_report()["pass"]
    assert independent_boundary_recoveries()["pass"]


def test_coordinate_changes_preserve_the_weighted_entropy() -> None:
    assert coordinate_invariance_report()["pass"]
    assert independent_coordinate_invariance()["pass"]


def test_five_support_function_mutations_are_rejected_twice() -> None:
    central = mutation_report()
    assert central["pass"]
    assert central["cases"] == central["rejected"] == 5
    assert independent_mutations()["pass"]


def test_claim_inventory_and_documents_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    separate_inventory = independent_inventory()
    assert central_inventory["pass"]
    assert separate_inventory["pass"]
    assert central_inventory["tests"] == separate_inventory["tests"] == 274
    assert claim_exactness_report()["pass"]
    assert document_sentinels()["pass"]


def test_seven_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 7


def test_complete_v024_report_passes_all_ten_gates() -> None:
    report = resettable_support_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
