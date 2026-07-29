from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Sequence

import networkx as nx


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
Edge = tuple[int, int]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps(value, indent=2, sort_keys=True) + "\n"
        )


def graph_parts(raw: dict[str, Any]) -> tuple[int, tuple[Edge, ...]]:
    return int(raw["node_count"]), tuple(
        tuple(edge) for edge in raw["edges"]
    )


def component_count(
    node_count: int,
    edges: Sequence[Edge],
    selected: Sequence[bool] | None = None,
) -> int:
    adjacency = [[] for _ in range(node_count)]
    for index, (source, target) in enumerate(edges):
        if selected is not None and not selected[index]:
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
            for neighbor in adjacency[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return count


def tutte_02_subset_expansion(
    node_count: int, edges: Sequence[Edge]
) -> int:
    base_components = component_count(node_count, edges)
    total = 0
    for bits in itertools.product((False, True), repeat=len(edges)):
        exponent = component_count(node_count, edges, bits) - base_components
        total += -1 if exponent % 2 else 1
    return total


def exhaustive_totally_cyclic(
    node_count: int, edges: Sequence[Edge]
) -> int:
    count = 0
    for bits in itertools.product((0, 1), repeat=len(edges)):
        directed = nx.DiGraph()
        directed.add_nodes_from(range(node_count))
        directed.add_edges_from(
            (source, target) if bit == 0 else (target, source)
            for (source, target), bit in zip(edges, bits, strict=True)
        )
        if all(
            nx.has_path(directed, target, source)
            for source, target in directed.edges()
        ):
            count += 1
    return count


def bridge_set(
    node_count: int, edges: Sequence[Edge]
) -> frozenset[int]:
    graph = nx.Graph()
    graph.add_nodes_from(range(node_count))
    graph.add_edges_from(edges)
    bridge_pairs = {frozenset(edge) for edge in nx.bridges(graph)}
    return frozenset(
        index
        for index, edge in enumerate(edges)
        if frozenset(edge) in bridge_pairs
    )


def exhaustive_asmp(
    node_count: int, edges: Sequence[Edge]
) -> int:
    bridges = bridge_set(node_count, edges)
    count = 0
    for bits in itertools.product((0, 1), repeat=len(edges)):
        directed = nx.DiGraph()
        directed.add_nodes_from(range(node_count))
        oriented = tuple(
            (source, target) if bit == 0 else (target, source)
            for (source, target), bit in zip(edges, bits, strict=True)
        )
        directed.add_edges_from(oriented)
        if all(
            index in bridges
            or nx.has_path(directed, target, source)
            for index, (source, target) in enumerate(oriented)
        ):
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    registration = json.loads(
        args.registration.read_text(encoding="utf-8")
    )
    result = json.loads(args.result.read_text(encoding="utf-8"))
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )

    checks: dict[str, bool] = {}
    checks["registration_hash"] = (
        sha256(args.registration) == result["registration_sha256"]
        == receipt["registration_sha256"]
    )
    checks["result_hash"] = sha256(args.result) == receipt["result_sha256"]
    checks["sealed_hashes"] = all(
        sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )

    independent: dict[str, Any] = {}
    for name, raw in protocol["primary_graphs"].items():
        node_count, edges = graph_parts(raw)
        subset = tutte_02_subset_expansion(node_count, edges)
        orientation = exhaustive_totally_cyclic(node_count, edges)
        asmp = exhaustive_asmp(node_count, edges)
        expected = result["primary_results"][name]
        independent[name] = {
            "asmp": asmp,
            "orientation": orientation,
            "subset_tutte_02": subset,
        }
        checks[f"{name}_three_way"] = (
            subset == orientation == asmp == expected["tutte_02"]
        )

    bridge_raw = protocol["controls"]["bridge_scope"]
    bridge_node_count, bridge_edges = graph_parts(bridge_raw)
    bridge_subset = tutte_02_subset_expansion(
        bridge_node_count, bridge_edges
    )
    bridge_orientation = exhaustive_totally_cyclic(
        bridge_node_count, bridge_edges
    )
    bridge_asmp = exhaustive_asmp(bridge_node_count, bridge_edges)
    bridge_result = result["gates"]["G6_bridge_scope_control"]
    checks["bridge_control"] = (
        bridge_subset
        == bridge_orientation
        == bridge_result["tutte_02"]
        == 0
        and bridge_asmp == bridge_result["asmp_numerator"]
    )

    product_raw = protocol["controls"]["block_product"]
    product_node_count, product_edges = graph_parts(product_raw)
    product_subset = tutte_02_subset_expansion(
        product_node_count, product_edges
    )
    product_orientation = exhaustive_totally_cyclic(
        product_node_count, product_edges
    )
    product_asmp = exhaustive_asmp(
        product_node_count, product_edges
    )
    product_result = result["gates"][
        "G7_block_product_and_localization"
    ]
    checks["block_product_control"] = (
        product_subset
        == product_orientation
        == product_asmp
        == product_result["tutte_02"]
    )
    checks["all_registered_gates_pass"] = all(
        result["gate_passes"].values()
    )
    checks["verdict"] = (
        result["verdict"]
        == protocol["verdict_map"]["all_gates_pass"]
    )

    payload = {
        "check_count": len(checks),
        "checks": checks,
        "independent_primary_results": independent,
        "pass": all(checks.values()),
        "result_sha256": sha256(args.result),
        "verifier_imports_implementation": False,
        "verifier_imports_runner": False,
    }
    write_json_exclusive(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

