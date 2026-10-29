from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from honest_search_barrier import (
    build_result,
    maximin_success,
    permutation_audit,
    required_queries,
    search_row,
    subset_strategy_audit,
)
from verify_honest_search_barrier import verify


Q = Fraction
HERE = Path(__file__).resolve().parent


def test_invalid_parameters_are_rejected() -> None:
    for bits, budget in ((0, 0), (3, -1), (3, 9)):
        with pytest.raises(ValueError):
            maximin_success(bits, budget)
    with pytest.raises(ValueError):
        required_queries(3, Q(0))


def test_refutation_dimension_and_post_witness_check_are_one() -> None:
    for bits in range(1, 41):
        row = search_row(bits)
        assert row["replication_quotiented_refutation_dimension"] == 1
        assert row["post_witness_verifier_semantic_queries"] == 1
        assert row["witness_description_bits"] == bits


def test_randomized_maximin_success_is_q_over_N() -> None:
    for bits in range(1, 13):
        marker_count = 1 << bits
        for budget in {0, 1, marker_count // 3, marker_count}:
            assert maximin_success(bits, budget) == Q(budget, marker_count)


def test_two_thirds_success_requires_linear_queries() -> None:
    for bits in range(1, 41):
        marker_count = 1 << bits
        assert required_queries(bits, Q(2, 3)) == (2 * marker_count + 2) // 3


def test_polynomial_index_budget_success_vanishes() -> None:
    rows = [search_row(bits) for bits in range(20, 41)]
    assert all(
        Q(row["exact_randomized_maximin_success"])
        == Q(row["index_bits"] ** 3, 1 << row["index_bits"])
        for row in rows
    )
    assert Q(rows[-1]["exact_randomized_maximin_success"]) < Q(1, 1_000_000)


def test_deterministic_exact_and_or_macro_cost_are_N() -> None:
    for bits in range(1, 21):
        row = search_row(bits)
        assert row["deterministic_exact_worst_case_queries"] == 1 << bits
        assert row["full_or_macro_evaluation_queries"] == 1 << bits


def test_small_uniform_subset_strategy_attains_upper_bound() -> None:
    rows = subset_strategy_audit()
    assert len(rows) == 63
    assert all(row["averaging_upper_bound_matches"] for row in rows)
    assert all(
        Q(row["uniform_subset_success_per_marker"])
        == Q(row["query_budget"], row["semantic_atom_count"])
        for row in rows
    )


def test_atom_permutations_preserve_dimension_and_search_cost() -> None:
    rows = permutation_audit()
    assert len(rows) == 30
    assert all(row["bijection"] for row in rows)
    assert all(row["refutation_dimension_before"] == row["refutation_dimension_after"] == 1 for row in rows)
    assert all(row["deterministic_search_queries_before"] == row["deterministic_search_queries_after"] for row in rows)


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["search_rows"]) == 40
    assert len(result["small_subset_strategy_audit"]) == 63
    assert len(result["permutation_invariance_audit"]) == 30
    assert result["certified"]
    assert len(result["gates"]) == 10
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 8
    assert all(result["checks"].values())


def test_find_check_and_interface_boundaries_are_explicit() -> None:
    theorem = (HERE / "HONEST_SEARCH_BARRIER_THEOREM_v2_1.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v2_1.md").read_text(encoding="utf-8")
    assert "Find(tau)" in theorem and "Check(tau,S)" in theorem
    assert "zero-marker world remains legal" in theorem
    assert "black-box and classical" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
