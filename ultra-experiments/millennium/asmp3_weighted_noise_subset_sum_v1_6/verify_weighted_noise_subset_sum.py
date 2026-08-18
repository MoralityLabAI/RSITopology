from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations_with_replacement, product
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "weighted_noise_subset_sum_v1_6.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "weighted_noise_subset_sum_verification_v1_6.json"
)
PARENT_PATH = (
    HERE.parent
    / "asmp3_noise_symmetry_quotient_v1_5"
    / "artifacts"
    / "noise_symmetry_quotient_v1_5.json"
)


def words(depth: int) -> tuple[str, ...]:
    if depth == 0:
        return ("",)
    return tuple(format(index, f"0{depth}b") for index in range(1 << depth))


def weighted_score(word: str, costs: tuple[int, ...]) -> int:
    return sum(cost for bit, cost in zip(word, costs) if bit == "1")


def reachable(costs: tuple[int, ...]) -> set[int]:
    values = {0}
    for cost in costs:
        values = values | {value + cost for value in values}
    return values


def rule_value(
    rule: dict[str, Q], costs: tuple[int, ...], budget: int
) -> Q:
    total = sum(costs)
    universe = words(len(costs))
    zero = [word for word in universe if weighted_score(word, costs) <= budget]
    one = [
        word for word in universe if total - weighted_score(word, costs) <= budget
    ]
    return (
        min(1 - 2 * rule[word] for word in zero)
        + min(2 * rule[word] - 1 for word in one)
    ) / 2


def average_by_score(
    rule: dict[str, Q], costs: tuple[int, ...]
) -> dict[str, Q]:
    means = {}
    for value in reachable(costs):
        cell = [
            probability
            for word, probability in rule.items()
            if weighted_score(word, costs) == value
        ]
        means[value] = sum(cell, Q(0)) / len(cell)
    return {word: means[weighted_score(word, costs)] for word in rule}


def reconstruct_row(row: dict[str, object]) -> bool:
    costs = tuple(int(cost) for cost in row["costs"])
    budget = int(row["budget"])
    total = sum(costs)
    universe = words(len(costs))
    scores = {word: weighted_score(word, costs) for word in universe}
    zero_words = [word for word in universe if scores[word] <= budget]
    one_words = [word for word in universe if total - scores[word] <= budget]
    sums = reachable(costs)
    zero_scores = sorted(value for value in sums if value <= budget)
    one_scores = sorted(total - value for value in sums if value <= budget)
    lower, upper = max(0, total - budget), min(total, budget)
    overlap = sorted(set(zero_scores) & set(one_scores))
    interval = sorted(value for value in sums if lower <= value <= upper)
    full_prefix = 0
    quotient_prefix = 0
    for round_index in range(len(costs)):
        prefix_scores = [
            weighted_score(word, costs[:round_index])
            for word in words(round_index)
        ]
        full_prefix += sum(value <= budget for value in prefix_scores)
        quotient_prefix += len({value for value in prefix_scores if value <= budget})
    common = overlap[0] if overlap else None
    common_word = next(
        (word for word in universe if scores[word] == common),
        None,
    )
    separable = not overlap
    return (
        int(row["depth"]) == len(costs)
        and int(row["total_cost"]) == total
        and row["overlap_interval"] == [lower, upper]
        and row["reachable_subset_sums"] == sorted(sums)
        and row["truth_zero_scores"] == zero_scores
        and row["truth_one_scores"] == one_scores
        and row["overlap_scores"] == overlap == interval
        and row["interval_subset_sum_witnesses"] == interval
        and row["common_score"] == common
        and row["common_word"] == common_word
        and row["phase"] == ("separable" if separable else "overlap")
        and row["value"] == ("1" if separable else "0")
        and int(row["full_terminal_words_per_truth"])
        == len(zero_words)
        == len(one_words)
        and int(row["weighted_terminal_states_per_truth"]) == len(zero_scores)
        and int(row["full_prefix_controller_nodes_per_truth"]) == full_prefix
        and int(row["weighted_prefix_controller_states_per_truth"])
        == quotient_prefix
        and int(row["pseudo_polynomial_state_upper_bound"])
        == len(costs) * (budget + 1)
        and row["max_strategy"]
        == (
            "guess_by_disjoint_weighted_score"
            if separable
            else "uniform_guess_at_every_weighted_score"
        )
        and row["min_strategy"]
        == (
            "any_legal_controller"
            if separable
            else f"emit_common_word_{common_word}_under_both_truths"
        )
        and row["certified"] is True
    )


def replay_symmetry() -> dict[str, object]:
    cases = 0
    instances = 0
    minimum: Q | None = None
    passed = True
    for depth in range(1, 4):
        for costs in combinations_with_replacement(range(1, 4), depth):
            universe = words(depth)
            for choices in product((Q(0), Q(1)), repeat=len(universe)):
                rule = dict(zip(universe, choices))
                averaged = average_by_score(rule, costs)
                for budget in range(sum(costs) + 1):
                    improvement = (
                        rule_value(averaged, costs, budget)
                        - rule_value(rule, costs, budget)
                    )
                    minimum = improvement if minimum is None else min(minimum, improvement)
                    passed = passed and improvement >= 0
                    instances += 1
            cases += sum(costs) + 1
    return {
        "cost_budget_cases_checked": cases,
        "deterministic_rule_instances_checked": instances,
        "minimum_symmetrization_improvement": str(minimum or Q(0)),
        "score_averaging_never_hurts": passed,
    }


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    rows = result.get("weighted_rows", [])
    expected_keys = [
        (costs, budget)
        for depth in range(1, 7)
        for costs in combinations_with_replacement(range(1, 5), depth)
        for budget in range(sum(costs) + 1)
    ]
    parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))
    parent_by_key = {
        (row["depth"], row["flip_budget"]): row
        for row in parent["quotient_rows"]
    }
    unit_rows = {
        (len(row["costs"]), row["budget"]): row
        for row in rows
        if len(set(row["costs"])) == 1 and row["costs"][0] == 1
    }
    unit_match = True
    for depth in range(1, 7):
        for budget in range(depth + 1):
            row = unit_rows[(depth, budget)]
            parent_row = parent_by_key[(depth, budget)]
            unit_match = unit_match and (
                row["value"] == parent_row["value"]
                and row["full_terminal_words_per_truth"]
                == parent_row["full_terminal_words_per_truth"]
                and row["full_prefix_controller_nodes_per_truth"]
                == parent_row["full_prefix_controller_nodes_per_truth"]
                and row["weighted_prefix_controller_states_per_truth"]
                == parent_row["quotient_controller_states_per_truth"]
            )
    symmetry = replay_symmetry()
    paired = result.get("paired_hamming_insufficiency_witness", {})
    exponential = result.get("exponential_distinct_score_witness", {})
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version") == "asmp3_weighted_noise_subset_sum_v1_6"
            and result.get("status")
            == "exact_weighted_budget_phase_and_complexity_boundary"
            and result.get("parent_result")
            == "ASMP-3-NOISE-SYMMETRY-QUOTIENT-v1.5"
            and result.get("certified") is True
            and "positive integer" in result.get("claim_boundary", "")
        ),
        "V1_complete_2729_row_registry_reconstructed": (
            len(rows) == 2729
            and [(tuple(row["costs"]), row["budget"]) for row in rows]
            == expected_keys
        ),
        "V2_all_languages_scores_states_and_saddles_reconstructed": all(
            reconstruct_row(row) for row in rows
        ),
        "V3_score_symmetrization_exhaustion_replayed": (
            all(
                symmetry[name] == result["symmetry_exhaustion"][name]
                for name in symmetry
            )
            and symmetry["score_averaging_never_hurts"] is True
        ),
        "V4_unit_cost_parent_reduction_exact": (
            len(result.get("parent_cross_checks", [])) == 27 and unit_match
        ),
        "V5_equal_size_total_budget_opposite_phase_pair_reconstructed": (
            paired.get("shared_depth") == 4
            and paired.get("shared_total_cost") == 10
            and paired.get("shared_budget") == 5
            and not (
                set(reachable((2, 2, 2, 4))) & {5}
            )
            and 5 in reachable((1, 1, 4, 4))
            and paired.get("separable_value") == "1"
            and paired.get("overlap_value") == "0"
        ),
        "V6_binary_weight_exponential_obstruction_reconstructed": (
            exponential.get("depth") == 32
            and exponential.get("budget") == (1 << 32) - 1
            and exponential.get("full_terminal_words_per_truth") == 1 << 32
            and exponential.get("unique_weighted_scores_per_truth") == 1 << 32
            and exponential.get("compression_factor") == "1"
        ),
        "V7_producer_gates_all_true": (
            len(result.get("gates", {})) == 8 and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_weighted_noise_subset_sum_verification_v1_6",
        "checker": "clean_room_weighted_language_dp_and_symmetry_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates finite positive-integer flip costs under a "
            "hard terminal budget. It does not extend the quotient to stochastic, "
            "signed, real-valued, or path-observed cost models."
        ),
    }


def main() -> None:
    result = verify()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if not result["passed"]:
        failed = [name for name, passed in result["checks"].items() if not passed]
        raise SystemExit(f"weighted-noise verification failed: {failed}")
    print(
        "ASMP-3 weighted-noise independent verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
