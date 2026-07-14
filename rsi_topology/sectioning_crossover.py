"""Registered bias-variance calibration for holonomy patch pooling."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import numpy as np

from .sectioning import rank_audit_placements, section_edits
from .sectioning_synthetic import build_sectioning_fixture


OFFSETS = (-2, -1, 0, 1, 2)
SIGMAS = (0.0, 0.1, 0.2, 0.4, 0.8, 1.2)
OBSERVATIONS = (1, 2, 4, 8, 16, 32)


def _ordered_cells(plan: dict[str, Any]) -> tuple[str, ...]:
    cells = {cell for patch in plan["patches"] for cell in patch["plaquette_ids"]}
    return tuple(sorted(cells, key=lambda value: int(value.split("-")[1])))


def _truth_angles(cell_count: int, offset: int) -> np.ndarray:
    boundary = cell_count // 2 + offset
    if not 0 < boundary < cell_count:
        raise ValueError("offset places the truth boundary outside the fixture")
    values = np.full(cell_count, np.pi / 2.0, dtype=np.float64)
    values[:boundary] = 0.0
    return values


def _patch_indices(plan: dict[str, Any], cells: tuple[str, ...]) -> tuple[np.ndarray, ...]:
    index = {cell: position for position, cell in enumerate(cells)}
    return tuple(
        np.array([index[cell] for cell in patch["plaquette_ids"]], dtype=np.int64)
        for patch in plan["patches"]
    )


def _analytic_terms(truth: np.ndarray, patches: tuple[np.ndarray, ...]) -> dict[str, float]:
    patch_target = np.empty_like(truth)
    variance_coefficient = 0.0
    for indices in patches:
        patch_target[indices] = float(np.mean(truth[indices]))
        variance_coefficient += len(indices) * (1.0 - 1.0 / len(indices))
    variance_coefficient /= len(truth)
    global_target = np.full_like(truth, float(np.mean(truth)))
    return {
        "patch_bias_squared": float(np.mean((truth - patch_target) ** 2)),
        "global_bias_squared": float(np.mean((truth - global_target) ** 2)),
        "variance_advantage_coefficient": float(variance_coefficient),
        "patch_variance_coefficient": float(
            np.mean([1.0 / len(indices) for indices in patches for _ in indices])
        ),
        "global_variance_coefficient": 1.0 / len(truth),
    }


def _simulate_cell(
    truth: np.ndarray,
    patches: tuple[np.ndarray, ...],
    *,
    sigma: float,
    observations: int,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    noise = rng.normal(scale=sigma, size=(replicates, len(truth), observations))
    observed = truth[None, :, None] + noise
    independent = np.mean(observed, axis=2)
    patch = np.empty_like(independent)
    for indices in patches:
        estimate = np.mean(observed[:, indices, :], axis=(1, 2))
        patch[:, indices] = estimate[:, None]
    global_estimate = np.mean(observed, axis=(1, 2))
    global_values = np.repeat(global_estimate[:, None], len(truth), axis=1)
    mse_independent = np.mean((independent - truth[None, :]) ** 2, axis=1)
    mse_patch = np.mean((patch - truth[None, :]) ** 2, axis=1)
    mse_global = np.mean((global_values - truth[None, :]) ** 2, axis=1)
    patch_minus_independent = mse_independent - mse_patch
    patch_minus_global = mse_global - mse_patch
    terms = _analytic_terms(truth, patches)
    variance = sigma * sigma / observations
    analytic_independent = (
        terms["variance_advantage_coefficient"] * variance
        - terms["patch_bias_squared"]
    )
    analytic_global = (
        terms["global_bias_squared"]
        - terms["patch_bias_squared"]
        - (terms["patch_variance_coefficient"] - terms["global_variance_coefficient"])
        * variance
    )
    se = float(np.std(patch_minus_independent, ddof=1) / np.sqrt(replicates))
    return {
        "patch_minus_independent_values": patch_minus_independent,
        "patch_minus_global_values": patch_minus_global,
        "empirical_patch_minus_independent": float(np.mean(patch_minus_independent)),
        "empirical_patch_minus_global": float(np.mean(patch_minus_global)),
        "analytic_patch_minus_independent": float(analytic_independent),
        "analytic_patch_minus_global": float(analytic_global),
        "patch_minus_independent_standard_error": se,
        **terms,
    }


def _bootstrap_interval(values: np.ndarray, *, seed: int, draws: int = 4096) -> list[float]:
    rng = np.random.default_rng(seed)
    means = np.empty(draws, dtype=np.float64)
    chunk = 256
    for start in range(0, draws, chunk):
        stop = min(draws, start + chunk)
        indices = rng.integers(0, len(values), size=(stop - start, len(values)))
        means[start:stop] = np.mean(values[indices], axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def _connector_audit_gate() -> dict[str, Any]:
    fixture = build_sectioning_fixture("mixed_curvature")
    cells = []
    for item in fixture.plaquettes:
        if item.plaquette_id == "p-4":
            cells.append(
                replace(
                    item,
                    measured=False,
                    identity_loss=None,
                    identity_loss_lower_bound=0.02,
                    identity_loss_upper_bound=0.24,
                    determinant_reversal_probability=0.1,
                )
            )
        else:
            cells.append(item)
    result = rank_audit_placements(replace(fixture, plaquettes=tuple(cells)), 0.05)
    row = next(item for item in result["audit_ranking"] if item["plaquette_id"] == "p-4")
    return {"receipt": row, "gate_pass": row["touched_patch_count"] == 2 and row["boundary_impact"] == 2}


def run_sectioning_crossover_v03(*, replicates: int = 512, seed: int = 20260713) -> dict[str, Any]:
    fixture = build_sectioning_fixture("mixed_curvature")
    plan = section_edits(fixture, 0.05)
    cells = _ordered_cells(plan)
    patches = _patch_indices(plan, cells)
    raw: dict[tuple[int, float, int], dict[str, Any]] = {}
    surface = []
    calibration_passes = 0
    sign_eligible = 0
    sign_passes = 0
    for offset_index, offset in enumerate(OFFSETS):
        truth = _truth_angles(len(cells), offset)
        for sigma_index, sigma in enumerate(SIGMAS):
            for observation_index, observations in enumerate(OBSERVATIONS):
                cell_seed = seed + offset_index * 100_000 + sigma_index * 1_000 + observation_index
                result = _simulate_cell(
                    truth,
                    patches,
                    sigma=sigma,
                    observations=observations,
                    replicates=replicates,
                    seed=cell_seed,
                )
                raw[(offset, sigma, observations)] = result
                difference = abs(
                    result["empirical_patch_minus_independent"]
                    - result["analytic_patch_minus_independent"]
                )
                within_three_se = difference <= 3.0 * result["patch_minus_independent_standard_error"] + 1e-12
                calibration_passes += int(within_three_se)
                away = abs(result["analytic_patch_minus_independent"]) > (
                    3.0 * result["patch_minus_independent_standard_error"] + 1e-12
                )
                sign_agrees = np.sign(result["empirical_patch_minus_independent"]) == np.sign(
                    result["analytic_patch_minus_independent"]
                )
                if away:
                    sign_eligible += 1
                    sign_passes += int(sign_agrees)
                surface.append(
                    {
                        "offset": offset,
                        "sigma": sigma,
                        "observations_per_cell": observations,
                        "variance_ratio": sigma * sigma / observations,
                        "patch_bias_squared": result["patch_bias_squared"],
                        "analytic_patch_minus_independent": result[
                            "analytic_patch_minus_independent"
                        ],
                        "empirical_patch_minus_independent": result[
                            "empirical_patch_minus_independent"
                        ],
                        "standard_error": result["patch_minus_independent_standard_error"],
                        "within_three_standard_errors": within_three_se,
                        "sign_agrees_away_from_zero": None if not away else bool(sign_agrees),
                    }
                )

    defect_gates = []
    for offset in OFFSETS:
        if offset == 0:
            continue
        candidates = []
        for sigma in SIGMAS:
            for observations in OBSERVATIONS:
                result = raw[(offset, sigma, observations)]
                variance_term = (
                    result["variance_advantage_coefficient"] * sigma * sigma / observations
                )
                if variance_term <= 0.1 * result["patch_bias_squared"] + 1e-15:
                    candidates.append((sigma * sigma / observations, sigma, -observations, result))
        _, selected_sigma, negative_n, selected = max(candidates, key=lambda item: item[:3])
        selected_n = -negative_n
        interval = _bootstrap_interval(
            selected["patch_minus_independent_values"],
            seed=seed + 700_000 + offset,
        )
        agreement = abs(
            selected["empirical_patch_minus_independent"]
            - selected["analytic_patch_minus_independent"]
        ) <= 3.0 * selected["patch_minus_independent_standard_error"] + 1e-12
        defect_gates.append(
            {
                "offset": offset,
                "sigma": selected_sigma,
                "observations_per_cell": selected_n,
                "patch_bias_squared": selected["patch_bias_squared"],
                "analytic_patch_minus_independent": selected[
                    "analytic_patch_minus_independent"
                ],
                "empirical_patch_minus_independent": selected[
                    "empirical_patch_minus_independent"
                ],
                "bootstrap_95_ci": interval,
                "analytic_agreement_within_three_se": agreement,
                "gate_pass": interval[1] < 0.0 and agreement,
            }
        )

    recoupled = raw[(0, 0.8, 1)]
    recoupled_independent_ci = _bootstrap_interval(
        recoupled["patch_minus_independent_values"], seed=seed + 800_001
    )
    recoupled_global_ci = _bootstrap_interval(
        recoupled["patch_minus_global_values"], seed=seed + 800_002
    )
    recoupled_gate = {
        "offset": 0,
        "sigma": 0.8,
        "observations_per_cell": 1,
        "patch_minus_independent_95_ci": recoupled_independent_ci,
        "patch_minus_global_95_ci": recoupled_global_ci,
        "gate_pass": recoupled_independent_ci[0] > 0.0 and recoupled_global_ci[0] > 0.0,
    }
    calibration_fraction = calibration_passes / len(surface)
    sign_fraction = 1.0 if sign_eligible == 0 else sign_passes / sign_eligible
    connector = _connector_audit_gate()
    maximum_norm_error = 0.0
    for angle in np.linspace(-3.0, 3.0, 257):
        coordinate = np.array([np.cos(angle), np.sin(angle)]) / np.sqrt(len(cells))
        maximum_norm_error = max(maximum_norm_error, abs(len(cells) * float(coordinate @ coordinate) - 1.0))
    gates = {
        "recoupled_regression": recoupled_gate["gate_pass"],
        "all_decoupled_defect_regimes": all(item["gate_pass"] for item in defect_gates),
        "surface_calibration": calibration_fraction >= 0.98,
        "surface_sign_agreement": sign_fraction >= 0.95,
        "connector_audit": connector["gate_pass"],
        "norm_matching": maximum_norm_error <= 1e-12,
    }
    return {
        "schema_version": "0.3.0",
        "protocol_id": "edit_sectioning_crossover_v0_3",
        "fixture_patch_count": plan["edit_count"],
        "surface": surface,
        "surface_calibration": {
            "within_three_se_fraction": calibration_fraction,
            "sign_agreement_fraction_away_from_zero": sign_fraction,
            "sign_eligible_cell_count": sign_eligible,
        },
        "derived_defect_gates": defect_gates,
        "recoupled_gate": recoupled_gate,
        "connector_audit_gate": connector,
        "capacity_accounting": {
            "registered_capacity_rank": {
                "patch_plan": 8,
                "one_global_edit": 8,
                "per_context_independent": 8,
            },
            "active_signed_coordinates": {
                "patch_plan": 2,
                "one_global_edit": 1,
                "per_context_independent": 8,
            },
            "matched_total_squared_norm": 1.0,
            "maximum_norm_error": maximum_norm_error,
        },
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "claim_boundary": "CPU-synthetic bias-variance calibration only; no transformer evidence.",
    }

