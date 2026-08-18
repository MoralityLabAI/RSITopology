"""Exact helpers for the ASMP-9 v0.63 capped-simplex modulus."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations
from typing import Iterable, Sequence


Q = Fraction
ALTERNATIVES = ("a", "b", "c")
RANKINGS = tuple(permutations(ALTERNATIVES))
CAPS = (Q(2, 5), Q(3, 5), Q(2, 5))
FLOOR = Q(1, 10)
MAX_GAMMA = Q(1, 50)
FullLaw = tuple[Fraction, Fraction, Fraction]


def _law(values: Sequence[Fraction]) -> FullLaw:
    values = tuple(Q(value) for value in values)
    if len(values) != 3 or min(values) <= 0 or sum(values, Q(0)) != 1:
        raise ValueError("expected a positive three-coordinate distribution")
    return values  # type: ignore[return-value]


def _gamma(value: Fraction) -> Fraction:
    value = Q(value)
    if not 0 < value <= MAX_GAMMA:
        raise ValueError("gamma must lie in (0,1/50]")
    return value


def ranking_weights(full: Sequence[Fraction]) -> tuple[Fraction, ...]:
    """Unique ranking weights compatible with the frozen binary fiber."""

    a, b, c = _law(full)
    return (
        Q(3, 5) - b,
        Q(2, 5) - c,
        Q(3, 5) - a,
        Q(2, 5) - c,
        Q(2, 5) - a,
        Q(3, 5) - b,
    )


def full_from_ranking_weights(weights: Sequence[Fraction]) -> FullLaw:
    weights = tuple(Q(value) for value in weights)
    if len(weights) != 6 or min(weights) < 0:
        raise ValueError("invalid ranking weights")
    if sum(weights, Q(0)) != 1:
        raise ValueError("ranking weights must sum to one")
    masses = []
    for item in ALTERNATIVES:
        masses.append(
            sum(
                weight
                for ranking, weight in zip(RANKINGS, weights)
                if ranking[0] == item
            )
        )
    return _law(masses)


def binary_probabilities_from_weights(
    weights: Sequence[Fraction],
) -> tuple[Fraction, Fraction, Fraction]:
    weights = tuple(Q(value) for value in weights)
    if len(weights) != 6 or min(weights) < 0:
        raise ValueError("invalid ranking weights")
    if sum(weights, Q(0)) != 1:
        raise ValueError("ranking weights must sum to one")
    pairs = (("a", "b"), ("a", "c"), ("b", "c"))
    values = []
    for winner, loser in pairs:
        values.append(
            sum(
                weight
                for ranking, weight in zip(RANKINGS, weights)
                if ranking.index(winner) < ranking.index(loser)
            )
        )
    return tuple(values)  # type: ignore[return-value]


def is_rum(full: Sequence[Fraction]) -> bool:
    full = _law(full)
    return all(value <= cap for value, cap in zip(full, CAPS))


def in_floor_class(full: Sequence[Fraction]) -> bool:
    return min(_law(full)) >= FLOOR


def violation_support(full: Sequence[Fraction]) -> tuple[int, ...]:
    full = _law(full)
    return tuple(
        index
        for index, (value, cap) in enumerate(zip(full, CAPS))
        if value > cap
    )


def violation_mass(full: Sequence[Fraction]) -> Fraction:
    full = _law(full)
    return sum(
        (value - cap for value, cap in zip(full, CAPS) if value > cap),
        Q(0),
    )


def tv(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    left = _law(left)
    right = _law(right)
    return sum(abs(a - b) for a, b in zip(left, right)) / 2


def symmetric_ratio(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> Fraction:
    left = _law(left)
    right = _law(right)
    return max(
        max(a / b, b / a)
        for a, b in zip(left, right)
    )


def rum_projection(full: Sequence[Fraction]) -> FullLaw:
    """Construct a closest capped-simplex point in exact arithmetic."""

    full = _law(full)
    projected = list(full)
    removed = Q(0)
    for index, cap in enumerate(CAPS):
        if projected[index] > cap:
            removed += projected[index] - cap
            projected[index] = cap
    for index, cap in enumerate(CAPS):
        if removed == 0:
            break
        room = cap - projected[index]
        if room <= 0:
            continue
        addition = min(room, removed)
        projected[index] += addition
        removed -= addition
    if removed != 0:
        raise AssertionError("capped simplex did not have enough slack")
    return _law(projected)


def possible_violation_supports() -> tuple[tuple[int, ...], ...]:
    supports = []
    for size in range(1, 4):
        for support in combinations(range(3), size):
            if sum((CAPS[index] for index in support), Q(0)) < 1:
                supports.append(support)
    return tuple(supports)


def support_bound(
    gamma: Fraction,
    support: Iterable[int],
) -> Fraction:
    gamma = _gamma(gamma)
    support = tuple(sorted(set(support)))
    if not support:
        raise ValueError("support must be nonempty")
    cap_sum = sum((CAPS[index] for index in support), Q(0))
    if not 0 < cap_sum < 1 or gamma >= 1 - cap_sum:
        raise ValueError("infeasible violation support")
    expansion = 1 + gamma / cap_sum
    contraction = (1 - cap_sum) / (1 - cap_sum - gamma)
    return max(expansion, contraction)


def all_support_bounds(
    gamma: Fraction,
) -> dict[tuple[int, ...], Fraction]:
    gamma = _gamma(gamma)
    return {
        support: support_bound(gamma, support)
        for support in possible_violation_supports()
    }


def delta_modulus(gamma: Fraction) -> Fraction:
    return _gamma(gamma)


def lambda_modulus(gamma: Fraction) -> Fraction:
    gamma = _gamma(gamma)
    return 1 + Q(5, 2) * gamma


def primal_pair(gamma: Fraction) -> tuple[FullLaw, FullLaw]:
    gamma = _gamma(gamma)
    rum = _law((Q(2, 5), Q(3, 10), Q(3, 10)))
    nonrum = _law(
        (
            Q(2, 5) + gamma,
            Q(3, 10) - gamma / 2,
            Q(3, 10) - gamma / 2,
        )
    )
    return rum, nonrum


def huber_threshold(gamma: Fraction) -> Fraction:
    gamma = _gamma(gamma)
    return gamma / (1 + gamma)


def common_huber_observation(gamma: Fraction) -> FullLaw:
    gamma = _gamma(gamma)
    left, right = primal_pair(gamma)
    return _law(
        tuple(max(a, b) / (1 + gamma) for a, b in zip(left, right))
    )


def common_recording_observation(
    gamma: Fraction,
) -> tuple[FullLaw, FullLaw, FullLaw]:
    """Return joint masses and the two bounded recording vectors."""

    gamma = _gamma(gamma)
    left, right = primal_pair(gamma)
    ratio = lambda_modulus(gamma)
    lower = 1 / ratio
    joint = tuple(lower * max(a, b) for a, b in zip(left, right))
    left_recording = tuple(mass / value for mass, value in zip(joint, left))
    right_recording = tuple(mass / value for mass, value in zip(joint, right))
    if not all(lower <= value <= 1 for value in left_recording):
        raise AssertionError("left recording vector is outside the boundary")
    if not all(lower <= value <= 1 for value in right_recording):
        raise AssertionError("right recording vector is outside the boundary")
    return (
        tuple(joint),  # type: ignore[return-value]
        tuple(left_recording),  # type: ignore[return-value]
        tuple(right_recording),  # type: ignore[return-value]
    )

