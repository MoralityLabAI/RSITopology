from __future__ import annotations

from fractions import Fraction

import pytest

from adaptive_transcript_coupling import (
    adaptive_path_risk,
    build_result,
    coupling_row,
    error_pattern_rows,
    exhaustive_adaptive_tree_audit,
    extraction_rows,
    majority_error,
    minimal_odd_depth,
    tightness_rows,
)
from build_release_manifest import verify_manifest
from verify_adaptive_transcript_coupling import verify


Q = Fraction


def test_invalid_parameters_are_rejected() -> None:
    with pytest.raises(ValueError):
        majority_error(0, Q(1, 5))
    with pytest.raises(ValueError):
        adaptive_path_risk(0, 3, Q(1, 5))
    with pytest.raises(ValueError):
        minimal_odd_depth(1, Q(1, 5), Q(1, 2))


def test_adaptive_path_risk_is_product_complement() -> None:
    for q in (1, 4, 16):
        error = majority_error(5, Q(1, 5))
        assert adaptive_path_risk(q, 5, Q(1, 5)) == 1 - (1 - error) ** q


def test_replication_depth_is_exactly_minimal() -> None:
    depth = minimal_odd_depth(64, Q(2, 5), Q(1, 100))
    assert adaptive_path_risk(64, depth, Q(2, 5)) <= Q(1, 100)
    assert adaptive_path_risk(64, depth - 2, Q(2, 5)) > Q(1, 100)


def test_ideal_to_noisy_gap_loses_at_most_twice_coupling() -> None:
    row = coupling_row(16, Q(1, 3), Q(1, 100))
    delta = Q(row["adaptive_path_coupling_failure"])
    assert Q(row["noisy_completeness_lower_bound"]) == Q(4, 5) - delta
    assert Q(row["noisy_soundness_upper_bound"]) == Q(1, 5) + delta
    assert Q(row["noisy_gap_lower_bound"]) == Q(3, 5) - 2 * delta


def test_every_error_pattern_space_matches_closed_form() -> None:
    rows = error_pattern_rows()
    assert len(rows) == 30
    assert all(row["certified"] for row in rows)


def test_all_small_adaptive_query_and_stopping_trees_couple() -> None:
    audit = exhaustive_adaptive_tree_audit()
    assert audit["coupled_execution_cases"] == 524_288
    assert audit["identical_paths_on_every_no_error_case"] == audit["no_error_cases"]
    assert audit["divergence_without_any_error"] == 0
    assert audit["different_stopping_outcomes_after_errors"] > 0
    assert audit["certified"]


def test_path_coupling_bound_is_attainable() -> None:
    rows = tightness_rows()
    assert len(rows) == 36
    assert all(row["bound_attained"] for row in rows)
    assert all(row["certified"] for row in rows)


def test_v2_5_extraction_coupling_is_now_derived() -> None:
    rows = extraction_rows()
    assert len(rows) == 12
    assert all(row["positive_extraction_margin"] for row in rows)
    assert all("coupling is now derived" in row["remaining_contracts"] for row in rows)


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["coupling_rows"]) == 42
    assert len(result["gates"]) == 11
    assert result["certified"]
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 9
    assert all(result["checks"].values())


def test_release_manifest_matches() -> None:
    assert verify_manifest()
