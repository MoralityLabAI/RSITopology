from __future__ import annotations

import json
from pathlib import Path

from run_verification import render_report


HERE = Path(__file__).resolve().parent


def test_gate_universe_matches_protocol() -> None:
    protocol = json.loads(
        (HERE / "protocol_v0_12.json").read_text(encoding="utf-8")
    )
    assert protocol["gate_ids"] == [
        "G0_registration_binding",
        "G1_exact_counterexample",
        "G2_nested_geometry",
        "G3_exact_repair_radius",
        "G4_query_count_lower_bound",
        "G5_orthonormal_optimum",
        "G6_fresh_coverage",
        "G7_simple_cycle_basis",
        "G8_conditioning_separation_liveness",
        "G9_resource_envelope",
    ]


def test_report_preserves_claim_boundary() -> None:
    report = render_report(
        {
            "verdict": "example",
            "gates": {"G0": True},
            "exact_witness": {
                "certificate": {
                    "obstruction_dimension": 2,
                    "short_amplification_squared": "3/2",
                    "robust_amplification_squared": "1",
                }
            },
            "fresh_cells": {
                "actual_count": 1,
                "dimension_distribution": {"2": 1},
                "shortest_suboptimal_count": 1,
                "maximum_amplification_ratio": 1.2,
            },
            "claim_boundary": "not a resolution",
        }
    )
    assert "not a resolution" in report
