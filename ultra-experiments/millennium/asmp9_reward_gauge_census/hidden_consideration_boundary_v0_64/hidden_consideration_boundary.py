"""Exact helpers for the ASMP-9 v0.64 hidden-consideration boundary."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations
from math import comb
from typing import Iterable, Mapping, Sequence


Q = Fraction


def rankings(n: int) -> tuple[tuple[int, ...], ...]:
    if n < 2:
        raise ValueError("n must be at least two")
    return tuple(permutations(range(n)))


def all_pairs(n: int) -> tuple[tuple[int, int], ...]:
    if n < 2:
        raise ValueError("n must be at least two")
    return tuple(combinations(range(n), 2))


def canonical_pairs(pairs: Iterable[Sequence[int]]) -> tuple[tuple[int, int], ...]:
    result = set()
    for pair in pairs:
        pair = tuple(pair)
        if len(pair) != 2 or pair[0] == pair[1]:
            raise ValueError("each query must contain two distinct items")
        result.add(tuple(sorted((int(pair[0]), int(pair[1])))))
    return tuple(sorted(result))


def winner(ranking: Sequence[int], considered: Iterable[int]) -> int:
    considered = set(considered)
    if not considered:
        raise ValueError("consideration set must be nonempty")
    for item in ranking:
        if item in considered:
            return int(item)
    raise ValueError("consideration set is outside the ranking universe")


def pair_signature(
    ranking: Sequence[int],
    pairs: Iterable[Sequence[int]],
) -> tuple[int, ...]:
    pairs = canonical_pairs(pairs)
    return tuple(winner(ranking, pair) for pair in pairs)


def canonical_consideration_family(
    n: int,
    consideration_sets: Iterable[Iterable[int]],
) -> tuple[tuple[int, ...], ...]:
    """Validate and canonicalize one hidden-compliance correspondence."""

    if n < 2:
        raise ValueError("n must be at least two")
    result = set()
    for considered in consideration_sets:
        considered = tuple(sorted({int(item) for item in considered}))
        if not considered:
            raise ValueError("consideration sets must be nonempty")
        if considered[0] < 0 or considered[-1] >= n:
            raise ValueError("consideration set is outside the item universe")
        result.add(considered)
    if not result:
        raise ValueError("an intervention needs at least one admissible set")
    return tuple(sorted(result))


def attainable_choices(
    ranking: Sequence[int],
    consideration_sets: Iterable[Iterable[int]],
) -> tuple[int, ...]:
    """Choices an unrestricted compliance mechanism can manufacture."""

    ranking = tuple(int(item) for item in ranking)
    n = len(ranking)
    if n < 2 or set(ranking) != set(range(n)):
        raise ValueError("ranking must permute the complete item universe")
    family = canonical_consideration_family(n, consideration_sets)
    return tuple(sorted({winner(ranking, considered) for considered in family}))


def intervention_separates(
    left: Sequence[int],
    right: Sequence[int],
    consideration_sets: Iterable[Iterable[int]],
) -> bool:
    """Whether one intervention separates two adversarial-compliance laws."""

    left_choices = set(attainable_choices(left, consideration_sets))
    right_choices = set(attainable_choices(right, consideration_sets))
    return left_choices.isdisjoint(right_choices)


def compliance_suite_identifies(
    n: int,
    interventions: Iterable[Iterable[Iterable[int]]],
) -> bool:
    """Exact finite separation criterion for a registered intervention suite."""

    orders = rankings(n)
    families = tuple(
        canonical_consideration_family(n, family)
        for family in interventions
    )
    if not families:
        return False
    for left_index, left in enumerate(orders):
        for right in orders[left_index + 1 :]:
            if not any(
                intervention_separates(left, right, family)
                for family in families
            ):
                return False
    return True


def minimum_separating_suite(
    n: int,
    candidate_interventions: Mapping[
        str,
        Iterable[Iterable[int]],
    ],
) -> tuple[int | None, tuple[str, ...]]:
    """Solve the finite separation-cover problem by exhaustive enumeration."""

    names = tuple(sorted(str(name) for name in candidate_interventions))
    if len(set(names)) != len(candidate_interventions):
        raise ValueError("intervention names must remain unique as strings")
    families = {
        str(name): canonical_consideration_family(n, family)
        for name, family in candidate_interventions.items()
    }
    orders = rankings(n)
    order_pairs = tuple(
        (left, right)
        for left_index, left in enumerate(orders)
        for right in orders[left_index + 1 :]
    )
    target = (1 << len(order_pairs)) - 1
    coverage = {}
    for name in names:
        mask = 0
        family = families[name]
        for index, (left, right) in enumerate(order_pairs):
            if intervention_separates(left, right, family):
                mask |= 1 << index
        coverage[name] = mask

    for size in range(len(names) + 1):
        for selected in combinations(names, size):
            combined = 0
            for name in selected:
                combined |= coverage[name]
            if combined == target:
                return size, selected
    return None, ()


def deterministic_identifiable(
    n: int,
    pairs: Iterable[Sequence[int]],
) -> bool:
    return canonical_pairs(pairs) == all_pairs(n)


def minimum_nonadaptive_pair_queries(n: int) -> int:
    if n < 2:
        raise ValueError("n must be at least two")
    return comb(n, 2)


def adjacent_swap_witness(
    n: int,
    missing_pair: Sequence[int],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    pair = canonical_pairs((missing_pair,))
    if len(pair) != 1:
        raise ValueError("expected one missing pair")
    x, y = pair[0]
    if not 0 <= x < n or not 0 <= y < n:
        raise ValueError("pair is outside the ranking universe")
    others = tuple(item for item in range(n) if item not in (x, y))
    split = len(others) // 2
    left = others[:split] + (x, y) + others[split:]
    right = others[:split] + (y, x) + others[split:]
    return left, right


def validate_kernel(
    kernel: Mapping[tuple[int, ...], Sequence[Fraction]],
) -> None:
    for menu, probabilities in kernel.items():
        menu = tuple(menu)
        probabilities = tuple(Q(value) for value in probabilities)
        if not menu or len(menu) != len(probabilities):
            raise ValueError("kernel row has inconsistent dimensions")
        if tuple(sorted(menu)) != menu or len(set(menu)) != len(menu):
            raise ValueError("menus must be sorted sets")
        if min(probabilities) < 0 or sum(probabilities, Q(0)) != 1:
            raise ValueError("kernel row must be a distribution")


def singleton_attention_observation(
    ranking: Sequence[int],
    kernel: Mapping[tuple[int, ...], Sequence[Fraction]],
) -> dict[tuple[int, ...], tuple[Fraction, ...]]:
    """Reproduce a kernel using singleton consideration, for any ranking."""

    validate_kernel(kernel)
    observed = {}
    for menu, probabilities in kernel.items():
        row = []
        for chosen, probability in zip(menu, probabilities):
            singleton = (chosen,)
            if winner(ranking, singleton) != chosen:
                raise AssertionError("singleton did not force its only item")
            row.append(Q(probability))
        observed[tuple(menu)] = tuple(row)
    return observed


def intervention_family_observation(
    ranking: Sequence[int],
    kernels: Mapping[
        str,
        Mapping[tuple[int, ...], Sequence[Fraction]],
    ],
) -> dict[str, dict[tuple[int, ...], tuple[Fraction, ...]]]:
    """Apply the singleton collapse independently after each instruction."""

    return {
        str(instruction): singleton_attention_observation(ranking, kernel)
        for instruction, kernel in kernels.items()
    }
