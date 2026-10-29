from __future__ import annotations

import json
from fractions import Fraction

from oracle_parametric_replay import (
    ARTIFACT_PATH,
    BASE_CONTRACT,
    build_artifact,
    contract_mutant_rows,
    execute_oracle_runtime,
    exhaustive_replay_audit,
    ideal_answer,
    node_index,
    reference_ideal_execution,
    seed_marginal_audit,
    transcript_only_firewall_rows,
    validate_bound_ideal_trace,
    validate_composed_contract,
)
from verify_oracle_parametric_replay import verify


def test_binary_tree_node_indexing_is_canonical() -> None:
    assert node_index(()) == 0
    assert [node_index((bit,)) for bit in (0, 1)] == [1, 2]
    assert [node_index(bits) for bits in ((0, 0), (0, 1), (1, 0), (1, 1))] == [3, 4, 5, 6]


def test_dependency_injection_matches_direct_ideal_semantics() -> None:
    policy = (0, 1, 2, 2, 1, 0, 2)
    for world in range(8):
        for claim in range(8):
            compiled = execute_oracle_runtime(policy, 3, world, claim, 3, ideal_answer)
            reference = reference_ideal_execution(policy, 3, world, claim, 3)
            assert compiled == reference


def test_every_compiled_rejection_has_a_valid_query_bounded_witness() -> None:
    policy = (0, 1, 2, 2, 1, 0, 2)
    for world in range(8):
        for claim in range(8):
            trace = execute_oracle_runtime(policy, 3, world, claim, 3, ideal_answer)
            valid, dimension = validate_bound_ideal_trace(trace, world, claim, 3)
            assert valid
            assert dimension <= 1


def test_exhaustive_replay_audit_is_large_and_exact() -> None:
    audit = exhaustive_replay_audit()
    assert audit["certified"]
    assert audit["policy_programs"] == 2355
    assert audit["ideal_executions"] == 144096
    assert audit["compiler_mismatches"] == 0
    assert audit["invalid_bound_traces"] == 0


def test_fresh_seed_marginals_need_not_recover_noisy_seeds() -> None:
    audit = seed_marginal_audit()
    assert audit["certified"]
    assert audit["fresh_seed_marginal_cases"] == 29056
    assert audit["exact_marginal_equalities"] == 29056
    assert audit["marginal_mismatches"] == 0


def test_contract_validator_accepts_both_restartable_modes() -> None:
    assert validate_composed_contract(BASE_CONTRACT) == (True, "certified")
    live = dict(BASE_CONTRACT)
    live["runtime_access"] = "restartable_live_interaction"
    live["execution_accounting"] = "external_online_messages_charged"
    assert validate_composed_contract(live) == (True, "certified")


def test_every_single_contract_mutant_is_rejected() -> None:
    rows = contract_mutant_rows()
    negative = [row for row in rows if not row["mutant"].startswith("positive_")]
    positive = [row for row in rows if row["mutant"].startswith("positive_")]
    assert len(negative) == 8
    assert all(not row["accepted"] for row in negative)
    assert len(positive) == 2
    assert all(row["accepted"] for row in positive)


def test_transcript_only_firewall_has_exact_search_rates() -> None:
    rows = transcript_only_firewall_rows()
    assert len(rows) == 19
    for row in rows:
        n = int(row["marker_count"])
        k = int(row["additional_ideal_probe_budget"])
        assert Fraction(row["best_transcript_only_worst_world_success"]) == Fraction(1, n)
        assert Fraction(row["best_transcript_plus_probes_success"]) == Fraction(k, n)
        assert Fraction(row["oracle_parametric_replay_success"]) == 1


def test_all_composed_resources_and_success_gates_pass() -> None:
    artifact = build_artifact()
    assert artifact["certified"]
    assert len(artifact["composition_rows"]) == 12
    assert all(artifact["gates"].values())


def test_written_artifact_matches_fresh_build() -> None:
    assert ARTIFACT_PATH.is_file()
    written = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert written == build_artifact()


def test_clean_room_checker_passes() -> None:
    receipt = verify()
    assert receipt["passed"]
    assert receipt["check_count"] == 10
    assert all(receipt["checks"].values())
