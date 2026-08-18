from __future__ import annotations

from fractions import Fraction

from .asmp9_native_fixture import load_native_sources
from .query_span import query_span_certificate
from .robust_probe_design import minimum_linf_factorized_probe_design
from .semantic_coupling import (
    coupling_quotient,
    factorized_probe_design,
)


def test_exact_basis_search_reduces_amplification_from_twelve_to_eight() -> None:
    sources = load_native_sources()
    quotient = coupling_quotient(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    greedy = factorized_probe_design(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    greedy_certificate = query_span_certificate(
        quotient.canonical_operator,
        greedy.probe_operator,
    )
    robust = minimum_linf_factorized_probe_design(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    robust_certificate = query_span_certificate(
        quotient.canonical_operator,
        robust.probe_operator,
    )

    assert greedy_certificate.worst_case_linf_amplification == 12
    assert robust.policy_basis_candidates == 10
    assert robust.cell_basis_candidates == 432
    assert robust.policy_contrast_basis_indices == (0, 1, 2)
    assert robust.cell_basis_indices == (0, 1, 2, 4, 5, 7)
    assert robust.policy_amplification == 2
    assert robust.cell_amplification == 4
    assert robust.combined_amplification == 8
    assert robust_certificate.spans_decision_quotient
    assert robust_certificate.worst_case_linf_amplification == Fraction(8)
