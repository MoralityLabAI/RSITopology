from __future__ import annotations

import json
from fractions import Fraction
from math import comb
from pathlib import Path


Q = Fraction
HERE = Path(__file__).resolve().parent
PARENT_ARTIFACT = (
    HERE.parent
    / "asmp3_expected_weighted_noise_v1_7"
    / "artifacts"
    / "expected_weighted_noise_v1_7.json"
)
ETA_REGISTRY = (Q(1, 100), Q(1, 10), Q(1, 5), Q(1, 4), Q(1, 3), Q(2, 5), Q(49, 100))


def qstr(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def validate(depth: int, eta: Q) -> None:
    if not isinstance(depth, int) or depth < 1:
        raise ValueError("depth must be a positive integer")
    if eta < 0 or eta > Q(1, 2):
        raise ValueError("eta must lie in [0,1/2]")


def binomial_probability(depth: int, errors: int, eta: Q) -> Q:
    return Q(comb(depth, errors)) * eta**errors * (Q(1) - eta) ** (depth - errors)


def bayes_error(depth: int, eta: Q | int) -> Q:
    eta = Q(eta)
    validate(depth, eta)
    strict_error = sum(
        (
            binomial_probability(depth, errors, eta)
            for errors in range(depth // 2 + 1, depth + 1)
        ),
        Q(0),
    )
    tie_error = (
        binomial_probability(depth, depth // 2, eta) / 2
        if depth % 2 == 0
        else Q(0)
    )
    return strict_error + tie_error


def verifier_value(depth: int, eta: Q | int) -> Q:
    return Q(1) - 2 * bayes_error(depth, eta)


def odd_step_gain(m: int, eta: Q | int) -> Q:
    eta = Q(eta)
    if m < 1 or eta < 0 or eta > Q(1, 2):
        raise ValueError("invalid odd-step parameters")
    return Q(comb(2 * m, m), 2) * (eta * (1 - eta)) ** m * (1 - 2 * eta)


def response_probability(word: str, truth: int, eta: Q) -> Q:
    if truth not in (0, 1) or any(bit not in "01" for bit in word):
        raise ValueError("invalid truth or response word")
    errors = sum(int(bit) != truth for bit in word)
    return eta**errors * (Q(1) - eta) ** (len(word) - errors)


def enumerated_total_variation(depth: int, eta: Q | int) -> Q:
    eta = Q(eta)
    validate(depth, eta)
    total = Q(0)
    for index in range(1 << depth):
        word = format(index, f"0{depth}b")
        total += abs(
            response_probability(word, 0, eta)
            - response_probability(word, 1, eta)
        )
    return total / 2


def amplification_row(depth: int, eta: Q | int) -> dict[str, object]:
    eta = Q(eta)
    validate(depth, eta)
    error = bayes_error(depth, eta)
    value = Q(1) - 2 * error
    persistent_value = Q(1) - 2 * eta
    base_squared = 4 * eta * (1 - eta)
    squared_error_bound = Q(1, 4) * base_squared**depth
    tie_probability = (
        binomial_probability(depth, depth // 2, eta)
        if depth % 2 == 0
        else Q(0)
    )
    return {
        "depth": depth,
        "eta": qstr(eta),
        "noise_class": "iid_Bernoulli_rate_p_with_0_le_p_le_eta",
        "aggregator": "majority_with_uniform_tie_break",
        "bayes_error": qstr(error),
        "value": qstr(value),
        "tie_probability_at_worst_rate": qstr(tie_probability),
        "persistent_correlated_error": qstr(eta),
        "persistent_correlated_value": qstr(persistent_value),
        "expected_budget_adversarial_value": qstr(persistent_value),
        "independence_value_gain": qstr(value - persistent_value),
        "bhattacharyya_base_squared": qstr(base_squared),
        "bayes_error_squared": qstr(error * error),
        "bhattacharyya_squared_upper_bound": qstr(squared_error_bound),
        "bound_holds": error * error <= squared_error_bound,
        "certified": (
            0 <= error <= Q(1, 2)
            and value == Q(1) - 2 * error
            and value >= persistent_value
            and error * error <= squared_error_bound
            and (depth < 3 or eta in (0, Q(1, 2)) or value > persistent_value)
        ),
    }


def word_enumeration_audit() -> list[dict[str, object]]:
    rows = []
    for eta in (Q(1, 5), Q(1, 3), Q(2, 5)):
        for depth in range(1, 11):
            tv = enumerated_total_variation(depth, eta)
            formula_value = verifier_value(depth, eta)
            rows.append(
                {
                    "depth": depth,
                    "eta": qstr(eta),
                    "words_enumerated": 1 << depth,
                    "enumerated_total_variation": qstr(tv),
                    "binomial_formula_value": qstr(formula_value),
                    "matches": tv == formula_value,
                }
            )
    return rows


def rate_adversary_audit() -> list[dict[str, object]]:
    rows = []
    for eta in ETA_REGISTRY:
        rates = tuple(eta * step / 8 for step in range(9))
        for depth in range(1, 17):
            errors = tuple(bayes_error(depth, rate) for rate in rates)
            rows.append(
                {
                    "depth": depth,
                    "eta": qstr(eta),
                    "rates_checked": [qstr(rate) for rate in rates],
                    "errors": [qstr(error) for error in errors],
                    "nondecreasing": all(
                        left <= right for left, right in zip(errors, errors[1:])
                    ),
                    "worst_rate_is_eta": errors[-1] == bayes_error(depth, eta),
                }
            )
    return rows


def recurrence_audit() -> list[dict[str, object]]:
    rows = []
    for eta in ETA_REGISTRY:
        for m in range(1, 32):
            even_error = bayes_error(2 * m, eta)
            prior_odd_error = bayes_error(2 * m - 1, eta)
            next_odd_error = bayes_error(2 * m + 1, eta)
            gain = odd_step_gain(m, eta)
            rows.append(
                {
                    "eta": qstr(eta),
                    "m": m,
                    "even_equals_prior_odd": even_error == prior_odd_error,
                    "odd_step_gain": qstr(even_error - next_odd_error),
                    "odd_step_gain_formula": qstr(gain),
                    "gain_formula_matches": even_error - next_odd_error == gain,
                    "gain_strictly_positive": gain > 0,
                }
            )
    return rows


def build_result() -> dict[str, object]:
    parent = json.loads(PARENT_ARTIFACT.read_text(encoding="utf-8"))
    rows = [
        amplification_row(depth, eta)
        for eta in ETA_REGISTRY
        for depth in range(1, 65)
    ]
    enumeration = word_enumeration_audit()
    rates = rate_adversary_audit()
    recurrences = recurrence_audit()
    witness = amplification_row(9, Q(1, 5))
    witness["persistent_law"] = (
        "one latent Bernoulli(eta) flip copied to every replication"
    )
    asymptotic = amplification_row(64, Q(1, 5))
    parent_formula = parent["theorem"]["value"]
    gates = {
        "I0_registry_complete": (
            len(rows) == len(ETA_REGISTRY) * 64
            and [(row["eta"], row["depth"]) for row in rows]
            == [
                (qstr(eta), depth)
                for eta in ETA_REGISTRY
                for depth in range(1, 65)
            ]
        ),
        "I1_all_exact_binomial_rows_certified": all(row["certified"] for row in rows),
        "I2_word_level_tv_enumeration_matches": (
            len(enumeration) == 30 and all(row["matches"] for row in enumeration)
        ),
        "I3_adversarial_iid_rate_is_worst_at_eta": (
            len(rates) == len(ETA_REGISTRY) * 16
            and all(row["nondecreasing"] and row["worst_rate_is_eta"] for row in rates)
        ),
        "I4_even_odd_recurrence_and_strict_gain_exact": (
            len(recurrences) == len(ETA_REGISTRY) * 31
            and all(
                row["even_equals_prior_odd"]
                and row["gain_formula_matches"]
                and row["gain_strictly_positive"]
                for row in recurrences
            )
        ),
        "I5_bhattacharyya_exponential_bound_exact": all(
            row["bound_holds"]
            and Q(row["bhattacharyya_base_squared"]) < 1
            for row in rows
        ),
        "I6_independence_never_worse_and_strict_after_two": all(
            Q(row["independence_value_gain"]) == 0
            if row["depth"] <= 2
            else Q(row["independence_value_gain"]) > 0
            for row in rows
        ),
        "I7_correlation_class_separation_witnessed": (
            Q(witness["value"]) > Q(witness["persistent_correlated_value"])
            and witness["persistent_correlated_value"] == "3/5"
        ),
        "I8_expected_budget_parent_formula_matches_persistent_baseline": (
            parent_formula == "max(0,1-2B/C)"
            and all(
                row["expected_budget_adversarial_value"]
                == row["persistent_correlated_value"]
                for row in rows
            )
            and Q(asymptotic["value"]) > Q(999, 1000)
        ),
    }
    return {
        "schema_version": "asmp3_independent_noise_amplification_v1_8",
        "experiment_id": "ASMP-3-INDEPENDENT-NOISE-AMPLIFICATION-v1.8",
        "status": "exact_iid_replication_amplification_profile",
        "parent_result": "ASMP-3-EXPECTED-WEIGHTED-NOISE-v1.7",
        "theorem": {
            "noise_class": "iid Bernoulli error rate p chosen adversarially in [0,eta]",
            "optimal_aggregator": "majority with uniform tie break",
            "bayes_error": "upper binomial tail plus half the even-depth tie mass",
            "value": "1-2*bayes_error(d,eta)",
            "persistent_baseline": "1-2eta",
            "exponential_certificate": "error^2 <= (1/4)(4eta(1-eta))^d",
        },
        "registry_parameters": {
            "depths": [1, 64],
            "etas": [qstr(eta) for eta in ETA_REGISTRY],
            "row_count": len(rows),
        },
        "amplification_rows": rows,
        "word_enumeration_audit": enumeration,
        "rate_adversary_audit": rates,
        "parity_recurrence_audit": recurrences,
        "correlation_class_separation_witness": witness,
        "depth_64_eta_one_fifth_witness": asymptotic,
        "gates": gates,
        "certified": all(gates.values()),
        "claim_boundary": (
            "The amplification theorem requires conditionally independent, "
            "identically distributed replication errors with one rate p<=eta, "
            "truth-independent error bits, registered meaning-preserving copies, "
            "and terminal observation of every response. Marginal accuracy alone "
            "does not imply this profile."
        ),
    }
