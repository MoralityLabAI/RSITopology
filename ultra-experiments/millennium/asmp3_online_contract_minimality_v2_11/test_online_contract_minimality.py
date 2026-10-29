from __future__ import annotations

import json
from fractions import Fraction

from online_contract_minimality import (
    ARTIFACT_PATH,
    build_artifact,
    ideal_probe_frontier_rows,
    observation_partition_rows,
    path_error_audit,
    premise_necessity_rows,
    sharp_path_error_rows,
    trace_without_H_rows,
)
from verify_online_contract_minimality import verify


def test_decision_only_has_no_common_safe_witness() -> None:
    rows = observation_partition_rows()
    assert len(rows) == 19
    assert all(row["decision_only_common_valid_witnesses"] == 0 for row in rows)
    assert all(row["decision_only_las_vegas_success"] == "0" for row in rows)


def test_candidate_trace_without_H_remains_ambiguous() -> None:
    rows = observation_partition_rows()
    assert all(row["trace_only_safe_candidate_observations"] == 0 for row in rows)
    assert all(
        row["trace_only_ambiguous_observations"] == row["marker_count"]
        for row in rows
    )


def test_candidate_trace_plus_H_has_exact_safe_partition() -> None:
    for row in observation_partition_rows():
        assert row["trace_plus_H_safe_positive_observations"] == row["marker_count"]
        assert row["trace_plus_H_fail_closed_observations"] == row["marker_count"]


def test_probe_frontier_is_exactly_k_over_N() -> None:
    rows = ideal_probe_frontier_rows()
    assert len(rows) == 73
    for row in rows:
        assert Fraction(row["exact_las_vegas_success"]) == Fraction(
            int(row["ideal_probe_budget"]), int(row["marker_count"])
        )
        assert row["minimum_world_hit_schedules"] == row[
            "maximum_world_hit_schedules"
        ]
        assert row["certified"]


def test_positive_decoy_mass_forces_trace_only_fail_closed() -> None:
    rows = trace_without_H_rows()
    assert len(rows) == 76
    assert all(row["trace_only_las_vegas_success"] == "0" for row in rows)
    assert all(Fraction(row["positive_decoy_probability"]) > 0 for row in rows)


def test_trusting_log_has_exact_invalid_mass_but_H_removes_it() -> None:
    for row in trace_without_H_rows():
        error = Fraction(row["positive_decoy_probability"])
        assert Fraction(row["trust_logged_candidate_invalid_probability"]) == error
        assert Fraction(row["trace_plus_H_success"]) == 1 - error
        assert row["trace_plus_H_invalid_probability"] == "0"


def test_path_error_lower_bound_is_attained_everywhere() -> None:
    rows = sharp_path_error_rows()
    audit = path_error_audit(rows)
    assert len(rows) == 270
    assert audit["certified"]
    assert audit["all_bounds_attained"]
    assert audit["soundness_zero_path_error_one_success"] == "0"


def test_each_premise_has_a_registered_counterfamily() -> None:
    rows = premise_necessity_rows()
    assert len(rows) == 6
    assert all(row["certified"] for row in rows)
    assert len({row["removed_premise"] for row in rows}) == 6


def test_parent_compositions_survive_minimality_audit() -> None:
    artifact = build_artifact()
    assert artifact["certified"]
    assert len(artifact["composition_rows"]) == 12
    assert all(len(row["necessary_online_contract"]) == 6 for row in artifact["composition_rows"])


def test_written_artifact_and_clean_room_checker_match() -> None:
    written = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert written == build_artifact()
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 10
