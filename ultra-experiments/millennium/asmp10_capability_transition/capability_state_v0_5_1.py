"""Frozen-candidate hysteretic state machine for ASMP-10 v0.5.1.

This module is executable specification, not authorization to collect or join
outcomes.  Transition onset is recorded at the first sample in a dwell that is
later confirmed; state availability is recorded at the confirming sample.
"""

from __future__ import annotations

import math
from typing import Any


UP_ACCURACY = 0.90
UP_LOSS = 0.50
DOWN_ACCURACY = 0.80
DOWN_LOSS = 0.75
ENTRY_DWELL_STEPS = 500
EXIT_DWELL_STEPS = 100
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
            value = float(row[field])
            if not math.isfinite(value):
                raise ValueError(f"{field} must be finite")
        if previous is not None and step - previous != spacing_steps:
            raise ValueError("evaluation grid is not regular at the declared spacing")
        previous = step


def state_events(rows: list[dict[str, Any]], spacing_steps: int) -> list[dict[str, Any]]:
    validate_grid(rows, spacing_steps)
    up_count = dwell_count(ENTRY_DWELL_STEPS, spacing_steps)
    down_count = dwell_count(EXIT_DWELL_STEPS, spacing_steps)
    capable = False
    up_streak = 0
    down_streak = 0
    events: list[dict[str, Any]] = []

    for index, row in enumerate(rows):
        if not capable:
            up_streak = up_streak + 1 if up_qualified(row) else 0
            if up_streak >= up_count:
                onset_index = index - up_count + 1
                events.append(
                    {
                        "kind": "entry",
                        "onset_step": int(rows[onset_index]["step"]),
                        "confirmation_step": int(row["step"]),
                    }
                )
                capable = True
                up_streak = 0
                down_streak = 0
        else:
            down_streak = down_streak + 1 if down_qualified(row) else 0
            if down_streak >= down_count:
                onset_index = index - down_count + 1
                events.append(
                    {
                        "kind": "exit",
                        "onset_step": int(rows[onset_index]["step"]),
                        "confirmation_step": int(row["step"]),
                    }
                )
                capable = False
                up_streak = 0
                down_streak = 0
    return events


def classify(
    rows: list[dict[str, Any]], spacing_steps: int, memorization_step: int
) -> dict[str, Any]:
    events = state_events(rows, spacing_steps)
    stable_entry = None
    for index, event in enumerate(events):
        if event["kind"] != "entry":
            continue
        if not any(later["kind"] == "exit" for later in events[index + 1 :]):
            stable_entry = event
            break

    latest_adjudicable_onset = HORIZON_STEP - MINIMUM_TERMINAL_TAIL_STEPS
    if stable_entry is None or int(stable_entry["onset_step"]) > latest_adjudicable_onset:
        label = "no_adjudicable_horizon_stable_transition"
        delay = None
    else:
        delay = int(stable_entry["onset_step"]) - int(memorization_step)
        label = "delayed_horizon_stable" if delay >= MINIMUM_DELAY_STEPS else "early_horizon_stable"

    return {
        "spacing_steps": spacing_steps,
        "label": label,
        "events": events,
        "stable_entry_onset_step": stable_entry["onset_step"] if stable_entry else None,
        "stable_entry_confirmation_step": stable_entry["confirmation_step"] if stable_entry else None,
        "delay_steps": delay,
        "right_censored_late_entry": bool(
            stable_entry is not None and int(stable_entry["onset_step"]) > latest_adjudicable_onset
        ),
    }


def subsample(rows: list[dict[str, Any]], spacing_steps: int) -> list[dict[str, Any]]:
    result = [row for row in rows if int(row["step"]) % spacing_steps == 0]
    validate_grid(result, spacing_steps)
    return result


def cadence_replay(rows_25: list[dict[str, Any]], memorization_step: int) -> dict[str, Any]:
    results = {
        spacing: classify(subsample(rows_25, spacing), spacing, memorization_step)
        for spacing in (25, 50, 100)
    }
    labels = {result["label"] for result in results.values()}
    event_kinds = {tuple(event["kind"] for event in result["events"]) for result in results.values()}
    stable_steps = [
        int(result["stable_entry_onset_step"])
        for result in results.values()
        if result["stable_entry_onset_step"] is not None
    ]
    timing_agrees = not stable_steps or max(stable_steps) - min(stable_steps) <= 100
    valid = len(labels) == 1 and len(event_kinds) == 1 and timing_agrees
    return {
        "instrument_status": "valid" if valid else "cadence_dependent",
        "gate_decision": "continue" if valid else "not_evaluated",
        "results": {str(key): value for key, value in results.items()},
        "label_agreement": len(labels) == 1,
        "event_order_agreement": len(event_kinds) == 1,
        "stable_transition_timing_within_100_steps": timing_agrees,
    }

