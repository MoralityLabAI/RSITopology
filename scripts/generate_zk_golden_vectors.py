"""Generate deterministic signed-control Q16.48 conformance vectors."""

from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import random
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rsi_topology.risk_gate import (
    ControlRiskMeasurement,
    EdgeRiskReceipt,
    LoopRiskReceipt,
    predict_control_gate,
)
from rsi_topology.zk.fixed_point import SCALE
from rsi_topology.zk.gate_reference import (
    ControlRiskMeasurementFP,
    EdgeRiskReceiptFP,
    LoopRiskReceiptFP,
    canonical_gate_error_serialization,
    canonical_gate_serialization,
    predict_control_gate_fp,
)


OUTPUT = REPO_ROOT / "rsi_topology" / "zk" / "golden_vectors.jsonl"
SEED = 20_260_715
Q_ULP = 1.0 / SCALE


def q_floor(value: float) -> int:
    return math.floor(value * SCALE)


def q_ceil(value: float) -> int:
    return math.ceil(value * SCALE)


def raw_case(
    case_id: str,
    *,
    retentions: list[tuple[float, float]],
    angle: float | None,
    angle_uncertainty: float,
    det_h_flag: bool,
    measured: bool,
    error_budget: float,
    category: str,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "category": category,
        "measurement_id": case_id,
        "edges": [
            {
                "edge_id": f"{case_id}.edge.{index}",
                "minimum_edge_worst_direction_retention": retention,
                "retention_uncertainty": uncertainty,
            }
            for index, (retention, uncertainty) in enumerate(retentions)
        ],
        "loop": {
            "maximum_canonical_angle_degrees": angle,
            "angle_uncertainty_degrees": angle_uncertainty,
            "det_h_flag": det_h_flag,
            "measured": measured,
        },
        "error_budget": error_budget,
    }


def float_measurement(raw: dict[str, Any]) -> ControlRiskMeasurement:
    return ControlRiskMeasurement(
        measurement_id=raw["measurement_id"],
        edges=tuple(EdgeRiskReceipt(**edge) for edge in raw["edges"]),
        loop=LoopRiskReceipt(**raw["loop"]),
    )


def fixed_measurement(raw: dict[str, Any]) -> ControlRiskMeasurementFP:
    loop = raw["loop"]
    angle = loop["maximum_canonical_angle_degrees"]
    return ControlRiskMeasurementFP(
        measurement_id=raw["measurement_id"],
        edges=tuple(
            EdgeRiskReceiptFP(
                edge_id=edge["edge_id"],
                minimum_edge_worst_direction_retention=q_floor(
                    edge["minimum_edge_worst_direction_retention"]
                ),
                retention_uncertainty=q_ceil(edge["retention_uncertainty"]),
            )
            for edge in raw["edges"]
        ),
        loop=LoopRiskReceiptFP(
            maximum_canonical_angle_degrees=None if angle is None else q_ceil(angle),
            angle_uncertainty_degrees=q_ceil(loop["angle_uncertainty_degrees"]),
            det_h_flag=loop["det_h_flag"],
            measured=loop["measured"],
        ),
    )


def measurement_to_dict(measurement: ControlRiskMeasurementFP) -> dict[str, Any]:
    return {
        "measurement_id": measurement.measurement_id,
        "edges": [
            {
                "edge_id": edge.edge_id,
                "minimum_edge_worst_direction_retention": edge.minimum_edge_worst_direction_retention,
                "retention_uncertainty": edge.retention_uncertainty,
            }
            for edge in measurement.edges
        ],
        "loop": {
            "maximum_canonical_angle_degrees": measurement.loop.maximum_canonical_angle_degrees,
            "angle_uncertainty_degrees": measurement.loop.angle_uncertainty_degrees,
            "det_h_flag": measurement.loop.det_h_flag,
            "measured": measurement.loop.measured,
        },
    }


def capture(call: Any) -> dict[str, Any]:
    try:
        return {"ok": True, "output": call()}
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error_type": type(exc).__name__, "message": str(exc)}


def materialize(raw: dict[str, Any]) -> dict[str, Any]:
    float_input = float_measurement(raw)
    fixed_input = fixed_measurement(raw)
    fixed_budget = q_floor(raw["error_budget"])
    float_path = capture(lambda: predict_control_gate(float_input, raw["error_budget"]))
    fixed_path = capture(lambda: predict_control_gate_fp(fixed_input, fixed_budget))
    if fixed_path["ok"]:
        serialized = canonical_gate_serialization(
            fixed_input, fixed_budget, fixed_path["output"]
        )
    else:
        serialized = canonical_gate_error_serialization(
            fixed_input,
            fixed_budget,
            fixed_path["error_type"],
            fixed_path["message"],
        )
    return {
        "case_id": raw["case_id"],
        "category": raw["category"],
        "raw_inputs": {
            "measurement_id": raw["measurement_id"],
            "edges": raw["edges"],
            "loop": raw["loop"],
            "error_budget": raw["error_budget"],
        },
        "float_path": float_path,
        "fixed_inputs": {
            "measurement": measurement_to_dict(fixed_input),
            "error_budget": fixed_budget,
        },
        "fixed_point": fixed_path,
        "canonical_sha256": sha256(serialized).hexdigest(),
    }


def build_cases() -> list[dict[str, Any]]:
    cases = [
        raw_case("invalid.no_edges", retentions=[], angle=0.0, angle_uncertainty=0.0, det_h_flag=False, measured=True, error_budget=1.0, category="validation"),
        raw_case("invalid.retention_low", retentions=[(-0.01, 0.0)], angle=0.0, angle_uncertainty=0.0, det_h_flag=False, measured=True, error_budget=1.0, category="validation"),
        raw_case("invalid.retention_high", retentions=[(1.01, 0.0)], angle=0.0, angle_uncertainty=0.0, det_h_flag=False, measured=True, error_budget=1.0, category="validation"),
        raw_case("invalid.retention_uncertainty", retentions=[(0.9, -0.01)], angle=0.0, angle_uncertainty=0.0, det_h_flag=False, measured=True, error_budget=1.0, category="validation"),
        raw_case("invalid.angle_uncertainty", retentions=[(0.9, 0.0)], angle=0.0, angle_uncertainty=-0.01, det_h_flag=False, measured=True, error_budget=1.0, category="validation"),
        raw_case("invalid.missing_angle", retentions=[(0.9, 0.0)], angle=None, angle_uncertainty=0.0, det_h_flag=False, measured=True, error_budget=1.0, category="validation"),
        raw_case("invalid.angle_low", retentions=[(0.9, 0.0)], angle=-0.01, angle_uncertainty=0.0, det_h_flag=False, measured=True, error_budget=1.0, category="validation"),
        raw_case("invalid.angle_high", retentions=[(0.9, 0.0)], angle=180.01, angle_uncertainty=0.0, det_h_flag=False, measured=True, error_budget=1.0, category="validation"),
        raw_case("invalid.budget_low", retentions=[(0.9, 0.0)], angle=0.0, angle_uncertainty=0.0, det_h_flag=False, measured=True, error_budget=-0.01, category="validation"),
        raw_case("invalid.budget_high", retentions=[(0.9, 0.0)], angle=0.0, angle_uncertainty=0.0, det_h_flag=False, measured=True, error_budget=2.01, category="validation"),
    ]

    edge_specs = [
        ("angle.zero", [(1.0, 0.0)], 0.0, 0.0, False, True, 0.0),
        ("angle.one_eighty", [(1.0, 0.0)], 180.0, 0.0, False, True, 2.0),
        ("angle.near_clamp", [(1.0, 0.0)], 179.999999, 0.000002, False, True, 2.0),
        ("retention.zero", [(0.0, 0.0)], 0.0, 0.0, False, True, 1.0),
        ("retention.one", [(1.0, 0.0)], 0.0, 0.0, False, True, 0.0),
        ("retention.below_uncertainty", [(0.1, 0.2)], 0.0, 0.0, False, True, 1.0),
        ("override.det_h", [(1.0, 0.0)], None, 0.0, True, True, 2.0),
        ("override.audit_gap", [(1.0, 0.0)], 0.0, 0.0, False, False, 2.0),
        ("override.both", [(0.5, 0.9)], None, 15.0, True, False, 2.0),
    ]
    for case_id, edges, angle, angle_uncertainty, det, measured, budget in edge_specs:
        cases.append(
            raw_case(
                case_id,
                retentions=edges,
                angle=angle,
                angle_uncertainty=angle_uncertainty,
                det_h_flag=det,
                measured=measured,
                error_budget=budget,
                category="edge_case",
            )
        )

    for index in range(12):
        retention = 0.55 + index * 0.025
        angle = 2.0 + index * 3.25
        template = raw_case(
            f"boundary.template.{index}",
            retentions=[(retention, 0.01 + (index % 3) * 0.005)],
            angle=angle,
            angle_uncertainty=0.25,
            det_h_flag=False,
            measured=True,
            error_budget=2.0,
            category="boundary",
        )
        bound = predict_control_gate(float_measurement(template), 2.0)[
            "signed_control_loss_upper_bound"
        ]
        for label, offset in (("below", -Q_ULP), ("equal", 0.0), ("above", Q_ULP)):
            budget = min(2.0, max(0.0, bound + offset))
            cases.append(
                raw_case(
                    f"boundary.{index}.{label}",
                    retentions=[(retention, 0.01 + (index % 3) * 0.005)],
                    angle=angle,
                    angle_uncertainty=0.25,
                    det_h_flag=False,
                    measured=True,
                    error_budget=budget,
                    category="boundary",
                )
            )

    rng = random.Random(SEED)
    for index in range(200):
        edge_count = rng.randint(1, 8)
        retentions = [
            (rng.uniform(0.0, 1.0), rng.uniform(0.0, 1.25))
            for _ in range(edge_count)
        ]
        det = rng.random() < 0.12
        measured = rng.random() >= 0.12
        angle = None if det and rng.random() < 0.8 else rng.uniform(0.0, 180.0)
        cases.append(
            raw_case(
                f"random.{index:03d}",
                retentions=retentions,
                angle=angle,
                angle_uncertainty=rng.uniform(0.0, 90.0),
                det_h_flag=det,
                measured=measured,
                error_budget=rng.uniform(0.0, 2.0),
                category="random",
            )
        )
    return cases


def main() -> int:
    rows = [materialize(case) for case in build_cases()]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(
                json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False)
                + "\n"
            )
    print(f"wrote {len(rows)} vectors to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
