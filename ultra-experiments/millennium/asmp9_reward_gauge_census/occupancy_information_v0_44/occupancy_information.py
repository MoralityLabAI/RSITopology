"""Policy-specific information envelopes for ASMP-9 v0.44.

The v0.43 KL bound becomes ``h * max_q kappa(theta,q)`` when every query may
be repeated and one takes a supremum over every policy before solving the
decision problem.  This module retains the policy tree attached to each risk
generator.  Each generator carries its own expected information occupancy,
and exact robust containment propagates the corresponding generator-specific
risk radius.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
import math
from pathlib import Path
import sys
from typing import Mapping, Sequence


HERE = Path(__file__).resolve().parent
V41 = HERE.parent / "sequential_risk_access_v0_41"
if str(V41) not in sys.path:
    sys.path.insert(0, str(V41))

from sequential_access import (  # noqa: E402
    DecisionProblem,
    QueryChannel,
    directed_upper_deficiency,
)


RiskVector = tuple[Q, ...]
InformationVector = tuple[Q, ...]


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


@dataclass(frozen=True)
class PolicyEnvelope:
    """One deterministic policy's center risk and information occupancy."""

    code: str
    risk: RiskVector
    information: InformationVector

    def jsonable(self) -> dict:
        return {
            "code": self.code,
            "risk": [qstr(value) for value in self.risk],
            "information": [
                qstr(value) for value in self.information
            ],
        }


def _validate_information_costs(
    queries: Sequence[QueryChannel],
    problem: DecisionProblem,
    information_costs: Mapping[tuple[int, str], Q],
) -> dict[tuple[int, str], Q]:
    names = {query.name for query in queries}
    expected = {
        (target, name)
        for target in range(problem.target_count)
        for name in names
    }
    if set(information_costs) != expected:
        raise ValueError("information-cost cell universe differs")
    frozen = {
        key: q(value) for key, value in information_costs.items()
    }
    if any(value < 0 for value in frozen.values()):
        raise ValueError("information costs must be nonnegative")
    return frozen


def enumerate_policy_envelopes(
    queries: Sequence[QueryChannel],
    problem: DecisionProblem,
    horizon: int,
    information_costs: Mapping[tuple[int, str], Q],
    query_budgets: Mapping[str, int] | None = None,
) -> tuple[PolicyEnvelope, ...]:
    """Enumerate unique risk/information pairs for deterministic policy trees.

    Policies may stop at any depth.  ``query_budgets`` bounds uses along every
    root-to-leaf path.  When omitted, every query receives budget ``horizon``,
    reproducing the repeatable-query grammar of v0.41.
    """

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    queries = tuple(queries)
    if len({query.name for query in queries}) != len(queries):
        raise ValueError("query names must be unique")
    if any(
        query.target_count != problem.target_count for query in queries
    ):
        raise ValueError("query and problem target counts differ")
    costs = _validate_information_costs(
        queries, problem, information_costs
    )
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

    @lru_cache(maxsize=None)
    def build(
        depth: int, remaining: tuple[int, ...]
    ) -> tuple[PolicyEnvelope, ...]:
        rows: list[PolicyEnvelope] = []
        for action in range(problem.action_count):
            rows.append(
                PolicyEnvelope(
                    code=f"A{action}",
                    risk=tuple(
                        problem.losses[target][action]
                        for target in range(problem.target_count)
                    ),
                    information=tuple(
                        [Q(0)] * problem.target_count
                    ),
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
                    information = tuple(
                        costs[(target, name)]
                        + sum(
                            (
                                query.rows[target][outcome]
                                * branches[outcome].information[target]
                                for outcome in range(query.outcome_count)
                            ),
                            Q(0),
                        )
                        for target in range(problem.target_count)
                    )
                    rows.append(
                        PolicyEnvelope(
                            code=(
                                f"{name}("
                                + ",".join(
                                    branch.code for branch in branches
                                )
                                + ")"
                            ),
                            risk=risk,
                            information=information,
                        )
                    )
        deduplicated: dict[
            tuple[RiskVector, InformationVector], PolicyEnvelope
        ] = {}
        for row in rows:
            key = (row.risk, row.information)
            current = deduplicated.get(key)
            if current is None or row.code < current.code:
                deduplicated[key] = row
        return tuple(
            sorted(
                deduplicated.values(),
                key=lambda row: (row.risk, row.information, row.code),
            )
        )

    return build(horizon, budgets)


def multinomial_chi_square(
    center: Sequence[Q], perturbed: Sequence[Q]
) -> Q:
    """Exact ``chi2(center || perturbed)`` with support validation."""

    center = tuple(q(value) for value in center)
    perturbed = tuple(q(value) for value in perturbed)
    if len(center) != len(perturbed) or not center:
        raise ValueError("probability rows must share a positive width")
    if (
        any(value < 0 for value in center)
        or any(value < 0 for value in perturbed)
        or sum(center, Q(0)) != 1
        or sum(perturbed, Q(0)) != 1
    ):
        raise ValueError("rows must be probability distributions")
    total = Q(0)
    for p, reference in zip(center, perturbed):
        if reference == 0:
            if p:
                raise ValueError(
                    "center support is not contained in perturbed support"
                )
            continue
        total += (p - reference) ** 2 / reference
    return total


def query_chi_square_costs(
    center_queries: Sequence[QueryChannel],
    perturbed_queries: Sequence[QueryChannel],
) -> dict[tuple[int, str], Q]:
    """Cell-wise rational upper bounds on directed KL."""

    centers = {query.name: query for query in center_queries}
    perturbed = {query.name: query for query in perturbed_queries}
    if set(centers) != set(perturbed):
        raise ValueError("query universes differ")
    costs: dict[tuple[int, str], Q] = {}
    for name in sorted(centers):
        left = centers[name]
        right = perturbed[name]
        if left.target_count != right.target_count:
            raise ValueError("query target counts differ")
        for target in range(left.target_count):
            costs[(target, name)] = multinomial_chi_square(
                left.rows[target], right.rows[target]
            )
    return costs


def sqrt_fraction_upper(value: Q, decimal_digits: int = 12) -> Q:
    """Certified rational upper enclosure of a nonnegative square root."""

    value = q(value)
    if value < 0:
        raise ValueError("cannot take a square root of a negative value")
    if decimal_digits < 0:
        raise ValueError("decimal_digits must be nonnegative")
    if value == 0:
        return Q(0)
    scale = 10**decimal_digits
    scaled_numerator = value.numerator * scale * scale
    floor = math.isqrt(scaled_numerator // value.denominator)
    while (
        (floor + 1) ** 2 * value.denominator
        <= scaled_numerator
    ):
        floor += 1
    while floor**2 * value.denominator > scaled_numerator:
        floor -= 1
    if floor**2 * value.denominator == scaled_numerator:
        return Q(floor, scale)
    return Q(floor + 1, scale)


def problem_loss_spans(problem: DecisionProblem) -> tuple[Q, ...]:
    return tuple(max(row) - min(row) for row in problem.losses)


def information_radii(
    envelopes: Sequence[PolicyEnvelope],
    problem: DecisionProblem,
    decimal_digits: int = 12,
) -> tuple[RiskVector, ...]:
    """Pinsker risk radii from each policy's information occupancy."""

    spans = problem_loss_spans(problem)
    radii = []
    for envelope in envelopes:
        if len(envelope.information) != problem.target_count:
            raise ValueError("policy and problem target counts differ")
        radii.append(
            tuple(
                min(
                    span,
                    span
                    * sqrt_fraction_upper(
                        information / 2, decimal_digits
                    ),
                )
                for span, information in zip(
                    spans, envelope.information
                )
            )
        )
    return tuple(radii)


@dataclass(frozen=True)
class RobustDeficiencyInterval:
    lower: Q
    point: Q
    upper: Q
    source_generators: int
    reference_generators: int

    def jsonable(self) -> dict:
        return {
            "lower": qstr(self.lower),
            "point": qstr(self.point),
            "upper": qstr(self.upper),
            "source_generators": self.source_generators,
            "reference_generators": self.reference_generators,
            "width": qstr(self.upper - self.lower),
        }


def _freeze_radii(
    centers: Sequence[RiskVector],
    radii: Sequence[RiskVector],
) -> tuple[tuple[RiskVector, ...], tuple[RiskVector, ...]]:
    centers = tuple(tuple(q(value) for value in row) for row in centers)
    radii = tuple(tuple(q(value) for value in row) for row in radii)
    if not centers or len(centers) != len(radii):
        raise ValueError("centers and radii must have one positive row count")
    width = len(centers[0])
    if width < 1:
        raise ValueError("risk vectors must be nonempty")
    if any(len(row) != width for row in centers + radii):
        raise ValueError("risk/radius dimensions differ")
    if any(value < 0 for row in radii for value in row):
        raise ValueError("radii must be nonnegative")
    lower = tuple(
        tuple(center - radius for center, radius in zip(row, bound))
        for row, bound in zip(centers, radii)
    )
    upper = tuple(
        tuple(center + radius for center, radius in zip(row, bound))
        for row, bound in zip(centers, radii)
    )
    return lower, upper


def robust_directed_deficiency_interval(
    source_centers: Sequence[RiskVector],
    source_radii: Sequence[RiskVector],
    reference_centers: Sequence[RiskVector],
    reference_radii: Sequence[RiskVector],
) -> RobustDeficiencyInterval:
    """Exact robust containment interval from generator-wise boxes.

    If every true source/reference generator lies in its registered
    coordinate-wise box, monotonicity of

    ``max_f min_mix max_theta(source_mix - f)``

    gives:

    ``D(source_minus, reference_plus) <= D_true
      <= D(source_plus, reference_minus)``.
    """

    source_centers = tuple(source_centers)
    reference_centers = tuple(reference_centers)
    source_lower, source_upper = _freeze_radii(
        source_centers, source_radii
    )
    reference_lower, reference_upper = _freeze_radii(
        reference_centers, reference_radii
    )
    point = directed_upper_deficiency(
        source_centers, reference_centers
    ).epsilon
    lower = directed_upper_deficiency(
        source_lower, reference_upper
    ).epsilon
    upper = directed_upper_deficiency(
        source_upper, reference_lower
    ).epsilon
    if not lower <= point <= upper:
        raise AssertionError("robust interval does not contain its center")
    return RobustDeficiencyInterval(
        lower=lower,
        point=point,
        upper=upper,
        source_generators=len(source_centers),
        reference_generators=len(reference_centers),
    )


def policy_specific_interval(
    envelopes: Sequence[PolicyEnvelope],
    problem: DecisionProblem,
    reference: Sequence[RiskVector],
    decimal_digits: int = 12,
) -> RobustDeficiencyInterval:
    centers = tuple(envelope.risk for envelope in envelopes)
    radii = information_radii(envelopes, problem, decimal_digits)
    reference = tuple(reference)
    zero_reference_radii = tuple(
        tuple([Q(0)] * problem.target_count) for _ in reference
    )
    return robust_directed_deficiency_interval(
        centers,
        radii,
        reference,
        zero_reference_radii,
    )


def uniform_information_interval(
    envelopes: Sequence[PolicyEnvelope],
    problem: DecisionProblem,
    queries: Sequence[QueryChannel],
    information_costs: Mapping[tuple[int, str], Q],
    horizon: int,
    reference: Sequence[RiskVector],
    decimal_digits: int = 12,
) -> RobustDeficiencyInterval:
    """The v0.43-style worst-cell radius applied to every generator."""

    spans = problem_loss_spans(problem)
    names = tuple(query.name for query in queries)
    target_radius = tuple(
        min(
            span,
            span
            * sqrt_fraction_upper(
                Q(horizon)
                * max(
                    q(information_costs[(target, name)])
                    for name in names
                )
                / 2,
                decimal_digits,
            ),
        )
        for target, span in enumerate(spans)
    )
    centers = tuple(envelope.risk for envelope in envelopes)
    radii = tuple(target_radius for _ in centers)
    reference = tuple(reference)
    zero_reference_radii = tuple(
        tuple([Q(0)] * problem.target_count) for _ in reference
    )
    return robust_directed_deficiency_interval(
        centers,
        radii,
        reference,
        zero_reference_radii,
    )
