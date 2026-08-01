from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from noise_symmetry_quotient import (
    all_words,
    build_result,
    language_size,
    overlap_weight_count,
    prefix_tree_states_per_truth,
    quotient_controller_states_per_truth,
    quotient_row,
    symmetrize_rule,
    worst_payoff,
)
from verify_noise_symmetry_quotient import verify


HERE = Path(__file__).resolve().parent


def test_invalid_quotient_parameters_are_rejected() -> None:
    for depth, budget in ((0, 0), (3, -1), (3, 4)):
        with pytest.raises(ValueError, match="invalid quotient parameters"):
            quotient_row(depth, budget)


def test_language_and_overlap_formulas_are_exact() -> None:
    for depth in range(1, 13):
        for budget in range(depth + 1):
            assert language_size(depth, budget) == sum(
                comb(depth, flips) for flips in range(budget + 1)
            )
            expected_overlap = max(0, 2 * budget - depth + 1)
            assert overlap_weight_count(depth, budget) == expected_overlap


def test_value_phase_is_exact_for_all_registered_rows() -> None:
    for depth in range(1, 33):
        for budget in range(depth + 1):
            row = quotient_row(depth, budget)
            assert (row["value"] == "1") == (2 * budget < depth)
            assert row["certified"]


def test_quotient_controller_closed_form_is_exact() -> None:
    for depth in range(1, 33):
        for budget in range(depth + 1):
            counted = quotient_controller_states_per_truth(depth, budget)
            formula = (budget + 1) * (depth - budget) + budget * (budget + 1) // 2
            assert counted == formula


def test_prefix_tree_count_dominates_quotient_count() -> None:
    for depth in range(1, 17):
        for budget in range(depth + 1):
            assert prefix_tree_states_per_truth(
                depth, budget
            ) >= quotient_controller_states_per_truth(depth, budget)


def test_symmetrized_rule_is_constant_on_weight_orbits() -> None:
    depth = 4
    rule = {
        word: Fraction(index, (1 << depth) - 1)
        for index, word in enumerate(all_words(depth))
    }
    symmetric = symmetrize_rule(rule, depth)
    for left in rule:
        for right in rule:
            if left.count("1") == right.count("1"):
                assert symmetric[left] == symmetric[right]


def test_symmetrization_never_hurts_all_small_deterministic_rules() -> None:
    for depth in range(1, 4):
        words = all_words(depth)
        for choices in product((Fraction(0), Fraction(1)), repeat=len(words)):
            rule = dict(zip(words, choices))
            symmetric = symmetrize_rule(rule, depth)
            for budget in range(depth + 1):
                assert worst_payoff(symmetric, depth, budget) >= worst_payoff(
                    rule, depth, budget
                )


def test_registry_and_parent_cross_checks_are_complete() -> None:
    result = build_result()
    expected = [
        (depth, budget)
        for depth in range(1, 33)
        for budget in range(depth + 1)
    ]
    assert [(row["depth"], row["flip_budget"]) for row in result["quotient_rows"]] == expected
    assert len(result["parent_cross_checks"]) == 27
    assert all(
        all(value for name, value in row.items() if name.endswith("_matches"))
        for row in result["parent_cross_checks"]
    )


def test_exponential_terminal_compression_witness() -> None:
    row = quotient_row(32, 32)
    assert row["full_terminal_words_per_truth"] == 1 << 32
    assert row["quotient_terminal_states_per_truth"] == 33
    assert row["quotient_controller_states_per_truth"] == 528


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


def test_invariance_and_open_scope_are_explicit() -> None:
    theorem = (HERE / "NOISE_SYMMETRY_QUOTIENT_THEOREM_v1_5.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v1_5.md").read_text(encoding="utf-8")
    assert "Invariance firewall" in theorem
    assert "Position-dependent queries" in theorem
    assert "honest-prover computation characterization = open" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
