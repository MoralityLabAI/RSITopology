"""Exact marginal-oracle reconstruction tools for ASMP-9 v0.24 development.

This module works in the frozen maximally noisy comparison model from v0.23.
For a graph with ``m`` edges, uniform count ``r`` corresponds to
``z = 2**(-r)``.  The liveness probability is a degree-at-most-``m``
polynomial ``P_G(z)`` with ``P_G(0) = 1``.

Exact ratios at consecutive uniform counts determine that polynomial up to
scale.  The value at zero fixes the scale.  Consecutive uniform ratios can in
turn be obtained by telescoping exact one-edge marginal ratios.

The routines below make that reduction executable with exact rational
arithmetic.  They are development instruments, not an optimizer.
"""

from __future__ import annotations

import importlib.util
from fractions import Fraction
from pathlib import Path
from typing import Callable, Sequence


Edge = tuple[int, int]
Polynomial = tuple[Fraction, ...]
MarginalOracle = Callable[[Sequence[int], int], Fraction]


def _load_v023_module():
    source = (
        Path(__file__).resolve().parents[1]
        / "nonuniform_multivariate_v0_23"
        / "nonuniform_multivariate.py"
    )
    spec = importlib.util.spec_from_file_location(
        "_asmp9_nonuniform_multivariate_v023", source
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load v0.23 source from {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_V023 = _load_v023_module()


def exact_availability(
    node_count: int,
    edges: Sequence[Edge],
    counts: Sequence[int],
) -> Fraction:
    """Return the exact v0.23 liveness probability."""

    return Fraction(
        _V023.multivariate_tutte_availability(
            node_count, tuple(edges), tuple(counts)
        )
    )


def polynomial_evaluate(
    coefficients: Sequence[Fraction], point: Fraction
) -> Fraction:
    """Evaluate monomial-basis coefficients by Horner's rule."""

    result = Fraction(0)
    for coefficient in reversed(tuple(coefficients)):
        result = result * point + Fraction(coefficient)
    return result


def _polynomial_add(
    left: Sequence[Fraction], right: Sequence[Fraction]
) -> list[Fraction]:
    size = max(len(left), len(right))
    result = [Fraction(0) for _ in range(size)]
    for index, value in enumerate(left):
        result[index] += Fraction(value)
    for index, value in enumerate(right):
        result[index] += Fraction(value)
    return result


def _polynomial_multiply(
    left: Sequence[Fraction], right: Sequence[Fraction]
) -> list[Fraction]:
    result = [
        Fraction(0) for _ in range(len(left) + len(right) - 1)
    ]
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] += (
                Fraction(left_value) * Fraction(right_value)
            )
    return result


def interpolate_polynomial(
    points: Sequence[Fraction], values: Sequence[Fraction]
) -> Polynomial:
    """Return the unique degree-``< len(points)`` interpolant."""

    xs = tuple(Fraction(point) for point in points)
    ys = tuple(Fraction(value) for value in values)
    if len(xs) != len(ys) or not xs:
        raise ValueError("points and values must have equal positive length")
    if len(set(xs)) != len(xs):
        raise ValueError("interpolation points must be distinct")

    result = [Fraction(0)]
    for index, (x_value, y_value) in enumerate(zip(xs, ys, strict=True)):
        basis = [Fraction(1)]
        denominator = Fraction(1)
        for other_index, other_x in enumerate(xs):
            if index == other_index:
                continue
            basis = _polynomial_multiply(
                basis, (-other_x, Fraction(1))
            )
            denominator *= x_value - other_x
        scaled = [
            coefficient * y_value / denominator
            for coefficient in basis
        ]
        result = _polynomial_add(result, scaled)
    return tuple(result)


def relative_values_from_ratios(
    ratios: Sequence[Fraction],
) -> tuple[Fraction, ...]:
    """Convert consecutive ratios into values relative to the first."""

    values = [Fraction(1)]
    for ratio in ratios:
        ratio_value = Fraction(ratio)
        if ratio_value <= 0:
            raise ValueError("availability ratios must be positive")
        values.append(values[-1] * ratio_value)
    return tuple(values)


def availability_polynomial_from_uniform_ratios(
    ratios: Sequence[Fraction],
) -> Polynomial:
    """Reconstruct ``P_G(z)`` from ``P(2^-(r+1))/P(2^-r)``.

    If ``len(ratios) == m``, the interpolation nodes are
    ``2^-1, ..., 2^-(m+1)``.  The relative interpolant is ``P/P(1/2)``.
    Since ``P(0)=1``, its constant coefficient is ``1/P(1/2)``.
    """

    ratio_values = tuple(Fraction(value) for value in ratios)
    if not ratio_values:
        raise ValueError("at least one ratio is required")
    relative_values = relative_values_from_ratios(ratio_values)
    points = tuple(
        Fraction(1, 2**trial_count)
        for trial_count in range(1, len(relative_values) + 1)
    )
    relative_polynomial = interpolate_polynomial(
        points, relative_values
    )
    constant = relative_polynomial[0]
    if constant == 0:
        raise ZeroDivisionError(
            "relative interpolant vanishes at the normalization point"
        )
    scale = Fraction(1, 1) / constant
    result = tuple(scale * coefficient for coefficient in relative_polynomial)
    if result[0] != 1:
        raise AssertionError("normalization failed to recover P_G(0)=1")
    return result


def uniform_ratio_sequence(
    node_count: int, edges: Sequence[Edge]
) -> tuple[Fraction, ...]:
    """Return the ``m`` exact ratios needed for degree-``m`` recovery."""

    edge_tuple = tuple(edges)
    edge_count = len(edge_tuple)
    values = [
        exact_availability(
            node_count, edge_tuple, (trial_count,) * edge_count
        )
        for trial_count in range(1, edge_count + 2)
    ]
    if any(value <= 0 for value in values):
        raise ValueError(
            "the theorem requires positive uniform availability values"
        )
    return tuple(
        values[index + 1] / values[index]
        for index in range(edge_count)
    )


def one_edge_marginal_ratio(
    node_count: int,
    edges: Sequence[Edge],
    counts: Sequence[int],
    edge_index: int,
) -> Fraction:
    """Return ``F_G(n + e_i) / F_G(n)`` exactly."""

    edge_tuple = tuple(edges)
    count_tuple = tuple(counts)
    if not 0 <= edge_index < len(edge_tuple):
        raise IndexError("edge_index outside edge universe")
    before = exact_availability(node_count, edge_tuple, count_tuple)
    if before <= 0:
        raise ZeroDivisionError("marginal ratio has zero denominator")
    after_counts = list(count_tuple)
    after_counts[edge_index] += 1
    after = exact_availability(
        node_count, edge_tuple, tuple(after_counts)
    )
    return after / before


def telescoped_uniform_ratio(
    node_count: int,
    edges: Sequence[Edge],
    trial_count: int,
    marginal_oracle: MarginalOracle | None = None,
) -> Fraction:
    """Obtain one uniform-round ratio from ``m`` local increments."""

    edge_tuple = tuple(edges)
    if trial_count < 1:
        raise ValueError("trial_count must be positive")
    if marginal_oracle is None:
        marginal_oracle = lambda counts, index: one_edge_marginal_ratio(
            node_count, edge_tuple, counts, index
        )
    counts = [trial_count] * len(edge_tuple)
    result = Fraction(1)
    for edge_index in range(len(edge_tuple)):
        ratio = Fraction(marginal_oracle(tuple(counts), edge_index))
        if ratio <= 0:
            raise ValueError("marginal oracle must return a positive ratio")
        result *= ratio
        counts[edge_index] += 1
    return result


def availability_polynomial_from_marginal_oracle(
    node_count: int,
    edges: Sequence[Edge],
    marginal_oracle: MarginalOracle,
) -> Polynomial:
    """Reconstruct the full curve using exactly ``m**2`` oracle calls."""

    edge_tuple = tuple(edges)
    ratios = tuple(
        telescoped_uniform_ratio(
            node_count,
            edge_tuple,
            trial_count,
            marginal_oracle,
        )
        for trial_count in range(1, len(edge_tuple) + 1)
    )
    return availability_polynomial_from_uniform_ratios(ratios)


def floor_availability_from_polynomial(
    coefficients: Sequence[Fraction],
) -> Fraction:
    """Return ``P_G(1/2)`` from a reconstructed availability polynomial."""

    return polynomial_evaluate(coefficients, Fraction(1, 2))

