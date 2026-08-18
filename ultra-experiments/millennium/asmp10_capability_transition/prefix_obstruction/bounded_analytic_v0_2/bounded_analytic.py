#!/usr/bin/env python3
"""Exact solver for the ASMP-10 bounded codimension-one continuation slice.

The implementation deliberately uses only :class:`fractions.Fraction` for the
mathematical path.  It discovers the first Hermite-kernel direction by exact
row reduction; the independent verifier in ``verify_bounded_analytic.py`` uses
a separate product, determinant, and dual-norm construction.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Iterable, Sequence


BASIS_ID = "monomial_ascending_in_physical_x_v1"
NORM_ID = "coefficient_l1_in_frozen_basis_v1"

# Each metric is a tuple of (weight, node offset from n, derivative order).
# A metric acts linearly on a continuation polynomial.  Its absolute
# difference induces the registered future-score pseudometric on pairs.
METRIC_SPECS: dict[str, tuple[tuple[Fraction, int, int], ...]] = {
    "future_gradient_at_n": ((Fraction(1), 0, 1),),
    "future_value_at_n": ((Fraction(1), 0, 0),),
    "future_value_at_n_plus_1": ((Fraction(1), 1, 0),),
    "future_gradient_at_n_plus_1": ((Fraction(1), 1, 1),),
    "future_secant_n_to_n_plus_1": (
        (Fraction(-1), 0, 0),
        (Fraction(1), 1, 0),
    ),
}


def as_fraction(value: int | str | Fraction) -> Fraction:
    """Coerce an exact public input while rejecting floating-point values."""

    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("budgets and exact inputs must not be bool or float")
    return Fraction(value)


def falling_factorial(degree: int, order: int) -> int:
    if degree < 0 or order < 0:
        raise ValueError("degree and derivative order must be nonnegative")
    if degree < order:
        return 0
    return math.factorial(degree) // math.factorial(degree - order)


def monomial_derivative_value(degree: int, order: int, x: int) -> Fraction:
    coefficient = falling_factorial(degree, order)
    if coefficient == 0:
        return Fraction(0)
    return Fraction(coefficient * (x ** (degree - order)))


def hermite_matrix(n_nodes: int, jet_order: int, degree: int) -> list[list[Fraction]]:
    """Return jets at nodes ``0,...,n_nodes-1`` in the frozen monomial basis."""

    if n_nodes < 1:
        raise ValueError("n_nodes must be positive")
    if jet_order < 0 or degree < 0:
        raise ValueError("jet_order and degree must be nonnegative")
    return [
        [
            monomial_derivative_value(column, order, node)
            for column in range(degree + 1)
        ]
        for node in range(n_nodes)
        for order in range(jet_order + 1)
    ]


def rref(
    matrix: Iterable[Iterable[Fraction]],
    n_columns: int,
) -> tuple[list[list[Fraction]], tuple[int, ...]]:
    """Compute exact reduced row-echelon form and pivot columns."""

    work = [[Fraction(value) for value in row] for row in matrix]
    if any(len(row) != n_columns for row in work):
        raise ValueError("ragged matrix")
    pivot_row = 0
    pivots: list[int] = []
    for column in range(n_columns):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(work):
            break
    return work, tuple(pivots)


def nullspace_basis(matrix: list[list[Fraction]], n_columns: int) -> list[tuple[Fraction, ...]]:
    reduced, pivots = rref(matrix, n_columns)
    pivot_set = set(pivots)
    free_columns = [column for column in range(n_columns) if column not in pivot_set]
    basis: list[tuple[Fraction, ...]] = []
    for free in free_columns:
        vector = [Fraction(0)] * n_columns
        vector[free] = Fraction(1)
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free]
        basis.append(tuple(vector))
    return basis


def matvec(
    matrix: Sequence[Sequence[Fraction]],
    vector: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    return tuple(
        sum((left * right for left, right in zip(row, vector)), Fraction(0))
        for row in matrix
    )


def coefficient_l1(coefficients: Sequence[Fraction]) -> Fraction:
    return sum((abs(value) for value in coefficients), Fraction(0))


def metric_vector(n_nodes: int, degree: int, metric_name: str) -> tuple[Fraction, ...]:
    try:
        terms = METRIC_SPECS[metric_name]
    except KeyError as error:
        raise ValueError(f"unknown registered metric: {metric_name}") from error
    return tuple(
        sum(
            (
                weight
                * monomial_derivative_value(column, derivative_order, n_nodes + offset)
                for weight, offset, derivative_order in terms
            ),
            Fraction(0),
        )
        for column in range(degree + 1)
    )


def evaluate_metric(
    coefficients: Sequence[Fraction],
    n_nodes: int,
    metric_name: str,
) -> Fraction:
    vector = metric_vector(n_nodes, len(coefficients) - 1, metric_name)
    return sum(
        (left * right for left, right in zip(vector, coefficients)),
        Fraction(0),
    )


def multiply_polynomials(
    left: Sequence[Fraction],
    right: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    output = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_degree, left_value in enumerate(left):
        for right_degree, right_value in enumerate(right):
            output[left_degree + right_degree] += left_value * right_value
    return tuple(output)


def explicit_kernel_product(n_nodes: int, jet_order: int) -> tuple[Fraction, ...]:
    """Return ``prod_i (x-i)^(jet_order+1)`` in ascending monomials."""

    coefficients: tuple[Fraction, ...] = (Fraction(1),)
    for node in range(n_nodes):
        factor = (Fraction(-node), Fraction(1))
        for _ in range(jet_order + 1):
            coefficients = multiply_polynomials(coefficients, factor)
    return coefficients


def shifted_monomial_coefficients(
    coefficients: Sequence[Fraction],
    center: Fraction,
) -> tuple[Fraction, ...]:
    """Express ``p(x)`` as ``sum b_j (x-center)^j`` exactly."""

    # Put y=x-center, so x=y+center and expand p(y+center).
    output = [Fraction(0)] * len(coefficients)
    for degree, value in enumerate(coefficients):
        for shifted_degree in range(degree + 1):
            output[shifted_degree] += (
                value
                * math.comb(degree, shifted_degree)
                * center ** (degree - shifted_degree)
            )
    return tuple(output)


def identified_control(n_nodes: int, jet_order: int) -> dict[str, int]:
    observations = n_nodes * (jet_order + 1)
    degree = observations - 1
    matrix = hermite_matrix(n_nodes, jet_order, degree)
    _, pivots = rref(matrix, degree + 1)
    rank = len(pivots)
    return {
        "n_nodes": n_nodes,
        "jet_order": jet_order,
        "degree": degree,
        "rank": rank,
        "nullity": degree + 1 - rank,
    }


def solve_first_kernel(
    n_nodes: int,
    jet_order: int,
    budget: int | str | Fraction,
    metric_name: str = "future_gradient_at_n",
    *,
    basis_id: str = BASIS_ID,
) -> dict[str, object]:
    """Solve the exact pairwise envelope in the first Hermite kernel.

    The optimization is over pairs ``p_plus,p_minus`` with identical exact
    registered jets and with each frozen-basis coefficient L1 norm at most
    ``budget``.  At degree ``J=n(k+1)`` the difference is one-dimensional.
    """

    if basis_id != BASIS_ID:
        raise ValueError(f"basis must be exactly {BASIS_ID}")
    exact_budget = as_fraction(budget)
    if exact_budget < 0:
        raise ValueError("budget must be nonnegative")

    observations = n_nodes * (jet_order + 1)
    degree = observations
    matrix = hermite_matrix(n_nodes, jet_order, degree)
    _, pivots = rref(matrix, degree + 1)
    kernel = nullspace_basis(matrix, degree + 1)
    if len(kernel) != 1:
        raise AssertionError("registered first-kernel system is not codimension one")

    direction = kernel[0]
    if direction[-1] == 0:
        raise AssertionError("kernel direction cannot be normalized to monic form")
    direction = tuple(value / direction[-1] for value in direction)
    direction_l1 = coefficient_l1(direction)
    metric_on_direction = evaluate_metric(direction, n_nodes, metric_name)
    amplitude = exact_budget / direction_l1
    plus = tuple(amplitude * value for value in direction)
    minus = tuple(-value for value in plus)
    plus_prefix = matvec(matrix, plus)
    minus_prefix = matvec(matrix, minus)
    separation = abs(
        evaluate_metric(plus, n_nodes, metric_name)
        - evaluate_metric(minus, n_nodes, metric_name)
    )
    optimum = Fraction(2) * exact_budget * abs(metric_on_direction) / direction_l1

    return {
        "basis_id": BASIS_ID,
        "norm_id": NORM_ID,
        "n_nodes": n_nodes,
        "jet_order": jet_order,
        "observations": observations,
        "degree": degree,
        "rank": len(pivots),
        "nullity": degree + 1 - len(pivots),
        "budget": exact_budget,
        "metric_name": metric_name,
        "kernel_direction": direction,
        "kernel_l1": direction_l1,
        "metric_on_kernel": metric_on_direction,
        "witness_amplitude": amplitude,
        "plus_coefficients": plus,
        "minus_coefficients": minus,
        "plus_prefix": plus_prefix,
        "minus_prefix": minus_prefix,
        "witness_separation": separation,
        "optimum_separation": optimum,
    }


def witness_is_feasible(result: dict[str, object]) -> bool:
    plus = result["plus_coefficients"]
    minus = result["minus_coefficients"]
    if not isinstance(plus, tuple) or not isinstance(minus, tuple):
        return False
    budget = result["budget"]
    if not isinstance(budget, Fraction):
        return False
    n_nodes = int(result["n_nodes"])
    jet_order = int(result["jet_order"])
    degree = int(result["degree"])
    metric_name = str(result["metric_name"])
    matrix = hermite_matrix(n_nodes, jet_order, degree)
    plus_prefix = matvec(matrix, plus)
    minus_prefix = matvec(matrix, minus)
    separation = abs(
        evaluate_metric(plus, n_nodes, metric_name)
        - evaluate_metric(minus, n_nodes, metric_name)
    )
    return bool(
        plus_prefix == minus_prefix
        and coefficient_l1(plus) <= budget
        and coefficient_l1(minus) <= budget
        and separation == result["witness_separation"]
        and separation == result["optimum_separation"]
    )
