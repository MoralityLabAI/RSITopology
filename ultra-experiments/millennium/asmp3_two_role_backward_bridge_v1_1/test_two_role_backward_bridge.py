from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from two_role_backward_bridge import (
    ZeroSumDAG,
    alternating_game,
    backward_induction,
    build_result,
    challenge_family_game,
    enumerate_strategies,
    evaluate_strategies,
    family_row,
    matching_boundary_row,
    revealed_matching_game,
    saddle_audit,
)
from verify_two_role_backward_bridge import verify


HERE = Path(__file__).resolve().parent


def test_family_games_are_valid_and_have_value_three_fifths() -> None:
    for count in range(1, 13):
        game = challenge_family_game(count)
        game.validate()
        assert backward_induction(game)["value"] == Fraction(3, 5)


def test_cycle_is_rejected() -> None:
    game = ZeroSumDAG(
        states=("a", "b"),
        terminals=("z",),
        owner={"a": "max", "b": "min"},
        actions={"a": ("go",), "b": ("back",)},
        transitions={
            ("a", "go"): {"b": Fraction(1)},
            ("b", "back"): {"a": Fraction(1)},
        },
        terminal_payoff={"z": Fraction(0)},
        initial={"a": Fraction(1)},
    )
    with pytest.raises(ValueError, match="not acyclic"):
        game.validate()


def test_backward_pair_evaluates_to_value() -> None:
    game = alternating_game()
    result = backward_induction(game)
    assert evaluate_strategies(
        game, result["max_strategy"], result["min_strategy"]
    ) == result["value"] == Fraction(7, 10)


def test_exhaustive_saddle_deviations_hold() -> None:
    for count in range(1, 9):
        audit = saddle_audit(challenge_family_game(count), exhaustive=True)
        assert audit["max_guarantee_holds"]
        assert audit["min_cap_holds"]
        assert audit["certified"]


def test_strategy_counts_are_exponential_for_challenger() -> None:
    for count in range(1, 9):
        game = challenge_family_game(count)
        assert len(enumerate_strategies(game, "max")) == count
        assert len(enumerate_strategies(game, "min")) == 1 << count


def test_family_rows_use_linear_backward_work() -> None:
    for count in range(1, 13):
        row = family_row(count)
        assert row["min_pure_strategy_count"] == 1 << count
        assert row["backward_action_evaluations"] == 3 * count
        assert row["exact_value"] == "3/5"
        assert row["certified"]


def test_alternating_game_full_saddle() -> None:
    audit = saddle_audit(alternating_game(), exhaustive=True)
    assert audit["backward_value"] == "7/10"
    assert audit["max_strategy_count"] == 32
    assert audit["min_strategy_count"] == 4
    assert audit["certified"]


def test_revealed_matching_has_value_negative_one() -> None:
    audit = saddle_audit(revealed_matching_game(), exhaustive=True)
    assert audit["backward_value"] == "-1"
    assert audit["certified"]


def test_hidden_matching_mixed_value_differs() -> None:
    row = matching_boundary_row()
    assert row["revealed_sequential_value"] == "-1"
    assert row["simultaneous_pure_maximin"] == "-1"
    assert row["simultaneous_mixed_value"] == "0"
    assert row["information_structure_changes_strategy_class"]


def test_all_producer_gates_pass() -> None:
    result = build_result()
    assert result["certified"]
    assert len(result["gates"]) == 6
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 7
    assert all(result["checks"].values())


def test_information_boundary_is_explicit() -> None:
    theorem = (HERE / "TWO_ROLE_BACKWARD_THEOREM_v1_1.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v1_1.md").read_text(encoding="utf-8")
    assert "perfect-information saddle" in theorem
    assert "Hidden simultaneous play" in theorem
    assert "perfect-recall sequence-form bridge = open" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
