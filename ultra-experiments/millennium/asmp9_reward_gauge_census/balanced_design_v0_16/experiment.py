from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Any, Iterable


def parse_fraction(value: str | Fraction | int) -> Fraction:
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


def product(values: Iterable[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def xyz(count: int, epsilon: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    if count < 1:
        raise ValueError("counts must be positive")
    if not 0 <= epsilon <= Fraction(1, 2):
        raise ValueError("epsilon must lie in [0,1/2]")
    r = 1 - epsilon
    s = epsilon
    return 1 - r**count, 1 - s**count, 1 - r**count - s**count


def availability_for_labels(
    counts: tuple[int, ...],
    epsilon: Fraction,
    labels: tuple[int, ...],
) -> Fraction:
    if len(counts) != len(labels) or not counts:
        raise ValueError("count/label dimensions must match and be nonzero")
    no_zero: list[Fraction] = []
    no_full: list[Fraction] = []
    interior: list[Fraction] = []
    for count, label in zip(counts, labels, strict=True):
        x, y, z = xyz(count, epsilon)
        if label == 0:
            no_zero.append(x)
            no_full.append(y)
        elif label == 1:
            no_zero.append(y)
            no_full.append(x)
        else:
            raise ValueError("labels must be zero or one")
        interior.append(z)
    return (
        product(no_zero)
        + product(no_full)
        - product(interior)
    )


def worst_endpoint_availability(
    counts: tuple[int, ...], epsilon: Fraction
) -> tuple[Fraction, list[tuple[int, ...]]]:
    minimum: Fraction | None = None
    witnesses: list[tuple[int, ...]] = []
    for labels in itertools.product((0, 1), repeat=len(counts)):
        value = availability_for_labels(counts, epsilon, labels)
        if minimum is None or value < minimum:
            minimum = value
            witnesses = [labels]
        elif value == minimum:
            witnesses.append(labels)
    if minimum is None:
        raise AssertionError("empty endpoint universe")
    return minimum, witnesses


def balanced_allocation(total: int, length: int) -> tuple[int, ...]:
    quotient, remainder = divmod(total, length)
    if quotient < 1:
        raise ValueError("every edge must receive at least one trial")
    return (
        (quotient,) * (length - remainder)
        + (quotient + 1,) * remainder
    )


def nondecreasing_allocations(
    total: int, length: int, minimum: int = 1
) -> Iterable[tuple[int, ...]]:
    if length == 1:
        if total >= minimum:
            yield (total,)
        return
    for first in range(minimum, total // length + 1):
        for rest in nondecreasing_allocations(
            total - first, length - 1, first
        ):
            yield (first, *rest)


def smoothing_pair(counts: tuple[int, ...]) -> tuple[int, int] | None:
    smallest = min(range(len(counts)), key=counts.__getitem__)
    largest = max(range(len(counts)), key=counts.__getitem__)
    if counts[largest] - counts[smallest] < 2:
        return None
    return smallest, largest


def smooth_once(counts: tuple[int, ...]) -> tuple[int, ...]:
    pair = smoothing_pair(counts)
    if pair is None:
        return counts
    low, high = pair
    result = list(counts)
    result[low] += 1
    result[high] -= 1
    return tuple(result)


def pair_constants(
    other_counts: tuple[int, ...],
    epsilon: Fraction,
    other_labels: tuple[int, ...],
) -> tuple[Fraction, Fraction, Fraction]:
    if len(other_counts) != len(other_labels):
        raise ValueError("other count/label dimensions must match")
    no_zero: list[Fraction] = []
    no_full: list[Fraction] = []
    interior: list[Fraction] = []
    for count, label in zip(other_counts, other_labels, strict=True):
        x, y, z = xyz(count, epsilon)
        no_zero.append(x if label == 0 else y)
        no_full.append(y if label == 0 else x)
        interior.append(z)
    return product(no_zero), product(no_full), product(interior)


def local_branches(
    a: int,
    b: int,
    epsilon: Fraction,
    U: Fraction,
    V: Fraction,
    W: Fraction,
) -> dict[str, Fraction]:
    if a > b:
        a, b = b, a
    if not 0 <= W <= min(U, V):
        raise ValueError("constants must satisfy 0<=W<=min(U,V)")
    M = max(U, V)
    m = min(U, V)
    xa, ya, za = xyz(a, epsilon)
    xb, yb, zb = xyz(b, epsilon)
    same = M * xa * xb + m * ya * yb - W * za * zb
    opposite = M * xa * yb + m * ya * xb - W * za * zb
    E = xa * xb + ya * yb - za * zb
    P = xa * xb + ya * yb
    D = xa * yb + ya * xb - za * zb
    C = xa * yb + ya * xb
    same_decomposition = (
        W * E + (m - W) * P + (M - m) * xa * xb
    )
    opposite_decomposition = (
        W * D + (m - W) * C + (M - m) * xa * yb
    )
    return {
        "same": same,
        "opposite": opposite,
        "minimum": min(same, opposite),
        "E": E,
        "P": P,
        "D": D,
        "C": C,
        "xaxb": xa * xb,
        "yayb": ya * yb,
        "xayb": xa * yb,
        "zazb": za * zb,
        "same_decomposition": same_decomposition,
        "opposite_decomposition": opposite_decomposition,
    }


def direct_local_minimum(
    a: int,
    b: int,
    epsilon: Fraction,
    U: Fraction,
    V: Fraction,
    W: Fraction,
) -> Fraction:
    values = []
    for left, right in itertools.product((0, 1), repeat=2):
        xa, ya, za = xyz(a, epsilon)
        xb, yb, zb = xyz(b, epsilon)
        ua, va = (xa, ya) if left == 0 else (ya, xa)
        ub, vb = (xb, yb) if right == 0 else (yb, xb)
        values.append(U * ua * ub + V * va * vb - W * za * zb)
    return min(values)


def smoothing_certificate(
    a: int,
    b: int,
    epsilon: Fraction,
    U: Fraction,
    V: Fraction,
    W: Fraction,
) -> dict[str, Any]:
    if b - a < 2:
        raise ValueError("smoothing requires b-a>=2")
    before = local_branches(a, b, epsilon, U, V, W)
    after = local_branches(a + 1, b - 1, epsilon, U, V, W)
    direct_before = direct_local_minimum(a, b, epsilon, U, V, W)
    direct_after = direct_local_minimum(
        a + 1, b - 1, epsilon, U, V, W
    )
    return {
        "a": a,
        "b": b,
        "epsilon": fraction_record(epsilon),
        "U": fraction_record(U),
        "V": fraction_record(V),
        "W": fraction_record(W),
        "branch_formula_matches_direct": (
            before["minimum"] == direct_before
            and after["minimum"] == direct_after
        ),
        "same_decomposition_holds": (
            before["same"] == before["same_decomposition"]
            and after["same"] == after["same_decomposition"]
        ),
        "opposite_decomposition_holds": (
            before["opposite"] == before["opposite_decomposition"]
            and after["opposite"] == after["opposite_decomposition"]
        ),
        "same_strictly_improves": after["same"] > before["same"],
        "opposite_strictly_improves": (
            after["opposite"] > before["opposite"]
        ),
        "minimum_strictly_improves": (
            direct_after > direct_before
        ),
        "D_is_invariant": after["D"] == before["D"],
        "E_is_nondecreasing": after["E"] >= before["E"],
        "pair_products_nondecrease": (
            after["xaxb"] > before["xaxb"]
            and after["yayb"] > before["yayb"]
            and after["xayb"] >= before["xayb"]
            and after["zazb"] > before["zazb"]
        ),
        "before_minimum": fraction_record(direct_before),
        "after_minimum": fraction_record(direct_after),
    }


def allocation_census(
    total: int, length: int, epsilon: Fraction
) -> dict[str, Any]:
    records = []
    for allocation in nondecreasing_allocations(total, length):
        value, witnesses = worst_endpoint_availability(
            allocation, epsilon
        )
        smoothed = tuple(sorted(smooth_once(allocation)))
        if smoothed == allocation:
            smoothed_value = value
        else:
            smoothed_value, _ = worst_endpoint_availability(
                smoothed, epsilon
            )
        records.append(
            {
                "allocation": list(allocation),
                "worst": fraction_record(value),
                "witness_count": len(witnesses),
                "smoothed": list(smoothed),
                "smoothing_strict_if_unbalanced": (
                    smoothed == allocation or smoothed_value > value
                ),
            }
        )
    optimum = max(
        parse_fraction(record["worst"]["fraction"])
        for record in records
    )
    optimizers = [
        record["allocation"]
        for record in records
        if parse_fraction(record["worst"]["fraction"]) == optimum
    ]
    balanced = balanced_allocation(total, length)
    balanced_value, _ = worst_endpoint_availability(balanced, epsilon)
    return {
        "cycle_length": length,
        "total_trials": total,
        "epsilon": fraction_record(epsilon),
        "allocation_count": len(records),
        "balanced_allocation": list(balanced),
        "balanced_value": fraction_record(balanced_value),
        "optimum": fraction_record(optimum),
        "optimizers": optimizers,
        "balanced_is_unique_modulo_permutation": (
            optimizers == [list(balanced)]
        ),
        "all_smoothing_steps_strict": all(
            record["smoothing_strict_if_unbalanced"]
            for record in records
        ),
    }


def balanced_worst_closed(
    total: int, length: int, epsilon: Fraction
) -> tuple[Fraction, list[tuple[int, int]]]:
    counts = balanced_allocation(total, length)
    lower = counts[0]
    upper = counts[-1]
    upper_count = total - lower * length
    lower_count = length - upper_count
    xl, yl, zl = xyz(lower, epsilon)
    xu, yu, zu = xyz(upper, epsilon)
    values: list[tuple[Fraction, tuple[int, int]]] = []
    for low_labels_lower in range(lower_count + 1):
        for low_labels_upper in range(upper_count + 1):
            first = (
                xl**low_labels_lower
                * yl ** (lower_count - low_labels_lower)
                * xu**low_labels_upper
                * yu ** (upper_count - low_labels_upper)
            )
            second = (
                yl**low_labels_lower
                * xl ** (lower_count - low_labels_lower)
                * yu**low_labels_upper
                * xu ** (upper_count - low_labels_upper)
            )
            value = (
                first
                + second
                - zl**lower_count * zu**upper_count
            )
            values.append(
                (value, (low_labels_lower, low_labels_upper))
            )
    minimum = min(value for value, _ in values)
    return minimum, [
        witness for value, witness in values if value == minimum
    ]


def minimal_total_trials(
    length: int,
    epsilon: Fraction,
    target: Fraction,
    maximum_total: int = 1_000_000,
) -> int | None:
    if length < 3:
        raise ValueError("the balanced-design theorem requires length>=3")
    if not 0 <= target < 1:
        raise ValueError("target must lie in [0,1)")
    if epsilon == 0:
        return None
    for total in range(length, maximum_total + 1):
        value, _ = balanced_worst_closed(total, length, epsilon)
        if value >= target:
            return total
    return None
