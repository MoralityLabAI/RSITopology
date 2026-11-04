from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from matrix_game_bridge import (
    MatrixGame,
    alias_row,
    audit_saddle_certificate,
    build_result,
    duplicate_actions,
    explicit_rows,
    identity_game,
    identity_row,
)
from verify_matrix_game_bridge import verify


HERE = Path(__file__).resolve().parent


def test_ragged_matrix_is_rejected() -> None:
    game = MatrixGame(((Fraction(1),), (Fraction(0), Fraction(1))))
    with pytest.raises(ValueError, match="ragged"):
        game.validate()


def test_invalid_distribution_is_rejected() -> None:
    game = identity_game(2)
    with pytest.raises(ValueError, match="does not sum to one"):
        audit_saddle_certificate(
            game,
            (Fraction(1, 3), Fraction(1, 3)),
            (Fraction(1, 2), Fraction(1, 2)),
            Fraction(1, 2),
        )


def test_explicit_saddles_are_exact() -> None:
    rows = explicit_rows()
    assert len(rows) == 3
    assert all(row["certificate"]["exact"] for row in rows)
    assert all(row["certified"] for row in rows)


def test_matching_pennies_mixed_value_differs_from_pure() -> None:
    row = {row["case_id"]: row for row in explicit_rows()}["matching_pennies"]
    assert row["pure_maximin"] == "-1"
    assert row["certificate"]["claimed_value"] == "0"


def test_biased_oversight_uses_nonuniform_max_mix() -> None:
    row = {row["case_id"]: row for row in explicit_rows()}["biased_oversight"]
    assert row["certificate"]["max_mix"] == ["1/4", "3/4"]
    assert row["certificate"]["min_mix"] == ["1/2", "1/2"]
    assert row["certificate"]["claimed_value"] == "1/2"


def test_identity_values_are_one_over_size() -> None:
    for size in range(1, 13):
        row = identity_row(size)
        assert row["mixed_value"] == str(Fraction(1, size))
        assert row["certificate"]["exact"]


def test_identity_pure_maximin_collapses_after_size_one() -> None:
    assert identity_row(1)["pure_maximin"] == "1"
    assert all(identity_row(size)["pure_maximin"] == "0" for size in range(2, 13))


def test_action_duplication_preserves_matrix_blocks() -> None:
    base = MatrixGame(((Fraction(1), Fraction(2)), (Fraction(3), Fraction(4))))
    expanded = duplicate_actions(base, 2, 3)
    assert expanded.row_count == 4
    assert expanded.column_count == 6
    assert expanded.payoff[0] == (Fraction(1),) * 3 + (Fraction(2),) * 3
    assert expanded.payoff[2] == (Fraction(3),) * 3 + (Fraction(4),) * 3


def test_alias_certificates_preserve_value() -> None:
    for copies in range(1, 7):
        row = alias_row(copies)
        assert row["value"] == "1/2"
        assert row["certificate"]["exact"]
        assert row["certified"]


def test_all_producer_gates_pass() -> None:
    result = build_result()
    assert result["certified"]
    assert len(result["gates"]) == 6
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 8
    assert all(result["checks"].values())


def test_normal_form_boundary_is_explicit() -> None:
    theorem = (HERE / "MATRIX_GAME_THEOREM_v1_2.md").read_text(encoding="utf-8")
    audit = (HERE / "COMPLETION_AUDIT_v1_2.md").read_text(encoding="utf-8")
    assert "finite simultaneous saddle" in theorem
    assert "Normal-form representation boundary" in theorem
    assert "perfect-recall sequence-form construction = open" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
