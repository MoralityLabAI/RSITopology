"""Exact finite observational-versus-interventional gauge access for ASMP-9.

The numerical comparison primitives are reused from the sealed v0.38
instrument without modifying that release.  Every scientific input is a
``Fraction`` and every accepted LP optimum carries the exact primal-dual
certificate checked by v0.38.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction as Q
from pathlib import Path
import sys
from typing import Sequence


V38 = Path(__file__).resolve().parents[1] / "decision_relative_access_v0_38"
if str(V38) not in sys.path:
    sys.path.insert(0, str(V38))

from relative_deficiency import (  # noqa: E402
    FiniteExperiment,
    independent_binary_product,
    ordinary_deficiency,
    policy_regret_problem,
    relative_deficiency,
)


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def three_policy_problem():
    occupancies = tuple(
        tuple(Q(int(row == column)) for column in range(3))
        for row in range(3)
    )
    return policy_regret_problem(
        "three_policy_regret", occupancies, occupancies
    )


def constant_experiment(target_count: int = 3) -> FiniteExperiment:
    if target_count < 2:
        raise ValueError("at least two target classes are required")
    return FiniteExperiment(tuple((Q(1),) for _ in range(target_count)))


def binary_experiment(one_probabilities: Sequence[Q]) -> FiniteExperiment:
    probabilities = tuple(map(q, one_probabilities))
    if len(probabilities) < 2:
        raise ValueError("at least two target probabilities are required")
    return independent_binary_product((probabilities,))


def gauge_leakage_radius(one_probabilities: Sequence[Q]) -> Q:
    probabilities = tuple(map(q, one_probabilities))
    if len(probabilities) < 2:
        raise ValueError("at least two target probabilities are required")
    if any(value < 0 or value > 1 for value in probabilities):
        raise ValueError("probabilities must lie in [0,1]")
    return (max(probabilities) - min(probabilities)) / 2


@dataclass(frozen=True)
class LeakageCertificate:
    probabilities: tuple[Q, ...]
    analytic_radius: Q
    decision_relative_radius: Q
    ordinary_radius: Q
    reverse_decision_relative: Q
    reverse_ordinary: Q

    def jsonable(self) -> dict:
        return {
            key: (
                [qstr(item) for item in value]
                if isinstance(value, tuple)
                else qstr(value)
            )
            for key, value in asdict(self).items()
        }


def certify_gauge_leakage(
    one_probabilities: Sequence[Q],
) -> LeakageCertificate:
    probabilities = tuple(map(q, one_probabilities))
    gauge = binary_experiment(probabilities)
    empty = constant_experiment(len(probabilities))
    problem = three_policy_problem()
    if len(probabilities) != problem.target_count:
        raise ValueError("the frozen decision type has exactly three targets")
    return LeakageCertificate(
        probabilities=probabilities,
        analytic_radius=gauge_leakage_radius(probabilities),
        decision_relative_radius=relative_deficiency(
            empty, gauge, (problem,)
        ).epsilon,
        ordinary_radius=ordinary_deficiency(empty, gauge).epsilon,
        reverse_decision_relative=relative_deficiency(
            gauge, empty, (problem,)
        ).epsilon,
        reverse_ordinary=ordinary_deficiency(gauge, empty).epsilon,
    )


def intervene_on_gauge(
    one_probabilities: Sequence[Q], intervention_probability: Q
) -> tuple[Q, ...]:
    """Replace the observational assignment by target-independent randomization."""

    probabilities = tuple(map(q, one_probabilities))
    intervention_probability = q(intervention_probability)
    if any(value < 0 or value > 1 for value in probabilities):
        raise ValueError("observational probabilities must lie in [0,1]")
    if intervention_probability < 0 or intervention_probability > 1:
        raise ValueError("intervention probability must lie in [0,1]")
    return (intervention_probability,) * len(probabilities)


def target_queries(high: Q, low: Q) -> dict[str, tuple[Q, ...]]:
    high, low = q(high), q(low)
    if not (Q(0) <= low < high <= Q(1)):
        raise ValueError("expected 0 <= low < high <= 1")
    return {
        "q0": (high, low, low),
        "q1": (low, high, low),
        "q2": (low, low, high),
        "q0_complement": (Q(1) - high, Q(1) - low, Q(1) - low),
        "constant": (Q(1, 2),) * 3,
    }


@dataclass(frozen=True)
class AlignmentCertificate:
    high: Q
    low: Q
    gauge_assignment: str
    leakage_radius: Q
    relative_substitution_deficiency: Q
    ordinary_substitution_deficiency: Q

    def jsonable(self) -> dict:
        return {
            key: qstr(value) if isinstance(value, Q) else value
            for key, value in asdict(self).items()
        }


def certify_access_alignment(
    high: Q, low: Q, gauge_assignment: str
) -> AlignmentCertificate:
    """Compare retained q1 + observed gauge against target access q0 + q1."""

    high, low = q(high), q(low)
    queries = target_queries(high, low)
    try:
        gauge = queries[gauge_assignment]
    except KeyError as exc:
        raise ValueError(f"unknown gauge assignment: {gauge_assignment}") from exc
    reference = independent_binary_product((queries["q0"], queries["q1"]))
    source = independent_binary_product((queries["q1"], gauge))
    problem = three_policy_problem()
    return AlignmentCertificate(
        high=high,
        low=low,
        gauge_assignment=gauge_assignment,
        leakage_radius=gauge_leakage_radius(gauge),
        relative_substitution_deficiency=relative_deficiency(
            source, reference, (problem,)
        ).epsilon,
        ordinary_substitution_deficiency=ordinary_deficiency(
            source, reference
        ).epsilon,
    )


DEVELOPMENT_STRENGTHS = (
    (Q(2, 3), Q(1, 3)),
    (Q(3, 4), Q(1, 4)),
    (Q(4, 5), Q(1, 5)),
    (Q(3, 5), Q(2, 5)),
)


def run_burned_development() -> dict:
    rows = []
    for high, low in DEVELOPMENT_STRENGTHS:
        for assignment in ("q0", "q0_complement", "q1", "q2", "constant"):
            rows.append(
                certify_access_alignment(
                    high, low, assignment
                ).jsonable()
            )
    return {
        "phase": "burned_development",
        "rows": rows,
        "row_count": len(rows),
    }
