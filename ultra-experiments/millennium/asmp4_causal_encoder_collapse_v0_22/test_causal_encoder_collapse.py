"""Focused tests for ASMP-4 v0.22 causal encoder collapse."""

from __future__ import annotations

from causal_encoder_collapse import (
    causal_collapse_theorem_report,
    causal_encoder_report,
    claim_exactness_report,
    contextual_separation_report,
    contract_exactness_report,
    finite_margin_report,
    memoryless_support_census_report,
    mutation_report,
    predecessor_inventory_report,
    resource_integrity_report,
    small_deterministic_census_report,
    verification_gates,
)
from verify_causal_encoder_collapse import (
    document_sentinels,
    independent_contextual_separation,
    independent_contract_and_claim,
    independent_general_theorem,
    independent_integrity,
    independent_inventory,
    independent_memoryless_and_margin,
    independent_report,
    independent_small_census,
)


def test_two_resource_seals_and_contract_match() -> None:
    assert resource_integrity_report()["pass"]
    assert independent_integrity()["pass"]
    assert contract_exactness_report()["pass"]


def test_general_causal_collapse_theorem_holds_twice() -> None:
    assert causal_collapse_theorem_report()["pass"]
    assert independent_general_theorem()["pass"]


def test_every_feasible_fixture_encodes_exact_binary_q_language() -> None:
    report = causal_collapse_theorem_report()
    feasible = [row for row in report["rows"] if row["feasible"]]
    assert len(feasible) == 5
    assert all(row["encoded_counts"][:4] == [2, 4, 8, 16] for row in feasible)
    assert all(row["causal_read_corner"] == 2 for row in feasible)


def test_contextual_fixture_strictly_separates_static_and_causal() -> None:
    central = contextual_separation_report()
    separate = independent_contextual_separation()
    assert central["pass"]
    assert separate["pass"]
    assert central["checks"]["only_discrete_static_partition_feasible"]
    assert central["checks"]["raw_language_three_power"]
    assert central["checks"]["causal_language_two_power"]


def test_all_256_small_transducers_inherit_collapse() -> None:
    central = small_deterministic_census_report()
    separate = independent_small_census()
    assert central["pass"]
    assert separate["pass"]
    assert central["census"] == {"transducers": 256, "feasible": 80, "infeasible": 176}


def test_memoryless_census_and_finite_margin_hold_twice() -> None:
    census = memoryless_support_census_report()
    margin = finite_margin_report()
    assert census["pass"]
    assert census["census"]["feasible"] == 724
    assert margin["pass"]
    assert margin["formula"]["region"] == "[2,infinity) x [2,infinity)"
    assert independent_memoryless_and_margin()["pass"]


def test_five_causal_encoding_mutations_are_rejected() -> None:
    report = mutation_report()
    assert report["pass"]
    assert report["cases"] == report["rejected"] == 5


def test_claim_inventory_and_documents_are_exact() -> None:
    central_inventory = predecessor_inventory_report()
    separate_inventory = independent_inventory()
    assert central_inventory["pass"]
    assert separate_inventory["pass"]
    assert central_inventory["tests"] == separate_inventory["tests"] == 254
    assert claim_exactness_report()["pass"]
    assert independent_contract_and_claim()["pass"]
    assert document_sentinels()["pass"]


def test_seven_import_independent_checks_pass() -> None:
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 7


def test_complete_v022_report_passes_all_ten_gates() -> None:
    report = causal_encoder_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 10
    assert all(gates.values())
