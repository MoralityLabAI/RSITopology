"""Exact incomplete-menu access analysis for ASMP-9 v0.55."""

from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, permutations, product
from typing import Dict, Iterable, Iterator, Mapping, Sequence, Tuple


Alternative = str
Menu = Tuple[Alternative, ...]
Event = Tuple[Menu, Alternative]
Kernel = Dict[Event, Q]
Ranking = Tuple[Alternative, ...]

X = ("a", "b", "c")
AB = ("a", "b")
AC = ("a", "c")
BC = ("b", "c")
ABC = ("a", "b", "c")
ALL_MENUS = (AB, AC, BC, ABC)
RANKINGS = tuple(permutations(X))

L = "scalar_luce"
R = "random_utility_non_luce"
N = "no_random_utility_representation"


def make_kernel(pair_ab, pair_ac, pair_bc, triple) -> Kernel:
    return {
        (AB, "a"): Q(pair_ab),
        (AB, "b"): 1 - Q(pair_ab),
        (AC, "a"): Q(pair_ac),
        (AC, "c"): 1 - Q(pair_ac),
        (BC, "b"): Q(pair_bc),
        (BC, "c"): 1 - Q(pair_bc),
        (ABC, "a"): Q(triple[0]),
        (ABC, "b"): Q(triple[1]),
        (ABC, "c"): Q(triple[2]),
    }


def full_grid() -> Iterator[Kernel]:
    pairs = tuple(Q(k, 6) for k in range(1, 6))
    triples = tuple(
        (Q(a, 6), Q(b, 6), Q(c, 6))
        for a in range(1, 6)
        for b in range(1, 6)
        for c in range(1, 6)
        if a + b + c == 6
    )
    for pair_ab, pair_ac, pair_bc, triple in product(
        pairs, pairs, pairs, triples
    ):
        yield make_kernel(pair_ab, pair_ac, pair_bc, triple)


def menu_domains() -> Iterator[Tuple[Menu, ...]]:
    for size in range(1, len(ALL_MENUS) + 1):
        yield from combinations(ALL_MENUS, size)


def domain_name(domain: Sequence[Menu]) -> str:
    labels = {AB: "ab", AC: "ac", BC: "bc", ABC: "abc"}
    return "+".join(labels[menu] for menu in domain)


def project(kernel: Mapping[Event, Q], domain: Sequence[Menu]) -> Kernel:
    domain = tuple(domain)
    return {
        (menu, choice): Q(kernel[(menu, choice)])
        for menu in domain
        for choice in menu
    }


def projection_key(kernel: Mapping[Event, Q]) -> Tuple[Tuple[Event, Q], ...]:
    return tuple(sorted((event, Q(value)) for event, value in kernel.items()))


def normalized(partial: Mapping[Event, Q], domain: Sequence[Menu]) -> bool:
    return all(
        all(Q(partial[(menu, x)]) > 0 for x in menu)
        and sum((Q(partial[(menu, x)]) for x in menu), Q(0)) == 1
        for menu in domain
    )


def scalar_completion(
    partial: Mapping[Event, Q],
    domain: Sequence[Menu],
) -> Dict[Alternative, Q] | None:
    """Find exact Luce weights by propagating observed probability ratios."""

    domain = tuple(domain)
    if not normalized(partial, domain):
        return None
    adjacency: Dict[Alternative, list[Tuple[Alternative, Q]]] = {
        x: [] for x in X
    }
    for menu in domain:
        for x, y in combinations(menu, 2):
            ratio = Q(partial[(menu, x)]) / Q(partial[(menu, y)])
            adjacency[x].append((y, ratio))
            adjacency[y].append((x, 1 / ratio))

    weights: Dict[Alternative, Q] = {}
    for root in X:
        if root in weights:
            continue
        weights[root] = Q(1)
        stack = [root]
        while stack:
            x = stack.pop()
            for y, ratio_xy in adjacency[x]:
                candidate = weights[x] / ratio_xy
                if y in weights:
                    if weights[y] != candidate:
                        return None
                else:
                    weights[y] = candidate
                    stack.append(y)

    for menu in domain:
        denominator = sum((weights[x] for x in menu), Q(0))
        for x in menu:
            if Q(partial[(menu, x)]) != weights[x] / denominator:
                return None
    return weights


def _matrix_rank(matrix: Sequence[Sequence[Q]]) -> int:
    rows = [[Q(value) for value in row] for row in matrix]
    if not rows:
        return 0
    width = len(rows[0])
    rank = 0
    for column in range(width):
        pivot = next(
            (r for r in range(rank, len(rows)) if rows[r][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for r in range(len(rows)):
            if r != rank and rows[r][column]:
                factor = rows[r][column]
                rows[r] = [
                    left - factor * right
                    for left, right in zip(rows[r], rows[rank])
                ]
        rank += 1
    return rank


def _independent_rows(matrix: Sequence[Sequence[Q]]) -> Tuple[int, ...]:
    chosen: list[int] = []
    current: list[Sequence[Q]] = []
    rank = 0
    for index, row in enumerate(matrix):
        candidate = current + [row]
        candidate_rank = _matrix_rank(candidate)
        if candidate_rank > rank:
            chosen.append(index)
            current.append(row)
            rank = candidate_rank
    return tuple(chosen)


def _solve_square(matrix: Sequence[Sequence[Q]], rhs: Sequence[Q]):
    width = len(matrix)
    rows = [
        [Q(value) for value in row] + [Q(value_rhs)]
        for row, value_rhs in zip(matrix, rhs)
    ]
    for column in range(width):
        pivot = next(
            (r for r in range(column, width) if rows[r][column]),
            None,
        )
        if pivot is None:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for r in range(width):
            if r != column and rows[r][column]:
                factor = rows[r][column]
                rows[r] = [
                    left - factor * right
                    for left, right in zip(rows[r], rows[column])
                ]
    return tuple(rows[i][-1] for i in range(width))


@lru_cache(maxsize=None)
def _observation_matrix(domain: Tuple[Menu, ...]):
    matrix = [[Q(1) for _ in RANKINGS]]
    for menu in domain:
        for choice in menu:
            matrix.append(
                [
                    Q(int(next(x for x in ranking if x in menu) == choice))
                    for ranking in RANKINGS
                ]
            )
    return tuple(tuple(row) for row in matrix)


@lru_cache(maxsize=None)
def _observation_linear_data(domain: Tuple[Menu, ...]):
    matrix = _observation_matrix(domain)
    return matrix, _independent_rows(matrix)


def observation_system(partial: Mapping[Event, Q], domain: Sequence[Menu]):
    domain = tuple(domain)
    matrix = _observation_matrix(domain)
    rhs = [Q(1)]
    for menu in domain:
        for choice in menu:
            rhs.append(Q(partial[(menu, choice)]))
    return matrix, rhs


def rum_completion(
    partial: Mapping[Event, Q],
    domain: Sequence[Menu],
) -> Dict[Ranking, Q] | None:
    """Return the average of all exact basic feasible ranking mixtures."""

    domain = tuple(domain)
    if not normalized(partial, domain):
        return None
    matrix, rhs = observation_system(partial, domain)
    _, row_indices = _observation_linear_data(domain)
    rank = len(row_indices)
    reduced_matrix = [matrix[i] for i in row_indices]
    reduced_rhs = [rhs[i] for i in row_indices]

    feasible: list[Tuple[Q, ...]] = []
    for columns in combinations(range(len(RANKINGS)), rank):
        square = [
            [reduced_matrix[row][column] for column in columns]
            for row in range(rank)
        ]
        solution = _solve_square(square, reduced_rhs)
        if solution is None or any(value < 0 for value in solution):
            continue
        candidate = [Q(0) for _ in RANKINGS]
        for column, value in zip(columns, solution):
            candidate[column] = value
        if all(
            sum(
                coefficient * value
                for coefficient, value in zip(row, candidate)
            )
            == target
            for row, target in zip(matrix, rhs)
        ):
            candidate_tuple = tuple(candidate)
            if candidate_tuple not in feasible:
                feasible.append(candidate_tuple)
    if not feasible:
        return None
    averaged = tuple(
        sum((candidate[index] for candidate in feasible), Q(0))
        / len(feasible)
        for index in range(len(RANKINGS))
    )
    return dict(zip(RANKINGS, averaged))


def full_kernel_from_mixture(mixture: Mapping[Ranking, Q]) -> Kernel:
    return {
        (menu, choice): sum(
            Q(value)
            for ranking, value in mixture.items()
            if next(x for x in ranking if x in menu) == choice
        )
        for menu in ALL_MENUS
        for choice in menu
    }


def is_luce_full(kernel: Mapping[Event, Q]) -> bool:
    return scalar_completion(kernel, ALL_MENUS) is not None


def _full_rum_by_block_marschak(kernel: Mapping[Event, Q]) -> bool:
    for lower_size in range(1, len(X) + 1):
        for lower in combinations(X, lower_size):
            missing = tuple(x for x in X if x not in lower)
            for choice in lower:
                value = Q(0)
                for added_size in range(len(missing) + 1):
                    for added in combinations(missing, added_size):
                        upper_set = set(lower).union(added)
                        upper = tuple(x for x in X if x in upper_set)
                        probability = (
                            Q(1)
                            if len(upper) == 1
                            else Q(kernel[(upper, choice)])
                        )
                        value += (
                            -1 if added_size % 2 else 1
                        ) * probability
                if value < 0:
                    return False
    return True


def plackett_luce_mixture(weights: Mapping[Alternative, Q]) -> Dict[Ranking, Q]:
    mixture = {}
    for ranking in RANKINGS:
        remaining = list(ranking)
        value = Q(1)
        while len(remaining) > 1:
            first = remaining[0]
            value *= Q(weights[first]) / sum(
                (Q(weights[x]) for x in remaining), Q(0)
            )
            remaining.pop(0)
        mixture[ranking] = value
    assert all(value > 0 for value in mixture.values())
    assert sum(mixture.values(), Q(0)) == 1
    return mixture


def _nullspace(matrix: Sequence[Sequence[Q]]) -> Tuple[Tuple[Q, ...], ...]:
    rows = [[Q(value) for value in row] for row in matrix]
    width = len(rows[0])
    pivot_row = 0
    pivots: list[int] = []
    for column in range(width):
        pivot = next(
            (r for r in range(pivot_row, len(rows)) if rows[r][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for r in range(len(rows)):
            if r != pivot_row and rows[r][column]:
                factor = rows[r][column]
                rows[r] = [
                    left - factor * right
                    for left, right in zip(rows[r], rows[pivot_row])
                ]
        pivots.append(column)
        pivot_row += 1
    free = [column for column in range(width) if column not in pivots]
    basis = []
    for free_column in free:
        vector = [Q(0) for _ in range(width)]
        vector[free_column] = Q(1)
        for row, pivot_column in enumerate(pivots):
            vector[pivot_column] = -rows[row][free_column]
        basis.append(tuple(vector))
    return tuple(basis)


def nonluce_rum_completion(
    partial: Mapping[Event, Q],
    domain: Sequence[Menu],
    weights: Mapping[Alternative, Q],
) -> Kernel:
    """Construct a RUM completion outside Luce for every proper domain."""

    domain = tuple(domain)
    if set(domain) == set(ALL_MENUS):
        raise ValueError("domain is complete")
    base = plackett_luce_mixture(weights)
    matrix = _observation_matrix(domain)
    basis = _nullspace(matrix)
    if not basis:
        raise AssertionError("proper domain had no ranking-law null direction")

    directions = list(basis)
    if len(basis) > 1:
        for coefficients in product((-2, -1, 0, 1, 2), repeat=len(basis)):
            if not any(coefficients):
                continue
            directions.append(
                tuple(
                    sum(
                        Q(coefficient) * basis[index][coordinate]
                        for index, coefficient in enumerate(coefficients)
                    )
                    for coordinate in range(len(RANKINGS))
                )
            )

    base_vector = tuple(base[ranking] for ranking in RANKINGS)
    for direction in directions:
        if not any(direction):
            continue
        for sign in (Q(1), Q(-1)):
            signed = tuple(sign * value for value in direction)
            limits = [
                base_value / (-delta)
                for base_value, delta in zip(base_vector, signed)
                if delta < 0
            ]
            if not limits:
                continue
            epsilon = min(limits) / 2
            candidate_values = tuple(
                value + epsilon * delta
                for value, delta in zip(base_vector, signed)
            )
            if any(value <= 0 for value in candidate_values):
                continue
            candidate = dict(zip(RANKINGS, candidate_values))
            full = full_kernel_from_mixture(candidate)
            if project(full, domain) != dict(partial):
                continue
            if not is_luce_full(full):
                return full
    raise AssertionError("failed to construct the registered non-Luce RUM completion")


def nonrum_completion(
    partial: Mapping[Event, Q],
    domain: Sequence[Menu],
) -> Kernel:
    """Complete missing menus with an explicit regularity violation."""

    domain = tuple(domain)
    if set(domain) == set(ALL_MENUS):
        raise ValueError("domain is complete")
    full: Kernel = {}
    for menu in (AB, AC, BC):
        if menu in domain:
            for x in menu:
                full[(menu, x)] = Q(partial[(menu, x)])
        else:
            full[(menu, menu[0])] = Q(1, 2)
            full[(menu, menu[1])] = Q(1, 2)

    if ABC not in domain:
        pair_value = full[(AB, "a")]
        triple_a = (Q(1) + pair_value) / 2
        full[(ABC, "a")] = triple_a
        full[(ABC, "b")] = (Q(1) - triple_a) / 2
        full[(ABC, "c")] = (Q(1) - triple_a) / 2
    else:
        for x in ABC:
            full[(ABC, x)] = Q(partial[(ABC, x)])
        missing_pair = next(menu for menu in (AB, AC, BC) if menu not in domain)
        x, y = missing_pair
        full[(missing_pair, x)] = full[(ABC, x)] / 2
        full[(missing_pair, y)] = 1 - full[(missing_pair, x)]

    assert project(full, domain) == dict(partial)
    assert all(value > 0 for value in full.values())
    assert not _full_rum_by_block_marschak(full)
    return full


def full_status(kernel: Mapping[Event, Q]) -> str:
    if is_luce_full(kernel):
        return L
    if _full_rum_by_block_marschak(kernel):
        return R
    return N


def compatible_tiers(
    partial: Mapping[Event, Q],
    domain: Sequence[Menu],
) -> Tuple[str, ...]:
    domain = tuple(domain)
    weights = scalar_completion(partial, domain)
    rum = rum_completion(partial, domain)
    if set(domain) == set(ALL_MENUS):
        return (full_status(partial),)
    if rum is None:
        return (N,)
    if weights is None:
        return (R, N)
    return (L, R, N)
