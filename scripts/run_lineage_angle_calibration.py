"""Run the registered multi-seed lineage-angle standing calibration."""

from __future__ import annotations

import importlib.metadata
import json
import math
import os
import platform
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.discovery import (  # noqa: E402
    DiscoveryConfig,
    discover_consensus_bands,
    evaluate_discovery,
    subspace_lineage,
)
from rsi_topology.synthetic import build_fixture  # noqa: E402


SEEDS = (20260711, 20260712, 20260713)
DEGREES = tuple(range(0, 91, 5))
OUTPUT = Path("artifacts/lineage_angle_calibration_v0_1.json")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


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


def planted_overlap(planted: np.ndarray, basis: np.ndarray) -> float:
    if basis.shape[1] == 0:
        return 0.0
    return float(np.linalg.norm(planted.T @ basis, ord="fro") ** 2 / basis.shape[1])


def fixture(seed: int, degrees: int):
    return build_fixture(
        seed=seed,
        contexts=4,
        candidates_per_context=24,
        dimension=24,
        planted_rank=6,
        geometry_noise=0.08,
        lineage_rotation_radians=math.radians(degrees),
    )


def evaluate(value, config: DiscoveryConfig):
    return evaluate_discovery(
        laplacians=value.laplacians,
        vectors=value.vectors,
        baseline_covariates=value.baseline_covariates,
        outcomes=value.outcomes,
        groups=value.groups,
        config=config,
    )


def main() -> None:
    if os.environ.get("RSI_TOPOLOGY_HARD_CAPS_ENFORCED") != "1":
        raise RuntimeError(
            "Refusing uncapped calibration. Use scripts/run_capped_discovery_wsl.sh."
        )
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite calibration receipt: {OUTPUT}")

    config = DiscoveryConfig(
        minimum_consensus_rank=4,
        maximum_consensus_rank=12,
        chunk_rows=24,
    )
    receipt = {
        "protocol_id": "rsi-topology-lineage-angle-calibration-v0.1",
        "status": "running",
        "claim_boundary": (
            "Synthetic multi-seed shape calibration only. Gate-flip locations "
            "are fixture constants and must not become real-model thresholds."
        ),
        "environment": environment(),
        "configuration": {
            "seeds": list(SEEDS),
            "rotation_degrees": list(DEGREES),
            "dimension": 24,
            "planted_rank": 6,
            "contexts": 4,
            "candidates_per_context": 24,
            "geometry_noise": 0.08,
        },
        "rows": [],
    }

    for seed in SEEDS:
        reference_fixture = fixture(seed, 0)
        reference_bands = discover_consensus_bands(reference_fixture.laplacians, config)
        reference_low = reference_bands["low"]
        reference_result = evaluate(reference_fixture, config)
        for degrees in DEGREES:
            current_fixture = (
                reference_fixture if degrees == 0 else fixture(seed, degrees)
            )
            current_bands = discover_consensus_bands(current_fixture.laplacians, config)
            current_low = current_bands["low"]
            current_result = (
                reference_result if degrees == 0 else evaluate(current_fixture, config)
            )
            same_shape = reference_low.occupancies.shape == current_low.occupancies.shape
            occupancy_difference = (
                float(
                    np.max(
                        np.abs(
                            reference_low.occupancies - current_low.occupancies
                        )
                    )
                )
                if same_shape
                else None
            )
            lineage = subspace_lineage(reference_low.basis, current_low.basis)
            cosine_squared = float(math.cos(math.radians(degrees)) ** 2)
            selected_band = current_result.geometry.get("selected_band")
            reference_band = reference_result.geometry.get("selected_band")
            receipt["rows"].append(
                {
                    "seed": seed,
                    "rotation_degrees": degrees,
                    "selected_band": selected_band,
                    "reference_selected_band": reference_band,
                    "selection_stability_warning": selected_band != reference_band,
                    "rank": current_low.rank,
                    "minimum_occupancy": current_low.minimum_occupancy,
                    "band_occupancy_margins": current_result.geometry.get(
                        "band_occupancy_margins"
                    ),
                    "maximum_occupancy_spectrum_difference": occupancy_difference,
                    "candidate_vectors_identical": bool(
                        np.array_equal(
                            reference_fixture.vectors, current_fixture.vectors
                        )
                    ),
                    "outcomes_identical": bool(
                        np.array_equal(
                            reference_fixture.outcomes, current_fixture.outcomes
                        )
                    ),
                    "lineage": lineage,
                    "cos2": cosine_squared,
                    "absolute_chordal_cos2_error": abs(
                        lineage["mean_chordal_lineage"] - cosine_squared
                    ),
                    "planted_overlap_synthetic_only": planted_overlap(
                        current_fixture.planted_basis, current_low.basis
                    ),
                    "policy_standardized_uplift": current_result.policy.get(
                        "mean_standardized_heldout_return_uplift"
                    ),
                    "policy_passed": current_result.policy["passed"],
                    "edit_passed": current_result.direct_edit["passed"],
                }
            )
            write_json(OUTPUT, receipt)

    summaries = {}
    for seed in SEEDS:
        rows = [row for row in receipt["rows"] if row["seed"] == seed]
        summaries[str(seed)] = {
            "selected_band_stable": not any(
                row["selection_stability_warning"] for row in rows
            ),
            "rank_stable": len({row["rank"] for row in rows}) == 1,
            "maximum_occupancy_spectrum_difference": max(
                row["maximum_occupancy_spectrum_difference"] for row in rows
            ),
            "lineage_monotone_nonincreasing": all(
                left["lineage"]["mean_chordal_lineage"]
                >= right["lineage"]["mean_chordal_lineage"]
                for left, right in zip(rows, rows[1:])
            ),
            "maximum_absolute_chordal_cos2_error": max(
                row["absolute_chordal_cos2_error"] for row in rows
            ),
            "policy_last_pass_degrees": max(
                (row["rotation_degrees"] for row in rows if row["policy_passed"]),
                default=None,
            ),
            "edit_last_pass_degrees": max(
                (row["rotation_degrees"] for row in rows if row["edit_passed"]),
                default=None,
            ),
        }
    receipt["summaries"] = summaries
    receipt["construction_invariants_passed"] = all(
        summary["selected_band_stable"]
        and summary["rank_stable"]
        and summary["maximum_occupancy_spectrum_difference"] <= 1e-10
        for summary in summaries.values()
    )
    receipt["status"] = "completed"
    write_json(OUTPUT, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
