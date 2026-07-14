from __future__ import annotations

import numpy as np
import pytest

from rsi_topology.risk_gate import (
    ControlRiskMeasurement,
    EdgeRiskReceipt,
    LoopRiskReceipt,
    control_risk_vector,
    predict_control_gate,
)
from rsi_topology.risk_redteam import _realized_chain, run_control_risk_redteam
from rsi_topology.risk_analysis import summarize_boundary_surface


def measurement(retention=1.0, angle=0.0, *, edges=1, det=False, measured=True):
    return ControlRiskMeasurement(
        measurement_id="test",
        edges=tuple(EdgeRiskReceipt(f"e{i}", retention) for i in range(edges)),
        loop=LoopRiskReceipt(None if det else angle, 0.0, det, measured),
    )


def test_holonomy_displacement_is_exact_for_rank_two_rotation():
    vector = control_risk_vector(measurement(angle=60.0))
    assert vector["holonomy_displacement_bound"] == pytest.approx(1.0)
    realized, _ = _realized_chain(np.ones(1), 60.0, False)
    assert np.linalg.norm(realized - np.eye(2), ord=2) == pytest.approx(1.0)


def test_cumulative_lineage_and_holonomy_bound_realized_loss():
    retention, angle, count = 0.88, 30.0, 4
    decision = predict_control_gate(measurement(retention, angle, edges=count), 2.0)
    realized, _ = _realized_chain(np.full(count, retention), angle, False)
    loss = np.linalg.norm(realized - np.eye(2), ord=2)
    assert loss <= decision["signed_control_loss_upper_bound"] + 1e-12


def test_equality_is_authorized_but_det_and_missing_measurement_are_not():
    item = measurement(angle=0.0)
    assert predict_control_gate(item, 0.0)["authorized"]
    assert not predict_control_gate(measurement(det=True), 2.0)["authorized"]
    assert not predict_control_gate(measurement(measured=False), 2.0)["authorized"]


def test_small_redteam_has_no_false_authorization_and_finds_baseline_blind_spots():
    result = run_control_risk_redteam(fixtures=90)
    assert result["metrics"]["false_authorization_rate"] == 0.0
    assert result["metrics"]["lineage_only_blind_spot_found"]
    assert result["metrics"]["holonomy_only_blind_spot_found"]


def test_boundary_summary_matches_analytic_thresholds():
    result = run_control_risk_redteam(fixtures=90)
    summary = summarize_boundary_surface(result)
    assert summary["false_authorizations"] == 0
    assert summary["analytic_pure_holonomy_boundary_degrees"] == pytest.approx(28.95502437185985)
    assert summary["analytic_pure_lineage_actual_retention_thresholds"]["4"] == pytest.approx(
        np.sqrt(0.5)
    )
