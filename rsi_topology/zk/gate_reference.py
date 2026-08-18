"""Deterministic fixed-point reference for the signed-control gate.

All numeric inputs and outputs are signed Q16.48 integers. This module uses
only the Python standard library and explicit field ordering so it can be
ported directly to a ``no_std`` Rust guest.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import struct
from typing import Any, Iterable, Mapping

from .fixed_point import (
    DEGREES_180,
    NEGATIVE_CONTROL_EPSILON_Q_FLOOR,
    ONE,
    TWO,
    chord_displacement_q_upper,
    require_int,
    sqrt_q_floor,
)


PROTOCOL_VERSION = "signed-control-gate-q16.48-v1"
SERIALIZATION_MAGIC = b"RSIZKG01"

ENGINEERING_EVIDENCE = "engineering_evidence"
LINEAGE_CERTIFIED = "lineage_certified"
HOLONOMY_CLEAN = "holonomy_clean"
LEVEL_ORDER = {ENGINEERING_EVIDENCE: 0, LINEAGE_CERTIFIED: 1, HOLONOMY_CLEAN: 2}

I64_MIN = -(1 << 63)
I64_MAX = (1 << 63) - 1
U32_MAX = (1 << 32) - 1


@dataclass(frozen=True)
class EdgeRiskReceiptFP:
    edge_id: str
    minimum_edge_worst_direction_retention: int
    retention_uncertainty: int = 0


@dataclass(frozen=True)
class LoopRiskReceiptFP:
    maximum_canonical_angle_degrees: int | None
    angle_uncertainty_degrees: int
    det_h_flag: bool
    measured: bool = True


@dataclass(frozen=True)
class ControlRiskMeasurementFP:
    measurement_id: str
    edges: tuple[EdgeRiskReceiptFP, ...]
    loop: LoopRiskReceiptFP


def _fixed_int(value: Any, label: str) -> int:
    return require_int(value, label)


def control_risk_vector_fp(measurement: ControlRiskMeasurementFP) -> dict[str, Any]:
    """Mirror ``control_risk_vector`` with conservative Q16.48 arithmetic."""

    if not measurement.edges:
        raise ValueError("at least one edge receipt is required")
    point_lineage = 0
    conservative_lineage = 0
    for edge in measurement.edges:
        value = _fixed_int(
            edge.minimum_edge_worst_direction_retention, "retention"
        )
        uncertainty = _fixed_int(edge.retention_uncertainty, "retention uncertainty")
        if not 0 <= value <= ONE or uncertainty < 0:
            raise ValueError(f"invalid retention receipt: {edge.edge_id}")
        point_lineage += ONE - sqrt_q_floor(value)
        conservative_retention = max(0, value - uncertainty)
        conservative_lineage += ONE - sqrt_q_floor(conservative_retention)

    loop = measurement.loop
    angle_uncertainty = _fixed_int(
        loop.angle_uncertainty_degrees, "angle uncertainty"
    )
    if angle_uncertainty < 0:
        raise ValueError("angle uncertainty must be finite and nonnegative")
    audit_gap = not loop.measured
    if loop.det_h_flag:
        point_holonomy = TWO
        conservative_holonomy = TWO
    else:
        if loop.maximum_canonical_angle_degrees is None:
            raise ValueError("orientation-preserving receipt requires a canonical angle")
        angle = _fixed_int(loop.maximum_canonical_angle_degrees, "canonical angle")
        if not 0 <= angle <= DEGREES_180:
            raise ValueError("canonical angle must lie in [0,180]")
        point_holonomy = chord_displacement_q_upper(angle)
        if angle_uncertainty >= DEGREES_180 - angle:
            upper_angle = DEGREES_180
        else:
            upper_angle = angle + angle_uncertainty
        conservative_holonomy = chord_displacement_q_upper(upper_angle)

    point = min(TWO, point_lineage + point_holonomy)
    conservative = min(TWO, conservative_lineage + conservative_holonomy)
    if audit_gap:
        conservative = TWO
    return {
        "measurement_id": measurement.measurement_id,
        "lineage_contraction_point": point_lineage,
        "lineage_contraction_bound": conservative_lineage,
        "holonomy_displacement_point": point_holonomy,
        "holonomy_displacement_bound": conservative_holonomy,
        "orientation_reversal_flag": loop.det_h_flag,
        "audit_gap": audit_gap,
        "measurement_uncertainty_margin": max(0, conservative - point),
        "point_risk_score": point,
        "signed_control_loss_upper_bound": conservative,
    }


def predict_control_gate_fp(
    measurement: ControlRiskMeasurementFP, error_budget: int
) -> dict[str, Any]:
    """Mirror ``predict_control_gate`` and deny on conservative fixed bounds."""

    error_budget = _fixed_int(error_budget, "error_budget")
    if not 0 <= error_budget <= TWO:
        raise ValueError("error_budget must lie in [0,2]")
    vector = control_risk_vector_fp(measurement)
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
        "authorization_margin": error_budget
        - vector["signed_control_loss_upper_bound"],
        "required_certification": HOLONOMY_CLEAN,
    }


def certification_level_from_margins_fp(
    *,
    matched_random_label_negative_control: int,
    mean_edge_chordal_lineage: int,
    minimum_edge_worst_direction_retention: int,
    holonomy_angle_degrees: int,
    holonomy_identity_loss: int,
    required_level: str,
    has_lineage_failures: bool = False,
    hashes_valid: bool = True,
    has_loop_receipts: bool = True,
    det_h_flag: bool = False,
    require_orientation_preserving: bool = True,
    holonomy_available: bool = True,
) -> dict[str, Any]:
    """Reproduce the threshold-compare half of ``certify_record``.

    The caller supplies margins and the structural outcomes produced by the
    out-of-scope registry validator. The strict float negative-control test is
    ``margin > 1e-12``. Margins are rounded down, so requiring the encoded
    margin to exceed ``floor(1e-12 * 2**48)`` is conservative.
    """

    margins = {
        "matched_random_label_negative_control": _fixed_int(
            matched_random_label_negative_control, "negative-control margin"
        ),
        "mean_edge_chordal_lineage": _fixed_int(
            mean_edge_chordal_lineage, "mean-lineage margin"
        ),
        "minimum_edge_worst_direction_retention": _fixed_int(
            minimum_edge_worst_direction_retention, "worst-retention margin"
        ),
        "holonomy_angle_degrees": _fixed_int(
            holonomy_angle_degrees, "holonomy-angle margin"
        ),
        "holonomy_identity_loss": _fixed_int(
            holonomy_identity_loss, "holonomy-loss margin"
        ),
    }
    if required_level not in LEVEL_ORDER:
        raise ValueError("unknown required certification level")

    failures: list[str] = []
    attained = ENGINEERING_EVIDENCE
    negative_control_passed = (
        margins["matched_random_label_negative_control"]
        > NEGATIVE_CONTROL_EPSILON_Q_FLOOR
    )
    if not negative_control_passed:
        failures.append("negative_control_not_passed")
    if margins["mean_edge_chordal_lineage"] < 0:
        failures.append("lineage:mean_edge_below_threshold")
    if margins["minimum_edge_worst_direction_retention"] < 0:
        failures.append("lineage:worst_direction_below_threshold")
    if (
        negative_control_passed
        and not has_lineage_failures
        and hashes_valid
        and margins["mean_edge_chordal_lineage"] >= 0
        and margins["minimum_edge_worst_direction_retention"] >= 0
    ):
        attained = LINEAGE_CERTIFIED

    holonomy_failures: list[str] = []
    if not holonomy_available:
        holonomy_failures.append("holonomy_unavailable")
    if not has_loop_receipts:
        holonomy_failures.append("holonomy:no_loop_receipts")
    if det_h_flag and require_orientation_preserving:
        holonomy_failures.append("holonomy:orientation_reversal")
    if margins["holonomy_angle_degrees"] < 0:
        holonomy_failures.append("holonomy:angle_budget_exceeded")
    if margins["holonomy_identity_loss"] < 0:
        holonomy_failures.append("holonomy:identity_loss_budget_exceeded")
    if attained == LINEAGE_CERTIFIED and not holonomy_failures:
        attained = HOLONOMY_CLEAN
    failures.extend(holonomy_failures)

    authorized = LEVEL_ORDER[attained] >= LEVEL_ORDER[required_level]
    if not authorized:
        failures.append(f"policy:requires_{required_level}")
    return {
        "certification_level": attained,
        "required_level": required_level,
        "authorized": authorized,
        "margins": margins,
        "failures": tuple(sorted(set(failures))),
    }


def canonical_bytes(value: Any) -> bytes:
    """Match ``attestation._canonical_bytes`` using sorted compact JSON."""

    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _canonical_bytes(value: Any) -> bytes:
    """Compatibility name matching the private float-spec helper."""

    return canonical_bytes(value)


def sha256_json(value: Any) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def array_sha256_le_f64(shape: Iterable[int], little_endian_f64_bytes: bytes) -> str:
    """Match ``array_sha256`` from an explicit shape and little-endian payload."""

    normalized_shape = []
    item_count = 1
    for dimension in shape:
        dimension = _fixed_int(dimension, "array dimension")
        if dimension < 0:
            raise ValueError("array dimensions must be nonnegative")
        normalized_shape.append(dimension)
        item_count *= dimension
    payload = bytes(little_endian_f64_bytes)
    if len(payload) != item_count * 8:
        raise ValueError("array payload length does not match shape")
    header = canonical_bytes({"dtype": "<f8", "shape": normalized_shape})
    return sha256(header + b"\n" + payload).hexdigest()


def array_sha256(shape: Iterable[int], little_endian_f64_bytes: bytes) -> str:
    """Guest-portable form of ``attestation.array_sha256``."""

    return array_sha256_le_f64(shape, little_endian_f64_bytes)


def _pack_u32(value: int) -> bytes:
    if not 0 <= value <= U32_MAX:
        raise ValueError("value does not fit u32")
    return struct.pack("<I", value)


def _pack_i64(value: int, label: str) -> bytes:
    value = _fixed_int(value, label)
    if not I64_MIN <= value <= I64_MAX:
        raise ValueError(f"{label} does not fit i64")
    return struct.pack("<q", value)


def _pack_bool(value: bool) -> bytes:
    if not isinstance(value, bool):
        raise ValueError("boolean field must be bool")
    return b"\x01" if value else b"\x00"


def _pack_string(value: str) -> bytes:
    if not isinstance(value, str):
        raise ValueError("string field must be str")
    encoded = value.encode("utf-8")
    return _pack_u32(len(encoded)) + encoded


def canonical_measurement_bytes(measurement: ControlRiskMeasurementFP) -> bytes:
    """Serialize the private measurement receipt in declared field order."""

    parts = [SERIALIZATION_MAGIC, _pack_string(PROTOCOL_VERSION)]
    parts.append(_pack_string(measurement.measurement_id))
    parts.append(_pack_u32(len(measurement.edges)))
    for edge in measurement.edges:
        parts.extend(
            (
                _pack_string(edge.edge_id),
                _pack_i64(
                    edge.minimum_edge_worst_direction_retention, "retention"
                ),
                _pack_i64(edge.retention_uncertainty, "retention uncertainty"),
            )
        )
    loop = measurement.loop
    has_angle = loop.maximum_canonical_angle_degrees is not None
    parts.append(_pack_bool(has_angle))
    if has_angle:
        parts.append(
            _pack_i64(loop.maximum_canonical_angle_degrees, "canonical angle")
        )
    parts.extend(
        (
            _pack_i64(loop.angle_uncertainty_degrees, "angle uncertainty"),
            _pack_bool(loop.det_h_flag),
            _pack_bool(loop.measured),
        )
    )
    return b"".join(parts)


def measurement_commitment_sha256(
    measurement: ControlRiskMeasurementFP, error_budget: int
) -> str:
    """Commit the private measurement together with its externally public budget."""

    payload = canonical_measurement_bytes(measurement) + _pack_i64(
        error_budget, "error_budget"
    )
    return sha256(payload).hexdigest()


_OUTPUT_FIXED_FIELDS = (
    "lineage_contraction_point",
    "lineage_contraction_bound",
    "holonomy_displacement_point",
    "holonomy_displacement_bound",
    "measurement_uncertainty_margin",
    "point_risk_score",
    "signed_control_loss_upper_bound",
    "error_budget",
    "authorization_margin",
)


def canonical_gate_serialization(
    measurement: ControlRiskMeasurementFP,
    error_budget: int,
    output: Mapping[str, Any],
) -> bytes:
    """Serialize valid gate inputs and outputs in canonical little-endian form."""

    parts = [canonical_measurement_bytes(measurement), _pack_i64(error_budget, "error_budget")]
    parts.append(b"\x01")
    for field in _OUTPUT_FIXED_FIELDS:
        parts.append(_pack_i64(output[field], field))
    parts.extend(
        (
            _pack_bool(output["orientation_reversal_flag"]),
            _pack_bool(output["audit_gap"]),
            _pack_bool(output["authorized"]),
        )
    )
    return b"".join(parts)


def canonical_gate_error_serialization(
    measurement: ControlRiskMeasurementFP,
    error_budget: int,
    error_type: str,
    error_message: str,
) -> bytes:
    """Serialize a rejected input and deterministic validation result."""

    return b"".join(
        (
            canonical_measurement_bytes(measurement),
            _pack_i64(error_budget, "error_budget"),
            b"\x00",
            _pack_string(error_type),
            _pack_string(error_message),
        )
    )


def gate_serialization_sha256(
    measurement: ControlRiskMeasurementFP,
    error_budget: int,
    output: Mapping[str, Any],
) -> str:
    return sha256(canonical_gate_serialization(measurement, error_budget, output)).hexdigest()


def journal_bytes(
    measurement_commitment_hash: bytes,
    decision: bool,
    authorization_margin: int,
) -> bytes:
    """Encode the future guest's public journal tuple."""

    commitment = bytes(measurement_commitment_hash)
    if len(commitment) != 32:
        raise ValueError("measurement commitment must contain 32 bytes")
    return b"".join(
        (
            commitment,
            _pack_string(PROTOCOL_VERSION),
            _pack_bool(decision),
            _pack_i64(authorization_margin, "authorization margin"),
        )
    )


def measurement_from_dict_fp(value: Mapping[str, Any]) -> ControlRiskMeasurementFP:
    return ControlRiskMeasurementFP(
        measurement_id=str(value["measurement_id"]),
        edges=tuple(EdgeRiskReceiptFP(**item) for item in value["edges"]),
        loop=LoopRiskReceiptFP(**value["loop"]),
    )
