"""Write the matched-lineage flat/curved monitor-holonomy control receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.holonomy import evaluate_grassmann_loop  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/monitor_holonomy_control.json"),
    )
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--step-size", type=float, default=0.1)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite receipt: {args.output}")

    flat = evaluate_grassmann_loop(
        "flat", steps=args.steps, step_size=args.step_size
    )
    curved = evaluate_grassmann_loop(
        "curved", steps=args.steps, step_size=args.step_size
    )
    gates = {
        "matched_minimum_edge_worst_direction_retention": abs(
            flat["minimum_edge_worst_direction_retention"]
            - curved["minimum_edge_worst_direction_retention"]
        )
        <= 1e-10,
        "both_minimum_edge_worst_direction_retention_at_least_0_99": min(
            flat["minimum_edge_worst_direction_retention"],
            curved["minimum_edge_worst_direction_retention"],
        )
        >= 0.99,
        "both_holonomies_preserve_orientation": (
            not flat["orientation_reversal_flag"]
            and not curved["orientation_reversal_flag"]
        ),
        "flat_phase_at_most_1e_8_degrees": abs(flat["holonomy_phase_degrees"])
        <= 1e-8,
        "curved_phase_at_least_45_degrees": (
            curved["holonomy_phase_degrees"] is not None
            and abs(curved["holonomy_phase_degrees"]) >= 45.0
        ),
        "curved_signed_return_below_0_60": curved["mean_signed_monitor_return"]
        < 0.60,
        "block_energy_is_preserved": abs(flat["block_energy_return"] - 1.0)
        <= 1e-10
        and abs(curved["block_energy_return"] - 1.0) <= 1e-10,
    }
    receipt = {
        "experiment": "monitor_holonomy_matched_local_lineage_control",
        "receipt_version": "v0.3",
        "status": "passed" if all(gates.values()) else "failed",
        "claim_boundary": (
            "Synthetic Grassmannian identifiability control only. It shows that "
            "local principal-angle lineage does not determine global signed-"
            "coordinate transport; it is not evidence of transformer monitor drift."
        ),
        "flat": flat,
        "curved": curved,
        "gates": gates,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
