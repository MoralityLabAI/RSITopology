"""Analyze the ASMP-9 v0.34 burned calibration pilot."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any, Iterable, Mapping

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from pilot_design import canonical_bytes, sha256_bytes  # noqa: E402
from run_burned_pilot import (  # noqa: E402
    MANIFEST_SCHEMA,
    RECORD_SCHEMA,
    REGISTRATION_SCHEMA,
    SUMMARY_SCHEMA,
    load_manifest,
    load_registration,
)


ANALYSIS_SCHEMA = "asmp9_physical_acquisition_burned_pilot_analysis_v0_34"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def q(value: str | int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def quantile(values: Iterable[float], probability: float) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("quantile requires at least one value")
    if not 0 <= probability <= 1:
        raise ValueError("quantile probability is outside [0,1]")
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("schema_version") != RECORD_SCHEMA:
                raise ValueError(
                    f"unexpected record schema on line {line_number}"
                )
            expected = str(record["record_sha256"])
            actual = sha256_bytes(
                canonical_bytes(
                    {
                        key: value
                        for key, value in record.items()
                        if key != "record_sha256"
                    }
                )
            )
            if actual != expected:
                raise ValueError(
                    f"record hash mismatch on line {line_number}"
                )
            records.append(record)
    if not records:
        raise ValueError("pilot record file is empty")
    return records


def validate_complete_pilot(
    manifest: Mapping[str, Any],
    summary: Mapping[str, Any],
    records: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    if summary.get("schema_version") != SUMMARY_SCHEMA:
        raise ValueError("unexpected capture-summary schema")
    if summary.get("status") != "burned_pilot_capture_completed":
        raise ValueError("analysis requires a complete burned pilot")
    expected_rows = {
        str(row["row_id"]): row
        for row in manifest["rows"]
        if row["phase"] == "burned_pilot"
    }
    if len(expected_rows) != 972:
        raise ValueError("burned-pilot row universe changed")
    observed: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record["phase"] != "burned_pilot":
            raise ValueError("holdout record present in pilot outcomes")
        observed[str(record["row_id"])].append(record)
    if set(observed) != set(expected_rows):
        missing = sorted(set(expected_rows) - set(observed))
        extra = sorted(set(observed) - set(expected_rows))
        raise ValueError(
            f"pilot row join mismatch: missing={missing[:3]} extra={extra[:3]}"
        )
    if any(len(items) != 2 for items in observed.values()):
        raise ValueError("each pilot row must have exactly two cold starts")
    if len(records) != 1944:
        raise ValueError("burned pilot requires exactly 1,944 records")
    return expected_rows


def group_mean(
    records: Iterable[Mapping[str, Any]],
    key_fields: tuple[str, ...],
) -> dict[tuple[Any, ...], float]:
    grouped: dict[tuple[Any, ...], list[float]] = defaultdict(list)
    for record in records:
        grouped[
            tuple(record.get(field) for field in key_fields)
        ].append(float(record["target_log_odds"]))
    return {
        key: statistics.fmean(values)
        for key, values in grouped.items()
    }


def crossing(points: list[tuple[Fraction, float]]) -> dict[str, Any]:
    ordered = sorted(points)
    violations = sum(
        right_value > left_value
        for (_, left_value), (_, right_value) in zip(
            ordered,
            ordered[1:],
        )
    )
    if ordered[0][1] < 0:
        return {
            "status": "below_grid",
            "estimate": None,
            "bound": str(ordered[0][0]),
            "monotonicity_violations": violations,
        }
    if ordered[-1][1] > 0:
        return {
            "status": "above_grid",
            "estimate": None,
            "bound": str(ordered[-1][0]),
            "monotonicity_violations": violations,
        }
    for probability, value in ordered:
        if value == 0:
            return {
                "status": "bracketed",
                "estimate": float(probability),
                "bracket": [str(probability), str(probability)],
                "monotonicity_violations": violations,
            }
    for (left_p, left_y), (right_p, right_y) in zip(
        ordered,
        ordered[1:],
    ):
        if left_y >= 0 >= right_y:
            denominator = left_y - right_y
            estimate = (
                float(left_p)
                if denominator == 0
                else float(left_p)
                + (left_y / denominator)
                * (float(right_p) - float(left_p))
            )
            return {
                "status": "bracketed",
                "estimate": estimate,
                "bracket": [str(left_p), str(right_p)],
                "monotonicity_violations": violations,
            }
    return {
        "status": "nonmonotone_unbracketed",
        "estimate": None,
        "monotonicity_violations": violations,
    }


def analyze_gambles(
    records: list[dict[str, Any]],
    query_type: str,
    object_field: str,
) -> list[dict[str, Any]]:
    selected = [
        record for record in records if record["query_type"] == query_type
    ]
    means = group_mean(
        selected,
        (object_field, "family_id", "anchor_probability"),
    )
    by_object: dict[tuple[str, str], list[tuple[Fraction, float]]] = (
        defaultdict(list)
    )
    for (object_id, family_id, probability), value in means.items():
        by_object[(str(object_id), str(family_id))].append(
            (q(str(probability)), value)
        )
    output: list[dict[str, Any]] = []
    for (object_id, family_id), points in sorted(by_object.items()):
        result = crossing(points)
        output.append(
            {
                object_field: object_id,
                "family_id": family_id,
                **result,
                "grid_log_odds": [
                    {
                        "anchor_probability": str(probability),
                        "mean_target_log_odds": value,
                    }
                    for probability, value in sorted(points)
                ],
            }
        )
    return output


def option_order_bias(records: list[dict[str, Any]]) -> list[float]:
    keys = (
        "query_type",
        "family_id",
        "cell_id",
        "mixture_id",
        "policy_contrast_index",
        "anchor_probability",
        "norm",
        "planned_epoch",
    )
    grouped: dict[tuple[Any, ...], dict[str, float]] = defaultdict(dict)
    for record in records:
        grouped[tuple(record.get(key) for key in keys)][
            str(record["choice_order"])
        ] = float(record["target_log_odds"])
    biases: list[float] = []
    for values in grouped.values():
        if set(values) != {"target_first", "target_second"}:
            raise ValueError("choice-order pair is incomplete")
        biases.append(
            0.5
            * abs(values["target_first"] - values["target_second"])
        )
    return biases


def cold_start_deltas(records: list[dict[str, Any]]) -> list[float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for record in records:
        grouped[str(record["row_id"])].append(
            float(record["target_log_odds"])
        )
    return [
        abs(values[0] - values[1])
        for values in grouped.values()
        if len(values) == 2
    ]


def analyze_policy_probes(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected = [
        record for record in records if record["query_type"] == "policy_probe"
    ]
    means = group_mean(
        selected,
        (
            "policy_contrast_index",
            "cell_index",
            "family_id",
            "norm",
        ),
    )
    grouped: dict[
        tuple[int, int, str],
        list[tuple[Fraction, float]],
    ] = defaultdict(list)
    for (contrast, cell, family, norm), value in means.items():
        grouped[(int(contrast), int(cell), str(family))].append(
            (q(str(norm)), value)
        )

    rows: list[dict[str, Any]] = []
    slopes_by_probe: dict[tuple[int, int], list[float]] = defaultdict(list)
    all_residuals: list[float] = []
    effect_magnitudes: list[float] = []
    for (contrast, cell, family), points in sorted(grouped.items()):
        point_map = dict(points)
        if Fraction(0) not in point_map:
            raise ValueError("policy probe lacks norm-zero sham")
        baseline = point_map[Fraction(0)]
        positive = sorted(
            (norm, value - baseline)
            for norm, value in points
            if norm > 0
        )
        denominator = sum(float(norm) ** 2 for norm, _ in positive)
        slope = (
            sum(float(norm) * delta for norm, delta in positive)
            / denominator
        )
        residuals = [
            {
                "norm": str(norm),
                "observed_delta_log_odds": delta,
                "linear_prediction": slope * float(norm),
                "absolute_secant_residual": abs(
                    delta - slope * float(norm)
                ),
            }
            for norm, delta in positive
        ]
        max_norm, max_effect = positive[-1]
        all_residuals.extend(
            item["absolute_secant_residual"] for item in residuals
        )
        effect_magnitudes.append(abs(max_effect))
        slopes_by_probe[(contrast, cell)].append(slope)
        rows.append(
            {
                "policy_contrast_index": contrast,
                "cell_index": cell,
                "family_id": family,
                "baseline_log_odds": baseline,
                "slope": slope,
                "maximum_norm": str(max_norm),
                "maximum_norm_effect": max_effect,
                "maximum_absolute_secant_residual": max(
                    item["absolute_secant_residual"] for item in residuals
                ),
                "norm_rows": residuals,
            }
        )

    slope_matrix = np.asarray(
        [
            [
                statistics.median(slopes_by_probe[(contrast, cell)])
                for cell in (0, 1, 2, 4, 5, 7)
            ]
            for contrast in (0, 1, 2)
        ],
        dtype=np.float64,
    )
    singular_values = np.linalg.svd(slope_matrix, compute_uv=False)
    scale = float(singular_values[0]) if singular_values.size else 0.0
    tolerance = max(slope_matrix.shape) * np.finfo(float).eps * scale
    numerical_rank = int(np.sum(singular_values > tolerance))
    summary = {
        "family_probe_rows": len(rows),
        "probe_count": len(slopes_by_probe),
        "median_slope_matrix": slope_matrix.tolist(),
        "slope_matrix_singular_values": singular_values.tolist(),
        "slope_matrix_numerical_rank": numerical_rank,
        "absolute_secant_residual": {
            "median": statistics.median(all_residuals),
            "q90": quantile(all_residuals, 0.9),
            "q95": quantile(all_residuals, 0.95),
            "maximum": max(all_residuals),
        },
        "maximum_norm_effect_magnitude": {
            "median": statistics.median(effect_magnitudes),
            "q10": quantile(effect_magnitudes, 0.1),
            "minimum": min(effect_magnitudes),
            "maximum": max(effect_magnitudes),
        },
    }
    return rows, summary


def mixture_residuals(
    cell_results: list[dict[str, Any]],
    mixture_results: list[dict[str, Any]],
    manifest: Mapping[str, Any],
) -> list[dict[str, Any]]:
    cells = {
        (row["cell_id"], row["family_id"]): row
        for row in cell_results
        if row["status"] == "bracketed"
    }
    mixtures = {
        (row["mixture_id"], row["family_id"]): row
        for row in mixture_results
        if row["status"] == "bracketed"
    }
    cell_id_by_index = {
        int(row["cell_index"]): str(row["cell_id"])
        for row in manifest["cells"]
    }
    output: list[dict[str, Any]] = []
    for mixture in manifest["compound_mixtures"]:
        mixture_id = str(mixture["mixture_id"])
        first_id = cell_id_by_index[int(mixture["first_cell_index"])]
        second_id = cell_id_by_index[int(mixture["second_cell_index"])]
        weight = float(q(str(mixture["first_weight"])))
        for family in manifest["families"]["burned_pilot"]:
            mixture_row = mixtures.get((mixture_id, family))
            first_row = cells.get((first_id, family))
            second_row = cells.get((second_id, family))
            available = all(
                row is not None
                for row in (mixture_row, first_row, second_row)
            )
            residual = None
            if available:
                residual = float(mixture_row["estimate"]) - (
                    weight * float(first_row["estimate"])
                    + (1 - weight) * float(second_row["estimate"])
                )
            output.append(
                {
                    "mixture_id": mixture_id,
                    "family_id": family,
                    "available": available,
                    "residual": residual,
                }
            )
    return output


def build_analysis(
    registration_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    registration = load_registration(registration_path)
    if registration.get("schema_version") != REGISTRATION_SCHEMA:
        raise ValueError("unexpected registration schema")
    manifest = load_manifest(registration)
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        raise ValueError("unexpected manifest schema")
    summary_path = output_dir / "summary.json"
    records_path = output_dir / "pilot_records.jsonl"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    records = load_records(records_path)
    validate_complete_pilot(manifest, summary, records)

    cell_results = analyze_gambles(
        records,
        "standard_gamble",
        "cell_id",
    )
    compound_results = analyze_gambles(
        records,
        "compound_gamble",
        "mixture_id",
    )
    policy_rows, policy_summary = analyze_policy_probes(records)
    residual_rows = mixture_residuals(
        cell_results,
        compound_results,
        manifest,
    )
    available_residuals = [
        abs(float(row["residual"]))
        for row in residual_rows
        if row["available"]
    ]
    order_biases = option_order_bias(records)
    cold_deltas = cold_start_deltas(records)

    cell_bracketed = sum(
        row["status"] == "bracketed" for row in cell_results
    )
    compound_bracketed = sum(
        row["status"] == "bracketed" for row in compound_results
    )
    monotonic_violations = sum(
        int(row["monotonicity_violations"])
        for row in (*cell_results, *compound_results)
    )
    analysis: dict[str, Any] = {
        "schema_version": ANALYSIS_SCHEMA,
        "status": "burned_pilot_analyzed_not_confirmation",
        "counts": {
            "records": len(records),
            "cell_family_curves": len(cell_results),
            "cell_family_curves_bracketed": cell_bracketed,
            "compound_family_curves": len(compound_results),
            "compound_family_curves_bracketed": compound_bracketed,
            "mixture_residuals_available": len(available_residuals),
            "monotonicity_violations": monotonic_violations,
        },
        "repeatability": {
            "cold_start_log_odds_delta": {
                "median": statistics.median(cold_deltas),
                "q95": quantile(cold_deltas, 0.95),
                "maximum": max(cold_deltas),
            },
            "absolute_option_order_bias": {
                "median": statistics.median(order_biases),
                "q90": quantile(order_biases, 0.9),
                "q95": quantile(order_biases, 0.95),
                "maximum": max(order_biases),
            },
        },
        "mixture_affinity": (
            {
                "absolute_residual_median": statistics.median(
                    available_residuals
                ),
                "absolute_residual_q90": quantile(
                    available_residuals,
                    0.9,
                ),
                "absolute_residual_maximum": max(available_residuals),
                "rows": residual_rows,
            }
            if available_residuals
            else {
                "status": "unavailable_no_jointly_bracketed_mixtures",
                "rows": residual_rows,
            }
        ),
        "policy_probes": {
            **policy_summary,
            "rows": policy_rows,
        },
        "standard_gambles": cell_results,
        "compound_gambles": compound_results,
        "pilot_derived_calibration_candidates": {
            "cold_start_log_odds_ceiling": (
                max(cold_deltas) * 2 + 1e-8
            ),
            "order_bias_q95": quantile(order_biases, 0.95),
            "secant_absolute_error_q95": policy_summary[
                "absolute_secant_residual"
            ]["q95"],
            "practical_policy_effect_floor_candidate": (
                2 * quantile(order_biases, 0.95)
            ),
            "warning": (
                "These are burned-pilot candidates, not registered confirmation "
                "thresholds. A versioned successor must freeze any chosen values "
                "before holdout execution."
            ),
        },
        "inputs": {
            "registration_sha256": sha256_file(registration_path),
            "registration_content_sha256": registration[
                "registration_content_sha256"
            ],
            "capture_summary_sha256": sha256_file(summary_path),
            "records_sha256": sha256_file(records_path),
            "analyzer_sha256": sha256_file(Path(__file__).resolve()),
        },
        "claim_boundary": registration["claim_boundary"],
    }
    analysis["analysis_content_sha256"] = sha256_bytes(
        canonical_bytes(
            {
                key: value
                for key, value in analysis.items()
                if key != "analysis_content_sha256"
            }
        )
    )
    return analysis


def render_report(analysis: Mapping[str, Any]) -> str:
    counts = analysis["counts"]
    repeatability = analysis["repeatability"]
    policy = analysis["policy_probes"]
    mixture = analysis["mixture_affinity"]
    mixture_text = (
        "unavailable"
        if "status" in mixture
        else (
            f"median absolute residual {mixture['absolute_residual_median']:.6g}; "
            f"90th percentile {mixture['absolute_residual_q90']:.6g}"
        )
    )
    return f"""# ASMP-9 v0.34 burned-pilot report

**Status:** `burned_pilot_analyzed_not_confirmation`

The full two-cold-start calibration captured {counts['records']:,} receipts.
The common standard-gamble ruler bracketed
{counts['cell_family_curves_bracketed']}/{counts['cell_family_curves']} cell-by-family
curves. Compound lotteries bracketed
{counts['compound_family_curves_bracketed']}/{counts['compound_family_curves']}
curves. Mixture-affinity calibration was {mixture_text}.

## Measurement stability

```text
maximum cold-start log-odds delta  {repeatability['cold_start_log_odds_delta']['maximum']:.9g}
95th-percentile option-order bias  {repeatability['absolute_option_order_bias']['q95']:.9g}
monotonicity violations            {counts['monotonicity_violations']}
```

## Factorized policy probes

```text
registered probes                  {policy['probe_count']}
median-slope matrix numerical rank {policy['slope_matrix_numerical_rank']}
minimum max-norm effect magnitude  {policy['maximum_norm_effect_magnitude']['minimum']:.9g}
95th-percentile secant residual    {policy['absolute_secant_residual']['q95']:.9g}
maximum secant residual            {policy['absolute_secant_residual']['maximum']:.9g}
```

These numbers calibrate a successor protocol; they are not gates retrofitted
to this pilot. Any confirmation must freeze its thresholds, common norm set,
prompt-family split, and practical margin in a new registration before
executing the untouched holdout families.

## Claim boundary

{analysis['claim_boundary']}

Machine-readable analysis content SHA-256:
`{analysis['analysis_content_sha256']}`
"""


def write_once(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"refusing to overwrite unequal result: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def run(args: argparse.Namespace) -> None:
    analysis = build_analysis(
        args.registration.resolve(),
        args.output_dir.resolve(),
    )
    write_once(args.analysis_json.resolve(), canonical_bytes(analysis))
    write_once(
        args.report.resolve(),
        render_report(analysis).encode("utf-8"),
    )
    print(json.dumps(analysis, indent=2, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--analysis-json",
        type=Path,
        default=HERE / "BURNED_PILOT_ANALYSIS_v0_34.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=HERE / "BURNED_PILOT_REPORT_v0_34.md",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
