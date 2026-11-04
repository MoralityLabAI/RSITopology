"""Independent verifier for the ASMP-9 v0.20 registered result.

This file imports neither the implementation module nor the registered runner.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
Edge = tuple[int, int]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def graph_signature(
    node_count: int, edges: Sequence[Edge]
) -> str:
    canonical = tuple(
        sorted(tuple(sorted(edge)) for edge in edges)
    )
    return hashlib.sha256(
        json.dumps(
            {
                "node_count": node_count,
                "edges": [list(edge) for edge in canonical],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def component_count(
    node_count: int,
    edges: Sequence[Edge],
    excluded: int | None = None,
) -> int:
    adjacency = [[] for _ in range(node_count)]
    for edge_id, (source, target) in enumerate(edges):
        if edge_id == excluded:
            continue
        adjacency[source].append(target)
        adjacency[target].append(source)
    seen: set[int] = set()
    count = 0
    for root in range(node_count):
        if root in seen:
            continue
        count += 1
        seen.add(root)
        stack = [root]
        while stack:
            node = stack.pop()
            for target in adjacency[node]:
                if target not in seen:
                    seen.add(target)
                    stack.append(target)
    return count


def bridges(
    node_count: int, edges: Sequence[Edge]
) -> frozenset[int]:
    base = component_count(node_count, edges)
    return frozenset(
        edge_id
        for edge_id in range(len(edges))
        if component_count(node_count, edges, edge_id) > base
    )


def blocks(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    parent = list(range(len(edges)))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        left = find(left)
        right = find(right)
        if left != right:
            parent[right] = left

    for selected in itertools.chain.from_iterable(
        itertools.combinations(range(len(edges)), size)
        for size in range(3, len(edges) + 1)
    ):
        degree = [0] * node_count
        adjacency = [[] for _ in range(node_count)]
        for edge_id in selected:
            source, target = edges[edge_id]
            degree[source] += 1
            degree[target] += 1
            adjacency[source].append(target)
            adjacency[target].append(source)
        vertices = {
            node for node, value in enumerate(degree) if value
        }
        if (
            len(vertices) != len(selected)
            or any(degree[node] != 2 for node in vertices)
        ):
            continue
        root = next(iter(vertices))
        seen = {root}
        stack = [root]
        while stack:
            node = stack.pop()
            for target in adjacency[node]:
                if target not in seen:
                    seen.add(target)
                    stack.append(target)
        if seen == vertices:
            for edge_id in selected[1:]:
                union(selected[0], edge_id)
    groups: dict[int, list[int]] = {}
    for edge_id in range(len(edges)):
        groups.setdefault(find(edge_id), []).append(edge_id)
    return tuple(
        sorted(
            (tuple(sorted(group)) for group in groups.values()),
            key=lambda block: (min(block), block),
        )
    )


def reachability(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[int],
    edge_ids: Sequence[int] | None = None,
) -> tuple[int, ...]:
    selected: Iterable[int] = (
        range(len(edges)) if edge_ids is None else edge_ids
    )
    reach = [1 << node for node in range(node_count)]
    for edge_id in selected:
        source, target = edges[edge_id]
        status = statuses[edge_id]
        if status in (0, 1):
            reach[source] |= 1 << target
        if status in (1, 2):
            reach[target] |= 1 << source
    for middle in range(node_count):
        bit = 1 << middle
        for source in range(node_count):
            if reach[source] & bit:
                reach[source] |= reach[middle]
    return tuple(reach)


@dataclass(frozen=True)
class OracleGraph:
    node_count: int
    edges: tuple[Edge, ...]
    blocks: tuple[tuple[int, ...], ...]
    bridges: frozenset[int]

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "OracleGraph":
        node_count = int(raw["node_count"])
        edges = tuple(tuple(edge) for edge in raw["edges"])
        return cls(
            node_count,
            edges,
            blocks(node_count, edges),
            bridges(node_count, edges),
        )

    @property
    def cyclic(self) -> tuple[tuple[int, ...], ...]:
        return tuple(
            block for block in self.blocks if len(block) > 1
        )

    def direct(self, statuses: Sequence[int]) -> bool:
        reach = reachability(
            self.node_count, self.edges, statuses
        )
        return all(
            edge_id in self.bridges
            or (
                reach[source] & (1 << target)
                and reach[target] & (1 << source)
            )
            for edge_id, (source, target) in enumerate(self.edges)
        )

    def blockwise(self, statuses: Sequence[int]) -> bool:
        for block in self.cyclic:
            vertices = {
                vertex
                for edge_id in block
                for vertex in self.edges[edge_id]
            }
            reach = reachability(
                self.node_count, self.edges, statuses, block
            )
            root = next(iter(vertices))
            if any(
                not (reach[root] & (1 << vertex))
                or not (reach[vertex] & (1 << root))
                for vertex in vertices
            ):
                return False
        return True


_LIVE: dict[
    tuple[int, tuple[Edge, ...]],
    tuple[tuple[int, ...], ...],
] = {}
_WORST: dict[
    tuple[
        int,
        tuple[Edge, ...],
        tuple[int, ...],
        int,
        int,
    ],
    tuple[Fraction, tuple[tuple[int, ...], ...]],
] = {}


def live_states(graph: OracleGraph) -> tuple[tuple[int, ...], ...]:
    key = graph.node_count, graph.edges
    if key not in _LIVE:
        _LIVE[key] = tuple(
            statuses
            for statuses in itertools.product(
                (0, 1, 2), repeat=len(graph.edges)
            )
            if graph.direct(statuses)
        )
    return _LIVE[key]


def weights(
    count: int, label: int, epsilon: Fraction
) -> tuple[int, int, int]:
    denominator = epsilon.denominator
    probability = (
        epsilon.numerator
        if label == 0
        else denominator - epsilon.numerator
    )
    zero = (denominator - probability) ** count
    full = probability**count
    return zero, denominator**count - zero - full, full


def availability(
    graph: OracleGraph,
    counts: Sequence[int],
    labels: Sequence[int],
    epsilon: Fraction,
) -> Fraction:
    laws = tuple(
        weights(count, label, epsilon)
        for count, label in zip(counts, labels, strict=True)
    )
    numerator = 0
    for statuses in live_states(graph):
        mass = 1
        for edge_id, status in enumerate(statuses):
            mass *= laws[edge_id][status]
        numerator += mass
    return Fraction(
        numerator, epsilon.denominator ** sum(counts)
    )


def local_graph(
    graph: OracleGraph, block: Sequence[int]
) -> OracleGraph:
    vertices = sorted(
        {
            vertex
            for edge_id in block
            for vertex in graph.edges[edge_id]
        }
    )
    local = {vertex: index for index, vertex in enumerate(vertices)}
    raw = {
        "node_count": len(vertices),
        "edges": [
            [
                local[graph.edges[edge_id][0]],
                local[graph.edges[edge_id][1]],
            ]
            for edge_id in block
        ],
    }
    return OracleGraph.from_raw(raw)


def product_availability(
    graph: OracleGraph,
    counts: Sequence[int],
    labels: Sequence[int],
    epsilon: Fraction,
) -> Fraction:
    result = Fraction(1)
    for block in graph.cyclic:
        result *= availability(
            local_graph(graph, block),
            tuple(counts[index] for index in block),
            tuple(labels[index] for index in block),
            epsilon,
        )
    return result


def worst(
    graph: OracleGraph,
    counts: Sequence[int],
    epsilon: Fraction,
) -> tuple[Fraction, tuple[tuple[int, ...], ...]]:
    key = (
        graph.node_count,
        graph.edges,
        tuple(counts),
        epsilon.numerator,
        epsilon.denominator,
    )
    if key in _WORST:
        return _WORST[key]
    best: Fraction | None = None
    witnesses = []
    for labels in itertools.product(
        (0, 1), repeat=len(graph.edges)
    ):
        value = availability(graph, counts, labels, epsilon)
        if best is None or value < best:
            best = value
            witnesses = [labels]
        elif value == best:
            witnesses.append(labels)
    if best is None:
        raise AssertionError("empty label universe")
    result = best, tuple(witnesses)
    _WORST[key] = result
    return result


def product_worst(
    graph: OracleGraph,
    counts: Sequence[int],
    epsilon: Fraction,
) -> Fraction:
    result = Fraction(1)
    for block in graph.cyclic:
        result *= worst(
            local_graph(graph, block),
            tuple(counts[index] for index in block),
            epsilon,
        )[0]
    return result


def compositions(
    total: int, parts: int
) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total - parts + 2):
        for tail in compositions(total - first, parts - 1):
            yield (first, *tail)


def design_oracle(
    graph: OracleGraph, total: int, epsilon: Fraction
) -> tuple[
    Fraction,
    tuple[tuple[int, ...], ...],
    int,
]:
    best: Fraction | None = None
    optimizers = []
    count = 0
    for allocation in compositions(total, len(graph.edges)):
        count += 1
        value = product_worst(graph, allocation, epsilon)
        if best is None or value > best:
            best = value
            optimizers = [allocation]
        elif value == best:
            optimizers.append(allocation)
    if best is None:
        raise AssertionError("empty allocation universe")
    return best, tuple(optimizers), count


def verify(
    protocol_path: Path,
    registration_path: Path,
    result_path: Path,
    receipt_path: Path,
) -> dict[str, bool]:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    registration = json.loads(
        registration_path.read_text(encoding="utf-8")
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["sealed_files"] = all(
        (REPO / relative).is_file()
        and sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )
    checks["hash_chain"] = (
        sha256(protocol_path)
        == result["protocol_sha256"]
        == receipt["protocol_sha256"]
        and sha256(registration_path)
        == result["registration_sha256"]
        == receipt["registration_sha256"]
        and sha256(result_path) == receipt["result_sha256"]
    )
    checks["claim_boundary"] = (
        result["claim_boundary"] == protocol["claim_boundary"]
    )

    graphs = {
        name: OracleGraph.from_raw(raw)
        for name, raw in protocol["graphs"].items()
    }
    burned = set(
        protocol["freshness_rule"][
            "burned_full_graph_signatures"
        ].values()
    )
    full_signatures = {
        name: graph_signature(graph.node_count, graph.edges)
        for name, graph in graphs.items()
    }
    freshness_ok = (
        len(set(full_signatures.values())) == len(full_signatures)
        and all(
            graph.node_count
            >= protocol["freshness_rule"][
                "minimum_node_count_for_every_registered_graph"
            ]
            for graph in graphs.values()
        )
        and not (set(full_signatures.values()) & burned)
    )
    reported_partitions = {
        row["graph"]: row for row in result["block_partitions"]
    }
    checks["block_partitions"] = all(
        graph.blocks
        == tuple(
            tuple(block)
            for block in protocol["graphs"][name][
                "expected_blocks"
            ]
        )
        == tuple(
            tuple(block)
            for block in reported_partitions[name][
                "implementation_blocks"
            ]
        )
        == tuple(
            tuple(block)
            for block in reported_partitions[name]["oracle_blocks"]
        )
        == tuple(
            tuple(block)
            for block in reported_partitions[name]["expected_blocks"]
        )
        and reported_partitions[name]["match"]
        for name, graph in graphs.items()
    )

    reported_status = {
        row["graph"]: row for row in result["status_censuses"]
    }
    status_ok = True
    for name in protocol["status_census_graphs"]:
        graph = graphs[name]
        mismatch = 0
        checked = 0
        for statuses in itertools.product(
            (0, 1, 2), repeat=len(graph.edges)
        ):
            checked += 1
            mismatch += graph.direct(statuses) != graph.blockwise(
                statuses
            )
        row = reported_status[name]
        status_ok = status_ok and (
            mismatch == 0
            and row["mismatch_count"] == 0
            and row["status_vectors_checked"] == checked
        )
    checks["status_equivalence"] = status_ok

    reported_probability = {
        row["graph"]: row
        for row in result["fixed_probability_products"]
    }
    probability_ok = True
    for raw in protocol["fixed_probability_cells"]:
        graph = graphs[raw["graph"]]
        counts = tuple(raw["counts"])
        labels = tuple(int(item) for item in raw["labels"])
        epsilon = Fraction(raw["epsilon"])
        direct = availability(graph, counts, labels, epsilon)
        product = product_availability(
            graph, counts, labels, epsilon
        )
        row = reported_probability[raw["graph"]]
        probability_ok = probability_ok and (
            direct == product
            and row["direct"] == fraction_text(direct)
            and row["product"] == fraction_text(product)
            and row["match"]
        )
    checks["probability_products"] = probability_ok

    raw = protocol["worst_label_cell"]
    graph = graphs[raw["graph"]]
    counts = tuple(raw["counts"])
    epsilon = Fraction(raw["epsilon"])
    global_worst, witnesses = worst(graph, counts, epsilon)
    local_product = product_worst(graph, counts, epsilon)
    reported_worst = result["worst_label_product"]
    checks["worst_label_product"] = (
        global_worst == local_product
        and reported_worst["global_worst"]
        == fraction_text(global_worst)
        and reported_worst["product_worst"]
        == fraction_text(local_product)
        and reported_worst["global_witness_count"]
        == len(witnesses)
        and reported_worst["match"]
    )

    bridge = graphs["bridge_separated_cycles"]
    epsilon = Fraction(2, 9)
    value_a = availability(
        bridge,
        (2, 1, 2, 1, 2, 1, 2, 1, 1),
        (0, 1, 0, 0, 1, 0, 1, 0, 0),
        epsilon,
    )
    value_b = availability(
        bridge,
        (2, 1, 2, 7, 2, 1, 2, 1, 5),
        (0, 1, 0, 1, 1, 0, 1, 0, 1),
        epsilon,
    )
    bridge_groups: dict[tuple[int, ...], bool] = {}
    bridge_status_violations = 0
    nonbridges = tuple(
        edge_id
        for edge_id in range(len(bridge.edges))
        if edge_id not in bridge.bridges
    )
    for statuses in itertools.product(
        (0, 1, 2), repeat=len(bridge.edges)
    ):
        key = tuple(statuses[index] for index in nonbridges)
        value = bridge.direct(statuses)
        if key in bridge_groups and bridge_groups[key] != value:
            bridge_status_violations += 1
        bridge_groups[key] = value
    reported_bridge = result["bridge_irrelevance"]
    checks["bridge_irrelevance"] = (
        bridge.bridges == frozenset((3, 8))
        and value_a == value_b
        and reported_bridge["availability_a"]
        == fraction_text(value_a)
        and reported_bridge["availability_b"]
        == fraction_text(value_b)
        and bridge_status_violations == 0
        and reported_bridge["status_violations"]
        == bridge_status_violations
        and reported_bridge["status_group_count"]
        == len(bridge_groups)
        and reported_bridge["exact_match"]
    )

    design_raw = protocol["design_cell"]
    design_value, design_optimizers, allocation_count = (
        design_oracle(
            graphs[design_raw["graph"]],
            int(design_raw["total_budget"]),
            Fraction(design_raw["epsilon"]),
        )
    )
    reported_design = result["design_comparison"]
    checks["design"] = (
        reported_design["bellman_value"]
        == reported_design["exhaustive_value"]
        == fraction_text(design_value)
        and {
            tuple(item)
            for item in reported_design["bellman_optimizers"]
        }
        == {
            tuple(item)
            for item in reported_design[
                "exhaustive_optimizers"
            ]
        }
        == set(design_optimizers)
        and reported_design["allocation_count"]
        == allocation_count
        and reported_design["exact_match"]
    )

    control_raw = protocol["one_block_negative_control"]
    control = graphs[control_raw["graph"]]
    control_value = availability(
        control,
        tuple(control_raw["counts"]),
        tuple(int(item) for item in control_raw["labels"]),
        Fraction(control_raw["epsilon"]),
    )
    reported_control = result["one_block_negative_control"]
    checks["one_block_control"] = (
        len(control.cyclic) == 1
        and reported_control["factor_count"] == 1
        and reported_control["direct"]
        == reported_control["product"]
        == fraction_text(control_value)
        and reported_control["exact_match"]
        and reported_control["interpretation"]
        == control_raw["required_interpretation"]
    )

    gate_map = {
        row["gate_id"]: bool(row["pass"])
        for row in result["gates"]
    }
    checks["gate_universe"] = (
        tuple(gate_map) == tuple(protocol["gate_ids"])
        and result["gate_count"] == len(protocol["gate_ids"])
        and result["gate_pass_count"] == sum(gate_map.values())
    )
    resources = result["resources"]
    recomputed_resource = (
        not resources["gpu_used"]
        and resources["elapsed_seconds"]
        <= protocol["resource_caps"]["wall_seconds"]
        and resources["peak_resident_bytes"]
        <= protocol["resource_caps"]["peak_resident_bytes"]
    )
    substantive = (
        checks["sealed_files"]
        and checks["hash_chain"]
        and checks["claim_boundary"]
        and checks["block_partitions"]
        and checks["status_equivalence"]
        and checks["probability_products"]
        and checks["worst_label_product"]
        and checks["bridge_irrelevance"]
        and checks["design"]
        and checks["one_block_control"]
    )
    expected_gate_map = {
        "G0_registration_binding": (
            checks["sealed_files"] and checks["hash_chain"]
        ),
        "G1_fresh_graph_registry": (
            freshness_ok
            and result["fresh_registry"]["violations"] == []
        ),
        "G2_block_partition": checks["block_partitions"],
        "G3_exhaustive_status_equivalence": checks[
            "status_equivalence"
        ],
        "G4_fixed_label_probability_product": checks[
            "probability_products"
        ],
        "G5_rectangular_worst_label_product": checks[
            "worst_label_product"
        ],
        "G6_bridge_irrelevance": checks["bridge_irrelevance"],
        "G7_bellman_equals_full_edge_census": checks["design"],
        "G8_one_block_negative_control": checks[
            "one_block_control"
        ],
        "G9_resource_and_scope": (
            recomputed_resource and checks["claim_boundary"]
        ),
    }
    checks["gate_mapping"] = gate_map == expected_gate_map
    all_gates = all(expected_gate_map.values())
    expected_verdict = (
        "finite_block_factorization_established_in_frozen_model_v0_20"
        if all_gates
        else "finite_block_factorization_not_established_v0_20"
    )
    checks["verdict_mapping"] = (
        result["verdict"] == receipt["verdict"] == expected_verdict
    )
    checks["all_recomputed_substance"] = substantive
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    checks = verify(
        args.protocol.resolve(),
        args.registration.resolve(),
        args.result.resolve(),
        args.receipt.resolve(),
    )
    output = {
        "checks": checks,
        "check_count": len(checks),
        "pass_count": sum(checks.values()),
        "pass": all(checks.values()),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    raise SystemExit(0 if output["pass"] else 1)


if __name__ == "__main__":
    main()
