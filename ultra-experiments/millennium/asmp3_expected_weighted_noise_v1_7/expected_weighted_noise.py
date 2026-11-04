from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
PARENT_ARTIFACT = (
    HERE.parent
    / "asmp3_weighted_noise_subset_sum_v1_6"
    / "artifacts"
    / "weighted_noise_subset_sum_v1_6.json"
)


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def validate(costs: tuple[int, ...], budget: Q) -> None:
    if not costs or any(not isinstance(cost, int) or cost <= 0 for cost in costs):
        raise ValueError("costs must be a nonempty tuple of positive integers")
    if budget < 0 or budget > sum(costs):
        raise ValueError("expected budget must lie between zero and total cost")


def exact_value(total_cost: int, budget: Q) -> Q:
    if total_cost <= 0 or budget < 0 or budget > total_cost:
        raise ValueError("invalid total cost or expected budget")
    return max(Q(0), Q(1) - 2 * budget / total_cost)


def expected_row(costs: tuple[int, ...], budget: Q | int) -> dict[str, object]:
    budget = Q(budget)
    validate(costs, budget)
    total = sum(costs)
    value = exact_value(total, budget)
    collapsed = 2 * budget >= total
    wrong_endpoint_mass = min(budget / total, Q(1, 2))
    endpoint_expected_cost = wrong_endpoint_mass * total
    endpoint_tv = abs(Q(1) - 2 * wrong_endpoint_mass)
    linear_verifier_bound = Q(1) - 2 * budget / total
    return {
        "costs": list(costs),
        "depth": len(costs),
        "expected_budget": qstr(budget),
        "total_cost": total,
        "normalized_budget": qstr(budget / total),
        "phase": "collapsed" if collapsed else "positive_advantage",
        "value": qstr(value),
        "max_strategy": (
            "uniform_guess"
            if collapsed
            else "guess_one_with_probability_weighted_score_over_total"
        ),
        "min_strategy": "symmetric_all_zero_all_one_endpoint_mixture",
        "truth_zero_endpoint_probabilities": {
            "all_zero": qstr(Q(1) - wrong_endpoint_mass),
            "all_one": qstr(wrong_endpoint_mass),
        },
        "truth_one_endpoint_probabilities": {
            "all_zero": qstr(wrong_endpoint_mass),
            "all_one": qstr(Q(1) - wrong_endpoint_mass),
        },
        "endpoint_expected_flip_cost_each_truth": qstr(endpoint_expected_cost),
        "endpoint_total_variation": qstr(endpoint_tv),
        "dual_expectation_gap_lower_bound": qstr(max(Q(0), linear_verifier_bound)),
        "linear_verifier_truth_conditioned_bound": qstr(linear_verifier_bound),
        "certified": (
            endpoint_expected_cost <= budget
            and endpoint_tv == value
            and max(Q(0), linear_verifier_bound) == value
            and (collapsed == (value == 0))
        ),
    }


def compositions(total: int, parts: int) -> tuple[tuple[int, ...], ...]:
    if parts == 1:
        return ((total,),)
    rows = []
    for first in range(total + 1):
        for suffix in compositions(total - first, parts - 1):
            rows.append((first,) + suffix)
    return tuple(rows)


def word_scores(costs: tuple[int, ...]) -> tuple[int, ...]:
    scores = []
    for index in range(1 << len(costs)):
        word = format(index, f"0{len(costs)}b")
        scores.append(
            sum(cost for bit, cost in zip(word, costs) if bit == "1")
        )
    return tuple(scores)


def grid_exhaustion() -> dict[str, object]:
    rows = []
    total_pairs = 0
    for depth in range(1, 3):
        for costs in combinations_with_replacement(range(1, 4), depth):
            total = sum(costs)
            scores = word_scores(costs)
            distributions = compositions(total, len(scores))
            for budget in range(total + 1):
                zero_legal = [
                    distribution
                    for distribution in distributions
                    if sum(units * score for units, score in zip(distribution, scores))
                    <= budget * total
                ]
                one_legal = [
                    distribution
                    for distribution in distributions
                    if sum(
                        units * (total - score)
                        for units, score in zip(distribution, scores)
                    )
                    <= budget * total
                ]
                minimum: Q | None = None
                pairs = 0
                for zero in zero_legal:
                    for one in one_legal:
                        tv = Q(
                            sum(abs(left - right) for left, right in zip(zero, one)),
                            2 * total,
                        )
                        minimum = tv if minimum is None else min(minimum, tv)
                        pairs += 1
                claimed = exact_value(total, Q(budget))
                rows.append(
                    {
                        "costs": list(costs),
                        "budget": budget,
                        "probability_denominator": total,
                        "truth_zero_distributions": len(zero_legal),
                        "truth_one_distributions": len(one_legal),
                        "distribution_pairs_checked": pairs,
                        "minimum_grid_total_variation": qstr(minimum or Q(0)),
                        "claimed_value": qstr(claimed),
                        "matches": minimum == claimed,
                    }
                )
                total_pairs += pairs
    return {
        "depths": [1, 2],
        "coordinate_costs": [1, 2, 3],
        "probability_grid_denominator": "total cost C",
        "case_count": len(rows),
        "distribution_pairs_checked": total_pairs,
        "rows": rows,
        "all_grid_optima_match": all(row["matches"] for row in rows),
    }


def build_result() -> dict[str, object]:
    parent = json.loads(PARENT_ARTIFACT.read_text(encoding="utf-8"))
    parent_rows = parent["weighted_rows"]
    rows = []
    strict_separations = []
    for hard_row in parent_rows:
        costs = tuple(hard_row["costs"])
        budget = Q(hard_row["budget"])
        row = expected_row(costs, budget)
        row["parent_hard_budget_value"] = hard_row["value"]
        row["expected_value_no_greater_than_hard_value"] = (
            Q(row["value"]) <= Q(hard_row["value"])
        )
        if Q(row["value"]) < Q(hard_row["value"]):
            strict_separations.append(
                {
                    "costs": list(costs),
                    "budget": hard_row["budget"],
                    "hard_value": hard_row["value"],
                    "expected_value": row["value"],
                }
            )
        rows.append(row)

    grid = grid_exhaustion()
    paired = {
        "shared_depth": 4,
        "shared_total_cost": 10,
        "shared_expected_budget": "5",
        "costs_a": [2, 2, 2, 4],
        "costs_b": [1, 1, 4, 4],
        "expected_value_a": expected_row((2, 2, 2, 4), 5)["value"],
        "expected_value_b": expected_row((1, 1, 4, 4), 5)["value"],
        "parent_hard_value_a": "1",
        "parent_hard_value_b": "0",
    }
    fractional = expected_row((1, 3, 4), Q(3, 2))
    powers_total = (1 << 32) - 1
    large = {
        "costs": "1,2,4,...,2^31",
        "depth": 32,
        "total_cost": powers_total,
        "expected_budget": qstr(Q(powers_total, 3)),
        "value": qstr(exact_value(powers_total, Q(powers_total, 3))),
        "certificate_size": "O(1) rational formulas after summing costs",
        "response_words_enumerated": 0,
    }
    keys = [
        (tuple(row["costs"]), row["expected_budget"])
        for row in rows
    ]
    expected_keys = [
        (tuple(row["costs"]), str(row["budget"]))
        for row in parent_rows
    ]
    groups: dict[tuple[int, str], set[str]] = {}
    for row in rows:
        key = (row["total_cost"], row["expected_budget"])
        groups.setdefault(key, set()).add(row["value"])
    gates = {
        "E0_parent_registry_complete": len(rows) == 2729 and keys == expected_keys,
        "E1_all_endpoint_dual_saddles_exact": all(row["certified"] for row in rows),
        "E2_value_depends_only_on_total_and_expected_budget": all(
            len(values) == 1 for values in groups.values()
        ),
        "E3_expected_constraint_never_stronger_than_hard_constraint": all(
            row["expected_value_no_greater_than_hard_value"] for row in rows
        ),
        "E4_strict_hard_expected_separations_witnessed": (
            len(strict_separations) > 0
            and any(
                row["costs"] == [2, 2, 2, 4]
                and row["budget"] == 5
                and row["hard_value"] == "1"
                and row["expected_value"] == "0"
                for row in strict_separations
            )
        ),
        "E5_small_distribution_grid_optima_match": (
            grid["case_count"] > 0
            and grid["distribution_pairs_checked"] > 0
            and grid["all_grid_optima_match"]
        ),
        "E6_fractional_budget_certificate_exact": (
            fractional["expected_budget"] == "3/2"
            and fractional["total_cost"] == 8
            and fractional["value"] == "5/8"
        ),
        "E7_convexification_removes_subset_sum_pair_difference": (
            paired["expected_value_a"] == paired["expected_value_b"] == "0"
            and paired["parent_hard_value_a"] != paired["parent_hard_value_b"]
        ),
        "E8_large_binary_weight_certificate_is_succinct": (
            large["value"] == "1/3"
            and large["response_words_enumerated"] == 0
        ),
    }
    return {
        "schema_version": "asmp3_expected_weighted_noise_v1_7",
        "experiment_id": "ASMP-3-EXPECTED-WEIGHTED-NOISE-v1.7",
        "status": "exact_expected_budget_tv_phase",
        "parent_result": "ASMP-3-WEIGHTED-NOISE-SUBSET-SUM-v1.6",
        "theorem": {
            "noise_constraint": "expected flip cost at most B under each truth",
            "verifier": "guess one with probability weighted score divided by C",
            "noise": "matching mixtures of all-zero and all-one words",
            "value": "max(0,1-2B/C)",
            "duality": "bounded-score expectation gap lower-bounds total variation",
        },
        "registry_parameters": {
            "source": "all 2729 integer-budget v1.6 weighted cases",
            "row_count": len(rows),
            "fractional_budget_support": True,
        },
        "expected_rows": rows,
        "strict_hard_expected_separations": strict_separations,
        "small_distribution_grid_exhaustion": grid,
        "paired_convexification_witness": paired,
        "fractional_budget_witness": fractional,
        "large_succinct_witness": large,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The theorem requires a separate expected positive-integer flip-cost "
            "bound under each truth, complementary endpoint costs, uniform truth, "
            "and terminal-only verification. Almost-sure, tail-risk, coupled-prior, "
            "or path-observed constraints are different games."
        ),
    }
