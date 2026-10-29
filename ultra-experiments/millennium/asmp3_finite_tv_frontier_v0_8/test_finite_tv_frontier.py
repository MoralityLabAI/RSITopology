from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from finite_tv_frontier import (
    audit_gap_certificate,
    bsc_law,
    build_result,
    exact_primal_vertex_optimum,
    explicit_case_rows,
    parity_certificate_row,
    parity_laws,
)
from verify_finite_tv_frontier import verify


HERE = Path(__file__).resolve().parent


def test_bsc_laws_are_exact_probabilities() -> None:
    for depth in range(1, 7):
        for word in range(1 << depth):
            law = bsc_law(word, depth, Fraction(1, 5))
            assert sum(law, Fraction(0)) == 1
            assert all(value >= 0 for value in law)


def test_parity_laws_partition_every_world() -> None:
    for depth in range(1, 7):
        honest, false = parity_laws(depth, Fraction(1, 5))
        assert len(honest) == len(false) == 1 << (depth - 1)
        assert all(sum(law, Fraction(0)) == 1 for law in (*honest, *false))


def test_explicit_certificates_are_matching_primal_dual_bounds() -> None:
    rows = explicit_case_rows()
    assert len(rows) == 3
    assert all(row["certificate_audit"]["exact"] for row in rows)
    assert all(row["vertex_solver_matches"] for row in rows)


def test_small_vertex_solver_recovers_single_bit_gap() -> None:
    acceptance, gap = exact_primal_vertex_optimum(
        ((Fraction(4, 5), Fraction(1, 5)),),
        ((Fraction(1, 5), Fraction(4, 5)),),
    )
    assert gap == Fraction(3, 5)
    assert all(Fraction(0) <= value <= Fraction(1) for value in acceptance)


def test_invalid_certificate_is_rejected() -> None:
    with pytest.raises(ValueError, match="do not sum to one"):
        audit_gap_certificate(
            ((Fraction(1), Fraction(0)),),
            ((Fraction(0), Fraction(1)),),
            (Fraction(1), Fraction(0)),
            Fraction(1),
            (Fraction(1, 2),),
            (Fraction(1), Fraction(0)),
        )


def test_parity_certificates_match_three_fifths_power() -> None:
    for depth in range(1, 9):
        row = parity_certificate_row(depth)
        assert row["closed_form_gap"] == str(Fraction(3, 5) ** depth)
        assert row["all_pair_gaps"] == [row["closed_form_gap"]]
        assert row["mixture_formula_matches"]
        assert row["certificate_exact"]


def test_convex_hull_collision_and_joint_signal_are_both_present() -> None:
    by_id = {row["case_id"]: row for row in explicit_case_rows()}
    assert by_id["convex_hull_collision"]["claimed_gap"] == "0"
    assert by_id["joint_correlation_signal"]["claimed_gap"] == "1"


def test_alias_refinement_preserves_the_gap() -> None:
    result = build_result()
    assert [
        row["alias_count_per_semantic_outcome"]
        for row in result["alias_refinement_rows"]
    ] == list(range(1, 9))
    assert all(
        row["certificate_exact"] and row["gap"] == "3/5"
        for row in result["alias_refinement_rows"]
    )


def test_all_producer_gates_pass() -> None:
    result = build_result()
    assert result["certified"]
    assert len(result["gates"]) == 8
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 9
    assert all(result["checks"].values())


def test_theorem_and_completion_boundary_are_explicit() -> None:
    theorem = (HERE / "FINITE_TV_FRONTIER_THEOREM_v0_8.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v0_8.md").read_text(encoding="utf-8")
    normalized_theorem = " ".join(theorem.split())
    assert "gamma*(H,F)" in theorem
    assert "min_(p in conv(H), q in conv(F)) TV(p,q)" in theorem
    assert "No novelty claim" in normalized_theorem
    assert "WV-ADM characterization" in audit
    assert "open" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
