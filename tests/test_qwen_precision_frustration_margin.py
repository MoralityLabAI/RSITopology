from __future__ import annotations

import numpy as np
import pytest

from rsi_topology.qwen_precision_filtration_w1 import measure_graph
from rsi_topology.qwen_precision_frustration_margin import (
    budget_gauge_preflight,
    cycle_budget_records,
    edge_angle_degrees_from_retention,
    summarize_graph,
)


def _vector(degrees: float) -> np.ndarray:
    radians = np.radians(degrees)
    return np.asarray([np.cos(radians), np.sin(radians), 0.0])


def _flat() -> dict:
    return {
        (state, f"shard-{column:02d}"): {
            "construction": _vector(0),
            "geometry_validation": _vector(0),
        }
        for state in ("base", "naive_qlora")
        for column in range(4)
    }


def test_edge_angle_inverts_rank_one_retention() -> None:
    assert edge_angle_degrees_from_retention(1.0) == pytest.approx(0.0)
    assert edge_angle_degrees_from_retention(0.25) == pytest.approx(60.0)
    assert edge_angle_degrees_from_retention(0.0) == pytest.approx(90.0)


def test_flat_fixture_is_forced_orientable() -> None:
    summary = summarize_graph(measure_graph(_flat()))
    assert summary["maximum_angle_budget_degrees"] == pytest.approx(0.0)
    assert summary["minimum_frustration_margin_degrees"] == pytest.approx(180.0)
    assert all(row["forced_orientable_point"] for row in summary["cycles"])
    assert all(not row["w1_live_point"] for row in summary["cycles"])


def test_live_negative_fixture_hits_projective_systole() -> None:
    bases = _flat()
    # p0 order: base/00 -> base/01 -> naive/01 -> naive/00 -> base/00.
    assignments = {
        ("base", "shard-00"): 0.0,
        ("base", "shard-01"): 60.0,
        ("naive_qlora", "shard-01"): 120.0,
        ("naive_qlora", "shard-00"): 180.0,
        ("base", "shard-02"): 60.0,
        ("base", "shard-03"): 60.0,
        ("naive_qlora", "shard-02"): 120.0,
        ("naive_qlora", "shard-03"): 120.0,
    }
    for key, angle in assignments.items():
        bases[key] = {
            "construction": _vector(angle),
            "geometry_validation": _vector(angle),
        }
    cycles = {row["cycle_id"]: row for row in cycle_budget_records(measure_graph(bases))}
    p0 = cycles["xor:p0"]
    assert p0["conservative_angle_budget_degrees"] == pytest.approx(180.0)
    assert p0["frustration_margin_degrees"] == pytest.approx(0.0)
    assert p0["geometry_validation_sign"] == -1
    assert p0["w1_live_point"] is True
    assert p0["forced_orientable_point"] is False


def test_budget_liveness_and_sign_are_gauge_invariant() -> None:
    receipt = budget_gauge_preflight(_flat(), reframings=64, seed=14)
    assert receipt["passed"] is True
    assert receipt["mismatches"] == 0
