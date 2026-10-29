"""Exact finite stochastic-choice classification for ASMP-9 v0.54."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations, product
from typing import Dict, Iterable, Iterator, Mapping, Sequence, Tuple


Alternative = str
Menu = Tuple[Alternative, ...]
Event = Tuple[Menu, Alternative]
Kernel = Dict[Event, Fraction]
Ranking = Tuple[Alternative, ...]


SCALAR_LUCE = "scalar_luce"
RANDOM_UTILITY_NON_LUCE = "random_utility_non_luce"
NO_RANDOM_UTILITY = "no_random_utility_representation"


@dataclass(frozen=True)
class Classification:
    status: str
    luce_weights: Tuple[Tuple[Alternative, Fraction], ...] | None
    ranking_mixture: Tuple[Tuple[Ranking, Fraction], ...] | None
    negative_block_marschak: Tuple[Alternative, Menu, Fraction] | None


def canonical_menu(items: Iterable[Alternative], universe: Sequence[Alternative]) -> Menu:
    wanted = set(items)
    return tuple(x for x in universe if x in wanted)


def menus(universe: Sequence[Alternative], include_singletons: bool = False) -> Iterator[Menu]:
    start = 1 if include_singletons else 2
    for size in range(start, len(universe) + 1):
        yield from combinations(tuple(universe), size)


def probability(
    kernel: Mapping[Event, Fraction],
    menu: Menu,
    choice: Alternative,
) -> Fraction:
    if len(menu) == 1:
        if menu[0] != choice:
            raise KeyError((menu, choice))
        return Fraction(1)
    return Fraction(kernel[(menu, choice)])


def validate_kernel(kernel: Mapping[Event, Fraction], universe: Sequence[Alternative]) -> None:
    universe = tuple(universe)
    for menu in menus(universe):
        values = []
        for choice in menu:
            key = (menu, choice)
            if key not in kernel:
                raise ValueError(f"missing choice event {key!r}")
            value = Fraction(kernel[key])
            if value < 0:
                raise ValueError(f"negative choice probability {key!r}")
            values.append(value)
        if sum(values, Fraction(0)) != 1:
            raise ValueError(f"probabilities do not normalize on {menu!r}")

    expected = {(menu, choice) for menu in menus(universe) for choice in menu}
    extra = set(kernel).difference(expected)
    if extra:
        raise ValueError(f"unexpected events: {sorted(extra)!r}")


def is_strictly_positive(kernel: Mapping[Event, Fraction]) -> bool:
    return all(Fraction(value) > 0 for value in kernel.values())


def luce_weights(
    kernel: Mapping[Event, Fraction],
    universe: Sequence[Alternative],
) -> Dict[Alternative, Fraction] | None:
    """Return a normalized Luce ratio scale or None.

    Full-menu probabilities provide a canonical normalization.
    """

    universe = tuple(universe)
    validate_kernel(kernel, universe)
    if not is_strictly_positive(kernel):
        return None

    full = tuple(universe)
    weights = {choice: probability(kernel, full, choice) for choice in universe}
    for menu in menus(universe):
        denominator = sum((weights[x] for x in menu), Fraction(0))
        for choice in menu:
            if probability(kernel, menu, choice) != weights[choice] / denominator:
                return None
    return weights


def block_marschak_polynomial(
    kernel: Mapping[Event, Fraction],
    universe: Sequence[Alternative],
    choice: Alternative,
    lower_menu: Menu,
) -> Fraction:
    """Compute the exact Block-Marschak alternating sum q(choice, lower_menu)."""

    universe = tuple(universe)
    lower_menu = canonical_menu(lower_menu, universe)
    if choice not in lower_menu:
        raise ValueError("choice must lie in the lower menu")

    missing = tuple(x for x in universe if x not in lower_menu)
    total = Fraction(0)
    for size in range(len(missing) + 1):
        for added in combinations(missing, size):
            upper = canonical_menu((*lower_menu, *added), universe)
            sign = -1 if size % 2 else 1
            total += sign * probability(kernel, upper, choice)
    return total


def block_marschak_table(
    kernel: Mapping[Event, Fraction],
    universe: Sequence[Alternative],
) -> Dict[Tuple[Alternative, Menu], Fraction]:
    universe = tuple(universe)
    validate_kernel(kernel, universe)
    return {
        (choice, menu): block_marschak_polynomial(kernel, universe, choice, menu)
        for menu in menus(universe, include_singletons=True)
        for choice in menu
    }


def _rref_solve_unique(
    matrix: Sequence[Sequence[Fraction]],
    rhs: Sequence[Fraction],
) -> Tuple[Fraction, ...] | None:
    """Solve an overdetermined exact system when it has a unique solution."""

    if len(matrix) != len(rhs):
        raise ValueError("matrix/rhs row mismatch")
    if not matrix:
        return tuple()
    width = len(matrix[0])
    rows = [
        [Fraction(value) for value in row] + [Fraction(value_rhs)]
        for row, value_rhs in zip(matrix, rhs)
    ]
    if any(len(row) != width + 1 for row in rows):
        raise ValueError("ragged matrix")

    pivot_row = 0
    pivot_columns: list[int] = []
    for column in range(width):
        found = next(
            (r for r in range(pivot_row, len(rows)) if rows[r][column] != 0),
            None,
        )
        if found is None:
            continue
        rows[pivot_row], rows[found] = rows[found], rows[pivot_row]
        pivot = rows[pivot_row][column]
        rows[pivot_row] = [value / pivot for value in rows[pivot_row]]
        for r in range(len(rows)):
            if r == pivot_row:
                continue
            factor = rows[r][column]
            if factor:
                rows[r] = [
                    left - factor * right
                    for left, right in zip(rows[r], rows[pivot_row])
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break

    for row in rows:
        if all(value == 0 for value in row[:width]) and row[width] != 0:
            return None
    if len(pivot_columns) != width:
        raise ValueError("registered three-alternative system was not uniquely identified")

    solution = [Fraction(0) for _ in range(width)]
    for row_index, column in enumerate(pivot_columns):
        solution[column] = rows[row_index][width]
    return tuple(solution)


def ranking_mixture(
    kernel: Mapping[Event, Fraction],
    universe: Sequence[Alternative],
) -> Dict[Ranking, Fraction] | None:
    """Recover the exact ranking law for the registered three-item universe."""

    universe = tuple(universe)
    if len(universe) != 3:
        raise ValueError("exact ranking recovery is registered only for three alternatives")
    validate_kernel(kernel, universe)
    rankings = tuple(permutations(universe))

    matrix: list[list[Fraction]] = []
    rhs: list[Fraction] = []
    matrix.append([Fraction(1) for _ in rankings])
    rhs.append(Fraction(1))
    for menu in menus(universe):
        for choice in menu:
            matrix.append(
                [
                    Fraction(int(next(x for x in ranking if x in menu) == choice))
                    for ranking in rankings
                ]
            )
            rhs.append(probability(kernel, menu, choice))

    solution = _rref_solve_unique(matrix, rhs)
    if solution is None or any(value < 0 for value in solution):
        return None
    mixture = dict(zip(rankings, solution))
    if any(
        sum(
            value
            for ranking, value in mixture.items()
            if next(x for x in ranking if x in menu) == choice
        )
        != probability(kernel, menu, choice)
        for menu in menus(universe)
        for choice in menu
    ):
        raise AssertionError("ranking mixture did not reproduce the kernel")
    return mixture


def classify(
    kernel: Mapping[Event, Fraction],
    universe: Sequence[Alternative] = ("a", "b", "c"),
) -> Classification:
    universe = tuple(universe)
    validate_kernel(kernel, universe)

    weights = luce_weights(kernel, universe)
    mixture = ranking_mixture(kernel, universe)
    bm_table = block_marschak_table(kernel, universe)
    negative = [
        (choice, menu, value)
        for (choice, menu), value in bm_table.items()
        if value < 0
    ]

    if (mixture is None) != bool(negative):
        raise AssertionError("Falmagne and ranking-simplex classifiers disagree")

    if weights is not None:
        if mixture is None:
            raise AssertionError("Luce kernel lacked a random-utility representation")
        return Classification(
            SCALAR_LUCE,
            tuple(weights.items()),
            tuple(mixture.items()),
            None,
        )
    if mixture is not None:
        return Classification(
            RANDOM_UTILITY_NON_LUCE,
            None,
            tuple(mixture.items()),
            None,
        )
    return Classification(
        NO_RANDOM_UTILITY,
        None,
        None,
        min(negative, key=lambda item: (item[2], item[0], item[1])),
    )


def make_kernel(
    pair_a_ab: Fraction,
    pair_a_ac: Fraction,
    pair_b_bc: Fraction,
    triple: Tuple[Fraction, Fraction, Fraction],
    universe: Sequence[Alternative] = ("a", "b", "c"),
) -> Kernel:
    universe = tuple(universe)
    if universe != ("a", "b", "c"):
        raise ValueError("registered constructor uses alternatives a,b,c")
    a, b, c = universe
    kernel: Kernel = {
        ((a, b), a): Fraction(pair_a_ab),
        ((a, b), b): 1 - Fraction(pair_a_ab),
        ((a, c), a): Fraction(pair_a_ac),
        ((a, c), c): 1 - Fraction(pair_a_ac),
        ((b, c), b): Fraction(pair_b_bc),
        ((b, c), c): 1 - Fraction(pair_b_bc),
        ((a, b, c), a): Fraction(triple[0]),
        ((a, b, c), b): Fraction(triple[1]),
        ((a, b, c), c): Fraction(triple[2]),
    }
    validate_kernel(kernel, universe)
    return kernel


def kernel_from_ranking_mixture(
    mixture: Mapping[Ranking, Fraction],
    universe: Sequence[Alternative] = ("a", "b", "c"),
) -> Kernel:
    universe = tuple(universe)
    mixture = {tuple(ranking): Fraction(value) for ranking, value in mixture.items()}
    if sum(mixture.values(), Fraction(0)) != 1 or any(v < 0 for v in mixture.values()):
        raise ValueError("invalid ranking mixture")
    expected = set(permutations(universe))
    if not set(mixture).issubset(expected):
        raise ValueError("ranking outside universe")
    kernel: Kernel = {}
    for menu in menus(universe):
        for choice in menu:
            kernel[(menu, choice)] = sum(
                value
                for ranking, value in mixture.items()
                if next(x for x in ranking if x in menu) == choice
            )
    validate_kernel(kernel, universe)
    return kernel


def denominator_six_census() -> Iterator[Kernel]:
    """Enumerate all 1/6-grid kernels that are positive on every event."""

    denominator = 6
    pair_values = tuple(Fraction(k, denominator) for k in range(1, denominator))
    triple_compositions = [
        (Fraction(a, denominator), Fraction(b, denominator), Fraction(c, denominator))
        for a in range(1, denominator)
        for b in range(1, denominator)
        for c in range(1, denominator)
        if a + b + c == denominator
    ]
    for pair_ab, pair_ac, pair_bc, triple in product(
        pair_values, pair_values, pair_values, triple_compositions
    ):
        yield make_kernel(pair_ab, pair_ac, pair_bc, triple)


def canonical_witnesses() -> Dict[str, Kernel]:
    scalar = make_kernel(
        Fraction(1, 3),
        Fraction(1, 4),
        Fraction(2, 5),
        (Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)),
    )
    middle = kernel_from_ranking_mixture(
        {
            ("a", "b", "c"): Fraction(1, 3),
            ("b", "c", "a"): Fraction(1, 3),
            ("c", "a", "b"): Fraction(1, 3),
        }
    )
    none = make_kernel(
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(1, 2),
        (Fraction(3, 4), Fraction(1, 8), Fraction(1, 8)),
    )
    scalar_access = make_kernel(
        Fraction(1, 2),
        Fraction(1, 2),
        Fraction(1, 2),
        (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)),
    )
    return {
        "scalar": scalar,
        "random_utility_non_luce": middle,
        "none": none,
        "scalar_access": scalar_access,
    }


def pair_projection(kernel: Mapping[Event, Fraction]) -> Tuple[Tuple[Event, Fraction], ...]:
    return tuple(sorted((event, value) for event, value in kernel.items() if len(event[0]) == 2))

