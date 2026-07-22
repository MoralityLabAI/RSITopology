"""Executable specification for the ASMP-10 v0.5.2 endpoint.

The module contains no model training and does not authorize outcome joining.
"""

from __future__ import annotations

import math
from typing import Any


UP_ACCURACY = 0.90
UP_LOSS = 0.50
DOWN_ACCURACY = 0.80
DOWN_LOSS = 0.75
ENTRY_DWELL_STEPS = 500
PRIMARY_EXIT_DWELL_STEPS = 300
EXIT_DWELL_SENSITIVITY = (250, 300, 400)
HORIZON_STEP = 15_000
MINIMUM_TERMINAL_TAIL_STEPS = 500
MINIMUM_DELAY_STEPS = 500


def dwell_count(span_steps: int, spacing_steps: int) -> int:
    if span_steps < 0 or spacing_steps <= 0 or span_steps % spacing_steps:
        raise ValueError("dwell span must be a nonnegative multiple of spacing")
    return span_steps // spacing_steps + 1


def up_qualified(row: dict[str, Any]) -> bool:
    return float(row["test_accuracy"]) >= UP_ACCURACY and float(row["test_loss"]) <= UP_LOSS


def down_qualified(row: dict[str, Any]) -> bool:
    return float(row["test_accuracy"]) < DOWN_ACCURACY or float(row["test_loss"]) > DOWN_LOSS


def validate_grid(rows: list[dict[str, Any]], spacing_steps: int) -> None:
    if not rows:
        raise ValueError("evaluation grid is empty")
    previous = None
    for row in rows:
        step = int(row["step"])
        for field in ("test_accuracy", "test_loss"):
            if not math.isfinite(float(row[field])):
                raise ValueError(f"{field} must be finite")
        if previous is not None and step - previous != spacing_steps:
            raise ValueError("evaluation grid is not regular at the declared spacing")
        previous = step


def state_events(
    rows: list[dict[str, Any]],
    spacing_steps: int,
    exit_dwell_steps: int = PRIMARY_EXIT_DWELL_STEPS,
) -> list[dict[str, Any]]:
    validate_grid(rows, spacing_steps)
    up_count = dwell_count(ENTRY_DWELL_STEPS, spacing_steps)
    down_count = dwell_count(exit_dwell_steps, spacing_steps)
    capable = False
    up_streak = 0
    down_streak = 0
    events: list[dict[str, Any]] = []

    for index, row in enumerate(rows):
        if not capable:
            up_streak = up_streak + 1 if up_qualified(row) else 0
            if up_streak >= up_count:
                onset = index - up_count + 1
                events.append(
                    {
                        "kind": "entry",
                        "onset_step": int(rows[onset]["step"]),
                        "confirmation_step": int(row["step"]),
                    }
                )
                capable = True
                up_streak = 0
                down_streak = 0
        else:
            down_streak = down_streak + 1 if down_qualified(row) else 0
            if down_streak >= down_count:
                onset = index - down_count + 1
                events.append(
                    {
                        "kind": "exit",
                        "onset_step": int(rows[onset]["step"]),
                        "confirmation_step": int(row["step"]),
                    }
                )
                capable = False
                up_streak = 0
                down_streak = 0
    return events


def classify(
    rows: list[dict[str, Any]],
    spacing_steps: int,
    memorization_step: int,
    exit_dwell_steps: int = PRIMARY_EXIT_DWELL_STEPS,
) -> dict[str, Any]:
    events = state_events(rows, spacing_steps, exit_dwell_steps)
    stable_entry = None
    for index, event in enumerate(events):
        if event["kind"] == "entry" and not any(
            later["kind"] == "exit" for later in events[index + 1 :]
        ):
            stable_entry = event
            break

    latest_onset = HORIZON_STEP - MINIMUM_TERMINAL_TAIL_STEPS
    if stable_entry is None or int(stable_entry["onset_step"]) > latest_onset:
        label = "no_adjudicable_horizon_stable_transition"
        delay = None
    else:
        delay = int(stable_entry["onset_step"]) - int(memorization_step)
        label = "delayed_horizon_stable" if delay >= MINIMUM_DELAY_STEPS else "early_horizon_stable"

    final_state = "capable" if events and events[-1]["kind"] == "entry" else "incapable"
    return {
        "spacing_steps": spacing_steps,
        "exit_dwell_steps": exit_dwell_steps,
        "label": label,
        "events": events,
        "event_kind_order": [event["kind"] for event in events],
        "final_state": final_state,
        "stable_entry_onset_step": stable_entry["onset_step"] if stable_entry else None,
        "stable_entry_confirmation_step": stable_entry["confirmation_step"] if stable_entry else None,
        "delay_steps": delay,
        "right_censored_late_entry": bool(
            stable_entry is not None and int(stable_entry["onset_step"]) > latest_onset
        ),
    }


def subsample(rows: list[dict[str, Any]], spacing_steps: int) -> list[dict[str, Any]]:
    selected = [row for row in rows if int(row["step"]) % spacing_steps == 0]
    validate_grid(selected, spacing_steps)
    return selected


def cadence_replay(rows_25: list[dict[str, Any]], memorization_step: int) -> dict[str, Any]:
    results = {
        spacing: classify(
            subsample(rows_25, spacing),
            spacing,
            memorization_step,
            PRIMARY_EXIT_DWELL_STEPS,
        )
        for spacing in (25, 50, 100)
    }
    labels = {result["label"] for result in results.values()}
    orders = {tuple(result["event_kind_order"]) for result in results.values()}
    stable_steps = [
        int(result["stable_entry_onset_step"])
        for result in results.values()
        if result["stable_entry_onset_step"] is not None
    ]
    timing_agrees = not stable_steps or max(stable_steps) - min(stable_steps) <= 100
    valid = len(labels) == 1 and len(orders) == 1 and timing_agrees
    return {
        "instrument_status": "valid" if valid else "cadence_dependent",
        "gate_decision": "continue" if valid else "not_evaluated",
        "label_agreement": len(labels) == 1,
        "event_order_agreement": len(orders) == 1,
        "stable_transition_timing_within_100_steps": timing_agrees,
        "results": {str(key): value for key, value in results.items()},
    }


def dwell_replay(rows_25: list[dict[str, Any]], memorization_step: int) -> dict[str, Any]:
    validate_grid(rows_25, 25)
    results = {
        dwell: classify(rows_25, 25, memorization_step, dwell)
        for dwell in EXIT_DWELL_SENSITIVITY
    }
    labels = {result["label"] for result in results.values()}
    orders = {tuple(result["event_kind_order"]) for result in results.values()}
    final_states = {result["final_state"] for result in results.values()}
    valid = len(labels) == 1 and len(orders) == 1 and len(final_states) == 1
    return {
        "instrument_status": "valid" if valid else "dwell_fragile",
        "gate_decision": "continue" if valid else "not_evaluated",
        "label_agreement": len(labels) == 1,
        "event_order_agreement": len(orders) == 1,
        "final_state_agreement": len(final_states) == 1,
        "results": {str(key): value for key, value in results.items()},
    }


def measurement_validity(rows_25: list[dict[str, Any]], memorization_step: int) -> dict[str, Any]:
    cadence = cadence_replay(rows_25, memorization_step)
    dwell = dwell_replay(rows_25, memorization_step)
    if cadence["instrument_status"] != "valid":
        status = "cadence_dependent"
    elif dwell["instrument_status"] != "valid":
        status = "dwell_fragile"
    else:
        status = "valid"
    return {
        "instrument_status": status,
        "gate_decision": "continue" if status == "valid" else "not_evaluated",
        "cadence": cadence,
        "dwell": dwell,
    }

