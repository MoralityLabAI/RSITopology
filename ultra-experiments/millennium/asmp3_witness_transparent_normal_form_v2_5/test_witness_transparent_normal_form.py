from __future__ import annotations

from fractions import Fraction
from math import comb
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from verify_witness_transparent_normal_form import verify
from witness_transparent_normal_form import (
    build_result,
    coupling_rows,
    coupling_summary,
    extraction_row,
    finite_nonbinding_audit,
    minimal_attempts,
    nonbinding_refute_rows,
    tightness_rows,
)


Q = Fraction
HERE = Path(__file__).resolve().parent


def test_invalid_extraction_parameters_are_rejected() -> None:
    with pytest.raises(ValueError):
        minimal_attempts(Q(0), Q(1, 10))
    with pytest.raises(ValueError):
        extraction_row(Q(4, 5), Q(1, 10), 1)
    with pytest.raises(ValueError):
        extraction_row(Q(1, 5), Q(4, 5), 1)
    with pytest.raises(ValueError):
        coupling_summary(0)


def test_coupled_decision_extraction_formula() -> None:
    row = extraction_row(Q(1, 5), Q(1, 20), 16)
    assert Q(row["extracted_one_shot_finder_success"]) == Q(3, 4)
    assert Q(row["noisy_rejection_probability_lower_bound"]) == Q(4, 5)
    assert row["extracted_quotient_dimension_bound"] == 16
    assert row["finder_success_dominates_gap_margin"]


def test_extraction_restart_count_is_minimal() -> None:
    row = extraction_row(Q(2, 5), Q(1, 10), 4)
    alpha = Q(row["extracted_one_shot_finder_success"])
    attempts = row["restart_attempts"]
    target = Q(row["target_finder_failure"])
    assert (1 - alpha) ** attempts <= target
    if attempts > 1:
        assert (1 - alpha) ** (attempts - 1) > target


def test_extraction_resource_ledger_is_complete() -> None:
    row = extraction_row(Q(1, 3), Q(1, 20), 64)
    assert row["one_shot_extraction_time"] == 10 * 64
    assert row["total_amplified_finder_time"] == row["restart_attempts"] * 640
    assert row["within_honest_prover_budget"]


def test_all_registered_binary_couplings_satisfy_bound() -> None:
    registered, held_out = coupling_rows()
    assert len(registered) == 16
    assert len(held_out) == 4
    assert sum(row["joint_binary_coupling_tables"] for row in (*registered, *held_out)) == comb(24, 4) - 1
    assert all(row["certified"] for row in (*registered, *held_out))


def test_held_out_coupling_digests_are_distinct() -> None:
    _, rows = coupling_rows()
    assert len({row["canonical_table_digest_sha256"] for row in rows}) == 4


def test_extraction_bound_is_sharp() -> None:
    rows = tightness_rows()
    assert len(rows) == 9
    assert all(row["bound_attained"] for row in rows)
    assert all(row["certified"] for row in rows)


def test_nonbinding_refute_changes_dimension_not_protocol() -> None:
    finite = finite_nonbinding_audit()
    assert len(finite) == 7
    assert sum(row["refute_subset_evaluations"] for row in finite) > 500_000
    assert all(row["certified"] for row in finite)
    assert all(row["transparent_false_claim_minimum_sizes"] == [1] for row in finite)
    assert all(
        row["padded_false_claim_minimum_sizes"] == [row["semantic_classes"]]
        for row in finite
    )
    assert all(row["protocol_consults_refute"] is False for row in finite)
    rows = nonbinding_refute_rows()
    assert len(rows) == 6
    for row in rows:
        assert row["protocol_value_unchanged_across_variants"]
        assert row["singleton_transparent_refute_dimension"] == 1
        assert row["padded_sound_complete_refute_dimension"] == row["prover_work"]
        assert row["empty_decidable_refute_dimension"] == "infinity"
        assert row["padded_dimension_exceeds_quartic_polylog"]
        assert row["literal_only_if_direction_fails"]


def test_parent_composition_produces_positive_canonical_gap() -> None:
    for soundness in (Q(1, 5), Q(2, 5)):
        row = extraction_row(soundness, Q(1, 10), 16)
        assert Q(row["canonical_protocol_gap_after_v2_4"]) > Q(9, 10)


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["extraction_rows"]) == 36
    assert len(result["gates"]) == 11
    assert result["certified"]
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 9
    assert all(result["checks"].values())


def test_claim_boundaries_are_explicit() -> None:
    theorem = (HERE / "WITNESS_TRANSPARENT_NORMAL_FORM_THEOREM_v2_5.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v2_5.md").read_text(encoding="utf-8")
    assert "Literal v0.1 two-sided separation" in theorem
    assert "does not cover" in theorem
    assert "unrestricted WV-FIX" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
