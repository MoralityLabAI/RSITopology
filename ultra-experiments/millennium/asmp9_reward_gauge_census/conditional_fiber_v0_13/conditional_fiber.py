from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import product
from math import comb, exp, lgamma, log
from typing import Iterable, Sequence


Count = tuple[int, ...]
Edge = tuple[int, int]


def incidence_rows(node_count: int, edges: Sequence[Edge]) -> list[list[int]]:
    rows: list[list[int]] = []
    for source, target in edges:
        if not (0 <= source < node_count and 0 <= target < node_count):
            raise ValueError("edge endpoint outside node universe")
        if source == target:
            raise ValueError("self loops are not supported")
        row = [0] * node_count
        row[source] = -1
        row[target] = 1
        rows.append(row)
    return rows


def vertex_balance(counts: Sequence[int], rows: Sequence[Sequence[int]]) -> tuple[int, ...]:
    if len(counts) != len(rows):
        raise ValueError("count and edge dimensions differ")
    node_count = len(rows[0]) if rows else 0
    return tuple(
        sum(int(counts[e]) * int(rows[e][v]) for e in range(len(rows)))
        for v in range(node_count)
    )


def enumerate_fibers(
    trials: Sequence[int], rows: Sequence[Sequence[int]]
) -> dict[tuple[int, ...], list[Count]]:
    if len(trials) != len(rows):
        raise ValueError("trial and edge dimensions differ")
    fibers: dict[tuple[int, ...], list[Count]] = defaultdict(list)
    for counts in product(*(range(int(n) + 1) for n in trials)):
        fibers[vertex_balance(counts, rows)].append(tuple(counts))
    return dict(fibers)


def _rational_rank(matrix: Sequence[Sequence[int | Fraction]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    row_count = len(work)
    col_count = len(work[0])
    pivot_row = 0
    for col in range(col_count):
        pivot = next(
            (r for r in range(pivot_row, row_count) if work[r][col] != 0),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][col]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [
                    work[row][j] - factor * work[pivot_row][j]
                    for j in range(col_count)
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def graph_cycle_rank(node_count: int, edges: Sequence[Edge]) -> int:
    rank = _rational_rank(incidence_rows(node_count, edges))
    return len(edges) - rank


def fiber_affine_rank(fiber: Sequence[Count]) -> int:
    if len(fiber) <= 1:
        return 0
    origin = fiber[0]
    differences = [
        [point[j] - origin[j] for j in range(len(origin))]
        for point in fiber[1:]
    ]
    return _rational_rank(differences)


def base_measure(counts: Sequence[int], trials: Sequence[int]) -> int:
    value = 1
    for y, n in zip(counts, trials, strict=True):
        if not 0 <= y <= n:
            return 0
        value *= comb(n, y)
    return value


def conditional_weights(
    fiber: Sequence[Count],
    trials: Sequence[int],
    odds: Sequence[Fraction],
) -> dict[Count, Fraction]:
    if len(trials) != len(odds):
        raise ValueError("trial and odds dimensions differ")
    unnormalized: dict[Count, Fraction] = {}
    for counts in fiber:
        value = Fraction(base_measure(counts, trials), 1)
        for ratio, exponent in zip(odds, counts, strict=True):
            if ratio <= 0:
                raise ValueError("odds must be strictly positive")
            value *= ratio**exponent
        unnormalized[counts] = value
    total = sum(unnormalized.values(), Fraction(0, 1))
    if total <= 0:
        raise ValueError("conditional fiber has zero mass")
    return {counts: value / total for counts, value in unnormalized.items()}


def gauge_transform_odds(
    odds: Sequence[Fraction],
    edges: Sequence[Edge],
    vertex_scales: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    if len(odds) != len(edges):
        raise ValueError("odds and edge dimensions differ")
    if any(scale <= 0 for scale in vertex_scales):
        raise ValueError("vertex scales must be strictly positive")
    return tuple(
        ratio * vertex_scales[target] / vertex_scales[source]
        for ratio, (source, target) in zip(odds, edges, strict=True)
    )


def flat_null_state_mass(
    fibers: dict[tuple[int, ...], list[Count]],
    trials: Sequence[int],
) -> dict[int, Fraction]:
    denominator = 2 ** sum(trials)
    mass: dict[int, Fraction] = defaultdict(Fraction)
    for fiber in fibers.values():
        rank = fiber_affine_rank(fiber)
        numerator = sum(base_measure(counts, trials) for counts in fiber)
        mass[rank] += Fraction(numerator, denominator)
    if sum(mass.values(), Fraction(0, 1)) != 1:
        raise AssertionError("flat-null fiber masses do not sum to one")
    return dict(sorted(mass.items()))


def exact_randomized_upper_test(
    cycle_length: int,
    trials_per_edge: int,
    odds_ratio: Fraction,
    alpha: Fraction,
) -> dict[str, object]:
    if cycle_length < 2 or trials_per_edge < 1:
        raise ValueError("cycle length and trials must be positive")
    if odds_ratio <= 1:
        raise ValueError("one-sided alternative odds ratio must exceed one")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0,1)")

    n = trials_per_edge
    k = cycle_length
    numerator = odds_ratio.numerator
    denominator = odds_ratio.denominator
    null_weights = [comb(n, z) ** k for z in range(n + 1)]
    alt_weights = [
        null_weights[z] * numerator**z * denominator ** (n - z)
        for z in range(n + 1)
    ]
    null_total = sum(null_weights)
    alt_total = sum(alt_weights)

    null_tail_above = Fraction(0, 1)
    alt_tail_above = Fraction(0, 1)
    boundary = 0
    randomization = Fraction(0, 1)
    for z in range(n, -1, -1):
        p0 = Fraction(null_weights[z], null_total)
        if null_tail_above <= alpha <= null_tail_above + p0:
            boundary = z
            randomization = (alpha - null_tail_above) / p0
            break
        null_tail_above += p0
        alt_tail_above += Fraction(alt_weights[z], alt_total)
    else:
        raise AssertionError("failed to locate randomized rejection boundary")

    power = alt_tail_above + randomization * Fraction(
        alt_weights[boundary], alt_total
    )
    size = null_tail_above + randomization * Fraction(
        null_weights[boundary], null_total
    )
    return {
        "boundary": boundary,
        "randomization": randomization,
        "size": size,
        "power": power,
    }


def conditional_power_float(
    cycle_length: int,
    trials_per_edge: int,
    odds_ratio: float,
    alpha: float,
) -> float:
    n = trials_per_edge
    k = cycle_length
    if n < 1 or k < 2 or odds_ratio <= 1 or not 0 < alpha < 1:
        raise ValueError("invalid conditional-power arguments")
    log_r = log(odds_ratio)
    log_null = [
        k * (lgamma(n + 1) - lgamma(z + 1) - lgamma(n - z + 1))
        for z in range(n + 1)
    ]
    max0 = max(log_null)
    null = [exp(value - max0) for value in log_null]
    total0 = sum(null)
    p0 = [value / total0 for value in null]

    log_alt = [value + z * log_r for z, value in enumerate(log_null)]
    max1 = max(log_alt)
    alt = [exp(value - max1) for value in log_alt]
    total1 = sum(alt)
    p1 = [value / total1 for value in alt]

    tail0 = 0.0
    tail1 = 0.0
    for z in range(n, -1, -1):
        if tail0 <= alpha <= tail0 + p0[z] + 1e-15:
            gamma = min(1.0, max(0.0, (alpha - tail0) / p0[z]))
            return tail1 + gamma * p1[z]
        tail0 += p0[z]
        tail1 += p1[z]
    raise AssertionError("failed to locate floating rejection boundary")


def first_power_attainment(
    cycle_length: int,
    odds_ratio: Fraction,
    alpha: Fraction,
    target_power: Fraction,
    maximum_trials: int,
) -> dict[str, object]:
    powers: list[float] = []
    candidate: int | None = None
    for n in range(1, maximum_trials + 1):
        power = conditional_power_float(
            cycle_length,
            n,
            float(odds_ratio),
            float(alpha),
        )
        powers.append(power)
        if power >= float(target_power):
            candidate = n
            break
    if candidate is None:
        return {
            "status": "not_reached",
            "maximum_trials": maximum_trials,
            "maximum_power": powers[-1],
        }

    exact = exact_randomized_upper_test(
        cycle_length, candidate, odds_ratio, alpha
    )
    while exact["power"] < target_power:
        candidate += 1
        if candidate > maximum_trials:
            return {
                "status": "not_reached",
                "maximum_trials": maximum_trials,
                "maximum_power": float(exact["power"]),
            }
        exact = exact_randomized_upper_test(
            cycle_length, candidate, odds_ratio, alpha
        )
    previous = (
        exact_randomized_upper_test(
            cycle_length, candidate - 1, odds_ratio, alpha
        )
        if candidate > 1
        else None
    )
    return {
        "status": "reached",
        "trials_per_edge": candidate,
        "exact_test": exact,
        "previous_power": previous["power"] if previous else Fraction(0, 1),
        "pre_attainment_power_decrease_count": sum(
            powers[i + 1] + 1e-12 < powers[i]
            for i in range(len(powers) - 1)
        ),
    }


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"
