"""Coordinate-invariant risk tools for ASMP-9 v0.70.1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import sympy as sp


def rational_matrix(rows: Sequence[Sequence[object]]) -> sp.Matrix:
    return sp.Matrix([[sp.Rational(value) for value in row] for row in rows])


def information_from_rows(
    rows: sp.Matrix, allocation: Sequence[int]
) -> sp.Matrix:
    if rows.rows != len(allocation):
        raise ValueError("one allocation count is required per query row")
    information = sp.zeros(rows.cols, rows.cols)
    for index, count in enumerate(allocation):
        if int(count) != count or count < 0:
            raise ValueError("counts must be nonnegative integers")
        row = rows[index, :].T
        information += int(count) * row * row.T
    return information


def reframe_rows(rows: sp.Matrix, coordinate_map: sp.Matrix) -> sp.Matrix:
    """Transform rows under x_new = T x_old."""

    _check_coordinate_map(coordinate_map, rows.cols)
    return rows * coordinate_map.inv()


def reframe_information(
    information: sp.Matrix, coordinate_map: sp.Matrix
) -> sp.Matrix:
    _check_coordinate_map(coordinate_map, information.rows)
    inverse = coordinate_map.inv()
    return inverse.T * information * inverse


def reframe_loss_metric(
    loss_metric: sp.Matrix, coordinate_map: sp.Matrix
) -> sp.Matrix:
    _check_coordinate_map(coordinate_map, loss_metric.rows)
    inverse = coordinate_map.inv()
    return inverse.T * loss_metric * inverse


def reframe_functional(
    functional: sp.Matrix, coordinate_map: sp.Matrix
) -> sp.Matrix:
    _check_coordinate_map(coordinate_map, functional.rows)
    return coordinate_map.inv().T * functional


def _check_coordinate_map(coordinate_map: sp.Matrix, dimension: int) -> None:
    if coordinate_map.shape != (dimension, dimension):
        raise ValueError("coordinate map has incompatible shape")
    if coordinate_map.det() == 0:
        raise ValueError("coordinate map must be invertible")


def quadratic_risk(
    information: sp.Matrix, loss_metric: sp.Matrix
) -> sp.Expr:
    if information.shape != loss_metric.shape:
        raise ValueError("information and metric must have equal shape")
    if information.det() == 0:
        return sp.oo
    return sp.trace(loss_metric * information.inv())


def functional_risk(
    information: sp.Matrix, functional: sp.Matrix
) -> sp.Expr:
    if functional.shape != (information.rows, 1):
        raise ValueError("functional has incompatible shape")
    if information.det() == 0:
        return sp.oo
    return (functional.T * information.inv() * functional)[0]


@dataclass(frozen=True)
class MetricOptimum:
    risk: sp.Expr
    allocations: tuple[tuple[int, ...], ...]


def weak_compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in weak_compositions(total - first, parts - 1):
            yield (first,) + rest


def exact_metric_optimum(
    rows: sp.Matrix, total: int, loss_metric: sp.Matrix
) -> MetricOptimum:
    best: sp.Expr | None = None
    winners: list[tuple[int, ...]] = []
    for allocation in weak_compositions(total, rows.rows):
        information = information_from_rows(rows, allocation)
        if information.det() == 0:
            continue
        risk = quadratic_risk(information, loss_metric)
        if best is None or risk < best:
            best = risk
            winners = [allocation]
        elif risk == best:
            winners.append(allocation)
    if best is None:
        return MetricOptimum(sp.oo, tuple())
    return MetricOptimum(best, tuple(winners))


def canonical_fixture() -> tuple[sp.Matrix, sp.Matrix]:
    rows = rational_matrix([[1, 0], [0, 1], [1, 1]])
    information = information_from_rows(rows, (5, 5, 2))
    return rows, information
