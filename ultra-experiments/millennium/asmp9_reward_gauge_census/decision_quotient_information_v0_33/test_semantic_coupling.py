from __future__ import annotations

from fractions import Fraction

from .asmp9_native_fixture import load_native_sources
from .semantic_coupling import (
    column_vectorize,
    coupling_quotient,
    decision_effect,
    decision_equivalent_couplings,
    independent_row_indices,
    matmul,
    matvec,
    nullspace_basis,
    outer,
    policy_difference_matrix,
    rational_rank,
    zeros,
)


def test_actual_coupling_quotient_has_rank_18_and_gauge_30() -> None:
    sources = load_native_sources()
    quotient = coupling_quotient(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    assert quotient.coupling_rows == 8
    assert quotient.coupling_columns == 6
    assert quotient.coupling_dimension == 48
    assert quotient.semantic_rank == 6
    assert quotient.policy_difference_rank == 3
    assert quotient.policy_analysis_rank == 3
    assert quotient.decision_rank == 18
    assert quotient.gauge_dimension == 30
    rows = independent_row_indices(quotient.canonical_operator)
    assert len(rows) == quotient.decision_rank
    assert rational_rank(
        tuple(quotient.canonical_operator[index] for index in rows)
    ) == 18


def test_actual_null_gauge_and_decision_changing_witnesses() -> None:
    sources = load_native_sources()
    q_matrix = policy_difference_matrix(sources.v031_policies)
    policy_analysis = matmul(q_matrix, sources.v031_analysis_map)
    null_vectors = nullspace_basis(policy_analysis)
    assert len(null_vectors) == 5
    null_coupling = outer(
        null_vectors[0],
        (Fraction(1), 0, 0, 0, 0, 0),
    )
    zero = zeros(8, 6)
    assert decision_equivalent_couplings(
        sources.v031_analysis_map,
        sources.v031_policies,
        null_coupling,
        zero,
        sources.v032_semantic_operator,
    )

    changing = None
    for row in range(8):
        for column in range(6):
            candidate = [
                [Fraction(0) for _ in range(6)] for _ in range(8)
            ]
            candidate[row][column] = 1
            effect = decision_effect(
                sources.v031_analysis_map,
                sources.v031_policies,
                candidate,
                sources.v032_semantic_operator,
            )
            if any(value for effect_row in effect for value in effect_row):
                changing = candidate
                break
        if changing is not None:
            break
    assert changing is not None
    assert not decision_equivalent_couplings(
        sources.v031_analysis_map,
        sources.v031_policies,
        changing,
        zero,
        sources.v032_semantic_operator,
    )


def test_canonical_kronecker_operator_matches_direct_composition() -> None:
    sources = load_native_sources()
    quotient = coupling_quotient(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    coupling = tuple(
        tuple(
            Fraction((row + 1) * (column + 2), 7)
            for column in range(6)
        )
        for row in range(8)
    )
    direct = decision_effect(
        sources.v031_analysis_map,
        sources.v031_policies,
        coupling,
        sources.v032_semantic_operator,
    )
    canonical = matvec(
        quotient.canonical_operator,
        column_vectorize(coupling),
    )
    assert canonical == column_vectorize(direct)


def test_policy_restriction_coarsens_coupling_quotient() -> None:
    sources = load_native_sources()
    restricted_policies = sources.v031_policies[:2]
    quotient = coupling_quotient(
        sources.v031_analysis_map,
        restricted_policies,
        sources.v032_semantic_operator,
    )
    assert quotient.policy_difference_rank == 1
    assert quotient.policy_analysis_rank == 1
    assert quotient.decision_rank == 6
    assert quotient.gauge_dimension == 42
