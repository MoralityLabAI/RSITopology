from __future__ import annotations

import json
from fractions import Fraction

from interactive_covering_frontier import (
    ARTIFACT_PATH,
    adaptive_tree_audit,
    bit_frontier_rows,
    build_artifact,
    compressed_codebook_audit,
    frontier_row,
    parent_audit,
    rotation_attainment_audit,
    round_schedule_audit,
)
from verify_interactive_covering_frontier import verify


def test_exact_interactive_value() -> None:
    for n in range(2, 33):
        for k in range(1, 9):
            for q in range(1, 9):
                row = frontier_row(n, k, q)
                assert Fraction(row["exact_public_coin_worst_marker_completeness"]) == min(Fraction(1), Fraction(k * q, n))


def test_perfect_completeness_iff_covering_capacity() -> None:
    for n in range(2, 33):
        for k in range(1, 9):
            for q in range(1, 9):
                row = frontier_row(n, k, q)
                assert row["perfect_completeness"] == (k * q >= n)
                assert row["perfect_completeness_iff_Kq_at_least_N"]


def test_adaptive_trees_compress_to_zero_answer_paths() -> None:
    audit = adaptive_tree_audit()
    assert audit["adaptive_trees_enumerated"] == 97062
    assert audit["marker_runs"] == 464010
    assert audit["zero_path_compression_violations"] == 0
    assert audit["certified"]


def test_small_compressed_codebooks_attain_capacity() -> None:
    rows = compressed_codebook_audit()
    assert len(rows) == 49
    assert all(row["maximum_union_found"] == min(row["semantic_atom_count"], row["complete_prover_transcript_count"] * row["query_budget"]) for row in rows)


def test_cyclic_public_coins_attain_maximin_value() -> None:
    rows = rotation_attainment_audit()
    assert len(rows) == 738
    assert all(row["exact_maximin_attainment"] for row in rows)
    assert all(row["transcript_budget_respected"] and row["query_budget_respected"] for row in rows)


def test_round_splitting_never_increases_transcript_capacity() -> None:
    rows = round_schedule_audit()
    assert len(rows) == 78
    assert all(not row["round_partition_changes_capacity"] for row in rows)
    assert all(row["minimum_complete_transcripts"] == 2 ** row["total_prover_bits"] for row in rows)


def test_power_of_two_bit_query_frontier_is_additive() -> None:
    rows = bit_frontier_rows()
    assert len(rows) == 3310
    assert all(row["perfect_completeness"] == (row["bit_query_exponent"] >= row["index_bits"]) for row in rows)


def test_parent_find_cost_is_preserved() -> None:
    parent = parent_audit()
    assert parent["certified"]
    assert parent["deterministic_honest_search"] == "N"
    assert parent["resource_parent_lower_bound"] == "K*q>=N message-query covering inequality"


def test_all_interface_flags_are_explicit() -> None:
    row = frontier_row(17, 3, 4)
    assert row["arbitrary_round_interaction_allowed"]
    assert row["adaptive_semantic_queries_allowed"]
    assert row["public_coins_allowed"]
    assert row["pointwise_perfect_zero_world_soundness"]


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
