from run_verification import render_report


def test_report_preserves_scope_and_nonmonotonicity_warning() -> None:
    result = {
        "verdict": "ok",
        "gates": {"G0": True},
        "liveness": {
            "graph_count": 1,
            "cell_count": 1,
            "gauge_factor_mismatch_count": 0,
            "normalized_law_mismatch_count": 0,
            "rank_upper_mismatch_count": 0,
        },
        "power_calibration": {
            "cell_count": 1,
            "records": [{"exact_power": {"decimal": 0.8}}],
            "size_mismatch_count": 0,
            "formula_mismatch_count": 0,
        },
        "claim_boundary": "conditional only",
    }
    report = render_report(result)
    assert "calibration points, not monotone critical thresholds" in report
    assert "conditional only" in report
