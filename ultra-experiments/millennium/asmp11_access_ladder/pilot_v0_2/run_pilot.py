from __future__ import annotations

import csv
import json
from fractions import Fraction
from pathlib import Path

from exact_power import all_registered_plans, find_exact_design


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "artifacts_pilot"
N_GRID = (8, 12, 16, 20)
K_GRID = (3, 4, 5, 6)
FLIP_GRID = (Fraction(1, 20), Fraction(3, 20), Fraction(1, 4))
ALPHA = Fraction(1, 20)
TARGET_POWER = Fraction(9, 10)
SAMPLE_CAP = 4096


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    cache = {}

    for n in N_GRID:
        for k in K_GRID:
            if k > n:
                continue
            plans = all_registered_plans(n, k)
            for flip_rate in FLIP_GRID:
                condition_rows = []
                for plan in plans:
                    key = (plan.query_count, flip_rate)
                    if key not in cache:
                        cache[key] = find_exact_design(
                            plan.query_count,
                            flip_rate,
                            ALPHA,
                            TARGET_POWER,
                            SAMPLE_CAP,
                        )
                    design = cache[key]
                    if design is None:
                        row = {
                            "n": n,
                            "k": k,
                            "flip_rate": str(flip_rate),
                            "plan": plan.name,
                            "observation_order": plan.observation_order,
                            "intervention_width": plan.intervention_width,
                            "query_count": plan.query_count,
                            "samples_per_query": None,
                            "total_samples": None,
                            "cutoff": None,
                            "fwer_upper": None,
                            "power_lower": None,
                            "feasible": 0,
                        }
                    else:
                        row = {
                            "n": n,
                            "k": k,
                            "flip_rate": str(flip_rate),
                            "plan": plan.name,
                            "observation_order": plan.observation_order,
                            "intervention_width": plan.intervention_width,
                            "query_count": plan.query_count,
                            "samples_per_query": design.samples_per_query,
                            "total_samples": design.total_samples,
                            "cutoff": design.cutoff,
                            "fwer_upper": str(design.familywise_error_upper),
                            "power_lower": str(design.signal_power_lower),
                            "feasible": 1,
                        }
                    rows.append(row)
                    condition_rows.append(row)

                pure = next(
                    row
                    for row in condition_rows
                    if row["observation_order"] == k and row["intervention_width"] == 0
                )
                boundary = [
                    row
                    for row in condition_rows
                    if row["observation_order"] + row["intervention_width"] == k
                    and row["feasible"]
                ]
                containment = [
                    row
                    for row in condition_rows
                    if row["observation_order"] == 0
                    and row["intervention_width"] >= k
                    and row["feasible"]
                ]
                first_inversion = next(
                    (
                        row
                        for row in sorted(containment, key=lambda item: int(item["intervention_width"]))
                        if int(row["total_samples"]) < int(pure["total_samples"])
                    ),
                    None,
                )
                summaries.append(
                    {
                        "n": n,
                        "k": k,
                        "flip_rate": str(flip_rate),
                        "pure_observation_samples": pure["total_samples"],
                        "best_boundary_samples": min(int(row["total_samples"]) for row in boundary),
                        "boundary_inversion": int(
                            min(int(row["total_samples"]) for row in boundary)
                            < int(pure["total_samples"])
                        ),
                        "first_containment_inversion_width": (
                            first_inversion["intervention_width"] if first_inversion else None
                        ),
                        "first_containment_inversion_samples": (
                            first_inversion["total_samples"] if first_inversion else None
                        ),
                        "full_clamp_samples": next(
                            row["total_samples"] for row in containment if row["intervention_width"] == n
                        ),
                    }
                )

    fieldnames = list(rows[0])
    with (OUTPUT / "pilot_cells.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    with (OUTPUT / "pilot_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)

    result = {
        "status": "construction_only_non_claim_eligible_pilot",
        "conditions": len(summaries),
        "cells": len(rows),
        "all_boundary_inversions_absent": all(not row["boundary_inversion"] for row in summaries),
        "all_containment_inversions_exist": all(
            row["first_containment_inversion_width"] is not None for row in summaries
        ),
        "minimum_inversion_width_fraction": min(
            Fraction(int(row["first_containment_inversion_width"]), int(row["n"]))
            for row in summaries
        ).__str__(),
        "maximum_inversion_width_fraction": max(
            Fraction(int(row["first_containment_inversion_width"]), int(row["n"]))
            for row in summaries
        ).__str__(),
        "interpretation": "Sample-cost inversion exists only after purchasing additional intervention width; no r+s=k boundary plan beats pure observation in this pilot.",
    }
    (OUTPUT / "pilot_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
