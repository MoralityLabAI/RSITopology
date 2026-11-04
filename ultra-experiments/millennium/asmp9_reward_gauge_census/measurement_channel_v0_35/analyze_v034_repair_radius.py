"""Retrospective repair-radius analysis of the burned v0.34.4 ruler."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import statistics
from typing import Any

from monotone_ruler import curve_certificate


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = (
    HERE.parent
    / "physical_acquisition_v0_34"
    / "BURNED_PILOT_ANALYSIS_v0_34_4.json"
)
EXPECTED_INPUT_SHA256 = (
    "9fec63ebcfaa1761b3826a70901e85f7c43b98cb7d77113c70a61b66832dfbf0"
)
CANONICAL_INPUT_PATH = (
    "ultra-experiments/millennium/asmp9_reward_gauge_census/"
    "physical_acquisition_v0_34/BURNED_PILOT_ANALYSIS_v0_34_4.json"
)
PREFERRED_CELLS = {"cell_00", "cell_01", "cell_02", "cell_04", "cell_05", "cell_07"}


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    radii = [float(row["monotone_linf_radius"]) for row in rows]
    normalized = [
        float(row["normalized_repair_radius"])
        for row in rows
        if row["normalized_repair_radius"] is not None
    ]
    return {
        "curves": len(rows),
        "robust_zero_crossings": sum(
            bool(row["robust_zero_crossing_at_repair_radius"]) for row in rows
        ),
        "monotone_linf_radius": {
            "median": statistics.median(radii),
            "q90": quantile(radii, 0.90),
            "q95": quantile(radii, 0.95),
            "maximum": max(radii),
        },
        "normalized_repair_radius": {
            "median": statistics.median(normalized),
            "q90": quantile(normalized, 0.90),
            "maximum": max(normalized),
        },
    }


def certify_rows(
    source_rows: list[dict[str, Any]],
    object_field: str,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in source_rows:
        values = [
            float(point["mean_target_log_odds"])
            for point in row["grid_log_odds"]
        ]
        output.append(
            {
                object_field: row[object_field],
                "family_id": row["family_id"],
                **curve_certificate(values),
            }
        )
    return output


def pooled_family_curves(
    source_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[list[float]]] = defaultdict(list)
    for row in source_rows:
        grouped[str(row["family_id"])].append(
            [
                float(point["mean_target_log_odds"])
                for point in row["grid_log_odds"]
            ]
        )
    output: list[dict[str, Any]] = []
    for family, curves in sorted(grouped.items()):
        means = [
            statistics.fmean(curve[index] for curve in curves)
            for index in range(len(curves[0]))
        ]
        output.append(
            {
                "family_id": family,
                "mean_curve": means,
                **curve_certificate(means),
            }
        )
    return output


def build_analysis(input_path: Path) -> dict[str, Any]:
    actual_hash = sha256_file(input_path)
    if actual_hash != EXPECTED_INPUT_SHA256:
        raise ValueError("v0.34.4 analysis hash mismatch")
    source = json.loads(input_path.read_text(encoding="utf-8"))
    standard = certify_rows(source["standard_gambles"], "cell_id")
    compound = certify_rows(source["compound_gambles"], "mixture_id")
    preferred = [row for row in standard if row["cell_id"] in PREFERRED_CELLS]
    result: dict[str, Any] = {
        "schema_version": "asmp9_measurement_channel_repair_radius_v0_35",
        "status": "retrospective_development_not_confirmation",
        "input": {
            "path": CANONICAL_INPUT_PATH,
            "sha256": actual_hash,
            "outcomes_previously_consumed": True,
        },
        "implementation": {
            "analyzer_sha256": sha256_file(Path(__file__).resolve()),
            "monotone_ruler_sha256": sha256_file(
                HERE / "monotone_ruler.py"
            ),
        },
        "theorem": {
            "object": "distance to the cone of nonincreasing ruler curves",
            "formula": "d_inf(y,C)=0.5*max_{i<j}(y_j-y_i)_+",
            "robust_crossing_condition": "y_0>=d_inf and y_m<=-d_inf",
            "novelty": "classical isotonic-regression specialization; no novelty claim",
        },
        "standard_gambles": {
            "summary": summarize(standard),
            "preferred_basis_summary": summarize(preferred),
            "pooled_family_curves": pooled_family_curves(
                source["standard_gambles"]
            ),
            "rows": standard,
        },
        "compound_gambles": {
            "summary": summarize(compound),
            "pooled_family_curves": pooled_family_curves(
                source["compound_gambles"]
            ),
            "rows": compound,
        },
        "decision": "v0_34_prompt_ruler_not_admissible",
        "decision_reason": (
            "Only a strict subset of required standard-gamble and compound "
            "curves has a robust zero crossing at its exact monotone-repair "
            "radius. Isotonic repair cannot manufacture missing endpoint support."
        ),
        "successor_requirement": (
            "Add independent position/code controls and p=0,p=1 dominance "
            "endpoints; derive the admissible repair radius from those controls "
            "before any mixture or decision-quotient gate."
        ),
        "claim_boundary": (
            "This is a retrospective analysis of burned pilot summaries. It "
            "cannot confirm a ruler, consume the untouched holdout, or resolve "
            "ASMP-9."
        ),
    }
    result["analysis_content_sha256"] = hashlib.sha256(
        canonical_bytes(result)
    ).hexdigest()
    return result


def render_report(result: dict[str, Any]) -> str:
    standard = result["standard_gambles"]["summary"]
    preferred = result["standard_gambles"]["preferred_basis_summary"]
    compound = result["compound_gambles"]["summary"]
    return f"""# ASMP-9 v0.35 monotone-ruler repair-radius analysis

**Status:** `retrospective_development_not_confirmation`

For an ordered score curve `y`, the exact distance to the cone of
nonincreasing curves is

```text
d_inf(y, C) = 0.5 * max_(i<j) (y_j - y_i)_+.
```

This is a classical isotonic-regression fact. It separates small local
non-monotonicity from the distinct problem of missing endpoint support.

| Curve set | Curves | Robust crossings | Median d_inf | Maximum d_inf |
|---|---:|---:|---:|---:|
| standard gambles | {standard['curves']} | {standard['robust_zero_crossings']} | {standard['monotone_linf_radius']['median']:.6f} | {standard['monotone_linf_radius']['maximum']:.6f} |
| preferred standard basis | {preferred['curves']} | {preferred['robust_zero_crossings']} | {preferred['monotone_linf_radius']['median']:.6f} | {preferred['monotone_linf_radius']['maximum']:.6f} |
| compound gambles | {compound['curves']} | {compound['robust_zero_crossings']} | {compound['monotone_linf_radius']['median']:.6f} | {compound['monotone_linf_radius']['maximum']:.6f} |

The repair radii are modest, especially for compound lotteries, but only a
strict subset of the required curves has endpoints that force a zero crossing
under every radius-close repair. Isotonic regression would smooth the curves;
it would not make the unavailable certainty equivalents observed.

## Decision

`v0_34_prompt_ruler_not_admissible`

The successor must independently estimate code/position error and include the
dominance endpoints `p=0` and `p=1`. Mixture and decision-quotient analysis
remain downstream of that admission gate.

## Claim boundary

{result['claim_boundary']}

Analysis content SHA-256:
`{result['analysis_content_sha256']}`
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_analysis(args.input.resolve())
    outputs = (
        (args.output, canonical_bytes(result)),
        (args.report, render_report(result).encode("utf-8")),
    )
    for path, payload in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != payload:
            raise FileExistsError(f"refusing to overwrite unequal output: {path}")
        if not path.exists():
            path.write_bytes(payload)


if __name__ == "__main__":
    main()
