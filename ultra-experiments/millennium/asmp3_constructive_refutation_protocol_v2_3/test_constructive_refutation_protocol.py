from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from constructive_refutation_protocol import (
    atom_error,
    build_result,
    joint_decoding_risk,
    minimal_odd_depth,
    protocol_row,
    scaling_rows,
)
from verify_constructive_refutation_protocol import verify


Q = Fraction
HERE = Path(__file__).resolve().parent


def test_invalid_parameters_are_rejected() -> None:
    with pytest.raises(ValueError):
        atom_error(0, Q(1, 5))
    with pytest.raises(ValueError):
        joint_decoding_risk(0, 3, Q(1, 5))
    with pytest.raises(ValueError):
        minimal_odd_depth(1, Q(1, 5), Q(1, 2))
    with pytest.raises(ValueError):
        protocol_row(0, Q(1, 5), Q(1, 10))


def test_joint_risk_is_exact_independent_block_union() -> None:
    for size in (1, 2, 8):
        for depth in (1, 3, 9):
            error = atom_error(depth, Q(1, 5))
            assert joint_decoding_risk(size, depth, Q(1, 5)) == 1 - (1 - error) ** size


def test_replication_depth_is_minimal_on_odd_grid() -> None:
    for size, eta, target in ((1, Q(1, 5), Q(1, 100)), (16, Q(1, 3), Q(1, 10)), (64, Q(2, 5), Q(1, 100))):
        depth = minimal_odd_depth(size, eta, target)
        assert joint_decoding_risk(size, depth, eta) <= target
        if depth > 1:
            assert joint_decoding_risk(size, depth - 2, eta) > target


def test_completeness_soundness_and_gap_are_matching_bounds() -> None:
    for size in (1, 4, 16):
        row = protocol_row(size, Q(1, 5), Q(1, 10))
        risk = Q(row["joint_decoding_error"])
        assert Q(row["completeness_lower_bound"]) == 1 - risk
        assert Q(row["soundness_upper_bound"]) == risk
        assert Q(row["completeness_soundness_gap_lower_bound"]) == 1 - 2 * risk


def test_target_error_implies_target_gap() -> None:
    for target in (Q(1, 10), Q(1, 100)):
        row = protocol_row(32, Q(1, 3), target)
        assert Q(row["joint_decoding_error"]) <= target
        assert Q(row["completeness_soundness_gap_lower_bound"]) >= 1 - 2 * target


def test_all_protocol_resources_are_explicitly_charged() -> None:
    row = protocol_row(16, Q(1, 5), Q(1, 100), atom_id_bits=32)
    assert row["semantic_query_count"] == 16 * row["replications_per_atom"]
    assert row["critic_message_bits"] == row["critic_message_length_prefix_bits"] + 16 * 33
    assert row["registered_finder_time_bound"] == 16 * 32


def test_noise_is_fresh_after_selection() -> None:
    row = protocol_row(4, Q(1, 5), Q(1, 10))
    assert row["noise_contract"].startswith("fresh disjoint iid blocks")
    assert "after transcript and witness are fixed" in row["noise_contract"]


def test_polylog_scaling_lane_fits_cubic_budget() -> None:
    rows = scaling_rows()
    assert len(rows) == 10
    assert all(row["all_resources_within_cubic_polylog_budget"] for row in rows)
    assert all(Q(row["gap_lower_bound"]) >= 1 - Q(2, row["log2_prover_work"]) for row in rows)


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["protocol_rows"]) == 42
    assert len(result["polylog_scaling_rows"]) == 10
    assert result["certified"]
    assert len(result["gates"]) == 10
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 8
    assert all(result["checks"].values())


def test_conditional_and_converse_boundaries_are_explicit() -> None:
    theorem = (HERE / "CONSTRUCTIVE_REFUTATION_PROTOCOL_THEOREM_v2_3.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v2_3.md").read_text(encoding="utf-8")
    assert "Positive-class contracts" in theorem
    assert "does not prove" in theorem
    assert "converse characterization" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
