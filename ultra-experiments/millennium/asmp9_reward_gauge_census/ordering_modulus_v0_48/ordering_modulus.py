"""Exact ordering-dependent Buehler bounds for finite experiments.

Development instrument for ASMP-9 v0.48.  It treats an evidence ordering as
part of the access object, computes the smallest nondecreasing honest direct
upper bound under that ordering, and exhausts all orderings for small outcome
spaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import permutations, product
from math import comb, factorial
from typing import Hashable, Mapping, Sequence


Parameter = Hashable
Outcome = tuple[int, ...]


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def count_outcomes(allocation: Sequence[int]) -> tuple[Outcome, ...]:
    allocation = tuple(int(value) for value in allocation)
    if not allocation or any(value < 1 for value in allocation):
        raise ValueError("allocation must contain positive counts")
    return tuple(
        product(*(range(samples + 1) for samples in allocation))
    )


def count_probability(
    parameter: Sequence[object],
    allocation: Sequence[int],
    outcome: Sequence[int],
) -> Q:
    parameter = tuple(q(value) for value in parameter)
    allocation = tuple(int(value) for value in allocation)
    outcome = tuple(int(value) for value in outcome)
    if not (
        len(parameter) == len(allocation) == len(outcome)
        and allocation
    ):
        raise ValueError("parameter, allocation, and outcome widths differ")
    if any(not Q(0) <= value <= Q(1, 2) for value in parameter):
        raise ValueError("channel rate leaves [0,1/2]")
    if any(
        samples < 1 or errors < 0 or errors > samples
        for samples, errors in zip(allocation, outcome)
    ):
        raise ValueError("invalid binomial count outcome")
    result = Q(1)
    for flip, samples, errors in zip(
        parameter, allocation, outcome
    ):
        result *= (
            Q(comb(samples, errors))
            * flip**errors
            * (Q(1) - flip) ** (samples - errors)
        )
    return result


def experiment_rows(
    parameters: Sequence[Parameter],
    allocation: Sequence[int],
) -> tuple[tuple[Outcome, ...], dict[Parameter, tuple[Q, ...]]]:
    parameters = tuple(parameters)
    if not parameters or len(set(parameters)) != len(parameters):
        raise ValueError("parameter universe must be nonempty and unique")
    outcomes = count_outcomes(allocation)
    rows = {
        parameter: tuple(
            count_probability(parameter, allocation, outcome)
            for outcome in outcomes
        )
        for parameter in parameters
    }
    if any(sum(row, Q(0)) != 1 for row in rows.values()):
        raise AssertionError("experiment row does not sum to one")
    return outcomes, rows


def uniform_parameter_mixture(
    probabilities: Mapping[Parameter, Sequence[Q]],
) -> tuple[Q, ...]:
    if not probabilities:
        raise ValueError("empty experiment")
    widths = {len(tuple(row)) for row in probabilities.values()}
    if len(widths) != 1:
        raise ValueError("experiment rows have different widths")
    denominator = Q(len(probabilities))
    result = tuple(
        sum(
            (q(row[index]) for row in probabilities.values()),
            Q(0),
        )
        / denominator
        for index in range(next(iter(widths)))
    )
    if sum(result, Q(0)) != 1:
        raise AssertionError("reference mixture does not sum to one")
    return result


def prefix_probability_tables(
    probabilities: Mapping[Parameter, Sequence[Q]],
) -> dict[Parameter, tuple[Q, ...]]:
    """Return exact subset probabilities indexed by outcome bitmask."""

    if not probabilities:
        raise ValueError("empty experiment")
    rows = {
        parameter: tuple(q(value) for value in row)
        for parameter, row in probabilities.items()
    }
    widths = {len(row) for row in rows.values()}
    if len(widths) != 1:
        raise ValueError("experiment rows have different widths")
    width = next(iter(widths))
    if width > 20:
        raise ValueError("exact subset table is capped at 20 outcomes")
    result = {}
    for parameter, row in rows.items():
        subset = [Q(0)] * (1 << width)
        for mask in range(1, 1 << width):
            bit = mask & -mask
            index = bit.bit_length() - 1
            subset[mask] = subset[mask ^ bit] + row[index]
        result[parameter] = tuple(subset)
    return result


def buehler_subset_bounds(
    risks: Mapping[Parameter, object],
    subset_probabilities: Mapping[Parameter, Sequence[Q]],
    alpha: object,
) -> tuple[Q, ...]:
    """Bound associated with every possible prefix subset."""

    alpha = q(alpha)
    risks = {parameter: q(value) for parameter, value in risks.items()}
    if not 0 < alpha < 1 or set(risks) != set(subset_probabilities):
        raise ValueError("invalid risk/subset universe")
    widths = {len(tuple(row)) for row in subset_probabilities.values()}
    if len(widths) != 1:
        raise ValueError("subset tables have different widths")
    result = []
    for mask in range(next(iter(widths))):
        eligible = [
            risks[parameter]
            for parameter, row in subset_probabilities.items()
            if q(row[mask]) > alpha
        ]
        result.append(max(eligible, default=Q(0)))
    return tuple(result)


def ordering_cost(
    ordering: Sequence[int],
    subset_bounds: Sequence[Q],
    reference_weights: Sequence[Q],
) -> Q:
    ordering = tuple(int(value) for value in ordering)
    reference_weights = tuple(q(value) for value in reference_weights)
    width = len(reference_weights)
    if sorted(ordering) != list(range(width)):
        raise ValueError("ordering is not a permutation")
    if len(subset_bounds) != 1 << width:
        raise ValueError("subset-bound table has wrong width")
    mask = 0
    result = Q(0)
    for index in ordering:
        mask |= 1 << index
        result += reference_weights[index] * q(subset_bounds[mask])
    return result


def ordered_bound_vector(
    ordering: Sequence[int],
    subset_bounds: Sequence[Q],
) -> tuple[Q, ...]:
    """Return the reported bound at each outcome under one ordering."""

    ordering = tuple(int(value) for value in ordering)
    width = len(ordering)
    if sorted(ordering) != list(range(width)):
        raise ValueError("ordering is not a permutation")
    if len(subset_bounds) != 1 << width:
        raise ValueError("subset-bound table has wrong width")
    result = [Q(0)] * width
    mask = 0
    for index in ordering:
        mask |= 1 << index
        result[index] = q(subset_bounds[mask])
    return tuple(result)


def coverage_by_parameter(
    risks: Mapping[Parameter, object],
    probabilities: Mapping[Parameter, Sequence[Q]],
    reported_bounds: Sequence[Q],
) -> dict[Parameter, Q]:
    """Exact coverage of one direct upper confidence procedure."""

    risks = {parameter: q(value) for parameter, value in risks.items()}
    if set(risks) != set(probabilities):
        raise ValueError("risk and probability universes differ")
    bounds = tuple(q(value) for value in reported_bounds)
    result = {}
    for parameter, row in probabilities.items():
        row = tuple(q(value) for value in row)
        if len(row) != len(bounds):
            raise ValueError("bound and experiment widths differ")
        result[parameter] = sum(
            (
                probability
                for probability, bound in zip(row, bounds)
                if risks[parameter] <= bound
            ),
            Q(0),
        )
    return result


@dataclass(frozen=True)
class OrderingCensus:
    outcome_count: int
    order_count: int
    optimum: Q
    optimizer_count: int
    optimizers: tuple[tuple[int, ...], ...]

    def jsonable(
        self, outcomes: Sequence[Outcome] | None = None
    ) -> dict:
        payload = {
            "outcome_count": self.outcome_count,
            "order_count": self.order_count,
            "optimum": qstr(self.optimum),
            "optimizer_count": self.optimizer_count,
            "optimizer_indices": [
                list(ordering) for ordering in self.optimizers
            ],
        }
        if outcomes is not None:
            outcomes = tuple(outcomes)
            payload["optimizer_outcomes"] = [
                [list(outcomes[index]) for index in ordering]
                for ordering in self.optimizers
            ]
        return payload


@dataclass(frozen=True)
class DynamicOrderingCensus:
    outcome_count: int
    order_count: int
    optimum: Q
    optimizer_count: int
    lexicographic_optimizer: tuple[int, ...]

    def jsonable(
        self, outcomes: Sequence[Outcome] | None = None
    ) -> dict:
        payload = {
            "outcome_count": self.outcome_count,
            "order_count": self.order_count,
            "optimum": qstr(self.optimum),
            "optimizer_count": self.optimizer_count,
            "lexicographic_optimizer_indices": list(
                self.lexicographic_optimizer
            ),
        }
        if outcomes is not None:
            outcomes = tuple(outcomes)
            payload["lexicographic_optimizer_outcomes"] = [
                list(outcomes[index])
                for index in self.lexicographic_optimizer
            ]
        return payload


def _dynamic_ordering_tables(
    subset_bounds: Sequence[Q],
    reference_weights: Sequence[Q],
) -> tuple[list[Q], list[int], list[tuple[int, ...]]]:
    reference_weights = tuple(q(value) for value in reference_weights)
    width = len(reference_weights)
    if width > 20:
        raise ValueError("subset dynamic program is capped at 20 outcomes")
    if len(subset_bounds) != 1 << width:
        raise ValueError("subset-bound table has wrong width")
    size = 1 << width
    values = [Q(0)] * size
    counts = [0] * size
    orders: list[tuple[int, ...]] = [tuple()] * size
    counts[0] = 1
    for mask in range(1, size):
        bound = q(subset_bounds[mask])
        best: Q | None = None
        count = 0
        lex: tuple[int, ...] | None = None
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            index = bit.bit_length() - 1
            previous = mask ^ bit
            candidate = (
                values[previous]
                + reference_weights[index] * bound
            )
            candidate_order = orders[previous] + (index,)
            if best is None or candidate < best:
                best = candidate
                count = counts[previous]
                lex = candidate_order
            elif candidate == best:
                count += counts[previous]
                if lex is None or candidate_order < lex:
                    lex = candidate_order
            remaining ^= bit
        if best is None or lex is None:
            raise AssertionError("dynamic state has no predecessor")
        values[mask] = best
        counts[mask] = count
        orders[mask] = lex
    return values, counts, orders


def dynamic_ordering_census(
    subset_bounds: Sequence[Q],
    reference_weights: Sequence[Q],
) -> DynamicOrderingCensus:
    values, counts, orders = _dynamic_ordering_tables(
        subset_bounds, reference_weights
    )
    width = len(tuple(reference_weights))
    return DynamicOrderingCensus(
        outcome_count=width,
        order_count=factorial(width),
        optimum=values[-1],
        optimizer_count=counts[-1],
        lexicographic_optimizer=orders[-1],
    )


def exhaustive_ordering_census(
    subset_bounds: Sequence[Q],
    reference_weights: Sequence[Q],
    keep_optimizers: int | None = None,
) -> OrderingCensus:
    reference_weights = tuple(q(value) for value in reference_weights)
    width = len(reference_weights)
    if width > 9:
        raise ValueError("permutation census is capped at nine outcomes")
    best: Q | None = None
    optimizers = []
    optimizer_count = 0
    for ordering in permutations(range(width)):
        value = ordering_cost(
            ordering, subset_bounds, reference_weights
        )
        if best is None or value < best:
            best = value
            optimizers = [ordering]
            optimizer_count = 1
        elif value == best:
            optimizer_count += 1
            if keep_optimizers is None or len(optimizers) < keep_optimizers:
                optimizers.append(ordering)
    if best is None:
        raise AssertionError("ordering universe is empty")
    return OrderingCensus(
        outcome_count=width,
        order_count=factorial(width),
        optimum=best,
        optimizer_count=optimizer_count,
        optimizers=tuple(optimizers),
    )


def cross_costs(
    first: OrderingCensus,
    first_bounds: Sequence[Q],
    second: OrderingCensus,
    second_bounds: Sequence[Q],
    reference_weights: Sequence[Q],
) -> dict:
    """Audit common optimality and each objective on the other's optima."""

    first_orders = set(first.optimizers)
    second_orders = set(second.optimizers)
    if first.optimizer_count != len(first_orders):
        raise ValueError(
            "cross audit requires every optimizer to be retained"
        )
    if second.optimizer_count != len(second_orders):
        raise ValueError(
            "cross audit requires every optimizer to be retained"
        )
    first_on_second = min(
        ordering_cost(ordering, first_bounds, reference_weights)
        for ordering in second_orders
    )
    second_on_first = min(
        ordering_cost(ordering, second_bounds, reference_weights)
        for ordering in first_orders
    )
    return {
        "common_optimizer_count": len(
            first_orders.intersection(second_orders)
        ),
        "first_optimum": qstr(first.optimum),
        "first_best_on_second_optima": qstr(first_on_second),
        "first_cross_regret": qstr(first_on_second - first.optimum),
        "second_optimum": qstr(second.optimum),
        "second_best_on_first_optima": qstr(second_on_first),
        "second_cross_regret": qstr(second_on_first - second.optimum),
    }


def exhaustive_cross_audit(
    first_optimum: Q,
    first_bounds: Sequence[Q],
    second_optimum: Q,
    second_bounds: Sequence[Q],
    reference_weights: Sequence[Q],
) -> dict:
    """Cross-audit two optimizer sets without retaining every ordering."""

    reference_weights = tuple(q(value) for value in reference_weights)
    width = len(reference_weights)
    if width > 9:
        raise ValueError("permutation cross audit is capped at nine outcomes")
    common = 0
    first_best_on_second: Q | None = None
    second_best_on_first: Q | None = None
    for ordering in permutations(range(width)):
        first_value = ordering_cost(
            ordering, first_bounds, reference_weights
        )
        second_value = ordering_cost(
            ordering, second_bounds, reference_weights
        )
        if first_value == first_optimum:
            if (
                second_best_on_first is None
                or second_value < second_best_on_first
            ):
                second_best_on_first = second_value
        if second_value == second_optimum:
            if (
                first_best_on_second is None
                or first_value < first_best_on_second
            ):
                first_best_on_second = first_value
        if (
            first_value == first_optimum
            and second_value == second_optimum
        ):
            common += 1
    if first_best_on_second is None or second_best_on_first is None:
        raise AssertionError("registered optima were not attained")
    return {
        "common_optimizer_count": common,
        "first_optimum": qstr(first_optimum),
        "first_best_on_second_optima": qstr(first_best_on_second),
        "first_cross_regret": qstr(
            first_best_on_second - first_optimum
        ),
        "second_optimum": qstr(second_optimum),
        "second_best_on_first_optima": qstr(second_best_on_first),
        "second_cross_regret": qstr(
            second_best_on_first - second_optimum
        ),
    }


def dynamic_cross_audit(
    first_bounds: Sequence[Q],
    second_bounds: Sequence[Q],
    reference_weights: Sequence[Q],
) -> dict:
    """Exact cross-regrets and common-optimum count by subset recursion."""

    reference_weights = tuple(q(value) for value in reference_weights)
    first_values, _, _ = _dynamic_ordering_tables(
        first_bounds, reference_weights
    )
    second_values, _, _ = _dynamic_ordering_tables(
        second_bounds, reference_weights
    )
    size = len(first_values)
    second_on_first: list[Q | None] = [None] * size
    first_on_second: list[Q | None] = [None] * size
    common_counts = [0] * size
    second_on_first[0] = Q(0)
    first_on_second[0] = Q(0)
    common_counts[0] = 1
    for mask in range(1, size):
        first_bound = q(first_bounds[mask])
        second_bound = q(second_bounds[mask])
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            index = bit.bit_length() - 1
            previous = mask ^ bit
            first_step = (
                first_values[previous]
                + reference_weights[index] * first_bound
            )
            second_step = (
                second_values[previous]
                + reference_weights[index] * second_bound
            )
            first_optimal = first_step == first_values[mask]
            second_optimal = second_step == second_values[mask]
            if first_optimal:
                prior = second_on_first[previous]
                if prior is None:
                    raise AssertionError("missing first-optimal prefix")
                candidate = (
                    prior
                    + reference_weights[index] * second_bound
                )
                current = second_on_first[mask]
                if current is None or candidate < current:
                    second_on_first[mask] = candidate
            if second_optimal:
                prior = first_on_second[previous]
                if prior is None:
                    raise AssertionError("missing second-optimal prefix")
                candidate = (
                    prior
                    + reference_weights[index] * first_bound
                )
                current = first_on_second[mask]
                if current is None or candidate < current:
                    first_on_second[mask] = candidate
            if first_optimal and second_optimal:
                common_counts[mask] += common_counts[previous]
            remaining ^= bit
    first_best_on_second = first_on_second[-1]
    second_best_on_first = second_on_first[-1]
    if first_best_on_second is None or second_best_on_first is None:
        raise AssertionError("cross optimum was not attained")
    return {
        "common_optimizer_count": common_counts[-1],
        "first_optimum": qstr(first_values[-1]),
        "first_best_on_second_optima": qstr(first_best_on_second),
        "first_cross_regret": qstr(
            first_best_on_second - first_values[-1]
        ),
        "second_optimum": qstr(second_values[-1]),
        "second_best_on_first_optima": qstr(second_best_on_first),
        "second_cross_regret": qstr(
            second_best_on_first - second_values[-1]
        ),
    }
