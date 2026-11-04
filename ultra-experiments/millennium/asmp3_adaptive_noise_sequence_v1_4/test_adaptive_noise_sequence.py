from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from adaptive_noise_sequence import (
    build_result,
    budget_noise_game,
    case_row,
    common_transcript,
    response_languages,
)
from build_release_manifest import verify_manifest
from verify_adaptive_noise_sequence import verify


HERE = Path(__file__).resolve().parent


def test_invalid_depth_budget_is_rejected() -> None:
    with pytest.raises(ValueError, match="invalid depth/budget"):
        budget_noise_game(3, 4)
    with pytest.raises(ValueError, match="invalid depth/budget"):
        budget_noise_game(0, 0)


def test_response_languages_have_expected_phase() -> None:
    for depth in range(1, 7):
        for budget in range(depth + 1):
            zero, one = response_languages(depth, budget)
            assert bool(zero & one) == (2 * budget >= depth)


def test_common_transcript_exists_exactly_in_overlap_phase() -> None:
    for depth in range(1, 7):
        for budget in range(depth + 1):
            if 2 * budget < depth:
                with pytest.raises(ValueError, match="do not overlap"):
                    common_transcript(depth, budget)
            else:
                target = common_transcript(depth, budget)
                zero, one = response_languages(depth, budget)
                assert target in zero & one


def test_separable_cases_have_value_one() -> None:
    for depth in range(1, 7):
        for budget in range(depth + 1):
            if 2 * budget < depth:
                row = case_row(depth, budget)
                assert row["phase"] == "separable"
                assert row["value"] == "1"
                assert row["majority_correct_on_both_languages"]
                assert row["audit"]["exact"]


def test_overlap_cases_have_value_zero() -> None:
    for depth in range(1, 7):
        for budget in range(depth + 1):
            if 2 * budget >= depth:
                row = case_row(depth, budget)
                assert row["phase"] == "overlap"
                assert row["value"] == "0"
                assert row["common_transcript_valid"]
                assert row["audit"]["exact"]


def test_every_case_has_matching_sequence_bounds() -> None:
    result = build_result()
    for row in result["case_rows"]:
        audit = row["audit"]
        value = Fraction(row["value"])
        assert Fraction(audit["lower_value"]) == value
        assert Fraction(audit["upper_value"]) == value
        assert Fraction(audit["mixed_pair_value"]) == value
        assert audit["exact"]


def test_registry_is_complete() -> None:
    result = build_result()
    expected = [
        (depth, budget)
        for depth in range(1, 7)
        for budget in range(depth + 1)
    ]
    assert [(row["depth"], row["flip_budget"]) for row in result["case_rows"]] == expected


def test_all_producer_gates_pass() -> None:
    result = build_result()
    assert result["certified"]
    assert len(result["gates"]) == 7
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 7
    assert all(result["checks"].values())


def test_joint_noise_scope_is_explicit() -> None:
    theorem = (HERE / "ADAPTIVE_NOISE_THEOREM_v1_4.md").read_text(encoding="utf-8")
    audit = (HERE / "COMPLETION_AUDIT_v1_4.md").read_text(encoding="utf-8")
    assert "joint budget boundary" in theorem
    assert "marginal profile is insufficient" in theorem
    assert "compact finite-state noise-controller formulation = open" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
