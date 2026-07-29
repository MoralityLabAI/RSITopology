"""Exact support calculations for the ASMP-9 v0.56 candidate theorem."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, permutations
from typing import Dict, Iterable, Mapping, Sequence, Tuple


Q = Fraction
Alternative = int
Menu = Tuple[Alternative, ...]
Event = Tuple[Menu, Alternative]
Kernel = Dict[Event, Q]


def menus(n: int) -> Tuple[Menu, ...]:
    if n < 3:
        raise ValueError("the registered theorem requires n >= 3")
    return tuple(
        menu
        for size in range(2, n + 1)
        for menu in combinations(range(n), size)
    )


def ambient_dimension(n: int) -> int:
    return sum(len(menu) - 1 for menu in menus(n))


def exact_rank(rows: Sequence[Sequence[int | Q]]) -> int:
    matrix = [[Q(value) for value in row] for row in rows]
    if not matrix:
        return 0
    width = len(matrix[0])
    rank = 0
    for column in range(width):
        pivot = next(
            (row for row in range(rank, len(matrix)) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        matrix[rank] = [value / scale for value in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                left - factor * right
                for left, right in zip(matrix[row], matrix[rank])
            ]
        rank += 1
        if rank == width:
            break
    return rank


def ranking_signature(n: int, ranking: Sequence[int]) -> Tuple[int, ...]:
    """Return affine coordinates, omitting one redundant choice per menu."""

    position = {alternative: index for index, alternative in enumerate(ranking)}
    values = [1]
    for menu in menus(n):
        winner = min(menu, key=position.__getitem__)
        values.extend(int(winner == choice) for choice in menu[:-1])
    return tuple(values)


def random_utility_affine_rank(n: int) -> int:
    rows = [
        ranking_signature(n, ranking)
        for ranking in permutations(range(n))
    ]
    return exact_rank(rows) - 1


def graph_components(n: int, observed: Iterable[Menu]) -> int:
    adjacency = {node: set() for node in range(n)}
    for menu in observed:
        for left, right in combinations(menu, 2):
            adjacency[left].add(right)
            adjacency[right].add(left)
    count = 0
    unseen = set(range(n))
    while unseen:
        count += 1
        stack = [unseen.pop()]
        while stack:
            node = stack.pop()
            neighbors = adjacency[node] & unseen
            unseen.difference_update(neighbors)
            stack.extend(neighbors)
    return count


def missing_coordinate_dimension(n: int, observed: Iterable[Menu]) -> int:
    observed_set = set(observed)
    return sum(
        len(menu) - 1
        for menu in menus(n)
        if menu not in observed_set
    )


def luce_fiber_dimension(n: int, observed: Iterable[Menu]) -> int:
    return graph_components(n, observed) - 1


def dimension_gap(n: int, observed: Iterable[Menu]) -> int:
    observed = tuple(observed)
    return (
        missing_coordinate_dimension(n, observed)
        - luce_fiber_dimension(n, observed)
    )


def uniform_kernel(n: int) -> Kernel:
    return {
        (menu, choice): Q(1, len(menu))
        for menu in menus(n)
        for choice in menu
    }


def _set_probability(
    kernel: Kernel,
    menu: Menu,
    choice: Alternative,
    value: Q,
) -> None:
    if not 0 < value < 1:
        raise ValueError("distinguished probability must lie strictly inside")
    rest = (1 - value) / (len(menu) - 1)
    for alternative in menu:
        kernel[(menu, alternative)] = (
            value if alternative == choice else rest
        )


def construct_nonrum_completion(
    n: int,
    observed: Iterable[Menu],
    partial: Mapping[Event, Q] | None = None,
) -> Kernel:
    """Preserve observed menus and force one strict regularity violation."""

    observed = tuple(observed)
    observed_set = set(observed)
    universe = menus(n)
    missing = [menu for menu in universe if menu not in observed_set]
    if not missing:
        raise ValueError("a proper menu domain is required")

    completion = uniform_kernel(n)
    if partial is not None:
        for menu in observed:
            for choice in menu:
                completion[(menu, choice)] = Q(partial[(menu, choice)])

    full = tuple(range(n))
    target = missing[0]
    choice = target[0]

    if target != full:
        outside = next(item for item in full if item not in target)
        superset = tuple(sorted((*target, outside)))
        if superset in observed_set:
            upper = completion[(superset, choice)]
            _set_probability(completion, target, choice, upper / 2)
        else:
            _set_probability(completion, target, choice, Q(1, 4))
            _set_probability(completion, superset, choice, Q(1, 2))
    else:
        subset = (full[0], full[1])
        if subset in observed_set:
            lower = completion[(subset, choice)]
            _set_probability(completion, full, choice, (1 + lower) / 2)
        else:
            _set_probability(completion, subset, choice, Q(1, 4))
            _set_probability(completion, full, choice, Q(1, 2))

    return completion


def regularity_violations(n: int, kernel: Mapping[Event, Q]):
    violations = []
    universe = menus(n)
    for smaller in universe:
        for larger in universe:
            if smaller == larger or not set(smaller).issubset(larger):
                continue
            for choice in smaller:
                if kernel[(larger, choice)] > kernel[(smaller, choice)]:
                    violations.append((smaller, larger, choice))
    return tuple(violations)


def proper_domains(n: int):
    universe = menus(n)
    for mask in range(1 << len(universe)):
        if mask == (1 << len(universe)) - 1:
            continue
        yield tuple(
            menu for index, menu in enumerate(universe) if mask & (1 << index)
        )

