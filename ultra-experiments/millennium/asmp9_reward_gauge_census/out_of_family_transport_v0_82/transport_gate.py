"""Pure v0.82 transport gates over a v0.68-compatible analysis object."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean, median
from typing import Mapping


def evaluate_transport(analysis: Mapping, protocol: Mapping) -> dict:
    if analysis.get("split") != "confirmation":
        raise ValueError("v0.82 consumes only the confirmation split")
    if int(analysis.get("record_count", -1)) != 528:
        raise ValueError("unexpected record universe")
    if int(analysis.get("scenario_count", -1)) != 12:
        raise ValueError("unexpected scenario universe")

    calibration = protocol["calibration"]
    lower = float(calibration["prediction_envelope_lower"])
    upper = float(calibration["prediction_envelope_upper"])
    common_lower = float(calibration["common_coefficient_interval_lower"])
    common_upper = float(calibration["common_coefficient_interval_upper"])
    epsilon = float(analysis["thresholds"]["endpoint_epsilon"])

    by_scenario: dict[str, list[float]] = defaultdict(list)
    cell_rows = []
    for cell in analysis["cells"]:
        scenario_id = str(cell["scenario_id"])
        values = [
            float(value)
            for value in cell["endpoints"]["specificity"]["by_order"]
        ]
        if len(values) != 2:
            raise ValueError("each target cell requires two display orders")
        by_scenario[scenario_id].extend(values)
        interval_lower = min(values) - epsilon
        interval_upper = max(values) + epsilon
        cell_rows.append(
            {
                "scenario_id": scenario_id,
                "target": int(cell["target"]),
                "specificity_by_order": values,
                "interval_lower": interval_lower,
                "interval_upper": interval_upper,
                "intersects_construction_interval": (
                    interval_lower <= common_upper
                    and interval_upper >= common_lower
                ),
            }
        )

    if len(by_scenario) != 12 or any(len(values) != 4 for values in by_scenario.values()):
        raise ValueError("incomplete target-by-order scenario vectors")

    scenario_rows = []
    for scenario_id in sorted(by_scenario):
        value = mean(by_scenario[scenario_id])
        scenario_rows.append(
            {
                "scenario_id": scenario_id,
                "mean_specificity": value,
                "inside_construction_prediction_envelope": lower <= value <= upper,
                "minimum_specificity": min(by_scenario[scenario_id]),
            }
        )

    envelope_hits = sum(
        row["inside_construction_prediction_envelope"] for row in scenario_rows
    )
    intersection_hits = sum(
        row["intersects_construction_interval"] for row in cell_rows
    )
    gates = {
        "N0": {
            "status": "pass",
            "record_count": 528,
            "scenario_count": 12,
        },
        "I0": {
            "status": (
                "pass"
                if analysis["instrument"]["mechanical_repeat_status"] == "passed"
                and analysis["instrument"]["quotient_admission_status"] == "passed"
                else "fail"
            )
        },
        "L0": {
            "status": (
                "pass"
                if analysis["local_specificity"]["status"]
                == "local_response_family_established_on_frozen_registry"
                else "fail"
            ),
            "scenario_successes": int(
                analysis["local_specificity"]["scenario_successes"]
            ),
            "required": 10,
        },
        "T0": {
            "status": "pass" if envelope_hits >= 10 else "fail",
            "envelope_hits": envelope_hits,
            "required": 10,
            "envelope_lower": lower,
            "envelope_upper": upper,
        },
        "G0": {
            "status": "pass" if intersection_hits == 24 else "fail",
            "intersection_hits": intersection_hits,
            "required": 24,
            "construction_interval_lower": common_lower,
            "construction_interval_upper": common_upper,
        },
    }
    scientific_pass = all(gate["status"] == "pass" for gate in gates.values())
    return {
        "schema_version": "asmp9_out_of_family_transport_analysis_v0_82",
        "gates": gates,
        "provisional_scientific_decision": (
            "out_of_family_response_transport_scientifically_established_pending_R0"
            if scientific_pass
            else "out_of_family_response_transport_not_established"
        ),
        "scenario_rows": scenario_rows,
        "cell_rows": cell_rows,
        "descriptive": {
            "mean_scenario_mean": mean(
                row["mean_specificity"] for row in scenario_rows
            ),
            "median_scenario_mean": median(
                row["mean_specificity"] for row in scenario_rows
            ),
            "maximum_absolute_error_from_construction_center": max(
                abs(
                    row["mean_specificity"]
                    - float(calibration["scenario_mean_center"])
                )
                for row in scenario_rows
            ),
        },
        "R0": "evaluated after the hard-cap wrapper and cleanup receipt exist",
        "claim_boundary": protocol["claim_boundary"],
    }

