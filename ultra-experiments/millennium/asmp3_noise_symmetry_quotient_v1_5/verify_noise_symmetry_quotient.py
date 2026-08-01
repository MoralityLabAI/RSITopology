from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "noise_symmetry_quotient_v1_5.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "noise_symmetry_quotient_verification_v1_5.json"
)


def words(depth: int) -> tuple[str, ...]:
    return tuple(format(index, f"0{depth}b") for index in range(1 << depth))


def languages(depth: int, budget: int) -> tuple[tuple[str, ...], tuple[str, ...]]:
    universe = words(depth)
    return (
        tuple(word for word in universe if word.count("1") <= budget),
        tuple(word for word in universe if word.count("0") <= budget),
    )


def worst_value(rule: dict[str, Q], depth: int, budget: int) -> Q:
    zero, one = languages(depth, budget)
    zero_value = min(1 - 2 * rule[word] for word in zero)
    one_value = min(2 * rule[word] - 1 for word in one)
    return (zero_value + one_value) / 2


def orbit_average(rule: dict[str, Q], depth: int) -> dict[str, Q]:
    averages: dict[int, Q] = {}
    for weight in range(depth + 1):
        orbit = [value for word, value in rule.items() if word.count("1") == weight]
        averages[weight] = sum(orbit, Q(0)) / len(orbit)
    return {word: averages[word.count("1")] for word in rule}


def exhaustive_symmetry_check(depth: int, budget: int) -> tuple[int, Q, bool]:
    universe = words(depth)
    checked = 0
    minimum: Q | None = None
    passed = True
    for choices in product((Q(0), Q(1)), repeat=len(universe)):
        rule = dict(zip(universe, choices))
        improvement = (
            worst_value(orbit_average(rule, depth), depth, budget)
            - worst_value(rule, depth, budget)
        )
        minimum = improvement if minimum is None else min(minimum, improvement)
        passed = passed and improvement >= 0
        checked += 1
    return checked, minimum or Q(0), passed


def check_quotient_row(row: dict[str, object]) -> bool:
    depth = int(row["depth"])
    budget = int(row["flip_budget"])
    separable = 2 * budget < depth
    zero_weights = list(range(budget + 1))
    one_weights = list(range(depth - budget, depth + 1))
    overlap = set(zero_weights) & set(one_weights)
    language_count = sum(comb(depth, flips) for flips in range(budget + 1))
    full_prefix_count = sum(
        sum(comb(round_index, flips) for flips in range(min(budget, round_index) + 1))
        for round_index in range(depth)
    )
    quotient_count = sum(min(budget, round_index) + 1 for round_index in range(depth))
    quotient_formula = (budget + 1) * (depth - budget) + budget * (budget + 1) // 2
    overlap_formula = max(0, min(depth, budget) - max(0, depth - budget) + 1)
    return (
        row["phase"] == ("separable" if separable else "overlap")
        and row["value"] == ("1" if separable else "0")
        and row["truth_zero_weight_range"] == zero_weights
        and row["truth_one_weight_range"] == one_weights
        and int(row["overlap_weight_count"]) == len(overlap) == overlap_formula
        and int(row["overlap_weight_count_formula"]) == overlap_formula
        and int(row["full_terminal_words_per_truth"]) == language_count
        and int(row["full_prefix_controller_nodes_per_truth"]) == full_prefix_count
        and int(row["quotient_controller_states_per_truth"])
        == quotient_count
        == quotient_formula
        and int(row["quotient_terminal_states_per_truth"]) == budget + 1
        and int(row["quotient_controller_formula"]) == quotient_formula
        and int(row["full_to_quotient_terminal_factor_numerator"])
        == language_count
        and int(row["full_to_quotient_terminal_factor_denominator"])
        == budget + 1
        and row["max_strategy"]
        == (
            "guess_by_disjoint_weight_range"
            if separable
            else "uniform_guess_at_every_weight"
        )
        and row["min_strategy"]
        == (
            "any_legal_controller"
            if separable
            else f"emit_common_weight_{depth - budget}_under_both_truths"
        )
        and row["certified"] is True
    )


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    rows = result.get("quotient_rows", [])
    expected_keys = [
        (depth, budget)
        for depth in range(1, 33)
        for budget in range(depth + 1)
    ]
    symmetry_rows = result.get("symmetry_exhaustion_rows", [])
    reconstructed_symmetry = {}
    for depth in range(1, 4):
        for budget in range(depth + 1):
            reconstructed_symmetry[(depth, budget)] = exhaustive_symmetry_check(
                depth, budget
            )
    symmetry_matches = len(symmetry_rows) == 9
    for row in symmetry_rows:
        key = (int(row["depth"]), int(row["flip_budget"]))
        if key not in reconstructed_symmetry:
            symmetry_matches = False
            continue
        checked, minimum, passed = reconstructed_symmetry[key]
        symmetry_matches = symmetry_matches and (
            int(row["deterministic_rules_checked"]) == checked
            and int(row["expected_rule_count"]) == checked
            and Fraction(row["minimum_symmetrization_improvement"]) == minimum
            and row["symmetrization_never_hurts"] is passed is True
        )

    parent_checks = result.get("parent_cross_checks", [])
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version") == "asmp3_noise_symmetry_quotient_v1_5"
            and result.get("status") == "exact_permutation_quotient_phase"
            and result.get("parent_result") == "ASMP-3-ADAPTIVE-NOISE-SEQUENCE-v1.4"
            and result.get("certified") is True
            and "Position-dependent" in result.get("claim_boundary", "")
        ),
        "V1_all_560_quotient_cases_present_in_order": (
            [(row["depth"], row["flip_budget"]) for row in rows] == expected_keys
        ),
        "V2_all_formulas_and_saddles_reconstructed": (
            len(rows) == len(expected_keys) and all(check_quotient_row(row) for row in rows)
        ),
        "V3_symmetrization_exhaustion_independently_replayed": symmetry_matches,
        "V4_parent_cross_checks_complete": (
            len(parent_checks) == 27
            and [(row["depth"], row["flip_budget"]) for row in parent_checks]
            == [(depth, budget) for depth in range(1, 7) for budget in range(depth + 1)]
            and all(
                row["value_matches"]
                and row["language_size_matches"]
                and row["prefix_state_count_matches"]
                for row in parent_checks
            )
        ),
        "V5_exponential_compression_witness_reconstructed": (
            next(
                row
                for row in rows
                if row["depth"] == 32 and row["flip_budget"] == 32
            )["full_terminal_words_per_truth"]
            == 1 << 32
            and next(
                row
                for row in rows
                if row["depth"] == 32 and row["flip_budget"] == 32
            )["quotient_terminal_states_per_truth"]
            == 33
        ),
        "V6_producer_gates_all_true": (
            len(result.get("gates", {})) == 7 and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_noise_symmetry_quotient_verification_v1_5",
        "checker": "clean_room_orbit_formula_and_small_rule_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker establishes the coordinate-permutation quotient for "
            "the registered hard Hamming-budget game only; it does not certify "
            "position-dependent observations, costs, or noise constraints."
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
        raise SystemExit(f"noise-symmetry verification failed: {failed}")
    print(
        "ASMP-3 noise-symmetry independent verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
