"""Exact allocation algebra for the ASMP-9 v0.70 Gaussian quotient.

The input rows are already expressed in the representative-insensitive
quotient coordinates supplied by v0.69.  Arithmetic for information, risk,
allocation, and fixed mean bias is exact over the rationals.  Gaussian tail
probabilities are descriptive floating evaluations of the proved formula.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import erfc, sqrt
from typing import Iterable, Sequence

import sympy as sp


def rational_matrix(rows: Sequence[Sequence[object]]) -> sp.Matrix:
    return sp.Matrix([[sp.Rational(value) for value in row] for row in rows])


def information_matrix(
    rows: sp.Matrix,
    variances: Sequence[object],
    allocation: Sequence[int],
) -> sp.Matrix:
    if rows.rows != len(variances) or rows.rows != len(allocation):
        raise ValueError("one variance and allocation count are required per row")
    if any(int(count) != count or count < 0 for count in allocation):
        raise ValueError("allocation counts must be nonnegative integers")

    information = sp.zeros(rows.cols, rows.cols)
    for index, count in enumerate(allocation):
        variance = sp.Rational(variances[index])
        if variance <= 0:
            raise ValueError("noise variances must be positive")
        row = rows[index, :].T
        information += sp.Rational(count, 1) / variance * (row * row.T)
    return information


def parameter_minimax_risk(information: sp.Matrix) -> sp.Expr:
    """Exact squared-Euclidean minimax risk, or infinity if unidentified."""

    if information.rows != information.cols:
        raise ValueError("information matrix must be square")
    if information.rank() < information.rows:
        return sp.oo
    return sp.trace(information.inv())


def quadratic_minimax_risk(
    information: sp.Matrix, loss_matrix: sp.Matrix
) -> sp.Expr:
    if loss_matrix.shape != information.shape:
        raise ValueError("loss and information matrices must have equal shape")
    if information.rank() < information.rows:
        return sp.oo
    return sp.trace(loss_matrix * information.inv())


def functional_variance(
    information: sp.Matrix, functional: sp.Matrix
) -> sp.Expr:
    if functional.cols != 1 or functional.rows != information.rows:
        raise ValueError("functional must be a compatible column vector")
    if information.rank() < information.rows:
        return sp.oo
    return (functional.T * information.inv() * functional)[0]


def estimator_bias(
    rows: sp.Matrix,
    variances: Sequence[object],
    allocation: Sequence[int],
    mean_bias: Sequence[object],
) -> sp.Matrix | None:
    """Mean bias of weighted least squares under per-query mean shifts."""

    if len(mean_bias) != rows.rows:
        raise ValueError("one mean bias is required per query row")
    information = information_matrix(rows, variances, allocation)
    if information.rank() < information.rows:
        return None
    score_bias = sp.zeros(rows.cols, 1)
    for index, count in enumerate(allocation):
        score_bias += (
            sp.Rational(count, 1)
            / sp.Rational(variances[index])
            * rows[index, :].T
            * sp.Rational(mean_bias[index])
        )
    return information.inv() * score_bias


def biased_parameter_mse(
    rows: sp.Matrix,
    variances: Sequence[object],
    allocation: Sequence[int],
    mean_bias: Sequence[object],
) -> sp.Expr:
    information = information_matrix(rows, variances, allocation)
    risk = parameter_minimax_risk(information)
    if risk is sp.oo:
        return sp.oo
    bias = estimator_bias(rows, variances, allocation, mean_bias)
    assert bias is not None
    return risk + (bias.T * bias)[0]


def two_policy_plugin_error(
    margin: float, functional_variance_value: float
) -> dict[str, float]:
    """Evaluate the exact normal-tail formula for a two-policy plug-in rule."""

    if margin <= 0:
        raise ValueError("the registered optimal-policy margin must be positive")
    if functional_variance_value <= 0:
        raise ValueError("functional variance must be positive")
    z_score = margin / sqrt(functional_variance_value)
    error_probability = 0.5 * erfc(z_score / sqrt(2.0))
    return {
        "z_score": z_score,
        "error_probability": error_probability,
        "expected_simple_regret": margin * error_probability,
    }


def weak_compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if total < 0 or parts <= 0:
        raise ValueError("invalid composition dimensions")
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in weak_compositions(total - first, parts - 1):
            yield (first,) + rest


@dataclass(frozen=True)
class AllocationOptimum:
    objective: sp.Expr
    allocations: tuple[tuple[int, ...], ...]
    evaluated_allocations: int
    identified_allocations: int

    def to_jsonable(self) -> dict[str, object]:
        return {
            "objective": str(self.objective),
            "allocations": [list(value) for value in self.allocations],
            "evaluated_allocations": self.evaluated_allocations,
            "identified_allocations": self.identified_allocations,
        }


def exact_allocation_optimum(
    rows: sp.Matrix,
    variances: Sequence[object],
    total: int,
    *,
    functional: sp.Matrix | None = None,
) -> AllocationOptimum:
    best: sp.Expr | None = None
    winners: list[tuple[int, ...]] = []
    evaluated = 0
    identified = 0

    for allocation in weak_compositions(total, rows.rows):
        evaluated += 1
        information = information_matrix(rows, variances, allocation)
        if information.rank() < rows.cols:
            continue
        identified += 1
        objective = (
            parameter_minimax_risk(information)
            if functional is None
            else functional_variance(information, functional)
        )
        if best is None or objective < best:
            best = objective
            winners = [allocation]
        elif objective == best:
            winners.append(allocation)

    if best is None:
        return AllocationOptimum(
            objective=sp.oo,
            allocations=tuple(),
            evaluated_allocations=evaluated,
            identified_allocations=identified,
        )
    return AllocationOptimum(
        objective=best,
        allocations=tuple(winners),
        evaluated_allocations=evaluated,
        identified_allocations=identified,
    )


def worst_vertex_bias_mse(
    rows: sp.Matrix,
    variances: Sequence[object],
    allocation: Sequence[int],
    bias_radii: Sequence[object],
) -> dict[str, object]:
    """Exact worst MSE over the registered rectangular mean-bias class."""

    if len(bias_radii) != rows.rows:
        raise ValueError("one bias radius is required per row")
    vertices = [
        tuple(
            sign * sp.Rational(radius)
            for sign, radius in zip(signs, bias_radii)
        )
        for signs in product((-1, 1), repeat=rows.rows)
    ]
    records = [
        (biased_parameter_mse(rows, variances, allocation, vertex), vertex)
        for vertex in vertices
    ]
    worst = max(value for value, _ in records)
    witnesses = [vertex for value, vertex in records if value == worst]
    return {
        "worst_mse": str(worst),
        "witnesses": [[str(value) for value in row] for row in witnesses],
        "vertex_count": len(vertices),
    }


def canonical_fixture() -> tuple[sp.Matrix, tuple[Fraction, ...]]:
    """Two-dimensional quotient with three scalar query directions."""

    rows = rational_matrix([[1, 0], [0, 1], [1, 1]])
    variances = (Fraction(1), Fraction(1), Fraction(1))
    return rows, variances
