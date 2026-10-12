from __future__ import annotations

import json
from pathlib import Path

import train_liveness_pilot_v0_4 as pilot


HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "pilot_liveness_config_v0_4.json").read_text(encoding="utf-8"))


def test_factorial_is_exact_and_caps_are_not_loosened() -> None:
    cells = {(row["train_fraction"], row["weight_decay"]) for row in CONFIG["runs"]}
    assert cells == {(fraction, decay) for fraction in (0.4, 0.55, 0.7) for decay in (1.0, 2.0)}
    assert len({row["run_id"] for row in CONFIG["runs"]}) == 6
    assert CONFIG["resource_intent"]["memory_mb"] == 2048
    assert CONFIG["resource_intent"]["gpu_allowance_mb"] == 3072
    assert CONFIG["resource_intent"]["allocator_hard_cap_mb"] == 2048
    assert CONFIG["resource_intent"]["swap_bytes"] == 0


def test_sustained_step_uses_start_of_first_complete_streak() -> None:
    metrics = [
        {"step": 100, "ok": True},
        {"step": 200, "ok": False},
        {"step": 300, "ok": True},
        {"step": 400, "ok": True},
        {"step": 500, "ok": True},
    ]
    assert pilot.first_sustained_step(
        metrics, predicate=lambda row: row["ok"], consecutive=3
    ) == 300


def test_delayed_transition_classifier_separates_early_generalization() -> None:
    metrics = [
        {"step": step, "train_accuracy": 1.0}
        for step in (100, 200, 300, 400, 500)
    ]
    result = {"transition_step": 900}
    classified = pilot.classify_cell(result, metrics, CONFIG)
    assert classified["memorization_step"] == 100
    assert classified["delay_steps"] == 800
    assert classified["delayed_transition_candidate"] is True
    early = pilot.classify_cell({"transition_step": 500}, metrics, CONFIG)
    assert early["delayed_transition_candidate"] is False


def test_allocator_cap_cannot_exceed_registered_allowance() -> None:
    assert (
        CONFIG["resource_intent"]["allocator_hard_cap_mb"]
        <= CONFIG["resource_intent"]["gpu_allowance_mb"]
    )
