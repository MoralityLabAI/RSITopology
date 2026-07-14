"""Find geometry-pass transitions with disproportionate downstream utility loss.

This is a scalar receipt analysis. It does not reconstruct operators, fit a
model, load weights, or change any registered gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("artifacts/external_fable_files3/occupancy_sweep.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/lineage_transition_analysis.json"),
    )
    parser.add_argument("--collapse-ratio", type=float, default=0.5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = json.loads(args.input.read_text(encoding="utf-8"))
    by_seed: dict[int, list[dict]] = {}
    for row in rows:
        if row.get("geom_passed") and row.get("policy_std") is not None:
            by_seed.setdefault(int(row["seed"]), []).append(row)

    transitions = []
    for seed, seed_rows in sorted(by_seed.items()):
        ordered = sorted(seed_rows, key=lambda row: float(row["noise"]))
        for left, right in zip(ordered, ordered[1:]):
            ratio = float(right["policy_std"]) / float(left["policy_std"])
            if ratio > args.collapse_ratio:
                continue
            transitions.append(
                {
                    "seed": seed,
                    "from_noise": float(left["noise"]),
                    "to_noise": float(right["noise"]),
                    "rank_before": int(left["rank"]),
                    "rank_after": int(right["rank"]),
                    "min_occupancy_before": float(left["min_occ"]),
                    "min_occupancy_after": float(right["min_occ"]),
                    "min_occupancy_absolute_change": float(right["min_occ"])
                    - float(left["min_occ"]),
                    "policy_standardized_before": float(left["policy_std"]),
                    "policy_standardized_after": float(right["policy_std"]),
                    "policy_retained_fraction": ratio,
                    "policy_loss_fraction": 1.0 - ratio,
                    "edit_passed_before": bool(left["edit_passed"]),
                    "edit_passed_after": bool(right["edit_passed"]),
                }
            )

    summary = {
        "analysis_id": "geometry-pass-utility-collapse-v0.1",
        "source_file": args.input.name,
        "source_sha256": sha256(args.input),
        "claim_boundary": (
            "Post hoc scalar analysis of external diagnostic receipts. It identifies "
            "a failure mode for occupancy-only sufficiency; it does not establish its "
            "mechanism or alter any frozen gate."
        ),
        "collapse_ratio_threshold": args.collapse_ratio,
        "band_attribution_available": all(
            "selected_band" in row for row in rows
        ),
        "interpretation_warning": (
            "The source summary omits selected_band. This analysis can detect a "
            "geometry-pass/utility-collapse transition but cannot distinguish "
            "within-band migration from categorical band failover."
        ),
        "transition_count": len(transitions),
        "transitions": transitions,
    }
    if transitions:
        summary["aggregate"] = {
            "mean_policy_retained_fraction": mean(
                row["policy_retained_fraction"] for row in transitions
            ),
            "mean_policy_loss_fraction": mean(
                row["policy_loss_fraction"] for row in transitions
            ),
            "mean_min_occupancy_absolute_change": mean(
                row["min_occupancy_absolute_change"] for row in transitions
            ),
            "edit_pass_to_fail_count": sum(
                row["edit_passed_before"] and not row["edit_passed_after"]
                for row in transitions
            ),
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
