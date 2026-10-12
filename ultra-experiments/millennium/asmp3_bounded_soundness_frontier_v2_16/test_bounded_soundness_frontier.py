from __future__ import annotations

import json
from fractions import Fraction

from bounded_soundness_frontier import (
    ARTIFACT_PATH,
    SOUNDNESS_VALUES,
    bounded_row,
    build_artifact,
    finite_seed_balancing_rows,
    finite_seed_exhaustive_audit,
    gap_target_rows,
    parent_audit,
)
from verify_bounded_soundness_frontier import verify


def test_zero_soundness_recovers_interactive_covering_value() -> None:
    for n in range(2, 33):
        for k in range(1, 6):
            for q in range(1, 6):
                row = bounded_row(n, k, q, Fraction(0))
                assert Fraction(row["exact_bounded_soundness_completeness"]) == min(Fraction(1), Fraction(k * q, n))


def test_exact_bounded_soundness_formula() -> None:
    for n in range(2, 17):
        for soundness in SOUNDNESS_VALUES:
            row = bounded_row(n, 3, 2, soundness)
            expected = soundness + (1 - soundness) * min(Fraction(1), Fraction(6, n))
            assert Fraction(row["exact_bounded_soundness_completeness"]) == expected


def test_exact_gap_formula() -> None:
    for soundness in SOUNDNESS_VALUES:
        row = bounded_row(17, 2, 3, soundness)
        assert Fraction(row["exact_completeness_soundness_gap"]) == (1 - soundness) * Fraction(6, 17)


def test_rational_public_seed_mixture_attains_every_sample() -> None:
    for soundness in SOUNDNESS_VALUES:
        row = bounded_row(19, 3, 4, soundness)
        assert row["exact_bounded_soundness_completeness"] == row["rational_attainment_probability"]


def test_finite_seed_cyclic_balancing_is_optimal() -> None:
    rows = finite_seed_balancing_rows()
    assert len(rows) == 12150
    assert all(row["certified"] for row in rows)


def test_small_seed_families_are_exhaustively_optimal() -> None:
    audit = finite_seed_exhaustive_audit()
    assert audit["families_enumerated"] == 25523
    assert audit["optimality_violations"] == 0
    assert audit["certified"]


def test_target_gap_transcript_thresholds_are_minimal() -> None:
    rows = gap_target_rows()
    assert len(rows) == 3103
    assert all(row["target_attained"] for row in rows)
    assert all(row["one_fewer_transcript_insufficient"] for row in rows)


def test_perfect_completeness_condition_is_unchanged_for_s_below_one() -> None:
    for soundness in SOUNDNESS_VALUES:
        assert bounded_row(17, 4, 4, soundness)["perfect_completeness"] is False
        assert bounded_row(17, 5, 4, soundness)["perfect_completeness"] is True


def test_parent_contracts_match() -> None:
    parent = parent_audit()
    assert parent["certified"]
    assert parent["interactive_parent_exact_value"] == "min(1,K*q/N)"


def test_all_producer_gates_pass() -> None:
    artifact = build_artifact()
    assert artifact["certified"]
    assert len(artifact["gates"]) == 10
    assert all(artifact["gates"].values())


def test_written_artifact_and_clean_room_verifier_match() -> None:
    assert json.loads(ARTIFACT_PATH.read_text(encoding="utf-8")) == build_artifact()
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 10
