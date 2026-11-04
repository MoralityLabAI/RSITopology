"""Post-hoc liveness check of v0.68 coordinates on burned v0.67 records.

This script is design evidence only.  It cannot make a claim eligible because
v0.68 was derived after the v0.67 construction outcomes were known.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_score(row: dict) -> float:
    raw = float(row["raw_log_odds_a_over_b"])
    return raw if int(row["display_order"]) == 0 else -raw


def binomial_upper_tail_half(successes: int, trials: int) -> float:
    return sum(math.comb(trials, k) for k in range(successes, trials + 1)) / (
        2**trials
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = [
        json.loads(line)
        for line in args.records.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_key: dict[tuple[str, str, int | None, int], dict] = {}
    for row in rows:
        key = (
            row["scenario_id"],
            row["arm"],
            row["target"],
            int(row["display_order"]),
        )
        if key in by_key:
            raise ValueError(f"duplicate record: {key}")
        by_key[key] = row

    cells: list[dict] = []
    for scenario_id in sorted({row["scenario_id"] for row in rows}):
        family = next(
            row["family"] for row in rows if row["scenario_id"] == scenario_id
        )
        for target in (0, 1):
            direction = 1.0 if target == 0 else -1.0
            endpoints: dict[str, list[float]] = defaultdict(list)
            for order in (0, 1):
                score = lambda arm, arm_target: canonical_score(  # noqa: E731
                    by_key[(scenario_id, arm, arm_target, order)]
                )
                content = direction * (
                    score("content", target) - score("balanced", None)
                )
                label = direction * (
                    score("label", target) - score("balanced", None)
                )
                specificity = direction * (
                    score("content", target) - score("label", target)
                )
                washout = direction * (
                    score("content_washout", target)
                    - score("balanced_washout", None)
                )
                endpoints["content_effect"].append(content)
                endpoints["label_effect"].append(label)
                endpoints["specificity"].append(specificity)
                endpoints["washout_effect"].append(washout)
            cells.append(
                {
                    "scenario_id": scenario_id,
                    "family": family,
                    "target": target,
                    "endpoints": {
                        name: {
                            "by_order": values,
                            "mean": sum(values) / 2.0,
                            "order_half_range": abs(values[0] - values[1]) / 2.0,
                            "strict_sign_agreement": (
                                values[0] > 0 and values[1] > 0
                            )
                            or (values[0] < 0 and values[1] < 0),
                        }
                        for name, values in endpoints.items()
                    },
                }
            )

    endpoint_summary = {}
    for endpoint in (
        "content_effect",
        "label_effect",
        "specificity",
        "washout_effect",
    ):
        values = [cell["endpoints"][endpoint] for cell in cells]
        positive_both = sum(
            item["by_order"][0] > 0 and item["by_order"][1] > 0
            for item in values
        )
        negative_both = sum(
            item["by_order"][0] < 0 and item["by_order"][1] < 0
            for item in values
        )
        intersection_lower = max(min(item["by_order"]) for item in values)
        intersection_upper = min(max(item["by_order"]) for item in values)
        endpoint_summary[endpoint] = {
            "cells": len(values),
            "positive_in_both_orders": positive_both,
            "negative_in_both_orders": negative_both,
            "opposed_or_zero_orders": len(values) - positive_both - negative_both,
            "median_order_mean": median(item["mean"] for item in values),
            "median_order_half_range": median(
                item["order_half_range"] for item in values
            ),
            "maximum_order_half_range": max(
                item["order_half_range"] for item in values
            ),
            "shared_effect_intersection_lower": intersection_lower,
            "shared_effect_intersection_upper": intersection_upper,
            "shared_effect_intersection_margin": (
                intersection_upper - intersection_lower
            ),
            "shared_effect_status": (
                "shared_effect_compatible_descriptive"
                if intersection_lower <= intersection_upper
                else "context_conditioning_required_descriptive"
            ),
            "exact_one_sided_sign_p_for_positive_both": binomial_upper_tail_half(
                positive_both, len(values)
            ),
        }

    result = {
        "schema_version": "asmp9_context_quotient_burned_reanalysis_v0_68",
        "status": "post_hoc_design_evidence_only",
        "source_records": {
            "path": str(args.records),
            "sha256": sha256(args.records),
            "count": len(rows),
        },
        "endpoint_summary": endpoint_summary,
        "cells": cells,
        "claim_boundary": (
            "The quotient and endpoints were chosen after these construction "
            "outcomes were known. This reanalysis can assess successor "
            "liveness but cannot support a scientific claim or reopen the "
            "v0.67 confirmation split."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(endpoint_summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
