"""Exact rational certificate for the smallest v0.12 conditioning witness."""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence


Matrix = tuple[tuple[Fraction, ...], ...]
Vector = tuple[Fraction, ...]


def _fraction_matrix(matrix: Sequence[Sequence[object]]) -> Matrix:
    rows = tuple(tuple(Fraction(value) for value in row) for row in matrix)
    if rows and any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("ragged matrix")
    return rows


def rank(matrix: Sequence[Sequence[object]]) -> int:
    rows = [list(row) for row in _fraction_matrix(matrix)]
    if not rows:
        return 0
    row_count = len(rows)
    column_count = len(rows[0])
    pivot_row = 0
    for column in range(column_count):
        selected = next(
            (
                row
                for row in range(pivot_row, row_count)
                if rows[row][column] != 0
            ),
            None,
        )
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        pivot = rows[pivot_row][column]
        rows[pivot_row] = [value / pivot for value in rows[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or rows[row][column] == 0:
                continue
            factor = rows[row][column]
            rows[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(rows[row], rows[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def pivot_columns(matrix: Sequence[Sequence[object]]) -> tuple[int, ...]:
    original = _fraction_matrix(matrix)
    if not original:
        return ()
    rows = [list(row) for row in original]
    row_count = len(rows)
    column_count = len(rows[0])
    pivot_row = 0
    pivots = []
    for column in range(column_count):
        selected = next(
            (
                row
                for row in range(pivot_row, row_count)
                if rows[row][column] != 0
            ),
            None,
        )
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        pivot = rows[pivot_row][column]
        rows[pivot_row] = [value / pivot for value in rows[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or rows[row][column] == 0:
                continue
            factor = rows[row][column]
            rows[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(rows[row], rows[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    return tuple(pivots)


def transpose(matrix: Matrix) -> Matrix:
    if not matrix:
        return ()
    return tuple(tuple(row[column] for row in matrix) for column in range(len(matrix[0])))


def matmul(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right:
        return ()
    if len(left[0]) != len(right):
        raise ValueError("incompatible matrix dimensions")
    right_t = transpose(right)
    return tuple(
        tuple(sum(a * b for a, b in zip(row, column)) for column in right_t)
        for row in left
    )


def inverse(matrix: Matrix) -> Matrix:
    matrix = _fraction_matrix(matrix)
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("inverse requires a square matrix")
    augmented = [
        list(row)
        + [Fraction(int(row_index == column)) for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for column in range(size):
        selected = next(
            (
                row
                for row in range(column, size)
                if augmented[row][column] != 0
            ),
            None,
        )
        if selected is None:
            raise ValueError("singular matrix")
        augmented[column], augmented[selected] = (
            augmented[selected],
            augmented[column],
        )
        pivot = augmented[column][column]
        augmented[column] = [value / pivot for value in augmented[column]]
        for row in range(size):
            if row == column or augmented[row][column] == 0:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(
                    augmented[row], augmented[column]
                )
            ]
    return tuple(tuple(row[size:]) for row in augmented)


def column_basis(matrix: Sequence[Sequence[object]]) -> Matrix:
    source = _fraction_matrix(matrix)
    if not source:
        return ()
    columns = pivot_columns(source)
    return tuple(tuple(row[column] for column in columns) for row in source)


def projector(matrix: Sequence[Sequence[object]]) -> Matrix:
    source = _fraction_matrix(matrix)
    row_count = len(source)
    basis = column_basis(source)
    if not basis or not basis[0]:
        return tuple(
            tuple(Fraction(0) for _ in range(row_count))
            for _ in range(row_count)
        )
    basis_t = transpose(basis)
    gram_inverse = inverse(matmul(basis_t, basis))
    return matmul(matmul(basis, gram_inverse), basis_t)


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return tuple(
        tuple(a - b for a, b in zip(left_row, right_row))
        for left_row, right_row in zip(left, right)
    )


def quadratic(left: Vector, matrix: Matrix, right: Vector) -> Fraction:
    return sum(
        left[row] * matrix[row][column] * right[column]
        for row in range(len(left))
        for column in range(len(right))
    )


def smallest_conditioning_witness() -> dict[str, object]:
    # Labelled edges:
    #   context 0: (0,3), (1,2)
    #   context 1: (0,1), (0,2), (1,3), (2,3)
    shared = _fraction_matrix(
        (
            (-1, 0, 0, 1),
            (0, -1, 1, 0),
            (-1, 1, 0, 0),
            (-1, 0, 1, 0),
            (0, -1, 0, 1),
            (0, 0, -1, 1),
        )
    )
    local = _fraction_matrix(
        (
            (-1, 0, 0, 1, 0, 0, 0, 0),
            (0, -1, 1, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, -1, 1, 0, 0),
            (0, 0, 0, 0, -1, 0, 1, 0),
            (0, 0, 0, 0, 0, -1, 0, 1),
            (0, 0, 0, 0, 0, 0, -1, 1),
        )
    )
    p_quotient = subtract(projector(local), projector(shared))
    short = (
        tuple(map(Fraction, (1, 0, -1, 0, -1, 0))),
        tuple(map(Fraction, (0, 1, 0, 0, -1, 1))),
    )
    robust = (
        tuple(map(Fraction, (1, -1, -1, 0, 0, -1))),
        tuple(map(Fraction, (1, 1, 0, -1, -1, 0))),
    )

    def normalized_gram(vectors: Sequence[Vector]) -> Matrix:
        norms_squared = [
            sum(value * value for value in vector) for vector in vectors
        ]
        raw = tuple(
            tuple(quadratic(left, p_quotient, right) for right in vectors)
            for left in vectors
        )
        # Both registered designs use equal-length rows, so all square-root
        # normalization factors are rational and identical within a design.
        if len(set(norms_squared)) != 1:
            raise AssertionError("certificate expects equal row norms")
        norm_squared = norms_squared[0]
        return tuple(
            tuple(value / norm_squared for value in row) for row in raw
        )

    short_gram = normalized_gram(short)
    robust_gram = normalized_gram(robust)
    return {
        "item_count": 4,
        "context_count": 2,
        "edge_count": 6,
        "local_rank": rank(local),
        "shared_rank": rank(shared),
        "obstruction_dimension": rank(local) - rank(shared),
        "short_total_support": 6,
        "short_normalized_gram": tuple(
            tuple(str(value) for value in row) for row in short_gram
        ),
        "short_sigma_min_squared": str(short_gram[0][0]),
        "short_amplification_squared": str(1 / short_gram[0][0]),
        "robust_total_support": 8,
        "robust_normalized_gram": tuple(
            tuple(str(value) for value in row) for row in robust_gram
        ),
        "robust_sigma_min_squared": str(robust_gram[0][0]),
        "robust_amplification_squared": str(1 / robust_gram[0][0]),
    }
