"""Sharp confidence-set modulus at a registered finite sample atom.

Development-only instrument for ASMP-9 v0.47.  The central result is generic:
uniform coverage forces every parameter whose probability of the observed atom
exceeds alpha into any deterministic confidence set at that atom.  A
whole-space-everywhere-else construction attains that mandatory set.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
from math import comb
from pathlib import Path
import sys
from typing import Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
V45 = HERE.parent / "sample_allocation_v0_45"
V46 = HERE.parent / "coupled_uncertainty_v0_46"
for path in (V45, V46):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from allocation_design import positive_allocations  # noqa: E402
from coupled_uncertainty import (  # noqa: E402
    certified_minimax_classification,
    flip_probability_bounds,
)


Parameter = tuple[Q, Q, Q]


def q(value: object) -> Q:
    return value if isinstance(value, Q) else Q(str(value))


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def validate_levels(levels: Iterable[object]) -> tuple[Q, ...]:
    result = tuple(sorted({q(value) for value in levels}))
    if not result or result[0] != 0:
        raise ValueError("the finite channel grid must contain zero")
    if any(value < 0 or value > Q(1, 2) for value in result):
        raise ValueError("flip levels must lie in [0,1/2]")
    return result


def parameter_grid(levels: Iterable[object]) -> tuple[Parameter, ...]:
    levels = validate_levels(levels)
    return tuple(product(levels, repeat=3))


def validate_allocation(allocation: Sequence[int]) -> tuple[int, int, int]:
    result = tuple(int(value) for value in allocation)
    if len(result) != 3 or any(value < 1 for value in result):
        raise ValueError("allocation must contain three positive counts")
    return result


def validate_parameter(parameter: Sequence[object]) -> Parameter:
    result = tuple(q(value) for value in parameter)
    if len(result) != 3 or any(
        value < 0 or value > Q(1, 2) for value in result
    ):
        raise ValueError("parameter must contain three rates in [0,1/2]")
    return result


def all_zero_probability(
    parameter: Sequence[object],
    allocation: Sequence[int],
) -> Q:
    parameter = validate_parameter(parameter)
    allocation = validate_allocation(allocation)
    result = Q(1)
    for flip, samples in zip(parameter, allocation):
        result *= _survival_power(flip, samples)
    return result


def total_error_cdf(
    parameter: Sequence[object],
    allocation: Sequence[int],
) -> tuple[Q, ...]:
    """Exact CDF of the total calibration-error count.

    The three cells are independent binomials with registered sample counts
    and possibly different symmetric-flip probabilities.  The returned row
    has support ``0,...,sum(allocation)`` and is suitable for
    :func:`buehler_upper_table`.
    """

    parameter = validate_parameter(parameter)
    allocation = validate_allocation(allocation)
    masses = [Q(1)]
    for flip, samples in zip(parameter, allocation):
        cell = [
            Q(comb(samples, errors))
            * flip**errors
            * (Q(1) - flip) ** (samples - errors)
            for errors in range(samples + 1)
        ]
        combined = [Q(0)] * (len(masses) + len(cell) - 1)
        for left_index, left in enumerate(masses):
            for right_index, right in enumerate(cell):
                combined[left_index + right_index] += left * right
        masses = combined
    cumulative = []
    running = Q(0)
    for mass in masses:
        running += mass
        cumulative.append(running)
    if cumulative[-1] != 1:
        raise AssertionError("total-error law does not sum to one")
    if cumulative[0] != all_zero_probability(parameter, allocation):
        raise AssertionError("minimum-statistic atom does not match")
    return tuple(cumulative)


@lru_cache(maxsize=None)
def _survival_power(flip: Q, samples: int) -> Q:
    return (Q(1) - flip) ** samples


def mandatory_atom_region(
    parameters: Iterable[Sequence[object]],
    allocation: Sequence[int],
    alpha: object,
) -> tuple[Parameter, ...]:
    """Parameters every deterministic honest confidence set must contain.

    The strict inequality is load-bearing.  A parameter whose atom
    probability equals alpha may be excluded while retaining coverage exactly
    1-alpha.
    """

    allocation = validate_allocation(allocation)
    alpha = q(alpha)
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    normalized = tuple(validate_parameter(row) for row in parameters)
    if len(set(normalized)) != len(normalized):
        raise ValueError("parameter grid contains duplicates")
    return tuple(
        parameter
        for parameter in normalized
        if all_zero_probability(parameter, allocation) > alpha
    )


def boundary_parameters(
    parameters: Iterable[Sequence[object]],
    allocation: Sequence[int],
    alpha: object,
) -> tuple[Parameter, ...]:
    allocation = validate_allocation(allocation)
    alpha = q(alpha)
    return tuple(
        parameter
        for parameter in (
            validate_parameter(row) for row in parameters
        )
        if all_zero_probability(parameter, allocation) == alpha
    )


def spike_confidence_coverage(
    parameters: Iterable[Sequence[object]],
    allocation: Sequence[int],
    alpha: object,
) -> dict[Parameter, Q]:
    """Coverage of the sharp atom construction.

    At the registered all-zero atom it returns precisely the mandatory
    parameter set.  At every other sample outcome it returns the full
    parameter set.  A parameter outside the mandatory set can therefore fail
    coverage only at the all-zero atom, whose probability is at most alpha.
    """

    allocation = validate_allocation(allocation)
    alpha = q(alpha)
    normalized = tuple(validate_parameter(row) for row in parameters)
    mandatory = set(mandatory_atom_region(normalized, allocation, alpha))
    return {
        parameter: (
            Q(1)
            if parameter in mandatory
            else Q(1) - all_zero_probability(parameter, allocation)
        )
        for parameter in normalized
    }


@dataclass(frozen=True)
class AtomModulus:
    allocation: tuple[int, int, int]
    alpha: Q
    mandatory_count: int
    boundary_count: int
    lower: Q
    upper: Q
    witnesses: tuple[Parameter, ...]
    minimum_spike_coverage: Q

    def jsonable(self) -> dict:
        return {
            "allocation": list(self.allocation),
            "alpha": qstr(self.alpha),
            "mandatory_count": self.mandatory_count,
            "boundary_count": self.boundary_count,
            "lower": qstr(self.lower),
            "upper": qstr(self.upper),
            "witnesses": [
                [qstr(value) for value in parameter]
                for parameter in self.witnesses
            ],
            "minimum_spike_coverage": qstr(
                self.minimum_spike_coverage
            ),
            "matched": self.lower == self.upper,
        }


def buehler_upper_table(
    risks: Mapping[object, Q],
    statistic_cdfs: Mapping[object, Sequence[Q]],
    alpha: object,
) -> tuple[Q, ...]:
    """Smallest nondecreasing honest upper bound based on one statistic.

    ``statistic_cdfs[theta][t]`` is ``P_theta(T <= t)`` on the registered
    ordered statistic support.  The formula is the finite Buehler
    construction:

        U(t) = sup {d(theta): P_theta(T <= t) > alpha}.
    """

    alpha = q(alpha)
    if not 0 < alpha < 1 or not risks:
        raise ValueError("invalid Buehler inputs")
    if set(risks) != set(statistic_cdfs):
        raise ValueError("risk and CDF parameter universes differ")
    lengths = {len(tuple(row)) for row in statistic_cdfs.values()}
    if len(lengths) != 1 or next(iter(lengths)) < 1:
        raise ValueError("CDF rows must share a positive length")
    width = next(iter(lengths))
    cdfs = {
        parameter: tuple(q(value) for value in row)
        for parameter, row in statistic_cdfs.items()
    }
    for row in cdfs.values():
        if (
            row[-1] != 1
            or any(not 0 <= value <= 1 for value in row)
            or any(left > right for left, right in zip(row, row[1:]))
        ):
            raise ValueError("invalid statistic CDF")
    normalized_risks = {
        parameter: q(value) for parameter, value in risks.items()
    }
    if any(value < 0 for value in normalized_risks.values()):
        raise ValueError("risks must be nonnegative")
    result = []
    for index in range(width):
        eligible = [
            normalized_risks[parameter]
            for parameter in normalized_risks
            if cdfs[parameter][index] > alpha
        ]
        result.append(max(eligible, default=Q(0)))
    if any(left > right for left, right in zip(result, result[1:])):
        raise AssertionError("Buehler table is not nondecreasing")
    for parameter, risk in normalized_risks.items():
        previous = Q(0)
        noncoverage = Q(0)
        for bound, cumulative in zip(result, cdfs[parameter]):
            mass = cumulative - previous
            previous = cumulative
            if risk > bound:
                noncoverage += mass
        if noncoverage > alpha:
            raise AssertionError("Buehler table violates coverage")
    return tuple(result)


def sharp_atom_modulus(
    risks: Mapping[Parameter, Q],
    allocation: Sequence[int],
    alpha: object,
    parameter_universe: Iterable[Sequence[object]] | None = None,
) -> AtomModulus:
    """Exact lower/upper confidence modulus at the all-zero atom."""

    if not risks:
        raise ValueError("risk table is empty")
    allocation = validate_allocation(allocation)
    alpha = q(alpha)
    normalized = {
        validate_parameter(parameter): q(risk)
        for parameter, risk in risks.items()
    }
    if any(risk < 0 for risk in normalized.values()):
        raise ValueError("risks must be nonnegative")
    parameters = tuple(
        sorted(
            normalized
            if parameter_universe is None
            else {
                validate_parameter(parameter)
                for parameter in parameter_universe
            }
        )
    )
    if not parameters:
        raise ValueError("parameter universe is empty")
    atom_probabilities = {
        parameter: all_zero_probability(parameter, allocation)
        for parameter in parameters
    }
    mandatory = tuple(
        parameter
        for parameter in parameters
        if atom_probabilities[parameter] > alpha
    )
    if not mandatory:
        raise AssertionError("zero channel should always be mandatory")
    missing = set(mandatory).difference(normalized)
    if missing:
        raise ValueError(
            "risk table omits mandatory parameters: "
            f"{sorted(missing)[:3]}"
        )
    boundary = tuple(
        parameter
        for parameter in parameters
        if atom_probabilities[parameter] == alpha
    )
    optimum = max(normalized[parameter] for parameter in mandatory)
    witnesses = tuple(
        parameter
        for parameter in mandatory
        if normalized[parameter] == optimum
    )
    mandatory_set = set(mandatory)
    minimum_coverage = min(
        (
            Q(1)
            if parameter in mandatory_set
            else Q(1) - atom_probabilities[parameter]
        )
        for parameter in parameters
    )
    if minimum_coverage < Q(1) - alpha:
        raise AssertionError("sharp atom construction is not honest")
    return AtomModulus(
        allocation=allocation,
        alpha=alpha,
        mandatory_count=len(mandatory),
        boundary_count=len(boundary),
        lower=optimum,
        upper=optimum,
        witnesses=witnesses,
        minimum_spike_coverage=minimum_coverage,
    )


def classification_risk_table(
    levels: Iterable[object],
    workers: int = 1,
) -> dict[Parameter, Q]:
    """Exact full-adaptive four-class risk over a finite channel grid."""

    return classification_risks(parameter_grid(levels), workers=workers)


def classification_risks(
    parameters: Iterable[Sequence[object]],
    workers: int = 1,
) -> dict[Parameter, Q]:
    """Exact full-adaptive risks on an explicit parameter subset."""

    parameters = tuple(
        sorted({validate_parameter(parameter) for parameter in parameters})
    )
    if not parameters:
        raise ValueError("parameter subset is empty")
    if workers < 1:
        raise ValueError("workers must be positive")
    if workers == 1:
        rows = map(_classification_risk_row, parameters)
    else:
        executor = ProcessPoolExecutor(max_workers=workers)
        try:
            rows = executor.map(
                _classification_risk_row,
                parameters,
                chunksize=1,
            )
            rows = tuple(rows)
        finally:
            executor.shutdown(wait=True, cancel_futures=True)
    return dict(rows)


def _classification_risk_row(
    parameter: Parameter,
) -> tuple[Parameter, Q]:
    parameter = validate_parameter(parameter)
    return (
        parameter,
        certified_minimax_classification(parameter)["risk"],
    )


def root_group_risk_table(
    levels: Iterable[object],
) -> dict[Parameter, Q]:
    """Exact root-group risk; branch channels are decision-irrelevant."""

    return {
        parameter: parameter[0]
        for parameter in parameter_grid(levels)
    }


def method_of_types_coupled_upper(
    allocation: Sequence[int],
    mode: str,
) -> Q:
    """Inherited v0.46 coupled upper at one fixed allocation."""

    allocation = validate_allocation(allocation)
    endpoints = tuple(
        flip_probability_bounds(samples).upper
        for samples in allocation
    )
    if mode == "branch_classification":
        return certified_minimax_classification(endpoints)["risk"]
    if mode == "root_group":
        return endpoints[0]
    raise ValueError("unknown decision mode")


@dataclass(frozen=True)
class AllocationModulusRow:
    allocation: tuple[int, int, int]
    modulus: AtomModulus

    def jsonable(self) -> dict:
        return self.modulus.jsonable()


def allocation_modulus_census(
    risks: Mapping[Parameter, Q],
    total_budget: int,
    alpha: object,
) -> dict:
    if total_budget < 3:
        raise ValueError("total budget must be at least three")
    rows = tuple(
        AllocationModulusRow(
            allocation=allocation,
            modulus=sharp_atom_modulus(risks, allocation, alpha),
        )
        for allocation in positive_allocations(total_budget, 3)
    )
    optimum = min(row.modulus.upper for row in rows)
    optimizers = tuple(
        row.allocation for row in rows if row.modulus.upper == optimum
    )
    quotient, remainder = divmod(total_budget, 3)
    uniform = tuple(
        quotient + int(index < remainder) for index in range(3)
    )
    uniform_row = next(row for row in rows if row.allocation == uniform)
    return {
        "total_budget": total_budget,
        "allocation_count": len(rows),
        "rows": rows,
        "optimum": optimum,
        "optimizers": optimizers,
        "unique": len(optimizers) == 1,
        "uniform": uniform_row,
    }
