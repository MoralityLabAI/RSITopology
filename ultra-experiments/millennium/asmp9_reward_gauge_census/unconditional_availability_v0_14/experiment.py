from __future__ import annotations

import itertools
import math
from collections import defaultdict
from fractions import Fraction
from typing import Any, Iterable


Outcome = tuple[int, ...]


def parse_fraction(value: str | int | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    numerator, denominator = value.split("/")
    return Fraction(int(numerator), int(denominator))


def fraction_record(value: Fraction) -> dict[str, Any]:
    return {
        "fraction": f"{value.numerator}/{value.denominator}",
        "decimal": float(value),
        "numerator_bit_length": abs(value.numerator).bit_length(),
        "denominator_bit_length": value.denominator.bit_length(),
    }


def all_outcomes(cycle_length: int, trials_per_edge: int) -> Iterable[Outcome]:
    return itertools.product(
        range(trials_per_edge + 1), repeat=cycle_length
    )


def canonical_fiber_key(outcome: Outcome) -> Outcome:
    minimum = min(outcome)
    return tuple(value - minimum for value in outcome)


def fiber_members(key: Outcome, trials_per_edge: int) -> list[Outcome]:
    if min(key) != 0:
        raise ValueError("fiber key must have minimum zero")
    maximum = max(key)
    if maximum > trials_per_edge:
        raise ValueError("fiber key exceeds trial range")
    return [
        tuple(value + shift for value in key)
        for shift in range(trials_per_edge - maximum + 1)
    ]


def base_measure(outcome: Outcome, trials_per_edge: int) -> int:
    result = 1
    for value in outcome:
        result *= math.comb(trials_per_edge, value)
    return result


def outcome_probability(
    outcome: Outcome,
    trials_per_edge: int,
    edge_odds: tuple[Fraction, ...],
) -> Fraction:
    if len(outcome) != len(edge_odds):
        raise ValueError("outcome/odds dimension mismatch")
    probability = Fraction(1)
    for value, odds in zip(outcome, edge_odds, strict=True):
        if odds <= 0:
            raise ValueError("odds must be positive")
        probability *= (
            Fraction(math.comb(trials_per_edge, value))
            * odds**value
            / (1 + odds) ** trials_per_edge
        )
    return probability


def availability_formula(
    trials_per_edge: int,
    edge_odds: tuple[Fraction, ...],
) -> Fraction:
    no_zero = Fraction(1)
    no_full = Fraction(1)
    all_interior = Fraction(1)
    for odds in edge_odds:
        probability_zero = (
            Fraction(1, 1) / (1 + odds)
        ) ** trials_per_edge
        probability_full = (
            odds / (1 + odds)
        ) ** trials_per_edge
        no_zero *= 1 - probability_zero
        no_full *= 1 - probability_full
        all_interior *= 1 - probability_zero - probability_full
    return no_zero + no_full - all_interior


def exact_conditional_upper_test(
    key: Outcome,
    trials_per_edge: int,
    odds_ratio: Fraction,
    alpha: Fraction,
) -> dict[str, Any]:
    if odds_ratio < 1:
        raise ValueError("odds ratio must be at least one")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0,1)")
    members = fiber_members(key, trials_per_edge)
    null_weights = [
        Fraction(base_measure(member, trials_per_edge))
        for member in members
    ]
    alternative_weights = [
        weight * odds_ratio ** member[0]
        for member, weight in zip(members, null_weights, strict=True)
    ]
    null_total = sum(null_weights, Fraction(0))
    alternative_total = sum(alternative_weights, Fraction(0))
    target = alpha * null_total
    tail = Fraction(0)
    boundary_index = -1
    boundary_randomization = Fraction(0)
    for index in range(len(members) - 1, -1, -1):
        weight = null_weights[index]
        if tail <= target <= tail + weight:
            boundary_index = index
            boundary_randomization = (target - tail) / weight
            break
        tail += weight
    if boundary_index < 0:
        raise AssertionError("exact conditional boundary not found")
    rejection_probabilities = [
        (
            Fraction(1)
            if index > boundary_index
            else boundary_randomization
            if index == boundary_index
            else Fraction(0)
        )
        for index in range(len(members))
    ]
    null_size = (
        sum(
            probability * weight
            for probability, weight in zip(
                rejection_probabilities, null_weights, strict=True
            )
        )
        / null_total
    )
    alternative_power = (
        sum(
            probability * weight
            for probability, weight in zip(
                rejection_probabilities, alternative_weights, strict=True
            )
        )
        / alternative_total
    )
    return {
        "member_count": len(members),
        "informative": len(members) >= 2,
        "boundary_outcome": members[boundary_index],
        "boundary_randomization": boundary_randomization,
        "null_size": null_size,
        "alternative_power": alternative_power,
    }


def drift_odds(
    cycle_length: int, nuisance_ratio: Fraction
) -> tuple[Fraction, ...]:
    if cycle_length < 2 or nuisance_ratio <= 0:
        raise ValueError("invalid cycle or nuisance ratio")
    odds = (
        nuisance_ratio ** (cycle_length - 1),
        *((Fraction(1, 1) / nuisance_ratio,) * (cycle_length - 1)),
    )
    product = math.prod(odds, start=Fraction(1))
    if product != 1:
        raise AssertionError("drift odds are not a scalar gradient")
    return odds


def run_cell(
    cycle_length: int,
    trials_per_edge: int,
    odds_ratio: Fraction,
    nuisance_ratio: Fraction,
    alpha: Fraction,
) -> dict[str, Any]:
    scalar_odds = drift_odds(cycle_length, nuisance_ratio)
    alternative_odds = (
        scalar_odds[0] * odds_ratio,
        *scalar_odds[1:],
    )
    fibers: dict[Outcome, list[Outcome]] = defaultdict(list)
    for outcome in all_outcomes(cycle_length, trials_per_edge):
        fibers[canonical_fiber_key(outcome)].append(outcome)

    null_mass: dict[Outcome, Fraction] = {}
    alternative_mass: dict[Outcome, Fraction] = {}
    tests: dict[Outcome, dict[str, Any]] = {}
    for key, outcomes in fibers.items():
        expected = fiber_members(key, trials_per_edge)
        if sorted(outcomes) != sorted(expected):
            raise AssertionError("canonical fiber partition mismatch")
        null_mass[key] = sum(
            (
                outcome_probability(
                    outcome, trials_per_edge, scalar_odds
                )
                for outcome in outcomes
            ),
            Fraction(0),
        )
        alternative_mass[key] = sum(
            (
                outcome_probability(
                    outcome, trials_per_edge, alternative_odds
                )
                for outcome in outcomes
            ),
            Fraction(0),
        )
        tests[key] = exact_conditional_upper_test(
            key, trials_per_edge, odds_ratio, alpha
        )

    if sum(null_mass.values(), Fraction(0)) != 1:
        raise AssertionError("null mass does not normalize")
    if sum(alternative_mass.values(), Fraction(0)) != 1:
        raise AssertionError("alternative mass does not normalize")

    informative_keys = {
        key for key, test in tests.items() if test["informative"]
    }
    availability_null = sum(
        (null_mass[key] for key in informative_keys), Fraction(0)
    )
    availability_alternative = sum(
        (alternative_mass[key] for key in informative_keys), Fraction(0)
    )
    formula_null = availability_formula(trials_per_edge, scalar_odds)
    formula_alternative = availability_formula(
        trials_per_edge, alternative_odds
    )

    size_all = sum(
        (
            null_mass[key] * tests[key]["null_size"]
            for key in fibers
        ),
        Fraction(0),
    )
    power_all = sum(
        (
            alternative_mass[key] * tests[key]["alternative_power"]
            for key in fibers
        ),
        Fraction(0),
    )
    size_gated = sum(
        (
            null_mass[key] * tests[key]["null_size"]
            for key in informative_keys
        ),
        Fraction(0),
    )
    power_gated = sum(
        (
            alternative_mass[key] * tests[key]["alternative_power"]
            for key in informative_keys
        ),
        Fraction(0),
    )
    excess_decomposition = sum(
        (
            alternative_mass[key]
            * (tests[key]["alternative_power"] - alpha)
            for key in informative_keys
        ),
        Fraction(0),
    )
    excess_power = power_all - alpha
    upper_bound = (1 - alpha) * availability_alternative
    alternative_probabilities = tuple(
        odds / (1 + odds) for odds in alternative_odds
    )
    epsilon_actual = min(
        min(probability, 1 - probability)
        for probability in alternative_probabilities
    )
    availability_interior_lower_bound = (
        1 - (1 - epsilon_actual) ** trials_per_edge
    ) ** cycle_length
    informative_power_gains = [
        tests[key]["alternative_power"] - alpha
        for key in informative_keys
    ]
    minimum_informative_power_gain = min(
        informative_power_gains, default=Fraction(0)
    )
    excess_interior_lower_bound = (
        availability_interior_lower_bound
        * minimum_informative_power_gain
    )

    return {
        "cycle_length": cycle_length,
        "trials_per_edge": trials_per_edge,
        "odds_ratio": f"{odds_ratio.numerator}/{odds_ratio.denominator}",
        "nuisance_ratio": (
            f"{nuisance_ratio.numerator}/{nuisance_ratio.denominator}"
        ),
        "fiber_count": len(fibers),
        "informative_fiber_count": len(informative_keys),
        "null_mass_normalized": (
            sum(null_mass.values(), Fraction(0)) == 1
        ),
        "alternative_mass_normalized": (
            sum(alternative_mass.values(), Fraction(0)) == 1
        ),
        "availability_null": fraction_record(availability_null),
        "availability_alternative": fraction_record(
            availability_alternative
        ),
        "availability_formula_null": fraction_record(formula_null),
        "availability_formula_alternative": fraction_record(
            formula_alternative
        ),
        "availability_formula_matches": (
            availability_null == formula_null
            and availability_alternative == formula_alternative
        ),
        "unconditional_size_all": fraction_record(size_all),
        "unconditional_power_all": fraction_record(power_all),
        "unconditional_size_gated": fraction_record(size_gated),
        "unconditional_power_gated": fraction_record(power_gated),
        "excess_power": fraction_record(excess_power),
        "excess_decomposition": fraction_record(excess_decomposition),
        "excess_decomposition_matches": (
            excess_power == excess_decomposition
        ),
        "availability_upper_bound": fraction_record(upper_bound),
        "upper_bound_holds": 0 <= excess_power <= upper_bound,
        "epsilon_actual": fraction_record(epsilon_actual),
        "availability_interior_lower_bound": fraction_record(
            availability_interior_lower_bound
        ),
        "minimum_informative_power_gain": fraction_record(
            minimum_informative_power_gain
        ),
        "excess_interior_lower_bound": fraction_record(
            excess_interior_lower_bound
        ),
        "interior_lower_bound_holds": (
            0 <= excess_interior_lower_bound <= excess_power
        ),
        "all_conditional_sizes_exact": all(
            test["null_size"] == alpha for test in tests.values()
        ),
        "singleton_test_count": sum(
            not test["informative"] for test in tests.values()
        ),
        "informative_test_count": sum(
            test["informative"] for test in tests.values()
        ),
    }


def run_registry(spec: dict[str, Any]) -> dict[str, Any]:
    alpha = parse_fraction(spec["alpha"])
    records = []
    for cycle_length in spec["cycle_lengths"]:
        for trials_per_edge in spec["trials_per_edge"]:
            for odds_ratio_raw in spec["odds_ratios"]:
                odds_ratio = parse_fraction(odds_ratio_raw)
                for nuisance_ratio_raw in spec["nuisance_ratios"]:
                    nuisance_ratio = parse_fraction(nuisance_ratio_raw)
                    records.append(
                        run_cell(
                            int(cycle_length),
                            int(trials_per_edge),
                            odds_ratio,
                            nuisance_ratio,
                            alpha,
                        )
                    )
    return {
        "alpha": spec["alpha"],
        "records": records,
        "cell_count": len(records),
        "availability_formula_mismatch_count": sum(
            not record["availability_formula_matches"]
            for record in records
        ),
        "conditional_size_mismatch_count": sum(
            not record["all_conditional_sizes_exact"]
            for record in records
        ),
        "mass_normalization_mismatch_count": sum(
            not record["null_mass_normalized"]
            or not record["alternative_mass_normalized"]
            for record in records
        ),
        "excess_decomposition_mismatch_count": sum(
            not record["excess_decomposition_matches"]
            for record in records
        ),
        "upper_bound_mismatch_count": sum(
            not record["upper_bound_holds"] for record in records
        ),
        "interior_lower_bound_mismatch_count": sum(
            not record["interior_lower_bound_holds"]
            for record in records
        ),
    }
