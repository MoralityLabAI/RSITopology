from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from randomized_finder_amplification import (
    build_result,
    exhaustive_restart_rows,
    finder_failure,
    joint_noise_risk,
    minimal_attempts,
    minimal_odd_depth,
    protocol_row,
    scaling_rows,
    unique_marker_retry_rows,
)
from verify_randomized_finder_amplification import verify


Q = Fraction
HERE = Path(__file__).resolve().parent


def test_invalid_parameters_are_rejected() -> None:
    with pytest.raises(ValueError):
        finder_failure(Q(0), 1)
    with pytest.raises(ValueError):
        minimal_attempts(Q(1, 2), Q(1))
    with pytest.raises(ValueError):
        minimal_odd_depth(0, Q(1, 5), Q(1, 10))
    with pytest.raises(ValueError):
        protocol_row(Q(1, 2), Q(1, 10), 0, Q(1, 5), Q(1, 10))


def test_independent_finder_failure_is_exact_power() -> None:
    for alpha in (Q(1, 4), Q(1, 2), Q(2, 3)):
        for attempts in (1, 2, 5):
            assert finder_failure(alpha, attempts) == (1 - alpha) ** attempts


def test_attempt_count_is_exactly_minimal() -> None:
    for alpha, target in ((Q(1, 4), Q(1, 100)), (Q(1, 2), Q(1, 10)), (Q(1, 20), Q(1, 20))):
        attempts = minimal_attempts(alpha, target)
        assert finder_failure(alpha, attempts) <= target
        if attempts > 1:
            assert finder_failure(alpha, attempts - 1) > target


def test_exhaustive_restart_spaces_match_closed_form() -> None:
    rows = exhaustive_restart_rows()
    assert len(rows) == 18
    assert sum(row["boolean_outcome_patterns"] for row in rows) == 378
    assert all(row["certified"] for row in rows)


def test_noise_depth_is_exactly_minimal() -> None:
    depth = minimal_odd_depth(16, Q(2, 5), Q(1, 100))
    assert joint_noise_risk(16, depth, Q(2, 5)) <= Q(1, 100)
    assert joint_noise_risk(16, depth - 2, Q(2, 5)) > Q(1, 100)


def test_completeness_soundness_and_gap_formula() -> None:
    row = protocol_row(Q(1, 2), Q(1, 10), 4, Q(1, 5), Q(1, 10))
    failure = Q(row["exact_amplified_finder_failure"])
    risk = Q(row["joint_decoding_error"])
    assert Q(row["completeness_lower_bound"]) == 1 - risk
    assert Q(row["soundness_upper_bound"]) == failure + (1 - failure) * risk
    assert Q(row["gap_lower_bound"]) == 1 - failure - 2 * risk + failure * risk


def test_decoupled_targets_imply_symbolic_gap() -> None:
    for target in (Q(1, 10), Q(1, 100)):
        row = protocol_row(Q(1, 4), target, 16, Q(1, 3), target)
        assert Q(row["gap_lower_bound"]) >= 1 - 3 * target + target**2


def test_all_retry_and_protocol_resources_are_charged() -> None:
    row = protocol_row(
        Q(1, 4), Q(1, 100), 16, Q(1, 5), Q(1, 100), atom_id_bits=32
    )
    assert row["total_honest_finder_time"] == row["finder_attempts"] * 16 * 32
    assert row["semantic_query_count"] == 16 * row["replications_per_atom"]
    assert row["critic_message_bits"] == row["critic_message_length_prefix_bits"] + 16 * 33


def test_inverse_log_scaling_and_held_out_confirmation() -> None:
    registered, confirmation = scaling_rows()
    assert len(registered) == 6
    assert len(confirmation) == 3
    assert all(row["certified"] for row in (*registered, *confirmation))
    assert [row["log2_prover_budget"] for row in confirmation] == [80, 90, 100]


def test_unique_marker_retry_still_pays_linear_total_search() -> None:
    rows = unique_marker_retry_rows()
    assert len(rows) == 6
    assert all(row["certified"] for row in rows)
    assert all(row["total_honest_search_queries"] >= row["linear_query_floor"] for row in rows)
    assert all(row["exceeds_registered_one_trial_budget"] for row in rows)


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["protocol_rows"]) == 72
    assert len(result["gates"]) == 11
    assert result["certified"]
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 9
    assert all(result["checks"].values())


def test_claim_and_normal_form_boundaries_are_explicit() -> None:
    theorem = (HERE / "RANDOMIZED_FINDER_AMPLIFICATION_THEOREM_v2_4.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v2_4.md").read_text(encoding="utf-8")
    assert "Las Vegas-with-FAIL" in theorem
    assert "does not derive" in theorem
    assert "normal-form converse" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
