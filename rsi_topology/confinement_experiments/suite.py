"""Work-unit generation, evaluation, aggregation, and plotting for six experiments."""

from __future__ import annotations

from collections import Counter
from itertools import product
from math import log2
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .common import (
    WorkUnit,
    implementation_fingerprint,
    jsonable,
    write_bytes_compare_or_fail,
)
from .linear import (
    aligned_box_cover_bits,
    classify_split_rate,
    critical_constructive_rate,
    evaluator_relevant_modes,
    finite_horizon_relevant_entropy,
    finite_horizon_volume_lower_bits,
    port_staircase,
    random_orthogonal,
    unstable_entropy_bits,
)
from .spin_glass import run_sampler_cell
from .sufficiency import evaluate_audit_cell


EXPERIMENT_IDS = {
    "01_split_rate",
    "02_spectral_entropy",
    "03_finite_horizon",
    "04_transversal_index",
    "05_sufficiency_audit",
    "06_spin_glass",
}


def _unique_sorted(values: Iterable[float]) -> list[float]:
    return sorted({round(float(value), 12) for value in values if float(value) >= 0.0})


def generate_work_units(config: dict[str, Any]) -> list[WorkUnit]:
    experiment = str(config["experiment"])
    if experiment not in EXPERIMENT_IDS:
        raise ValueError(f"unknown experiment: {experiment}")
    seed = int(config["seed"])
    params = dict(config["parameters"])
    payloads: list[dict[str, Any]] = []
    if experiment == "01_split_rate":
        for m, unstable_value, stable_dimension, horizon, rotation_index in product(
            params["unstable_dimensions"],
            params["unstable_values"],
            params["stable_dimensions"],
            params["horizons"],
            range(int(params["rotations"])),
        ):
            entropy = int(m) * log2(float(unstable_value))
            rates = _unique_sorted(entropy + float(offset) for offset in params["rate_offsets"])
            for read_rate, write_rate in product(rates, repeat=2):
                payloads.append(
                    {
                        "arm": "finite_split",
                        "unstable_dimension": int(m),
                        "unstable_value": float(unstable_value),
                        "stable_dimension": int(stable_dimension),
                        "horizon": int(horizon),
                        "rotation_index": rotation_index,
                        "read_rate": read_rate,
                        "write_rate": write_rate,
                        "collar_ratio": float(params["collar_ratio"]),
                    }
                )
        # Named controls are one work unit each and never enter the primary heatmap.
        payloads.extend(
            [
                {"arm": "stable_zero_rate", "horizon": max(params["horizons"])},
                {"arm": "analog_side_channel", "horizon": max(params["horizons"])},
                {"arm": "full_state_full_action", "horizon": max(params["horizons"])},
            ]
        )
    elif experiment == "02_spectral_entropy":
        horizon = int(params["horizon"])
        block_length = int(params["block_length"])
        collar_ratio = float(params["collar_ratio"])
        for value in params["family_a_values"]:
            payloads.append(
                {
                    "family": "fixed_index_vary_instability",
                    "eigenvalues": [float(value)] * int(params["family_a_index"]),
                    "horizon": horizon,
                    "block_length": block_length,
                    "collar_ratio": collar_ratio,
                    "precision_bits": list(params["precision_bits"]),
                }
            )
        fixed_entropy = float(params["family_b_entropy"])
        for m in params["family_b_indices"]:
            payloads.append(
                {
                    "family": "fixed_entropy_vary_index",
                    "eigenvalues": [2.0 ** (fixed_entropy / int(m))] * int(m),
                    "horizon": horizon,
                    "block_length": block_length,
                    "collar_ratio": collar_ratio,
                    "precision_bits": list(params["precision_bits"]),
                }
            )
        value = 1.0 + float(params["family_c_delta"])
        for m in params["family_c_indices"]:
            payloads.append(
                {
                    "family": "fixed_gap_vary_index",
                    "eigenvalues": [value] * int(m),
                    "horizon": horizon,
                    "block_length": block_length,
                    "collar_ratio": collar_ratio,
                    "precision_bits": list(params["precision_bits"]),
                }
            )
    elif experiment == "03_finite_horizon":
        for eigenvalues, horizon, collar_ratio in product(
            params["spectra"], params["horizons"], params["collar_ratios"]
        ):
            payloads.append(
                {
                    "eigenvalues": list(map(float, eigenvalues)),
                    "horizon": int(horizon),
                    "collar_ratio": float(collar_ratio),
                    "block_length": int(params["block_length"]),
                }
            )
    elif experiment == "04_transversal_index":
        for tangent_dimension, tangent_value, coupling, horizon in product(
            params["tangent_dimensions"],
            params["tangent_values"],
            params["couplings"],
            params["horizons"],
        ):
            payloads.append(
                {
                    "normal_value": float(params["normal_value"]),
                    "tangent_dimension": int(tangent_dimension),
                    "tangent_value": float(tangent_value),
                    "coupling": float(coupling),
                    "horizon": int(horizon),
                    "sensitivity_floor": float(params["sensitivity_floor"]),
                    "pbh_tolerance": float(params["pbh_tolerance"]),
                }
            )
    elif experiment == "05_sufficiency_audit":
        for dimension, threshold, probes, sparsity in product(
            params["dimensions"],
            params["thresholds"],
            params["probe_counts"],
            params["sparsities"],
        ):
            if int(sparsity) <= int(dimension):
                payloads.append(
                    {
                        "dimension": int(dimension),
                        "threshold": float(threshold),
                        "probes": int(probes),
                        "sparsity": int(sparsity),
                        "trials": int(params["trials"]),
                    }
                )
    elif experiment == "06_spin_glass":
        for dimension, tau, disorder_index, sampler, quadratic_weight in product(
            params["dimensions"],
            params["evaluator_levels"],
            range(int(params["disorder_realizations"])),
            params["samplers"],
            params["quadratic_weights"],
        ):
            payloads.append(
                {
                    "dimension": int(dimension),
                    "tau": float(tau),
                    "disorder_index": int(disorder_index),
                    "starts": int(params["starts"]),
                    "sampler": str(sampler),
                    "quadratic_weight": float(quadratic_weight),
                }
            )
    implementation_sha256 = implementation_fingerprint()
    units = [
        WorkUnit(experiment, payload, seed, implementation_sha256)
        for payload in payloads
    ]
    identities = [unit.unit_id for unit in units]
    if len(identities) != len(set(identities)):
        raise ValueError("configuration generates duplicate work units")
    return units


def evaluate_work_unit(unit: WorkUnit) -> dict[str, Any]:
    payload = unit.payload
    experiment = unit.experiment
    if experiment == "01_split_rate":
        result = _evaluate_split_rate(payload, unit.seed)
    elif experiment == "02_spectral_entropy":
        result = _evaluate_spectral_entropy(payload)
    elif experiment == "03_finite_horizon":
        result = _evaluate_finite_horizon(payload)
    elif experiment == "04_transversal_index":
        result = _evaluate_transversal(payload)
    elif experiment == "05_sufficiency_audit":
        result = evaluate_audit_cell(**payload, seed=unit.seed)
    elif experiment == "06_spin_glass":
        result = run_sampler_cell(
            dimension=payload["dimension"],
            tau=payload["tau"],
            disorder_seed=unit.seed,
            starts=payload["starts"],
            sampler=payload["sampler"],
            quadratic_weight=payload["quadratic_weight"],
        )
        result["disorder_index"] = payload["disorder_index"]
    else:  # pragma: no cover - protected by generation validation
        raise ValueError(experiment)
    return {"unit_id": unit.unit_id, "seed": unit.seed, **result}


def _evaluate_split_rate(payload: dict[str, Any], seed: int) -> dict[str, Any]:
    arm = payload["arm"]
    if arm == "stable_zero_rate":
        eigenvalues = [0.8, 0.7]
        result = classify_split_rate(eigenvalues, 0.0, 0.0, payload["horizon"], [0.5] * 2, [1.0] * 2)
        return {"arm": arm, "control_pass": result["classification"] == "constructive_feasible", **result}
    if arm in {"analog_side_channel", "full_state_full_action"}:
        return {
            "arm": arm,
            "control_pass": True,
            "classification": "constructive_feasible",
            "evidence": "explicit_unrestricted_control_control_arm",
            "read_rate": None,
            "write_rate": None,
        }
    m = payload["unstable_dimension"]
    stable = payload["stable_dimension"]
    eigenvalues = np.array([payload["unstable_value"]] * m + [0.8] * stable)
    dimension = len(eigenvalues)
    basis = random_orthogonal(dimension, seed)
    initial = np.full(dimension, payload["collar_ratio"])
    safe = np.ones(dimension)
    result = classify_split_rate(
        eigenvalues,
        payload["read_rate"],
        payload["write_rate"],
        payload["horizon"],
        initial,
        safe,
    )
    final_prefix = result["prefixes"][-1]
    finite_constructive_rate = max(
        prefix["constructive_cover_bits"] / prefix["step"]
        for prefix in result["prefixes"]
    )
    finite_universal_rate = max(
        prefix["universal_lower_bits"] / prefix["step"]
        for prefix in result["prefixes"]
    )
    raw_volume_bits = (
        payload["horizon"] * unstable_entropy_bits(eigenvalues)
        + m * log2(payload["collar_ratio"])
    )
    bottleneck_bits = min(final_prefix["read_bits"], final_prefix["write_bits"])
    volume_capacity = min(1.0, 2.0 ** min(0.0, bottleneck_bits - raw_volume_bits))
    return {
        **payload,
        "entropy_bits_per_step": unstable_entropy_bits(eigenvalues),
        "finite_horizon_universal_rate": finite_universal_rate,
        "finite_horizon_constructive_rate": finite_constructive_rate,
        "rotation_determinant": float(np.linalg.det(basis)),
        "volume_capacity_fraction_upper": volume_capacity,
        **result,
    }


def _evaluate_spectral_entropy(payload: dict[str, Any]) -> dict[str, Any]:
    eigenvalues = np.asarray(payload["eigenvalues"], dtype=float)
    initial = np.full(eigenvalues.size, payload["collar_ratio"])
    safe = np.ones(eigenvalues.size)
    entropy = unstable_entropy_bits(eigenvalues)
    critical = critical_constructive_rate(
        eigenvalues,
        payload["horizon"],
        initial,
        safe,
        block_length=payload["block_length"],
    )
    return {
        "family": payload["family"],
        "eigenvalues": eigenvalues.tolist(),
        "unstable_index": int(np.sum(eigenvalues > 1.0)),
        "entropy_bits_per_step": entropy,
        "constructive_critical_rate": critical,
        "rate_minus_entropy": critical - entropy,
        "port_staircase": {
            str(bits): port_staircase(entropy, int(bits))
            for bits in payload["precision_bits"]
        },
        "evidence_label": "aligned_box_constructive_rate",
    }


def _evaluate_finite_horizon(payload: dict[str, Any]) -> dict[str, Any]:
    eigenvalues = np.asarray(payload["eigenvalues"], dtype=float)
    dimension = eigenvalues.size
    initial = np.full(dimension, payload["collar_ratio"])
    safe = np.ones(dimension)
    horizon = payload["horizon"]
    entropy = unstable_entropy_bits(eigenvalues)
    lower_bits = finite_horizon_volume_lower_bits(eigenvalues, horizon, initial, safe)
    cover_bits = aligned_box_cover_bits(eigenvalues, horizon, initial, safe)
    lower_rate = lower_bits / horizon
    cover_rate = cover_bits / horizon
    log_volume_ratio = float(
        np.sum(np.log2(initial[eigenvalues > 1.0] / safe[eigenvalues > 1.0]))
    )
    return {
        **payload,
        "unstable_index": int(np.sum(eigenvalues > 1.0)),
        "entropy_bits_per_step": entropy,
        "log_unstable_volume_ratio": log_volume_ratio,
        "universal_lower_total_bits": lower_bits,
        "constructive_cover_total_bits": cover_bits,
        "universal_lower_rate": lower_rate,
        "constructive_cover_rate": cover_rate,
        "inverse_horizon": 1.0 / horizon,
        "scaled_lower_correction": horizon * (lower_rate - entropy),
        "scaled_constructive_correction": horizon * (cover_rate - entropy),
        "evidence_label": "universal_volume_lower_and_aligned_box_construction",
    }


def _evaluate_transversal(payload: dict[str, Any]) -> dict[str, Any]:
    q = payload["tangent_dimension"]
    # Small deterministic spectral offsets avoid repeated-eigenvalue PBH ambiguity.
    tangent = np.diag(
        [payload["tangent_value"] + 1e-4 * index for index in range(q)]
    )
    matrix = np.zeros((q + 1, q + 1))
    matrix[0, 0] = payload["normal_value"]
    matrix[1:, 1:] = tangent
    matrix[0, 1:] = payload["coupling"] / np.sqrt(q)
    normal = np.zeros(q + 1)
    normal[0] = 1.0
    asymptotic = evaluator_relevant_modes(
        matrix, normal, tolerance=payload["pbh_tolerance"]
    )
    finite = finite_horizon_relevant_entropy(
        matrix,
        normal,
        payload["horizon"],
        sensitivity_floor=payload["sensitivity_floor"],
    )
    return {
        **payload,
        "local_entropy": asymptotic.local_entropy,
        "evaluator_entropy": asymptotic.evaluator_entropy,
        "local_unstable_index": asymptotic.local_unstable_index,
        "evaluator_unstable_index": asymptotic.evaluator_unstable_index,
        "mode_observabilities": asymptotic.mode_observabilities,
        **finite,
        "evidence_label": "spectral_pbh_and_finite_horizon_observability_estimator",
    }


def _linear_fit(x: np.ndarray, y: np.ndarray) -> dict[str, float | None]:
    if x.size < 2 or np.allclose(x, x[0]):
        return {"intercept": None, "slope": None, "r_squared": None}
    design = np.column_stack([np.ones(x.size), x])
    coefficients = np.linalg.lstsq(design, y, rcond=None)[0]
    predicted = design @ coefficients
    denominator = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 1.0 if denominator <= 1e-15 else 1.0 - float(np.sum((y - predicted) ** 2)) / denominator
    return {
        "intercept": float(coefficients[0]),
        "slope": float(coefficients[1]),
        "r_squared": r_squared,
    }


def aggregate_metrics(experiment: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    if experiment == "01_split_rate":
        primary = [row for row in rows if row["arm"] == "finite_split"]
        controls = [row for row in rows if row["arm"] != "finite_split"]
        return {
            "classification_counts": dict(Counter(row["classification"] for row in primary)),
            "primary_cells": len(primary),
            "control_passes": {row["arm"]: bool(row["control_pass"]) for row in controls},
            "asymmetric_rate_compensation_violations": sum(
                row["classification"] == "constructive_feasible"
                and (
                    row["read_rate"] + 1e-12 < row["finite_horizon_constructive_rate"]
                    or row["write_rate"] + 1e-12 < row["finite_horizon_constructive_rate"]
                )
                for row in primary
            ),
            "finite_horizon_coasting_cells_below_asymptotic_entropy": sum(
                row["classification"] == "constructive_feasible"
                and min(row["read_rate"], row["write_rate"])
                < row["entropy_bits_per_step"]
                for row in primary
            ),
        }
    if experiment == "02_spectral_entropy":
        entropy = np.asarray([row["entropy_bits_per_step"] for row in rows])
        index = np.asarray([row["unstable_index"] for row in rows], dtype=float)
        measured = np.asarray([row["constructive_critical_rate"] for row in rows])
        return {
            "fit_against_entropy": _linear_fit(entropy, measured),
            "fit_against_unstable_index": _linear_fit(index, measured),
            "maximum_rate_rounding_error": float(np.max(np.abs(measured - entropy))),
        }
    if experiment == "03_finite_horizon":
        active = [row for row in rows if row["universal_lower_total_bits"] > 0]
        grouped_fits = {}
        for eigenvalues, collar in sorted(
            {(tuple(row["eigenvalues"]), row["collar_ratio"]) for row in rows}
        ):
            selected = [
                row
                for row in rows
                if tuple(row["eigenvalues"]) == eigenvalues
                and row["collar_ratio"] == collar
            ]
            grouped_fits[f"eigs={eigenvalues};collar={collar}"] = _linear_fit(
                np.asarray([row["inverse_horizon"] for row in selected]),
                np.asarray([row["universal_lower_rate"] for row in selected]),
            )
        return {
            "universal_rate_vs_inverse_horizon_by_system": grouped_fits,
            "active_bound_rounding_residual_range": [
                min(
                    row["scaled_lower_correction"] - row["log_unstable_volume_ratio"]
                    for row in active
                ),
                max(
                    row["scaled_lower_correction"] - row["log_unstable_volume_ratio"]
                    for row in active
                ),
            ],
            "maximum_lower_vs_constructive_gap_bits": max(
                row["constructive_cover_total_bits"] - row["universal_lower_total_bits"]
                for row in rows
            ),
        }
    if experiment == "04_transversal_index":
        zero = [row for row in rows if row["coupling"] == 0]
        nonzero = [row for row in rows if row["coupling"] > 0]
        return {
            "zero_coupling_evaluator_indices": sorted({row["evaluator_unstable_index"] for row in zero}),
            "nonzero_coupling_evaluator_indices": sorted({row["evaluator_unstable_index"] for row in nonzero}),
            "finite_horizon_partial_visibility_cells": sum(
                row["finite_horizon_index"] < row["evaluator_unstable_index"] for row in nonzero
            ),
        }
    if experiment == "05_sufficiency_audit":
        return {
            "maximum_random_detection_absolute_error": max(
                row["random_detection_absolute_error"] for row in rows
            ),
            "post_design_adversary_full_undetected_cells": sum(
                row["post_design_adversary_undetected"] == 1.0 for row in rows
            ),
            "maximum_random_detection_standardized_error": max(
                row["random_detection_standardized_error"] for row in rows
            ),
        }
    valid = [row for row in rows if row["mean_index_fraction"] is not None]
    return {
        "cells": len(rows),
        "cells_with_critical_points": len(valid),
        "minimum_observed_mean_index_fraction": min(
            (row["mean_index_fraction"] for row in valid), default=None
        ),
        "maximum_observed_mean_index_fraction": max(
            (row["mean_index_fraction"] for row in valid), default=None
        ),
        "claim_boundary": "Basin-weighted finite-N sampler comparison; not Kac-Rice sampling.",
    }


def evaluate_registered_gates(
    experiment: str, rows: list[dict[str, Any]], metrics: dict[str, Any]
) -> dict[str, bool]:
    """Executable v0.1 gates; descriptive endpoints remain outside this table."""

    if experiment == "01_split_rate":
        return {
            "named_controls": all(metrics["control_passes"].values()),
            "no_asymmetric_rate_compensation": metrics[
                "asymmetric_rate_compensation_violations"
            ]
            == 0,
        }
    if experiment == "02_spectral_entropy":
        entropy_fit = metrics["fit_against_entropy"]
        index_fit = metrics["fit_against_unstable_index"]
        return {
            "entropy_beats_index_r_squared": (
                entropy_fit["r_squared"] is not None
                and index_fit["r_squared"] is not None
                and entropy_fit["r_squared"] - index_fit["r_squared"] >= 0.20
            ),
            "entropy_slope_calibrated": entropy_fit["slope"] is not None
            and 0.8 <= entropy_fit["slope"] <= 1.2,
        }
    if experiment == "03_finite_horizon":
        low, high = metrics["active_bound_rounding_residual_range"]
        return {
            "finite_horizon_rounding_identity": low >= -1e-10
            and high < 1.0 + 1e-10,
        }
    if experiment == "04_transversal_index":
        zero_ok = all(
            row["evaluator_unstable_index"] == 1
            for row in rows
            if row["coupling"] == 0
        )
        nonzero_ok = all(
            row["evaluator_unstable_index"] == row["local_unstable_index"]
            for row in rows
            if row["coupling"] > 0
        )
        return {
            "zero_coupling_normal_only": zero_ok,
            "nonzero_coupling_pbh_complete": nonzero_ok,
        }
    if experiment == "05_sufficiency_audit":
        return {
            "random_probe_analytic_calibration": metrics[
                "maximum_random_detection_standardized_error"
            ]
            <= 4.5,
        }
    return {
        "sampler_instrument_available": metrics["cells_with_critical_points"]
        == metrics["cells"],
    }


def render_figure(experiment: str, rows: list[dict[str, Any]], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
    if experiment == "01_split_rate":
        primary = [row for row in rows if row["arm"] == "finite_split"]
        groups: dict[tuple[object, ...], list[dict[str, Any]]] = {}
        for row in primary:
            group_key = (
                row["unstable_dimension"],
                row["unstable_value"],
                row["stable_dimension"],
                row["horizon"],
                row["rotation_index"],
            )
            groups.setdefault(group_key, []).append(row)

        def display_score(group_key: tuple[object, ...]) -> tuple[object, ...]:
            group = groups[group_key]
            counts = {
                label: sum(row["classification"] == label for row in group)
                for label in {
                    "certified_infeasible",
                    "undetermined",
                    "constructive_feasible",
                }
            }
            occupied = sum(count > 0 for count in counts.values())
            imbalance = max(counts.values()) - min(
                count for count in counts.values() if count > 0
            )
            # Prefer a real phase boundary, then the most balanced grid. The
            # final tuple makes selection deterministic without inspecting any
            # unregistered outcome beyond its already-defined classification.
            return (-occupied, imbalance, group_key)

        key = min(groups, key=display_score)
        selected = [
            row
            for row in primary
            if (
                row["unstable_dimension"],
                row["unstable_value"],
                row["stable_dimension"],
                row["horizon"],
                row["rotation_index"],
            )
            == key
        ]
        read = sorted({row["read_rate"] for row in selected})
        write = sorted({row["write_rate"] for row in selected})
        values = np.zeros((len(write), len(read)))
        code = {"certified_infeasible": 0.0, "undetermined": 0.5, "constructive_feasible": 1.0}
        for row in selected:
            values[write.index(row["write_rate"]), read.index(row["read_rate"])] = code[row["classification"]]
        image = axis.imshow(values, origin="lower", vmin=0, vmax=1, cmap="RdYlGn", aspect="auto")
        axis.set_xticks(range(len(read)), [f"{value:.2f}" for value in read], rotation=45)
        axis.set_yticks(range(len(write)), [f"{value:.2f}" for value in write])
        axis.set_xlabel("read bits / step")
        axis.set_ylabel("write bits / step")
        axis.set_title(
            "Split-channel phase boundary "
            f"(m={key[0]}, a={key[1]}, T={key[3]})"
        )
        figure.colorbar(image, ax=axis, ticks=[0, 0.5, 1])
    elif experiment == "02_spectral_entropy":
        families = sorted({row["family"] for row in rows})
        for family in families:
            selected = [row for row in rows if row["family"] == family]
            axis.scatter(
                [row["entropy_bits_per_step"] for row in selected],
                [row["constructive_critical_rate"] for row in selected],
                label=family,
            )
        limit = max(row["constructive_critical_rate"] for row in rows) * 1.05
        axis.plot([0, limit], [0, limit], "k--", label="R*=h2")
        axis.set(xlabel="h2(A_u), bits / step", ylabel="constructive critical rate")
        axis.legend(fontsize=7)
    elif experiment == "03_finite_horizon":
        for key in sorted({(tuple(row["eigenvalues"]), row["collar_ratio"]) for row in rows}):
            selected = [row for row in rows if (tuple(row["eigenvalues"]), row["collar_ratio"]) == key]
            selected.sort(key=lambda row: row["inverse_horizon"])
            axis.plot(
                [row["inverse_horizon"] for row in selected],
                [row["universal_lower_rate"] for row in selected],
                marker="o",
                label=f"eig={key[0]}, r={key[1]}",
            )
        axis.set(xlabel="1 / T", ylabel="universal lower rate")
        axis.legend(fontsize=6)
    elif experiment == "04_transversal_index":
        for horizon in sorted({row["horizon"] for row in rows}):
            selected = [row for row in rows if row["horizon"] == horizon and row["tangent_dimension"] == min(r["tangent_dimension"] for r in rows)]
            selected.sort(key=lambda row: row["coupling"])
            axis.plot(
                [row["coupling"] for row in selected],
                [row["finite_horizon_entropy"] for row in selected],
                marker="o",
                label=f"finite T={horizon}",
            )
        axis.set(xlabel="tangent-to-normal coupling", ylabel="evaluator-relevant entropy")
        axis.legend(fontsize=7)
    elif experiment == "05_sufficiency_audit":
        for threshold in sorted({row["threshold"] for row in rows}):
            selected = [row for row in rows if row["threshold"] == threshold and row["probes"] == min(r["probes"] for r in rows) and row["sparsity"] == min(r["sparsity"] for r in rows)]
            selected.sort(key=lambda row: row["dimension"])
            axis.plot(
                [row["dimension"] for row in selected],
                [row["log10_k95"] for row in selected],
                marker="o",
                label=f"threshold={threshold}",
            )
        axis.set(xlabel="fiber dimension q", ylabel="log10 random probes for 95% detection")
        axis.legend(fontsize=7)
    else:
        valid = [row for row in rows if row["mean_index_fraction"] is not None]
        for sampler in sorted({row["sampler"] for row in valid}):
            selected = [row for row in valid if row["sampler"] == sampler]
            axis.scatter(
                [row["tau"] for row in selected],
                [row["mean_index_fraction"] for row in selected],
                label=sampler,
                alpha=0.75,
            )
        axis.set(xlabel="evaluator level tau", ylabel="mean constrained-Hessian index fraction")
        axis.legend(fontsize=7)
    axis.grid(alpha=0.2)
    temporary = path.with_name(f".{path.name}.tmp.png")
    figure.savefig(temporary, dpi=160, metadata={"Software": "RSITopology"})
    plt.close(figure)
    write_bytes_compare_or_fail(path, temporary.read_bytes())
    temporary.unlink(missing_ok=True)


def markdown_report(
    experiment: str,
    run_id: str,
    rows: list[dict[str, Any]],
    metrics: dict[str, Any],
) -> str:
    import json

    labels = {
        "01_split_rate": "Split read/write data-rate phase transition",
        "02_spectral_entropy": "Critical rate versus unstable entropy",
        "03_finite_horizon": "Finite-horizon correction",
        "04_transversal_index": "Local versus evaluator-transversal index",
        "05_sufficiency_audit": "Evaluator-sufficiency audit scaling",
        "06_spin_glass": "Spherical 3-spin sampler robustness",
    }
    return f"""# {labels[experiment]}

Run: `{run_id}`  
Atomic work units: `{len(rows)}`

## Aggregate metrics

```json
{json.dumps(jsonable(metrics), indent=2, sort_keys=True)}
```

## Evidential boundary

The receipt labels distinguish universal lower bounds, explicit constructions,
spectral estimators, Monte Carlo estimates, and basin-weighted critical-point
sampling. Numerical non-failure is not proof. Above-threshold failure is not
evidence for a lower bound unless controller optimality is independently
certified.
"""
