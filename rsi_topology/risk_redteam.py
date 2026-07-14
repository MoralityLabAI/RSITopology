"""CPU-only red-team controls for the signed-control risk gate."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import numpy as np
from sklearn.metrics import roc_auc_score

from .risk_gate import (
    ControlRiskMeasurement,
    EdgeRiskReceipt,
    LoopRiskReceipt,
    control_risk_vector,
    predict_control_gate,
)


def _rotation(angle_degrees: float) -> np.ndarray:
    angle = np.radians(angle_degrees)
    return np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])


def _operator_norm_2x2(matrix: np.ndarray) -> float:
    gram = matrix.T @ matrix
    trace = float(np.trace(gram))
    determinant = float(np.linalg.det(gram))
    largest = 0.5 * (trace + np.sqrt(max(0.0, trace * trace - 4.0 * determinant)))
    return float(np.sqrt(max(0.0, largest)))


def _realized_chain(retentions: np.ndarray, angle_degrees: float, reversing: bool) -> tuple[np.ndarray, np.ndarray]:
    count = len(retentions)
    edge_angle = angle_degrees / count
    maps = []
    orthogonal = []
    for index, retention in enumerate(retentions):
        q = _rotation(edge_angle)
        if reversing and index == count - 1:
            q = np.diag([-1.0, 1.0]) @ q
        contraction = np.diag([np.sqrt(retention), 1.0])
        maps.append(q @ contraction)
        orthogonal.append(q)
    realized = np.eye(2)
    holonomy = np.eye(2)
    for actual, q in zip(maps, orthogonal):
        realized = actual @ realized
        holonomy = q @ holonomy
    return realized, holonomy


def _one_fixture(
    rng: np.random.Generator,
    index: int,
    *,
    family: str,
    error_budget: float,
    retention_uncertainty: float,
    angle_uncertainty: float,
    unmeasured_probability: float,
    reversal_probability: float,
) -> dict[str, Any]:
    edge_count = int(rng.integers(1, 7))
    if family == "lineage_dominant":
        true_retentions = rng.uniform(0.64, 0.94, size=edge_count)
        true_angle = float(rng.uniform(0.0, 15.0))
    elif family == "holonomy_dominant":
        true_retentions = rng.uniform(0.97, 1.0, size=edge_count)
        true_angle = float(rng.uniform(25.0, 160.0))
    else:
        true_retentions = rng.uniform(0.72, 1.0, size=edge_count)
        true_angle = float(rng.uniform(0.0, 160.0))
    reversing = bool(rng.random() < reversal_probability)
    measured = bool(rng.random() >= unmeasured_probability)
    realized, holonomy = _realized_chain(true_retentions, true_angle, reversing)
    actual_loss = _operator_norm_2x2(realized - np.eye(2))

    observed_retentions = np.clip(
        true_retentions + rng.uniform(-retention_uncertainty, retention_uncertainty, size=edge_count),
        0.0,
        1.0,
    )
    observed_angle = float(np.clip(true_angle + rng.uniform(-angle_uncertainty, angle_uncertainty), 0, 180))
    measurement = ControlRiskMeasurement(
        measurement_id=f"fixture-{index:06d}",
        edges=tuple(
            EdgeRiskReceipt(
                edge_id=f"edge-{edge_index}",
                minimum_edge_worst_direction_retention=float(value),
                retention_uncertainty=retention_uncertainty,
            )
            for edge_index, value in enumerate(observed_retentions)
        ),
        loop=LoopRiskReceipt(
            maximum_canonical_angle_degrees=None if reversing else observed_angle,
            angle_uncertainty_degrees=angle_uncertainty,
            det_h_flag=reversing,
            measured=measured,
        ),
    )
    decision = predict_control_gate(measurement, error_budget)
    return {
        "measurement": asdict(measurement),
        "family": family,
        "actual_control_loss": actual_loss,
        "control_lost": actual_loss > error_budget,
        "authorized": decision["authorized"],
        "risk_vector": {key: decision[key] for key in (
            "lineage_contraction_bound",
            "holonomy_displacement_bound",
            "orientation_reversal_flag",
            "measurement_uncertainty_margin",
            "audit_gap",
            "signed_control_loss_upper_bound",
        )},
        "lineage_only_score": min(2.0, decision["lineage_contraction_bound"]),
        "holonomy_only_score": min(2.0, decision["holonomy_displacement_bound"]),
    }


def _boundary_grid(error_budget: float) -> dict[str, Any]:
    retentions = (0.64, 0.72, 0.8, 0.88, 0.94, 0.98, 1.0)
    angles = (0, 10, 20, 30, 45, 60, 90, 120, 150, 180)
    edge_counts = (1, 2, 4, 6)
    rows = []
    for edge_count in edge_counts:
        for retention in retentions:
            for angle in angles:
                true = np.full(edge_count, retention)
                realized, _ = _realized_chain(true, angle, False)
                loss = _operator_norm_2x2(realized - np.eye(2))
                measurement = ControlRiskMeasurement(
                    measurement_id=f"grid-m{edge_count}-l{retention}-a{angle}",
                    edges=tuple(EdgeRiskReceipt(f"e{i}", retention) for i in range(edge_count)),
                    loop=LoopRiskReceipt(float(angle), 0.0, False, True),
                )
                decision = predict_control_gate(measurement, error_budget)
                rows.append({
                    "edge_count": edge_count,
                    "minimum_edge_retention": retention,
                    "holonomy_angle_degrees": angle,
                    "actual_control_loss": loss,
                    "control_lost": loss > error_budget,
                    "authorized": decision["authorized"],
                    "risk_bound": decision["signed_control_loss_upper_bound"],
                })
    return {
        "error_budget": error_budget,
        "rows": rows,
        "false_authorizations": sum(row["authorized"] and row["control_lost"] for row in rows),
    }


def run_control_risk_redteam(*, fixtures: int = 6000, seed: int = 20260712) -> dict[str, Any]:
    error_budget = 0.5
    rng = np.random.default_rng(seed)
    families = ("lineage_dominant", "holonomy_dominant", "mixed")
    rows = [
        _one_fixture(
            rng,
            index,
            family=families[index % len(families)],
            error_budget=error_budget,
            retention_uncertainty=0.01,
            angle_uncertainty=2.0,
            unmeasured_probability=0.1,
            reversal_probability=0.05,
        )
        for index in range(fixtures)
    ]
    labels = np.array([row["control_lost"] for row in rows], dtype=int)
    full = np.array([row["risk_vector"]["signed_control_loss_upper_bound"] for row in rows])
    lineage = np.array([row["lineage_only_score"] for row in rows])
    holonomy = np.array([row["holonomy_only_score"] for row in rows])
    authorized = np.array([row["authorized"] for row in rows], dtype=bool)
    safe = labels == 0
    authorized_count = int(np.sum(authorized))
    false_authorized = int(np.sum(authorized & ~safe))
    precision = 1.0 if authorized_count == 0 else float(np.sum(authorized & safe) / authorized_count)
    boundary = _boundary_grid(error_budget)

    lineage_blind = any(
        row["family"] == "holonomy_dominant"
        and row["control_lost"]
        and row["lineage_only_score"] <= error_budget
        for row in rows
    )
    holonomy_blind = any(
        row["family"] == "lineage_dominant"
        and row["control_lost"]
        and row["holonomy_only_score"] <= error_budget
        for row in rows
    )
    reversal_denied = all(
        not row["authorized"] for row in rows if row["risk_vector"]["orientation_reversal_flag"]
    )
    unmeasured_denied = all(not row["authorized"] for row in rows if row["risk_vector"]["audit_gap"])
    metrics = {
        "fixture_count": fixtures,
        "control_loss_prevalence": float(np.mean(labels)),
        "authorized_count": authorized_count,
        "authorization_coverage": float(np.mean(authorized)),
        "authorized_precision": precision,
        "false_authorization_rate": float(false_authorized / fixtures),
        "full_vector_auroc": float(roc_auc_score(labels, full)),
        "lineage_only_auroc": float(roc_auc_score(labels, lineage)),
        "holonomy_only_auroc": float(roc_auc_score(labels, holonomy)),
        "lineage_only_blind_spot_found": lineage_blind,
        "holonomy_only_blind_spot_found": holonomy_blind,
        "orientation_reversal_denied": reversal_denied,
        "unmeasured_loop_abstained": unmeasured_denied,
        "analytic_boundary_false_authorizations": boundary["false_authorizations"],
    }
    gates = {
        "authorized_precision": metrics["authorized_precision"] >= 0.99,
        "false_authorization_rate": metrics["false_authorization_rate"] <= 0.01,
        "full_vector_auroc": metrics["full_vector_auroc"] >= 0.90,
        "lineage_blind_spot": lineage_blind,
        "holonomy_blind_spot": holonomy_blind,
        "orientation_reversal": reversal_denied,
        "unmeasured_loop": unmeasured_denied,
        "analytic_boundary": boundary["false_authorizations"] == 0,
    }
    return {
        "schema_version": "1.0.0",
        "protocol_id": "control_risk_redteam_v0_1",
        "metrics": metrics,
        "gates": gates,
        "all_gates_pass": bool(all(gates.values())),
        "boundary_surface": boundary,
        "claim_boundary": "CPU-synthetic signed-control loss only; no real-model capability or self-improvement claim.",
    }
