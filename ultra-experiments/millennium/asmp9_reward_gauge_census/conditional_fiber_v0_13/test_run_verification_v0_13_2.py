from run_verification_v0_13_2 import render_report


def test_report_preserves_v0132_scope_and_warning() -> None:
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
            "exact_representation": "direct",
        },
        "claim_boundary": "conditional only",
    }
    report = render_report(result)
    assert "verification v0.13.2" in report
    assert "calibration points, not monotone critical thresholds" in report
    assert "conditional only" in report

