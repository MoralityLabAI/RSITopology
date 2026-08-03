#!/usr/bin/env python3
"""Independent closed-form and dual verifier for bounded analytic v0.2.

This module intentionally imports nothing from ``bounded_analytic``.  It
reconstructs the Hermite product, checks an independent square determinant,
evaluates the future metric symbolically, and supplies the L-infinity dual
witness for the frozen coefficient L1 norm.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Sequence


BASIS_ID = "monomial_ascending_in_physical_x_v1"
NORM_ID = "coefficient_l1_in_frozen_basis_v1"

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


def _multiply(left: Sequence[Fraction], right: Sequence[Fraction]) -> tuple[Fraction, ...]:
    output = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_degree, left_value in enumerate(left):
        for right_degree, right_value in enumerate(right):
            output[left_degree + right_degree] += left_value * right_value
    return tuple(output)


def closed_form_kernel(n_nodes: int, jet_order: int) -> tuple[Fraction, ...]:
    if n_nodes < 1 or jet_order < 0:
        raise ValueError("invalid Hermite dimensions")
    result: tuple[Fraction, ...] = (Fraction(1),)
    for root in range(n_nodes):
        for _ in range(jet_order + 1):
            result = _multiply(result, (Fraction(-root), Fraction(1)))
    return result


def derivative_value(
    coefficients: Sequence[Fraction],
    x: int,
    order: int,
) -> Fraction:
    total = Fraction(0)
    for degree in range(order, len(coefficients)):
        multiplier = math.factorial(degree) // math.factorial(degree - order)
        total += coefficients[degree] * multiplier * (x ** (degree - order))
    return total


def evaluate_metric(
    coefficients: Sequence[Fraction],
    n_nodes: int,
    metric_name: str,
) -> Fraction:
    try:
        terms = METRIC_SPECS[metric_name]
    except KeyError as error:
        raise ValueError(f"unknown registered metric: {metric_name}") from error
    return sum(
        (
            weight * derivative_value(coefficients, n_nodes + offset, order)
            for weight, offset, order in terms
        ),
        Fraction(0),
    )


def _jet_entry(degree: int, order: int, node: int) -> Fraction:
    if degree < order:
        return Fraction(0)
    multiplier = math.factorial(degree) // math.factorial(degree - order)
    return Fraction(multiplier * node ** (degree - order))


def identified_square_matrix(n_nodes: int, jet_order: int) -> list[list[Fraction]]:
    observations = n_nodes * (jet_order + 1)
    return [
        [_jet_entry(column, order, node) for column in range(observations)]
        for node in range(n_nodes)
        for order in range(jet_order + 1)
    ]


def exact_determinant(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    """Compute a determinant by independent fraction-preserving elimination."""

    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant requires a square matrix")
    if size == 0:
        return Fraction(1)
    work = [[Fraction(value) for value in row] for row in matrix]
    sign = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        pivot_value = work[column][column]
        for row in range(column + 1, size):
            if work[row][column] == 0:
                continue
            factor = work[row][column] / pivot_value
            for inner_column in range(column, size):
                work[row][inner_column] -= factor * work[column][inner_column]
    determinant = sign
    for diagonal in range(size):
        determinant *= work[diagonal][diagonal]
    return determinant


def primary_gradient_closed_form(n_nodes: int, jet_order: int) -> Fraction:
    """Return q'(n) from q(n) times the logarithmic derivative."""

    multiplicity = jet_order + 1
    q_at_n = Fraction(math.factorial(n_nodes) ** multiplicity)
    harmonic = sum((Fraction(1, distance) for distance in range(1, n_nodes + 1)), Fraction(0))
    return multiplicity * q_at_n * harmonic


def sign_dual(coefficients: Sequence[Fraction]) -> tuple[Fraction, ...]:
    return tuple(
        Fraction(1) if value > 0 else Fraction(-1) if value < 0 else Fraction(0)
        for value in coefficients
    )


def independent_certificate(
    n_nodes: int,
    jet_order: int,
    budget: int | str | Fraction,
    metric_name: str,
) -> dict[str, object]:
    exact_budget = Fraction(budget)
    if exact_budget < 0:
        raise ValueError("budget must be nonnegative")
    kernel = closed_form_kernel(n_nodes, jet_order)
    kernel_l1 = sum((abs(value) for value in kernel), Fraction(0))
    metric_on_kernel = evaluate_metric(kernel, n_nodes, metric_name)
    dual = sign_dual(kernel)
    dual_pairing = sum(
        (left * right for left, right in zip(dual, kernel)),
        Fraction(0),
    )
    determinant = exact_determinant(identified_square_matrix(n_nodes, jet_order))
    exact_prefix_kernel = all(
        derivative_value(kernel, node, order) == 0
        for node in range(n_nodes)
        for order in range(jet_order + 1)
    )
    optimum = Fraction(2) * exact_budget * abs(metric_on_kernel) / kernel_l1
    primary_closed_form_ok = (
        metric_name != "future_gradient_at_n"
        or metric_on_kernel == primary_gradient_closed_form(n_nodes, jet_order)
    )
    checks = {
        "identified_square_determinant_nonzero": determinant != 0,
        "closed_form_kernel_has_registered_multiplicities": exact_prefix_kernel,
        "kernel_is_monic_at_first_nullity": len(kernel) == n_nodes * (jet_order + 1) + 1
        and kernel[-1] == 1,
        "dual_linf_feasible": max((abs(value) for value in dual), default=Fraction(0)) <= 1,
        "dual_saturates_l1": dual_pairing == kernel_l1,
        "primary_gradient_closed_form": primary_closed_form_ok,
    }
    return {
        "basis_id": BASIS_ID,
        "norm_id": NORM_ID,
        "kernel_direction": kernel,
        "kernel_l1": kernel_l1,
        "metric_on_kernel": metric_on_kernel,
        "dual_vector": dual,
        "identified_determinant": determinant,
        "optimum_separation": optimum,
        "checks": checks,
        "certificate_valid": all(checks.values()),
    }


def verify_solver_result(result: dict[str, object]) -> dict[str, object]:
    certificate = independent_certificate(
        int(result["n_nodes"]),
        int(result["jet_order"]),
        result["budget"],
        str(result["metric_name"]),
    )
    agreements = {
        "basis": result["basis_id"] == certificate["basis_id"],
        "norm": result["norm_id"] == certificate["norm_id"],
        "kernel": result["kernel_direction"] == certificate["kernel_direction"],
        "kernel_l1": result["kernel_l1"] == certificate["kernel_l1"],
        "metric_on_kernel": result["metric_on_kernel"] == certificate["metric_on_kernel"],
        "optimum": result["optimum_separation"] == certificate["optimum_separation"],
    }
    return {
        "agreements": agreements,
        "certificate": certificate,
        "verified": certificate["certificate_valid"] and all(agreements.values()),
    }

