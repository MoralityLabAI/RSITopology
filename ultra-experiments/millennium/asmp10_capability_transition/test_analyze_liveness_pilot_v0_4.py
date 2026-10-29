from __future__ import annotations

import analyze_liveness_pilot_v0_4 as analysis


def test_terminal_stability_requires_registered_tail_length() -> None:
    metrics = [{"step": step, "ok": ok} for step, ok in enumerate([False, True, True, True], 1)]
    assert analysis.terminal_stable_step(metrics, lambda row: row["ok"], 3) == 2
    assert analysis.terminal_stable_step(metrics, lambda row: row["ok"], 4) is None


def test_first_sustained_step_is_not_terminal_stability() -> None:
    metrics = [
        {"step": 100, "ok": True},
        {"step": 200, "ok": True},
        {"step": 300, "ok": False},
        {"step": 400, "ok": True},
        {"step": 500, "ok": True}
    ]
    assert analysis.first_sustained_step(metrics, lambda row: row["ok"], 2) == 100
    assert analysis.terminal_stable_step(metrics, lambda row: row["ok"], 2) == 400
