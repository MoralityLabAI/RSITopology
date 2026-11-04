from __future__ import annotations

import json
from fractions import Fraction

from correlated_path_risk import (
    ARTIFACT_PATH,
    build_artifact,
    common_mode_rows,
    conditional_chain_rows,
    controller_comparison_rows,
    exchangeable_mixture_audit,
    persistent_online_composition_rows,
    selection_correlated_rows,
)
from verify_correlated_path_risk import verify


def test_common_mode_path_error_is_eta_for_every_query_count() -> None:
    rows = common_mode_rows()
    assert len(rows) == 24
    assert all(Fraction(row["path_error_probability"]) == Fraction(row["eta"]) for row in rows)
    assert all(not row["replication_amplifies"] for row in rows)


def test_common_mode_online_margin_remains_positive() -> None:
    assert all(Fraction(row["online_finder_success_lower_bound"]) > 0 for row in common_mode_rows())


def test_conditional_chain_bound_does_not_assume_independence() -> None:
    rows = conditional_chain_rows()
    assert len(rows) == 20
    for row in rows:
        assert not row["independence_required"]
        assert Fraction(row["matching_prefix_probability_lower_bound"]) + Fraction(
            row["path_error_probability_upper_bound"]
        ) == 1


def test_exchangeable_mixture_jensen_audit_is_exact() -> None:
    audit = exchangeable_mixture_audit()
    assert audit["mixture_query_cases"] == 18_012
    assert audit["jensen_bound_violations"] == 0
    assert audit["jensen_equality_cases"] > 0
    assert audit["certified"]


def test_same_marginals_have_distinct_joint_path_risk() -> None:
    rows = controller_comparison_rows()
    assert len(rows) == 20
    assert all(row["same_fixed_atom_marginal"] for row in rows)
    assert all(row["common_mode_is_no_worse_for_path_risk"] for row in rows)


def test_selection_correlated_marginals_do_not_bound_selected_error() -> None:
    rows = selection_correlated_rows()
    assert len(rows) == 31
    for row in rows:
        n = int(row["semantic_class_count"])
        assert Fraction(row["each_fixed_class_marginal_error"]) == Fraction(1, n)
        assert Fraction(row["actual_selected_path_error"]) == 1
        assert row["marginal_to_path_risk_ratio"] == n


def test_persistent_common_mode_composes_with_all_online_rows() -> None:
    rows = persistent_online_composition_rows()
    assert len(rows) == 12
    assert all(row["certified"] for row in rows)
    assert all(not row["noise_independence_required"] for row in rows)
    assert all(not row["strategy_restart_required"] for row in rows)


def test_useless_replication_is_removed_from_persistent_composition() -> None:
    for row in persistent_online_composition_rows():
        assert row["raw_semantic_queries_without_useless_replication"] == row[
            "maximum_adaptive_queries"
        ]


def test_all_producer_gates_pass() -> None:
    artifact = build_artifact()
    assert artifact["certified"]
    assert len(artifact["gates"]) == 10
    assert all(artifact["gates"].values())


def test_written_artifact_and_clean_room_checker_match() -> None:
    assert json.loads(ARTIFACT_PATH.read_text(encoding="utf-8")) == build_artifact()
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 10
