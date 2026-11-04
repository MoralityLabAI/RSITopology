"""Lineage-first graph filtration for admitting holonomy measurements.

Holonomy is defined only after the registered transport graph has been filtered
at a frozen lineage floor.  The cycle rank of that graph, rather than an
arbitrary loop-count threshold, determines whether loop closure is structurally
available.  This module introduces no evidence level beyond the existing
engineering, lineage, and holonomy-clean levels.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class BifiltrationEdge:
    edge_id: str
    source_node: str
    target_node: str
    lineage: float


@dataclass(frozen=True)
class BifiltrationLoop:
    loop_id: str
    edge_ids: tuple[str, ...]


@dataclass(frozen=True)
class LineageHolonomyBifiltration:
    lineage_floor: float
    registered_node_count: int
    admitted_edge_count: int
    connected_component_count: int
    connected_components: tuple[tuple[str, ...], ...]
    component_cycle_ranks: tuple[int, ...]
    beta_1: int
    status: str
    admitted_edge_ids: tuple[str, ...]
    excluded_edge_ids: tuple[str, ...]
    admitted_loop_ids: tuple[str, ...]
    rejected_loops: tuple[Mapping[str, str], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineage_floor": self.lineage_floor,
            "registered_node_count": self.registered_node_count,
            "admitted_edge_count": self.admitted_edge_count,
            "connected_component_count": self.connected_component_count,
            "connected_components": [list(value) for value in self.connected_components],
            "component_cycle_ranks": list(self.component_cycle_ranks),
            "beta_1": self.beta_1,
            "status": self.status,
            "holonomy_clean_possible": self.beta_1 > 0,
            "attestation_cap_when_unavailable": (
                None if self.beta_1 > 0 else "lineage_certified"
            ),
            "admitted_edge_ids": list(self.admitted_edge_ids),
            "excluded_edge_ids": list(self.excluded_edge_ids),
            "admitted_loop_ids": list(self.admitted_loop_ids),
            "rejected_loops": [dict(value) for value in self.rejected_loops],
            "cycle_rank_formula": "beta_1 = |E_tau| - |V| + c(G_tau)",
        }

    def attestation_metadata(self) -> dict[str, Any]:
        """Return the minimal receipt consumed by the attestation cap."""

        return {
            "beta_1": self.beta_1,
            "status": self.status,
            "lineage_floor": self.lineage_floor,
            "admitted_edge_count": self.admitted_edge_count,
            "registered_node_count": self.registered_node_count,
            "connected_component_count": self.connected_component_count,
        }


class _UnionFind:
    def __init__(self, nodes: Sequence[str]) -> None:
        self.parent = {node: node for node in nodes}
        self.size = {node: 1 for node in nodes}

    def find(self, node: str) -> str:
        root = node
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[node] != node:
            following = self.parent[node]
            self.parent[node] = root
            node = following
        return root

    def union(self, first: str, second: str) -> None:
        left = self.find(first)
        right = self.find(second)
        if left == right:
            return
        if self.size[left] < self.size[right]:
            left, right = right, left
        self.parent[right] = left
        self.size[left] += self.size[right]


def _value(item: Any, name: str, *aliases: str) -> Any:
    if isinstance(item, Mapping):
        for key in (name, *aliases):
            if key in item:
                return item[key]
    else:
        for key in (name, *aliases):
            if hasattr(item, key):
                return getattr(item, key)
    raise ValueError(f"receipt is missing {name}")


def _normalize_edge(item: Any) -> BifiltrationEdge:
    edge = BifiltrationEdge(
        edge_id=str(_value(item, "edge_id")),
        source_node=str(_value(item, "source_node")),
        target_node=str(_value(item, "target_node")),
        lineage=float(
            _value(
                item,
                "minimum_edge_worst_direction_retention",
                "worst_direction_retention",
                "lineage",
            )
        ),
    )
    if not edge.edge_id or not edge.source_node or not edge.target_node:
        raise ValueError("edge identifiers and endpoints must be nonempty")
    if not np.isfinite(edge.lineage) or not 0.0 <= edge.lineage <= 1.0:
        raise ValueError(f"edge {edge.edge_id} has invalid lineage")
    return edge


def _normalize_loop(item: Any) -> BifiltrationLoop:
    edge_ids = tuple(
        str(value) for value in _value(item, "edge_ids", "edge_order")
    )
    loop = BifiltrationLoop(
        loop_id=str(_value(item, "loop_id")),
        edge_ids=edge_ids,
    )
    if not loop.loop_id or not loop.edge_ids:
        raise ValueError("loop identifiers and boundaries must be nonempty")
    return loop


def build_lineage_holonomy_bifiltration(
    *,
    edges: Iterable[Any],
    lineage_floor: float,
    loops: Iterable[Any] = (),
    registered_nodes: Iterable[str] = (),
) -> LineageHolonomyBifiltration:
    """Filter transports by lineage, compute components and cycle rank.

    Registered loops are admitted only when every boundary edge survives the
    lineage filter and belongs to one connected component.  A zero cycle rank
    returns ``holonomy_unavailable`` regardless of how many low-lineage loop
    receipts were attempted.
    """

    if not np.isfinite(lineage_floor) or not 0.0 <= lineage_floor <= 1.0:
        raise ValueError("lineage_floor must be finite and in [0, 1]")
    normalized_edges = tuple(_normalize_edge(edge) for edge in edges)
    edge_by_id: dict[str, BifiltrationEdge] = {}
    nodes = {str(node) for node in registered_nodes}
    for edge in normalized_edges:
        if edge.edge_id in edge_by_id:
            raise ValueError(f"duplicate edge_id: {edge.edge_id}")
        edge_by_id[edge.edge_id] = edge
        nodes.add(edge.source_node)
        nodes.add(edge.target_node)
    if not nodes:
        raise ValueError("at least one registered node is required")

    admitted = {
        edge.edge_id: edge
        for edge in normalized_edges
        if edge.lineage >= lineage_floor
    }
    union_find = _UnionFind(sorted(nodes))
    for edge in admitted.values():
        union_find.union(edge.source_node, edge.target_node)

    component_map: dict[str, list[str]] = {}
    for node in sorted(nodes):
        component_map.setdefault(union_find.find(node), []).append(node)
    components = tuple(
        sorted((tuple(sorted(values)) for values in component_map.values()), key=lambda value: value[0])
    )
    component_index = {
        node: index for index, component in enumerate(components) for node in component
    }
    edges_by_component = [0 for _ in components]
    for edge in admitted.values():
        component = component_index[edge.source_node]
        if component != component_index[edge.target_node]:
            raise AssertionError("admitted union-find edge crossed components")
        edges_by_component[component] += 1
    component_cycle_ranks = tuple(
        edges_by_component[index] - len(component) + 1
        for index, component in enumerate(components)
    )
    if any(value < 0 for value in component_cycle_ranks):
        raise AssertionError("component cycle rank cannot be negative")
    beta_1 = len(admitted) - len(nodes) + len(components)
    if beta_1 != sum(component_cycle_ranks):
        raise AssertionError("global and component cycle ranks disagree")

    admitted_loops: list[str] = []
    rejected_loops: list[Mapping[str, str]] = []
    for item in loops:
        loop = _normalize_loop(item)
        missing = [edge_id for edge_id in loop.edge_ids if edge_id not in edge_by_id]
        below = [edge_id for edge_id in loop.edge_ids if edge_id in edge_by_id and edge_id not in admitted]
        if missing:
            rejected_loops.append(
                {"loop_id": loop.loop_id, "reason": "missing_edge_receipt"}
            )
            continue
        if below:
            rejected_loops.append(
                {"loop_id": loop.loop_id, "reason": "edge_below_lineage_floor"}
            )
            continue
        boundary_components = {
            component_index[node]
            for edge_id in loop.edge_ids
            for node in (
                edge_by_id[edge_id].source_node,
                edge_by_id[edge_id].target_node,
            )
        }
        if len(boundary_components) != 1:
            rejected_loops.append(
                {"loop_id": loop.loop_id, "reason": "cross_component_boundary"}
            )
            continue
        if beta_1 == 0:
            rejected_loops.append(
                {"loop_id": loop.loop_id, "reason": "cycle_rank_zero"}
            )
            continue
        admitted_loops.append(loop.loop_id)

    return LineageHolonomyBifiltration(
        lineage_floor=float(lineage_floor),
        registered_node_count=len(nodes),
        admitted_edge_count=len(admitted),
        connected_component_count=len(components),
        connected_components=components,
        component_cycle_ranks=component_cycle_ranks,
        beta_1=beta_1,
        status=(
            "holonomy_structurally_available"
            if beta_1 > 0
            else "holonomy_unavailable"
        ),
        admitted_edge_ids=tuple(sorted(admitted)),
        excluded_edge_ids=tuple(sorted(set(edge_by_id) - set(admitted))),
        admitted_loop_ids=tuple(sorted(admitted_loops)),
        rejected_loops=tuple(sorted(rejected_loops, key=lambda value: value["loop_id"])),
    )
