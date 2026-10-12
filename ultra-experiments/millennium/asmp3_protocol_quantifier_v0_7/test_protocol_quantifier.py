from __future__ import annotations

from fractions import Fraction

from build_release_manifest import verify_manifest
from protocol_quantifier_harness import (
    DEPTHS,
    LAMBDA,
    bit_cost_row,
    build_result,
    canonical_nonoracle_transcript,
    claim_classification,
    cross_world_transcript_identity,
    exhaustive_binary_test_gap,
    exhaustive_terminal_refutation_audit,
    game_parameters,
    honest_strategy_terminal_coverage,
    parity_channel_row,
    rich_vector_protocol_audit,
    semantic_refutation_minimum,
    xor_cross_examination_local_lemma,
)
from verify_protocol_quantifier import verify


def test_game_parameters_cover_non_power_of_two_lengths() -> None:
    for public_length in range(4, 130):
        row = game_parameters(public_length)
        leaves = row["formal_leaf_count"]
        assert leaves <= public_length < 2 * leaves
        assert row["semantic_atom_count"] == row["depth"]
        assert row["prover_budget"] == public_length


def test_claim_partition_is_exhaustive() -> None:
    allowed = {
        "malformed",
        "fully_true",
        "true_output_both_components_false",
        "formal_false",
        "semantic_false",
    }
    for true_formal in (0, 1):
        for true_semantic in (0, 1):
            for claimed_formal in (0, 1):
                for claimed_semantic in (0, 1):
                    for claimed_output in (0, 1):
                        assert (
                            claim_classification(
                                true_formal,
                                true_semantic,
                                claimed_formal,
                                claimed_semantic,
                                claimed_output,
                            )
                            in allowed
                        )


def test_semantic_refutation_dimension_is_depth() -> None:
    for depth in range(2, 8):
        for value in range(1 << depth):
            bits = tuple((value >> index) & 1 for index in range(depth))
            assert semantic_refutation_minimum(bits) == depth
        audit = exhaustive_terminal_refutation_audit(depth)
        assert audit["dimension_equals_depth"]
        assert audit["all_false_cases_refutable"]


def test_uniform_honest_strategy_covers_all_realized_cases() -> None:
    assert xor_cross_examination_local_lemma()
    assert honest_strategy_terminal_coverage()


def test_nonoracle_transcript_is_cross_world_identical() -> None:
    for depth in DEPTHS:
        assert cross_world_transcript_identity(depth)
        for formal_root in (0, 1):
            transcript = canonical_nonoracle_transcript(depth, formal_root)
            assert "canonical_sorted_refuting_set" in str(transcript)


def test_frozen_gap_and_all_binary_tests() -> None:
    for depth in DEPTHS:
        row = parity_channel_row(depth)
        assert Fraction(row["frozen_encoding_gap"]) == LAMBDA**depth
        if depth <= 4:
            assert exhaustive_binary_test_gap(depth) == LAMBDA**depth
            assert row["binary_test_optimum_matches_tv"]


def test_rich_vector_protocol_has_constant_gap() -> None:
    for depth in range(2, 7):
        row = rich_vector_protocol_audit(depth)
        assert row[
            "all_opposite_parity_vectors_have_a_differing_coordinate"
        ]
        assert Fraction(row["constant_completeness_soundness_gap"]) == Fraction(
            3, 5
        )
        assert row["semantic_queries"] == 1


def test_resource_ledgers_are_polylogarithmic() -> None:
    for public_length in range(4, 1025):
        row = bit_cost_row(public_length)
        depth = row["depth"]
        assert row["both_are_polylog_in_prover_budget"]
        assert row["semantic_query_budget"] == depth**2
        assert row["verifier_time_budget"] == 64 * depth**2
        assert row["transcript_budget"] == 18 * depth**2
        assert row["rich_transcript_bit_upper_bound"] <= row[
            "transcript_budget"
        ]


def test_producer_and_independent_verifier_pass() -> None:
    result = build_result()
    assert result["certified"]
    assert all(result["gates"].values())
    verification = verify()
    assert verification["passed"]
    assert all(verification["checks"].values())


def test_release_manifest_matches() -> None:
    assert verify_manifest()
