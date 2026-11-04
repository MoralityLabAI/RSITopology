"""Retrospective exact percolation curves over frozen Qwen edge receipts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .bifiltration import build_lineage_holonomy_bifiltration
from .confinement_experiments.common import file_sha256
from .percolation import lineage_percolation_curve


PROTOCOL_ID = "qwen08_percolation_reanalysis_v0_1"


def qwen_edge_class(edge_id: str) -> str:
    return "checkpoint" if ":precision:" in str(edge_id) else "context"


def _site_edges(source: Mapping[str, Any], site: str) -> list[dict[str, Any]]:
    prefix = f"{site}:graph_reachability:r1:"
    values = [item for item in source["edge_receipts"] if str(item["edge_id"]).startswith(prefix)]
    if len(values) != 10:
        raise ValueError(f"{site} does not have the registered ten-edge grid")
    return values


def _site_loops(source: Mapping[str, Any], site: str) -> list[dict[str, Any]]:
    return [item for item in source["loop_receipts"] if item.get("site") == site]


def analyze_site(source: Mapping[str, Any], site: str, *, tolerance: float = 1e-12) -> dict[str, Any]:
    edges = _site_edges(source, site)
    loops = _site_loops(source, site)
    nodes = sorted(
        {str(edge[key]) for edge in edges for key in ("source_node", "target_node")}
    )
    classes = {str(edge["edge_id"]): qwen_edge_class(str(edge["edge_id"])) for edge in edges}
    curve = lineage_percolation_curve(
        edges=edges,
        loops=loops,
        registered_nodes=nodes,
        edge_classes=classes,
    )
    tau_conn = curve.critical_floors.tau_conn
    critical = [] if tau_conn is None else [
        {
            "edge_id": edge["edge_id"],
            "edge_class": classes[edge["edge_id"]],
            "retention": float(edge["worst_direction_retention"]),
        }
        for edge in edges
        if abs(float(edge["worst_direction_retention"]) - tau_conn) <= tolerance
    ]
    floor_zero = next(item for item in curve.floors if item.lineage_floor == 0.0)
    frozen = build_lineage_holonomy_bifiltration(
        edges=edges,
        lineage_floor=0.9,
        loops=loops,
        registered_nodes=nodes,
    )
    return {
        "site": site,
        "curve": curve.to_dict(),
        "critical_floors": curve.critical_floors.to_dict(),
        "critical_connectivity_edges": critical,
        "critical_connectivity_classes": sorted({item["edge_class"] for item in critical}),
        "context_only_connectivity_transition": bool(critical)
        and all(item["edge_class"] == "context" for item in critical),
        "floor_zero_beta_1": floor_zero.beta_1,
        "frozen_floor_state": frozen.to_dict(),
        "edge_retention_ranges": {
            label: [
                min(float(edge["worst_direction_retention"]) for edge in edges if classes[edge["edge_id"]] == label),
                max(float(edge["worst_direction_retention"]) for edge in edges if classes[edge["edge_id"]] == label),
            ]
            for label in ("checkpoint", "context")
        },
    }


def run_reanalysis(protocol_path: str | Path) -> dict[str, Any]:
    path = Path(protocol_path).resolve()
    protocol = json.loads(path.read_text(encoding="utf-8-sig"))
    if protocol.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("unexpected Qwen percolation protocol")
    if protocol.get("new_invariant_levels") is not False:
        raise ValueError("Qwen percolation reanalysis introduces an invariant level")
    source_path = Path(protocol["source"]["path"]).resolve()
    if file_sha256(source_path) != protocol["source"]["sha256"]:
        raise ValueError("Qwen percolation source hash mismatch")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    sites = [analyze_site(source, site) for site in protocol["site_universe"]]
    p1 = all(item["context_only_connectivity_transition"] for item in sites)
    layer15 = next(item for item in sites if item["site"] == "model.layers.15")
    p2 = (
        layer15["floor_zero_beta_1"] > 0
        and layer15["critical_floors"]["tau_cycle"] is not None
        and layer15["critical_floors"]["tau_cycle"] < protocol["frozen_lineage_floor"]
    )
    return {
        "schema_version": "qwen08_percolation_reanalysis_result_v0_1",
        "protocol_sha256": file_sha256(path),
        "source_sha256": file_sha256(source_path),
        "epistemic_status": protocol["epistemic_status"],
        "sites": sites,
        "predictions": {"P1_context_edges_critical": p1, "P2_layer15_threshold_effect": p2},
        "all_predictions_pass": p1 and p2,
        "claim_boundary": protocol["claim_boundary"],
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
        "new_invariant_levels": False,
    }
