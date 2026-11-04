from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

try:
    from .semantic_coupling import (
        Matrix,
        independent_column_indices,
        independent_row_indices,
        inverse,
        matrix,
        matmul,
        matvec,
        nullspace_basis,
        rational_rank,
        select_columns,
        select_rows,
        stack_rows,
    )
except ImportError:
    from semantic_coupling import (  # type: ignore[no-redef]
        Matrix,
        independent_column_indices,
        independent_row_indices,
        inverse,
        matrix,
        matmul,
        matvec,
        nullspace_basis,
        rational_rank,
        select_columns,
        select_rows,
        stack_rows,
    )


@dataclass(frozen=True)
class QuerySpanCertificate:
    accessible_decision_dimensions: int
    decision_rank: int
    invisible_witness: tuple[Fraction, ...] | None
    missing_decision_dimensions: int
    query_rank: int
    reconstruction_operator: Matrix | None
    reconstruction_query_row_indices: tuple[int, ...] | None
    spans_decision_quotient: bool
    worst_case_linf_amplification: Fraction | None
    witness_decision_effect: tuple[Fraction, ...] | None
    witness_query_effect: tuple[Fraction, ...] | None


def row_reconstruction_operator(
    target_rows: Sequence[Sequence],
    independent_basis_rows: Sequence[Sequence],
) -> Matrix:
    target = matrix(target_rows)
    basis = matrix(independent_basis_rows)
    if len(target[0]) != len(basis[0]):
        raise ValueError("target and basis must share a parameter space")
    if rational_rank(basis) != len(basis):
        raise ValueError("basis rows must be linearly independent")
    pivot_columns = independent_column_indices(basis)
    square_basis = select_columns(basis, pivot_columns)
    target_pivots = select_columns(target, pivot_columns)
    reconstruction = matmul(target_pivots, inverse(square_basis))
    if matmul(reconstruction, basis) != target:
        raise ValueError("target rows are not in the declared basis span")
    return reconstruction


def linf_reconstruction_amplification(
    reconstruction_operator: Sequence[Sequence],
) -> Fraction:
    reconstruction = matrix(reconstruction_operator)
    return max(
        sum((abs(value) for value in row), Fraction(0))
        for row in reconstruction
    )


def query_span_certificate(
    canonical_decision_operator: Sequence[Sequence],
    query_operator: Sequence[Sequence],
) -> QuerySpanCertificate:
    decision = matrix(canonical_decision_operator)
    queries = matrix(query_operator)
    if len(decision[0]) != len(queries[0]):
        raise ValueError(
            "decision and query operators must share a parameter space"
        )
    decision_rank = rational_rank(decision)
    query_rank = rational_rank(queries)
    joint_rank = rational_rank(stack_rows(queries, decision))
    missing = joint_rank - query_rank
    accessible = decision_rank - missing
    if not 0 <= accessible <= decision_rank:
        raise RuntimeError("invalid decision-row-space intersection")
    if missing == 0:
        independent_queries = independent_row_indices(queries)
        query_basis = select_rows(queries, independent_queries)
        basis_reconstruction = row_reconstruction_operator(
            decision,
            query_basis,
        )
        reconstruction = tuple(
            tuple(
                (
                    basis_reconstruction[row][
                        independent_queries.index(column)
                    ]
                    if column in independent_queries
                    else Fraction(0)
                )
                for column in range(len(queries))
            )
            for row in range(len(decision))
        )
        amplification = linf_reconstruction_amplification(
            reconstruction
        )
        return QuerySpanCertificate(
            accessible_decision_dimensions=accessible,
            decision_rank=decision_rank,
            invisible_witness=None,
            missing_decision_dimensions=0,
            query_rank=query_rank,
            reconstruction_operator=reconstruction,
            reconstruction_query_row_indices=independent_queries,
            spans_decision_quotient=True,
            worst_case_linf_amplification=amplification,
            witness_decision_effect=None,
            witness_query_effect=None,
        )

    for witness in nullspace_basis(queries):
        query_effect = matvec(queries, witness)
        decision_effect = matvec(decision, witness)
        if any(decision_effect):
            if any(query_effect):
                raise RuntimeError("constructed witness is query-visible")
            return QuerySpanCertificate(
                accessible_decision_dimensions=accessible,
                decision_rank=decision_rank,
                invisible_witness=witness,
                missing_decision_dimensions=missing,
                query_rank=query_rank,
                reconstruction_operator=None,
                reconstruction_query_row_indices=None,
                spans_decision_quotient=False,
                worst_case_linf_amplification=None,
                witness_decision_effect=decision_effect,
                witness_query_effect=query_effect,
            )
    raise RuntimeError(
        "row-space test found a gap but no invisible witness"
    )


def identity_rows(
    dimension: int,
    retained_indices: Sequence[int] | None = None,
) -> Matrix:
    if dimension <= 0:
        raise ValueError("dimension must be positive")
    retained = (
        tuple(range(dimension))
        if retained_indices is None
        else tuple(retained_indices)
    )
    if not retained:
        raise ValueError("at least one identity row is required")
    if len(set(retained)) != len(retained):
        raise ValueError("identity row indices must be unique")
    if any(index < 0 or index >= dimension for index in retained):
        raise IndexError("identity row index is out of range")
    return tuple(
        tuple(
            Fraction(int(column == row))
            for column in range(dimension)
        )
        for row in retained
    )
