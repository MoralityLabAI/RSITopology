"""Scalar audit of an externally generated lineage dose-response receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def linear_r_squared(xs: list[float], ys: list[float]) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    denominator = sum((value - x_mean) ** 2 for value in xs)
    slope = sum(
        (x_value - x_mean) * (y_value - y_mean)
        for x_value, y_value in zip(xs, ys)
    ) / denominator
    intercept = y_mean - slope * x_mean
    total = sum((value - y_mean) ** 2 for value in ys)
    residual = sum(
        (y_value - (intercept + slope * x_value)) ** 2
        for x_value, y_value in zip(xs, ys)
    )
    return 1.0 - residual / total


def first(rows: list[dict], predicate) -> int | None:
    match = next((row for row in rows if predicate(row)), None)
    return None if match is None else int(match["deg"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("artifacts/external_fable_files6/lineage_dose_response.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/lineage_dose_response_audit.json"),
    )
    args = parser.parse_args()
    rows = sorted(
        json.loads(args.input.read_text(encoding="utf-8")),
        key=lambda row: int(row["deg"]),
    )
    expected = list(range(0, 91, 5))
    actual = [int(row["deg"]) for row in rows]
    errors = [abs(float(row["chordal"]) - float(row["cos2"])) for row in rows]
    occupancies = [float(row["min_occ"]) for row in rows]
    linear_rows = [row for row in rows if int(row["deg"]) <= 50]
    payload = {
        "analysis_id": "lineage-dose-response-external-audit-v0.1",
        "source_file": args.input.name,
        "source_sha256": file_sha256(args.input),
        "evidence_class": "external_single_seed_unit_diagnostic_not_promoted",
        "row_count": len(rows),
        "expected_degrees": expected,
        "missing_degrees": [degree for degree in expected if degree not in actual],
        "complete_five_degree_grid": actual == expected,
        "lineage_monotone_nonincreasing": all(
            float(left["chordal"]) >= float(right["chordal"])
            for left, right in zip(rows, rows[1:])
        ),
        "maximum_absolute_chordal_cos2_error": max(errors),
        "mean_absolute_chordal_cos2_error": sum(errors) / len(errors),
        "minimum_occupancy_range": max(occupancies) - min(occupancies),
        "policy_uplift_vs_lineage_r_squared_through_50_degrees": linear_r_squared(
            [float(row["chordal"]) for row in linear_rows],
            [float(row["pol_std"]) for row in linear_rows],
        ),
        "policy_last_pass_degrees": max(
            int(row["deg"]) for row in rows if bool(row["pol_pass"])
        ),
        "policy_first_fail_degrees": first(rows, lambda row: not row["pol_pass"]),
        "edit_last_pass_degrees": max(
            int(row["deg"]) for row in rows if bool(row["edit_pass"])
        ),
        "edit_first_fail_degrees": first(rows, lambda row: not row["edit_pass"]),
        "claim_boundary": (
            "This verifies monotonic shape, constant occupancy, and staged gate "
            "failure in one external unit-scale seed. Missing grid cells and "
            "solver residuals are explicit. Flip locations are not thresholds."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
