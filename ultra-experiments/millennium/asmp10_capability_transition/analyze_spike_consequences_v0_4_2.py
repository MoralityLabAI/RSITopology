"""Describe which v0.4 post-crossing spikes caused metric excursions.

The table is descriptive and has no gate. It intentionally reuses the frozen
post-hoc spike definition from v0.4.1 rather than tuning a classifier.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DEFAULT_RUNS = HERE / "pilot_artifacts_v0_4" / "runs"
DEFAULT_JSON = HERE / "pilot_artifacts_v0_4" / "spike_consequences_v0_4_2.json"
DEFAULT_MD = HERE / "SPIKE_CONSEQUENCE_TABLE_v0_4_2.md"


def load_base():
    path = HERE / "analyze_reversion_diagnostics_v0_4_1.py"
    spec = importlib.util.spec_from_file_location("reversion_diagnostics_v041", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


BASE = load_base()


def ratio(row: dict[str, Any], rows: list[dict[str, Any]], index: int, field: str) -> float:
    median = BASE.preceding_median(rows, index, field, BASE.ROLLING_WINDOW)
    return float(row[field]) / max(median, 1e-300)


def analyze(runs_dir: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    source_hashes: dict[str, str] = {}
    for path in sorted(runs_dir.glob("*/metrics.json")):
        rows = json.loads(path.read_text(encoding="utf-8"))
        BASE.validate_rows(rows)
        crossing = BASE.first_sustained_index(rows)
        source_hashes[path.as_posix()] = BASE.sha256(path)
        if crossing is None:
            continue
        crossing_step = int(rows[crossing]["step"])
        for index in range(crossing + BASE.UP_DWELL, len(rows)):
            row = rows[index]
            loss_ratio = ratio(row, rows, index, "train_loss")
            gradient_ratio = ratio(row, rows, index, "gradient_norm")
            if loss_ratio < BASE.LOSS_SPIKE_RATIO or gradient_ratio < BASE.GRADIENT_SPIKE_RATIO:
                continue
            causes_excursion = not BASE.up_qualified(row)
            next_recovers = index + 1 < len(rows) and BASE.up_qualified(rows[index + 1])
            records.append(
                {
                    "run_id": path.parent.name,
                    "step": int(row["step"]),
                    "steps_since_first_sustained_crossing": int(row["step"]) - crossing_step,
                    "train_loss_ratio": loss_ratio,
                    "gradient_norm_ratio": gradient_ratio,
                    "severity_geometric_mean_over_rule_thresholds": math.sqrt(
                        (loss_ratio / BASE.LOSS_SPIKE_RATIO)
                        * (gradient_ratio / BASE.GRADIENT_SPIKE_RATIO)
                    ),
                    "test_accuracy": float(row["test_accuracy"]),
                    "test_loss": float(row["test_loss"]),
                    "causes_old_detector_excursion": causes_excursion,
                    "crosses_v0_5_1_down_threshold": BASE.down_qualified(row),
                    "recovers_at_next_100_step_evaluation": next_recovers if causes_excursion else None,
                }
            )

    by_loss = sorted(records, key=lambda record: (-record["train_loss_ratio"], record["run_id"], record["step"]))
    by_gradient = sorted(
        records, key=lambda record: (-record["gradient_norm_ratio"], record["run_id"], record["step"])
    )
    loss_rank = {(record["run_id"], record["step"]): index + 1 for index, record in enumerate(by_loss)}
    gradient_rank = {
        (record["run_id"], record["step"]): index + 1 for index, record in enumerate(by_gradient)
    }
    for record in records:
        key = (record["run_id"], record["step"])
        record["train_loss_ratio_rank_desc"] = loss_rank[key]
        record["gradient_norm_ratio_rank_desc"] = gradient_rank[key]

    excursions = [record for record in records if record["causes_old_detector_excursion"]]
    nonexcursions = [record for record in records if not record["causes_old_detector_excursion"]]
    top_count = len(excursions)

    def median_for(group: list[dict[str, Any]], field: str) -> float | None:
        return float(statistics.median(record[field] for record in group)) if group else None

    return {
        "schema_version": "asmp10_spike_consequences_v0_4_2",
        "status": "posthoc_descriptive_no_gate",
        "spike_rule_unchanged_from_v0_4_1": True,
        "aggregate": {
            "post_crossing_spikes": len(records),
            "old_detector_excursion_spikes": len(excursions),
            "nonexcursion_spikes": len(nonexcursions),
            "excursions_among_top_7_train_loss_ratios": sum(
                record["causes_old_detector_excursion"] for record in by_loss[:top_count]
            ),
            "excursions_among_top_7_gradient_norm_ratios": sum(
                record["causes_old_detector_excursion"] for record in by_gradient[:top_count]
            ),
            "median_train_loss_ratio_excursion": median_for(excursions, "train_loss_ratio"),
            "median_train_loss_ratio_nonexcursion": median_for(nonexcursions, "train_loss_ratio"),
            "median_gradient_ratio_excursion": median_for(excursions, "gradient_norm_ratio"),
            "median_gradient_ratio_nonexcursion": median_for(nonexcursions, "gradient_norm_ratio"),
            "median_steps_since_crossing_excursion": median_for(
                excursions, "steps_since_first_sustained_crossing"
            ),
            "median_steps_since_crossing_nonexcursion": median_for(
                nonexcursions, "steps_since_first_sustained_crossing"
            ),
        },
        "records": sorted(records, key=lambda record: (record["run_id"], record["step"])),
        "source_sha256": source_hashes,
        "claim_boundary": (
            "Describes the burned v0.4 cells only. Magnitude ranks and timing do not define a "
            "predictor, causal mechanism, or confirmation hypothesis."
        ),
    }


def markdown(result: dict[str, Any]) -> str:
    aggregate = result["aggregate"]
    lines = [
        "# ASMP-10 v0.4.2 spike-consequence table",
        "",
        "Post-hoc descriptive output over burned v0.4 cells. The spike rule is unchanged from v0.4.1 and no gate consumes this table.",
        "",
        "## Aggregate",
        "",
        f"- Spikes: {aggregate['post_crossing_spikes']} ({aggregate['old_detector_excursion_spikes']} excursion-causing; {aggregate['nonexcursion_spikes']} not).",
        f"- Excursion spikes among the seven largest train-loss ratios: {aggregate['excursions_among_top_7_train_loss_ratios']}/7.",
        f"- Excursion spikes among the seven largest gradient ratios: {aggregate['excursions_among_top_7_gradient_norm_ratios']}/7.",
        f"- Median train-loss ratio, excursion versus non-excursion: {aggregate['median_train_loss_ratio_excursion']:.2f} versus {aggregate['median_train_loss_ratio_nonexcursion']:.2f}.",
        f"- Median gradient ratio, excursion versus non-excursion: {aggregate['median_gradient_ratio_excursion']:.2f} versus {aggregate['median_gradient_ratio_nonexcursion']:.2f}.",
        f"- Median steps since crossing, excursion versus non-excursion: {aggregate['median_steps_since_crossing_excursion']:.0f} versus {aggregate['median_steps_since_crossing_nonexcursion']:.0f}.",
        "",
        "The seven excursion-causing spikes are not simply the seven largest under either component of the registered spike rule. This leaves state dependence live as a descriptive possibility, but the six-cell pilot cannot identify it.",
        "",
        "## Records",
        "",
        "| run | step | since crossing | loss ratio | gradient ratio | loss rank | gradient rank | excursion | down threshold |",
        "|---|---:|---:|---:|---:|---:|---:|:---:|:---:|",
    ]
    for record in result["records"]:
        lines.append(
            "| {run_id} | {step} | {steps_since_first_sustained_crossing} | {train_loss_ratio:.2f} | "
            "{gradient_norm_ratio:.2f} | {train_loss_ratio_rank_desc} | "
            "{gradient_norm_ratio_rank_desc} | {excursion} | {down} |".format(
                **record,
                excursion="yes" if record["causes_old_detector_excursion"] else "no",
                down="yes" if record["crosses_v0_5_1_down_threshold"] else "no",
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            result["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    result = analyze(args.runs_dir)
    args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(result), encoding="utf-8")
    print(json.dumps(result["aggregate"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

