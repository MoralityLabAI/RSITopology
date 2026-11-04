"""Focused tests for ASMP-4 v0.20 sensor-refinement inflation."""

from __future__ import annotations

from sensor_refinement_inflation_stop import (
    claim_exactness_report,
    cloned_small_census_report,
    coarsening_report,
    contract_exactness_report,
    deterministic_robustness_report,
    finite_margin_report,
    mutation_report,
    predecessor_inventory_report,
    refinement_stop_report,
    refinement_theorem_report,
    resource_integrity_report,
    unbounded_inflation_report,
    verification_gates,
)
from verify_sensor_refinement_inflation_stop import (
    document_sentinels,
    independent_cloned_census,
    independent_contract_and_claim,
    independent_integrity,
    independent_inventory,
    independent_margin_and_stop,
    independent_refinement_theorem,
    independent_robustness,
    independent_report,
)


def test_two_resource_seals_and_contract_match() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert contract_exactness_report()["pass"]


def test_general_refinement_theorem_holds_twice() -> None:
    central = refinement_theorem_report()
    separate = independent_refinement_theorem()
    assert central["pass"]
    assert central["cases"] == 16
    assert separate["pass"]
    assert deterministic_robustness_report()["pass"]
    assert independent_robustness()["pass"]


def test_coarsening_exactly_recovers_base_sensor() -> None:
    report = coarsening_report()
    assert report["pass"]
    assert all(row["support_recovers"] for row in report["rows"])


def test_computed_read_inflation_is_unbounded_but_write_is_fixed() -> None:
    central = unbounded_inflation_report()
    separate = independent_margin_and_stop()
    assert central["pass"]
    assert central["rows"][0]["raw_read_corner"] == 2
    assert central["rows"][-1]["raw_read_corner"] == 10
    assert len({row["write_corner"] for row in central["rows"]}) == 1
    assert separate["pass"]


def test_all_768_cloned_small_transducers_match_independent_census() -> None:
    central = cloned_small_census_report()
    separate = independent_cloned_census()
    assert central["pass"]
    assert separate["pass"]
    assert all(
        row == {"feasible": 80, "infeasible": 176}
        for row in central["by_colors"].values()
    )


def test_exact_finite_margin_ratio_is_m_power_t() -> None:
    report = finite_margin_report()
    assert report["pass"]
    assert report["formula"]["ratio"] == "m^T"
    assert report["checks"]["write_equals_coarsened"]


def test_five_refinement_mutations_are_rejected() -> None:
    report = mutation_report()
    assert report["pass"]
    assert report["cases"] == report["rejected"] == 5


def test_claim_inventory_and_documents_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    separate_inventory = independent_inventory()
    assert central_inventory["pass"]
    assert separate_inventory["pass"]
    assert central_inventory["tests"] == separate_inventory["tests"] == 234
    assert claim_exactness_report()["pass"]
    assert independent_contract_and_claim()["pass"]
    assert document_sentinels()["pass"]


def test_seven_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 7


def test_complete_v020_report_passes_all_ten_gates() -> None:
    report = refinement_stop_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
