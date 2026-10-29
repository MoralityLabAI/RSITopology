from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = (
    ROOT
    / "ultra-experiments"
    / "millennium"
    / "asmp9_reward_gauge_census"
    / "physical_acquisition_v0_34"
)


def test_published_prime_analysis_matches_reported_measurement_boundary() -> None:
    analysis = json.loads(
        (EXPERIMENT / "BURNED_PILOT_ANALYSIS_v0_34_4.json").read_text(
            encoding="utf-8"
        )
    )
    assert analysis["status"] == "burned_pilot_analyzed_not_confirmation"
    assert analysis["counts"] == {
        "cell_family_curves": 36,
        "cell_family_curves_bracketed": 10,
        "compound_family_curves": 18,
        "compound_family_curves_bracketed": 10,
        "mixture_residuals_available": 0,
        "monotonicity_violations": 67,
        "records": 1944,
    }
    assert analysis["repeatability"]["cold_start_log_odds_delta"]["maximum"] == 0
    assert (
        analysis["repeatability"]["absolute_option_order_bias"]["q95"]
        == 0.8141393590561858
    )
    assert analysis["mixture_affinity"]["status"] == (
        "unavailable_no_jointly_bracketed_mixtures"
    )


def test_closeout_hashes_match_committed_analysis_artifacts() -> None:
    closeout = json.loads(
        (EXPERIMENT / "PRIME_CLOSEOUT_v0_34_4.json").read_text(encoding="utf-8")
    )
    for name, expected in closeout["analysis"]["files"].items():
        if name == "analysis_wrapper_summary.json":
            continue
        actual = hashlib.sha256((EXPERIMENT / name).read_bytes()).hexdigest()
        assert actual == expected
    assert closeout["account_closeout"]["active_pod_count"] == 0
    assert closeout["pod"]["final_status"] == "terminated"
