from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
PARENT_ARTIFACT = (
    HERE.parent
    / "asmp3_adaptive_noise_sequence_v1_4"
    / "artifacts"
    / "adaptive_noise_sequence_v1_4.json"
)


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def language_size(depth: int, budget: int) -> int:
    return sum(comb(depth, flips) for flips in range(budget + 1))


def prefix_tree_states_per_truth(depth: int, budget: int) -> int:
    return sum(
        sum(comb(round_index, flips) for flips in range(min(budget, round_index) + 1))
        for round_index in range(depth)
    )


def quotient_controller_states_per_truth(depth: int, budget: int) -> int:
    return sum(min(budget, round_index) + 1 for round_index in range(depth))


def quotient_terminal_states_per_truth(depth: int, budget: int) -> int:
    return min(depth, budget) + 1


def weight_ranges(depth: int, budget: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return tuple(range(0, budget + 1)), tuple(range(depth - budget, depth + 1))


def overlap_weight_count(depth: int, budget: int) -> int:
    low = max(0, depth - budget)
    high = min(depth, budget)
    return max(0, high - low + 1)


def quotient_row(depth: int, budget: int) -> dict[str, object]:
    if depth < 1 or budget < 0 or budget > depth:
        raise ValueError("invalid quotient parameters")
    zero_weights, one_weights = weight_ranges(depth, budget)
    overlap = set(zero_weights) & set(one_weights)
    separable = 2 * budget < depth
    full_language = language_size(depth, budget)
    full_prefix = prefix_tree_states_per_truth(depth, budget)
    quotient_controller = quotient_controller_states_per_truth(depth, budget)
    quotient_terminal = quotient_terminal_states_per_truth(depth, budget)
    return {
        "depth": depth,
        "flip_budget": budget,
        "phase": "separable" if separable else "overlap",
        "value": "1" if separable else "0",
        "truth_zero_weight_range": list(zero_weights),
        "truth_one_weight_range": list(one_weights),
        "overlap_weight_count": len(overlap),
        "overlap_weight_count_formula": overlap_weight_count(depth, budget),
        "full_terminal_words_per_truth": full_language,
        "full_prefix_controller_nodes_per_truth": full_prefix,
        "quotient_controller_states_per_truth": quotient_controller,
        "quotient_terminal_states_per_truth": quotient_terminal,
        "quotient_controller_formula": (
            (budget + 1) * (depth - budget) + budget * (budget + 1) // 2
        ),
        "full_to_quotient_terminal_factor_numerator": full_language,
        "full_to_quotient_terminal_factor_denominator": quotient_terminal,
        "max_strategy": (
            "guess_by_disjoint_weight_range"
            if separable
            else "uniform_guess_at_every_weight"
        ),
        "min_strategy": (
            "any_legal_controller"
            if separable
            else f"emit_common_weight_{depth - budget}_under_both_truths"
        ),
        "certified": (
            bool(overlap) is (not separable)
            and len(overlap) == overlap_weight_count(depth, budget)
            and quotient_controller
            == (budget + 1) * (depth - budget)
            + budget * (budget + 1) // 2
        ),
    }


def all_words(depth: int) -> tuple[str, ...]:
    return tuple(format(value, f"0{depth}b") for value in range(1 << depth))


def response_languages(depth: int, budget: int) -> tuple[tuple[str, ...], tuple[str, ...]]:
    words = all_words(depth)
    return (
        tuple(word for word in words if word.count("1") <= budget),
        tuple(word for word in words if word.count("0") <= budget),
    )


def worst_payoff(
    rule: dict[str, Q], depth: int, budget: int
) -> Q:
    zero, one = response_languages(depth, budget)
    zero_payoff = min(1 - 2 * rule[word] for word in zero)
    one_payoff = min(2 * rule[word] - 1 for word in one)
    return (zero_payoff + one_payoff) / 2


def symmetrize_rule(rule: dict[str, Q], depth: int) -> dict[str, Q]:
    by_weight = {}
    for weight in range(depth + 1):
        orbit = [word for word in rule if word.count("1") == weight]
        by_weight[weight] = sum((rule[word] for word in orbit), Q(0)) / len(orbit)
    return {word: by_weight[word.count("1")] for word in rule}


def symmetry_exhaustion_row(depth: int, budget: int) -> dict[str, object]:
    words = all_words(depth)
    rules_checked = 0
    minimum_improvement: Q | None = None
    all_hold = True
    for bits in product((Q(0), Q(1)), repeat=len(words)):
        rule = dict(zip(words, bits))
        original = worst_payoff(rule, depth, budget)
        symmetric = worst_payoff(symmetrize_rule(rule, depth), depth, budget)
        improvement = symmetric - original
        minimum_improvement = (
            improvement
            if minimum_improvement is None
            else min(minimum_improvement, improvement)
        )
        all_hold = all_hold and improvement >= 0
        rules_checked += 1
    return {
        "depth": depth,
        "flip_budget": budget,
        "deterministic_rules_checked": rules_checked,
        "expected_rule_count": 1 << (1 << depth),
        "minimum_symmetrization_improvement": qstr(minimum_improvement or Q(0)),
        "symmetrization_never_hurts": all_hold,
    }


def parent_cross_checks(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    parent = json.loads(PARENT_ARTIFACT.read_text(encoding="utf-8"))
    parent_by_key = {
        (row["depth"], row["flip_budget"]): row for row in parent["case_rows"]
    }
    checks = []
    for row in rows:
        if row["depth"] > 6:
            continue
        parent_row = parent_by_key[(row["depth"], row["flip_budget"])]
        checks.append(
            {
                "depth": row["depth"],
                "flip_budget": row["flip_budget"],
                "value_matches": row["value"] == parent_row["value"],
                "language_size_matches": (
                    row["full_terminal_words_per_truth"]
                    == parent_row["truth_zero_language_size"]
                ),
                "prefix_state_count_matches": (
                    2 * row["full_prefix_controller_nodes_per_truth"]
                    == parent_row["min_information_sets"]
                ),
            }
        )
    return checks


def build_result() -> dict[str, object]:
    rows = [
        quotient_row(depth, budget)
        for depth in range(1, 33)
        for budget in range(depth + 1)
    ]
    symmetry = [
        symmetry_exhaustion_row(depth, budget)
        for depth in range(1, 4)
        for budget in range(depth + 1)
    ]
    cross_checks = parent_cross_checks(rows)
    gates = {
        "Q0_registry_complete": len(rows) == sum(depth + 1 for depth in range(1, 33)),
        "Q1_all_quotient_rows_certified": all(row["certified"] for row in rows),
        "Q2_value_phase_matches_two_b_boundary": all(
            (row["value"] == "1") == (2 * row["flip_budget"] < row["depth"])
            for row in rows
        ),
        "Q3_controller_state_formula_exact": all(
            row["quotient_controller_states_per_truth"]
            == row["quotient_controller_formula"]
            for row in rows
        ),
        "Q4_symmetrization_exhaustion_passes": all(
            row["symmetrization_never_hurts"]
            and row["deterministic_rules_checked"] == row["expected_rule_count"]
            for row in symmetry
        ),
        "Q5_parent_v1_4_cross_checks_pass": all(
            row["value_matches"]
            and row["language_size_matches"]
            and row["prefix_state_count_matches"]
            for row in cross_checks
        ),
        "Q6_exponential_compression_witnessed": (
            quotient_row(32, 32)["full_terminal_words_per_truth"] == 1 << 32
            and quotient_row(32, 32)["quotient_terminal_states_per_truth"] == 33
        ),
    }
    return {
        "schema_version": "asmp3_noise_symmetry_quotient_v1_5",
        "experiment_id": "ASMP-3-NOISE-SYMMETRY-QUOTIENT-v1.5",
        "status": "exact_permutation_quotient_phase",
        "parent_result": "ASMP-3-ADAPTIVE-NOISE-SEQUENCE-v1.4",
        "theorem": {
            "group": "all coordinate permutations S_d",
            "orbits": "response words with equal Hamming weight",
            "symmetrization": (
                "averaging a verifier over S_d cannot decrease either "
                "truth-conditioned worst-case payoff"
            ),
            "controller_state": "(truth, round, flips_used)",
            "terminal_observation": "Hamming weight",
            "value": "1 if 2b<d, otherwise 0",
        },
        "quotient_rows": rows,
        "symmetry_exhaustion_rows": symmetry,
        "parent_cross_checks": cross_checks,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The quotient relies on coordinate-permutation invariance of the "
            "truth prior, hard Hamming budget, terminal payoff, and verifier "
            "observation costs. Position-dependent queries or noise invalidate it."
        ),
    }
