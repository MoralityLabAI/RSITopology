from __future__ import annotations

from fractions import Fraction

from build_release_manifest import verify_manifest
from trace_binding_extractor import (
    build_result,
    composition_rows,
    decision_only_firewall_rows,
    exhaustive_trace_audit,
    mutant_trace_audit,
    refute_vector_claim,
    validate_and_extract,
)
from verify_trace_binding_extractor import verify


Q = Fraction


def test_vector_refute_and_formal_empty_witness() -> None:
    assert refute_vector_claim(0, 2, (0,), (1,))
    assert not refute_vector_claim(1, 2, (0,), (1,))
    assert refute_vector_claim(0, 2, (), (), malformed=True)


def test_bound_reject_trace_extracts_last_successful_call() -> None:
    trace = [
        {"op": "query", "class": 0, "answer": 1},
        {"op": "refute", "classes": [0], "answers": [1], "result": True},
        {"op": "terminal", "decision": "reject"},
    ]
    checked = validate_and_extract(trace, world=1, claim=0, task_bits=2, semantic_classes=2)
    assert checked["valid"]
    assert checked["extracted_classes"] == [0]
    assert checked["extracted_answers"] == [1]


def test_unbound_rejection_is_invalid() -> None:
    checked = validate_and_extract(
        [{"op": "terminal", "decision": "reject"}],
        world=0,
        claim=0,
        task_bits=2,
        semantic_classes=2,
    )
    assert not checked["valid"]
    assert checked["invalid_reason"] == "unbound_rejection"


def test_exhaustive_trace_compiler_audit_passes() -> None:
    audit = exhaustive_trace_audit()
    assert audit["trace_programs_audited"] > 100_000
    assert audit["candidate_witness_subset_evaluations"] > 100_000
    assert audit["rejections_with_extracted_witness"] == audit["valid_reject_traces"]
    assert audit["query_dimension_violations"] == 0
    assert audit["certified"]


def test_all_trace_binding_mutants_are_rejected() -> None:
    rows = mutant_trace_audit()
    assert len(rows) == 10
    assert all(row["rejected_by_validator"] for row in rows)
    assert all(row["certified"] for row in rows)


def test_decision_only_firewall_retains_search_barrier() -> None:
    rows = decision_only_firewall_rows()
    assert len(rows) == 20
    assert all(row["observable_terminal_decisions"] == 1 for row in rows)
    assert all(Q(row["best_decision_only_worst_world_success"]) == Q(1, row["singleton_witness_worlds"]) for row in rows)
    assert all(row["decision_only_binding_is_insufficient"] for row in rows)


def test_v2_7_and_trace_binding_derive_positive_finder_margin() -> None:
    rows = composition_rows()
    assert len(rows) == 12
    assert all(Q(row["trace_bound_finder_success"]) > 0 for row in rows)
    assert all("transparency and coupling are derived" in row["remaining_contract"] for row in rows)


def test_all_extractor_resources_are_charged() -> None:
    for row in composition_rows():
        assert row["one_shot_extractor_time"] == (
            row["honest_critic_time"]
            + row["verifier_ideal_replay_time"]
            + row["ideal_semantic_evaluation_time"]
            + row["trace_scan_time"]
            + row["canonicalization_time"]
        )


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["gates"]) == 10
    assert result["certified"]
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 9
    assert all(result["checks"].values())


def test_release_manifest_matches() -> None:
    assert verify_manifest()
