from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


Matrix = tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class CouplingQuotient:
    canonical_operator: Matrix
    coupling_columns: int
    coupling_dimension: int
    coupling_rows: int
    decision_rank: int
    gauge_dimension: int
    policy_difference_rank: int
    policy_analysis_rank: int
    semantic_rank: int


@dataclass(frozen=True)
class FactorizedProbeDesign:
    active_entrywise_coordinates: tuple[int, ...]
    cell_basis_indices: tuple[int, ...]
    canonical_row_indices: tuple[int, ...]
    policy_contrast_basis_indices: tuple[int, ...]
    probe_operator: Matrix
    raw_entrywise_query_count: int
    scalar_composite_query_count: int


def q(value: int | str | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def matrix(values: Sequence[Sequence]) -> Matrix:
    rows = tuple(tuple(q(value) for value in row) for row in values)
    if not rows or not rows[0]:
        raise ValueError("matrix must be nonempty")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("matrix must be rectangular")
    return rows


def zeros(rows: int, columns: int) -> Matrix:
    if rows <= 0 or columns <= 0:
        raise ValueError("matrix dimensions must be positive")
    return tuple(
        tuple(Fraction(0) for _ in range(columns)) for _ in range(rows)
    )


def transpose(values: Sequence[Sequence]) -> Matrix:
    source = matrix(values)
    return tuple(
        tuple(source[row][column] for row in range(len(source)))
        for column in range(len(source[0]))
    )


def matmul(left: Sequence[Sequence], right: Sequence[Sequence]) -> Matrix:
    a = matrix(left)
    b = matrix(right)
    if len(a[0]) != len(b):
        raise ValueError("matrix inner dimensions do not match")
    return tuple(
        tuple(
            sum(
                (
                    a[row][inner] * b[inner][column]
                    for inner in range(len(b))
                ),
                Fraction(0),
            )
            for column in range(len(b[0]))
        )
        for row in range(len(a))
    )


def column_vectorize(values: Sequence[Sequence]) -> tuple[Fraction, ...]:
    source = matrix(values)
    return tuple(
        source[row][column]
        for column in range(len(source[0]))
        for row in range(len(source))
    )


def matvec(
    values: Sequence[Sequence],
    vector: Sequence,
) -> tuple[Fraction, ...]:
    source = matrix(values)
    target = tuple(q(value) for value in vector)
    if len(source[0]) != len(target):
        raise ValueError("matrix and vector dimensions do not match")
    return tuple(
        sum(
            (
                source[row][column] * target[column]
                for column in range(len(target))
            ),
            Fraction(0),
        )
        for row in range(len(source))
    )


def subtract(left: Sequence[Sequence], right: Sequence[Sequence]) -> Matrix:
    a = matrix(left)
    b = matrix(right)
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        raise ValueError("matrix dimensions do not match")
    return tuple(
        tuple(x - y for x, y in zip(row_a, row_b, strict=True))
        for row_a, row_b in zip(a, b, strict=True)
    )


def rational_rank(values: Sequence[Sequence]) -> int:
    work = [list(row) for row in matrix(values)]
    row = 0
    for column in range(len(work[0])):
        pivot = next(
            (
                candidate
                for candidate in range(row, len(work))
                if work[candidate][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        scale = work[row][column]
        work[row] = [value / scale for value in work[row]]
        for candidate in range(len(work)):
            if candidate == row or not work[candidate][column]:
                continue
            factor = work[candidate][column]
            work[candidate] = [
                value - factor * pivot_value
                for value, pivot_value in zip(
                    work[candidate],
                    work[row],
                    strict=True,
                )
            ]
        row += 1
        if row == len(work):
            break
    return row


def inverse(values: Sequence[Sequence]) -> Matrix:
    source = matrix(values)
    dimension = len(source)
    if len(source[0]) != dimension:
        raise ValueError("inverse requires a square matrix")
    work = [
        [
            *source[row],
            *(
                Fraction(int(row == column))
                for column in range(dimension)
            ),
        ]
        for row in range(dimension)
    ]
    for column in range(dimension):
        pivot = next(
            (
                candidate
                for candidate in range(column, dimension)
                if work[candidate][column]
            ),
            None,
        )
        if pivot is None:
            raise ValueError("matrix is singular")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(dimension):
            if row == column or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(
                    work[row],
                    work[column],
                    strict=True,
                )
            ]
    return tuple(
        tuple(row[dimension:])
        for row in work
    )


def policy_difference_matrix(
    policies: Sequence[Sequence],
    reference: int = 0,
) -> Matrix:
    source = matrix(policies)
    if not 0 <= reference < len(source):
        raise IndexError("policy reference is out of range")
    baseline = source[reference]
    rows = tuple(
        tuple(value - base for value, base in zip(policy, baseline, strict=True))
        for index, policy in enumerate(source)
        if index != reference
    )
    if not rows:
        raise ValueError("at least two policies are required")
    return rows


def kronecker(left: Sequence[Sequence], right: Sequence[Sequence]) -> Matrix:
    a = matrix(left)
    b = matrix(right)
    return tuple(
        tuple(
            a_block * b_value
            for a_block in a_row
            for b_value in b_row
        )
        for a_row in a
        for b_row in b
    )


def decision_effect(
    analysis_map: Sequence[Sequence],
    policies: Sequence[Sequence],
    coupling: Sequence[Sequence],
    semantic_operator: Sequence[Sequence],
) -> Matrix:
    q_matrix = policy_difference_matrix(policies)
    return matmul(
        matmul(matmul(q_matrix, analysis_map), coupling),
        semantic_operator,
    )


def decision_equivalent_couplings(
    analysis_map: Sequence[Sequence],
    policies: Sequence[Sequence],
    first: Sequence[Sequence],
    second: Sequence[Sequence],
    semantic_operator: Sequence[Sequence],
) -> bool:
    delta = subtract(first, second)
    effect = decision_effect(
        analysis_map,
        policies,
        delta,
        semantic_operator,
    )
    return all(value == 0 for row in effect for value in row)


def coupling_quotient(
    analysis_map: Sequence[Sequence],
    policies: Sequence[Sequence],
    semantic_operator: Sequence[Sequence],
) -> CouplingQuotient:
    analysis = matrix(analysis_map)
    semantic = matrix(semantic_operator)
    policy_differences = policy_difference_matrix(policies)
    if len(analysis[0]) <= 0 or len(semantic) <= 0:
        raise ValueError("coupling dimensions must be positive")
    policy_analysis = matmul(policy_differences, analysis)
    canonical = kronecker(transpose(semantic), policy_analysis)
    coupling_rows = len(analysis[0])
    coupling_columns = len(semantic)
    coupling_dimension = coupling_rows * coupling_columns
    decision_rank = rational_rank(canonical)
    rank_product = rational_rank(semantic) * rational_rank(policy_analysis)
    if decision_rank != rank_product:
        raise RuntimeError("Kronecker rank identity failed")
    return CouplingQuotient(
        canonical_operator=canonical,
        coupling_columns=coupling_columns,
        coupling_dimension=coupling_dimension,
        coupling_rows=coupling_rows,
        decision_rank=decision_rank,
        gauge_dimension=coupling_dimension - decision_rank,
        policy_difference_rank=rational_rank(policy_differences),
        policy_analysis_rank=rational_rank(policy_analysis),
        semantic_rank=rational_rank(semantic),
    )


def nullspace_basis(values: Sequence[Sequence]) -> tuple[tuple[Fraction, ...], ...]:
    work = [list(row) for row in matrix(values)]
    pivot_columns: list[int] = []
    row = 0
    for column in range(len(work[0])):
        pivot = next(
            (
                candidate
                for candidate in range(row, len(work))
                if work[candidate][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        scale = work[row][column]
        work[row] = [value / scale for value in work[row]]
        for candidate in range(len(work)):
            if candidate == row or not work[candidate][column]:
                continue
            factor = work[candidate][column]
            work[candidate] = [
                value - factor * pivot_value
                for value, pivot_value in zip(
                    work[candidate],
                    work[row],
                    strict=True,
                )
            ]
        pivot_columns.append(column)
        row += 1
        if row == len(work):
            break
    free_columns = [
        column
        for column in range(len(work[0]))
        if column not in pivot_columns
    ]
    basis = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(len(work[0]))]
        vector[free] = 1
        for pivot_row, pivot_column in enumerate(pivot_columns):
            vector[pivot_column] = -work[pivot_row][free]
        basis.append(tuple(vector))
    return tuple(basis)


def outer(left: Sequence, right: Sequence) -> Matrix:
    left_values = tuple(q(value) for value in left)
    right_values = tuple(q(value) for value in right)
    if not left_values or not right_values:
        raise ValueError("outer-product vectors must be nonempty")
    return tuple(
        tuple(a * b for b in right_values) for a in left_values
    )


def independent_row_indices(values: Sequence[Sequence]) -> tuple[int, ...]:
    source = matrix(values)
    selected: list[int] = []
    current_rank = 0
    for index, row in enumerate(source):
        candidate = tuple(source[item] for item in (*selected, index))
        rank = rational_rank(candidate)
        if rank > current_rank:
            selected.append(index)
            current_rank = rank
    return tuple(selected)


def independent_column_indices(
    values: Sequence[Sequence],
) -> tuple[int, ...]:
    return independent_row_indices(transpose(values))


def select_rows(
    values: Sequence[Sequence],
    indices: Sequence[int],
) -> Matrix:
    source = matrix(values)
    selected = tuple(indices)
    if not selected:
        raise ValueError("at least one row must be selected")
    if len(set(selected)) != len(selected):
        raise ValueError("row indices must be unique")
    if any(index < 0 or index >= len(source) for index in selected):
        raise IndexError("row index is out of range")
    return tuple(source[index] for index in selected)


def select_columns(
    values: Sequence[Sequence],
    indices: Sequence[int],
) -> Matrix:
    source = matrix(values)
    selected = tuple(indices)
    if not selected:
        raise ValueError("at least one column must be selected")
    if len(set(selected)) != len(selected):
        raise ValueError("column indices must be unique")
    if any(index < 0 or index >= len(source[0]) for index in selected):
        raise IndexError("column index is out of range")
    return tuple(
        tuple(row[index] for index in selected)
        for row in source
    )


def stack_rows(*blocks: Sequence[Sequence]) -> Matrix:
    converted = tuple(matrix(block) for block in blocks)
    if not converted:
        raise ValueError("at least one matrix is required")
    width = len(converted[0][0])
    if any(len(block[0]) != width for block in converted):
        raise ValueError("stacked matrices must have equal column counts")
    return tuple(row for block in converted for row in block)


def factorized_probe_design(
    analysis_map: Sequence[Sequence],
    policies: Sequence[Sequence],
    semantic_operator: Sequence[Sequence],
) -> FactorizedProbeDesign:
    analysis = matrix(analysis_map)
    semantic = matrix(semantic_operator)
    policy_analysis = matmul(
        policy_difference_matrix(policies),
        analysis,
    )
    quotient = coupling_quotient(analysis, policies, semantic)
    policy_indices = independent_row_indices(policy_analysis)
    cell_indices = independent_column_indices(semantic)
    policy_basis = select_rows(policy_analysis, policy_indices)
    semantic_basis = select_columns(semantic, cell_indices)
    probe_operator = kronecker(transpose(semantic_basis), policy_basis)
    policy_count = len(policy_analysis)
    canonical_rows = tuple(
        cell * policy_count + policy
        for cell in cell_indices
        for policy in policy_indices
    )
    extracted = select_rows(quotient.canonical_operator, canonical_rows)
    if extracted != probe_operator:
        raise RuntimeError("factorized probes do not match canonical rows")
    if rational_rank(probe_operator) != quotient.decision_rank:
        raise RuntimeError("factorized probes do not attain decision rank")
    if rational_rank(
        stack_rows(probe_operator, quotient.canonical_operator)
    ) != quotient.decision_rank:
        raise RuntimeError("factorized probes do not span decision row space")
    active_coordinates = tuple(
        column
        for column in range(len(quotient.canonical_operator[0]))
        if any(
            row[column]
            for row in quotient.canonical_operator
        )
    )
    return FactorizedProbeDesign(
        active_entrywise_coordinates=active_coordinates,
        cell_basis_indices=cell_indices,
        canonical_row_indices=canonical_rows,
        policy_contrast_basis_indices=policy_indices,
        probe_operator=probe_operator,
        raw_entrywise_query_count=len(active_coordinates),
        scalar_composite_query_count=len(probe_operator),
    )
