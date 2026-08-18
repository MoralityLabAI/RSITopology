from __future__ import annotations

import json
from fractions import Fraction
from math import comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "artifacts" / "independent_noise_amplification_v1_8.json"
OUTPUT_PATH = (
    HERE / "artifacts" / "independent_noise_amplification_verification_v1_8.json"
)
PARENT_PATH = (
    HERE.parent
    / "asmp3_expected_weighted_noise_v1_7"
    / "artifacts"
    / "expected_weighted_noise_v1_7.json"
)
ETAS = (Q(1, 100), Q(1, 10), Q(1, 5), Q(1, 4), Q(1, 3), Q(2, 5), Q(49, 100))


def text(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def probability(depth: int, errors: int, eta: Q) -> Q:
    return Q(comb(depth, errors)) * eta**errors * (1 - eta) ** (depth - errors)


def error_formula(depth: int, eta: Q) -> Q:
    result = sum(
        (probability(depth, errors, eta) for errors in range(depth // 2 + 1, depth + 1)),
        Q(0),
    )
    if depth % 2 == 0:
        result += probability(depth, depth // 2, eta) / 2
    return result


def word_tv(depth: int, eta: Q) -> Q:
    total = Q(0)
    for index in range(1 << depth):
        weight = index.bit_count()
        p0 = eta**weight * (1 - eta) ** (depth - weight)
        p1 = eta ** (depth - weight) * (1 - eta) ** weight
        total += abs(p0 - p1)
    return total / 2


def reconstruct_row(row: dict[str, object]) -> bool:
    depth = int(row["depth"])
    eta = Q(row["eta"])
    error = error_formula(depth, eta)
    value = 1 - 2 * error
    baseline = 1 - 2 * eta
    tie = probability(depth, depth // 2, eta) if depth % 2 == 0 else Q(0)
    base_squared = 4 * eta * (1 - eta)
    upper = Q(1, 4) * base_squared**depth
    return (
        row["noise_class"] == "iid_Bernoulli_rate_p_with_0_le_p_le_eta"
        and row["aggregator"] == "majority_with_uniform_tie_break"
        and Q(row["bayes_error"]) == error
        and Q(row["value"]) == value
        and Q(row["tie_probability_at_worst_rate"]) == tie
        and Q(row["persistent_correlated_error"]) == eta
        and Q(row["persistent_correlated_value"]) == baseline
        and Q(row["expected_budget_adversarial_value"]) == baseline
        and Q(row["independence_value_gain"]) == value - baseline
        and Q(row["bhattacharyya_base_squared"]) == base_squared
        and Q(row["bayes_error_squared"]) == error * error
        and Q(row["bhattacharyya_squared_upper_bound"]) == upper
        and row["bound_holds"] is (error * error <= upper)
        and row["certified"] is True
    )


def verify() -> dict[str, object]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    parent = json.loads(PARENT_PATH.read_text(encoding="utf-8"))
    rows = result.get("amplification_rows", [])
    expected_keys = [(text(eta), depth) for eta in ETAS for depth in range(1, 65)]

    enumeration = result.get("word_enumeration_audit", [])
    enumeration_matches = len(enumeration) == 30
    for row in enumeration:
        depth = int(row["depth"])
        eta = Q(row["eta"])
        tv = word_tv(depth, eta)
        enumeration_matches = enumeration_matches and (
            int(row["words_enumerated"]) == 1 << depth
            and Q(row["enumerated_total_variation"]) == tv
            and Q(row["binomial_formula_value"]) == 1 - 2 * error_formula(depth, eta)
            and row["matches"] is (tv == 1 - 2 * error_formula(depth, eta))
        )

    rates = result.get("rate_adversary_audit", [])
    rates_match = len(rates) == len(ETAS) * 16
    for row in rates:
        depth = int(row["depth"])
        eta = Q(row["eta"])
        sampled = tuple(eta * step / 8 for step in range(9))
        errors = tuple(error_formula(depth, rate) for rate in sampled)
        rates_match = rates_match and (
            row["rates_checked"] == [text(rate) for rate in sampled]
            and row["errors"] == [text(error) for error in errors]
            and row["nondecreasing"]
            is all(left <= right for left, right in zip(errors, errors[1:]))
            and row["worst_rate_is_eta"] is (errors[-1] == error_formula(depth, eta))
        )

    recurrences = result.get("parity_recurrence_audit", [])
    recurrences_match = len(recurrences) == len(ETAS) * 31
    for row in recurrences:
        eta = Q(row["eta"])
        m = int(row["m"])
        even = error_formula(2 * m, eta)
        prior = error_formula(2 * m - 1, eta)
        following = error_formula(2 * m + 1, eta)
        gain = Q(comb(2 * m, m), 2) * (eta * (1 - eta)) ** m * (1 - 2 * eta)
        recurrences_match = recurrences_match and (
            row["even_equals_prior_odd"] is (even == prior)
            and Q(row["odd_step_gain"]) == even - following
            and Q(row["odd_step_gain_formula"]) == gain
            and row["gain_formula_matches"] is (even - following == gain)
            and row["gain_strictly_positive"] is (gain > 0)
        )

    witness = result.get("correlation_class_separation_witness", {})
    depth64 = result.get("depth_64_eta_one_fifth_witness", {})
    checks = {
        "V0_schema_parent_status_boundary": (
            result.get("schema_version")
            == "asmp3_independent_noise_amplification_v1_8"
            and result.get("status") == "exact_iid_replication_amplification_profile"
            and result.get("parent_result") == "ASMP-3-EXPECTED-WEIGHTED-NOISE-v1.7"
            and result.get("certified") is True
            and "Marginal accuracy alone" in result.get("claim_boundary", "")
        ),
        "V1_complete_448_row_registry_reconstructed": (
            len(rows) == 448
            and [(row["eta"], row["depth"]) for row in rows] == expected_keys
        ),
        "V2_all_binomial_tv_and_bound_fields_reconstructed": all(
            reconstruct_row(row) for row in rows
        ),
        "V3_word_level_total_variation_replayed": enumeration_matches,
        "V4_rate_adversary_monotonicity_grid_replayed": rates_match,
        "V5_even_odd_recurrence_reconstructed": recurrences_match,
        "V6_correlation_and_parent_comparison_exact": (
            witness.get("depth") == 9
            and Q(witness.get("eta")) == Q(1, 5)
            and Q(witness.get("value")) == Q(375327, 390625)
            and Q(witness.get("persistent_correlated_value")) == Q(3, 5)
            and parent["theorem"]["value"] == "max(0,1-2B/C)"
            and Q(depth64.get("value")) > Q(999, 1000)
        ),
        "V7_producer_gates_all_true": (
            len(result.get("gates", {})) == 9 and all(result["gates"].values())
        ),
    }
    return {
        "schema_version": "asmp3_independent_noise_amplification_verification_v1_8",
        "checker": "clean_room_binomial_tv_rate_and_recurrence_reconstruction",
        "check_count": len(checks),
        "checks": checks,
        "passed": all(checks.values()),
        "claim_boundary": (
            "This checker validates conditionally i.i.d. truth-independent "
            "replication errors with one adversarial rate p<=eta. It does not "
            "infer independence from marginal error bounds."
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
        raise SystemExit(f"independent-noise verification failed: {failed}")
    print(
        "ASMP-3 independent-noise verification passed: "
        f"{result['check_count']}/{result['check_count']}"
    )


if __name__ == "__main__":
    main()
