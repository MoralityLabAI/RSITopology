from __future__ import annotations

from .asmp9_native_fixture import load_native_sources
from .query_span import identity_rows, query_span_certificate
from .semantic_coupling import (
    coupling_quotient,
    factorized_probe_design,
    matmul,
)


def actual_operators():
    sources = load_native_sources()
    quotient = coupling_quotient(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    probes = factorized_probe_design(
        sources.v031_analysis_map,
        sources.v031_policies,
        sources.v032_semantic_operator,
    )
    return quotient.canonical_operator, probes.probe_operator


def assert_valid_failure(certificate) -> None:
    assert not certificate.spans_decision_quotient
    assert certificate.missing_decision_dimensions > 0
    assert certificate.invisible_witness is not None
    assert certificate.witness_query_effect is not None
    assert not any(certificate.witness_query_effect)
    assert certificate.witness_decision_effect is not None
    assert any(certificate.witness_decision_effect)


def test_factorized_probe_grammar_spans_exactly() -> None:
    canonical, probes = actual_operators()
    certificate = query_span_certificate(canonical, probes)
    assert certificate.spans_decision_quotient
    assert certificate.query_rank == 18
    assert certificate.decision_rank == 18
    assert certificate.accessible_decision_dimensions == 18
    assert certificate.missing_decision_dimensions == 0
    assert certificate.invisible_witness is None
    assert certificate.reconstruction_operator is not None
    assert matmul(certificate.reconstruction_operator, probes) == canonical
    assert certificate.reconstruction_query_row_indices == tuple(range(18))
    assert certificate.worst_case_linf_amplification is not None


def test_every_leave_one_out_factorized_grammar_fails_closed() -> None:
    canonical, probes = actual_operators()
    for omitted in range(len(probes)):
        reduced = tuple(
            row for index, row in enumerate(probes) if index != omitted
        )
        certificate = query_span_certificate(canonical, reduced)
        assert certificate.query_rank == 17
        assert certificate.accessible_decision_dimensions == 17
        assert certificate.missing_decision_dimensions == 1
        assert_valid_failure(certificate)


def test_entrywise_47_of_48_fails_for_every_omitted_coordinate() -> None:
    canonical, _ = actual_operators()
    for omitted in range(48):
        retained = tuple(index for index in range(48) if index != omitted)
        certificate = query_span_certificate(
            canonical,
            identity_rows(48, retained),
        )
        assert certificate.query_rank == 47
        assert certificate.accessible_decision_dimensions == 17
        assert certificate.missing_decision_dimensions == 1
        assert_valid_failure(certificate)


def test_six_diagonalized_composite_probes_leave_twelve_dimensions() -> None:
    canonical, probes = actual_operators()
    diagonal = tuple(probes[index] for index in (0, 4, 8, 9, 13, 17))
    certificate = query_span_certificate(canonical, diagonal)
    assert certificate.query_rank == 6
    assert certificate.accessible_decision_dimensions == 6
    assert certificate.missing_decision_dimensions == 12
    assert_valid_failure(certificate)
