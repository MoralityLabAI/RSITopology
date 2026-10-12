"""Focused tests for the ASMP-4 v0.8 randomness quantifier boundary."""

from __future__ import annotations

import json
from pathlib import Path

from randomness_quantifier import (
    canonical_randomness_quantifier_audit,
    continuous_diagonal_fixture,
    countable_disturbance_collapse,
    finite_grid_census,
    finite_grid_formula_phase_map,
    monte_carlo_trap_report,
    quantifier_models,
    randomness_quantifier_report,
    verification_gates,
)
from verify_randomness_quantifier import (
    document_sentinels,
    independent_grid_census,
    independent_phase_map,
    independent_quantifier_logic,
    independent_source_audit,
    predecessor_firewall,
)

HERE = Path(__file__).resolve().parent


def test_canonical_source_omits_probability_disturbance_order() -> None:
    report = canonical_randomness_quantifier_audit()
    assert report["pass"]
    assert report["probabilistic_safety_marker_count"] == 0
    assert report["decision"] == "randomness_disturbance_quantifier_underdetermined"


def test_independent_source_parser_reproduces_scope_audit() -> None:
    report = independent_source_audit()
    assert report["pass"]
    assert all(report["checks"].values())


def test_continuous_diagonal_separates_stochastic_semantics() -> None:
    report = continuous_diagonal_fixture()
    assert report["pass"]
    assert report["per_disturbance_almost_sure_safety"]
    assert not report["uniform_almost_sure_safety"]
    assert not report["support_zero_error_safety"]
    assert report["read_rate"] == report["write_rate"] == 0


def test_countable_disturbance_alphabet_collapses_almost_sure_order() -> None:
    report = countable_disturbance_collapse()
    assert report["pass"]
    assert all(report["obligations"].values())
    assert any("countably many" in step.lower() for step in report["proof_steps"])
    assert "null union" in report["proof_steps"][-1].lower()


def test_finite_grid_census_matches_every_closed_formula() -> None:
    report = finite_grid_census()
    assert report["pass"]
    assert report["cells"] == 16
    assert report["enumerated_seed_disturbance_pairs"] == 484524
    assert report["failures"] == []
    row = next(
        item for item in report["rows"] if item["symbols"] == 5 and item["horizon"] == 4
    )
    assert row["safe_seed_words_per_fixed_disturbance"] == 4**4
    assert row["safe_seed_disturbance_pairs"] == 20**4
    assert row["universal_safe_seed_words"] == 0


def test_base_n_independent_census_reproduces_all_pairs() -> None:
    report = independent_grid_census()
    assert report["pass"]
    assert report["total_pairs"] == 484524
    assert report["failures"] == []


def test_formula_phase_map_has_noncommuting_limits() -> None:
    report = finite_grid_formula_phase_map()
    assert report["pass"]
    assert report["cells"] == 60
    assert report["noncommuting_limits"] == {
        "lim_N_to_infinity_then_T_to_infinity_success": 1,
        "lim_T_to_infinity_then_N_to_infinity_success": 0,
    }


def test_independent_fraction_phase_map_agrees() -> None:
    report = independent_phase_map()
    assert report["pass"]
    assert report["cells"] == 60
    assert report["limit_order"] == {"N_then_T": 1, "T_then_N": 0}


def test_monte_carlo_nonfailure_does_not_certify_worst_case() -> None:
    report = monte_carlo_trap_report()
    assert report["pass"]
    assert report["continuous_random_pair_failure_probability"] == 0
    assert report["continuous_adaptive_diagonal_failure_probability"] == 1


def test_four_quantifier_models_change_zero_rate_feasibility() -> None:
    report = quantifier_models()
    assert report["pass"]
    models = report["models"]
    assert models["per_disturbance_almost_sure"]["region_contains_origin"]
    assert not models["uniform_almost_sure"]["region_contains_origin"]
    assert not models["support_zero_error"]["region_contains_origin"]
    assert not models["adaptive_disturbance"]["region_contains_origin"]


def test_independent_measure_logic_matches_quantifier_fork() -> None:
    report = independent_quantifier_logic()
    assert report["pass"]
    assert report["per_disturbance_almost_sure"]
    assert not report["uniform_almost_sure"]


def test_frozen_claim_matches_exact_evidence() -> None:
    claim = json.loads(
        (HERE / "randomness_claim_v0_8.json").read_text(encoding="utf-8")
    )
    assert claim["finite_grid_census"]["enumerated_seed_disturbance_pairs"] == 484524
    assert claim["formula_phase_map"]["cells"] == 60
    assert claim["continuous_diagonal_fixture"]["per_disturbance_almost_sure_safe"]
    assert not claim["continuous_diagonal_fixture"]["support_zero_error_safe"]


def test_documents_and_v07_firewall_are_complete() -> None:
    assert document_sentinels()["pass"]
    assert predecessor_firewall()["pass"]


def test_complete_payload_passes_all_eight_gates() -> None:
    report = randomness_quantifier_report()
    gates = verification_gates(report)
    assert report["pass"]
    assert len(gates) == 8
    assert all(gates.values())
