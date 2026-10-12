from __future__ import annotations

from .run_query_span_development import build_report


def test_query_span_report_is_total_and_fail_closed() -> None:
    report = build_report()
    robust = report["passing_grammars"]["minimum_linf_factorized"]
    assert robust["query_count"] == 18
    assert robust["query_rank"] == 18
    assert robust["spans"]
    assert robust["behavioral_cell_basis_indices"] == [0, 1, 2, 4, 5, 7]
    assert robust["worst_case_linf_amplification"] == "8"

    failures = report["failing_controls"]
    assert failures["factorized_leave_one_out"]["failures"] == 18
    assert failures["entrywise_leave_one_out"]["failures"] == 48
    assert failures["six_diagonal_composites"][
        "missing_decision_dimensions"
    ] == 12
    for name in ("factorized_leave_one_out", "entrywise_leave_one_out"):
        witness = failures[name]["representative"]
        assert witness["query_effect_is_zero"]
        assert witness["decision_effect_nonzero_entries"]
    assert not any(report["claim_boundary"].values())
