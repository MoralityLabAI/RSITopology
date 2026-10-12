"""Decision-directed sample allocation for ASMP-9 v0.45.

The module precomputes each deterministic policy's target-wise query
occupancy.  A prospective integer allocation then induces simultaneous
per-query KL confidence tolls, policy-specific Pinsker radii, and an exact
robust directed-deficiency upper bound.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
import math
from math import comb
from pathlib import Path
import sys
from typing import Mapping, Sequence


HERE = Path(__file__).resolve().parent
V41 = HERE.parent / "sequential_risk_access_v0_41"
V44 = HERE.parent / "occupancy_information_v0_44"
for path in (V41, V44):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from occupancy_information import (  # noqa: E402
    robust_directed_deficiency_interval,
    sqrt_fraction_upper,
)
from sequential_access import (  # noqa: E402
    DecisionProblem,
    QueryChannel,
    directed_upper_deficiency,
)


RiskVector = tuple[Q, ...]


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


@dataclass(frozen=True)
class OccupancyEnvelope:
    """One policy's center risk and target-by-query expected use counts."""

    code: str
    risk: RiskVector
    occupancy: tuple[tuple[Q, ...], ...]

    def jsonable(self, query_names: Sequence[str]) -> dict:
        return {
            "code": self.code,
            "risk": [qstr(value) for value in self.risk],
            "occupancy": {
                str(target): {
                    name: qstr(self.occupancy[target][index])
                    for index, name in enumerate(query_names)
                }
                for target in range(len(self.occupancy))
            },
        }


def enumerate_policy_occupancies(
    queries: Sequence[QueryChannel],
    problem: DecisionProblem,
    horizon: int,
    query_budgets: Mapping[str, int] | None = None,
) -> tuple[OccupancyEnvelope, ...]:
    """Enumerate unique center-risk/query-occupancy policy generators."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    queries = tuple(queries)
    if len({query.name for query in queries}) != len(queries):
        raise ValueError("query names must be unique")
    if any(
        query.target_count != problem.target_count for query in queries
    ):
        raise ValueError("query and problem target counts differ")
    names = tuple(query.name for query in queries)
    query_by_name = {query.name: query for query in queries}
    if query_budgets is None:
        budgets = tuple([horizon] * len(names))
    else:
        if set(query_budgets) != set(names):
            raise ValueError("query-budget universe differs")
        budgets = tuple(int(query_budgets[name]) for name in names)
        if any(value < 0 for value in budgets):
            raise ValueError("query budgets must be nonnegative")

    zero_occupancy = tuple(
        tuple([Q(0)] * len(names))
        for _ in range(problem.target_count)
    )

    @lru_cache(maxsize=None)
    def build(
        depth: int, remaining: tuple[int, ...]
    ) -> tuple[OccupancyEnvelope, ...]:
        rows: list[OccupancyEnvelope] = []
        for action in range(problem.action_count):
            rows.append(
                OccupancyEnvelope(
                    code=f"A{action}",
                    risk=tuple(
                        problem.losses[target][action]
                        for target in range(problem.target_count)
                    ),
                    occupancy=zero_occupancy,
                )
            )
        if depth:
            for query_index, name in enumerate(names):
                if remaining[query_index] == 0:
                    continue
                query = query_by_name[name]
                next_remaining = list(remaining)
                next_remaining[query_index] -= 1
                children = build(depth - 1, tuple(next_remaining))
                for branches in product(
                    children, repeat=query.outcome_count
                ):
                    risk = tuple(
                        sum(
                            (
                                query.rows[target][outcome]
                                * branches[outcome].risk[target]
                                for outcome in range(query.outcome_count)
                            ),
                            Q(0),
                        )
                        for target in range(problem.target_count)
                    )
                    occupancy_rows = []
                    for target in range(problem.target_count):
                        target_row = []
                        for index in range(len(names)):
                            expected_future = sum(
                                (
                                    query.rows[target][outcome]
                                    * branches[outcome].occupancy[target][
                                        index
                                    ]
                                    for outcome in range(
                                        query.outcome_count
                                    )
                                ),
                                Q(0),
                            )
                            target_row.append(
                                expected_future
                                + Q(int(index == query_index))
                            )
                        occupancy_rows.append(tuple(target_row))
                    rows.append(
                        OccupancyEnvelope(
                            code=(
                                f"{name}("
                                + ",".join(
                                    branch.code for branch in branches
                                )
                                + ")"
                            ),
                            risk=risk,
                            occupancy=tuple(occupancy_rows),
                        )
                    )
        deduplicated: dict[
            tuple[RiskVector, tuple[tuple[Q, ...], ...]],
            OccupancyEnvelope,
        ] = {}
        for row in rows:
            key = (row.risk, row.occupancy)
            current = deduplicated.get(key)
            if current is None or row.code < current.code:
                deduplicated[key] = row
        return tuple(
            sorted(
                deduplicated.values(),
                key=lambda row: (row.risk, row.occupancy, row.code),
            )
        )

    return build(horizon, budgets)


def _decimal_log_upper(value: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = 80
        return context.next_plus(value.ln())


def decimal_fraction_upper(
    value: Decimal, decimal_digits: int = 12
) -> Q:
    """Outward rational ceiling of a nonnegative Decimal."""

    if value < 0:
        raise ValueError("value must be nonnegative")
    if decimal_digits < 0:
        raise ValueError("decimal_digits must be nonnegative")
    scale = Decimal(10) ** decimal_digits
    numerator = int(
        (value * scale).to_integral_value(rounding=ROUND_CEILING)
    )
    return Q(numerator, 10**decimal_digits)


@lru_cache(maxsize=None)
def method_of_types_kl_upper(
    samples: int,
    query_count: int,
    alpha_text: str = "0.05",
    decimal_digits: int = 12,
) -> Q:
    """Simultaneous binary empirical-to-population KL upper bound.

    The method-of-types bound

    ``P[KL(P_hat||P) >= eps] <= (n+1) exp(-n eps)``

    is Bonferroni-adjusted over ``query_count`` registered shared binary
    parameters.  The returned value is rounded outward to a rational grid.
    """

    if samples < 1 or query_count < 1:
        raise ValueError("sample and query counts must be positive")
    alpha = Decimal(alpha_text)
    if not Decimal(0) < alpha < Decimal(1):
        raise ValueError("alpha must lie strictly between zero and one")
    with localcontext() as context:
        context.prec = 80
        ratio = (
            Decimal(query_count)
            * Decimal(samples + 1)
            / alpha
        )
        value = context.next_plus(
            _decimal_log_upper(ratio) / Decimal(samples)
        )
    return decimal_fraction_upper(value, decimal_digits)


def positive_allocations(
    total_budget: int, query_count: int
) -> tuple[tuple[int, ...], ...]:
    """All positive integer allocations with exact total budget."""

    if query_count < 1 or total_budget < query_count:
        raise ValueError(
            "total budget must support one sample per query"
        )

    def build(remaining: int, cells: int):
        if cells == 1:
            yield (remaining,)
            return
        for first in range(1, remaining - cells + 2):
            for suffix in build(remaining - first, cells - 1):
                yield (first,) + suffix

    return tuple(build(total_budget, query_count))


def problem_loss_spans(problem: DecisionProblem) -> tuple[Q, ...]:
    return tuple(max(row) - min(row) for row in problem.losses)


def information_for_allocation(
    envelope: OccupancyEnvelope,
    allocation: Sequence[int],
    query_count: int,
    alpha_text: str = "0.05",
    decimal_digits: int = 12,
) -> tuple[Q, ...]:
    allocation = tuple(int(value) for value in allocation)
    if len(allocation) != query_count or any(
        value < 1 for value in allocation
    ):
        raise ValueError("allocation must give every query a sample")
    tolls = tuple(
        method_of_types_kl_upper(
            samples,
            query_count,
            alpha_text,
            decimal_digits,
        )
        for samples in allocation
    )
    return tuple(
        sum(
            (
                occupancy * toll
                for occupancy, toll in zip(target_row, tolls)
            ),
            Q(0),
        )
        for target_row in envelope.occupancy
    )


def radii_for_allocation(
    envelopes: Sequence[OccupancyEnvelope],
    problem: DecisionProblem,
    allocation: Sequence[int],
    query_count: int,
    alpha_text: str = "0.05",
    decimal_digits: int = 12,
) -> tuple[RiskVector, ...]:
    spans = problem_loss_spans(problem)
    rows = []
    for envelope in envelopes:
        information = information_for_allocation(
            envelope,
            allocation,
            query_count,
            alpha_text,
            decimal_digits,
        )
        rows.append(
            tuple(
                min(
                    span,
                    span
                    * sqrt_fraction_upper(
                        value / 2, decimal_digits
                    ),
                )
                for span, value in zip(spans, information)
            )
        )
    return tuple(rows)


@dataclass(frozen=True)
class AllocationEvaluation:
    allocation: tuple[int, ...]
    lower: Q
    point: Q
    upper: Q

    def jsonable(self, query_names: Sequence[str]) -> dict:
        return {
            "allocation": {
                name: self.allocation[index]
                for index, name in enumerate(query_names)
            },
            "lower": qstr(self.lower),
            "point": qstr(self.point),
            "upper": qstr(self.upper),
            "width": qstr(self.upper - self.lower),
            "upper_float": float(self.upper),
        }


def evaluate_allocation(
    envelopes: Sequence[OccupancyEnvelope],
    problem: DecisionProblem,
    allocation: Sequence[int],
    query_count: int,
    reference: Sequence[RiskVector],
    alpha_text: str = "0.05",
    decimal_digits: int = 12,
) -> AllocationEvaluation:
    centers = tuple(envelope.risk for envelope in envelopes)
    radii = radii_for_allocation(
        envelopes,
        problem,
        allocation,
        query_count,
        alpha_text,
        decimal_digits,
    )
    reference = tuple(reference)
    zero_reference = tuple(
        tuple([Q(0)] * problem.target_count) for _ in reference
    )
    interval = robust_directed_deficiency_interval(
        centers, radii, reference, zero_reference
    )
    return AllocationEvaluation(
        allocation=tuple(int(value) for value in allocation),
        lower=interval.lower,
        point=interval.point,
        upper=interval.upper,
    )


def registered_constructive_upper(
    allocation: Sequence[int],
    mode: str,
    alpha_text: str = "0.05",
    decimal_digits: int = 12,
) -> Q:
    """Safe constructive upper bound for the registered tree.

    The query order is ``(root, left, right)``.  For four-class
    identification, a perfect center policy uses the root and exactly one
    branch query, while uniform randomization over terminal actions supplies
    the no-information bound ``3/4``.  For root-group loss, the perfect policy
    uses only the root and the no-information bound is ``1/2``.
    """

    allocation = tuple(int(value) for value in allocation)
    if len(allocation) != 3 or any(value < 1 for value in allocation):
        raise ValueError("registered formula needs three positive cells")
    tolls = tuple(
        method_of_types_kl_upper(
            value, 3, alpha_text, decimal_digits
        )
        for value in allocation
    )
    if mode == "branch_classification":
        information = tolls[0] + max(tolls[1], tolls[2])
        return min(
            Q(3, 4),
            sqrt_fraction_upper(information / 2, decimal_digits),
        )
    if mode == "root_group":
        return min(
            Q(1, 2),
            sqrt_fraction_upper(tolls[0] / 2, decimal_digits),
        )
    raise ValueError("unknown registered constructive mode")


def exact_upper_for_allocation(
    envelopes: Sequence[OccupancyEnvelope],
    problem: DecisionProblem,
    allocation: Sequence[int],
    query_count: int,
    reference: Sequence[RiskVector],
    alpha_text: str = "0.05",
    decimal_digits: int = 12,
) -> Q:
    """Compute only the exact upper endpoint used in formula audits."""

    centers = tuple(envelope.risk for envelope in envelopes)
    radii = radii_for_allocation(
        envelopes,
        problem,
        allocation,
        query_count,
        alpha_text,
        decimal_digits,
    )
    source_upper = tuple(
        tuple(center + radius for center, radius in zip(row, bound))
        for row, bound in zip(centers, radii)
    )
    return directed_upper_deficiency(source_upper, tuple(reference)).epsilon


def optimize_constructive_upper(
    total_budget: int,
    mode: str,
    alpha_text: str = "0.05",
    decimal_digits: int = 12,
) -> dict:
    """Exhaust the constructive bound over the integer allocation universe."""

    allocations = positive_allocations(total_budget, 3)
    rows = tuple(
        (
            allocation,
            registered_constructive_upper(
                allocation, mode, alpha_text, decimal_digits
            ),
        )
        for allocation in allocations
    )
    best = min(value for _, value in rows)
    optima = tuple(
        allocation for allocation, value in rows if value == best
    )
    quotient, remainder = divmod(total_budget, 3)
    uniform = tuple(
        quotient + int(index < remainder) for index in range(3)
    )
    uniform_value = next(
        value for allocation, value in rows if allocation == uniform
    )
    return {
        "optima": optima,
        "optimum": min(optima),
        "best_upper": best,
        "uniform": uniform,
        "uniform_upper": uniform_value,
        "evaluated_allocations": len(rows),
        "strict_improvement": best < uniform_value,
    }


@dataclass(frozen=True)
class AllocationOptimum:
    optimum: AllocationEvaluation
    uniform: AllocationEvaluation
    evaluated_allocations: int
    tied_optima: tuple[tuple[int, ...], ...]

    def jsonable(self, query_names: Sequence[str]) -> dict:
        return {
            "optimum": self.optimum.jsonable(query_names),
            "uniform": self.uniform.jsonable(query_names),
            "evaluated_allocations": self.evaluated_allocations,
            "tied_optima": [
                {
                    name: allocation[index]
                    for index, name in enumerate(query_names)
                }
                for allocation in self.tied_optima
            ],
            "strict_improvement": self.optimum.upper < self.uniform.upper,
            "absolute_improvement": float(
                self.uniform.upper - self.optimum.upper
            ),
            "relative_improvement": (
                float(
                    (self.uniform.upper - self.optimum.upper)
                    / self.uniform.upper
                )
                if self.uniform.upper
                else 0.0
            ),
        }


@lru_cache(maxsize=None)
def _optimize_allocation_cached(
    envelopes: tuple[OccupancyEnvelope, ...],
    problem: DecisionProblem,
    total_budget: int,
    query_names: tuple[str, ...],
    reference: tuple[RiskVector, ...],
    alpha_text: str = "0.05",
    decimal_digits: int = 12,
) -> AllocationOptimum:
    allocations = positive_allocations(
        total_budget, len(query_names)
    )
    evaluations = tuple(
        evaluate_allocation(
            envelopes,
            problem,
            allocation,
            len(query_names),
            reference,
            alpha_text,
            decimal_digits,
        )
        for allocation in allocations
    )
    best_upper = min(row.upper for row in evaluations)
    tied = tuple(
        row.allocation for row in evaluations if row.upper == best_upper
    )
    optimum = min(
        (row for row in evaluations if row.upper == best_upper),
        key=lambda row: row.allocation,
    )
    quotient, remainder = divmod(total_budget, len(query_names))
    uniform_allocation = tuple(
        quotient + int(index < remainder)
        for index in range(len(query_names))
    )
    uniform = next(
        row
        for row in evaluations
        if row.allocation == uniform_allocation
    )
    return AllocationOptimum(
        optimum=optimum,
        uniform=uniform,
        evaluated_allocations=len(evaluations),
        tied_optima=tied,
    )


def optimize_allocation(
    envelopes: Sequence[OccupancyEnvelope],
    problem: DecisionProblem,
    total_budget: int,
    query_names: Sequence[str],
    reference: Sequence[RiskVector],
    alpha_text: str = "0.05",
    decimal_digits: int = 12,
) -> AllocationOptimum:
    """Exhaustively optimize a frozen integer allocation.

    All inputs are immutable mathematical objects, so repeated requests for
    the same registered problem reuse the first exact certificate.  This is
    an execution optimization only: every positive allocation is still
    evaluated once.
    """

    return _optimize_allocation_cached(
        tuple(envelopes),
        problem,
        int(total_budget),
        tuple(query_names),
        tuple(tuple(q(value) for value in row) for row in reference),
        str(alpha_text),
        int(decimal_digits),
    )


def serial_information_objective(
    allocation: Sequence[int],
    alpha_text: str = "0.05",
    decimal_digits: int = 12,
) -> Q:
    """Information for a matched policy that uses every query once."""

    allocation = tuple(int(value) for value in allocation)
    return sum(
        (
            method_of_types_kl_upper(
                value,
                len(allocation),
                alpha_text,
                decimal_digits,
            )
            for value in allocation
        ),
        Q(0),
    )


def optimize_serial_control(
    total_budget: int,
    query_count: int,
    alpha_text: str = "0.05",
    decimal_digits: int = 12,
) -> dict:
    allocations = positive_allocations(total_budget, query_count)
    rows = tuple(
        (
            allocation,
            serial_information_objective(
                allocation, alpha_text, decimal_digits
            ),
        )
        for allocation in allocations
    )
    best = min(value for _, value in rows)
    optima = tuple(
        allocation for allocation, value in rows if value == best
    )
    quotient, remainder = divmod(total_budget, query_count)
    uniform = tuple(
        quotient + int(index < remainder)
        for index in range(query_count)
    )
    return {
        "optima": optima,
        "uniform": uniform,
        "uniform_is_optimal": uniform in optima,
        "best_information": best,
        "evaluated_allocations": len(rows),
    }


def asymptotic_continuous_lower(
    total_budget: int,
    query_count: int,
    alpha_text: str,
    mode: str,
) -> float:
    """Continuous oracle lower benchmark after dropping type prefactors.

    ``kappa(n) >= log(query_count/alpha)/n``.  The returned objective is the
    best Pinsker radius under that smaller toll for the two registered
    occupancy patterns.
    """

    if total_budget <= 0 or query_count != 3:
        raise ValueError("registered lower benchmark needs 3 queries")
    alpha = float(alpha_text)
    constant = math.log(query_count / alpha)
    if mode == "root_group":
        information = constant / total_budget
    elif mode == "branch_classification":
        information = (
            constant
            * (1.0 + math.sqrt(2.0)) ** 2
            / total_budget
        )
    else:
        raise ValueError("unknown lower-benchmark mode")
    return min(1.0, math.sqrt(information / 2.0))


def symmetric_binomial_bayes_error(
    samples: int,
    half_gap: Q,
) -> Q:
    """Exact equal-prior testing error for p=1/2 +/- half_gap."""

    half_gap = q(half_gap)
    if samples < 1 or not Q(0) < half_gap < Q(1, 2):
        raise ValueError("invalid symmetric binomial experiment")
    left = Q(1, 2) - half_gap
    right = Q(1, 2) + half_gap
    total_variation = sum(
        (
            abs(
                Q(comb(samples, successes))
                * left**successes
                * (Q(1) - left) ** (samples - successes)
                - Q(comb(samples, successes))
                * right**successes
                * (Q(1) - right) ** (samples - successes)
            )
            for successes in range(samples + 1)
        ),
        Q(0),
    ) / 2
    return (Q(1) - total_variation) / 2


def two_point_radius_lower(
    samples: int,
    alpha: Q = Q(1, 20),
    denominator: int = 200,
) -> dict:
    """Registered-grid lower bound for a uniform Bernoulli CI radius.

    If a confidence set has coverage at least ``1-alpha`` under both
    ``1/2-d`` and ``1/2+d`` and always has radius strictly below ``d``,
    it induces a test with both errors at most ``alpha``.  Therefore every
    grid point whose exact equal-prior Bayes error exceeds ``alpha`` is a
    certified obstruction.
    """

    alpha = q(alpha)
    if samples < 1 or not Q(0) < alpha < Q(1, 2):
        raise ValueError("invalid two-point lower-bound inputs")
    if denominator < 3:
        raise ValueError("grid denominator is too small")
    rows = []
    for numerator in range(1, (denominator + 1) // 2):
        half_gap = Q(numerator, denominator)
        error = symmetric_binomial_bayes_error(samples, half_gap)
        rows.append((half_gap, error))
    obstructed = [
        (half_gap, error)
        for half_gap, error in rows
        if error > alpha
    ]
    if not obstructed:
        raise ValueError("registered grid found no obstruction")
    half_gap, error = max(obstructed)
    return {
        "samples": samples,
        "alpha": alpha,
        "grid_denominator": denominator,
        "radius_lower": half_gap,
        "bayes_error": error,
        "next_grid_error": next(
            (
                candidate_error
                for candidate_gap, candidate_error in rows
                if candidate_gap == half_gap + Q(1, denominator)
            ),
            None,
        ),
    }
