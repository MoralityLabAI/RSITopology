from __future__ import annotations

import json
from fractions import Fraction

from online_noisy_trace_extractor import (
    ARTIFACT_PATH,
    BASE_CONTRACT,
    build_artifact,
    contract_rows,
    exhaustive_online_audit,
    probability_table_audit,
    revalidate_candidate_online,
    run_noisy_bound_runtime,
    stateful_one_shot_rows,
    validate_online_contract,
)
from verify_online_noisy_trace_extractor import verify


def test_all_correct_rejection_extracts_without_replay() -> None:
    queries, candidate, decision = run_noisy_bound_runtime((0,), 1, 1, 0, 0, 2)
    extracted, reason = revalidate_candidate_online(
        queries, candidate, decision, 1, 0
    )
    assert decision == "reject"
    assert extracted == (0, 1)
    assert reason == "certified"


def test_noisy_false_candidate_is_safely_failed() -> None:
    # The claim is false at class 1, while noise forges a mismatch at class 0.
    queries, candidate, decision = run_noisy_bound_runtime((0,), 1, 2, 0, 1, 2)
    extracted, reason = revalidate_candidate_online(
        queries, candidate, decision, 2, 0
    )
    assert decision == "reject"
    assert candidate == (0, 1)
    assert extracted is None
    assert reason == "ideal_revalidation_failed"


def test_accepting_path_returns_fail() -> None:
    queries, candidate, decision = run_noisy_bound_runtime((0,), 1, 0, 0, 0, 2)
    assert revalidate_candidate_online(queries, candidate, decision, 0, 0) == (
        None,
        "no_rejection",
    )


def test_exhaustive_audit_covers_over_one_million_noisy_runs() -> None:
    audit = exhaustive_online_audit()
    assert audit["certified"]
    assert audit["noisy_executions"] == 1_144_000
    assert audit["raw_semantic_queries"] == 3_423_680
    assert audit["invalid_outputs"] == 0
    assert audit["all_correct_rejection_misses"] == 0


def test_every_invalid_noisy_candidate_is_contained() -> None:
    audit = exhaustive_online_audit()
    assert audit["invalid_noisy_candidates"] == 499_952
    assert audit["invalid_candidates_safely_failed"] == 499_952


def test_probability_bound_is_exact_and_sharp() -> None:
    audit = probability_table_audit()
    assert audit["certified"]
    assert audit["joint_tables"] == 53_129
    assert audit["inequality_violations"] == 0
    assert audit["sharp_equality_tables"] == 1_770


def test_contract_accepts_one_shot_and_restartable_modes() -> None:
    assert validate_online_contract(BASE_CONTRACT) == (True, "certified")
    restartable = dict(BASE_CONTRACT)
    restartable["interaction_mode"] = "restartable_allowed"
    assert validate_online_contract(restartable) == (True, "certified")


def test_all_contract_mutants_fail_closed() -> None:
    rows = contract_rows()
    negative = [row for row in rows if not row["case"].startswith("positive_")]
    positive = [row for row in rows if row["case"].startswith("positive_")]
    assert len(negative) == 8
    assert all(not row["accepted"] for row in negative)
    assert len(positive) == 2
    assert all(row["accepted"] for row in positive)


def test_stateful_erased_strategy_rows_need_no_restart() -> None:
    rows = stateful_one_shot_rows()
    assert len(rows) == 18
    assert all(row["strategy_state_erased"] for row in rows)
    assert all(not row["runtime_restartable"] for row in rows)
    assert all(Fraction(row["online_extractor_success"]) > 0 for row in rows)
    assert all(row["certified"] for row in rows)


def test_all_compositions_preserve_positive_margin_without_replay() -> None:
    artifact = build_artifact()
    assert artifact["certified"]
    assert len(artifact["composition_rows"]) == 12
    assert all(not row["strategy_restart_required"] for row in artifact["composition_rows"])
    assert all(not row["ideal_execution_replay_required"] for row in artifact["composition_rows"])


def test_artifact_and_clean_room_checker_match() -> None:
    written = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert written == build_artifact()
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 10
