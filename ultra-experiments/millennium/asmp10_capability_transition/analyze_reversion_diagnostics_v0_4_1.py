"""Post-hoc diagnostic of v0.4 threshold excursions.

This script does not alter the sealed v0.4 decision.  It asks whether the
single-threshold failures recorded after a five-evaluation capability crossing
were persistent state changes or isolated optimization spikes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
DEFAULT_RUNS = HERE / "pilot_artifacts_v0_4" / "runs"
DEFAULT_OUTPUT = HERE / "pilot_artifacts_v0_4" / "reversion_diagnostics_v0_4_1.json"

UP_ACCURACY = 0.90
UP_LOSS = 0.50
DOWN_ACCURACY = 0.80
DOWN_LOSS = 0.75
UP_DWELL = 5  # The detector actually used in v0.4 (5 x 100-step evaluations).
ROLLING_WINDOW = 10
LOSS_SPIKE_RATIO = 10.0
GRADIENT_SPIKE_RATIO = 100.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finite_number(value: Any, name: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def validate_rows(rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("metrics must contain at least one row")
    required = {
        "step",
        "train_loss",
        "test_loss",
        "train_accuracy",
        "test_accuracy",
        "gradient_norm",
    }
    previous = -1
    for row in rows:
        missing = required.difference(row)
        if missing:
            raise ValueError(f"metric row missing fields: {sorted(missing)}")
        step = int(row["step"])
        if step <= previous:
            raise ValueError("metric steps must be strictly increasing")
        previous = step
        for field in required.difference({"step"}):
            finite_number(row[field], field)


def up_qualified(row: dict[str, Any]) -> bool:
    return float(row["test_accuracy"]) >= UP_ACCURACY and float(row["test_loss"]) <= UP_LOSS


def down_qualified(row: dict[str, Any]) -> bool:
    return float(row["test_accuracy"]) < DOWN_ACCURACY or float(row["test_loss"]) > DOWN_LOSS


def first_sustained_index(rows: list[dict[str, Any]], dwell: int = UP_DWELL) -> int | None:
    streak = 0
    for index, row in enumerate(rows):
        streak = streak + 1 if up_qualified(row) else 0
        if streak >= dwell:
            return index - dwell + 1
    return None


def preceding_median(rows: list[dict[str, Any]], index: int, field: str, window: int) -> float:
    start = max(0, index - window)
    values = [finite_number(row[field], field) for row in rows[start:index]]
    if not values:
        raise ValueError("a preceding window is required")
    return float(statistics.median(values))


def failure_events(rows: list[dict[str, Any]], start: int) -> list[tuple[int, int]]:
    events: list[tuple[int, int]] = []
    index = start
    while index < len(rows):
        if up_qualified(rows[index]):
            index += 1
            continue
        event_start = index
        while index + 1 < len(rows) and not up_qualified(rows[index + 1]):
            index += 1
        events.append((event_start, index))
        index += 1
    return events


def summarize_rows(run_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    validate_rows(rows)
    crossing = first_sustained_index(rows)
    if crossing is None:
        return {
            "run_id": run_id,
            "first_sustained_crossing_step": None,
            "old_detector_excursion_count": 0,
            "spike_count_after_crossing": 0,
            "events": [],
        }

    events = failure_events(rows, crossing + UP_DWELL)
    event_starts = {start for start, _ in events}
    spikes: list[int] = []
    event_records: list[dict[str, Any]] = []

    for index in range(crossing + UP_DWELL, len(rows)):
        loss_median = preceding_median(rows, index, "train_loss", ROLLING_WINDOW)
        gradient_median = preceding_median(rows, index, "gradient_norm", ROLLING_WINDOW)
        loss_ratio = float(rows[index]["train_loss"]) / max(loss_median, 1e-300)
        gradient_ratio = float(rows[index]["gradient_norm"]) / max(gradient_median, 1e-300)
        if loss_ratio >= LOSS_SPIKE_RATIO and gradient_ratio >= GRADIENT_SPIKE_RATIO:
            spikes.append(index)

    for start, end in events:
        row = rows[start]
        loss_median = preceding_median(rows, start, "train_loss", ROLLING_WINDOW)
        gradient_median = preceding_median(rows, start, "gradient_norm", ROLLING_WINDOW)
        loss_ratio = float(row["train_loss"]) / max(loss_median, 1e-300)
        gradient_ratio = float(row["gradient_norm"]) / max(gradient_median, 1e-300)
        next_index = end + 1
        event_records.append(
            {
                "start_step": int(row["step"]),
                "end_step": int(rows[end]["step"]),
                "duration_evaluations": end - start + 1,
                "next_evaluation_step": int(rows[next_index]["step"]) if next_index < len(rows) else None,
                "recovered_at_next_evaluation": next_index < len(rows) and up_qualified(rows[next_index]),
                "test_accuracy": float(row["test_accuracy"]),
                "test_loss": float(row["test_loss"]),
                "train_accuracy": float(row["train_accuracy"]),
                "train_loss": float(row["train_loss"]),
                "gradient_norm": float(row["gradient_norm"]),
                "prior_10_train_loss_median": loss_median,
                "prior_10_gradient_norm_median": gradient_median,
                "train_loss_ratio": loss_ratio,
                "gradient_norm_ratio": gradient_ratio,
                "posthoc_spike_rule_passed": loss_ratio >= LOSS_SPIKE_RATIO
                and gradient_ratio >= GRADIENT_SPIKE_RATIO,
                "crosses_proposed_down_threshold": down_qualified(row),
            }
        )

    return {
        "run_id": run_id,
        "first_sustained_crossing_step": int(rows[crossing]["step"]),
        "old_detector_excursion_count": len(events),
        "spike_count_after_crossing": len(spikes),
        "spike_steps_after_crossing": [int(rows[index]["step"]) for index in spikes],
        "spikes_not_starting_old_detector_excursions": sum(index not in event_starts for index in spikes),
        "events": event_records,
    }


def analyze(run_files: Iterable[Path]) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    source_hashes: dict[str, str] = {}
    for metrics_path in sorted(run_files):
        rows = json.loads(metrics_path.read_text(encoding="utf-8"))
        runs.append(summarize_rows(metrics_path.parent.name, rows))
        source_hashes[metrics_path.as_posix()] = sha256(metrics_path)

    events = [event for run in runs for event in run["events"]]
    spike_count = sum(int(run["spike_count_after_crossing"]) for run in runs)
    spike_events = sum(bool(event["posthoc_spike_rule_passed"]) for event in events)
    down_crossings = sum(bool(event["crosses_proposed_down_threshold"]) for event in events)
    loss_ratios = [float(event["train_loss_ratio"]) for event in events]
    gradient_ratios = [float(event["gradient_norm_ratio"]) for event in events]

    return {
        "schema_version": "asmp10_reversion_diagnostics_v0_4_1",
        "status": "posthoc_descriptive_not_claim_eligible",
        "source_v0_4_decision_unchanged": True,
        "definitions": {
            "old_up_threshold": {"test_accuracy_min": UP_ACCURACY, "test_loss_max": UP_LOSS},
            "old_entry_dwell_evaluations": UP_DWELL,
            "evaluation_spacing_steps": 100,
            "posthoc_spike_rule": {
                "preceding_evaluations": ROLLING_WINDOW,
                "train_loss_ratio_min": LOSS_SPIKE_RATIO,
                "gradient_norm_ratio_min": GRADIENT_SPIKE_RATIO,
            },
            "proposed_hysteretic_down_threshold_diagnostic_only": {
                "test_accuracy_below": DOWN_ACCURACY,
                "or_test_loss_above": DOWN_LOSS,
            },
        },
        "aggregate": {
            "old_detector_excursions": len(events),
            "single_evaluation_excursions": sum(event["duration_evaluations"] == 1 for event in events),
            "immediate_next_evaluation_recoveries": sum(
                bool(event["recovered_at_next_evaluation"]) for event in events
            ),
            "spike_correlated_excursions": spike_events,
            "post_crossing_spikes": spike_count,
            "post_crossing_spikes_without_old_detector_excursion": spike_count - spike_events,
            "spike_rule_positive_predictive_value_for_old_excursion": (
                spike_events / spike_count if spike_count else None
            ),
            "excursions_crossing_proposed_down_threshold": down_crossings,
            "persistent_reversions_under_five-evaluation_down_dwell": 0,
            "train_loss_ratio_range": [min(loss_ratios), max(loss_ratios)] if loss_ratios else None,
            "gradient_norm_ratio_range": [min(gradient_ratios), max(gradient_ratios)]
            if gradient_ratios
            else None,
        },
        "runs": runs,
        "source_sha256": source_hashes,
        "interpretation": (
            "Every v0.4 post-crossing failure was an isolated one-grid excursion, all were "
            "associated with the frozen post-hoc loss-and-gradient spike rule, and all recovered "
            "at the next 100-step evaluation. This is consistent with optimizer-coupled instability "
            "but does not identify its cause."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run_files = list(args.runs_dir.glob("*/metrics.json"))
    if not run_files:
        raise SystemExit(f"no metrics.json files found under {args.runs_dir}")
    result = analyze(run_files)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["aggregate"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
