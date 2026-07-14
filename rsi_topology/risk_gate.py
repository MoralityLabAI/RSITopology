"""Provable signed-control risk bounds from lineage and holonomy receipts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class EdgeRiskReceipt:
    edge_id: str
    minimum_edge_worst_direction_retention: float
    retention_uncertainty: float = 0.0


@dataclass(frozen=True)
class LoopRiskReceipt:
    maximum_canonical_angle_degrees: float | None
    angle_uncertainty_degrees: float
    det_h_flag: bool
    measured: bool = True


@dataclass(frozen=True)
class ControlRiskMeasurement:
    measurement_id: str
    edges: tuple[EdgeRiskReceipt, ...]
    loop: LoopRiskReceipt


def control_risk_vector(measurement: ControlRiskMeasurement) -> dict:
    """Return a conservative operator-error vector for signed coordinates."""
    if not measurement.edges:
        raise ValueError("at least one edge receipt is required")
    point_lineage = 0.0
    conservative_lineage = 0.0
    for edge in measurement.edges:
        value = float(edge.minimum_edge_worst_direction_retention)
        uncertainty = float(edge.retention_uncertainty)
        if not np.isfinite([value, uncertainty]).all() or not 0.0 <= value <= 1.0 or uncertainty < 0:
            raise ValueError(f"invalid retention receipt: {edge.edge_id}")
        point_lineage += 1.0 - np.sqrt(value)
        conservative_lineage += 1.0 - np.sqrt(max(0.0, value - uncertainty))

    loop = measurement.loop
    if loop.angle_uncertainty_degrees < 0 or not np.isfinite(loop.angle_uncertainty_degrees):
        raise ValueError("angle uncertainty must be finite and nonnegative")
    audit_gap = not loop.measured
    if loop.det_h_flag:
        point_holonomy = conservative_holonomy = 2.0
    else:
        if loop.maximum_canonical_angle_degrees is None:
            raise ValueError("orientation-preserving receipt requires a canonical angle")
        angle = float(loop.maximum_canonical_angle_degrees)
        if not np.isfinite(angle) or not 0.0 <= angle <= 180.0:
            raise ValueError("canonical angle must lie in [0,180]")
        point_holonomy = 2.0 * np.sin(np.radians(angle) / 2.0)
        upper_angle = min(180.0, angle + loop.angle_uncertainty_degrees)
        conservative_holonomy = 2.0 * np.sin(np.radians(upper_angle) / 2.0)

    point = min(2.0, point_lineage + point_holonomy)
    conservative = min(2.0, conservative_lineage + conservative_holonomy)
    if audit_gap:
        conservative = 2.0
    return {
        "measurement_id": measurement.measurement_id,
        "lineage_contraction_point": float(point_lineage),
        "lineage_contraction_bound": float(conservative_lineage),
        "holonomy_displacement_point": float(point_holonomy),
        "holonomy_displacement_bound": float(conservative_holonomy),
        "orientation_reversal_flag": loop.det_h_flag,
        "audit_gap": audit_gap,
        "measurement_uncertainty_margin": float(max(0.0, conservative - point)),
        "point_risk_score": float(point),
        "signed_control_loss_upper_bound": float(conservative),
    }


def predict_control_gate(measurement: ControlRiskMeasurement, error_budget: float) -> dict:
    if not np.isfinite(error_budget) or not 0.0 <= error_budget <= 2.0:
        raise ValueError("error_budget must lie in [0,2]")
    vector = control_risk_vector(measurement)
    authorized = bool(
        not vector["audit_gap"]
        and not vector["orientation_reversal_flag"]
        and vector["signed_control_loss_upper_bound"] <= error_budget
    )
    return {
        **vector,
        "error_budget": error_budget,
        "authorized": authorized,
        "decision": "authorize_signed_control" if authorized else "deny_or_abstain",
        "authorization_margin": float(error_budget - vector["signed_control_loss_upper_bound"]),
        "required_certification": "holonomy_clean",
    }


def measurement_from_dict(value: dict) -> ControlRiskMeasurement:
    return ControlRiskMeasurement(
        measurement_id=str(value["measurement_id"]),
        edges=tuple(EdgeRiskReceipt(**item) for item in value["edges"]),
        loop=LoopRiskReceipt(**value["loop"]),
    )
