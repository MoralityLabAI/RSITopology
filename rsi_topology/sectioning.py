"""Holonomy-bounded edit sectioning over context-by-checkpoint grids.

Holonomy remains the terminal invariant.  This module only turns registered
edge and plaquette receipts into operational patches, persistence receipts,
and audit priorities for existing consumers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .attestation import AnchorRegistry, AttestationPolicy, HOLONOMY_CLEAN, array_sha256


@dataclass(frozen=True)
class GridEdgeReceipt:
    edge_id: str
    source_node: str
    target_node: str
    transport_matrix: tuple[tuple[float, ...], ...]
    mean_edge_chordal_lineage: float
    minimum_edge_worst_direction_retention: float


@dataclass(frozen=True)
class PlaquetteReceipt:
    plaquette_id: str
    row: int
    column: int
    node_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    measured: bool
    identity_loss: float | None
    identity_loss_lower_bound: float
    identity_loss_upper_bound: float
    det_h_flag: bool
    determinant_reversal_probability: float = 0.0


@dataclass(frozen=True)
class SectioningInput:
    grid_id: str
    rank: int
    edges: tuple[GridEdgeReceipt, ...]
    plaquettes: tuple[PlaquetteReceipt, ...]
    reference_coordinate: tuple[float, ...]


def section_edits(receipts: SectioningInput, holonomy_budget: float) -> dict[str, Any]:
    """Return maximal connected patches of measured, budget-clean plaquettes."""
    _validate_input(receipts)
    if not np.isfinite(holonomy_budget) or holonomy_budget < 0:
        raise ValueError("holonomy_budget must be finite and nonnegative")
    policy = AttestationPolicy()
    edge_by_id = {edge.edge_id: edge for edge in receipts.edges}

    def lineage_clean(cell: PlaquetteReceipt) -> bool:
        return all(
            edge_by_id[edge_id].mean_edge_chordal_lineage
            >= policy.minimum_mean_edge_chordal_lineage
            and edge_by_id[edge_id].minimum_edge_worst_direction_retention
            >= policy.minimum_edge_worst_direction_retention
            for edge_id in cell.edge_ids
        )

    admissible = {
        item.plaquette_id: item
        for item in receipts.plaquettes
        if item.measured
        and not item.det_h_flag
        and lineage_clean(item)
        and item.identity_loss_upper_bound <= holonomy_budget
    }
    components = _cell_components(tuple(admissible.values()))
    patches = [
        _build_patch(receipts, cells, holonomy_budget, index)
        for index, cells in enumerate(components)
    ]
    if not patches:
        status = "no_admissible_multi_patch_section"
    elif len(patches) == 1:
        status = "single_flat_patch"
    else:
        status = "multi_patch_section"
    excluded = []
    for cell in sorted(receipts.plaquettes, key=lambda item: item.plaquette_id):
        if cell.plaquette_id in admissible:
            continue
        if not cell.measured:
            reason = "unmeasured"
        elif cell.det_h_flag:
            reason = "orientation_reversal"
        elif not lineage_clean(cell):
            reason = "edge_lineage_below_threshold"
        else:
            reason = "holonomy_budget_exceeded"
        excluded.append({"plaquette_id": cell.plaquette_id, "reason": reason})
    return {
        "schema_version": "1.0.0",
        "grid_id": receipts.grid_id,
        "holonomy_budget": holonomy_budget,
        "status": status,
        "edit_count": len(patches),
        "patches": patches,
        "excluded_plaquettes": excluded,
        "claim_boundary": (
            "Worst-case bounds range over registered elementary plaquettes in each patch; "
            "they do not certify unmeasured or arbitrary composite loops."
        ),
    }


def _cell_components(cells: Sequence[PlaquetteReceipt]) -> list[tuple[PlaquetteReceipt, ...]]:
    by_position = {(item.row, item.column): item for item in cells}
    unseen = set(by_position)
    output = []
    while unseen:
        seed = min(unseen)
        stack = [seed]
        unseen.remove(seed)
        component = []
        while stack:
            position = stack.pop()
            component.append(by_position[position])
            row, column = position
            for neighbor in ((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
        output.append(tuple(sorted(component, key=lambda item: item.plaquette_id)))
    return sorted(output, key=lambda values: values[0].plaquette_id)


def _build_patch(
    receipts: SectioningInput,
    cells: tuple[PlaquetteReceipt, ...],
    budget: float,
    index: int,
) -> dict[str, Any]:
    cell_ids = tuple(item.plaquette_id for item in cells)
    node_ids = tuple(sorted({node for item in cells for node in item.node_ids}))
    anchor_node = node_ids[0]
    coordinates, paths = _transport_patch_coordinate(receipts, node_ids, anchor_node)
    bound = max(item.identity_loss_upper_bound for item in cells)
    edge_by_id = {edge.edge_id: edge for edge in receipts.edges}
    patch_edge_ids = tuple(sorted({edge_id for item in cells for edge_id in item.edge_ids}))
    patch_edges = [edge_by_id[edge_id] for edge_id in patch_edge_ids]
    policy = AttestationPolicy()
    patch_hash = sha256("\n".join(cell_ids).encode()).hexdigest()[:16]
    coordinate_payload = np.vstack([coordinates[node] for node in node_ids])
    return {
        "patch_id": f"patch-{index:03d}-{patch_hash}",
        "plaquette_ids": list(cell_ids),
        "node_ids": list(node_ids),
        "anchor_node": anchor_node,
        "spanning_tree_paths": {node: paths[node] for node in node_ids},
        "transported_edit_coordinates": {
            node: coordinates[node].tolist() for node in node_ids
        },
        "transported_coordinate_sha256": array_sha256(coordinate_payload),
        "edge_receipt_ids": list(patch_edge_ids),
        "minimum_mean_edge_chordal_lineage": min(
            edge.mean_edge_chordal_lineage for edge in patch_edges
        ),
        "minimum_edge_worst_direction_retention": min(
            edge.minimum_edge_worst_direction_retention for edge in patch_edges
        ),
        "mean_edge_lineage_margin": min(
            edge.mean_edge_chordal_lineage for edge in patch_edges
        )
        - policy.minimum_mean_edge_chordal_lineage,
        "worst_direction_lineage_margin": min(
            edge.minimum_edge_worst_direction_retention for edge in patch_edges
        )
        - policy.minimum_edge_worst_direction_retention,
        "worst_case_registered_loop_identity_loss_bound": bound,
        "holonomy_margin": budget - bound,
        "det_h_flag": any(item.det_h_flag for item in cells),
        "required_certification": HOLONOMY_CLEAN,
    }


def _transport_patch_coordinate(
    receipts: SectioningInput, node_ids: tuple[str, ...], anchor: str
) -> tuple[dict[str, np.ndarray], dict[str, list[str]]]:
    allowed = set(node_ids)
    adjacency: dict[str, list[tuple[str, str, np.ndarray]]] = {node: [] for node in node_ids}
    for edge in receipts.edges:
        if edge.source_node not in allowed or edge.target_node not in allowed:
            continue
        matrix = np.asarray(edge.transport_matrix, dtype=np.float64)
        adjacency[edge.source_node].append((edge.target_node, edge.edge_id, matrix))
        adjacency[edge.target_node].append((edge.source_node, edge.edge_id, matrix.T))
    coordinate = np.asarray(receipts.reference_coordinate, dtype=np.float64)
    coordinate = coordinate / np.linalg.norm(coordinate)
    values = {anchor: coordinate}
    paths = {anchor: []}
    queue = [anchor]
    while queue:
        source = queue.pop(0)
        for target, edge_id, transport in sorted(adjacency[source], key=lambda item: (item[0], item[1])):
            if target in values:
                continue
            values[target] = transport @ values[source]
            paths[target] = paths[source] + [edge_id]
            queue.append(target)
    missing = sorted(allowed - set(values))
    if missing:
        raise ValueError(f"patch transport graph is disconnected: {missing}")
    return values, paths


def persistence_curve(receipts: SectioningInput, budgets: Iterable[float]) -> dict[str, Any]:
    values = tuple(sorted(set(float(value) for value in budgets)))
    if not values or any(not np.isfinite(value) or value < 0 for value in values):
        raise ValueError("budgets must be finite nonnegative values")
    active: dict[str, dict[str, Any]] = {}
    lifetimes: dict[str, dict[str, Any]] = {}
    rows = []
    next_id = 0
    for budget in values:
        plan = section_edits(receipts, budget)
        current_sets = [frozenset(patch["plaquette_ids"]) for patch in plan["patches"]]
        new_active: dict[str, dict[str, Any]] = {}
        for cells in current_sets:
            overlapping = sorted(
                (component_id for component_id, item in active.items() if cells & item["cells"]),
                key=lambda component_id: (lifetimes[component_id]["birth_budget"], component_id),
            )
            if not overlapping:
                component_id = f"component-{next_id:04d}"
                next_id += 1
                lifetimes[component_id] = {
                    "component_id": component_id,
                    "birth_budget": budget,
                    "death_budget": None,
                    "merged_into": None,
                    "cells_at_birth": sorted(cells),
                    "cells_at_death": None,
                }
            else:
                component_id = overlapping[0]
                for dying in overlapping[1:]:
                    lifetimes[dying]["death_budget"] = budget
                    lifetimes[dying]["merged_into"] = component_id
                    lifetimes[dying]["cells_at_death"] = sorted(active[dying]["cells"])
            new_active[component_id] = {"cells": cells}
        active = new_active
        rows.append(
            {
                "holonomy_budget": budget,
                "edit_count": len(current_sets),
                "admissible_plaquette_count": sum(len(item) for item in current_sets),
                "active_component_ids": sorted(active),
            }
        )
    return {
        "schema_version": "1.0.0",
        "grid_id": receipts.grid_id,
        "curve": rows,
        "component_birth_death_receipts": sorted(lifetimes.values(), key=lambda item: item["component_id"]),
    }


def rank_audit_placements(receipts: SectioningInput, holonomy_budget: float) -> dict[str, Any]:
    """Rank unmeasured plaquettes by expected patch-boundary uncertainty reduction."""
    base = section_edits(receipts, holonomy_budget)
    measured_components = [set(item["plaquette_ids"]) for item in base["patches"]]
    measured_by_position = {
        (item.row, item.column): item
        for item in receipts.plaquettes
        if item.measured and not item.det_h_flag and item.identity_loss_upper_bound <= holonomy_budget
    }
    rows = []
    for item in receipts.plaquettes:
        if item.measured:
            continue
        lower, upper = item.identity_loss_lower_bound, item.identity_loss_upper_bound
        if upper <= lower:
            probability_flat = float(upper <= holonomy_budget)
        else:
            probability_flat = float(np.clip((holonomy_budget - lower) / (upper - lower), 0.0, 1.0))
        probability_flat *= 1.0 - item.determinant_reversal_probability
        classification_uncertainty = 4.0 * probability_flat * (1.0 - probability_flat)
        neighbor_positions = (
            (item.row - 1, item.column),
            (item.row + 1, item.column),
            (item.row, item.column - 1),
            (item.row, item.column + 1),
        )
        neighboring_cells = {
            measured_by_position[position].plaquette_id
            for position in neighbor_positions
            if position in measured_by_position
        }
        touched_components = sum(bool(component & neighboring_cells) for component in measured_components)
        boundary_impact = 1 + max(0, touched_components - 1)
        expected_reduction = classification_uncertainty * boundary_impact
        rows.append(
            {
                "plaquette_id": item.plaquette_id,
                "expected_boundary_uncertainty_reduction": expected_reduction,
                "probability_budget_clean": probability_flat,
                "classification_uncertainty": classification_uncertainty,
                "boundary_impact": boundary_impact,
                "touched_patch_count": touched_components,
                "identity_loss_interval": [lower, upper],
                "determinant_reversal_probability": item.determinant_reversal_probability,
            }
        )
    rows.sort(key=lambda row: (-row["expected_boundary_uncertainty_reduction"], row["plaquette_id"]))
    for rank, row in enumerate(rows, start=1):
        row["audit_rank"] = rank
    return {
        "schema_version": "1.0.0",
        "grid_id": receipts.grid_id,
        "holonomy_budget": holonomy_budget,
        "current_patch_count": base["edit_count"],
        "audit_ranking": rows,
    }


def authorize_patch(
    patch: Mapping[str, Any],
    registry: AnchorRegistry,
    node_to_site: Mapping[str, str],
) -> dict[str, Any]:
    certificates = []
    for node in patch["node_ids"]:
        site_id = node_to_site[node]
        certificate = registry.certify(site_id, requested_use="disparate_weight_edit")
        certificates.append(certificate)
    authorized = (
        patch["holonomy_margin"] >= 0
        and not patch["det_h_flag"]
        and all(item.authorized and item.certification_level == HOLONOMY_CLEAN for item in certificates)
    )
    return {
        "patch_id": patch["patch_id"],
        "consumer": "hrmmmm_control_harness",
        "authorized": authorized,
        "site_certificates": [item.to_dict() for item in certificates],
        "failures": [] if authorized else ["patch_or_site_not_holonomy_clean"],
    }


def sectioning_input_from_dict(value: Mapping[str, Any]) -> SectioningInput:
    return SectioningInput(
        grid_id=value["grid_id"],
        rank=int(value["rank"]),
        edges=tuple(GridEdgeReceipt(**item) for item in value["edges"]),
        plaquettes=tuple(
            PlaquetteReceipt(
                **{
                    **item,
                    "node_ids": tuple(item["node_ids"]),
                    "edge_ids": tuple(item["edge_ids"]),
                }
            )
            for item in value["plaquettes"]
        ),
        reference_coordinate=tuple(value["reference_coordinate"]),
    )


def _validate_input(receipts: SectioningInput) -> None:
    if receipts.rank < 1 or len(receipts.reference_coordinate) != receipts.rank:
        raise ValueError("rank and reference coordinate disagree")
    if not receipts.plaquettes:
        raise ValueError("at least one plaquette receipt is required")
    edge_ids: set[str] = set()
    for edge in receipts.edges:
        if edge.edge_id in edge_ids:
            raise ValueError(f"duplicate edge_id: {edge.edge_id}")
        edge_ids.add(edge.edge_id)
        matrix = np.asarray(edge.transport_matrix, dtype=np.float64)
        if matrix.shape != (receipts.rank, receipts.rank):
            raise ValueError(f"edge {edge.edge_id} transport rank mismatch")
        if not np.allclose(matrix.T @ matrix, np.eye(receipts.rank), atol=1e-8):
            raise ValueError(f"edge {edge.edge_id} transport is not orthogonal")
        lineage_values = (
            edge.mean_edge_chordal_lineage,
            edge.minimum_edge_worst_direction_retention,
        )
        if not all(np.isfinite(lineage_values)) or not all(0.0 <= value <= 1.0 for value in lineage_values):
            raise ValueError(f"edge {edge.edge_id} has invalid lineage metrics")
    cell_ids: set[str] = set()
    positions: set[tuple[int, int]] = set()
    for item in receipts.plaquettes:
        if item.plaquette_id in cell_ids or (item.row, item.column) in positions:
            raise ValueError("duplicate plaquette identifier or position")
        cell_ids.add(item.plaquette_id)
        positions.add((item.row, item.column))
        if not set(item.edge_ids) <= edge_ids:
            raise ValueError(f"plaquette {item.plaquette_id} references unknown edge")
        if not (0 <= item.identity_loss_lower_bound <= item.identity_loss_upper_bound <= 2.0):
            raise ValueError(f"plaquette {item.plaquette_id} has invalid loss interval")
        if item.measured and item.identity_loss is None:
            raise ValueError(f"measured plaquette {item.plaquette_id} lacks identity_loss")
        if item.measured and not (
            item.identity_loss_lower_bound <= float(item.identity_loss) <= item.identity_loss_upper_bound
        ):
            raise ValueError(f"plaquette {item.plaquette_id} measured loss lies outside its interval")
        if not 0 <= item.determinant_reversal_probability <= 1:
            raise ValueError("determinant reversal probability must lie in [0,1]")
        if len(item.node_ids) != len(item.edge_ids) or len(item.node_ids) < 3:
            raise ValueError(f"plaquette {item.plaquette_id} boundary is incomplete")
        product = np.eye(receipts.rank, dtype=np.float64)
        edge_by_id = {edge.edge_id: edge for edge in receipts.edges}
        targets = item.node_ids[1:] + item.node_ids[:1]
        for source, target, edge_id in zip(item.node_ids, targets, item.edge_ids):
            edge = edge_by_id[edge_id]
            matrix = np.asarray(edge.transport_matrix, dtype=np.float64)
            if edge.source_node == source and edge.target_node == target:
                transport = matrix
            elif edge.source_node == target and edge.target_node == source:
                transport = matrix.T
            else:
                raise ValueError(f"plaquette {item.plaquette_id} edge {edge_id} breaks boundary order")
            product = transport @ product
        computed_det_flag = bool(np.linalg.det(product) < 0.0)
        if computed_det_flag != item.det_h_flag:
            raise ValueError(f"plaquette {item.plaquette_id} determinant flag disagrees with transports")
        if item.measured:
            computed_loss = float(1.0 - np.trace(product) / receipts.rank)
            if not np.isclose(computed_loss, float(item.identity_loss), atol=1e-8):
                raise ValueError(f"plaquette {item.plaquette_id} loss disagrees with boundary holonomy")
