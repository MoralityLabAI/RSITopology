"""Lineage percolation and rank-one Z/2 gauge diagnostics.

The lineage threshold is swept by repeatedly delegating edge and loop
admission to :func:`build_lineage_holonomy_bifiltration`.  This module adds no
attestation level; its outputs are diagnostics on the existing filtered graph.

At rank one, O(1) transports are signs.  Their products on a cycle basis form
the first Stiefel--Whitney class.  Node-frame flips add a coboundary to the edge
cochain, leaving every cycle product unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from .bifiltration import build_lineage_holonomy_bifiltration
from .confinement_experiments.common import derived_seed
from .rank1_w1 import gf2_rank


@dataclass(frozen=True)
class PercolationFloorRecord:
    lineage_floor: float
    admitted_edge_count: int
    connected_component_count: int
    largest_component_fraction: float
    beta_1: int
    admitted_registered_loop_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineage_floor": self.lineage_floor,
            "admitted_edge_count": self.admitted_edge_count,
            "connected_component_count": self.connected_component_count,
            "largest_component_fraction": self.largest_component_fraction,
            "beta_1": self.beta_1,
            "admitted_registered_loop_count": self.admitted_registered_loop_count,
        }


@dataclass(frozen=True)
class CriticalFloors:
    tau_conn: float | None
    tau_cycle: float | None
    tau_loop: float | None

    def to_dict(self) -> dict[str, float | None]:
        return {
            "tau_conn": self.tau_conn,
            "tau_cycle": self.tau_cycle,
            "tau_loop": self.tau_loop,
        }


@dataclass(frozen=True)
class LineagePercolationCurve:
    floors: tuple[PercolationFloorRecord, ...]
    critical_floors: CriticalFloors
    by_edge_class: Mapping[str, CriticalFloors]
    per_class_curves: Mapping[str, tuple[PercolationFloorRecord, ...]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "floors": [item.to_dict() for item in self.floors],
            "critical_floors": self.critical_floors.to_dict(),
            "by_edge_class": {
                key: value.to_dict() for key, value in sorted(self.by_edge_class.items())
            },
            "per_class_curves": {
                key: [item.to_dict() for item in value]
                for key, value in sorted(self.per_class_curves.items())
            },
            "threshold_ordering": {
                "guaranteed": "tau_loop <= tau_cycle when both are defined",
                "not_guaranteed": "tau_cycle and tau_conn have no universal ordering",
            },
        }


@dataclass(frozen=True)
class SignSyndrome:
    cycle_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    cycle_edge_incidence: tuple[tuple[int, ...], ...]
    syndrome: tuple[int, ...]
    incidence_rank: int
    w1_trivial: bool
    frustrated_cycle_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_ids": list(self.cycle_ids),
            "edge_ids": list(self.edge_ids),
            "cycle_edge_incidence": [list(row) for row in self.cycle_edge_incidence],
            "syndrome": list(self.syndrome),
            "incidence_rank": self.incidence_rank,
            "w1_trivial": self.w1_trivial,
            "frustrated_cycle_ids": list(self.frustrated_cycle_ids),
        }


@dataclass(frozen=True)
class FrustratedClusterReport:
    cluster_count: int
    clusters: tuple[tuple[str, ...], ...]
    cluster_sizes: tuple[int, ...]
    largest_cluster_fraction: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "cluster_count": self.cluster_count,
            "clusters": [list(value) for value in self.clusters],
            "cluster_sizes": list(self.cluster_sizes),
            "largest_cluster_fraction": self.largest_cluster_fraction,
        }


@dataclass(frozen=True)
class CoboundaryDistance:
    mode: str
    exact_distance: int | None
    lower_bound: int
    upper_bound: int
    correction_edge_ids: tuple[str, ...]
    cycle_rank: int
    coset_dimension: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "exact_distance": self.exact_distance,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "correction_edge_ids": list(self.correction_edge_ids),
            "cycle_rank": self.cycle_rank,
            "coset_dimension": self.coset_dimension,
        }


@dataclass(frozen=True)
class PhasePoint:
    lineage_floor: float
    phase: str
    admitted_edge_count: int
    connected_component_count: int
    largest_component_fraction: float
    beta_1: int
    admitted_registered_loop_count: int
    syndrome: SignSyndrome
    frustrated_clusters: FrustratedClusterReport
    coboundary_distance: CoboundaryDistance

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineage_floor": self.lineage_floor,
            "phase": self.phase,
            "admitted_edge_count": self.admitted_edge_count,
            "connected_component_count": self.connected_component_count,
            "largest_component_fraction": self.largest_component_fraction,
            "beta_1": self.beta_1,
            "admitted_registered_loop_count": self.admitted_registered_loop_count,
            "syndrome": self.syndrome.to_dict(),
            "frustrated_clusters": self.frustrated_clusters.to_dict(),
            "coboundary_distance": self.coboundary_distance.to_dict(),
            "attestation_effect": "diagnostic_only_no_new_level",
        }


def _field(item: Any, name: str, *aliases: str) -> Any:
    if isinstance(item, Mapping):
        for key in (name, *aliases):
            if key in item:
                return item[key]
    else:
        for key in (name, *aliases):
            if hasattr(item, key):
                return getattr(item, key)
    raise ValueError(f"receipt is missing {name}")


def _edge_record(item: Any) -> dict[str, Any]:
    value = {
        "edge_id": str(_field(item, "edge_id")),
        "source_node": str(_field(item, "source_node")),
        "target_node": str(_field(item, "target_node")),
        "lineage": float(
            _field(
                item,
                "minimum_edge_worst_direction_retention",
                "worst_direction_retention",
                "lineage",
            )
        ),
    }
    if not all(value[key] for key in ("edge_id", "source_node", "target_node")):
        raise ValueError("edge identifiers and endpoints must be nonempty")
    if not np.isfinite(value["lineage"]) or not 0.0 <= value["lineage"] <= 1.0:
        raise ValueError(f"edge {value['edge_id']} has invalid lineage")
    return value


def _loop_record(item: Any) -> dict[str, Any]:
    return {
        "loop_id": str(_field(item, "loop_id")),
        "edge_ids": tuple(map(str, _field(item, "edge_ids", "edge_order"))),
    }


def _normalize_edges(edges: Iterable[Any]) -> tuple[dict[str, Any], ...]:
    values = tuple(_edge_record(item) for item in edges)
    if not values:
        raise ValueError("percolation curve requires at least one edge")
    ids = [item["edge_id"] for item in values]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate edge_id")
    return values


def _node_universe(edges: Sequence[Mapping[str, Any]], registered_nodes: Iterable[str]) -> tuple[str, ...]:
    nodes = {str(value) for value in registered_nodes}
    for edge in edges:
        nodes.update((str(edge["source_node"]), str(edge["target_node"])))
    if not nodes:
        raise ValueError("at least one registered node is required")
    return tuple(sorted(nodes))


def _critical(records: Sequence[PercolationFloorRecord]) -> CriticalFloors:
    def maximum(predicate) -> float | None:
        values = [item.lineage_floor for item in records if predicate(item)]
        return max(values) if values else None

    return CriticalFloors(
        tau_conn=maximum(lambda item: item.connected_component_count == 1),
        tau_cycle=maximum(lambda item: item.beta_1 > 0),
        tau_loop=maximum(lambda item: item.admitted_registered_loop_count > 0),
    )


def _curve(
    edges: Sequence[Mapping[str, Any]],
    loops: Sequence[Mapping[str, Any]],
    nodes: Sequence[str],
) -> tuple[PercolationFloorRecord, ...]:
    floors = sorted({0.0, 1.0, *(float(edge["lineage"]) for edge in edges)}, reverse=True)
    records: list[PercolationFloorRecord] = []
    previous_edges = -1
    for floor in floors:
        filtered = build_lineage_holonomy_bifiltration(
            edges=edges,
            lineage_floor=floor,
            loops=loops,
            registered_nodes=nodes,
        )
        largest = max(map(len, filtered.connected_components), default=0) / len(nodes)
        record = PercolationFloorRecord(
            lineage_floor=floor,
            admitted_edge_count=filtered.admitted_edge_count,
            connected_component_count=filtered.connected_component_count,
            largest_component_fraction=float(largest),
            beta_1=filtered.beta_1,
            admitted_registered_loop_count=len(filtered.admitted_loop_ids),
        )
        if record.admitted_edge_count < previous_edges:
            raise AssertionError("edge admission is not monotone as floor decreases")
        previous_edges = record.admitted_edge_count
        records.append(record)
    thresholds = _critical(records)
    if (
        thresholds.tau_loop is not None
        and thresholds.tau_cycle is not None
        and thresholds.tau_loop > thresholds.tau_cycle + 1e-15
    ):
        raise AssertionError("registered loop threshold exceeded cycle threshold")
    return tuple(records)


def lineage_percolation_curve(
    *,
    edges: Iterable[Any],
    loops: Iterable[Any] = (),
    registered_nodes: Iterable[str] = (),
    edge_classes: Mapping[str, str] | None = None,
) -> LineagePercolationCurve:
    """Sweep exact retention jumps, delegating admission to the bifiltration."""

    normalized_edges = _normalize_edges(edges)
    normalized_loops = tuple(_loop_record(item) for item in loops)
    loop_ids = [item["loop_id"] for item in normalized_loops]
    if len(loop_ids) != len(set(loop_ids)):
        raise ValueError("duplicate loop_id")
    nodes = _node_universe(normalized_edges, registered_nodes)
    records = _curve(normalized_edges, normalized_loops, nodes)
    class_thresholds: dict[str, CriticalFloors] = {}
    class_curves: dict[str, tuple[PercolationFloorRecord, ...]] = {}
    if edge_classes is not None:
        edge_ids = {item["edge_id"] for item in normalized_edges}
        if set(map(str, edge_classes)) != edge_ids:
            raise ValueError("edge_classes must cover the exact edge universe")
        for label in sorted(set(map(str, edge_classes.values()))):
            selected = tuple(
                item for item in normalized_edges if str(edge_classes[item["edge_id"]]) == label
            )
            selected_ids = {item["edge_id"] for item in selected}
            selected_loops = tuple(
                item for item in normalized_loops if set(item["edge_ids"]) <= selected_ids
            )
            class_records = _curve(selected, selected_loops, nodes)
            class_curves[label] = class_records
            class_thresholds[label] = _critical(class_records)
    return LineagePercolationCurve(
        floors=records,
        critical_floors=_critical(records),
        by_edge_class=class_thresholds,
        per_class_curves=class_curves,
    )


def _normalize_cycle_basis(
    cycle_basis_edge_ids: Mapping[str, Sequence[str]] | Sequence[Sequence[str]],
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    if isinstance(cycle_basis_edge_ids, Mapping):
        values = tuple(
            (str(key), tuple(map(str, edges)))
            for key, edges in sorted(cycle_basis_edge_ids.items(), key=lambda item: str(item[0]))
        )
    else:
        values = tuple(
            (f"cycle-{index:03d}", tuple(map(str, edges)))
            for index, edges in enumerate(cycle_basis_edge_ids)
        )
    if any(not cycle_id or not edges for cycle_id, edges in values):
        raise ValueError("cycle ids and boundaries must be nonempty")
    if len({cycle_id for cycle_id, _ in values}) != len(values):
        raise ValueError("duplicate cycle id")
    return values


def sign_syndrome(
    *,
    cycle_basis_edge_ids: Mapping[str, Sequence[str]] | Sequence[Sequence[str]],
    edge_signs: Mapping[str, int],
) -> SignSyndrome:
    """Evaluate a rank-one edge-sign cochain on a registered cycle basis."""

    cycles = _normalize_cycle_basis(cycle_basis_edge_ids)
    universe = tuple(sorted({edge for _, values in cycles for edge in values}))
    missing = set(universe) - set(map(str, edge_signs))
    if missing:
        raise ValueError(f"edge_signs missing cycle edges: {sorted(missing)}")
    signs = {str(key): int(value) for key, value in edge_signs.items()}
    if any(value not in (-1, 1) for value in signs.values()):
        raise ValueError("edge signs must lie in {-1,+1}")
    incidence = tuple(
        tuple(int(edge in set(boundary)) for edge in universe)
        for _, boundary in cycles
    )
    rank = gf2_rank(incidence)
    if rank != len(cycles):
        raise ValueError("cycle_basis_edge_ids is not an independent cycle basis")
    syndrome = tuple(
        sum(signs[edge] < 0 for edge in boundary) % 2 for _, boundary in cycles
    )
    ids = tuple(cycle_id for cycle_id, _ in cycles)
    frustrated = tuple(
        cycle_id for cycle_id, value in zip(ids, syndrome) if value
    )
    return SignSyndrome(
        cycle_ids=ids,
        edge_ids=universe,
        cycle_edge_incidence=incidence,
        syndrome=syndrome,
        incidence_rank=rank,
        w1_trivial=not any(syndrome),
        frustrated_cycle_ids=frustrated,
    )


def frustrated_clusters(
    *,
    syndrome: SignSyndrome,
    cycle_basis_edge_ids: Mapping[str, Sequence[str]] | Sequence[Sequence[str]],
) -> FrustratedClusterReport:
    """Cluster frustrated basis cycles by shared admitted edges."""

    cycles = dict(_normalize_cycle_basis(cycle_basis_edge_ids))
    if tuple(cycles) != syndrome.cycle_ids:
        raise ValueError("cycle basis does not match syndrome receipt")
    frustrated = list(syndrome.frustrated_cycle_ids)
    adjacency = {cycle_id: set() for cycle_id in frustrated}
    for left_index, left in enumerate(frustrated):
        for right in frustrated[left_index + 1 :]:
            if set(cycles[left]) & set(cycles[right]):
                adjacency[left].add(right)
                adjacency[right].add(left)
    unseen = set(frustrated)
    components = []
    while unseen:
        root = min(unseen)
        stack = [root]
        component = set()
        while stack:
            node = stack.pop()
            if node in component:
                continue
            component.add(node)
            stack.extend(sorted(adjacency[node] - component, reverse=True))
        unseen -= component
        components.append(tuple(sorted(component)))
    ordered = tuple(sorted(components, key=lambda item: (-len(item), item)))
    sizes = tuple(len(item) for item in ordered)
    denominator = syndrome.incidence_rank
    largest = (max(sizes, default=0) / denominator) if denominator else 0.0
    return FrustratedClusterReport(
        cluster_count=len(ordered),
        clusters=ordered,
        cluster_sizes=sizes,
        largest_cluster_fraction=float(largest),
    )


def _rref_solution(matrix: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, list[np.ndarray], int]:
    rows, columns = matrix.shape
    augmented = np.column_stack([matrix.copy() % 2, target.copy() % 2]).astype(np.uint8)
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(columns):
        candidates = np.flatnonzero(augmented[pivot_row:, column])
        if not len(candidates):
            continue
        selected = pivot_row + int(candidates[0])
        augmented[[pivot_row, selected]] = augmented[[selected, pivot_row]]
        for row in range(rows):
            if row != pivot_row and augmented[row, column]:
                augmented[row] ^= augmented[pivot_row]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break
    for row in range(pivot_row, rows):
        if not np.any(augmented[row, :columns]) and augmented[row, columns]:
            raise ValueError("syndrome is inconsistent with cycle incidence")
    particular = np.zeros(columns, dtype=np.uint8)
    for row, column in enumerate(pivot_columns):
        particular[column] = augmented[row, columns]
    free_columns = [column for column in range(columns) if column not in pivot_columns]
    null_basis = []
    for free in free_columns:
        vector = np.zeros(columns, dtype=np.uint8)
        vector[free] = 1
        for row, pivot in enumerate(pivot_columns):
            vector[pivot] = augmented[row, free]
        null_basis.append(vector)
    return particular, null_basis, len(pivot_columns)


def _edge_disjoint_lower_bound(
    cycles: Sequence[tuple[str, tuple[str, ...]]], syndrome: Sequence[int]
) -> int:
    selected: list[set[str]] = []
    candidates = sorted(
        (set(boundary) for (_, boundary), value in zip(cycles, syndrome) if value),
        key=lambda value: (len(value), tuple(sorted(value))),
    )
    for candidate in candidates:
        if all(candidate.isdisjoint(existing) for existing in selected):
            selected.append(candidate)
    return len(selected)


def coboundary_distance(
    *,
    cycle_basis_edge_ids: Mapping[str, Sequence[str]] | Sequence[Sequence[str]],
    edge_signs: Mapping[str, int],
) -> CoboundaryDistance:
    """Minimum edge-sign corrections needed to trivialize the measured w1.

    The exact path enumerates the affine kernel coset when its dimension is at
    most 20.  Larger instances return a certified edge-disjoint-cycle lower
    bound and a valid observed-sign correction upper bound.
    """

    cycles = _normalize_cycle_basis(cycle_basis_edge_ids)
    receipt = sign_syndrome(cycle_basis_edge_ids=dict(cycles), edge_signs=edge_signs)
    matrix = np.asarray(receipt.cycle_edge_incidence, dtype=np.uint8)
    target = np.asarray(receipt.syndrome, dtype=np.uint8)
    if matrix.size == 0:
        return CoboundaryDistance("exact_coset_enumeration", 0, 0, 0, (), 0, 0)
    particular, null_basis, rank = _rref_solution(matrix, target)
    nullity = matrix.shape[1] - rank
    if nullity <= 20:
        best = particular.copy()
        best_weight = int(np.sum(best))
        for coefficients in product((0, 1), repeat=nullity):
            candidate = particular.copy()
            for coefficient, vector in zip(coefficients, null_basis):
                if coefficient:
                    candidate ^= vector
            weight = int(np.sum(candidate))
            if weight < best_weight or (
                weight == best_weight and tuple(candidate.tolist()) < tuple(best.tolist())
            ):
                best, best_weight = candidate, weight
        correction = tuple(
            edge for edge, value in zip(receipt.edge_ids, best) if value
        )
        return CoboundaryDistance(
            mode="exact_coset_enumeration",
            exact_distance=best_weight,
            lower_bound=best_weight,
            upper_bound=best_weight,
            correction_edge_ids=correction,
            cycle_rank=rank,
            coset_dimension=nullity,
        )
    observed = np.asarray(
        [int(int(edge_signs[edge]) < 0) for edge in receipt.edge_ids], dtype=np.uint8
    )
    if not np.array_equal((matrix @ observed) % 2, target):
        raise AssertionError("observed negative-edge set did not reproduce syndrome")
    lower = _edge_disjoint_lower_bound(cycles, receipt.syndrome)
    correction = tuple(
        edge for edge, value in zip(receipt.edge_ids, observed) if value
    )
    return CoboundaryDistance(
        mode="certified_bounds_observed_correction_upper",
        exact_distance=None,
        lower_bound=lower,
        upper_bound=len(correction),
        correction_edge_ids=correction,
        cycle_rank=rank,
        coset_dimension=nullity,
    )


class _UnionFind:
    def __init__(self, nodes: Sequence[str]) -> None:
        self.parent = {value: value for value in nodes}

    def find(self, value: str) -> str:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, first: str, second: str) -> bool:
        left, right = self.find(first), self.find(second)
        if left == right:
            return False
        if left > right:
            left, right = right, left
        self.parent[right] = left
        return True


def _tree_path(adjacency: Mapping[str, list[tuple[str, str]]], source: str, target: str) -> list[str]:
    stack = [(source, None)]
    parent: dict[str, tuple[str | None, str | None]] = {source: (None, None)}
    while stack:
        node, _ = stack.pop()
        if node == target:
            break
        for neighbor, edge_id in sorted(adjacency[node], reverse=True):
            if neighbor not in parent:
                parent[neighbor] = (node, edge_id)
                stack.append((neighbor, edge_id))
    if target not in parent:
        raise AssertionError("tree endpoints are not connected")
    edges = []
    node = target
    while parent[node][0] is not None:
        previous, edge_id = parent[node]
        edges.append(str(edge_id))
        node = str(previous)
    return list(reversed(edges))


def fundamental_cycle_basis(
    *, edges: Iterable[Any], registered_nodes: Iterable[str] = ()
) -> dict[str, tuple[str, ...]]:
    """Return a deterministic fundamental-cycle basis of the admitted graph."""

    normalized = _normalize_edges(edges)
    nodes = _node_universe(normalized, registered_nodes)
    union = _UnionFind(nodes)
    adjacency: dict[str, list[tuple[str, str]]] = {node: [] for node in nodes}
    cycles: dict[str, tuple[str, ...]] = {}
    for edge in sorted(normalized, key=lambda value: value["edge_id"]):
        source, target, edge_id = edge["source_node"], edge["target_node"], edge["edge_id"]
        if union.union(source, target):
            adjacency[source].append((target, edge_id))
            adjacency[target].append((source, edge_id))
        else:
            path = _tree_path(adjacency, source, target) if source != target else []
            cycles[f"fundamental:{edge_id}"] = tuple(path + [edge_id])
    expected = len(normalized) - len(nodes) + len({union.find(node) for node in nodes})
    if len(cycles) != expected:
        raise AssertionError("fundamental-cycle count differs from beta_1")
    return cycles


def gauge_transform_edge_signs(
    *,
    edges: Iterable[Any],
    edge_signs: Mapping[str, int],
    node_flips: Mapping[str, int],
) -> dict[str, int]:
    """Apply a node-frame coboundary to edge signs."""

    normalized = _normalize_edges(edges)
    output = dict((str(key), int(value)) for key, value in edge_signs.items())
    for edge in normalized:
        source_flip = int(node_flips.get(edge["source_node"], 1))
        target_flip = int(node_flips.get(edge["target_node"], 1))
        if source_flip not in (-1, 1) or target_flip not in (-1, 1):
            raise ValueError("node flips must lie in {-1,+1}")
        output[edge["edge_id"]] = (
            int(edge_signs[edge["edge_id"]]) * source_flip * target_flip
        )
    return output


def percolation_phase_point(
    *,
    edges: Iterable[Any],
    loops: Iterable[Any],
    registered_nodes: Iterable[str],
    edge_signs: Mapping[str, int],
    lineage_floor: float,
) -> PhasePoint:
    """Classify one lineage-floor/sign-field point with re-derivable receipts."""

    normalized = _normalize_edges(edges)
    nodes = _node_universe(normalized, registered_nodes)
    loop_values = tuple(_loop_record(item) for item in loops)
    filtered = build_lineage_holonomy_bifiltration(
        edges=normalized,
        lineage_floor=lineage_floor,
        loops=loop_values,
        registered_nodes=nodes,
    )
    admitted_ids = set(filtered.admitted_edge_ids)
    admitted = tuple(item for item in normalized if item["edge_id"] in admitted_ids)
    admitted_signs = {edge_id: int(edge_signs[edge_id]) for edge_id in admitted_ids}
    basis = fundamental_cycle_basis(edges=admitted, registered_nodes=nodes) if admitted else {}
    if basis:
        syndrome = sign_syndrome(cycle_basis_edge_ids=basis, edge_signs=admitted_signs)
        clusters = frustrated_clusters(syndrome=syndrome, cycle_basis_edge_ids=basis)
        distance = coboundary_distance(cycle_basis_edge_ids=basis, edge_signs=admitted_signs)
    else:
        syndrome = SignSyndrome((), (), (), (), 0, True, ())
        clusters = FrustratedClusterReport(0, (), (), 0.0)
        distance = CoboundaryDistance("exact_coset_enumeration", 0, 0, 0, (), 0, 0)
    connected = filtered.connected_component_count == 1
    phase = "disconnected" if not connected else ("coherent" if syndrome.w1_trivial else "frustrated")
    largest = max(map(len, filtered.connected_components), default=0) / len(nodes)
    return PhasePoint(
        lineage_floor=float(lineage_floor),
        phase=phase,
        admitted_edge_count=filtered.admitted_edge_count,
        connected_component_count=filtered.connected_component_count,
        largest_component_fraction=float(largest),
        beta_1=filtered.beta_1,
        admitted_registered_loop_count=len(filtered.admitted_loop_ids),
        syndrome=syndrome,
        frustrated_clusters=clusters,
        coboundary_distance=distance,
    )


def retention_permutation_nulls(
    *,
    edges: Iterable[Any],
    loops: Iterable[Any] = (),
    registered_nodes: Iterable[str] = (),
    edge_classes: Mapping[str, str],
    replicates: int,
    root_seed: int,
    experiment_id: str = "07_percolation_phase",
) -> dict[str, list[dict[str, Any]]]:
    """Return separately named pooled and within-class retention nulls."""

    normalized = _normalize_edges(edges)
    if replicates < 1:
        raise ValueError("replicates must be positive")
    ids = [item["edge_id"] for item in normalized]
    if set(edge_classes) != set(ids):
        raise ValueError("edge_classes must cover the exact edge universe")
    output = {"pooled_retention_permutation": [], "within_class_retention_permutation": []}
    for name in output:
        for replicate in range(replicates):
            seed = derived_seed(root_seed, f"{experiment_id}:{name}:{replicate}")
            rng = np.random.default_rng(seed)
            values = np.asarray([item["lineage"] for item in normalized])
            shuffled = values.copy()
            if name == "pooled_retention_permutation":
                rng.shuffle(shuffled)
            else:
                for label in sorted(set(edge_classes.values())):
                    indices = [index for index, edge_id in enumerate(ids) if edge_classes[edge_id] == label]
                    selected = shuffled[indices].copy()
                    rng.shuffle(selected)
                    shuffled[indices] = selected
            permuted = [dict(item, lineage=float(value)) for item, value in zip(normalized, shuffled)]
            curve = lineage_percolation_curve(
                edges=permuted,
                loops=loops,
                registered_nodes=registered_nodes,
                edge_classes=edge_classes,
            )
            output[name].append(
                {"replicate": replicate, "seed": seed, "curve": curve.to_dict()}
            )
    return output


def sign_noise_ensemble(
    *,
    edges: Iterable[Any],
    loops: Iterable[Any],
    registered_nodes: Iterable[str],
    base_edge_signs: Mapping[str, int],
    lineage_floor: float,
    q_values: Sequence[float],
    replicates: int,
    root_seed: int,
    experiment_id: str = "07_percolation_phase",
) -> list[dict[str, Any]]:
    """Flip each edge sign independently and emit phase receipts."""

    normalized = _normalize_edges(edges)
    if replicates < 1:
        raise ValueError("replicates must be positive")
    rows = []
    for q in q_values:
        if not np.isfinite(q) or not 0.0 <= q <= 1.0:
            raise ValueError("sign-flip rate q must lie in [0,1]")
        for replicate in range(replicates):
            cell = f"{lineage_floor:.12g}:{q:.12g}:{replicate}"
            seed = derived_seed(root_seed, f"{experiment_id}:sign_noise:{cell}")
            rng = np.random.default_rng(seed)
            signs = {
                item["edge_id"]: int(base_edge_signs[item["edge_id"]])
                * (-1 if rng.random() < q else 1)
                for item in normalized
            }
            point = percolation_phase_point(
                edges=normalized,
                loops=loops,
                registered_nodes=registered_nodes,
                edge_signs=signs,
                lineage_floor=lineage_floor,
            )
            rows.append(
                {"q": float(q), "replicate": replicate, "seed": seed, **point.to_dict()}
            )
    return rows
