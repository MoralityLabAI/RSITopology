from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Sequence


Edge = tuple[int, int]
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def component_count(
    node_count: int,
    edges: Sequence[Edge],
    excluded: int | None = None,
) -> int:
    adjacency = [[] for _ in range(node_count)]
    for index, (source, target) in enumerate(edges):
        if index == excluded:
            continue
        adjacency[source].append(target)
        adjacency[target].append(source)
    count = 0
    seen: set[int] = set()
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


def bridges(node_count: int, edges: Sequence[Edge]) -> set[int]:
    base = component_count(node_count, edges)
    return {
        index
        for index in range(len(edges))
        if component_count(node_count, edges, index) > base
    }


def core_components(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    bridge_set = bridges(node_count, edges)
    adjacency: list[list[tuple[int, int]]] = [
        [] for _ in range(node_count)
    ]
    for index, (source, target) in enumerate(edges):
        if index in bridge_set:
            continue
        adjacency[source].append((target, index))
        adjacency[target].append((source, index))
    seen: set[int] = set()
    rows = []
    for root in range(node_count):
        if root in seen or not adjacency[root]:
            continue
        vertices = {root}
        edge_ids: set[int] = set()
        seen.add(root)
        stack = [root]
        while stack:
            node = stack.pop()
            for neighbor, edge_id in adjacency[node]:
                vertices.add(neighbor)
                edge_ids.add(edge_id)
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        rows.append((tuple(sorted(vertices)), tuple(sorted(edge_ids))))
    return tuple(rows)


def minimal_cuts(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    cuts: set[frozenset[int]] = set()
    for vertices, edge_ids in core_components(node_count, edges):
        root = vertices[0]
        remainder = vertices[1:]
        for mask in range(1 << len(remainder)):
            side = {
                root,
                *(
                    vertex
                    for index, vertex in enumerate(remainder)
                    if mask & (1 << index)
                ),
            }
            if len(side) == len(vertices):
                continue
            cuts.add(
                frozenset(
                    edge_id
                    for edge_id in edge_ids
                    if (edges[edge_id][0] in side)
                    != (edges[edge_id][1] in side)
                )
            )
    minimal = [
        cut for cut in cuts if not any(other < cut for other in cuts)
    ]
    return tuple(
        sorted(
            (tuple(sorted(cut)) for cut in minimal),
            key=lambda item: (len(item), item),
        )
    )


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
    checks["registration_files"] = all(
        (REPO / relative).is_file()
        and sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )
    checks["result_receipt_hash"] = (
        sha256(result_path) == receipt["result_sha256"]
    )
    checks["protocol_binding"] = (
        sha256(protocol_path) == result["protocol_sha256"]
        == receipt["protocol_sha256"]
    )
    checks["registration_binding"] = (
        sha256(registration_path) == result["registration_sha256"]
        == receipt["registration_sha256"]
    )
    graph_results = {row["name"]: row for row in result["graphs"]}
    bond_checks = []
    certificate_checks = []
    for name, raw in protocol["graphs"].items():
        node_count = int(raw["node_count"])
        edges = tuple(tuple(edge) for edge in raw["edges"])
        expected_bonds = minimal_cuts(node_count, edges)
        reported = tuple(
            tuple(row) for row in graph_results[name]["bonds"]
        )
        bond_checks.append(reported == expected_bonds)
        weights = tuple(
            Fraction(value)
            for value in raw["design_certificate"]["primal_weights"]
        )
        threshold = Fraction(
            raw["design_certificate"]["threshold"]
        )
        primal = min(
            sum(weights[edge] for edge in bond)
            for bond in expected_bonds
        )
        distribution = tuple(
            (
                tuple(row["support"]),
                Fraction(row["mass"]),
            )
            for row in raw["design_certificate"]["dual_distribution"]
        )
        loads = tuple(
            sum(mass for support, mass in distribution if edge in support)
            for edge in range(len(edges))
        )
        certificate_checks.append(
            sum(weights) == 1
            and primal == threshold
            and sum(mass for _, mass in distribution) == 1
            and all(support in expected_bonds for support, _ in distribution)
            and max(loads) == threshold
        )
    checks["independent_bond_reconstruction"] = all(bond_checks)
    checks["independent_certificate_replay"] = all(certificate_checks)
    checks["all_registered_gates_pass"] = (
        set(result["gates"]) == set(protocol["gate_ids"])
        and all(result["gates"].values())
    )
    checks["verdict"] = result["verdict"] == (
        "bond_characterization_established_in_frozen_model"
    )
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol", type=Path, default=HERE / "protocol_v0_18.json"
    )
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_18.json",
    )
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    checks = verify(
        args.protocol.resolve(),
        args.registration.resolve(),
        args.result.resolve(),
        args.receipt.resolve(),
    )
    payload = {
        "checks": checks,
        "check_count": len(checks),
        "passed_count": sum(checks.values()),
        "pass": all(checks.values()),
    }
    if args.output:
        if args.output.exists():
            raise FileExistsError(args.output)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not payload["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
