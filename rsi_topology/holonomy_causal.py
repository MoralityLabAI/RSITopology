"""Causal path-transfer falsification controls for holonomy diagnostics.

The static holonomy controls establish that pairwise principal-angle lineage
does not determine a globally consistent signed coordinate.  This module adds
the next, deliberately model-free rung: carry the same root edit to one target
along two paths, apply a frozen Lipschitz causal response, and test whether the
measured loop displacement predicts the disagreement.

Nothing here is transformer evidence.  The fixture is useful because the
geometry, causal map, gauge action, and control-loss bound are all known, so a
failure identifies the instrument or analysis rather than an unknown model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .holonomy import (
    build_grassmann_loop,
    canonical_rotation_angles_degrees,
    holonomy_orientation_receipt,
    loop_holonomy,
    procrustes_transport,
)
from .risk_gate import (
    ControlRiskMeasurement,
    EdgeRiskReceipt,
    LoopRiskReceipt,
    predict_control_gate,
)


Array = np.ndarray


@dataclass(frozen=True)
class PathPair:
    """Two root-to-target transports and the induced rooted loop closure."""

    forward: Array
    backward: Array
    holonomy: Array
    target_index: int
    path_edge_count: int


def _direct_sum(left: Array, right: Array) -> Array:
    left_value = np.asarray(left, dtype=np.float64)
    right_value = np.asarray(right, dtype=np.float64)
    output = np.zeros(
        (
            left_value.shape[0] + right_value.shape[0],
            left_value.shape[1] + right_value.shape[1],
        ),
        dtype=np.float64,
    )
    output[: left_value.shape[0], : left_value.shape[1]] = left_value
    output[left_value.shape[0] :, left_value.shape[1] :] = right_value
    return output


def build_rank_four_loop(
    condition: str,
    *,
    steps: int,
    step_size: float,
) -> tuple[Array, ...]:
    """Return a flat-flat or curved-flat direct-sum Grassmann loop."""

    if condition not in {"flat_flat", "curved_flat"}:
        raise ValueError("condition must be flat_flat or curved_flat")
    flat = build_grassmann_loop("flat", steps=steps, step_size=step_size)
    first = (
        flat
        if condition == "flat_flat"
        else build_grassmann_loop("curved", steps=steps, step_size=step_size)
    )
    if first.points != flat.points:
        raise ValueError("direct-sum loop blocks do not share a boundary grid")
    return tuple(
        _direct_sum(first_frame, flat_frame)
        for first_frame, flat_frame in zip(first.frames, flat.frames)
    )


def _compose_forward(frames: Sequence[Array], indices: Sequence[int]) -> Array:
    if len(indices) < 2:
        raise ValueError("a path needs at least one edge")
    rank = np.asarray(frames[0]).shape[1]
    product = np.eye(rank, dtype=np.float64)
    for source_index, target_index in zip(indices[:-1], indices[1:]):
        transport, _ = procrustes_transport(
            frames[source_index], frames[target_index]
        )
        product = transport @ product
    return product


def two_path_transports(frames: Sequence[Array]) -> PathPair:
    """Transport root coordinates to the opposite loop vertex two ways."""

    values = tuple(np.asarray(frame, dtype=np.float64) for frame in frames)
    if len(values) < 4 or len(values) % 2:
        raise ValueError("the registered boundary needs an even vertex count")
    target = len(values) // 2
    forward_indices = tuple(range(0, target + 1))
    backward_indices = (0,) + tuple(range(len(values) - 1, target - 1, -1))
    forward = _compose_forward(values, forward_indices)
    backward = _compose_forward(values, backward_indices)
    rooted_holonomy = backward.T @ forward
    measured = loop_holonomy(values).matrix
    if not np.allclose(rooted_holonomy, measured, atol=1e-9):
        raise ValueError("two-path convention disagrees with registered loop order")
    return PathPair(
        forward=forward,
        backward=backward,
        holonomy=rooted_holonomy,
        target_index=target,
        path_edge_count=target,
    )


def _unit(value: Array) -> Array:
    vector = np.asarray(value, dtype=np.float64)
    norm = float(np.linalg.norm(vector))
    if not np.isfinite(norm) or norm <= 1e-14:
        raise ValueError("direction must have nonzero finite norm")
    return vector / norm


def _directions(pair: PathPair, rng: np.random.Generator) -> dict[str, Array]:
    difference = pair.forward - pair.backward
    _, _, right_t = np.linalg.svd(difference)
    return {
        "maximally_exposed": _unit(right_t[0]),
        "seeded_haar": _unit(rng.normal(size=difference.shape[1])),
        "minimally_exposed": _unit(right_t[-1]),
    }


def _causal_map(
    *,
    rank: int,
    output_dimension: int,
    replicate: int,
    seed: int,
) -> tuple[Array, float]:
    rng = np.random.default_rng(seed + 100_003 * replicate)
    value = rng.normal(size=(output_dimension, rank))
    spectral = float(np.linalg.svd(value, compute_uv=False)[0])
    target_norm = float(rng.uniform(0.75, 1.5))
    value *= target_norm / spectral
    return value, target_norm


def _response(causal_map: Array, coordinate: Array) -> Array:
    return np.tanh(causal_map @ coordinate)


def _loop_metrics(frames: Sequence[Array]) -> dict[str, Any]:
    measured = loop_holonomy(frames)
    orientation = holonomy_orientation_receipt(measured.matrix)
    angles = (
        None
        if orientation["orientation_reversal_flag"]
        else list(canonical_rotation_angles_degrees(measured.matrix))
    )
    return {
        "minimum_edge_worst_direction_retention": (
            measured.minimum_edge_worst_direction_retention
        ),
        "mean_edge_chordal_lineage": measured.mean_edge_chordal_lineage,
        "det_h": orientation["holonomy_determinant"],
        "orientation_flag": orientation["orientation_reversal_flag"],
        "canonical_angles_degrees": angles,
        "maximum_canonical_angle_degrees": (
            None if angles is None else float(max(angles, default=0.0))
        ),
    }


def generate_causal_transfer_rows(
    *,
    step_sizes: Sequence[float],
    steps_per_side: int,
    causal_map_replicates: int,
    causal_output_dimension: int,
    edit_norms: Sequence[float],
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Generate the frozen causal path-transfer population."""

    if causal_map_replicates < 6:
        raise ValueError("at least six causal-map groups are required")
    rows: list[dict[str, Any]] = []
    loop_receipts: list[dict[str, Any]] = []
    for step_index, raw_step_size in enumerate(step_sizes):
        step_size = float(raw_step_size)
        condition_cache: dict[str, tuple[tuple[Array, ...], PathPair, dict]] = {}
        for condition in ("flat_flat", "curved_flat"):
            frames = build_rank_four_loop(
                condition, steps=steps_per_side, step_size=step_size
            )
            pair = two_path_transports(frames)
            metrics = _loop_metrics(frames)
            condition_cache[condition] = (frames, pair, metrics)
            loop_receipts.append(
                {
                    "loop_id": f"{condition}-step-{step_index:02d}",
                    "condition": condition,
                    "step_size": step_size,
                    "path_edge_count": pair.path_edge_count,
                    **metrics,
                }
            )

        for replicate in range(causal_map_replicates):
            causal_map, lipschitz = _causal_map(
                rank=4,
                output_dimension=causal_output_dimension,
                replicate=replicate,
                seed=seed,
            )
            for condition_index, condition in enumerate(("flat_flat", "curved_flat")):
                frames, pair, metrics = condition_cache[condition]
                direction_rng = np.random.default_rng(
                    seed
                    + step_index * 1_000_003
                    + replicate * 10_007
                    + condition_index * 101
                )
                for direction_class, direction in _directions(
                    pair, direction_rng
                ).items():
                    forward_unit = pair.forward @ direction
                    backward_unit = pair.backward @ direction
                    path_displacement = float(
                        np.linalg.norm(forward_unit - backward_unit)
                    )
                    holonomy_displacement = float(
                        np.linalg.norm((pair.holonomy - np.eye(4)) @ direction)
                    )
                    identity_error = abs(path_displacement - holonomy_displacement)
                    jacobian_visibility = 0.5 * float(
                        np.linalg.norm(causal_map @ forward_unit)
                        + np.linalg.norm(causal_map @ backward_unit)
                    )
                    for edit_norm in edit_norms:
                        norm = float(edit_norm)
                        forward_coordinate = norm * forward_unit
                        backward_coordinate = norm * backward_unit
                        response_disagreement = float(
                            np.linalg.norm(
                                _response(causal_map, forward_coordinate)
                                - _response(causal_map, backward_coordinate)
                            )
                        )
                        risk_bound = norm * lipschitz * path_displacement
                        rows.append(
                            {
                                "row_id": (
                                    f"s{step_index:02d}-m{replicate:03d}-"
                                    f"{condition}-{direction_class}-a{norm:g}"
                                ),
                                "causal_map_replicate": replicate,
                                "condition": condition,
                                "step_size": step_size,
                                "direction_class": direction_class,
                                "edit_norm": norm,
                                "causal_lipschitz_constant": lipschitz,
                                "jacobian_visibility": jacobian_visibility,
                                "minimum_edge_worst_direction_retention": metrics[
                                    "minimum_edge_worst_direction_retention"
                                ],
                                "mean_edge_chordal_lineage": metrics[
                                    "mean_edge_chordal_lineage"
                                ],
                                "path_edge_count": pair.path_edge_count,
                                "directional_path_displacement": path_displacement,
                                "holonomy_expression_absolute_error": identity_error,
                                "causal_risk_bound": risk_bound,
                                "maximum_canonical_angle_degrees": metrics[
                                    "maximum_canonical_angle_degrees"
                                ],
                                "det_h": metrics["det_h"],
                                "orientation_flag": metrics["orientation_flag"],
                                "downstream_response_disagreement": response_disagreement,
                                "bound_excess": response_disagreement - risk_bound,
                                "transported_energy_difference": abs(
                                    float(forward_coordinate @ forward_coordinate)
                                    - float(backward_coordinate @ backward_coordinate)
                                ),
                            }
                        )
    return rows, {"loop_receipts": loop_receipts}


def _design_pipeline(numeric: Sequence[str], categorical: Sequence[str]) -> Pipeline:
    transformer = ColumnTransformer(
        [
            ("numeric", StandardScaler(), list(numeric)),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(categorical),
            ),
        ],
        remainder="drop",
    )
    return Pipeline([("features", transformer), ("ridge", Ridge(alpha=1.0))])


def _matrix(rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> Array:
    return np.asarray(
        [[float(row[field]) for field in fields] for row in rows], dtype=np.float64
    )


def _oof_predictions(
    rows: Sequence[dict[str, Any]],
    *,
    numeric: Sequence[str],
    categorical: Sequence[str],
    target: str,
    groups: Array,
) -> Array:
    # ColumnTransformer accepts a dict-like table poorly without pandas.  A
    # compact object matrix preserves the declared column order and types.
    fields = tuple(numeric) + tuple(categorical)
    table = np.empty((len(rows), len(fields)), dtype=object)
    for row_index, row in enumerate(rows):
        for column_index, field in enumerate(fields):
            table[row_index, column_index] = row[field]
    numeric_indices = list(range(len(numeric)))
    categorical_indices = list(range(len(numeric), len(fields)))
    transformer = ColumnTransformer(
        [
            ("numeric", StandardScaler(), numeric_indices),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_indices,
            ),
        ],
        remainder="drop",
    )
    target_values = np.asarray([float(row[target]) for row in rows])
    predictions = np.empty(len(rows), dtype=np.float64)
    splitter = GroupKFold(n_splits=6)
    for train, test in splitter.split(table, target_values, groups):
        model = Pipeline(
            [("features", transformer), ("ridge", Ridge(alpha=1.0))]
        )
        model.fit(table[train], target_values[train])
        predictions[test] = model.predict(table[test])
    return predictions


def _bootstrap_relative_sse(
    rows: Sequence[dict[str, Any]],
    baseline_predictions: Array,
    augmented_predictions: Array,
    *,
    draws: int,
    seed: int,
) -> dict[str, Any]:
    outcomes = np.asarray(
        [float(row["downstream_response_disagreement"]) for row in rows]
    )
    groups = np.asarray([int(row["causal_map_replicate"]) for row in rows])
    unique = np.unique(groups)
    baseline_error = (outcomes - baseline_predictions) ** 2
    augmented_error = (outcomes - augmented_predictions) ** 2
    baseline_sse = float(np.sum(baseline_error))
    augmented_sse = float(np.sum(augmented_error))
    point = 1.0 - augmented_sse / max(baseline_sse, 1e-30)
    rng = np.random.default_rng(seed)
    samples = np.empty(draws, dtype=np.float64)
    group_baseline = np.asarray(
        [np.sum(baseline_error[groups == group]) for group in unique]
    )
    group_augmented = np.asarray(
        [np.sum(augmented_error[groups == group]) for group in unique]
    )
    for draw in range(draws):
        chosen = rng.integers(0, len(unique), size=len(unique))
        samples[draw] = 1.0 - float(np.sum(group_augmented[chosen])) / max(
            float(np.sum(group_baseline[chosen])), 1e-30
        )
    return {
        "baseline_sse": baseline_sse,
        "augmented_sse": augmented_sse,
        "relative_sse_reduction": float(point),
        "grouped_bootstrap_90_interval": [
            float(np.quantile(samples, 0.05)),
            float(np.quantile(samples, 0.95)),
        ],
        "grouped_bootstrap_draws": draws,
        "group_count": int(len(unique)),
    }


def _gauge_preflight(seed: int) -> dict[str, Any]:
    frames = build_rank_four_loop("curved_flat", steps=8, step_size=0.1)
    pair = two_path_transports(frames)
    direction = _directions(pair, np.random.default_rng(seed))["maximally_exposed"]
    causal_map, lipschitz = _causal_map(
        rank=4, output_dimension=6, replicate=0, seed=seed
    )
    rng = np.random.default_rng(seed + 77)
    gauges: list[Array] = []
    reframed: list[Array] = []
    for frame in frames:
        raw = rng.normal(size=(4, 4))
        gauge, triangular = np.linalg.qr(raw)
        signs = np.where(np.diag(triangular) >= 0.0, 1.0, -1.0)
        gauge = gauge * signs
        gauges.append(gauge)
        reframed.append(frame @ gauge)
    transformed = two_path_transports(reframed)
    root_direction = gauges[0].T @ direction
    target_gauge = gauges[pair.target_index]
    transformed_causal_map = causal_map @ target_gauge
    norm = 0.5
    original_forward = norm * pair.forward @ direction
    original_backward = norm * pair.backward @ direction
    changed_forward = norm * transformed.forward @ root_direction
    changed_backward = norm * transformed.backward @ root_direction
    original_response = float(
        np.linalg.norm(
            _response(causal_map, original_forward)
            - _response(causal_map, original_backward)
        )
    )
    changed_response = float(
        np.linalg.norm(
            _response(transformed_causal_map, changed_forward)
            - _response(transformed_causal_map, changed_backward)
        )
    )
    original_angles = canonical_rotation_angles_degrees(pair.holonomy)
    changed_angles = canonical_rotation_angles_degrees(transformed.holonomy)
    discrepancies = {
        "directional_path_displacement": abs(
            float(np.linalg.norm(pair.forward @ direction - pair.backward @ direction))
            - float(
                np.linalg.norm(
                    transformed.forward @ root_direction
                    - transformed.backward @ root_direction
                )
            )
        ),
        "response_disagreement": abs(original_response - changed_response),
        "canonical_angles": float(
            np.max(np.abs(np.asarray(original_angles) - np.asarray(changed_angles)))
        ),
        "determinant": abs(
            float(np.linalg.det(pair.holonomy))
            - float(np.linalg.det(transformed.holonomy))
        ),
        "risk_bound": abs(
            norm
            * lipschitz
            * float(np.linalg.norm(pair.forward @ direction - pair.backward @ direction))
            - norm
            * lipschitz
            * float(
                np.linalg.norm(
                    transformed.forward @ root_direction
                    - transformed.backward @ root_direction
                )
            )
        ),
    }
    return {
        "discrepancies": discrepancies,
        "maximum_discrepancy": float(max(discrepancies.values())),
    }


def _orientation_control(error_budget: float) -> dict[str, Any]:
    reflection = np.diag([-1.0, 1.0, 1.0, 1.0])
    orientation = holonomy_orientation_receipt(reflection)
    angle_suppressed = False
    try:
        canonical_rotation_angles_degrees(reflection)
    except ValueError:
        angle_suppressed = True
    measurement = ControlRiskMeasurement(
        measurement_id="orientation-reversal-control",
        edges=(EdgeRiskReceipt("edge-0", 1.0),),
        loop=LoopRiskReceipt(None, 0.0, True, True),
    )
    decision = predict_control_gate(measurement, error_budget)
    return {
        "det_h": orientation["holonomy_determinant"],
        "orientation_flag": orientation["orientation_reversal_flag"],
        "canonical_angles_suppressed": angle_suppressed,
        "authorized": decision["authorized"],
    }


def evaluate_causal_transfer(
    *,
    step_sizes: Sequence[float] = (0.02, 0.04, 0.06, 0.08, 0.1, 0.12),
    steps_per_side: int = 8,
    causal_map_replicates: int = 24,
    causal_output_dimension: int = 6,
    edit_norms: Sequence[float] = (0.1, 0.25, 0.5, 1.0),
    seed: int = 2026071602,
    bootstrap_draws: int = 4096,
    control_error_budget: float = 0.25,
) -> dict[str, Any]:
    """Run the registered CPU-synthetic causal holonomy falsification."""

    rows, geometry = generate_causal_transfer_rows(
        step_sizes=step_sizes,
        steps_per_side=steps_per_side,
        causal_map_replicates=causal_map_replicates,
        causal_output_dimension=causal_output_dimension,
        edit_norms=edit_norms,
        seed=seed,
    )
    baseline_numeric = (
        "edit_norm",
        "causal_lipschitz_constant",
        "jacobian_visibility",
        "minimum_edge_worst_direction_retention",
        "mean_edge_chordal_lineage",
        "path_edge_count",
        "step_size",
    )
    augmented_numeric = baseline_numeric + (
        "directional_path_displacement",
        "causal_risk_bound",
        "maximum_canonical_angle_degrees",
    )
    categorical = ("direction_class",)
    groups = np.asarray([row["causal_map_replicate"] for row in rows])
    baseline_predictions = _oof_predictions(
        rows,
        numeric=baseline_numeric,
        categorical=categorical,
        target="downstream_response_disagreement",
        groups=groups,
    )
    augmented_predictions = _oof_predictions(
        rows,
        numeric=augmented_numeric,
        categorical=categorical,
        target="downstream_response_disagreement",
        groups=groups,
    )
    permutation_rng = np.random.default_rng(seed + 17)
    permuted_rows = [dict(row) for row in rows]
    strata: dict[tuple[Any, ...], list[int]] = {}
    for index, row in enumerate(rows):
        key = (
            row["step_size"],
            row["edit_norm"],
            row["direction_class"],
        )
        strata.setdefault(key, []).append(index)
    augmented_only = (
        "directional_path_displacement",
        "causal_risk_bound",
        "maximum_canonical_angle_degrees",
    )
    for indices in strata.values():
        sources = permutation_rng.permutation(indices)
        for target_index, source_index in zip(indices, sources):
            for field in augmented_only:
                permuted_rows[target_index][field] = rows[source_index][field]
    permuted_predictions = _oof_predictions(
        permuted_rows,
        numeric=augmented_numeric,
        categorical=categorical,
        target="downstream_response_disagreement",
        groups=groups,
    )
    prediction = _bootstrap_relative_sse(
        rows,
        baseline_predictions,
        augmented_predictions,
        draws=bootstrap_draws,
        seed=seed + 9,
    )
    permuted_prediction = _bootstrap_relative_sse(
        rows,
        baseline_predictions,
        permuted_predictions,
        draws=bootstrap_draws,
        seed=seed + 19,
    )

    loop_rows = geometry["loop_receipts"]
    lineage_differences = []
    for step_size in step_sizes:
        matched = [
            row for row in loop_rows if float(row["step_size"]) == float(step_size)
        ]
        if len(matched) != 2:
            raise ValueError("matched loop receipt is incomplete")
        lineage_differences.append(
            abs(
                float(matched[0]["minimum_edge_worst_direction_retention"])
                - float(matched[1]["minimum_edge_worst_direction_retention"])
            )
        )
    maximum_lineage_difference = float(max(lineage_differences, default=0.0))
    maximum_identity_error = float(
        max(row["holonomy_expression_absolute_error"] for row in rows)
    )
    maximum_bound_excess = float(max(row["bound_excess"] for row in rows))
    maximum_flat_displacement = float(
        max(
            row["directional_path_displacement"]
            for row in rows
            if row["condition"] == "flat_flat"
        )
    )
    curved_exposed = [
        row
        for row in rows
        if row["condition"] == "curved_flat"
        and row["direction_class"] == "maximally_exposed"
    ]
    maximum_curved_displacement = float(
        max(row["directional_path_displacement"] for row in curved_exposed)
    )
    maximum_curved_response = float(
        max(row["downstream_response_disagreement"] for row in curved_exposed)
    )
    safe_rows = [
        row for row in rows if row["causal_risk_bound"] <= control_error_budget
    ]
    false_authorizations = sum(
        row["downstream_response_disagreement"] > control_error_budget
        for row in safe_rows
    )
    maximum_energy_difference = float(
        max(row["transported_energy_difference"] for row in rows)
    )
    gauge = _gauge_preflight(seed)
    orientation = _orientation_control(control_error_budget)
    lower_prediction = prediction["grouped_bootstrap_90_interval"][0]
    gates = {
        "G0_matched_local_lineage": maximum_lineage_difference <= 1e-10,
        "G1_path_identity": maximum_identity_error <= 1e-9,
        "G2_bound_coverage": maximum_bound_excess <= 1e-10,
        "G3_flat_negative_control": maximum_flat_displacement <= 1e-8,
        "G4_curved_positive_control": (
            maximum_curved_displacement > 0.5 and maximum_curved_response > 0.1
        ),
        "G5_incremental_prediction": (
            prediction["relative_sse_reduction"] >= 0.25
            and lower_prediction > 0.10
        ),
        "G6_bound_authorization": false_authorizations == 0,
        "G7_energy_invariance": maximum_energy_difference <= 1e-12,
        "G8_gauge_invariance": gauge["maximum_discrepancy"] <= 1e-9,
        "G9_orientation_reversal": (
            orientation["det_h"] < 0
            and orientation["orientation_flag"]
            and orientation["canonical_angles_suppressed"]
            and not orientation["authorized"]
        ),
    }
    instrument_gates = (
        "G0_matched_local_lineage",
        "G1_path_identity",
        "G2_bound_coverage",
        "G3_flat_negative_control",
        "G7_energy_invariance",
        "G8_gauge_invariance",
        "G9_orientation_reversal",
    )
    if not all(gates[name] for name in instrument_gates):
        decision = "invalid_instrument"
    elif not gates["G6_bound_authorization"]:
        decision = "unsafe_bound"
    elif not gates["G4_curved_positive_control"] or not gates[
        "G5_incremental_prediction"
    ]:
        decision = "geometry_only"
    else:
        decision = "pass"
    return {
        "schema_version": "1.0.0",
        "protocol_id": "holonomy_causal_transfer_falsification_v0_1",
        "decision": decision,
        "all_gates_pass": bool(all(gates.values())),
        "gates": gates,
        "metrics": {
            "row_count": len(rows),
            "loop_count": len(loop_rows),
            "maximum_matched_lineage_difference": maximum_lineage_difference,
            "maximum_path_identity_error": maximum_identity_error,
            "maximum_bound_excess": maximum_bound_excess,
            "maximum_flat_displacement": maximum_flat_displacement,
            "maximum_curved_exposed_displacement": maximum_curved_displacement,
            "maximum_curved_exposed_response_disagreement": maximum_curved_response,
            "authorized_row_count": len(safe_rows),
            "authorization_coverage": len(safe_rows) / len(rows),
            "false_authorization_count": int(false_authorizations),
            "maximum_energy_difference": maximum_energy_difference,
        },
        "prediction": prediction,
        "permuted_holonomy_prediction": permuted_prediction,
        "gauge_preflight": gauge,
        "orientation_control": orientation,
        "loop_receipts": loop_rows,
        "rows": rows,
        "claim_boundary": "CPU-synthetic causal path-transfer calibration only; no transformer, capability, self-improvement, or RSI claim.",
    }
