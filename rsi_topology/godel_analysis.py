"""Replayable Godel Globes v0.1 identity-geometry analysis.

This module contains no model code and accepts no behavioral outcomes.  It
turns sealed activation chunks into v0.3 rank filtrations, lineage-first graph
receipts, measured elementary holonomy, patch plans, attestations, audit
placements, and the JSONL contract consumed by the static Godel globe.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .attestation import (
    ENGINEERING_EVIDENCE,
    AnchorRecord,
    AnchorRegistry,
    AttestationPolicy,
    EdgeReceipt,
    HolonomyBudget,
    LoopReceipt,
    array_sha256,
)
from .bifiltration import build_lineage_holonomy_bifiltration
from .discovery import (
    CrossFittedRankFiltration,
    _between_class_scatter_basis,
    discover_between_class_rank_filtration,
    subspace_lineage,
)
from .godel_capture import (
    CaptureStore,
    canonical_json_bytes,
    canonical_json_sha256,
    prompt_rows_for_chunk,
    sha256_file,
    write_once_or_equal,
)
from .holonomy import (
    canonical_rotation_angles_degrees,
    holonomy_orientation_receipt,
    loop_holonomy,
    procrustes_transport,
)
from .sectioning import (
    GridEdgeReceipt,
    PlaquetteReceipt,
    SectioningInput,
    persistence_curve,
    rank_audit_placements,
    section_edits,
)


ANALYSIS_SCHEMA = "godel_globes_analysis_v0_1"


def _stable_seed(seed: int, *values: str) -> int:
    payload = "\0".join(map(str, values)).encode("utf-8")
    return (seed + int.from_bytes(hashlib.sha256(payload).digest()[:4], "big")) % (2**32)


def _layer_from_site(site: str) -> int:
    tokens = site.split(".")
    try:
        index = tokens.index("layers")
        return int(tokens[index + 1])
    except (ValueError, IndexError):
        digits = "".join(character if character.isdigit() else " " for character in site)
        values = [int(item) for item in digits.split()]
        return values[0] if values else 0


def node_id(runtime: str, site: str, family: str, shard: str, rank: int) -> str:
    return f"{runtime}/L{_layer_from_site(site)}/{family}/{shard}/rank-{rank}"


def classify_runtime_support(runtime_supported_ranks: Mapping[str, int]) -> tuple[int, str]:
    """Return the common rank and the frozen precision-axis status."""

    if not runtime_supported_ranks:
        raise ValueError("at least one runtime rank is required")
    values = [int(value) for value in runtime_supported_ranks.values()]
    if any(value < 0 for value in values):
        raise ValueError("runtime supported ranks must be nonnegative")
    common = min(values)
    if common > 0:
        return common, "cross_runtime_supported"
    if any(value > 0 for value in values):
        return 0, "runtime_specific_identity"
    return 0, "no_supported_identity_rank"


def _orthogonal_hash(matrix: np.ndarray) -> str:
    return array_sha256(np.asarray(matrix, dtype=np.float64))


@dataclass
class NodeGeometry:
    runtime: str
    site: str
    family: str
    shard: str
    filtration: CrossFittedRankFiltration

    @property
    def supported_rank(self) -> int:
        return self.filtration.supported_rank

    def basis(self, half: str, rank: int) -> np.ndarray:
        if rank < 1 or rank > self.filtration.maximum_rank:
            raise ValueError("rank is outside the node filtration")
        item = self.filtration.objects[rank - 1]
        index = 0 if half == "construction" else 1
        return np.asarray(item.basis_by_half[index], dtype=np.float64)

    def receipt(self) -> dict[str, Any]:
        return {
            "runtime_precision": self.runtime,
            "site_id": self.site,
            "behavior_family": self.family,
            "context_shard": self.shard,
            **self.filtration.receipt(),
        }


@dataclass
class PhysicalEdge:
    edge_id: str
    source_node: str
    target_node: str
    construction_transport: np.ndarray
    validation_transport: np.ndarray
    construction_lineage: Mapping[str, float | int]
    validation_lineage: Mapping[str, float | int]
    mean_edge_chordal_lineage: float
    minimum_edge_worst_direction_retention: float
    rank: int

    def grid_receipt(self) -> GridEdgeReceipt:
        return GridEdgeReceipt(
            edge_id=self.edge_id,
            source_node=self.source_node,
            target_node=self.target_node,
            transport_matrix=tuple(
                tuple(float(value) for value in row)
                for row in self.validation_transport
            ),
            mean_edge_chordal_lineage=self.mean_edge_chordal_lineage,
            minimum_edge_worst_direction_retention=(
                self.minimum_edge_worst_direction_retention
            ),
        )

    def globe_receipt(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "mean_chordal_lineage": self.mean_edge_chordal_lineage,
            "worst_direction_retention": self.minimum_edge_worst_direction_retention,
            "rank": self.rank,
            "transport_hash": _orthogonal_hash(self.validation_transport),
            "construction_transport_hash": _orthogonal_hash(self.construction_transport),
            "construction_lineage": dict(self.construction_lineage),
            "geometry_validation_lineage": dict(self.validation_lineage),
            "gate_metric_rule": "minimum across construction and geometry_validation",
        }


def _family_indices(
    manifest: Mapping[str, Any], *, shard: str, half: str, family: str
) -> tuple[np.ndarray, np.ndarray]:
    rows = prompt_rows_for_chunk(manifest, context_shard=shard, half=half)
    selected = [index for index, row in enumerate(rows) if row["behavior_family"] == family]
    labels = [rows[index]["subcondition_id"] for index in selected]
    return np.asarray(selected, dtype=np.int64), np.asarray(labels)


def _node_features(
    store: CaptureStore,
    manifest: Mapping[str, Any],
    *,
    runtime: str,
    site: str,
    family: str,
    shard: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    labels: list[str] = []
    halves: list[str] = []
    for half in ("construction", "geometry_validation"):
        values = store.load(runtime, site, shard, half)
        indices, half_labels = _family_indices(
            manifest, shard=shard, half=half, family=family
        )
        features.append(values[indices])
        labels.extend(map(str, half_labels))
        halves.extend([half] * len(indices))
    return np.vstack(features), np.asarray(labels), np.asarray(halves)


def _instrument_control(
    *, maximum_rank: int, replicates: int, seed: int
) -> CrossFittedRankFiltration:
    # More classes than retained dimensions are essential here: at the full
    # class-mean rank, any random relabeling spans the same signal space and is
    # therefore not a useful permutation null.
    classes = maximum_rank + 4
    dimension = max(24, 3 * maximum_rank + 4)
    rng = np.random.default_rng(seed)
    planted = np.linalg.qr(rng.normal(size=(dimension, maximum_rank)), mode="reduced")[0]
    codes = rng.normal(size=(classes, maximum_rank))
    codes -= np.mean(codes, axis=0, keepdims=True)
    features: list[np.ndarray] = []
    labels: list[str] = []
    halves: list[str] = []
    for half in ("calibration-a", "calibration-b"):
        for class_index in range(classes):
            rows = 4.5 * (planted @ codes[class_index])[None, :]
            rows = rows + rng.normal(size=(24, dimension)) * np.linspace(
                1.5, 0.35, dimension
            )
            features.append(rows)
            labels.extend([f"random-named-family-{class_index:02d}"] * len(rows))
            halves.extend([half] * len(rows))
    return discover_between_class_rank_filtration(
        features=np.vstack(features),
        family_labels=labels,
        construction_halves=halves,
        maximum_rank=maximum_rank,
        object_kind="matched_random_named_family_instrument_calibration",
        gate_role="matched_random_label_negative_control",
        replicates=replicates,
        seed=seed + 1,
        minimum_strict_margin=0.02,
    )


def _make_edge(
    edge_id: str,
    source_node: str,
    target_node: str,
    source: NodeGeometry,
    target: NodeGeometry,
    rank: int,
) -> PhysicalEdge:
    construction_source = source.basis("construction", rank)
    construction_target = target.basis("construction", rank)
    validation_source = source.basis("geometry_validation", rank)
    validation_target = target.basis("geometry_validation", rank)
    construction_transport, _ = procrustes_transport(
        construction_source, construction_target
    )
    validation_transport, _ = procrustes_transport(
        validation_source, validation_target
    )
    construction_lineage = subspace_lineage(
        construction_source, construction_target
    )
    validation_lineage = subspace_lineage(validation_source, validation_target)
    return PhysicalEdge(
        edge_id=edge_id,
        source_node=source_node,
        target_node=target_node,
        construction_transport=construction_transport,
        validation_transport=validation_transport,
        construction_lineage=construction_lineage,
        validation_lineage=validation_lineage,
        mean_edge_chordal_lineage=min(
            float(construction_lineage["mean_chordal_lineage"]),
            float(validation_lineage["mean_chordal_lineage"]),
        ),
        minimum_edge_worst_direction_retention=min(
            float(construction_lineage["worst_direction_retention"]),
            float(validation_lineage["worst_direction_retention"]),
        ),
        rank=rank,
    )


def _loop_product(
    nodes: Sequence[str], edge_ids: Sequence[str], edges: Mapping[str, PhysicalEdge], *, half: str
) -> np.ndarray:
    rank = next(iter(edges.values())).rank
    product = np.eye(rank, dtype=np.float64)
    targets = tuple(nodes[1:]) + (nodes[0],)
    for source, target, edge_id in zip(nodes, targets, edge_ids):
        edge = edges[edge_id]
        matrix = (
            edge.construction_transport
            if half == "construction"
            else edge.validation_transport
        )
        if edge.source_node == source and edge.target_node == target:
            transport = matrix
        elif edge.source_node == target and edge.target_node == source:
            transport = matrix.T
        else:
            raise ValueError(f"edge {edge_id} breaks loop boundary")
        product = transport @ product
    return product


def _matrix_receipt(matrix: np.ndarray) -> dict[str, Any]:
    orientation = holonomy_orientation_receipt(matrix)
    reversing = bool(orientation["orientation_reversal_flag"])
    angles = None if reversing else list(canonical_rotation_angles_degrees(matrix))
    return {
        "det_h": float(np.linalg.det(matrix)),
        "orientation_flag": reversing,
        "canonical_angles_degrees": angles,
        "maximum_canonical_angle_degrees": None if angles is None else max(angles, default=0.0),
        "identity_loss": float(1.0 - np.trace(matrix) / matrix.shape[0]),
        "matrix_sha256": _orthogonal_hash(matrix),
    }


def _resample_basis(
    features: np.ndarray, labels: np.ndarray, rank: int, rng: np.random.Generator
) -> np.ndarray:
    selected: list[int] = []
    for label in np.unique(labels):
        members = np.flatnonzero(labels == label)
        selected.extend(rng.choice(members, size=len(members), replace=True).tolist())
    basis, _ = _between_class_scatter_basis(
        features[np.asarray(selected)], labels[np.asarray(selected)], rank
    )
    return basis


def _validation_features_for_grid(
    store: CaptureStore,
    manifest: Mapping[str, Any],
    *, site: str,
    family: str,
    runtimes: Sequence[str],
    shards: Sequence[str],
) -> dict[tuple[str, str], tuple[np.ndarray, np.ndarray]]:
    output: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
    for runtime in runtimes:
        for shard in shards:
            values = store.load(runtime, site, shard, "geometry_validation")
            indices, labels = _family_indices(
                manifest, shard=shard, half="geometry_validation", family=family
            )
            output[(runtime, shard)] = (values[indices], labels)
    return output


def _flat_noise_null(
    nodes: Mapping[tuple[str, str], NodeGeometry],
    *,
    rank: int,
    runtimes: Sequence[str],
    shards: Sequence[str],
    loop_nodes: Sequence[tuple[str, str]],
    replicates: int,
    seed: int,
) -> np.ndarray:
    root = nodes[(runtimes[0], shards[0])].basis("geometry_validation", rank)
    discrepancies = []
    for item in nodes.values():
        lineage = subspace_lineage(
            item.basis("construction", rank),
            item.basis("geometry_validation", rank),
        )
        discrepancies.append(
            math.sqrt(max(0.0, 1.0 - float(lineage["mean_chordal_lineage"])))
        )
    scale = max(float(np.median(discrepancies)), 1e-6) / math.sqrt(root.shape[0])
    rng = np.random.default_rng(seed)
    values = np.empty(replicates, dtype=np.float64)
    for replicate in range(replicates):
        frames = []
        for _ in loop_nodes:
            frames.append(
                np.linalg.qr(root + rng.normal(scale=scale, size=root.shape), mode="reduced")[0]
            )
        loop = loop_holonomy(frames)
        receipt = _matrix_receipt(loop.matrix)
        values[replicate] = (
            180.0
            if receipt["orientation_flag"]
            else float(receipt["maximum_canonical_angle_degrees"])
        )
    return values


def _bootstrap_loops(
    raw: Mapping[tuple[str, str], tuple[np.ndarray, np.ndarray]],
    *,
    rank: int,
    runtimes: Sequence[str],
    shards: Sequence[str],
    replicates: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    loop_count = len(shards) - 1
    losses = np.empty((replicates, loop_count), dtype=np.float64)
    angles = np.empty((replicates, loop_count), dtype=np.float64)
    reversing = np.empty((replicates, loop_count), dtype=bool)
    rng = np.random.default_rng(seed)
    for replicate in range(replicates):
        bases = {
            key: _resample_basis(features, labels, rank, rng)
            for key, (features, labels) in raw.items()
        }
        for column in range(loop_count):
            order = (
                (runtimes[0], shards[column]),
                (runtimes[0], shards[column + 1]),
                (runtimes[1], shards[column + 1]),
                (runtimes[1], shards[column]),
            )
            loop = loop_holonomy([bases[key] for key in order])
            receipt = _matrix_receipt(loop.matrix)
            losses[replicate, column] = receipt["identity_loss"]
            reversing[replicate, column] = receipt["orientation_flag"]
            angles[replicate, column] = (
                180.0
                if receipt["orientation_flag"]
                else float(receipt["maximum_canonical_angle_degrees"])
            )
    return losses, angles, reversing


def _build_graph(
    *,
    store: CaptureStore,
    manifest: Mapping[str, Any],
    protocol: Mapping[str, Any],
    site: str,
    family: str,
    nodes: Mapping[tuple[str, str], NodeGeometry],
    control: CrossFittedRankFiltration,
    rank: int,
    seed: int,
) -> dict[str, Any]:
    runtimes = tuple(protocol["runtime_precisions"])
    shards = tuple(f"shard-{index:02d}" for index in range(int(manifest["context_shards"])))
    ids = {
        key: node_id(key[0], site, family, key[1], rank)
        for key in nodes
    }
    edges: dict[str, PhysicalEdge] = {}
    for runtime in runtimes:
        for column in range(len(shards) - 1):
            source_key = (runtime, shards[column])
            target_key = (runtime, shards[column + 1])
            edge_id = f"{site}:{family}:r{rank}:{runtime}:shard-{column:02d}-{column + 1:02d}"
            edges[edge_id] = _make_edge(
                edge_id, ids[source_key], ids[target_key], nodes[source_key], nodes[target_key], rank
            )
    for column, shard in enumerate(shards):
        source_key = (runtimes[0], shard)
        target_key = (runtimes[1], shard)
        edge_id = f"{site}:{family}:r{rank}:precision:{column:02d}"
        edges[edge_id] = _make_edge(
            edge_id, ids[source_key], ids[target_key], nodes[source_key], nodes[target_key], rank
        )

    loop_specs: list[dict[str, Any]] = []
    for column in range(len(shards) - 1):
        loop_id = f"{site}:{family}:r{rank}:plaquette-{column:02d}"
        node_order = (
            ids[(runtimes[0], shards[column])],
            ids[(runtimes[0], shards[column + 1])],
            ids[(runtimes[1], shards[column + 1])],
            ids[(runtimes[1], shards[column])],
        )
        edge_order = (
            f"{site}:{family}:r{rank}:{runtimes[0]}:shard-{column:02d}-{column + 1:02d}",
            f"{site}:{family}:r{rank}:precision:{column + 1:02d}",
            f"{site}:{family}:r{rank}:{runtimes[1]}:shard-{column:02d}-{column + 1:02d}",
            f"{site}:{family}:r{rank}:precision:{column:02d}",
        )
        loop_specs.append(
            {"loop_id": loop_id, "node_ids": node_order, "edge_ids": edge_order, "column": column}
        )

    bifiltration = build_lineage_holonomy_bifiltration(
        registered_nodes=tuple(ids.values()),
        edges=[edge.globe_receipt() for edge in edges.values()],
        loops=[{"loop_id": item["loop_id"], "edge_ids": item["edge_ids"]} for item in loop_specs],
        lineage_floor=float(protocol["graph"]["lineage_floor"]),
    )
    raw = _validation_features_for_grid(
        store,
        manifest,
        site=site,
        family=family,
        runtimes=runtimes,
        shards=shards,
    )
    resamples = int(protocol["holonomy"]["prompt_resampling_replicates"])
    bootstrap_losses, bootstrap_angles, bootstrap_reversing = _bootstrap_loops(
        raw,
        rank=rank,
        runtimes=runtimes,
        shards=shards,
        replicates=resamples,
        seed=_stable_seed(seed, site, family, "loop-bootstrap"),
    )
    admitted = set(bifiltration.admitted_loop_ids)
    loop_rows: list[dict[str, Any]] = []
    plaquettes: list[PlaquetteReceipt] = []
    for item in loop_specs:
        construction = _matrix_receipt(
            _loop_product(item["node_ids"], item["edge_ids"], edges, half="construction")
        )
        validation_matrix = _loop_product(
            item["node_ids"], item["edge_ids"], edges, half="geometry_validation"
        )
        validation = _matrix_receipt(validation_matrix)
        column = int(item["column"])
        lower = float(np.quantile(bootstrap_losses[:, column], 0.05, method="linear"))
        upper = float(np.quantile(bootstrap_losses[:, column], 0.95, method="linear"))
        observed_loss = float(validation["identity_loss"])
        lower = min(lower, observed_loss)
        upper = max(upper, observed_loss)
        null = _flat_noise_null(
            nodes,
            rank=rank,
            runtimes=runtimes,
            shards=shards,
            loop_nodes=(
                (runtimes[0], shards[column]),
                (runtimes[0], shards[column + 1]),
                (runtimes[1], shards[column + 1]),
                (runtimes[1], shards[column]),
            ),
            replicates=resamples,
            seed=_stable_seed(seed, site, family, item["loop_id"], "flat-null"),
        )
        null_upper = float(np.quantile(null, 0.95, method="linear"))
        validation_angle = (
            180.0
            if validation["orientation_flag"]
            else float(validation["maximum_canonical_angle_degrees"])
        )
        construction_angle = (
            180.0
            if construction["orientation_flag"]
            else float(construction["maximum_canonical_angle_degrees"])
        )
        agreement = bool(
            construction["orientation_flag"] == validation["orientation_flag"]
            and abs(construction_angle - validation_angle) <= max(1.0, null_upper)
        )
        measured = item["loop_id"] in admitted
        row = {
            "loop_id": item["loop_id"],
            "root_node": item["node_ids"][0],
            "edge_order": list(item["edge_ids"]),
            "det_h": validation["det_h"],
            "canonical_angles_degrees": validation["canonical_angles_degrees"],
            "identity_loss": validation["identity_loss"],
            "orientation_flag": validation["orientation_flag"],
            "basis_hashes": [
                array_sha256(nodes[key].basis("geometry_validation", rank))
                for key in (
                    (runtimes[0], shards[column]),
                    (runtimes[0], shards[column + 1]),
                    (runtimes[1], shards[column + 1]),
                    (runtimes[1], shards[column]),
                )
            ],
            "rank": rank,
            "site": site,
            "family": family,
            "admitted_by_bifiltration": measured,
            "identity_loss_interval_90": [lower, upper],
            "bootstrap_orientation_reversal_probability": float(
                np.mean(bootstrap_reversing[:, column])
            ),
            "flat_noise_null_angle_upper_95": null_upper,
            "construction_maximum_angle_degrees": construction_angle,
            "construction_validation_agreement": agreement,
            "nontrivial_above_instrument_floor": bool(
                measured
                and not validation["orientation_flag"]
                and agreement
                and validation_angle > null_upper
            ),
        }
        loop_rows.append(row)
        plaquettes.append(
            PlaquetteReceipt(
                plaquette_id=item["loop_id"],
                row=0,
                column=column,
                node_ids=tuple(item["node_ids"]),
                edge_ids=tuple(item["edge_ids"]),
                measured=measured,
                identity_loss=observed_loss if measured else None,
                identity_loss_lower_bound=lower if measured else 0.0,
                identity_loss_upper_bound=upper if measured else 2.0,
                det_h_flag=bool(validation["orientation_flag"]),
                determinant_reversal_probability=float(
                    np.mean(bootstrap_reversing[:, column])
                ),
            )
        )
    section_input = SectioningInput(
        grid_id=f"{site}:{family}:rank-{rank}",
        rank=rank,
        edges=tuple(edge.grid_receipt() for edge in edges.values()),
        plaquettes=tuple(plaquettes),
        reference_coordinate=tuple([1.0] + [0.0] * (rank - 1)),
    )
    budget = float(protocol["holonomy"]["budget"]["maximum_identity_loss"])
    plan = section_edits(section_input, budget)
    curve = persistence_curve(section_input, protocol["sectioning"]["budgets"])
    audit = rank_audit_placements(section_input, budget)
    return {
        "site": site,
        "family": family,
        "rank": rank,
        "node_ids": ids,
        "nodes": nodes,
        "edges": edges,
        "loop_rows": loop_rows,
        "section_input": section_input,
        "bifiltration": bifiltration,
        "section_plan": plan,
        "persistence": curve,
        "audit": audit,
        "bootstrap_losses": bootstrap_losses,
        "bootstrap_reversing": bootstrap_reversing,
        "control": control.objects[rank - 1],
        "area_perimeter_calibration": {
            "status": "not_identifiable_on_two_by_n_strip",
            "reason": "For this grid perimeter = 2*area + 2, so area and perimeter predictors are collinear.",
        },
    }


def _directed_edge_receipt(
    edge: PhysicalEdge, *, source: str, target: str, identifier: str
) -> EdgeReceipt:
    if edge.source_node == source and edge.target_node == target:
        matrix = edge.validation_transport
    elif edge.source_node == target and edge.target_node == source:
        matrix = edge.validation_transport.T
    else:
        raise ValueError("directed receipt endpoints do not match physical edge")
    return EdgeReceipt(
        edge_id=identifier,
        source_node=source,
        target_node=target,
        selected_band=f"between_class_rank_{edge.rank}",
        source_basis_sha256="0" * 64,
        target_basis_sha256="0" * 64,
        transport_sha256=_orthogonal_hash(matrix),
        mean_edge_chordal_lineage=edge.mean_edge_chordal_lineage,
        minimum_edge_worst_direction_retention=edge.minimum_edge_worst_direction_retention,
    )


def _basis_by_node(graph: Mapping[str, Any]) -> dict[str, np.ndarray]:
    return {
        graph["node_ids"][key]: value.basis("geometry_validation", graph["rank"])
        for key, value in graph["nodes"].items()
    }


def _component_paths(
    *, nodes: Sequence[str], edge_ids: Sequence[str], edges: Mapping[str, PhysicalEdge], root: str
) -> tuple[dict[str, tuple[str, ...]], tuple[EdgeReceipt, ...]]:
    allowed = set(nodes)
    adjacency: dict[str, list[tuple[str, str, PhysicalEdge]]] = {node: [] for node in nodes}
    for edge_id in edge_ids:
        edge = edges[edge_id]
        if edge.source_node in allowed and edge.target_node in allowed:
            adjacency[edge.source_node].append((edge.target_node, edge_id, edge))
            adjacency[edge.target_node].append((edge.source_node, edge_id, edge))
    paths: dict[str, tuple[str, ...]] = {root: ()}
    receipts: list[EdgeReceipt] = []
    queue = [root]
    while queue:
        source = queue.pop(0)
        for target, physical_id, edge in sorted(adjacency[source], key=lambda item: item[0]):
            if target in paths:
                continue
            directed_id = f"path:{root}:{source}->{target}:{physical_id}"
            receipt = _directed_edge_receipt(
                edge, source=source, target=target, identifier=directed_id
            )
            receipts.append(receipt)
            paths[target] = paths[source] + (directed_id,)
            queue.append(target)
    return paths, tuple(receipts)


def _patch_attestations(graph: Mapping[str, Any], protocol: Mapping[str, Any]) -> tuple[list[dict], list[dict]]:
    bases = _basis_by_node(graph)
    edges: Mapping[str, PhysicalEdge] = graph["edges"]
    loop_by_id = {row["loop_id"]: row for row in graph["loop_rows"]}
    control_receipt = graph["control"].receipt()
    budget = HolonomyBudget(
        maximum_canonical_angle_degrees=float(
            protocol["holonomy"]["budget"]["maximum_canonical_angle_degrees"]
        ),
        maximum_identity_loss=float(
            protocol["holonomy"]["budget"]["maximum_identity_loss"]
        ),
    )
    records: dict[str, AnchorRecord] = {}
    # First give every lineage-connected node a loop-free component record.
    for component_index, component in enumerate(graph["bifiltration"].connected_components):
        admitted_edges = [
            edge_id
            for edge_id in graph["bifiltration"].admitted_edge_ids
            if edges[edge_id].source_node in component and edges[edge_id].target_node in component
        ]
        root = min(component)
        paths, tree_receipts = _component_paths(
            nodes=component, edge_ids=admitted_edges, edges=edges, root=root
        )
        receipt_by_path_id = {item.edge_id: item for item in tree_receipts}
        for node in component:
            patched_receipts = []
            for item in tree_receipts:
                patched_receipts.append(
                    EdgeReceipt(
                        **{
                            **asdict(item),
                            "source_basis_sha256": array_sha256(bases[item.source_node]),
                            "target_basis_sha256": array_sha256(bases[item.target_node]),
                        }
                    )
                )
            records[node] = AnchorRecord(
                site_id=node,
                consumer="vpd_edit_program",
                artifact_kind="disparate_weight_edit",
                reference_node=root,
                site_node=node,
                reference_basis_sha256=array_sha256(bases[root]),
                current_basis_sha256=array_sha256(bases[node]),
                selected_band=f"between_class_rank_{graph['rank']}",
                spanning_tree_transport_path=paths.get(node, ()),
                edge_receipts=tuple(patched_receipts),
                loop_receipts=(),
                holonomy_budget=budget,
                det_h_flag=False,
                metadata={
                    "matched_random_label_negative_control": control_receipt,
                    "lineage_holonomy_bifiltration": graph["bifiltration"].attestation_metadata(),
                    "component_index": component_index,
                    "identity_scope": "lineage_component_without_loop_authorization",
                },
            )

    # Replace nodes in budget-clean patches with patch-rooted loop receipts.
    for patch in graph["section_plan"]["patches"]:
        patch_nodes = tuple(patch["node_ids"])
        patch_edge_ids = tuple(patch["edge_receipt_ids"])
        root = str(patch["anchor_node"])
        paths, path_receipts = _component_paths(
            nodes=patch_nodes, edge_ids=patch_edge_ids, edges=edges, root=root
        )
        directed_receipts: list[EdgeReceipt] = [
            EdgeReceipt(
                **{
                    **asdict(item),
                    "source_basis_sha256": array_sha256(bases[item.source_node]),
                    "target_basis_sha256": array_sha256(bases[item.target_node]),
                }
            )
            for item in path_receipts
        ]
        loop_receipts: list[LoopReceipt] = []
        for loop_id in patch["plaquette_ids"]:
            row = loop_by_id[loop_id]
            nodes = tuple(
                graph["section_input"].plaquettes[
                    next(
                        index
                        for index, item in enumerate(graph["section_input"].plaquettes)
                        if item.plaquette_id == loop_id
                    )
                ].node_ids
            )
            physical_ids = tuple(row["edge_order"])
            loop_edge_ids = []
            targets = nodes[1:] + nodes[:1]
            for source, target, physical_id in zip(nodes, targets, physical_ids):
                identifier = f"loop:{loop_id}:{source}->{target}:{physical_id}"
                receipt = _directed_edge_receipt(
                    edges[physical_id], source=source, target=target, identifier=identifier
                )
                receipt = EdgeReceipt(
                    **{
                        **asdict(receipt),
                        "source_basis_sha256": array_sha256(bases[source]),
                        "target_basis_sha256": array_sha256(bases[target]),
                    }
                )
                directed_receipts.append(receipt)
                loop_edge_ids.append(identifier)
            angles = row["canonical_angles_degrees"]
            loop_receipts.append(
                LoopReceipt(
                    loop_id=loop_id,
                    edge_ids=tuple(loop_edge_ids),
                    determinant=float(row["det_h"]),
                    det_h_flag=bool(row["orientation_flag"]),
                    maximum_canonical_angle_degrees=(
                        None if angles is None else max(angles, default=0.0)
                    ),
                    identity_loss=float(row["identity_loss"]),
                )
            )
        # Duplicate receipt IDs can arise when a tree edge also bounds a loop,
        # but the directed loop aliases are distinct by construction.
        for node in patch_nodes:
            records[node] = AnchorRecord(
                site_id=node,
                consumer="vpd_edit_program",
                artifact_kind="disparate_weight_edit",
                reference_node=root,
                site_node=node,
                reference_basis_sha256=array_sha256(bases[root]),
                current_basis_sha256=array_sha256(bases[node]),
                selected_band=f"between_class_rank_{graph['rank']}",
                spanning_tree_transport_path=paths[node],
                edge_receipts=tuple(directed_receipts),
                loop_receipts=tuple(loop_receipts),
                holonomy_budget=budget,
                det_h_flag=any(item.det_h_flag for item in loop_receipts),
                metadata={
                    "matched_random_label_negative_control": control_receipt,
                    "lineage_holonomy_bifiltration": graph["bifiltration"].attestation_metadata(),
                    "patch_id": patch["patch_id"],
                    "identity_scope": "budget_clean_elementary_loop_patch",
                },
            )
    registry = AnchorRegistry(records=records.values(), policy=AttestationPolicy())
    anchors = [asdict(records[key]) for key in sorted(records)]
    certificates = [
        registry.certify(key, requested_use="disparate_weight_edit").to_dict()
        for key in sorted(records)
    ]
    return anchors, certificates


def _partial_transport_distance(
    source_a: np.ndarray,
    target_a: np.ndarray,
    source_b: np.ndarray,
    target_b: np.ndarray,
) -> float:
    transport_a, _ = procrustes_transport(source_a, target_a)
    transport_b, _ = procrustes_transport(source_b, target_b)
    # <Ut T Us^T, Vt S Vs^T> without materializing an ambient d x d map.
    inner = np.trace(
        transport_a.T
        @ (target_a.T @ target_b)
        @ transport_b
        @ (source_b.T @ source_a)
    )
    rank = source_a.shape[1]
    squared = max(0.0, 2.0 * rank - 2.0 * float(inner))
    return float(math.sqrt(squared / (2.0 * rank)))


def _corotation_summary(
    geometries: Mapping[tuple[str, str, str, str], NodeGeometry],
    *,
    protocol: Mapping[str, Any],
    manifest: Mapping[str, Any],
    seed: int,
) -> dict[str, Any]:
    runtimes = tuple(protocol["runtime_precisions"])
    sites = tuple(protocol["candidate_sites"])
    families = tuple(manifest["families"])
    shards = tuple(f"shard-{index:02d}" for index in range(int(manifest["context_shards"])))
    within: list[tuple[str, float]] = []
    cross: list[tuple[str, float]] = []
    for site in sites:
        for runtime in runtimes:
            for column in range(len(shards) - 1):
                available = []
                for family in families:
                    left = geometries[(runtime, site, family, shards[column])]
                    right = geometries[(runtime, site, family, shards[column + 1])]
                    rank = min(left.supported_rank, right.supported_rank)
                    if rank:
                        available.append((family, left, right, rank))
                for family, left, right, rank in available:
                    within.append(
                        (site, _partial_transport_distance(
                            left.basis("construction", rank),
                            right.basis("construction", rank),
                            left.basis("geometry_validation", rank),
                            right.basis("geometry_validation", rank),
                        ))
                    )
                for first_index in range(len(available)):
                    for second_index in range(first_index + 1, len(available)):
                        _, left_a, right_a, rank_a = available[first_index]
                        _, left_b, right_b, rank_b = available[second_index]
                        rank = min(rank_a, rank_b)
                        cross.append(
                            (site, _partial_transport_distance(
                                left_a.basis("geometry_validation", rank),
                                right_a.basis("geometry_validation", rank),
                                left_b.basis("geometry_validation", rank),
                                right_b.basis("geometry_validation", rank),
                            ))
                        )
    if not within or not cross:
        return {
            "status": "not_established_insufficient_equal_rank_family_pairs",
            "within_count": len(within),
            "cross_count": len(cross),
        }
    within_values = np.asarray([value for _, value in within])
    cross_values = np.asarray([value for _, value in cross])
    observed = float(np.median(cross_values) - np.median(within_values))
    rng = np.random.default_rng(seed)
    draws = 2048
    samples = np.empty(draws, dtype=np.float64)
    cluster_ids = sorted({site for site, _ in within} & {site for site, _ in cross})
    within_by_cluster = {
        site: np.asarray([value for owner, value in within if owner == site])
        for site in cluster_ids
    }
    cross_by_cluster = {
        site: np.asarray([value for owner, value in cross if owner == site])
        for site in cluster_ids
    }
    for index in range(draws):
        selected = rng.choice(cluster_ids, size=len(cluster_ids), replace=True)
        sampled_within = np.concatenate([within_by_cluster[site] for site in selected])
        sampled_cross = np.concatenate([cross_by_cluster[site] for site in selected])
        samples[index] = float(
            np.median(sampled_cross) - np.median(sampled_within)
        )
    lower = float(np.quantile(samples, 0.05, method="linear"))
    return {
        "status": "established" if lower > 0.0 else "not_established",
        "estimand": "median_cross_family_distance - median_within_family_construction_validation_distance",
        "ambient_partial_isometry_gauge_invariant": True,
        "within_count": len(within),
        "cross_count": len(cross),
        "within_median": float(np.median(within_values)),
        "cross_median": float(np.median(cross_values)),
        "contrast": observed,
        "one_sided_lower_95": lower,
        "bootstrap_draws": draws,
        "inference_note": "Bootstrap resamples physical sites as superclusters, preserving all family and edge dependence inside each site.",
        "cluster_count": len(cluster_ids),
    }


def _gauge_preflight(graphs: Sequence[Mapping[str, Any]], *, reframings: int, seed: int, tolerance: float) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    maximum_error = 0.0
    decision_mismatches = 0
    checked = 0
    for graph in graphs:
        rank = int(graph["rank"])
        if rank < 1:
            continue
        bases = _basis_by_node(graph)
        original_loops = {row["loop_id"]: row for row in graph["loop_rows"]}
        for _ in range(reframings):
            reframed = {}
            for key, basis in bases.items():
                q = np.linalg.qr(rng.normal(size=(rank, rank)))[0]
                reframed[key] = basis @ q
            for plaquette in graph["section_input"].plaquettes:
                frames = [reframed[node] for node in plaquette.node_ids]
                receipt = _matrix_receipt(loop_holonomy(frames).matrix)
                original = original_loops[plaquette.plaquette_id]
                if bool(receipt["orientation_flag"]) != bool(original["orientation_flag"]):
                    decision_mismatches += 1
                if not receipt["orientation_flag"]:
                    left = np.asarray(receipt["canonical_angles_degrees"], dtype=float)
                    right = np.asarray(original["canonical_angles_degrees"], dtype=float)
                    maximum_error = max(maximum_error, float(np.max(np.abs(left - right), initial=0.0)))
                checked += 1
    return {
        "status": (
            "passed"
            if decision_mismatches == 0 and maximum_error <= tolerance
            else "failed"
        ),
        "reframings_per_grid": reframings,
        "loop_replays": checked,
        "orientation_decision_mismatches": decision_mismatches,
        "maximum_canonical_angle_error_degrees": maximum_error,
        "tolerance": tolerance,
        "absolute_globe_orientation": "presentational_only",
    }


def _stability_summary(graph: Mapping[str, Any], protocol: Mapping[str, Any]) -> dict[str, Any]:
    losses = np.asarray(graph["bootstrap_losses"])
    reversing = np.asarray(graph["bootstrap_reversing"])
    budget = float(protocol["holonomy"]["budget"]["maximum_identity_loss"])
    edge_by_id = {edge.edge_id: edge for edge in graph["section_input"].edges}

    def clean_edge_set(item: PlaquetteReceipt) -> bool:
        return all(
            edge_by_id[edge_id].mean_edge_chordal_lineage >= 0.95
            and edge_by_id[edge_id].minimum_edge_worst_direction_retention >= 0.90
            for edge_id in item.edge_ids
        )

    def count_runs(clean: Sequence[bool]) -> int:
        return sum(value and (index == 0 or not clean[index - 1]) for index, value in enumerate(clean))

    point_clean = [
        bool(
            item.measured
            and not item.det_h_flag
            and clean_edge_set(item)
            and item.identity_loss_upper_bound <= budget
        )
        for item in graph["section_input"].plaquettes
    ]
    point_counts = {
        str(prefix): count_runs(point_clean[: max(0, int(prefix) - 1)])
        for prefix in protocol["sectioning"]["shard_prefixes"]
    }
    deltas = []
    if losses.shape[1] >= 7:
        for replicate in range(losses.shape[0]):
            counts = []
            for shard_count in (6, 8):
                cells = shard_count - 1
                clean = [
                    bool(
                        base.measured
                        and not reversing[replicate, column]
                        and clean_edge_set(base)
                        and losses[replicate, column] <= budget
                    )
                    for column, base in enumerate(
                        graph["section_input"].plaquettes[:cells]
                    )
                ]
                counts.append(count_runs(clean))
            deltas.append(counts[1] - counts[0])
    if not deltas:
        return {"status": "unavailable", "point_patch_counts": point_counts}
    lower, upper = np.quantile(np.asarray(deltas), [0.025, 0.975], method="linear")
    six_count = max(1, int(point_counts.get("6", 0)))
    equivalence = max(1, math.ceil(0.10 * six_count))
    return {
        "status": "stable" if lower >= -equivalence and upper <= equivalence else "not_stable",
        "point_patch_counts": point_counts,
        "six_to_eight_delta_interval_95": [float(lower), float(upper)],
        "equivalence_bound": equivalence,
        "bootstrap_replicates": len(deltas),
    }


def analyze_godel_capture(
    *,
    store: CaptureStore,
    manifest: Mapping[str, Any],
    protocol: Mapping[str, Any],
    seed: int = 2026071603,
) -> dict[str, Any]:
    runtimes = tuple(protocol["runtime_precisions"])
    sites = tuple(protocol["candidate_sites"])
    families = tuple(manifest["families"])
    shards = tuple(f"shard-{index:02d}" for index in range(int(manifest["context_shards"])))
    maximum_rank = min(
        max(map(int, protocol["primary_object"]["ranks"])),
        int(manifest["subconditions_per_family"]) - 1,
    )
    replicates = int(protocol["primary_object"]["bootstrap_replicates"])
    control = _instrument_control(
        maximum_rank=maximum_rank,
        replicates=replicates,
        seed=_stable_seed(seed, "instrument-calibration"),
    )
    geometries: dict[tuple[str, str, str, str], NodeGeometry] = {}
    for runtime in runtimes:
        for site in sites:
            for family in families:
                for shard in shards:
                    features, labels, halves = _node_features(
                        store,
                        manifest,
                        runtime=runtime,
                        site=site,
                        family=family,
                        shard=shard,
                    )
                    filtration = discover_between_class_rank_filtration(
                        features=features,
                        family_labels=labels,
                        construction_halves=halves,
                        maximum_rank=maximum_rank,
                        replicates=replicates,
                        seed=_stable_seed(seed, runtime, site, family, shard),
                        minimum_strict_margin=float(
                            protocol["primary_object"]["minimum_strict_null_margin"]
                        ),
                    )
                    geometries[(runtime, site, family, shard)] = NodeGeometry(
                        runtime=runtime,
                        site=site,
                        family=family,
                        shard=shard,
                        filtration=filtration,
                    )

    runtime_grid_ranks: list[dict[str, Any]] = []
    graphs: list[dict[str, Any]] = []
    for site in sites:
        for family in families:
            runtime_ranks = {
                runtime: min(
                    geometries[(runtime, site, family, shard)].supported_rank
                    for shard in shards
                )
                for runtime in runtimes
            }
            cross_runtime_rank, state = classify_runtime_support(runtime_ranks)
            runtime_grid_ranks.append(
                {
                    "site": site,
                    "family": family,
                    "runtime_supported_ranks": runtime_ranks,
                    "cross_runtime_supported_rank": cross_runtime_rank,
                    "status": state,
                }
            )
            if cross_runtime_rank:
                graph_nodes = {
                    (runtime, shard): geometries[(runtime, site, family, shard)]
                    for runtime in runtimes
                    for shard in shards
                }
                graphs.append(
                    _build_graph(
                        store=store,
                        manifest=manifest,
                        protocol=protocol,
                        site=site,
                        family=family,
                        nodes=graph_nodes,
                        control=control,
                        rank=cross_runtime_rank,
                        seed=seed,
                    )
                )

    anchors: list[dict[str, Any]] = []
    certificates: list[dict[str, Any]] = []
    for graph in graphs:
        graph_anchors, graph_certificates = _patch_attestations(graph, protocol)
        anchors.extend(graph_anchors)
        certificates.extend(graph_certificates)
        graph["stability"] = _stability_summary(graph, protocol)

    gauge = _gauge_preflight(
        graphs,
        reframings=int(protocol["gauge_preflight"]["reframings"]),
        seed=_stable_seed(seed, "gauge-preflight"),
        tolerance=float(protocol["gauge_preflight"]["tolerance"]),
    )
    corotation = _corotation_summary(
        geometries,
        protocol=protocol,
        manifest=manifest,
        seed=_stable_seed(seed, "corotation"),
    )
    nontrivial = [
        row
        for graph in graphs
        for row in graph["loop_rows"]
        if row["nontrivial_above_instrument_floor"]
    ]
    nontrivial_sites = {row["site"] for row in nontrivial}
    nontrivial_families = {row["family"] for row in nontrivial}
    minimum_sites = int(protocol["aggregate_identity_gate"]["minimum_physical_sites"])
    minimum_families = int(protocol["aggregate_identity_gate"]["minimum_behavior_families"])
    holonomy_signal_status = (
        "established"
        if len(nontrivial_sites) >= minimum_sites and len(nontrivial_families) >= minimum_families
        else "not_established"
    )
    clean_certificates = [
        row for row in certificates if row["certification_level"] == "holonomy_clean"
    ]
    lineage_certificates = [
        row for row in certificates if row["certification_level"] == "lineage_certified"
    ]
    return {
        "schema_version": ANALYSIS_SCHEMA,
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": canonical_json_sha256(protocol),
        "prompt_manifest_sha256": canonical_json_sha256(manifest),
        "capture_index_sha256": sha256_file(store.index_path),
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
        "instrument_calibration": control.receipt(),
        "instrument_calibration_passed_all_ranks": all(item.passed for item in control.objects),
        "node_rank_filtrations": [
            geometries[key].receipt() for key in sorted(geometries)
        ],
        "runtime_grid_ranks": runtime_grid_ranks,
        "graphs": [
            {
                "site": graph["site"],
                "family": graph["family"],
                "rank": graph["rank"],
                "bifiltration": graph["bifiltration"].to_dict(),
                "section_plan": graph["section_plan"],
                "persistence": graph["persistence"],
                "audit": graph["audit"],
                "stability": graph["stability"],
                "area_perimeter_calibration": graph["area_perimeter_calibration"],
            }
            for graph in graphs
        ],
        "edge_receipts": [
            edge.globe_receipt()
            for graph in graphs
            for edge in graph["edges"].values()
        ],
        "loop_receipts": [row for graph in graphs for row in graph["loop_rows"]],
        "anchor_records": anchors,
        "lineage_certificates": certificates,
        "summary": {
            "graph_count": len(graphs),
            "runtime_specific_grid_count": sum(
                row["status"] == "runtime_specific_identity"
                for row in runtime_grid_ranks
            ),
            "no_supported_grid_count": sum(
                row["status"] == "no_supported_identity_rank"
                for row in runtime_grid_ranks
            ),
            "beta_1_zero_grid_count": sum(
                graph["bifiltration"].beta_1 == 0 for graph in graphs
            ),
            "nontrivial_loop_count": len(nontrivial),
            "nontrivial_holonomy_signal": holonomy_signal_status,
            "holonomy_clean_certificate_count": len(clean_certificates),
            "lineage_only_certificate_count": len(lineage_certificates),
            "corotation": corotation,
            "gauge_preflight": gauge,
            "navigation_mode": (
                "hierarchical"
                if any(
                    graph["section_plan"]["edit_count"]
                    > int(protocol["sectioning"]["navigation_ceiling_per_family"])
                    for graph in graphs
                )
                else "direct_patch_list"
            ),
        },
        "claim_boundary": protocol["claim_boundary"],
    }


def _jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        for row in rows
    )


def write_analysis_bundle(output_dir: str | Path, result: Mapping[str, Any]) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    files = {
        "analysis_result.json": canonical_json_bytes(result),
        "edge_receipts.jsonl": _jsonl_bytes(result["edge_receipts"]),
        "loop_receipts.jsonl": _jsonl_bytes(result["loop_receipts"]),
        "anchor_records.jsonl": _jsonl_bytes(result["anchor_records"]),
        "lineage_certificates.jsonl": _jsonl_bytes(
            {
                "site_id": item["site_id"],
                "attained_level": item["certification_level"],
                "margins": item["margins"],
                "authorized": item["authorized"],
                "failures": item["failures"],
                "record_sha256": item["record_sha256"],
            }
            for item in result["lineage_certificates"]
        ),
    }
    nonreversing_nulls = [
        float(row["flat_noise_null_angle_upper_95"])
        for row in result["loop_receipts"]
        if not row["orientation_flag"]
    ]
    files["calibration.json"] = canonical_json_bytes(
        {
            "bias_floor_degrees": (
                float(np.median(nonreversing_nulls)) if nonreversing_nulls else 0.0
            ),
            "source": "median matched flat/noise loop upper-95 across nonreversing measured grids",
        }
    )
    for name, data in files.items():
        write_once_or_equal(output / name, data)
    manifest_core = {
        "schema_version": "godel_globes_release_manifest_v0_1",
        "analysis_schema": result["schema_version"],
        "protocol_sha256": result["protocol_sha256"],
        "prompt_manifest_sha256": result["prompt_manifest_sha256"],
        "capture_index_sha256": result["capture_index_sha256"],
        "file_sha256": {
            name: sha256_file(output / name) for name in sorted(files)
        },
    }
    manifest = {
        **manifest_core,
        "manifest_payload_sha256": canonical_json_sha256(manifest_core),
    }
    write_once_or_equal(output / "release_manifest.json", canonical_json_bytes(manifest))
    return manifest
