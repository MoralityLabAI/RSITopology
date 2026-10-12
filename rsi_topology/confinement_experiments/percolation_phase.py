"""Synthetic rectangular lineage/sign-percolation phase cells."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from ..percolation import lineage_percolation_curve, percolation_phase_point


def rectangular_transport_fixture(
    *,
    layers: int,
    context_columns: int,
    checkpoint_mean: float,
    checkpoint_sd: float,
    context_mean: float,
    context_sd: float,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str], dict[str, str]]:
    """Build an L-by-C transport grid with elementary plaquettes."""

    if layers < 2 or context_columns < 2:
        raise ValueError("rectangular fixture requires at least 2x2 nodes")
    for name, mean, sd in (
        ("checkpoint", checkpoint_mean, checkpoint_sd),
        ("context", context_mean, context_sd),
    ):
        if not 0.0 <= mean <= 1.0 or sd < 0.0:
            raise ValueError(f"invalid {name} retention distribution")
    rng = np.random.default_rng(seed)
    nodes = [f"state-{row:02d}/context-{column:02d}" for row in range(layers) for column in range(context_columns)]
    edges: list[dict[str, Any]] = []
    classes: dict[str, str] = {}

    def add(edge_id: str, source: str, target: str, label: str, mean: float, sd: float) -> None:
        retention = float(np.clip(rng.normal(mean, sd), 0.0, 1.0))
        edges.append(
            {
                "edge_id": edge_id,
                "source_node": source,
                "target_node": target,
                "lineage": retention,
            }
        )
        classes[edge_id] = label

    for row in range(layers):
        for column in range(context_columns - 1):
            add(
                f"context:r{row:02d}:c{column:02d}-{column + 1:02d}",
                f"state-{row:02d}/context-{column:02d}",
                f"state-{row:02d}/context-{column + 1:02d}",
                "context",
                context_mean,
                context_sd,
            )
    for row in range(layers - 1):
        for column in range(context_columns):
            add(
                f"checkpoint:r{row:02d}-{row + 1:02d}:c{column:02d}",
                f"state-{row:02d}/context-{column:02d}",
                f"state-{row + 1:02d}/context-{column:02d}",
                "checkpoint",
                checkpoint_mean,
                checkpoint_sd,
            )
    loops = []
    for row in range(layers - 1):
        for column in range(context_columns - 1):
            loops.append(
                {
                    "loop_id": f"plaquette:r{row:02d}:c{column:02d}",
                    "edge_ids": [
                        f"context:r{row:02d}:c{column:02d}-{column + 1:02d}",
                        f"checkpoint:r{row:02d}-{row + 1:02d}:c{column + 1:02d}",
                        f"context:r{row + 1:02d}:c{column:02d}-{column + 1:02d}",
                        f"checkpoint:r{row:02d}-{row + 1:02d}:c{column:02d}",
                    ],
                }
            )
    return edges, loops, nodes, classes


def _permuted_retentions(
    edges: list[dict[str, Any]],
    edge_classes: Mapping[str, str],
    *,
    arm: str,
    seed: int,
) -> list[dict[str, Any]]:
    if arm == "observed":
        return [dict(item) for item in edges]
    rng = np.random.default_rng(seed)
    output = [dict(item) for item in edges]
    if arm == "pooled_retention_permutation":
        values = np.asarray([item["lineage"] for item in output])
        rng.shuffle(values)
        for item, value in zip(output, values):
            item["lineage"] = float(value)
        return output
    if arm == "within_class_retention_permutation":
        for label in sorted(set(edge_classes.values())):
            indices = [
                index for index, item in enumerate(output)
                if edge_classes[item["edge_id"]] == label
            ]
            values = np.asarray([output[index]["lineage"] for index in indices])
            rng.shuffle(values)
            for index, value in zip(indices, values):
                output[index]["lineage"] = float(value)
        return output
    raise ValueError(f"unknown retention arm: {arm}")


def evaluate_percolation_cell(payload: Mapping[str, Any], *, seed: int) -> dict[str, Any]:
    """Evaluate one independently receipted synthetic phase cell."""

    edges, loops, nodes, edge_classes = rectangular_transport_fixture(
        layers=int(payload["layers"]),
        context_columns=int(payload["context_columns"]),
        checkpoint_mean=float(payload["checkpoint_mean"]),
        checkpoint_sd=float(payload["checkpoint_sd"]),
        context_mean=float(payload["context_mean"]),
        context_sd=float(payload["context_sd"]),
        seed=int(payload["graph_seed"]),
    )
    arm = str(payload["retention_arm"])
    edges = _permuted_retentions(
        edges,
        edge_classes,
        arm=arm,
        seed=int(payload["retention_permutation_seed"]),
    )
    q = float(payload["q"])
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must lie in [0,1]")
    # The same uniforms are reused across q for one graph replicate, making
    # the sign-noise exposure nested rather than replacing the graph at every q.
    sign_rng = np.random.default_rng(int(payload["sign_draw_seed"]))
    uniforms = sign_rng.random(len(edges))
    edge_signs = {
        item["edge_id"]: (-1 if value < q else 1)
        for item, value in zip(edges, uniforms)
    }
    point = percolation_phase_point(
        edges=edges,
        loops=loops,
        registered_nodes=nodes,
        edge_signs=edge_signs,
        lineage_floor=float(payload["lineage_floor"]),
    )
    curve = lineage_percolation_curve(
        edges=edges,
        loops=loops,
        registered_nodes=nodes,
        edge_classes=edge_classes,
    )
    critical = curve.critical_floors
    class_critical = {
        key: value.to_dict() for key, value in curve.by_edge_class.items()
    }
    if (
        critical.tau_loop is not None
        and critical.tau_cycle is not None
        and critical.tau_loop > critical.tau_cycle + 1e-15
    ):
        raise AssertionError("tau_loop exceeded tau_cycle")
    exact = point.coboundary_distance.exact_distance
    return {
        **dict(payload),
        "evaluation_seed": int(seed),
        "phase": point.phase,
        "admitted_edge_count": point.admitted_edge_count,
        "connected_component_count": point.connected_component_count,
        "largest_component_fraction": point.largest_component_fraction,
        "beta_1": point.beta_1,
        "admitted_registered_loop_count": point.admitted_registered_loop_count,
        "w1_trivial": point.syndrome.w1_trivial,
        "frustrated_cycle_count": len(point.syndrome.frustrated_cycle_ids),
        "largest_frustrated_cluster_fraction": point.frustrated_clusters.largest_cluster_fraction,
        "coboundary_distance": exact if exact is not None else point.coboundary_distance.upper_bound,
        "coboundary_distance_mode": point.coboundary_distance.mode,
        "coboundary_distance_lower": point.coboundary_distance.lower_bound,
        "coboundary_distance_upper": point.coboundary_distance.upper_bound,
        "negative_edge_count": sum(value < 0 for value in edge_signs.values()),
        "edge_count": len(edges),
        "tau_conn": critical.tau_conn,
        "tau_cycle": critical.tau_cycle,
        "tau_loop": critical.tau_loop,
        "critical_floors_by_edge_class": class_critical,
        "curve_receipt": curve.to_dict(),
        "evidence_label": "synthetic_model_only_phase_calibration",
        "attestation_effect": "diagnostic_only_no_new_level",
    }
