"""Certified coupled shared-channel uncertainty for ASMP-9 v0.46."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
from itertools import product
import json
from math import lcm
from pathlib import Path
import sys
from typing import Sequence

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
V38 = HERE.parent / "decision_relative_access_v0_38"
V41 = HERE.parent / "sequential_risk_access_v0_41"
V44 = HERE.parent / "occupancy_information_v0_44"
V45 = HERE.parent / "sample_allocation_v0_45"
for path in (V38, V41, V44, V45):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from relative_deficiency import _exact_linprog  # noqa: E402
from allocation_design import (  # noqa: E402
    method_of_types_kl_upper,
    positive_allocations,
)
from occupancy_information import (  # noqa: E402
    robust_directed_deficiency_interval,
)
from sequential_access import (  # noqa: E402
    ADAPTIVITY_GAP_QUERIES,
    QueryChannel,
    adaptive_upper_generators,
    binary_group_problem,
    classification_problem,
    directed_upper_deficiency,
)


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def floor_grid(value: Q, digits: int) -> Q:
    if digits < 0:
        raise ValueError("digits must be nonnegative")
    scale = 10**digits
    return Q(value.numerator * scale // value.denominator, scale)


def ceil_grid(value: Q, digits: int) -> Q:
    if digits < 0:
        raise ValueError("digits must be nonnegative")
    scale = 10**digits
    numerator = -((-value.numerator * scale) // value.denominator)
    return Q(numerator, scale)


def exp_neg_fraction_bounds(
    value: Q,
    target_width: Q = Q(1, 10**15),
    max_terms: int = 256,
) -> tuple[Q, Q]:
    """Exact rational lower/upper bounds on ``exp(-value)``.

    Scale ``value`` by a power of two until it is at most one. The alternating
    Taylor partial sums then bracket ``exp(-y)`` because term magnitudes
    decrease. Positive integer powers preserve the bracket.
    """

    value = q(value)
    target_width = q(target_width)
    if value < 0 or target_width <= 0:
        raise ValueError("invalid exponential-bound inputs")
    if value == 0:
        return Q(1), Q(1)
    scale = 1
    while value > scale:
        scale *= 2
    y = value / scale
    term = Q(1)
    partial = Q(1)
    lower = None
    upper = Q(1)
    for order in range(1, max_terms + 1):
        term *= -y / order
        partial += term
        if order % 2:
            lower = partial
        else:
            upper = partial
        if lower is not None and lower >= 0:
            powered_lower = lower**scale
            powered_upper = upper**scale
            if powered_upper - powered_lower <= target_width:
                return powered_lower, powered_upper
    raise RuntimeError("exponential bracket did not converge")


@dataclass(frozen=True)
class ProbabilityBounds:
    samples: int
    kappa: Q
    lower: Q
    upper: Q

    def jsonable(self) -> dict:
        return {
            "samples": self.samples,
            "kappa": qstr(self.kappa),
            "lower": qstr(self.lower),
            "upper": qstr(self.upper),
            "width": qstr(self.upper - self.lower),
        }


@lru_cache(maxsize=None)
def flip_probability_bounds(
    samples: int,
    query_count: int = 3,
    alpha_text: str = "0.05",
    digits: int = 12,
) -> ProbabilityBounds:
    """Certified grid bounds on ``1-exp(-kappa(samples))``."""

    kappa = method_of_types_kl_upper(
        samples, query_count, alpha_text, digits
    )
    exp_lower, exp_upper = exp_neg_fraction_bounds(kappa)
    raw_lower = Q(1) - exp_upper
    raw_upper = Q(1) - exp_lower
    lower = min(
        Q(1, 2),
        max(Q(0), floor_grid(raw_lower, digits)),
    )
    upper = min(Q(1, 2), ceil_grid(raw_upper, digits))
    if not Q(0) <= lower <= upper <= Q(1, 2):
        raise AssertionError("invalid flip-probability bracket")
    return ProbabilityBounds(samples, kappa, lower, upper)


@dataclass(frozen=True)
class RegisteredTreeBounds:
    allocation: tuple[int, int, int]
    lower: Q
    upper: Q
    probability_bounds: tuple[ProbabilityBounds, ...]

    def jsonable(self, query_names=("root", "left", "right")) -> dict:
        return {
            "allocation": {
                name: self.allocation[index]
                for index, name in enumerate(query_names)
            },
            "lower": qstr(self.lower),
            "upper": qstr(self.upper),
            "width": qstr(self.upper - self.lower),
            "probability_bounds": {
                name: self.probability_bounds[index].jsonable()
                for index, name in enumerate(query_names)
            },
        }


def _registered_tree_classification_upper(
    probabilities: Sequence[Q],
) -> Q:
    root, left, right = (q(value) for value in probabilities)
    branch = max(left, right)
    return root + branch - root * branch


def _group_objective(probabilities: Sequence[Q]) -> Q:
    return q(probabilities[0])


# Every horizon-two policy risk is a polynomial of total degree at most two
# in the three shared flip probabilities.  These ten monomials form a frozen
# exact basis for the full adaptive policy class.
MONOMIAL_EXPONENTS = (
    (0, 0, 0),
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (2, 0, 0),
    (1, 1, 0),
    (1, 0, 1),
    (0, 2, 0),
    (0, 1, 1),
    (0, 0, 2),
)
MONOMIAL_INDEX = {
    exponent: index
    for index, exponent in enumerate(MONOMIAL_EXPONENTS)
}


def _multiply_polynomial_by_variable(
    coefficients: np.ndarray,
    variable: int,
) -> np.ndarray:
    result = np.zeros_like(coefficients)
    for index, exponent in enumerate(MONOMIAL_EXPONENTS):
        if sum(exponent) >= 2:
            if coefficients[index]:
                raise ValueError("policy polynomial exceeded degree two")
            continue
        shifted = list(exponent)
        shifted[variable] += 1
        result[MONOMIAL_INDEX[tuple(shifted)]] += coefficients[index]
    return result


def _compose_symbolic_query(
    query_index: int,
    child_zero: np.ndarray,
    child_one: np.ndarray,
) -> np.ndarray:
    """Compose a binary noisy query with two symbolic continuations."""

    signatures = tuple(
        int(row[1]) for row in ADAPTIVITY_GAP_QUERIES[query_index].rows
    )
    result = np.zeros_like(child_zero)
    for target, signature in enumerate(signatures):
        if signature == 0:
            base = child_zero[target]
            delta = child_one[target] - child_zero[target]
        else:
            base = child_one[target]
            delta = child_zero[target] - child_one[target]
        result[target] = (
            base
            + _multiply_polynomial_by_variable(delta, query_index)
        )
    return result


@lru_cache(maxsize=1)
def symbolic_classification_policies() -> np.ndarray:
    """All unique horizon-two adaptive four-class policy polynomials."""

    terminal = np.zeros(
        (4, 4, len(MONOMIAL_EXPONENTS)),
        dtype=np.int16,
    )
    for action in range(4):
        for target in range(4):
            terminal[action, target, 0] = int(action != target)

    depth_one = [row for row in terminal]
    for query_index in range(3):
        for left in terminal:
            for right in terminal:
                depth_one.append(
                    _compose_symbolic_query(
                        query_index, left, right
                    )
                )
    depth_one_array = np.unique(
        np.stack(depth_one, axis=0), axis=0
    )

    depth_two = [row for row in terminal]
    for query_index in range(3):
        for left in depth_one_array:
            for right in depth_one_array:
                depth_two.append(
                    _compose_symbolic_query(
                        query_index, left, right
                    )
                )
    policies = np.unique(np.stack(depth_two, axis=0), axis=0)
    policies.setflags(write=False)
    return policies


def monomial_values(
    probabilities: Sequence[Q],
) -> tuple[Q, ...]:
    probabilities = tuple(q(value) for value in probabilities)
    if len(probabilities) != 3:
        raise ValueError("three probabilities are required")
    if any(not Q(0) <= value <= Q(1, 2) for value in probabilities):
        raise ValueError("probability leaves the symmetric-flip range")
    return tuple(
        probabilities[0] ** exponent[0]
        * probabilities[1] ** exponent[1]
        * probabilities[2] ** exponent[2]
        for exponent in MONOMIAL_EXPONENTS
    )


def evaluate_symbolic_policies(
    probabilities: Sequence[Q],
) -> tuple[tuple[Q, ...], ...]:
    """Evaluate the exact symbolic policy library at rational rates."""

    values = monomial_values(probabilities)
    policies = symbolic_classification_policies()
    rows = []
    for policy in policies:
        rows.append(
            tuple(
                sum(
                    (
                        Q(int(coefficient)) * value
                        for coefficient, value in zip(
                            policy[target], values
                        )
                    ),
                    Q(0),
                )
                for target in range(4)
            )
        )
    return tuple(rows)


def evaluate_symbolic_policies_float(
    probabilities: Sequence[Q],
) -> np.ndarray:
    values = np.asarray(
        [float(value) for value in monomial_values(probabilities)],
        dtype=np.float64,
    )
    return np.tensordot(
        symbolic_classification_policies().astype(np.float64),
        values,
        axes=([2], [0]),
    )


@lru_cache(maxsize=1)
def _symbolic_policies_object() -> np.ndarray:
    policies = symbolic_classification_policies().astype(object)
    policies.setflags(write=False)
    return policies


def policy_risk_integer_grid(
    probabilities: Sequence[Q],
) -> tuple[np.ndarray, int]:
    """Evaluate policy risks on one exact shared integer denominator."""

    probabilities = tuple(q(value) for value in probabilities)
    monomial_values(probabilities)
    denominator = lcm(
        *(value.denominator for value in probabilities)
    )
    numerators = tuple(
        value.numerator * (denominator // value.denominator)
        for value in probabilities
    )
    monomials = []
    for exponent in MONOMIAL_EXPONENTS:
        degree = sum(exponent)
        value = denominator ** (2 - degree)
        for variable, power in enumerate(exponent):
            value *= numerators[variable] ** power
        monomials.append(value)
    policies = _symbolic_policies_object()
    risks = np.zeros(policies.shape[:2], dtype=object)
    for index, value in enumerate(monomials):
        risks += policies[:, :, index] * value
    return risks, denominator**2


def floating_minimax_prior(
    probabilities: Sequence[Q],
) -> tuple[float, tuple[float, ...]]:
    """Float proposal for the exact four-target minimax game."""

    risks = evaluate_symbolic_policies_float(probabilities)
    policy_count = risks.shape[0]
    inequalities = np.column_stack(
        (-risks, -np.ones(policy_count, dtype=np.float64))
    )
    result = linprog(
        c=np.asarray([0.0, 0.0, 0.0, 0.0, 1.0]),
        A_ub=inequalities,
        b_ub=-np.ones(policy_count, dtype=np.float64),
        A_eq=np.asarray([[1.0, 1.0, 1.0, 1.0, 0.0]]),
        b_eq=np.asarray([1.0]),
        bounds=[(0.0, None)] * 5,
        method="highs",
    )
    if not result.success:
        raise RuntimeError(
            f"floating minimax proposal failed: {result.message}"
        )
    return 1.0 - float(result.x[-1]), tuple(
        float(value) for value in result.x[:4]
    )


def rational_simplex(
    values: Sequence[float],
    denominator: int = 10**10,
) -> tuple[Q, ...]:
    """Round a floating simplex point to an exact rational simplex."""

    array = np.asarray(values, dtype=np.float64)
    if (
        denominator < 1
        or array.ndim != 1
        or len(array) < 2
        or np.any(array < -1e-9)
        or not np.isclose(array.sum(), 1.0, atol=1e-8)
    ):
        raise ValueError("invalid simplex proposal")
    array = np.maximum(array, 0.0)
    array /= array.sum()
    scaled = array * denominator
    numerators = np.floor(scaled).astype(np.int64)
    remainder = denominator - int(numerators.sum())
    order = np.argsort(-(scaled - numerators), kind="stable")
    for index in order[:remainder]:
        numerators[index] += 1
    if int(numerators.sum()) != denominator:
        raise AssertionError("simplex rounding did not preserve mass")
    return tuple(Q(int(value), denominator) for value in numerators)


def prior_lower_bound(
    probabilities: Sequence[Q],
    prior: Sequence[Q],
) -> Q:
    """Exact Bayes-risk lower bound for any frozen target prior."""

    prior = tuple(q(value) for value in prior)
    if (
        len(prior) != 4
        or any(value < 0 for value in prior)
        or sum(prior, Q(0)) != 1
    ):
        raise ValueError("prior must be an exact four-target simplex")
    return min(
        sum(
            (weight * loss for weight, loss in zip(prior, row)),
            Q(0),
        )
        for row in evaluate_symbolic_policies(probabilities)
    )


def fast_prior_lower_bound(
    probabilities: Sequence[Q],
    prior: Sequence[Q],
) -> Q:
    """Integer-grid implementation of :func:`prior_lower_bound`."""

    prior = tuple(q(value) for value in prior)
    if (
        len(prior) != 4
        or any(value < 0 for value in prior)
        or sum(prior, Q(0)) != 1
    ):
        raise ValueError("prior must be an exact four-target simplex")
    denominator = lcm(*(value.denominator for value in prior))
    numerators = np.asarray(
        [
            value.numerator * (denominator // value.denominator)
            for value in prior
        ],
        dtype=object,
    )
    risks, risk_denominator = policy_risk_integer_grid(probabilities)
    expected = risks @ numerators
    return Q(int(min(expected)), risk_denominator * denominator)


def certified_minimax_classification(
    probabilities: Sequence[Q],
) -> dict:
    """Solve the full adaptive minimax game with an exact LP certificate."""

    risks = evaluate_symbolic_policies(probabilities)
    inequalities = tuple(
        tuple(-value for value in row) + (Q(-1),)
        for row in risks
    )
    solution = _exact_linprog(
        objective=(Q(0), Q(0), Q(0), Q(0), Q(1)),
        inequalities=inequalities,
        inequality_rhs=tuple([Q(-1)] * len(inequalities)),
        equalities=((Q(1), Q(1), Q(1), Q(1), Q(0)),),
        equality_rhs=(Q(1),),
    )
    return {
        "risk": Q(1) - solution.value,
        "prior": tuple(solution.variables[:4]),
        "one_minus_risk": solution.value,
        "active_labels": solution.active_labels,
        "dual_weights": solution.dual_weights,
        "policy_count": len(risks),
    }


def blackwell_postprocessing_flip(lower: Q, upper: Q) -> Q:
    """Flip rate taking BSC(lower) to BSC(upper), when ordered."""

    lower = q(lower)
    upper = q(upper)
    if not Q(0) <= lower <= upper <= Q(1, 2):
        raise ValueError("channels are not ordered symmetric flips")
    if lower == Q(1, 2):
        return Q(0)
    rate = (upper - lower) / (Q(1) - 2 * lower)
    if not Q(0) <= rate <= Q(1, 2):
        raise AssertionError("invalid Blackwell postprocessing rate")
    return rate


@dataclass(frozen=True)
class MinimaxAllocationBounds:
    allocation: tuple[int, int, int]
    lower: Q
    float_value: float
    upper_hint: float
    prior: tuple[Q, ...]
    probability_lower: tuple[Q, ...]
    probability_upper: tuple[Q, ...]

    def jsonable(self) -> dict:
        return {
            "allocation": list(self.allocation),
            "lower": qstr(self.lower),
            "float_value": self.float_value,
            "upper_hint": self.upper_hint,
            "prior": [qstr(value) for value in self.prior],
            "probability_lower": [
                qstr(value) for value in self.probability_lower
            ],
            "probability_upper": [
                qstr(value) for value in self.probability_upper
            ],
        }


def classification_allocation_lower_bound(
    allocation: Sequence[int],
) -> MinimaxAllocationBounds:
    allocation = tuple(int(value) for value in allocation)
    if len(allocation) != 3 or any(value < 1 for value in allocation):
        raise ValueError("allocation must contain three positive counts")
    bounds = tuple(flip_probability_bounds(value) for value in allocation)
    lower_probabilities = tuple(value.lower for value in bounds)
    upper_probabilities = tuple(value.upper for value in bounds)
    float_value, proposed_prior = floating_minimax_prior(
        lower_probabilities
    )
    prior = rational_simplex(proposed_prior)
    lower = fast_prior_lower_bound(lower_probabilities, prior)
    if lower > Q(str(float_value + 1e-8)):
        raise AssertionError("certified lower bound exceeds float optimum")
    return MinimaxAllocationBounds(
        allocation=allocation,
        lower=lower,
        float_value=float_value,
        # This is proposal-only. The probability bracket is at most one
        # 1e-12 grid cell wide, and exact bounds below decide uniqueness.
        upper_hint=float_value,
        prior=prior,
        probability_lower=lower_probabilities,
        probability_upper=upper_probabilities,
    )


@lru_cache(maxsize=None)
def optimize_coupled_minimax_classification(
    total_budget: int,
) -> dict:
    """Certify the global allocation optimum for the full adaptive game."""

    rows = tuple(
        classification_allocation_lower_bound(allocation)
        for allocation in positive_allocations(total_budget, 3)
    )
    proposed = min(
        rows, key=lambda row: (row.upper_hint, row.allocation)
    )
    candidate_lower = certified_minimax_classification(
        proposed.probability_lower
    )
    candidate_exact = certified_minimax_classification(
        proposed.probability_upper
    )
    candidate_upper = candidate_exact["risk"]
    ambiguous = [
        row
        for row in rows
        if row.allocation != proposed.allocation
        and row.lower <= candidate_upper
    ]
    sharpened = []
    for row in ambiguous:
        exact = certified_minimax_classification(
            row.probability_lower
        )
        sharpened.append(
            {
                "allocation": row.allocation,
                "lower": exact["risk"],
                "prior": exact["prior"],
            }
        )
    competitor_lowers = [
        row.lower
        for row in rows
        if row.allocation != proposed.allocation
        and row.lower > candidate_upper
    ] + [row["lower"] for row in sharpened]
    competitor_lower = min(competitor_lowers)
    quotient, remainder = divmod(total_budget, 3)
    uniform_allocation = tuple(
        quotient + int(index < remainder) for index in range(3)
    )
    uniform_row = next(
        row for row in rows if row.allocation == uniform_allocation
    )
    uniform_exact = certified_minimax_classification(
        uniform_row.probability_lower
    )
    uniform_upper = certified_minimax_classification(
        uniform_row.probability_upper
    )
    return {
        "mode": "branch_classification",
        "total_budget": total_budget,
        "evaluated_allocations": len(rows),
        "rows": rows,
        "rows_sha256": hashlib.sha256(
            canonical_json_bytes([row.jsonable() for row in rows])
        ).hexdigest(),
        "candidate": proposed,
        "candidate_exact_lower": candidate_lower,
        "candidate_exact_upper": candidate_exact,
        "uniform": uniform_row,
        "uniform_exact_lower": uniform_exact,
        "uniform_exact_upper": uniform_upper,
        "ambiguous_before_sharpening": len(ambiguous),
        "sharpened": sharpened,
        "competitor_lower": competitor_lower,
        "certified_unique_gap": competitor_lower - candidate_upper,
        "unique_certified": competitor_lower > candidate_upper,
        "relative_improvement_lower": (
            (uniform_exact["risk"] - candidate_upper)
            / uniform_exact["risk"]
        ),
    }


@lru_cache(maxsize=None)
def optimize_coupled_root_group(total_budget: int) -> dict:
    rows = []
    for allocation in positive_allocations(total_budget, 3):
        root = flip_probability_bounds(allocation[0])
        rows.append((allocation, root.lower, root.upper))
    proposed = min(rows, key=lambda row: (row[2], row[0]))
    competitors = tuple(row for row in rows if row[0] != proposed[0])
    competitor_lower = min(row[1] for row in competitors)
    quotient, remainder = divmod(total_budget, 3)
    uniform_allocation = tuple(
        quotient + int(index < remainder) for index in range(3)
    )
    uniform = next(row for row in rows if row[0] == uniform_allocation)
    json_rows = [
        {
            "allocation": list(allocation),
            "lower": qstr(lower),
            "upper": qstr(upper),
        }
        for allocation, lower, upper in rows
    ]
    return {
        "mode": "root_group",
        "total_budget": total_budget,
        "evaluated_allocations": len(rows),
        "rows": tuple(rows),
        "rows_sha256": hashlib.sha256(
            canonical_json_bytes(json_rows)
        ).hexdigest(),
        "candidate": proposed,
        "uniform": uniform,
        "competitor_lower": competitor_lower,
        "certified_unique_gap": competitor_lower - proposed[2],
        "unique_certified": competitor_lower > proposed[2],
        "relative_improvement_lower": (
            (uniform[1] - proposed[2]) / uniform[1]
        ),
    }


def registered_tree_bounds(
    allocation: Sequence[int],
    mode: str,
    digits: int = 12,
) -> RegisteredTreeBounds:
    allocation = tuple(int(value) for value in allocation)
    if len(allocation) != 3 or any(value < 1 for value in allocation):
        raise ValueError("allocation must contain three positive counts")
    bounds = tuple(
        flip_probability_bounds(value, digits=digits)
        for value in allocation
    )
    lower_probabilities = tuple(row.lower for row in bounds)
    upper_probabilities = tuple(row.upper for row in bounds)
    if mode == "branch_classification":
        objective = _registered_tree_classification_upper
    elif mode == "root_group":
        objective = _group_objective
    else:
        raise ValueError("unknown coupled-objective mode")
    return RegisteredTreeBounds(
        allocation=allocation,
        lower=objective(lower_probabilities),
        upper=objective(upper_probabilities),
        probability_bounds=bounds,
    )


def optimize_registered_tree(
    total_budget: int,
    mode: str,
    digits: int = 12,
) -> dict:
    """Certify a unique optimizer using disjoint objective intervals."""

    rows = tuple(
        registered_tree_bounds(allocation, mode, digits)
        for allocation in positive_allocations(total_budget, 3)
    )
    candidate = min(rows, key=lambda row: (row.upper, row.allocation))
    competitors = tuple(
        row for row in rows if row.allocation != candidate.allocation
    )
    competitor_lower = min(row.lower for row in competitors)
    certified_gap = competitor_lower - candidate.upper
    quotient, remainder = divmod(total_budget, 3)
    uniform_allocation = tuple(
        quotient + int(index < remainder) for index in range(3)
    )
    uniform = next(
        row for row in rows if row.allocation == uniform_allocation
    )
    return {
        "mode": mode,
        "total_budget": total_budget,
        "evaluated_allocations": len(rows),
        "candidate": candidate,
        "uniform": uniform,
        "competitor_lower": competitor_lower,
        "certified_unique_gap": certified_gap,
        "unique_certified": certified_gap > 0,
        "relative_improvement_lower": (
            (uniform.lower - candidate.upper) / uniform.lower
            if uniform.lower
            else Q(0)
        ),
    }


def symmetric_flip_queries(
    probabilities: Sequence[Q],
) -> tuple[QueryChannel, ...]:
    probabilities = tuple(q(value) for value in probabilities)
    if len(probabilities) != len(ADAPTIVITY_GAP_QUERIES):
        raise ValueError("one flip probability is required per query")
    result = []
    for query, flip in zip(
        ADAPTIVITY_GAP_QUERIES, probabilities
    ):
        if not Q(0) <= flip <= Q(1, 2):
            raise ValueError("flip probability leaves registered range")
        result.append(
            QueryChannel(
                query.name,
                tuple(
                    (
                        (Q(1) - flip, flip)
                        if row[0] == 1
                        else (flip, Q(1) - flip)
                    )
                    for row in query.rows
                ),
            )
        )
    return tuple(result)


def exact_channel_deficiency(
    probabilities: Sequence[Q],
    mode: str,
) -> Q:
    if mode == "branch_classification":
        problem = classification_problem(4)
    elif mode == "root_group":
        problem = binary_group_problem(
            "root_group",
            (0, 0, 1, 1),
            false_positive_cost=Q(1),
        )
    else:
        raise ValueError("unknown exact-channel mode")
    reference = (tuple([Q(0)] * problem.target_count),)
    return directed_upper_deficiency(
        adaptive_upper_generators(
            symmetric_flip_queries(probabilities), problem, 2
        ),
        reference,
    ).epsilon


def product_box_control() -> dict:
    """Small exact control where independent generator boxes are realizable."""

    centers = ((Q(1, 4), Q(3, 4)), (Q(3, 4), Q(1, 4)))
    radii = ((Q(1, 20), Q(1, 10)), (Q(1, 10), Q(1, 20)))
    reference = ((Q(0), Q(0)),)
    zero = ((Q(0), Q(0)),)
    interval = robust_directed_deficiency_interval(
        centers, radii, reference, zero
    )
    values = []
    for signs in product((-1, 1), repeat=4):
        actual = (
            (
                centers[0][0] + signs[0] * radii[0][0],
                centers[0][1] + signs[1] * radii[0][1],
            ),
            (
                centers[1][0] + signs[2] * radii[1][0],
                centers[1][1] + signs[3] * radii[1][1],
            ),
        )
        values.append(
            directed_upper_deficiency(actual, reference).epsilon
        )
    exact_supremum = max(values)
    return {
        "vertices": len(values),
        "rectangular_upper": interval.upper,
        "exact_product_supremum": exact_supremum,
        "match": exact_supremum == interval.upper,
    }
