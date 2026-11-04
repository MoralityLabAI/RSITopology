"""Focused tests for the ASMP-4 v0.10 adversarial stopping audit."""

from __future__ import annotations

from stopping_red_team import (
    canonical_scope_report,
    claim_exactness_report,
    coordinate_relabeling_report,
    counterargument_matrix,
    machine_index_report,
    minimal_stopping_theorem,
    prior_art_scope_report,
    primary_sensor_witness_report,
    resource_integrity_report,
    selector_mutation_report,
    stochastic_scope_firewall_report,
    stopping_red_team_report,
    targeted_literature_near_miss_report,
    test_inventory_report as predecessor_test_inventory_report,
    verification_gates,
)
from verify_stopping_red_team import (
    document_sentinels,
    independent_claim_audit,
    independent_coordinate_relabeling,
    independent_index_audit,
    independent_integrity,
    independent_prior_art_scope,
    independent_report,
    independent_scope_parser,
    independent_selector_mutations,
    independent_sensor_replay,
    independent_stochastic_firewall,
    independent_targeted_literature_near_misses,
    independent_test_inventory,
)


def test_five_sealed_resources_match_in_both_implementations() -> None:
    central = resource_integrity_report()
    independent = independent_integrity()
    assert central["pass"]
    assert independent["pass"]
    assert central["resources"] == len(independent["rows"]) == 5


def test_two_parsers_partition_canonical_scope() -> None:
    central = canonical_scope_report()
    independent = independent_scope_parser()
    assert central["pass"]
    assert independent["pass"]
    assert central["checks"]["positive_conjecture_is_registered_nhim"]
    assert central["checks"]["boundary_task_names_nonhyperbolicity"]


def test_four_cited_primary_sources_supply_no_two_port_registry_selector() -> None:
    central = prior_art_scope_report()
    independent = independent_prior_art_scope()
    assert central["pass"]
    assert independent["pass"]
    assert central["totals"] == independent["totals"]
    assert central["totals"]["canonical_primary_sources"] == 4
    assert central["totals"]["single_charged_information_resources"] == 4
    assert central["totals"]["separate_write_ports_charged"] == 0
    assert central["totals"]["asmp4_two_port_registry_selectors"] == 0
    assert central["totals"]["explicit_information_pattern_sensitivity_sources"] == 1
    assert central["totals"]["external_expert_review"] is False


def test_three_targeted_near_misses_require_added_architecture_mapping() -> None:
    central = targeted_literature_near_miss_report()
    independent = independent_targeted_literature_near_misses()
    assert central["pass"]
    assert independent["pass"]
    assert central["totals"] == independent["totals"]
    assert central["totals"]["reviewed_primary_near_misses"] == 3
    assert central["totals"]["genuine_multirate_regions"] == 1
    assert central["totals"]["same_channel_multiple_rate_notions"] == 1
    assert central["totals"]["network_ife_compositions"] == 1
    assert central["totals"]["asmp4_registry_selectors"] == 0
    assert central["totals"]["full_text_definition_reviews"] == 3
    assert central["totals"]["exhaustive_search"] is False
    assert central["totals"]["external_expert_review"] is False


def test_machine_index_cannot_supply_either_selector() -> None:
    central = machine_index_report()
    independent = independent_index_audit()
    assert central["pass"]
    assert independent["pass"]
    assert central["checks"]["index_is_non_normative"]
    assert central["checks"]["graduation_unsatisfied"]


def test_rational_embedding_has_nhim_and_local_control_checks() -> None:
    report = primary_sensor_witness_report()
    assert report["pass"]
    assert all(report["embedding_checks"].values())
    assert len(report["invariant_set_rows"]) == 16
    assert all(row["correct_stays_in_K"] for row in report["invariant_set_rows"])
    assert all(row["wrong_leaves_K"] for row in report["invariant_set_rows"])
    assert report["primary_witness_scope"] == (
        "registered NHIM/local-control sensor-domain fork"
    )


def test_same_plant_models_satisfy_thirteen_obligations() -> None:
    report = primary_sensor_witness_report()
    checks = report["source_model_checks"]
    assert checks["thirteen_source_obligations"]
    assert checks["computed_model_satisfies_all"]
    assert checks["raw_model_satisfies_all"]
    assert checks["same_plant_and_only_upstream_change"]


def test_mode_word_replay_matches_all_finite_formulas() -> None:
    central = primary_sensor_witness_report()
    independent = independent_sensor_replay()
    assert central["enumerated_mode_words_per_registry"] == 5460
    assert len(central["rows"]) == len(independent["rows"]) == 12
    assert not central["failures"]
    assert not independent["failures"]
    assert all(row["matches_formula"] for row in central["rows"])


def test_primary_witness_regions_are_exact_and_distinct() -> None:
    report = primary_sensor_witness_report()
    formulas = report["all_horizon_formulas"]
    assert formulas["computed_region"] == "[1,infinity) x [1,infinity)"
    assert formulas["raw_region"] == "[2,infinity) x [1,infinity)"
    assert formulas["computed_region"] != formulas["raw_region"]
    assert formulas["sealed_finite_formulas_match"]


def test_all_coordinate_and_symbol_relabelings_preserve_regions() -> None:
    central = coordinate_relabeling_report()
    independent = independent_coordinate_relabeling()
    assert central["pass"]
    assert independent["pass"]
    assert central["cases"] == independent["cases"] == 2304
    assert (
        central["mode_words_per_registry"]
        == (independent["mode_words_per_registry"])
        == 193536
    )
    assert central["failures"] == []
    assert independent["failures"] == 0


def test_stochastic_diagonal_is_explicitly_firewalled() -> None:
    central = stochastic_scope_firewall_report()
    independent = independent_stochastic_firewall()
    assert central["pass"]
    assert independent["pass"]
    assert not central["classification"]["positive_nhim_conjecture_witness"]
    assert not central["classification"]["used_by_minimal_sensor_stopping_proof"]
    assert not independent["minimal_proof_dependency"]


def test_explicit_selector_mutations_make_the_target_determinate() -> None:
    central = selector_mutation_report()
    independent = independent_selector_mutations()
    assert central["pass"]
    assert independent["pass"]
    assert len(central["rows"]) == len(independent["rows"]) == 5
    assert not central["rows"][0]["determinate"]
    assert all(row["determinate"] for row in central["rows"][1:])
    assert central["rows"][-1]["selected_target"] == ("[1,infinity) x [1,infinity)")


def test_all_fourteen_adversarial_counterarguments_are_resolved() -> None:
    report = counterargument_matrix()
    assert report["pass"]
    assert report["count"] == 14
    assert report["unresolved"] == []
    assert all(row["resolved"] for row in report["rows"])


def test_minimal_stopping_theorem_uses_no_stochastic_premise() -> None:
    report = minimal_stopping_theorem()
    assert report["pass"]
    assert all(report["premises"].values())
    assert report["stochastic_witness_used"] is False
    assert report["decision"] == (
        "sensor_registry_alone_proves_semantic_underdetermination"
    )


def test_predecessor_inventory_is_ten_packages_and_127_tests() -> None:
    central = predecessor_test_inventory_report()
    independent = independent_test_inventory()
    assert central["pass"]
    assert independent["pass"]
    assert central["packages"] == independent["packages"] == 10
    assert central["predecessor_tests"] == independent["tests"] == 127


def test_frozen_v010_claim_is_exact_in_both_implementations() -> None:
    assert claim_exactness_report()["pass"]
    assert independent_claim_audit()["pass"]


def test_documents_and_independent_report_pass() -> None:
    assert document_sentinels()["pass"]
    report = independent_report()
    assert report["pass"]
    assert len(report["checks"]) == 13


def test_complete_red_team_report_passes_all_fourteen_gates() -> None:
    report = stopping_red_team_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 14
    assert all(gates.values())
