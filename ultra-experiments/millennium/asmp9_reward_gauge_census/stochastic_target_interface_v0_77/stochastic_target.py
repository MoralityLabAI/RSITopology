"""Finite stochastic target recovery for ASMP-9 v0.77."""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Hashable, Sequence

import sympy as sp


Law = tuple[sp.Rational, ...]


def law(values: Sequence[object]) -> Law:
    result = tuple(sp.Rational(value) for value in values)
    if not result or any(value < 0 for value in result) or sum(result) != 1:
        raise ValueError("a law must be nonnegative and sum to one")
    return result


def affinity(left: Law, right: Law) -> sp.Expr:
    if len(left) != len(right):
        raise ValueError("laws have different alphabets")
    return sp.simplify(
        sum((sp.sqrt(a * b) for a, b in zip(left, right)), sp.Integer(0))
    )


@dataclass(frozen=True)
class StochasticInterface:
    status: str
    population_target_recoverable: bool
    representative_insensitive: bool
    minimum_cross_target_hellinger_squared: sp.Expr | None
    maximum_within_target_hellinger_squared: sp.Expr
    underidentification_witnesses: tuple[tuple[int, int], ...]
    representative_leakage_witnesses: tuple[tuple[int, int], ...]


def analyze_stochastic_interface(
    targets: Sequence[Hashable],
    laws: Sequence[Law],
) -> StochasticInterface:
    if not targets or len(targets) != len(laws):
        raise ValueError("targets and laws must have equal positive size")
    alphabet_size = len(laws[0])
    if any(len(item) != alphabet_size for item in laws):
        raise ValueError("laws have different alphabets")

    underidentified = []
    leakage = []
    cross_h2 = []
    within_h2 = [sp.Integer(0)]
    for left in range(len(laws)):
        for right in range(left + 1, len(laws)):
            same_target = targets[left] == targets[right]
            same_law = laws[left] == laws[right]
            h2 = sp.simplify(1 - affinity(laws[left], laws[right]))
            if same_target:
                within_h2.append(h2)
                if not same_law:
                    leakage.append((left, right))
            else:
                cross_h2.append(h2)
                if same_law:
                    underidentified.append((left, right))

    recoverable = not underidentified
    insensitive = not leakage
    if recoverable and insensitive:
        status = "exact_stochastic_target_interface"
    elif recoverable:
        status = "recoverable_with_distributional_leakage"
    elif insensitive:
        status = "population_underidentified"
    else:
        status = "cross_cut_stochastic_interface"

    return StochasticInterface(
        status=status,
        population_target_recoverable=recoverable,
        representative_insensitive=insensitive,
        minimum_cross_target_hellinger_squared=(
            min(cross_h2, key=lambda value: float(value.evalf()))
            if cross_h2
            else None
        ),
        maximum_within_target_hellinger_squared=max(
            within_h2, key=lambda value: float(value.evalf())
        ),
        underidentification_witnesses=tuple(underidentified),
        representative_leakage_witnesses=tuple(leakage),
    )


def hellinger_mle_union_bound(
    targets: Sequence[Hashable],
    laws: Sequence[Law],
    sample_count: int,
) -> sp.Expr:
    """Worst-case union bound for maximum-likelihood target recovery."""

    if sample_count < 0:
        raise ValueError("sample count must be nonnegative")
    analyze_stochastic_interface(targets, laws)
    per_true_parameter = []
    for left in range(len(laws)):
        error_bound = sum(
            (
                affinity(laws[left], laws[right]) ** sample_count
                for right in range(len(laws))
                if targets[left] != targets[right]
            ),
            sp.Integer(0),
        )
        per_true_parameter.append(error_bound)
    if not per_true_parameter:
        return sp.Integer(0)
    worst = max(per_true_parameter, key=lambda value: float(value.evalf()))
    return sp.Min(sp.Integer(1), sp.simplify(worst))


def minimum_hellinger_bound_samples(
    targets: Sequence[Hashable],
    laws: Sequence[Law],
    alpha: object,
    *,
    maximum_samples: int = 100_000,
) -> int | None:
    threshold = sp.Rational(alpha)
    if threshold <= 0 or threshold >= 1:
        raise ValueError("alpha must lie strictly between zero and one")
    for sample_count in range(maximum_samples + 1):
        bound = hellinger_mle_union_bound(targets, laws, sample_count)
        if float(bound.evalf(50)) <= float(threshold):
            return sample_count
    return None


def exact_binary_bayes_error(left: Law, right: Law, sample_count: int) -> sp.Rational:
    """Equal-prior Bayes error for two binary iid laws."""

    if len(left) != 2 or len(right) != 2 or sample_count < 0:
        raise ValueError("two binary laws and nonnegative sample count required")
    left_count = [
        sp.Rational(comb(sample_count, successes))
        * left[0] ** successes
        * left[1] ** (sample_count - successes)
        for successes in range(sample_count + 1)
    ]
    right_count = [
        sp.Rational(comb(sample_count, successes))
        * right[0] ** successes
        * right[1] ** (sample_count - successes)
        for successes in range(sample_count + 1)
    ]
    total_variation = sp.Rational(1, 2) * sum(
        (abs(a - b) for a, b in zip(left_count, right_count)),
        sp.Integer(0),
    )
    return sp.Rational(1, 2) * (1 - total_variation)


def minimum_exact_binary_bayes_samples(
    left: Law,
    right: Law,
    alpha: object,
    *,
    maximum_samples: int = 100_000,
) -> int | None:
    threshold = sp.Rational(alpha)
    for sample_count in range(maximum_samples + 1):
        if exact_binary_bayes_error(left, right, sample_count) <= threshold:
            return sample_count
    return None


def iid_tv_misspecification_penalty(
    per_sample_tv: object,
    sample_count: int,
) -> sp.Rational:
    epsilon = sp.Rational(per_sample_tv)
    if epsilon < 0 or epsilon > 1 or sample_count < 0:
        raise ValueError("invalid TV radius or sample count")
    return sp.simplify(1 - (1 - epsilon) ** sample_count)


def robustified_error_bound(
    registered_bound: object,
    per_sample_tv: object,
    sample_count: int,
) -> sp.Expr:
    return sp.Min(
        sp.Integer(1),
        sp.Rational(registered_bound)
        + iid_tv_misspecification_penalty(per_sample_tv, sample_count),
    )
