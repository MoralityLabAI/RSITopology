from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Sequence

try:
    from .query_span import (
        linf_reconstruction_amplification,
        query_span_certificate,
        row_reconstruction_operator,
    )
    from .semantic_coupling import (
        Matrix,
        coupling_quotient,
        kronecker,
        matmul,
        matrix,
        policy_difference_matrix,
        rational_rank,
        select_columns,
        select_rows,
        transpose,
    )
except ImportError:
    from query_span import (  # type: ignore[no-redef]
        linf_reconstruction_amplification,
        query_span_certificate,
        row_reconstruction_operator,
    )
    from semantic_coupling import (  # type: ignore[no-redef]
        Matrix,
        coupling_quotient,
        kronecker,
        matmul,
        matrix,
        policy_difference_matrix,
        rational_rank,
        select_columns,
        select_rows,
        transpose,
    )


@dataclass(frozen=True)
class RobustFactorizedProbeDesign:
    cell_amplification: Fraction
    cell_basis_candidates: int
    cell_basis_indices: tuple[int, ...]
    combined_amplification: Fraction
    policy_amplification: Fraction
    policy_basis_candidates: int
    policy_contrast_basis_indices: tuple[int, ...]
    probe_operator: Matrix


def minimum_linf_factorized_probe_design(
    analysis_map: Sequence[Sequence],
    policies: Sequence[Sequence],
    semantic_operator: Sequence[Sequence],
) -> RobustFactorizedProbeDesign:
    analysis = matrix(analysis_map)
    semantic = matrix(semantic_operator)
    policy_analysis = matmul(
        policy_difference_matrix(policies),
        analysis,
    )
    policy_rank = rational_rank(policy_analysis)
    semantic_rank = rational_rank(semantic)

    policy_candidates: list[
        tuple[Fraction, tuple[int, ...], Matrix]
    ] = []
    for indices in combinations(range(len(policy_analysis)), policy_rank):
        basis = select_rows(policy_analysis, indices)
        if rational_rank(basis) != policy_rank:
            continue
        reconstruction = row_reconstruction_operator(
            policy_analysis,
            basis,
        )
        policy_candidates.append(
            (
                linf_reconstruction_amplification(reconstruction),
                indices,
                basis,
            )
        )
    if not policy_candidates:
        raise RuntimeError("no policy-contrast row basis exists")
    policy_amplification, policy_indices, policy_basis = min(
        policy_candidates,
        key=lambda candidate: (candidate[0], candidate[1]),
    )

    semantic_target = transpose(semantic)
    cell_candidates: list[
        tuple[Fraction, tuple[int, ...], Matrix]
    ] = []
    for indices in combinations(range(len(semantic[0])), semantic_rank):
        basis = transpose(select_columns(semantic, indices))
        if rational_rank(basis) != semantic_rank:
            continue
        reconstruction = row_reconstruction_operator(
            semantic_target,
            basis,
        )
        cell_candidates.append(
            (
                linf_reconstruction_amplification(reconstruction),
                indices,
                basis,
            )
        )
    if not cell_candidates:
        raise RuntimeError("no behavioral-cell column basis exists")
    cell_amplification, cell_indices, cell_basis = min(
        cell_candidates,
        key=lambda candidate: (candidate[0], candidate[1]),
    )

    probe_operator = kronecker(cell_basis, policy_basis)
    quotient = coupling_quotient(analysis, policies, semantic)
    certificate = query_span_certificate(
        quotient.canonical_operator,
        probe_operator,
    )
    expected_amplification = (
        policy_amplification * cell_amplification
    )
    if not certificate.spans_decision_quotient:
        raise RuntimeError("optimized probe basis does not span quotient")
    if certificate.worst_case_linf_amplification != expected_amplification:
        raise RuntimeError("Kronecker amplification identity failed")

    return RobustFactorizedProbeDesign(
        cell_amplification=cell_amplification,
        cell_basis_candidates=len(cell_candidates),
        cell_basis_indices=cell_indices,
        combined_amplification=expected_amplification,
        policy_amplification=policy_amplification,
        policy_basis_candidates=len(policy_candidates),
        policy_contrast_basis_indices=policy_indices,
        probe_operator=probe_operator,
    )
