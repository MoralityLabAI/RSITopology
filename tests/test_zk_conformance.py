from __future__ import annotations

import ast
from hashlib import sha256
import json
import math
from pathlib import Path

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from rsi_topology import attestation
from rsi_topology.risk_gate import (
    ControlRiskMeasurement,
    EdgeRiskReceipt,
    LoopRiskReceipt,
    predict_control_gate,
)
from rsi_topology.zk.fixed_point import (
    DEGREES_180,
    NEGATIVE_CONTROL_EPSILON_Q_FLOOR,
    ONE,
    SCALE,
    chord_displacement_q_upper,
    sqrt_q_floor,
)
from rsi_topology.zk.gate_reference import (
    ENGINEERING_EVIDENCE,
    HOLONOMY_CLEAN,
    LINEAGE_CERTIFIED,
    PROTOCOL_VERSION,
    ControlRiskMeasurementFP,
    EdgeRiskReceiptFP,
    LoopRiskReceiptFP,
    array_sha256_le_f64,
    canonical_bytes,
    canonical_gate_error_serialization,
    canonical_gate_serialization,
    certification_level_from_margins_fp,
    journal_bytes,
    measurement_commitment_sha256,
    measurement_from_dict_fp,
    predict_control_gate_fp,
    sha256_json,
)


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_PATH = ROOT / "rsi_topology" / "zk" / "golden_vectors.jsonl"
DECISION_SEPARATION = 2**-20


def _q_floor(value: float) -> int:
    return math.floor(value * SCALE)


def _q_ceil(value: float) -> int:
    return math.ceil(value * SCALE)


def _float_measurement(raw: dict[str, object]) -> ControlRiskMeasurement:
    return ControlRiskMeasurement(
        measurement_id=str(raw["measurement_id"]),
        edges=tuple(EdgeRiskReceipt(**edge) for edge in raw["edges"]),
        loop=LoopRiskReceipt(**raw["loop"]),
    )


def _fixed_measurement(raw: dict[str, object]) -> ControlRiskMeasurementFP:
    loop = raw["loop"]
    angle = loop["maximum_canonical_angle_degrees"]
    return ControlRiskMeasurementFP(
        measurement_id=str(raw["measurement_id"]),
        edges=tuple(
            EdgeRiskReceiptFP(
                edge_id=edge["edge_id"],
                minimum_edge_worst_direction_retention=_q_floor(
                    edge["minimum_edge_worst_direction_retention"]
                ),
                retention_uncertainty=_q_ceil(edge["retention_uncertainty"]),
            )
            for edge in raw["edges"]
        ),
        loop=LoopRiskReceiptFP(
            maximum_canonical_angle_degrees=(
                None if angle is None else _q_ceil(angle)
            ),
            angle_uncertainty_degrees=_q_ceil(loop["angle_uncertainty_degrees"]),
            det_h_flag=loop["det_h_flag"],
            measured=loop["measured"],
        ),
    )


def _capture(call):
    try:
        return {"ok": True, "output": call()}
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error_type": type(exc).__name__, "message": str(exc)}


def _assert_decision_contract(
    float_output: dict[str, object], fixed_output: dict[str, object], budget: float
) -> None:
    float_bound = float_output["signed_control_loss_upper_bound"]
    fixed_bound = fixed_output["signed_control_loss_upper_bound"] / SCALE
    assert fixed_bound >= float_bound
    if not float_output["authorized"]:
        assert not fixed_output["authorized"]
    if abs(float_bound - budget) > DECISION_SEPARATION:
        assert fixed_output["authorized"] is float_output["authorized"]


def test_replay_all_golden_vectors() -> None:
    rows = [json.loads(line) for line in GOLDEN_PATH.read_text().splitlines()]
    assert len(rows) >= 200
    assert sum(row["category"] == "random" for row in rows) >= 100
    assert {row["category"] for row in rows} == {
        "validation",
        "edge_case",
        "boundary",
        "random",
    }

    for row in rows:
        raw = row["raw_inputs"]
        float_measurement = _float_measurement(raw)
        fixed_measurement = measurement_from_dict_fp(
            row["fixed_inputs"]["measurement"]
        )
        fixed_budget = row["fixed_inputs"]["error_budget"]
        assert fixed_measurement == _fixed_measurement(raw)
        assert fixed_budget == _q_floor(raw["error_budget"])

        float_path = _capture(
            lambda: predict_control_gate(float_measurement, raw["error_budget"])
        )
        fixed_path = _capture(
            lambda: predict_control_gate_fp(fixed_measurement, fixed_budget)
        )
        assert float_path == row["float_path"], row["case_id"]
        assert fixed_path == row["fixed_point"], row["case_id"]

        if fixed_path["ok"]:
            serialization = canonical_gate_serialization(
                fixed_measurement, fixed_budget, fixed_path["output"]
            )
            if float_path["ok"]:
                _assert_decision_contract(
                    float_path["output"], fixed_path["output"], raw["error_budget"]
                )
        else:
            serialization = canonical_gate_error_serialization(
                fixed_measurement,
                fixed_budget,
                fixed_path["error_type"],
                fixed_path["message"],
            )
        assert sha256(serialization).hexdigest() == row["canonical_sha256"]


finite_unit = st.floats(
    min_value=0.0,
    max_value=1.0,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)
finite_nonnegative = st.floats(
    min_value=0.0,
    max_value=2.0,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)
finite_angle = st.floats(
    min_value=0.0,
    max_value=180.0,
    allow_nan=False,
    allow_infinity=False,
    width=64,
)


@st.composite
def valid_gate_inputs(draw):
    edge_values = draw(
        st.lists(st.tuples(finite_unit, finite_nonnegative), min_size=1, max_size=8)
    )
    det_h_flag = draw(st.booleans())
    angle = draw(finite_angle)
    raw = {
        "measurement_id": "hypothesis",
        "edges": [
            {
                "edge_id": f"edge-{index}",
                "minimum_edge_worst_direction_retention": retention,
                "retention_uncertainty": uncertainty,
            }
            for index, (retention, uncertainty) in enumerate(edge_values)
        ],
        "loop": {
            "maximum_canonical_angle_degrees": None if det_h_flag else angle,
            "angle_uncertainty_degrees": draw(finite_angle),
            "det_h_flag": det_h_flag,
            "measured": draw(st.booleans()),
        },
        "error_budget": draw(finite_nonnegative),
    }
    return raw


@given(valid_gate_inputs())
@settings(max_examples=500, deadline=None)
def test_float_fixed_decision_property(raw: dict[str, object]) -> None:
    float_output = predict_control_gate(
        _float_measurement(raw), raw["error_budget"]
    )
    fixed_output = predict_control_gate_fp(
        _fixed_measurement(raw), _q_floor(raw["error_budget"])
    )
    _assert_decision_contract(float_output, fixed_output, raw["error_budget"])


@given(valid_gate_inputs(), st.floats(min_value=-2**-18, max_value=2**-18))
@settings(max_examples=300, deadline=None)
def test_boundary_decisions_are_conservative(
    raw: dict[str, object], offset: float
) -> None:
    measurement = _float_measurement(raw)
    bound = predict_control_gate(measurement, 2.0)[
        "signed_control_loss_upper_bound"
    ]
    budget = min(2.0, max(0.0, bound + offset))
    raw["error_budget"] = budget
    float_output = predict_control_gate(measurement, budget)
    fixed_output = predict_control_gate_fp(
        _fixed_measurement(raw), _q_floor(budget)
    )
    _assert_decision_contract(float_output, fixed_output, budget)


@given(st.integers(min_value=0, max_value=ONE))
def test_sqrt_uses_exact_floor_rounding(value_q: int) -> None:
    root_q = sqrt_q_floor(value_q)
    radicand = value_q * SCALE
    assert root_q * root_q <= radicand < (root_q + 1) * (root_q + 1)


@given(st.integers(min_value=0, max_value=DEGREES_180))
def test_chord_displacement_is_an_upper_bound(angle_q: int) -> None:
    exact = 2.0 * math.sin(math.radians(angle_q / SCALE) / 2.0)
    assert chord_displacement_q_upper(angle_q) / SCALE >= exact


def test_fixed_modules_contain_no_float_literals_or_numpy() -> None:
    for relative in (
        Path("rsi_topology/zk/fixed_point.py"),
        Path("rsi_topology/zk/gate_reference.py"),
    ):
        tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
        assert not any(
            isinstance(node, ast.Constant) and isinstance(node.value, float)
            for node in ast.walk(tree)
        )
        imports = [
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        ]
        assert "numpy" not in imports


def test_attestation_threshold_levels_and_strict_epsilon() -> None:
    base = {
        "mean_edge_chordal_lineage": 0,
        "minimum_edge_worst_direction_retention": 0,
        "holonomy_angle_degrees": 0,
        "holonomy_identity_loss": 0,
        "required_level": HOLONOMY_CLEAN,
    }
    failed = certification_level_from_margins_fp(
        matched_random_label_negative_control=NEGATIVE_CONTROL_EPSILON_Q_FLOOR,
        **base,
    )
    assert failed["certification_level"] == ENGINEERING_EVIDENCE
    assert not failed["authorized"]

    passed = certification_level_from_margins_fp(
        matched_random_label_negative_control=(
            NEGATIVE_CONTROL_EPSILON_Q_FLOOR + 1
        ),
        **base,
    )
    assert passed["certification_level"] == HOLONOMY_CLEAN
    assert passed["authorized"]

    lineage_only = certification_level_from_margins_fp(
        matched_random_label_negative_control=(
            NEGATIVE_CONTROL_EPSILON_Q_FLOOR + 1
        ),
        det_h_flag=True,
        required_level=LINEAGE_CERTIFIED,
        **{key: value for key, value in base.items() if key != "required_level"},
    )
    assert lineage_only["certification_level"] == LINEAGE_CERTIFIED
    assert lineage_only["authorized"]


def test_canonical_hashes_match_attestation_spec() -> None:
    value = {"z": [3, "non-ascii: \u03bb"], "a": {"flag": True, "none": None}}
    assert canonical_bytes(value) == attestation._canonical_bytes(value)
    assert sha256_json(value) == attestation.sha256_json(value)

    array = np.array([[1.5, -0.0], [math.pi, math.inf]], dtype=">f8")
    canonical_array = np.ascontiguousarray(array, dtype="<f8")
    assert array_sha256_le_f64(
        canonical_array.shape, canonical_array.tobytes(order="C")
    ) == attestation.array_sha256(array)


def test_measurement_commitment_and_journal_are_deterministic() -> None:
    measurement = ControlRiskMeasurementFP(
        measurement_id="receipt-1",
        edges=(EdgeRiskReceiptFP("edge-1", ONE, 0),),
        loop=LoopRiskReceiptFP(0, 0, False, True),
    )
    output = predict_control_gate_fp(measurement, 0)
    commitment_hex = measurement_commitment_sha256(measurement, 0)
    first = journal_bytes(
        bytes.fromhex(commitment_hex), output["authorized"], output["authorization_margin"]
    )
    second = journal_bytes(
        bytes.fromhex(commitment_hex), output["authorized"], output["authorization_margin"]
    )
    assert first == second
    assert first[:32] == bytes.fromhex(commitment_hex)
    assert PROTOCOL_VERSION.encode("utf-8") in first


def test_array_hash_rejects_wrong_payload_length() -> None:
    with pytest.raises(ValueError, match="payload length"):
        array_sha256_le_f64((2, 2), b"too short")
