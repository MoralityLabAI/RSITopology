from __future__ import annotations

import copy

import pytest

from rsi_topology.confinement_experiments.common import load_config
from rsi_topology.confinement_experiments.suite import (
    evaluate_work_unit,
    generate_work_units,
)
from rsi_topology.percolation import (
    coboundary_distance,
    frustrated_clusters,
    gauge_transform_edge_signs,
    lineage_percolation_curve,
    percolation_phase_point,
    sign_syndrome,
)


def edge(edge_id: str, source: str, target: str, lineage: float = 1.0):
    return {
        "edge_id": edge_id,
        "source_node": source,
        "target_node": target,
        "lineage": lineage,
    }


def test_triangle_one_negative_edge_is_frustrated_at_distance_one():
    edges = [edge("ab", "a", "b"), edge("bc", "b", "c"), edge("ca", "c", "a")]
    point = percolation_phase_point(
        edges=edges,
        loops=[{"loop_id": "triangle", "edge_ids": ["ab", "bc", "ca"]}],
        registered_nodes=["a", "b", "c"],
        edge_signs={"ab": -1, "bc": 1, "ca": 1},
        lineage_floor=1.0,
    )
    assert point.beta_1 == 1
    assert point.phase == "frustrated"
    assert point.syndrome.incidence_rank == 1
    assert point.syndrome.syndrome == (1,)
    assert point.coboundary_distance.exact_distance == 1


def test_four_cycle_two_negative_cut_is_w1_trivial_distance_zero():
    basis = {"square": ("ab", "bc", "cd", "da")}
    signs = {"ab": -1, "bc": 1, "cd": 1, "da": -1}
    syndrome = sign_syndrome(cycle_basis_edge_ids=basis, edge_signs=signs)
    distance = coboundary_distance(cycle_basis_edge_ids=basis, edge_signs=signs)
    assert syndrome.w1_trivial
    assert syndrome.syndrome == (0,)
    assert distance.exact_distance == 0


def test_theta_shared_negative_edge_forms_one_frustrated_cluster():
    basis = {
        "upper": ("shared", "upper-left", "upper-right"),
        "lower": ("shared", "lower-left", "lower-right"),
    }
    signs = {edge_id: 1 for boundary in basis.values() for edge_id in boundary}
    signs["shared"] = -1
    syndrome = sign_syndrome(cycle_basis_edge_ids=basis, edge_signs=signs)
    clusters = frustrated_clusters(syndrome=syndrome, cycle_basis_edge_ids=basis)
    distance = coboundary_distance(cycle_basis_edge_ids=basis, edge_signs=signs)
    assert syndrome.syndrome == (1, 1)
    assert clusters.cluster_count == 1
    assert clusters.cluster_sizes == (2,)
    assert clusters.largest_cluster_fraction == 1.0
    assert distance.exact_distance == 1


def test_node_gauge_flips_leave_phase_receipt_bit_identical():
    edges = [edge("ab", "a", "b"), edge("bc", "b", "c"), edge("ca", "c", "a")]
    signs = {"ab": -1, "bc": 1, "ca": 1}
    common = {
        "edges": edges,
        "loops": [{"loop_id": "triangle", "edge_ids": ["ab", "bc", "ca"]}],
        "registered_nodes": ["a", "b", "c"],
        "lineage_floor": 1.0,
    }
    original = percolation_phase_point(edge_signs=signs, **common)
    reframed = gauge_transform_edge_signs(
        edges=edges,
        edge_signs=signs,
        node_flips={"a": -1, "b": 1, "c": -1},
    )
    transformed = percolation_phase_point(edge_signs=reframed, **common)
    assert transformed.to_dict() == original.to_dict()


def test_curve_is_exact_and_cycle_can_precede_global_connectivity():
    # The triangle closes at 0.7 while node d is not connected until 0.6.
    # This is the counterexample to the tempting but false tau_cycle <= tau_conn axiom.
    edges = [
        edge("ab", "a", "b", 0.9),
        edge("bc", "b", "c", 0.8),
        edge("ca", "c", "a", 0.7),
        edge("cd", "c", "d", 0.6),
        edge("da", "d", "a", 0.5),
    ]
    curve = lineage_percolation_curve(
        edges=edges,
        loops=[{"loop_id": "abc", "edge_ids": ["ab", "bc", "ca"]}],
        registered_nodes=["a", "b", "c", "d"],
    )
    table = {
        item.lineage_floor: (
            item.admitted_edge_count,
            item.connected_component_count,
            item.beta_1,
            item.admitted_registered_loop_count,
        )
        for item in curve.floors
    }
    assert table == {
        1.0: (0, 4, 0, 0),
        0.9: (1, 3, 0, 0),
        0.8: (2, 2, 0, 0),
        0.7: (3, 2, 1, 1),
        0.6: (4, 1, 1, 1),
        0.5: (5, 1, 2, 1),
        0.0: (5, 1, 2, 1),
    }
    assert curve.critical_floors.tau_loop == 0.7
    assert curve.critical_floors.tau_cycle == 0.7
    assert curve.critical_floors.tau_conn == 0.6
    assert curve.critical_floors.tau_loop <= curve.critical_floors.tau_cycle
    assert curve.critical_floors.tau_cycle > curve.critical_floors.tau_conn


def test_edge_class_null_surface_is_explicit_and_exact():
    edges = [edge("a", "n0", "n1", 0.9), edge("b", "n1", "n2", 0.4)]
    curve = lineage_percolation_curve(
        edges=edges,
        registered_nodes=["n0", "n1", "n2"],
        edge_classes={"a": "checkpoint", "b": "context"},
    )
    assert set(curve.by_edge_class) == {"checkpoint", "context"}
    assert curve.critical_floors.tau_conn == 0.4
    assert curve.by_edge_class["checkpoint"].tau_conn is None
    assert curve.by_edge_class["context"].tau_conn is None


def test_degenerate_guards():
    with pytest.raises(ValueError, match="at least one edge"):
        lineage_percolation_curve(edges=[], registered_nodes=["a"])
    with pytest.raises(ValueError, match="duplicate edge_id"):
        lineage_percolation_curve(
            edges=[edge("x", "a", "b"), edge("x", "b", "c")]
        )
    with pytest.raises(ValueError, match="invalid lineage"):
        lineage_percolation_curve(edges=[edge("x", "a", "b", 1.01)])
    with pytest.raises(ValueError, match="exact edge universe"):
        lineage_percolation_curve(
            edges=[edge("x", "a", "b")], edge_classes={"missing": "context"}
        )


def test_smoke_work_units_share_graph_disorder_and_keep_nulls_named():
    config = load_config("configs/smoke/07_percolation_phase.yaml")
    units = generate_work_units(config)
    assert len(units) == 24
    assert {unit.payload["retention_arm"] for unit in units} == {
        "observed",
        "pooled_retention_permutation",
        "within_class_retention_permutation",
    }
    assert len({unit.payload["graph_seed"] for unit in units}) == 2
    by_replicate = {}
    for unit in units:
        by_replicate.setdefault(unit.payload["graph_replicate"], []).append(unit)
    for values in by_replicate.values():
        assert len({item.payload["graph_seed"] for item in values}) == 1
        assert len({item.payload["sign_draw_seed"] for item in values}) == 1


def test_one_experiment_cell_is_rederivable_and_diagnostic_only():
    config = load_config("configs/smoke/07_percolation_phase.yaml")
    unit = next(
        value
        for value in generate_work_units(config)
        if value.payload["retention_arm"] == "observed"
        and value.payload["lineage_floor"] == 0.85
        and value.payload["q"] == 0.0
    )
    row = evaluate_work_unit(unit)
    assert row["phase"] == "coherent"
    assert row["w1_trivial"] is True
    assert row["attestation_effect"] == "diagnostic_only_no_new_level"
    assert row["tau_loop"] <= row["tau_cycle"]
