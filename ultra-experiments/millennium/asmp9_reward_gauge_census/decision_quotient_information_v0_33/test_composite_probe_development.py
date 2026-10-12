from __future__ import annotations

from .run_composite_probe_development import build_report


def test_composite_probe_report_is_exact_and_conservatively_scoped() -> None:
    report = build_report()
    grammar = report["candidate_composite_probe_grammar"]
    access = report["access_comparison"]
    assert grammar["policy_contrast_basis_indices"] == [0, 1, 2]
    assert grammar["behavioral_cell_basis_indices"] == [0, 1, 2, 4, 5, 6]
    assert grammar["probe_operator_rank"] == 18
    assert len(grammar["probes"]) == 18
    assert access["minimum_entrywise_queries"] == 48
    assert access["minimum_factorized_composite_queries"] == 18
    assert access["entrywise_to_composite_ratio"] == "8/3"
    assert report["decision_claim"] == {
        "composite_rows_span_full_decision_quotient": True,
        "decision_quotient_dimension": 18,
    }
    assert not any(report["claim_boundary"].values())
