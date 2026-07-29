from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import networkx as nx


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
K4_EDGES = (
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 3),
    (2, 3),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def components(
    node_count: int, edges: tuple[tuple[int, int], ...], mask: int
) -> int:
    graph = nx.Graph()
    graph.add_nodes_from(range(node_count))
    graph.add_edges_from(
        edge
        for index, edge in enumerate(edges)
        if (mask >> index) & 1
    )
    return nx.number_connected_components(graph)


def random_cluster_numerator(
    node_count: int,
    edges: tuple[tuple[int, int], ...],
    counts: tuple[int, ...],
) -> int:
    weights = tuple(2**count - 1 for count in counts)
    total = 0
    for mask in range(1 << len(edges)):
        term = (-1) ** components(node_count, edges, mask)
        for index, weight in enumerate(weights):
            if (mask >> index) & 1:
                term *= weight
        total += term
    return -total


def direct_numerator(
    node_count: int,
    edges: tuple[tuple[int, int], ...],
    counts: tuple[int, ...],
) -> int:
    total = 0
    for statuses in itertools.product((0, 1, 2), repeat=len(edges)):
        graph = nx.DiGraph()
        graph.add_nodes_from(range(node_count))
        multiplicity = 1
        for index, ((source, target), status) in enumerate(
            zip(edges, statuses, strict=True)
        ):
            if status in (0, 1):
                graph.add_edge(source, target)
            if status in (1, 2):
                graph.add_edge(target, source)
            if status == 1:
                multiplicity *= 2**counts[index] - 2
        if nx.is_strongly_connected(graph):
            total += multiplicity
    return total


def coefficient(
    node_count: int,
    edges: tuple[tuple[int, int], ...],
    interior_mask: int,
) -> int:
    total = 0
    for mask in range(1 << len(edges)):
        if mask & interior_mask != interior_mask:
            continue
        total -= (-1) ** components(node_count, edges, mask)
    return total


def direct_completion_count(
    node_count: int,
    edges: tuple[tuple[int, int], ...],
    interior_mask: int,
) -> int:
    oriented = tuple(
        index
        for index in range(len(edges))
        if not (interior_mask >> index) & 1
    )
    total = 0
    for directions in itertools.product((0, 1), repeat=len(oriented)):
        graph = nx.DiGraph()
        graph.add_nodes_from(range(node_count))
        assignment = dict(zip(oriented, directions, strict=True))
        for index, (source, target) in enumerate(edges):
            if (interior_mask >> index) & 1:
                graph.add_edge(source, target)
                graph.add_edge(target, source)
            elif assignment[index] == 0:
                graph.add_edge(source, target)
            else:
                graph.add_edge(target, source)
        total += nx.is_strongly_connected(graph)
    return total


def record_fraction(record: dict[str, int]) -> Fraction:
    return Fraction(record["numerator"], record["denominator"])


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
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    result = json.loads(args.result.read_text(encoding="utf-8"))
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    checks["registration_hash"] = (
        sha256(args.registration) == result["registration_sha256"]
        == receipt["registration_sha256"]
    )
    checks["result_hash"] = sha256(args.result) == receipt["result_sha256"]
    checks["sealed_files"] = all(
        sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )
    checks["protocol_hash"] = (
        sha256(REPO / registration["protocol_path"])
        == receipt["protocol_sha256"]
    )

    raw_graph = protocol["fresh_validation"]["graph"]
    node_count = raw_graph["node_count"]
    edges = tuple(tuple(edge) for edge in raw_graph["edges"])
    expected_primary: dict[str, int] = {}
    for name, raw_counts in protocol["fresh_validation"]["counts"].items():
        counts = tuple(raw_counts)
        expected_primary[name] = random_cluster_numerator(
            node_count, edges, counts
        )
        checks[f"primary_direct_{name}"] = (
            direct_numerator(node_count, edges, counts)
            == expected_primary[name]
        )
    for row in result["primary_rows"]:
        expected = expected_primary[row["name"]]
        checks[f"primary_result_{row['name']}"] = (
            row["trial_numerator"] == expected
            and record_fraction(row["direct"])
            == Fraction(expected, 2 ** row["total_trials"])
            and record_fraction(row["multivariate"])
            == Fraction(expected, 2 ** row["total_trials"])
        )

    expected_coefficients = {}
    for mask in protocol["fresh_validation"]["coefficient_masks"]:
        expected_coefficients[mask] = coefficient(
            node_count, edges, mask
        )
        checks[f"coefficient_direct_{mask}"] = (
            direct_completion_count(node_count, edges, mask)
            == expected_coefficients[mask]
        )
    checks["coefficient_result_rows"] = all(
        row["coefficient"] == expected_coefficients[row["mask"]]
        and row["direct_completion_count"]
        == expected_coefficients[row["mask"]]
        for row in result["coefficient_rows"]
    )

    k4_ok = True
    for row in result["k4_rows"]:
        s = row["s"]
        t = 2**s
        trap = (s - 1, s, s + 1, s + 1, s, s - 1)
        balanced = (s,) * 6
        trap_value = random_cluster_numerator(4, K4_EDGES, trap)
        balanced_value = random_cluster_numerator(
            4, K4_EDGES, balanced
        )
        k4_ok &= row["trap_numerator"] == trap_value
        k4_ok &= row["balanced_numerator"] == balanced_value
        k4_ok &= (
            row["balanced_minus_trap_gap"]
            == balanced_value - trap_value
            == 3 * t * (3 * t - 4) // 2
        )
        k4_ok &= row["neighbor_count"] == 30
        k4_ok &= row["neighbor_class_count"] == 9
        k4_ok &= row["neighbor_minimum_gap"] > 0
        k4_ok &= all(
            exchange["deficit"] == t**2 * (4 * t - 5) // 2
            and exchange["positive"]
            for exchange in row["exchange_rows"]
        )
    checks["k4_rows"] = k4_ok
    checks["all_gates_pass"] = all(result["gate_passes"].values())
    checks["verdict"] = result["verdict"] == protocol["verdict_map"][
        "all_gates_pass"
    ]
    checks["resource_caps"] = (
        receipt["wall_seconds"]
        <= protocol["resource_caps"]["wall_seconds"]
        and receipt["peak_resident_bytes"]
        <= protocol["resource_caps"]["peak_resident_bytes"]
    )

    output = {
        "check_count": len(checks),
        "checks": checks,
        "pass": all(checks.values()),
        "receipt_sha256": sha256(args.receipt),
        "result_sha256": sha256(args.result),
        "verifier_sha256": sha256(Path(__file__)),
    }
    write_json_exclusive(args.output, output)
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
