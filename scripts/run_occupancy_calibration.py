from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.discovery import DiscoveryConfig, evaluate_discovery
from rsi_topology.synthetic import build_fixture


DEFAULT_NOISE = (0.015, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.5)
DEFAULT_SEEDS = (20260711, 20260712, 20260713)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the v0.2.2 dense occupancy calibration control."
    )
    parser.add_argument(
        "--out-dir", type=Path, default=Path("artifacts/occupancy_calibration_v0_2_1")
    )
    parser.add_argument("--noise", type=float, nargs="*", default=list(DEFAULT_NOISE))
    parser.add_argument("--seeds", type=int, nargs="*", default=list(DEFAULT_SEEDS))
    parser.add_argument("--candidates-per-context", type=int, default=96)
    parser.add_argument("--chunk-rows", type=int, default=64)
    return parser.parse_args()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def environment() -> dict:
    return {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("numpy", "scipy", "scikit-learn")
        },
    }


def main() -> int:
    args = parse_args()
    if not args.noise or not args.seeds:
        raise ValueError("noise grid and seeds must be nonempty")
    if any(value < 0 for value in args.noise):
        raise ValueError("geometry noise must be nonnegative")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    config = DiscoveryConfig(chunk_rows=args.chunk_rows)
    receipt = {
        "protocol_id": "rsi-topology-spectral-bundle-v0.2.2",
        "status": "running",
        "claim_boundary": "Dense synthetic occupancy calibration only; no model weights or real outcomes.",
        "environment": environment(),
        "configuration": {
            "dimension": 48,
            "planted_rank": 12,
            "contexts": 10,
            "candidates_per_context": args.candidates_per_context,
            "noise_grid": args.noise,
            "seeds": args.seeds,
            "chunk_rows": args.chunk_rows,
        },
        "rows": [],
    }
    checkpoint = args.out_dir / "occupancy_calibration.json"
    for noise in args.noise:
        for seed in args.seeds:
            fixture = build_fixture(
                seed=seed,
                contexts=10,
                candidates_per_context=args.candidates_per_context,
                dimension=48,
                planted_rank=12,
                geometry_noise=noise,
            )
            result = evaluate_discovery(
                laplacians=fixture.laplacians,
                vectors=fixture.vectors,
                baseline_covariates=fixture.baseline_covariates,
                outcomes=fixture.outcomes,
                groups=fixture.groups,
                config=config,
            )
            receipt["rows"].append(
                {
                    "noise": noise,
                    "seed": seed,
                    "geometry_passed": result.geometry["passed"],
                    "selected_band": result.geometry.get("selected_band"),
                    "rank": result.geometry.get("selected_rank", 0),
                    "minimum_occupancy": result.geometry.get("minimum_occupancy", 0.0),
                    "occupancy_margin": result.geometry.get(
                        "consensus_occupancy_margin"
                    ),
                    "low_margin_warning": result.geometry.get(
                        "low_occupancy_margin_warning"
                    ),
                    "occupancy_margin_band": result.geometry.get(
                        "occupancy_margin_band"
                    ),
                    "band_occupancy_margins": result.geometry.get(
                        "band_occupancy_margins"
                    ),
                    "policy_passed": result.policy["passed"],
                    "policy_standardized_uplift": result.policy.get(
                        "mean_standardized_heldout_return_uplift"
                    ),
                    "policy_mean_realized_ic": result.policy.get("mean_realized_ic"),
                    "direct_edit_passed": result.direct_edit["passed"],
                }
            )
            write_json(checkpoint, receipt)
    positive_noise = [float(value) for value in args.noise if value > 0]
    reference_noise = min(positive_noise) if positive_noise else min(args.noise)
    references = {
        int(row["seed"]): row.get("selected_band")
        for row in receipt["rows"]
        if float(row["noise"]) == reference_noise
    }
    for row in receipt["rows"]:
        reference_band = references.get(int(row["seed"]))
        row["reference_noise"] = reference_noise
        row["reference_selected_band"] = reference_band
        row["selection_stable"] = bool(
            reference_band is not None
            and row.get("selected_band") == reference_band
        )
        row["selection_stability_warning"] = not row["selection_stable"]
        row["lineage_serialization_required"] = row[
            "selection_stability_warning"
        ]
    warning_count = sum(
        bool(row["selection_stability_warning"]) for row in receipt["rows"]
    )
    receipt["selection_stability_warning_count"] = warning_count
    receipt["lineage_serialization_complete"] = warning_count == 0
    receipt["status"] = (
        "completed"
        if warning_count == 0
        else "completed_engineering_evidence_lineage_required"
    )
    write_json(checkpoint, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
