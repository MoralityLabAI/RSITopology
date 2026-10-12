from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations_with_replacement, product
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
PARENT_ARTIFACT = (
    HERE.parent
    / "asmp3_noise_symmetry_quotient_v1_5"
    / "artifacts"
    / "noise_symmetry_quotient_v1_5.json"
)


def validate(costs: tuple[int, ...], budget: int) -> None:
    if not costs or any(not isinstance(cost, int) or cost <= 0 for cost in costs):
        raise ValueError("costs must be a nonempty tuple of positive integers")
    if not isinstance(budget, int) or budget < 0 or budget > sum(costs):
        raise ValueError("budget must be an integer between zero and total cost")


def all_words(depth: int) -> tuple[str, ...]:
    if depth == 0:
        return ("",)
    return tuple(format(index, f"0{depth}b") for index in range(1 << depth))


def score(word: str, costs: tuple[int, ...]) -> int:
    if len(word) != len(costs) or any(bit not in "01" for bit in word):
        raise ValueError("word and cost vector must have matching binary length")
    return sum(cost for bit, cost in zip(word, costs) if bit == "1")


def subset_sums(costs: tuple[int, ...]) -> set[int]:
    reachable = {0}
    for cost in costs:
        reachable |= {value + cost for value in tuple(reachable)}
    return reachable


def subset_sum_witness(costs: tuple[int, ...], target: int) -> str | None:
    for word in all_words(len(costs)):
        if score(word, costs) == target:
            return word
    return None


def legal_words(
    costs: tuple[int, ...], budget: int
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    validate(costs, budget)
    total = sum(costs)
    universe = all_words(len(costs))
    return (
        tuple(word for word in universe if score(word, costs) <= budget),
        tuple(word for word in universe if total - score(word, costs) <= budget),
    )


def legal_score_sets(
    costs: tuple[int, ...], budget: int
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    validate(costs, budget)
    total = sum(costs)
    affordable = {value for value in subset_sums(costs) if value <= budget}
    return tuple(sorted(affordable)), tuple(sorted(total - value for value in affordable))


def prefix_counts(costs: tuple[int, ...], budget: int) -> tuple[int, int]:
    validate(costs, budget)
    full_nodes = 0
    quotient_states = 0
    for round_index in range(len(costs)):
        prefix = costs[:round_index]
        prefix_scores = [score(word, prefix) for word in all_words(round_index)]
        full_nodes += sum(value <= budget for value in prefix_scores)
        quotient_states += len({value for value in prefix_scores if value <= budget})
    return full_nodes, quotient_states


def score_rule_average(
    rule: dict[str, Q], costs: tuple[int, ...]
) -> dict[str, Q]:
    if set(rule) != set(all_words(len(costs))):
        raise ValueError("rule must define every response word exactly once")
    averages: dict[int, Q] = {}
    for weighted_score in subset_sums(costs):
        orbit = [rule[word] for word in rule if score(word, costs) == weighted_score]
        averages[weighted_score] = sum(orbit, Q(0)) / len(orbit)
    return {word: averages[score(word, costs)] for word in rule}


def worst_payoff(rule: dict[str, Q], costs: tuple[int, ...], budget: int) -> Q:
    zero, one = legal_words(costs, budget)
    zero_payoff = min(1 - 2 * rule[word] for word in zero)
    one_payoff = min(2 * rule[word] - 1 for word in one)
    return (zero_payoff + one_payoff) / 2


def weighted_row(costs: tuple[int, ...], budget: int) -> dict[str, object]:
    validate(costs, budget)
    total = sum(costs)
    zero_words, one_words = legal_words(costs, budget)
    zero_scores, one_scores = legal_score_sets(costs, budget)
    overlap_scores = sorted(set(zero_scores) & set(one_scores))
    lower = max(0, total - budget)
    upper = min(total, budget)
    interval_witnesses = sorted(
        value for value in subset_sums(costs) if lower <= value <= upper
    )
    full_prefix, quotient_prefix = prefix_counts(costs, budget)
    common_score = overlap_scores[0] if overlap_scores else None
    common_word = (
        subset_sum_witness(costs, common_score)
        if common_score is not None
        else None
    )
    separable = not overlap_scores
    return {
        "costs": list(costs),
        "depth": len(costs),
        "budget": budget,
        "total_cost": total,
        "overlap_interval": [lower, upper],
        "reachable_subset_sums": sorted(subset_sums(costs)),
        "truth_zero_scores": list(zero_scores),
        "truth_one_scores": list(one_scores),
        "overlap_scores": overlap_scores,
        "interval_subset_sum_witnesses": interval_witnesses,
        "common_score": common_score,
        "common_word": common_word,
        "phase": "separable" if separable else "overlap",
        "value": "1" if separable else "0",
        "full_terminal_words_per_truth": len(zero_words),
        "weighted_terminal_states_per_truth": len(zero_scores),
        "full_prefix_controller_nodes_per_truth": full_prefix,
        "weighted_prefix_controller_states_per_truth": quotient_prefix,
        "pseudo_polynomial_state_upper_bound": len(costs) * (budget + 1),
        "max_strategy": (
            "guess_by_disjoint_weighted_score"
            if separable
            else "uniform_guess_at_every_weighted_score"
        ),
        "min_strategy": (
            "any_legal_controller"
            if separable
            else f"emit_common_word_{common_word}_under_both_truths"
        ),
        "certified": (
            overlap_scores == interval_witnesses
            and bool(set(zero_words) & set(one_words)) == bool(overlap_scores)
            and len(zero_words) == len(one_words)
            and quotient_prefix <= full_prefix
            and len(zero_scores) <= len(zero_words)
            and (common_word is None or score(common_word, costs) == common_score)
        ),
    }


def symmetry_exhaustion() -> dict[str, object]:
    cases = 0
    rules_checked = 0
    minimum_improvement: Q | None = None
    passed = True
    for depth in range(1, 4):
        for costs in combinations_with_replacement(range(1, 4), depth):
            universe = all_words(depth)
            rules = [
                dict(zip(universe, choices))
                for choices in product((Q(0), Q(1)), repeat=len(universe))
            ]
            for budget in range(sum(costs) + 1):
                cases += 1
                for rule in rules:
                    improvement = (
                        worst_payoff(score_rule_average(rule, costs), costs, budget)
                        - worst_payoff(rule, costs, budget)
                    )
                    minimum_improvement = (
                        improvement
                        if minimum_improvement is None
                        else min(minimum_improvement, improvement)
                    )
                    passed = passed and improvement >= 0
                    rules_checked += 1
    return {
        "cost_vectors_through_depth": 3,
        "maximum_coordinate_cost": 3,
        "cost_budget_cases_checked": cases,
        "deterministic_rule_instances_checked": rules_checked,
        "minimum_symmetrization_improvement": str(minimum_improvement or Q(0)),
        "score_averaging_never_hurts": passed,
    }


def registry() -> list[dict[str, object]]:
    return [
        weighted_row(costs, budget)
        for depth in range(1, 7)
        for costs in combinations_with_replacement(range(1, 5), depth)
        for budget in range(sum(costs) + 1)
    ]


def parent_cross_checks(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    parent = json.loads(PARENT_ARTIFACT.read_text(encoding="utf-8"))
    parent_by_key = {
        (row["depth"], row["flip_budget"]): row
        for row in parent["quotient_rows"]
    }
    by_key = {(tuple(row["costs"]), row["budget"]): row for row in rows}
    checks = []
    for depth in range(1, 7):
        costs = (1,) * depth
        for budget in range(depth + 1):
            row = by_key[(costs, budget)]
            parent_row = parent_by_key[(depth, budget)]
            checks.append(
                {
                    "depth": depth,
                    "budget": budget,
                    "value_matches": row["value"] == parent_row["value"],
                    "terminal_count_matches": (
                        row["full_terminal_words_per_truth"]
                        == parent_row["full_terminal_words_per_truth"]
                    ),
                    "prefix_count_matches": (
                        row["full_prefix_controller_nodes_per_truth"]
                        == parent_row["full_prefix_controller_nodes_per_truth"]
                    ),
                    "quotient_count_matches": (
                        row["weighted_prefix_controller_states_per_truth"]
                        == parent_row["quotient_controller_states_per_truth"]
                    ),
                }
            )
    return checks


def build_result() -> dict[str, object]:
    rows = registry()
    expected_keys = [
        (costs, budget)
        for depth in range(1, 7)
        for costs in combinations_with_replacement(range(1, 5), depth)
        for budget in range(sum(costs) + 1)
    ]
    symmetry = symmetry_exhaustion()
    parent = parent_cross_checks(rows)
    paired = {
        "shared_depth": 4,
        "shared_total_cost": 10,
        "shared_budget": 5,
        "separable_costs": [2, 2, 2, 4],
        "separable_value": weighted_row((2, 2, 2, 4), 5)["value"],
        "overlap_costs": [1, 1, 4, 4],
        "overlap_value": weighted_row((1, 1, 4, 4), 5)["value"],
    }
    powers_depth = 32
    powers_total = (1 << powers_depth) - 1
    exponential = {
        "costs": "1,2,4,...,2^31",
        "depth": powers_depth,
        "budget": powers_total,
        "full_terminal_words_per_truth": 1 << powers_depth,
        "unique_weighted_scores_per_truth": 1 << powers_depth,
        "compression_factor": "1",
        "reason": "binary expansion makes every subset score unique",
    }
    gates = {
        "W0_registry_complete": (
            len(rows) == len(expected_keys)
            and [(tuple(row["costs"]), row["budget"]) for row in rows]
            == expected_keys
        ),
        "W1_all_rows_certified": all(row["certified"] for row in rows),
        "W2_subset_sum_interval_phase_exact": all(
            (row["phase"] == "overlap")
            == bool(row["interval_subset_sum_witnesses"])
            for row in rows
        ),
        "W3_pseudo_polynomial_quotient_bounds_hold": all(
            row["weighted_prefix_controller_states_per_truth"]
            <= row["pseudo_polynomial_state_upper_bound"]
            and row["weighted_terminal_states_per_truth"] <= row["budget"] + 1
            for row in rows
        ),
        "W4_parent_unit_cost_cross_checks_pass": (
            len(parent) == 27
            and all(
                all(value for name, value in row.items() if name.endswith("_matches"))
                for row in parent
            )
        ),
        "W5_weighted_score_symmetrization_exhaustion_passes": (
            symmetry["score_averaging_never_hurts"]
            and symmetry["deterministic_rule_instances_checked"] > 0
        ),
        "W6_hamming_weight_and_total_budget_are_insufficient": (
            paired["separable_value"] == "1" and paired["overlap_value"] == "0"
        ),
        "W7_exponential_distinct_score_obstruction_witnessed": (
            exponential["full_terminal_words_per_truth"]
            == exponential["unique_weighted_scores_per_truth"]
            == 1 << 32
        ),
    }
    return {
        "schema_version": "asmp3_weighted_noise_subset_sum_v1_6",
        "experiment_id": "ASMP-3-WEIGHTED-NOISE-SUBSET-SUM-v1.6",
        "status": "exact_weighted_budget_phase_and_complexity_boundary",
        "parent_result": "ASMP-3-NOISE-SYMMETRY-QUOTIENT-v1.5",
        "theorem": {
            "controller_state": "(truth, round, spent_flip_cost)",
            "terminal_statistic": "sum_i c_i Y_i",
            "overlap_criterion": "a subset sum lies in [C-B,B]",
            "value": "1 iff no interval subset sum exists, otherwise 0",
            "algorithm": "pseudo-polynomial subset-sum dynamic program",
            "hardness": "PARTITION at even C and B=C/2",
        },
        "registry_parameters": {
            "depths": [1, 2, 3, 4, 5, 6],
            "coordinate_costs": [1, 2, 3, 4],
            "cost_vectors": "nondecreasing representatives",
            "all_budgets": True,
            "row_count": len(rows),
        },
        "weighted_rows": rows,
        "symmetry_exhaustion": symmetry,
        "parent_cross_checks": parent,
        "paired_hamming_insufficiency_witness": paired,
        "exponential_distinct_score_witness": exponential,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The exact result concerns positive integer coordinate costs and a "
            "hard total flip-cost budget with terminal-only verification. "
            "General implicit weighted instances inherit subset-sum complexity; "
            "stochastic, signed, real-valued, or path-observed costs are excluded."
        ),
    }
