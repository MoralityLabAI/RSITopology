from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "expected_weighted_noise_v1_7.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "expected_weighted_noise_verification_v1_7.json"
)
PARENT_PATH = (
    HERE.parent
    / "asmp3_weighted_noise_subset_sum_v1_6"
    / "artifacts"
    / "weighted_noise_subset_sum_v1_6.json"
)


def text(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def formula(total: int, budget: Q) -> Q:
    return max(Q(0), Q(1) - 2 * budget / total)


def reconstruct_row(row: dict[str, object]) -> bool:
    costs = tuple(int(cost) for cost in row["costs"])
    total = sum(costs)
    budget = Q(row["expected_budget"])
    value = formula(total, budget)
    collapsed = 2 * budget >= total
    wrong_mass = min(budget / total, Q(1, 2))
    expected_cost = wrong_mass * total
    tv = abs(Q(1) - 2 * wrong_mass)
    linear_bound = Q(1) - 2 * budget / total
    zero_probabilities = row["truth_zero_endpoint_probabilities"]
    one_probabilities = row["truth_one_endpoint_probabilities"]
    return (
        int(row["depth"]) == len(costs)
        and int(row["total_cost"]) == total
        and row["normalized_budget"] == text(budget / total)
        and row["phase"] == ("collapsed" if collapsed else "positive_advantage")
        and Q(row["value"]) == value
        and row["max_strategy"]
        == (
            "uniform_guess"
            if collapsed
            else "guess_one_with_probability_weighted_score_over_total"
        )
        and row["min_strategy"]
        == "symmetric_all_zero_all_one_endpoint_mixture"
        and Q(zero_probabilities["all_zero"]) == Q(1) - wrong_mass
        and Q(zero_probabilities["all_one"]) == wrong_mass
        and Q(one_probabilities["all_zero"]) == wrong_mass
        and Q(one_probabilities["all_one"]) == Q(1) - wrong_mass
        and Q(row["endpoint_expected_flip_cost_each_truth"]) == expected_cost
        and expected_cost <= budget
        and Q(row["endpoint_total_variation"]) == tv == value
        and Q(row["dual_expectation_gap_lower_bound"])
        == max(Q(0), linear_bound)
        == value
        and Q(row["linear_verifier_truth_conditioned_bound"]) == linear_bound
        and row["certified"] is True
    )


def weak_compositions(total: int, parts: int):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for suffix in weak_compositions(total - first, parts - 1):
            yield (first,) + suffix


def scores(costs: tuple[int, ...]) -> tuple[int, ...]:
    result = []
    for index in range(1 << len(costs)):
        result.append(
            sum(
                cost
                for position, cost in enumerate(reversed(costs))
                if index & (1 << position)
            )
        )
    return tuple(result)


def replay_grid() -> dict[str, object]:
    rows = []
    pair_count = 0
    for depth in (1, 2):
        for costs in combinations_with_replacement((1, 2, 3), depth):
            total = sum(costs)
            word_costs = scores(costs)
            distributions = tuple(weak_compositions(total, len(word_costs)))
            for budget in range(total + 1):
                zero = tuple(
                    distribution
                    for distribution in distributions
                    if sum(
                        units * cost
                        for units, cost in zip(distribution, word_costs)
                    )
                    <= budget * total
                )
                one = tuple(
                    distribution
                    for distribution in distributions
                    if sum(
                        units * (total - cost)
                        for units, cost in zip(distribution, word_costs)
                    )
                    <= budget * total
                )
                minimum = min(
                    Q(
                        sum(abs(a - b) for a, b in zip(left, right)),
                        2 * total,
                    )
                    for left in zero
                    for right in one
                )
                pairs = len(zero) * len(one)
                pair_count += pairs
                rows.append(
                    {
                        "costs": list(costs),
                        "budget": budget,
                        "probability_denominator": total,
                        "truth_zero_distributions": len(zero),
                        "truth_one_distributions": len(one),
                        "distribution_pairs_checked": pairs,
                        "minimum_grid_total_variation": text(minimum),
                        "claimed_value": text(formula(total, Q(budget))),
                        "matches": minimum == formula(total, Q(budget)),
                    }
                )
    return {
        "case_count": len(rows),
        "distribution_pairs_checked": pair_count,
        "rows": rows,
        "all_grid_optima_match": all(row["matches"] for row in rows),
    }


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))
    rows = result.get("expected_rows", [])
    parent_rows = parent["weighted_rows"]
    expected_keys = [
        (tuple(row["costs"]), str(row["budget"]))
        for row in parent_rows
    ]
    grid = replay_grid()
    recorded_grid = result.get("small_distribution_grid_exhaustion", {})
    parent_order_and_inequality = len(rows) == len(parent_rows)
    strict = 0
    for expected, hard in zip(rows, parent_rows):
        expected_value = Q(expected["value"])
        hard_value = Q(hard["value"])
        parent_order_and_inequality = parent_order_and_inequality and (
            expected["costs"] == hard["costs"]
            and Q(expected["expected_budget"]) == hard["budget"]
            and expected["parent_hard_budget_value"] == hard["value"]
            and expected_value <= hard_value
            and expected["expected_value_no_greater_than_hard_value"] is True
        )
        strict += expected_value < hard_value
    paired = result.get("paired_convexification_witness", {})
    fractional = result.get("fractional_budget_witness", {})
    large = result.get("large_succinct_witness", {})
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version") == "asmp3_expected_weighted_noise_v1_7"
            and result.get("status") == "exact_expected_budget_tv_phase"
            and result.get("parent_result")
            == "ASMP-3-WEIGHTED-NOISE-SUBSET-SUM-v1.6"
            and result.get("certified") is True
            and "expected positive-integer" in result.get("claim_boundary", "")
        ),
        "V1_complete_parent_registry_reconstructed": (
            len(rows) == 2729
            and [(tuple(row["costs"]), row["expected_budget"]) for row in rows]
            == expected_keys
        ),
        "V2_all_continuum_saddle_fields_reconstructed": all(
            reconstruct_row(row) for row in rows
        ),
        "V3_expected_constraint_order_and_strict_cases_reconstructed": (
            parent_order_and_inequality
            and strict == len(result.get("strict_hard_expected_separations", []))
            and strict == 1139
        ),
        "V4_small_rational_distribution_grid_replayed": (
            grid["case_count"] == recorded_grid.get("case_count") == 39
            and grid["distribution_pairs_checked"]
            == recorded_grid.get("distribution_pairs_checked")
            == 35808
            and grid["rows"] == recorded_grid.get("rows")
            and grid["all_grid_optima_match"] is True
        ),
        "V5_convexification_pair_and_fractional_case_exact": (
            paired.get("expected_value_a") == paired.get("expected_value_b") == "0"
            and paired.get("parent_hard_value_a") == "1"
            and paired.get("parent_hard_value_b") == "0"
            and Q(fractional.get("expected_budget")) == Q(3, 2)
            and Q(fractional.get("value")) == Q(5, 8)
            and reconstruct_row(fractional)
        ),
        "V6_large_succinct_formula_reconstructed": (
            large.get("depth") == 32
            and large.get("total_cost") == (1 << 32) - 1
            and Q(large.get("expected_budget")) == Q((1 << 32) - 1, 3)
            and Q(large.get("value")) == Q(1, 3)
            and large.get("response_words_enumerated") == 0
        ),
        "V7_producer_gates_all_true": (
            len(result.get("gates", {})) == 9 and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_expected_weighted_noise_verification_v1_7",
        "checker": "clean_room_tv_saddle_parent_order_and_grid_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates separate per-truth expected flip-cost "
            "constraints and terminal verification. It does not identify "
            "almost-sure, tail-risk, coupled, or path-dependent noise games."
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
        raise SystemExit(f"expected-weighted-noise verification failed: {failed}")
    print(
        "ASMP-3 expected-weighted-noise independent verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
