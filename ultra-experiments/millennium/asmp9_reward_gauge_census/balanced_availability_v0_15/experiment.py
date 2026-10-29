from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Any, Iterable


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


def product(values: Iterable[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def availability(
    trials: tuple[int, ...], probabilities: tuple[Fraction, ...]
) -> Fraction:
    if len(trials) != len(probabilities) or not trials:
        raise ValueError("trial/probability dimensions must match and be nonzero")
    no_zero = []
    no_full = []
    interior = []
    for n, probability in zip(trials, probabilities, strict=True):
        if n < 1 or not 0 <= probability <= 1:
            raise ValueError("invalid trials or probability")
        probability_zero = (1 - probability) ** n
        probability_full = probability**n
        no_zero.append(1 - probability_zero)
        no_full.append(1 - probability_full)
        interior.append(1 - probability_zero - probability_full)
    return product(no_zero) + product(no_full) - product(interior)


def vertex_availability_equal(
    cycle_length: int,
    trials_per_edge: int,
    epsilon: Fraction,
    low_edge_count: int,
) -> Fraction:
    if not 0 <= low_edge_count <= cycle_length:
        raise ValueError("invalid low-edge count")
    probabilities = (
        (epsilon,) * low_edge_count
        + (1 - epsilon,) * (cycle_length - low_edge_count)
    )
    return availability(
        (trials_per_edge,) * cycle_length, probabilities
    )


def sharp_min_availability(
    cycle_length: int, trials_per_edge: int, epsilon: Fraction
) -> Fraction:
    if cycle_length < 2 or trials_per_edge < 1:
        raise ValueError("invalid cycle length or trial count")
    if not 0 <= epsilon <= Fraction(1, 2):
        raise ValueError("epsilon must lie in [0,1/2]")
    low = cycle_length // 2
    return vertex_availability_equal(
        cycle_length, trials_per_edge, epsilon, low
    )


def exhaustive_vertex_minimum_equal(
    cycle_length: int, trials_per_edge: int, epsilon: Fraction
) -> tuple[Fraction, list[int]]:
    values = [
        vertex_availability_equal(
            cycle_length, trials_per_edge, epsilon, low_count
        )
        for low_count in range(cycle_length + 1)
    ]
    minimum = min(values)
    return minimum, [
        index for index, value in enumerate(values) if value == minimum
    ]


def one_sided_drift_availability(
    cycle_length: int, trials_per_edge: int, epsilon: Fraction
) -> Fraction:
    return vertex_availability_equal(
        cycle_length, trials_per_edge, epsilon, 1
    )


def v014_crude_lower_bound(
    cycle_length: int, trials_per_edge: int, epsilon: Fraction
) -> Fraction:
    return (
        1 - (1 - epsilon) ** trials_per_edge
    ) ** cycle_length


def minimal_equal_trials(
    cycle_length: int,
    epsilon: Fraction,
    target_availability: Fraction,
    maximum_trials: int = 100_000,
) -> int | None:
    if not 0 <= target_availability < 1:
        raise ValueError("target availability must lie in [0,1)")
    if epsilon == 0:
        return None
    for trials_per_edge in range(1, maximum_trials + 1):
        if (
            sharp_min_availability(
                cycle_length, trials_per_edge, epsilon
            )
            >= target_availability
        ):
            return trials_per_edge
    return None


def endpoint_worst_allocation(
    trials: tuple[int, ...], epsilon: Fraction
) -> tuple[Fraction, list[tuple[int, ...]]]:
    minimum: Fraction | None = None
    witnesses: list[tuple[int, ...]] = []
    for bits in itertools.product((0, 1), repeat=len(trials)):
        probabilities = tuple(
            epsilon if bit == 0 else 1 - epsilon for bit in bits
        )
        value = availability(trials, probabilities)
        if minimum is None or value < minimum:
            minimum = value
            witnesses = [bits]
        elif value == minimum:
            witnesses.append(bits)
    if minimum is None:
        raise AssertionError("empty endpoint universe")
    return minimum, witnesses


def nondecreasing_allocations(
    total_trials: int,
    cycle_length: int,
    minimum: int = 1,
) -> Iterable[tuple[int, ...]]:
    if cycle_length == 1:
        if total_trials >= minimum:
            yield (total_trials,)
        return
    maximum_first = total_trials // cycle_length
    for first in range(minimum, maximum_first + 1):
        for rest in nondecreasing_allocations(
            total_trials - first, cycle_length - 1, first
        ):
            yield (first, *rest)


def balanced_allocation(
    total_trials: int, cycle_length: int
) -> tuple[int, ...]:
    quotient, remainder = divmod(total_trials, cycle_length)
    if quotient < 1:
        raise ValueError("every edge must receive at least one trial")
    return (
        (quotient,) * (cycle_length - remainder)
        + (quotient + 1,) * remainder
    )


def exact_allocation_optima(
    total_trials: int, cycle_length: int, epsilon: Fraction
) -> dict[str, Any]:
    records = []
    for trials in nondecreasing_allocations(
        total_trials, cycle_length
    ):
        worst, witnesses = endpoint_worst_allocation(trials, epsilon)
        records.append((worst, trials, witnesses))
    optimum = max(record[0] for record in records)
    optimizers = [
        {
            "allocation": list(trials),
            "worst_availability": fraction_record(worst),
            "witnesses": [list(witness) for witness in witnesses],
        }
        for worst, trials, witnesses in records
        if worst == optimum
    ]
    balanced = balanced_allocation(total_trials, cycle_length)
    balanced_worst, balanced_witnesses = endpoint_worst_allocation(
        balanced, epsilon
    )
    return {
        "cycle_length": cycle_length,
        "total_trials": total_trials,
        "epsilon": fraction_record(epsilon),
        "allocation_count": len(records),
        "optimum": fraction_record(optimum),
        "optimizers": optimizers,
        "balanced_allocation": list(balanced),
        "balanced_worst_availability": fraction_record(balanced_worst),
        "balanced_witnesses": [
            list(witness) for witness in balanced_witnesses
        ],
        "balanced_is_optimal": balanced_worst == optimum,
    }
