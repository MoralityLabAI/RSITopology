"""Deterministic summaries for sealed control-risk boundary receipts."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping


def summarize_boundary_surface(receipt: Mapping[str, Any]) -> dict[str, Any]:
    surface = receipt["boundary_surface"]
    grouped: dict[tuple[int, float], list[Mapping[str, Any]]] = defaultdict(list)
    for row in surface["rows"]:
        grouped[(int(row["edge_count"]), float(row["minimum_edge_retention"]))].append(row)
    summaries = []
    for (edge_count, retention), rows in sorted(grouped.items()):
        rows = sorted(rows, key=lambda row: float(row["holonomy_angle_degrees"]))
        actual = next((float(row["holonomy_angle_degrees"]) for row in rows if row["control_lost"]), None)
        denial = next((float(row["holonomy_angle_degrees"]) for row in rows if not row["authorized"]), None)
        summaries.append(
            {
                "edge_count": edge_count,
                "minimum_edge_retention": retention,
                "first_sampled_actual_control_loss_angle_degrees": actual,
                "first_sampled_gate_denial_angle_degrees": denial,
                "gate_lead_degrees": None if actual is None or denial is None else actual - denial,
            }
        )
    return {
        "schema_version": "1.0.0",
        "source_protocol_id": receipt["protocol_id"],
        "error_budget": surface["error_budget"],
        "analytic_pure_holonomy_boundary_degrees": 28.95502437185985,
        "analytic_pure_lineage_actual_retention_thresholds": {
            "1": 0.25,
            "2": 0.5,
            "4": 0.7071067811865476,
            "6": 0.7937005259840998
        },
        "analytic_pure_lineage_gate_retention_thresholds": {
            "1": 0.25,
            "2": 0.5625,
            "4": 0.765625,
            "6": 0.8402777777777777
        },
        "sampled_boundaries": summaries,
        "false_authorizations": surface["false_authorizations"],
    }

