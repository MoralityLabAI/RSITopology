from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from block_selection_composition import (
    atom_error,
    build_result,
    composition_row,
    depth_requirement_rows,
    enumerate_small_case,
    minimal_depth,
)
from build_release_manifest import verify_manifest
from verify_block_selection_composition import verify


Q = Fraction
HERE = Path(__file__).resolve().parent


def test_invalid_parameters_are_rejected() -> None:
    for atoms, depth, eta in ((0, 3, Q(1, 5)), (2, 0, Q(1, 5)), (2, 3, Q(-1)), (2, 3, Q(1, 2))):
        with pytest.raises(ValueError):
            composition_row(atoms, depth, eta)
    with pytest.raises(ValueError):
        minimal_depth(1, Q(1, 5), Q(0), union_safe=False)


def test_single_atom_composition_reduces_to_parent_error() -> None:
    for eta in (Q(1, 10), Q(1, 5), Q(1, 3), Q(2, 5)):
        for depth in range(1, 32):
            row = composition_row(1, depth, eta)
            assert Q(row["independent_block_any_error"]) == atom_error(depth, eta)


def test_independent_joint_risk_is_exact_product_complement() -> None:
    for eta in (Q(1, 5), Q(1, 3)):
        for atoms in (1, 2, 4, 8):
            for depth in (1, 3, 5, 9):
                error = atom_error(depth, eta)
                row = composition_row(atoms, depth, eta)
                assert Q(row["independent_block_any_error"]) == 1 - (1 - error) ** atoms


def test_or_and_failure_selector_are_tight_interfaces() -> None:
    row = composition_row(32, 9, Q(1, 5))
    assert row["independent_block_any_error"] == row["or_all_zero_refutation_error"]
    assert row["independent_block_any_error"] == row["truth_aware_failure_selector_risk"]
    assert Q(row["selector_inflation_over_one_atom"]) > 0


def test_marginal_only_extremum_is_union_bound() -> None:
    for eta in (Q(1, 5), Q(1, 3)):
        for atoms in (1, 4, 16, 64):
            row = composition_row(atoms, 7, eta)
            error = atom_error(7, eta)
            assert Q(row["marginal_only_extremal_union_risk"]) == min(1, atoms * error)
            assert Q(row["independent_block_any_error"]) <= Q(row["union_bound"])


def test_persistent_per_atom_noise_is_never_improved_by_replication() -> None:
    for eta in (Q(1, 5), Q(1, 3)):
        for atoms in (1, 4, 16):
            shallow = composition_row(atoms, 1, eta)
            deep = composition_row(atoms, 9, eta)
            assert shallow["independent_per_atom_persistent_risk"] == deep[
                "independent_per_atom_persistent_risk"
            ]
            assert Q(deep["block_independence_improvement_over_per_atom_persistence"]) > 0


def test_raw_small_response_enumeration_matches_formula() -> None:
    for eta in (Q(1, 5), Q(1, 3)):
        for atoms in (1, 2, 3):
            for depth in (1, 3):
                row = enumerate_small_case(atoms, depth, eta)
                assert row["response_profiles_enumerated"] == 1 << (atoms * depth)
                assert row["matches"]


def test_minimal_depth_search_certifies_previous_odd_failure() -> None:
    for atoms, eta, target in ((1, Q(1, 5), Q(1, 100)), (16, Q(1, 3), Q(1, 10)), (64, Q(2, 5), Q(1, 100))):
        exact = minimal_depth(atoms, eta, target, union_safe=False)
        safe = minimal_depth(atoms, eta, target, union_safe=True)
        assert exact <= safe
        assert Q(composition_row(atoms, exact, eta)["independent_block_any_error"]) <= target
        assert Q(composition_row(atoms, safe, eta)["union_bound"]) <= target
        if exact > 1:
            assert Q(composition_row(atoms, exact - 2, eta)["independent_block_any_error"]) > target


def test_depth_requirement_registry_is_complete() -> None:
    rows = depth_requirement_rows()
    assert len(rows) == 24
    assert all(row["exact_minimality_certified"] for row in rows)
    assert all(row["union_minimality_certified"] for row in rows)


def test_query_cost_is_explicitly_charged() -> None:
    for atoms in (1, 2, 8, 32):
        for depth in (1, 5, 11):
            row = composition_row(atoms, depth, Q(1, 5))
            assert row["total_semantic_queries"] == atoms * depth


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["composition_rows"]) == 744
    assert len(result["small_response_enumeration"]) == 12
    assert len(result["depth_requirement_rows"]) == 24
    assert result["certified"]
    assert len(result["gates"]) == 9
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 8
    assert all(result["checks"].values())


def test_selection_and_global_protocol_boundaries_are_explicit() -> None:
    theorem = (HERE / "BLOCK_SELECTION_COMPOSITION_THEOREM_v1_9.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v1_9.md").read_text(encoding="utf-8")
    assert "Compositional firewall" in theorem
    assert "globally" in theorem and "optimized adaptive protocol" in theorem
    assert "Harness-based stopping boundary" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
