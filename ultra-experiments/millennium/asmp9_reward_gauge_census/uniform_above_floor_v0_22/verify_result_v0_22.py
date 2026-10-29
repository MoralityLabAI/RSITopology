from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
Edge = tuple[int, int]
MultiEdge = tuple[int, int]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps(value, indent=2, sort_keys=True) + "\n"
        )


def graph_parts(
    raw: dict[str, Any],
) -> tuple[int, tuple[Edge, ...]]:
    return int(raw["node_count"]), tuple(
        tuple(edge) for edge in raw["edges"]
    )


def canonical(edges: Iterable[MultiEdge]) -> tuple[MultiEdge, ...]:
    frozen = [(min(a, b), max(a, b)) for a, b in edges]
    if not frozen:
        return ()
    vertices = sorted({vertex for edge in frozen for vertex in edge})
    relabel = {vertex: index for index, vertex in enumerate(vertices)}
    return tuple(
        sorted((relabel[a], relabel[b]) for a, b in frozen)
    )


def alternative_path(
    edges: Sequence[MultiEdge], excluded: int
) -> bool:
    source, target = edges[excluded]
    if source == target:
        return True
    adjacency: dict[int, list[int]] = {}
    for index, (left, right) in enumerate(edges):
        if index == excluded or left == right:
            continue
        adjacency.setdefault(left, []).append(right)
        adjacency.setdefault(right, []).append(left)
    seen = {source}
    stack = [source]
    while stack:
        node = stack.pop()
        for neighbor in adjacency.get(node, ()):
            if neighbor == target:
                return True
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return False


def delete(
    edges: Sequence[MultiEdge], index: int
) -> tuple[MultiEdge, ...]:
    return canonical(
        edge for edge_index, edge in enumerate(edges) if edge_index != index
    )


def contract(
    edges: Sequence[MultiEdge], index: int
) -> tuple[MultiEdge, ...]:
    source, target = edges[index]
    result = []
    for edge_index, (left, right) in enumerate(edges):
        if edge_index == index:
            continue
        result.append(
            (
                source if left == target else left,
                source if right == target else right,
            )
        )
    return canonical(result)


def tutte_deletion_contraction(
    edges: Sequence[Edge],
    x_value: Fraction,
    y_value: Fraction,
) -> Fraction:
    @lru_cache(maxsize=None)
    def evaluate(state: tuple[MultiEdge, ...]) -> Fraction:
        if not state:
            return Fraction(1)
        for index, (source, target) in enumerate(state):
            if source == target:
                return y_value * evaluate(delete(state, index))
        index = 0
        if not alternative_path(state, index):
            return x_value * evaluate(contract(state, index))
        return evaluate(delete(state, index)) + evaluate(
            contract(state, index)
        )

    return evaluate(canonical(edges))


def strong(
    node_count: int, edges: Sequence[Edge], statuses: Sequence[int]
) -> bool:
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    reverse: list[list[int]] = [[] for _ in range(node_count)]
    for (source, target), status in zip(
        edges, statuses, strict=True
    ):
        arcs = []
        if status in (0, 1):
            arcs.append((source, target))
        if status in (1, 2):
            arcs.append((target, source))
        for left, right in arcs:
            adjacency[left].append(right)
            reverse[right].append(left)

    def visit(graph: Sequence[Sequence[int]]) -> int:
        seen = {0}
        stack = [0]
        while stack:
            node = stack.pop()
            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        return len(seen)

    return visit(adjacency) == node_count and visit(reverse) == node_count


def microtrial(
    node_count: int, edges: Sequence[Edge], trial_count: int
) -> Fraction:
    bit_count = len(edges) * trial_count
    successes = 0
    for bits in itertools.product((0, 1), repeat=bit_count):
        statuses = []
        for edge_index in range(len(edges)):
            values = bits[
                edge_index
                * trial_count : (edge_index + 1)
                * trial_count
            ]
            statuses.append(
                0
                if all(value == 0 for value in values)
                else 2
                if all(value == 1 for value in values)
                else 1
            )
        successes += strong(node_count, edges, statuses)
    return Fraction(successes, 2**bit_count)


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
    checks: dict[str, bool] = {
        "registration_hash": (
            sha256(args.registration) == result["registration_sha256"]
            == receipt["registration_sha256"]
        ),
        "result_hash": sha256(args.result) == receipt["result_sha256"],
        "sealed_hashes": all(
            sha256(REPO / relative) == expected
            for relative, expected in registration["sealed_files"].items()
        ),
    }

    independent: dict[str, Any] = {}
    for graph_name, raw in protocol["primary_graphs"].items():
        node_count, edges = graph_parts(raw)
        graph_results: dict[str, Any] = {}
        genus = len(edges) - node_count + 1
        for trial_count in protocol["registered_trial_counts"]:
            z = Fraction(1, 2**trial_count)
            x_value = (1 - 2 * z) / (1 - z)
            y_value = 1 / z
            tutte = tutte_deletion_contraction(edges, x_value, y_value)
            availability = (
                (1 - z) ** (node_count - 1) * z**genus * tutte
            )
            expected = Fraction(
                result["cells"][graph_name][str(trial_count)][
                    "availability"
                ]
            )
            checks[f"{graph_name}_r{trial_count}"] = (
                availability == expected
            )
            graph_results[str(trial_count)] = {
                "availability": (
                    f"{availability.numerator}/{availability.denominator}"
                ),
                "tutte_value": (
                    f"{tutte.numerator}/{tutte.denominator}"
                ),
            }
        independent[graph_name] = graph_results

    wheel_node_count, wheel_edges = graph_parts(
        protocol["primary_graphs"]["wheel_6"]
    )
    independent_micro = microtrial(wheel_node_count, wheel_edges, 2)
    expected_micro = Fraction(
        result["gates"]["G5_minimal_above_floor_microtrial"][
            "microtrial_availability"
        ]
    )
    checks["independent_microtrial"] = independent_micro == expected_micro
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
        "independent_microtrial": (
            f"{independent_micro.numerator}/{independent_micro.denominator}"
        ),
        "independent_results": independent,
        "pass": all(checks.values()),
        "result_sha256": sha256(args.result),
        "verifier_imports_implementation": False,
        "verifier_imports_runner": False,
    }
    write_json_exclusive(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

