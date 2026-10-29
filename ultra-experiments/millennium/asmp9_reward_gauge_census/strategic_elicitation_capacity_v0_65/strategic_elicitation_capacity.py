"""Exact helpers for ASMP-9 strategic elicitation capacity v0.65."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations, product
from math import comb, factorial
from typing import Iterable, Mapping, Sequence


Q = Fraction


def rankings(n: int) -> tuple[tuple[int, ...], ...]:
    if n < 2:
        raise ValueError("n must be at least two")
    return tuple(permutations(range(n)))


def validate_ranking(
    ranking: Sequence[int],
    n: int | None = None,
) -> tuple[int, ...]:
    ranking = tuple(int(item) for item in ranking)
    if n is None:
        n = len(ranking)
    if n < 2:
        raise ValueError("outcome universe must contain at least two items")
    if len(ranking) != n or set(ranking) != set(range(n)):
        raise ValueError("ranking must be a strict complete order")
    return ranking


def validate_types(
    types: Iterable[Sequence[int]],
    n: int | None = None,
) -> tuple[tuple[int, ...], ...]:
    types = tuple(tuple(int(item) for item in ranking) for ranking in types)
    if not types:
        raise ValueError("type domain must be nonempty")
    if n is None:
        n = len(types[0])
    if n < 2:
        raise ValueError("outcome universe must contain at least two items")
    types = tuple(validate_ranking(ranking, n) for ranking in types)
    if len(set(types)) != len(types):
        raise ValueError("type domain must not contain duplicates")
    return types


def positions(ranking: Sequence[int]) -> dict[int, int]:
    return {int(item): index for index, item in enumerate(ranking)}


def top_on(ranking: Sequence[int], outcomes: Iterable[int]) -> int:
    outcomes = frozenset(int(outcome) for outcome in outcomes)
    if not outcomes:
        raise ValueError("outcome menu must be nonempty")
    for outcome in ranking:
        if outcome in outcomes:
            return int(outcome)
    raise ValueError("outcome menu is outside the ranking universe")


def best_report_indices(
    ranking: Sequence[int],
    outcome_map: Sequence[int],
) -> tuple[int, ...]:
    if not outcome_map:
        raise ValueError("outcome map must be nonempty")
    order = positions(ranking)
    try:
        best_position = min(order[int(outcome)] for outcome in outcome_map)
    except KeyError as error:
        raise ValueError("mapped outcome is outside the ranking") from error
    return tuple(
        index
        for index, outcome in enumerate(outcome_map)
        if order[int(outcome)] == best_position
    )


def strictly_incentive_identifies(
    types: Iterable[Sequence[int]],
    outcome_map: Sequence[int],
) -> bool:
    types = validate_types(types)
    outcome_map = tuple(int(outcome) for outcome in outcome_map)
    if len(outcome_map) != len(types):
        raise ValueError("one designated report is required per type")
    n = len(types[0])
    if any(outcome < 0 or outcome >= n for outcome in outcome_map):
        raise ValueError("mapped outcome is outside the outcome universe")
    return all(
        best_report_indices(ranking, outcome_map) == (index,)
        for index, ranking in enumerate(types)
    )


def weakly_truthful(
    types: Iterable[Sequence[int]],
    outcome_map: Sequence[int],
) -> bool:
    types = validate_types(types)
    outcome_map = tuple(int(outcome) for outcome in outcome_map)
    if len(outcome_map) != len(types):
        raise ValueError("one designated report is required per type")
    return all(
        index in best_report_indices(ranking, outcome_map)
        for index, ranking in enumerate(types)
    )


def strict_capacity(
    types: Iterable[Sequence[int]],
) -> tuple[int, tuple[tuple[int, int], ...]]:
    """Return capacity and one (type-index, assigned-outcome) witness."""

    types = validate_types(types)
    n = len(types[0])
    best: tuple[tuple[int, int], ...] = ()
    for size in range(1, n + 1):
        for menu in combinations(range(n), size):
            first_type_by_top: dict[int, int] = {}
            for type_index, ranking in enumerate(types):
                top = top_on(ranking, menu)
                first_type_by_top.setdefault(top, type_index)
            witness = tuple(
                sorted(
                    (type_index, outcome)
                    for outcome, type_index in first_type_by_top.items()
                )
            )
            if len(witness) > len(best):
                best = witness
    return len(best), best


def brute_force_capacity(
    types: Iterable[Sequence[int]],
) -> int:
    """Reference implementation; suitable only for very small type domains."""

    types = validate_types(types)
    n = len(types[0])
    for size in range(min(len(types), n), 0, -1):
        for selected in combinations(range(len(types)), size):
            selected_types = tuple(types[index] for index in selected)
            for outcome_map in product(range(n), repeat=size):
                if strictly_incentive_identifies(
                    selected_types,
                    outcome_map,
                ):
                    return size
    raise AssertionError("a singleton type is always implementable")


def report_top_outcome_map(
    types: Iterable[Sequence[int]],
) -> tuple[int, ...]:
    types = validate_types(types)
    return tuple(ranking[0] for ranking in types)


def full_domain_capacity(n: int) -> int:
    capacity, _ = strict_capacity(rankings(n))
    return capacity


def report_top_best_response_multiplicity(n: int) -> int:
    types = rankings(n)
    outcome_map = report_top_outcome_map(types)
    counts = {
        len(best_report_indices(ranking, outcome_map))
        for ranking in types
    }
    expected = factorial(n - 1)
    if counts != {expected}:
        raise AssertionError("unexpected report-top multiplicity")
    return expected


def all_pairs(n: int) -> tuple[tuple[int, int], ...]:
    if n < 2:
        raise ValueError("n must be at least two")
    return tuple(combinations(range(n), 2))


def validate_pair_weights(
    n: int,
    weights: Mapping[tuple[int, int], Fraction | int],
) -> dict[tuple[int, int], Fraction]:
    allowed = set(all_pairs(n))
    normalized: dict[tuple[int, int], Fraction] = {}
    if not weights:
        raise ValueError("pair distribution must be nonempty")
    for raw_pair, raw_weight in weights.items():
        pair = tuple(int(item) for item in raw_pair)
        if len(pair) != 2 or pair[0] >= pair[1] or pair not in allowed:
            raise ValueError("pair keys must be canonical outcome pairs")
        weight = Q(raw_weight)
        if weight <= 0:
            raise ValueError("all included pairs must have positive weight")
        normalized[pair] = weight
    if sum(normalized.values(), Q(0)) != Q(1):
        raise ValueError("pair weights must sum exactly to one")
    return normalized


def uniform_pair_weights(n: int) -> dict[tuple[int, int], Fraction]:
    pairs = all_pairs(n)
    weight = Q(1, len(pairs))
    return {pair: weight for pair in pairs}


def pair_lottery_regret(
    true_ranking: Sequence[int],
    reported_ranking: Sequence[int],
    utilities: Sequence[Fraction | int],
    weights: Mapping[tuple[int, int], Fraction | int],
) -> Fraction:
    """Expected-utility loss from a false report under random pair selection."""

    true_ranking = validate_ranking(true_ranking)
    n = len(true_ranking)
    reported_ranking = validate_ranking(reported_ranking, n)
    utilities = tuple(Q(value) for value in utilities)
    if len(utilities) != n:
        raise ValueError("one utility is required per outcome")
    if any(
        utilities[true_ranking[index]]
        <= utilities[true_ranking[index + 1]]
        for index in range(n - 1)
    ):
        raise ValueError("utilities must strictly represent the true ranking")
    weights = validate_pair_weights(n, weights)
    return sum(
        (
            weight
            * (
                utilities[top_on(true_ranking, pair)]
                - utilities[top_on(reported_ranking, pair)]
            )
            for pair, weight in weights.items()
        ),
        Q(0),
    )


def pair_lottery_strictly_elicits_all(
    n: int,
    weights: Mapping[tuple[int, int], Fraction | int],
) -> bool:
    weights = validate_pair_weights(n, weights)
    return set(weights) == set(all_pairs(n))


def minimum_pair_lottery_support(n: int) -> int:
    if n < 2:
        raise ValueError("n must be at least two")
    return comb(n, 2)


def sharp_uniform_incentive_margin(
    n: int,
    adjacent_utility_gap: Fraction | int,
) -> Fraction:
    """Worst false-report regret with uniform pairs and normalized utilities."""

    if n < 2:
        raise ValueError("n must be at least two")
    gap = Q(adjacent_utility_gap)
    if gap <= 0 or gap * (n - 1) > 1:
        raise ValueError(
            "gap must be positive and permit a unit-range ranking"
        )
    return gap / comb(n, 2)


def revealed_pair_class_size(n: int) -> int:
    if n < 2:
        raise ValueError("n must be at least two")
    return factorial(n) // 2
