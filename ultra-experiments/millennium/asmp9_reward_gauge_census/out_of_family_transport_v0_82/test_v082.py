from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


validator = _module("v082_validator_test", HERE / "validate_prereveal_v082.py")
gate = _module("v082_gate_test", HERE / "transport_gate.py")


def _fixture(value: float = 0.8) -> dict:
    cells = []
    for scenario in range(12):
        for target in (0, 1):
            cells.append(
                {
                    "scenario_id": f"s{scenario}",
                    "target": target,
                    "endpoints": {"specificity": {"by_order": [value, value]}},
                }
            )
    return {
        "split": "confirmation",
        "record_count": 528,
        "scenario_count": 12,
        "thresholds": {"endpoint_epsilon": 0.02},
        "instrument": {
            "mechanical_repeat_status": "passed",
            "quotient_admission_status": "passed",
        },
        "local_specificity": {
            "status": "local_response_family_established_on_frozen_registry",
            "scenario_successes": 12,
        },
        "cells": cells,
    }


def _protocol() -> dict:
    return json.loads((HERE / "protocol_v0_82.json").read_text(encoding="utf-8"))


def test_manifest_is_disjoint_and_exact() -> None:
    value = validator.validate(
        HERE / "scenario_manifest_v0_82.json",
        HERE.parent / "context_quotient_response_v0_68" / "scenario_manifest_v0_68.json",
    )
    assert value["new_family_count"] == 12
    assert value["old_family_overlap"] == []
    assert value["record_count"] == 528
    assert value["validation"]["padding_excluded_from_jobs"] is True


def test_planted_transport_passes() -> None:
    result = gate.evaluate_transport(_fixture(0.74), _protocol())
    assert all(row["status"] == "pass" for row in result["gates"].values())


def test_prediction_envelope_can_fail_without_breaking_liveness() -> None:
    analysis = _fixture(1.5)
    result = gate.evaluate_transport(analysis, _protocol())
    assert result["gates"]["L0"]["status"] == "pass"
    assert result["gates"]["T0"]["status"] == "fail"


def test_global_transport_can_fail_separately() -> None:
    analysis = _fixture(0.53)
    result = gate.evaluate_transport(analysis, _protocol())
    assert result["gates"]["T0"]["status"] == "pass"
    assert result["gates"]["G0"]["status"] == "fail"
