"""Run the registered perimeter-noise versus area-curvature control."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.holonomy import evaluate_perimeter_area_control  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path("protocols/monitor_holonomy_noise_null_v0_2.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/monitor_holonomy_noise_null_v0_2.json"),
    )
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite receipt: {args.output}")

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    geometry = protocol["geometry"]
    noise = protocol["noise"]
    thresholds = protocol["gates"]
    result = evaluate_perimeter_area_control(
        steps_grid=tuple(geometry["steps_grid"]),
        step_size=float(geometry["step_size"]),
        noise_scale=float(noise["scale"]),
        replicates=int(noise["replicates"]),
        seed=int(noise["seed"]),
        matched_minimum_worst_direction_retention=float(
            noise["matched_minimum_edge_worst_direction_retention_target"]
        ),
    )
    curvature_fit = result["curvature_phase_vs_area_fit"]
    noise_fit = result["noise_variance_vs_perimeter_fit"]
    gates = {
        "curvature_area_law": curvature_fit["r_squared"]
        >= float(thresholds["minimum_curvature_area_r_squared"]),
        "noise_perimeter_law": noise_fit["r_squared"]
        >= float(thresholds["minimum_noise_perimeter_r_squared"]),
        "matched_local_lineage": result[
            "reference_worst_direction_retention_absolute_error"
        ]
        <= float(thresholds["maximum_reference_lineage_absolute_error"]),
        "positive_scaling_slopes": curvature_fit["slope"] > 0.0
        and noise_fit["slope"] > 0.0,
        "analytic_origin_rate_match": result[
            "curvature_fit_slope_relative_error_from_analytic_origin"
        ]
        <= float(thresholds["maximum_area_fit_relative_error_from_analytic_origin"]),
        "no_orientation_reversal_in_registered_control": all(
            row["orientation_reversal_count"] == 0
            for row in result["noise_rows"]
        )
        and all(
            row["holonomy_determinant"] > 0.0
            for row in result["curvature_rows"]
        ),
    }
    receipt = {
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": sha256_file(args.protocol),
        "status": "passed" if all(gates.values()) else "failed",
        "gates": gates,
        "result": result,
        "canonical_summary": protocol["primary_statistics"][
            "higher_rank_summary"
        ],
        "signed_transport_rule": protocol["signed_transport_rule"],
        "claim_boundary": protocol["claim_boundary"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
