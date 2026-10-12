from __future__ import annotations

from fractions import Fraction
from itertools import product
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from verify_weighted_noise_subset_sum import verify
from weighted_noise_subset_sum import (
    all_words,
    build_result,
    legal_score_sets,
    legal_words,
    prefix_counts,
    score,
    score_rule_average,
    subset_sum_witness,
    subset_sums,
    weighted_row,
    worst_payoff,
)


HERE = Path(__file__).resolve().parent


def test_invalid_cost_models_are_rejected() -> None:
    for costs, budget in (((), 0), ((1, 0), 0), ((1, -1), 0), ((1, 2), -1), ((1, 2), 4)):
        with pytest.raises(ValueError):
            weighted_row(costs, budget)


def test_binary_words_and_scores_are_exact() -> None:
    costs = (1, 3, 7)
    assert all_words(0) == ("",)
    assert all_words(3) == ("000", "001", "010", "011", "100", "101", "110", "111")
    assert [score(word, costs) for word in all_words(3)] == [0, 7, 3, 10, 1, 8, 4, 11]


def test_subset_sum_witness_is_constructive() -> None:
    costs = (2, 3, 7, 11)
    assert subset_sums(costs) == {score(word, costs) for word in all_words(4)}
    for target in subset_sums(costs):
        witness = subset_sum_witness(costs, target)
        assert witness is not None
        assert score(witness, costs) == target
    assert subset_sum_witness(costs, 6) is None


def test_score_overlap_matches_full_language_overlap() -> None:
    for costs in ((1, 2, 4), (2, 2, 3), (1, 1, 4, 4), (2, 2, 2, 4)):
        for budget in range(sum(costs) + 1):
            zero_words, one_words = legal_words(costs, budget)
            zero_scores, one_scores = legal_score_sets(costs, budget)
            assert bool(set(zero_words) & set(one_words)) == bool(
                set(zero_scores) & set(one_scores)
            )


def test_exact_value_is_interval_subset_sum_criterion() -> None:
    for costs in ((1,), (1, 2), (1, 3, 4), (2, 2, 2, 4), (1, 1, 4, 4)):
        total = sum(costs)
        sums = subset_sums(costs)
        for budget in range(total + 1):
            overlap = any(total - budget <= value <= budget for value in sums)
            row = weighted_row(costs, budget)
            assert (row["value"] == "0") == overlap
            assert row["certified"]


def test_equal_size_total_and_budget_can_have_opposite_values() -> None:
    separable = weighted_row((2, 2, 2, 4), 5)
    overlap = weighted_row((1, 1, 4, 4), 5)
    assert separable["total_cost"] == overlap["total_cost"] == 10
    assert separable["value"] == "1"
    assert overlap["value"] == "0"
    assert overlap["common_score"] == 5


def test_prefix_dynamic_program_compresses_histories() -> None:
    for costs in ((1, 1, 1, 1), (1, 2, 4, 8), (2, 3, 3, 4)):
        for budget in range(sum(costs) + 1):
            full, quotient = prefix_counts(costs, budget)
            assert quotient <= full
            assert quotient <= len(costs) * (budget + 1)


def test_score_averaging_is_constant_and_never_hurts_small_rules() -> None:
    costs = (1, 1, 2)
    universe = all_words(3)
    for choices in product((Fraction(0), Fraction(1)), repeat=len(universe)):
        rule = dict(zip(universe, choices))
        averaged = score_rule_average(rule, costs)
        for left in universe:
            for right in universe:
                if score(left, costs) == score(right, costs):
                    assert averaged[left] == averaged[right]
        for budget in range(sum(costs) + 1):
            assert worst_payoff(averaged, costs, budget) >= worst_payoff(
                rule, costs, budget
            )


def test_unit_cost_rows_reduce_exactly_to_hamming_phase() -> None:
    for depth in range(1, 9):
        for budget in range(depth + 1):
            row = weighted_row((1,) * depth, budget)
            assert (row["value"] == "1") == (2 * budget < depth)
            assert row["weighted_terminal_states_per_truth"] == budget + 1


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["weighted_rows"]) == 2729
    assert len(result["parent_cross_checks"]) == 27
    assert result["certified"]
    assert len(result["gates"]) == 8
    assert all(result["gates"].values())


def test_exponential_distinct_score_obstruction() -> None:
    result = build_result()["exponential_distinct_score_witness"]
    assert result["depth"] == 32
    assert result["full_terminal_words_per_truth"] == 1 << 32
    assert result["unique_weighted_scores_per_truth"] == 1 << 32
    assert result["compression_factor"] == "1"


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 8
    assert all(result["checks"].values())


def test_complexity_and_claim_boundaries_are_explicit() -> None:
    theorem = (HERE / "WEIGHTED_NOISE_SUBSET_SUM_THEOREM_v1_6.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v1_6.md").read_text(encoding="utf-8")
    assert "PARTITION boundary" in theorem
    assert "pseudo-polynomial" in theorem
    assert "Convincing local stopping boundary" in audit
    assert "honest-prover computation characterization = open" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
