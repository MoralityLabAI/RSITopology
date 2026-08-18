"""Run the sealed Ultra transient-amplification synthetic experiment."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from fractions import Fraction
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rsi_topology.ultra.transient_amplification import (  # noqa: E402
    boundary_decision,
    classify_jordan_radius,
    departure_from_normality,
    finite_horizon_gain,
    jordan_chain,
    jordan_exact_gain_bounds,
    maximum_sampled_gain,
    metric_norm,
    normal_control,
    reframe_operator,
    sample_metric_unit_directions,
    spectral_radius,
    worst_case_trajectory,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def write_once(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != content:
            raise FileExistsError(f"refusing to replace non-identical artifact: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def git_text(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def tracked_diff_sha256() -> str:
    result = subprocess.run(
        ["git", "diff", "--binary", "HEAD", "--"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return hashlib.sha256(result.stdout).hexdigest()


def sorted_eigenvalue_discrepancy(left: np.ndarray, right: np.ndarray) -> float:
    left_values = np.sort_complex(np.linalg.eigvals(left))
    right_values = np.sort_complex(np.linalg.eigvals(right))
    return float(np.max(np.abs(left_values - right_values)))


def registered_reframes(
    dimension: int,
    count: int,
    *,
    seed: int,
    condition_number: float,
) -> list[np.ndarray]:
    """Generate fixed-condition-number coordinate maps from seeded Haar frames."""

    rng = np.random.default_rng(seed)
    singular_values = np.geomspace(1.0, condition_number, dimension)
    transforms = []
    for _ in range(count):
        left, _ = np.linalg.qr(rng.normal(size=(dimension, dimension)))
        right, _ = np.linalg.qr(rng.normal(size=(dimension, dimension)))
        transforms.append(left @ np.diag(singular_values) @ right.T)
    return transforms


def run(protocol_path: Path, amendment_path: Path, output: Path) -> dict[str, Any]:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    amendment = json.loads(amendment_path.read_text(encoding="utf-8"))
    fixture = protocol["primary_fixture"]
    probe_spec = protocol["registered_direction_probes"]
    reframe_spec = amendment["metric_covariance_reframes"]

    dimension = int(fixture["dimension"])
    decay = float(fixture["decay_eigenvalue"])
    horizon = int(fixture["horizon"])
    initial_radius = float(fixture["initial_radius"])
    safety_radius = float(fixture["safety_radius"])
    couplings = [float(value) for value in fixture["coupling_grid"]]
    identity_metric = np.eye(dimension)
    control = normal_control(dimension, decay)

    rows: list[dict[str, Any]] = []
    reframe_manifest: list[dict[str, Any]] = []
    maximum_reframe_error = 0.0
    maximum_witness_error = 0.0
    maximum_probe_excess = 0.0
    for coupling_index, coupling in enumerate(couplings):
        operator = jordan_chain(dimension, decay, coupling)
        exact_bounds = jordan_exact_gain_bounds(
            dimension,
            Fraction(str(decay)),
            Fraction(str(coupling)),
            horizon,
        )
        certified_decision = classify_jordan_radius(
            exact_bounds,
            initial_radius=Fraction(str(initial_radius)),
            safety_radius=Fraction(str(safety_radius)),
        )
        gain = finite_horizon_gain(operator, horizon, metric=identity_metric)
        trajectory = worst_case_trajectory(
            operator,
            gain,
            initial_radius=initial_radius,
        )
        witness_radius = metric_norm(trajectory[-1], identity_metric)
        predicted_radius = initial_radius * gain.gain
        witness_error = abs(witness_radius - predicted_radius)
        maximum_witness_error = max(maximum_witness_error, witness_error)

        directions = sample_metric_unit_directions(
            dimension,
            int(probe_spec["count_per_matrix"]),
            seed=int(probe_spec["seed"]) + coupling_index,
            metric=identity_metric,
        )
        sampled_gain, sampled_time, _ = maximum_sampled_gain(
            operator,
            directions,
            horizon,
            metric=identity_metric,
        )
        probe_excess = max(0.0, sampled_gain - gain.gain)
        maximum_probe_excess = max(maximum_probe_excess, probe_excess)

        reframe_errors = []
        for reframe_index, coordinate_map in enumerate(
            registered_reframes(
                dimension,
                int(reframe_spec["count_per_matrix"]),
                seed=int(reframe_spec["seed"]) + 1000 * coupling_index,
                condition_number=float(reframe_spec["condition_number"]),
            )
        ):
            matrix_hash = hashlib.sha256(
                np.asarray(coordinate_map, dtype="<f8", order="C").tobytes(order="C")
            ).hexdigest()
            reframe_manifest.append(
                {
                    "coupling": coupling,
                    "reframe_index": reframe_index,
                    "seed": int(reframe_spec["seed"]) + 1000 * coupling_index,
                    "sha256_float64_c_order": matrix_hash,
                    "condition_number": float(np.linalg.cond(coordinate_map)),
                }
            )
            reframed, reframed_metric = reframe_operator(
                operator,
                identity_metric,
                coordinate_map,
            )
            reframed_gain = finite_horizon_gain(
                reframed,
                horizon,
                metric=reframed_metric,
            )
            relative_error = abs(reframed_gain.gain - gain.gain) / max(gain.gain, 1.0)
            reframe_errors.append(relative_error)
            maximum_reframe_error = max(maximum_reframe_error, relative_error)

        radius = spectral_radius(operator)
        spectral_pass = radius < 1.0
        rows.append(
            {
                "coupling": coupling,
                "spectral_radius": radius,
                "spectral_gate_pass": spectral_pass,
                "finite_horizon_gain": gain.gain,
                "maximizing_time": gain.maximizing_time,
                "predicted_worst_radius": predicted_radius,
                "certified_lower_gain": float(
                    np.sqrt(float(exact_bounds.lower_gain_squared))
                ),
                "certified_lower_gain_squared_fraction": (
                    f"{exact_bounds.lower_gain_squared.numerator}/"
                    f"{exact_bounds.lower_gain_squared.denominator}"
                ),
                "certified_upper_gain": float(exact_bounds.upper_gain),
                "certified_upper_gain_fraction": (
                    f"{exact_bounds.upper_gain.numerator}/"
                    f"{exact_bounds.upper_gain.denominator}"
                ),
                "certified_radius_decision": certified_decision,
                "spectral_declared_radius_miss": (
                    spectral_pass and certified_decision == "fail"
                ),
                "sampled_direction_gain": sampled_gain,
                "sampled_maximizing_time": sampled_time,
                "sampled_to_exact_ratio": sampled_gain / gain.gain,
                "witness_absolute_error": witness_error,
                "eigenvalue_discrepancy": sorted_eigenvalue_discrepancy(
                    operator, control
                ),
                "departure_from_normality": departure_from_normality(operator),
                "maximum_metric_reframe_relative_error": max(reframe_errors),
                "reframe_count": len(reframe_errors),
            }
        )

    tolerances = amendment["clarified_gates"]
    sensitivity_coupling = Fraction(
        str(amendment["metric_relative_only"]["registered_witness_coupling"])
    )
    sensitivity_scaled = sensitivity_coupling * Fraction(3, 4)
    sensitivity_original_bounds = jordan_exact_gain_bounds(
        dimension, Fraction(str(decay)), sensitivity_coupling, horizon
    )
    sensitivity_scaled_bounds = jordan_exact_gain_bounds(
        dimension, Fraction(str(decay)), sensitivity_scaled, horizon
    )
    sensitivity_original_decision = classify_jordan_radius(
        sensitivity_original_bounds,
        initial_radius=Fraction(str(initial_radius)),
        safety_radius=Fraction(str(safety_radius)),
    )
    sensitivity_scaled_decision = classify_jordan_radius(
        sensitivity_scaled_bounds,
        initial_radius=Fraction(str(initial_radius)),
        safety_radius=Fraction(str(safety_radius)),
    )
    gate_results = {
        "G0_eigenvalue_match": {
            "pass": max(row["eigenvalue_discrepancy"] for row in rows)
            <= float(tolerances["G0_eigenvalue_match_tolerance"]),
            "maximum_discrepancy": max(
                row["eigenvalue_discrepancy"] for row in rows
            ),
        },
        "G1_exact_witness": {
            "pass": maximum_witness_error
            <= float(tolerances["G1_witness_absolute_tolerance"]),
            "maximum_absolute_error": maximum_witness_error,
        },
        "G2_probe_consistency": {
            "pass": maximum_probe_excess
            <= float(tolerances["G2_probe_upper_tolerance"]),
            "maximum_sampled_gain_minus_exact_gain": maximum_probe_excess,
            "universal_decision_source": "top_singular_vector",
        },
        "G3_spectral_blind_spot": {
            "pass": all(row["spectral_gate_pass"] for row in rows)
            and any(row["spectral_declared_radius_miss"] for row in rows)
            and any(row["certified_radius_decision"] == "pass" for row in rows),
            "spectral_declared_radius_miss_count": sum(
                bool(row["spectral_declared_radius_miss"]) for row in rows
            ),
            "certified_pass_count": sum(
                row["certified_radius_decision"] == "pass" for row in rows
            ),
            "certified_fail_count": sum(
                row["certified_radius_decision"] == "fail" for row in rows
            ),
            "numerically_indeterminate_count": sum(
                row["certified_radius_decision"] == "numerically_indeterminate"
                for row in rows
            ),
        },
        "G4_metric_covariance": {
            "pass": maximum_reframe_error
            <= float(tolerances["G4_relative_tolerance"]),
            "maximum_relative_error": maximum_reframe_error,
        },
        "G5_metric_relative_only": {
            "pass": sensitivity_original_decision == "fail"
            and sensitivity_scaled_decision == "pass",
            "euclidean_decision": sensitivity_original_decision,
            "alternative_metric_decision": sensitivity_scaled_decision,
            "alternative_metric_condition_number": float((Fraction(4, 3) ** 14)),
        },
    }
    overall = all(record["pass"] for record in gate_results.values())

    output.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    per_coupling_path = output / "per_coupling.csv"
    write_once(per_coupling_path, buffer.getvalue().encode("utf-8"))

    reframe_manifest_path = output / "reframe_manifest.json"
    write_once(
        reframe_manifest_path,
        canonical_json(
            {
                "schema": "ultra_metric_reframe_manifest_v0_1",
                "serialization": reframe_spec["matrix_serialization"],
                "records": reframe_manifest,
            }
        ).encode("utf-8"),
    )

    summary = {
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": sha256_file(protocol_path),
        "amendment_id": amendment["amendment_id"],
        "amendment_sha256": sha256_file(amendment_path),
        "instrument_status": "valid" if overall else "invalid",
        "evidence_layers": {
            "mathematical_theorem": "proved_in_claim_packet",
            "deterministic_fixture_calibration": "pass" if overall else "invalid",
            "application_hypothesis": "untested",
        },
        "gate_results": gate_results,
        "first_certified_failure_coupling": next(
            (
                row["coupling"]
                for row in rows
                if row["certified_radius_decision"] == "fail"
            ),
            None,
        ),
        "claim_boundary": protocol["scientific_scope"],
    }
    summary_path = output / "summary.json"
    write_once(summary_path, canonical_json(summary).encode("utf-8"))

    figure_path = output / "transient_phase.png"
    figure, left_axis = plt.subplots(figsize=(8.0, 4.8), constrained_layout=True)
    x = np.asarray([row["coupling"] for row in rows])
    worst_radius = np.asarray([row["predicted_worst_radius"] for row in rows])
    lower_radius = initial_radius * np.asarray(
        [row["certified_lower_gain"] for row in rows]
    )
    upper_radius = initial_radius * np.asarray(
        [row["certified_upper_gain"] for row in rows]
    )
    left_axis.fill_between(
        x,
        lower_radius,
        upper_radius,
        color="#d95f02",
        alpha=0.18,
        label="rigorous gain bracket",
    )
    left_axis.plot(x, worst_radius, marker="o", color="#d95f02", label="float64 SVD estimate")
    left_axis.axhline(
        safety_radius,
        color="#8b1a1a",
        linestyle="--",
        label="declared radius",
    )
    left_axis.axhspan(0.0, safety_radius, color="#3b8c6e", alpha=0.08)
    left_axis.set_xlabel("non-normal coupling kappa")
    left_axis.set_ylabel("worst state radius through T=40")
    left_axis.set_title("Matched eigenvalues, different finite-horizon radius decisions")
    right_axis = left_axis.twinx()
    right_axis.plot(
        x,
        [row["spectral_radius"] for row in rows],
        color="#3366aa",
        linestyle=":",
        label="spectral radius",
    )
    right_axis.set_ylabel("spectral radius")
    right_axis.set_ylim(0.0, 1.05)
    handles_left, labels_left = left_axis.get_legend_handles_labels()
    handles_right, labels_right = right_axis.get_legend_handles_labels()
    left_axis.legend(handles_left + handles_right, labels_left + labels_right, loc="upper left")
    figure_buffer = BytesIO()
    figure.savefig(figure_buffer, format="png", dpi=180, metadata={"Software": "RSITopology Ultra"})
    plt.close(figure)
    write_once(figure_path, figure_buffer.getvalue())

    runner_path = Path(__file__).resolve()
    receipt = {
        "receipt_schema": "ultra_transient_amplification_receipt_v0_1",
        "protocol_sha256": sha256_file(protocol_path),
        "amendment_sha256": sha256_file(amendment_path),
        "runner_sha256": sha256_file(runner_path),
        "source_module_sha256": sha256_file(
            REPO_ROOT / "rsi_topology" / "ultra" / "transient_amplification.py"
        ),
        "git_commit_at_run": git_text("rev-parse", "HEAD"),
        "git_tracked_diff_sha256_at_run": tracked_diff_sha256(),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
            "platform": platform.platform(),
        },
        "artifacts": {
            "per_coupling.csv": sha256_file(per_coupling_path),
            "reframe_manifest.json": sha256_file(reframe_manifest_path),
            "summary.json": sha256_file(summary_path),
            "transient_phase.png": sha256_file(figure_path),
        },
        "overall_gate_pass": overall,
    }
    receipt_path = output / "receipt.json"
    write_once(receipt_path, canonical_json(receipt).encode("utf-8"))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--amendment", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args.protocol, args.amendment, args.output)
    print(canonical_json(summary), end="")


if __name__ == "__main__":
    main()
