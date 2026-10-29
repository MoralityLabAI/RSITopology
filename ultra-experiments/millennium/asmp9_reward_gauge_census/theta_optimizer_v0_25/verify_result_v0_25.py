from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterator, Sequence

import networkx as nx


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def build_theta(
    path_lengths: Sequence[int],
) -> tuple[int, tuple[tuple[int, int], ...]]:
    edges: list[tuple[int, int]] = []
    next_node = 2
    for length in path_lengths:
        nodes = [0]
        for _ in range(length - 1):
            nodes.append(next_node)
            next_node += 1
        nodes.append(1)
        edges.extend(zip(nodes[:-1], nodes[1:], strict=True))
    return next_node, tuple(edges)


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


def theta_numerator(paths: Sequence[Sequence[int]]) -> int:
    usable = 1
    one_direction = 1
    for path in paths:
        a_value = math.prod(2**count - 1 for count in path)
        b_value = math.prod(2**count - 2 for count in path)
        usable *= 2 * a_value - b_value
        one_direction *= a_value - b_value
    return usable - 2 * one_direction


def positive_compositions(
    total: int, dimension: int
) -> Iterator[tuple[int, ...]]:
    if dimension == 1:
        yield (total,)
        return
    for first in range(1, total - dimension + 2):
        for suffix in positive_compositions(total - first, dimension - 1):
            yield (first,) + suffix


def split_paths(
    flat: Sequence[int], lengths: Sequence[int]
) -> tuple[tuple[int, ...], ...]:
    offset = 0
    result: list[tuple[int, ...]] = []
    for length in lengths:
        result.append(tuple(flat[offset : offset + length]))
        offset += length
    return tuple(result)


def balanced_counts(length: int, total: int) -> tuple[int, ...]:
    quotient, remainder = divmod(total, length)
    return (quotient + 1,) * remainder + (quotient,) * (
        length - remainder
    )


def independent_reduced_optimum(
    lengths: tuple[int, ...], total: int
) -> tuple[int, tuple[tuple[int, ...], ...], int]:
    best: int | None = None
    optimizers: list[tuple[int, ...]] = []
    cell_count = 0
    for totals in positive_compositions(
        total - sum(lengths) + len(lengths), len(lengths)
    ):
        adjusted = tuple(
            value + length - 1
            for value, length in zip(totals, lengths, strict=True)
        )
        cell_count += 1
        value = theta_numerator(
            tuple(
                balanced_counts(length, subtotal)
                for length, subtotal in zip(
                    lengths, adjusted, strict=True
                )
            )
        )
        if best is None or value > best:
            best = value
            optimizers = [adjusted]
        elif value == best:
            optimizers.append(adjusted)
    if best is None:
        raise AssertionError("independent reduction returned no cells")
    return best, tuple(optimizers), cell_count


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
        sha256(args.registration)
        == result["registration_sha256"]
        == receipt["registration_sha256"]
    )
    checks["result_hash"] = sha256(args.result) == receipt["result_sha256"]
    checks["protocol_hash"] = (
        sha256(REPO / registration["protocol_path"])
        == receipt["protocol_sha256"]
    )
    checks["sealed_files"] = all(
        sha256(REPO / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )

    formula_by_name = {row["name"]: row for row in result["formula_rows"]}
    formula_ok = True
    direct_ok = True
    for cell in protocol["fresh_validation"]["formula_cells"]:
        paths = tuple(tuple(path) for path in cell["path_counts"])
        lengths = tuple(cell["path_lengths"])
        flat = tuple(value for path in paths for value in path)
        numerator = theta_numerator(paths)
        denominator = 2 ** sum(flat)
        row = formula_by_name[cell["name"]]
        formula_ok &= record_fraction(row["closed_form"]) == Fraction(
            numerator, denominator
        )
        node_count, edges = build_theta(lengths)
        direct_ok &= direct_numerator(
            node_count, edges, flat
        ) == numerator
    checks["formula_rows"] = formula_ok
    checks["formula_direct_orientation_census"] = direct_ok

    optimizer_by_name = {
        row["name"]: row for row in result["optimizer_rows"]
    }
    optimizer_ok = True
    for cell in protocol["fresh_validation"]["optimizer_cells"]:
        lengths = tuple(cell["path_lengths"])
        total = int(cell["total_budget"])
        expected, totals, composition_count = independent_reduced_optimum(
            lengths, total
        )
        row = optimizer_by_name[cell["name"]]
        optimizer_ok &= row["reduced_maximum_numerator"] == expected
        optimizer_ok &= row["full_maximum_numerator"] == expected
        optimizer_ok &= tuple(
            tuple(values) for values in row["reduced_path_totals"]
        ) == totals
        optimizer_ok &= row["composition_count"] == composition_count
        optimizer_ok &= composition_count == math.comb(
            total - sum(lengths) + len(lengths) - 1,
            len(lengths) - 1,
        )
        optimizer_ok &= row["full_cell_count"] == math.comb(
            total - 1, sum(lengths) - 1
        )
        optimizer_ok &= row["full_optimizers_path_balanced"]
    checks["optimizer_rows"] = optimizer_ok

    checks["gate_universe"] = set(result["gate_passes"]) == set(
        protocol["gate_ids"]
    )
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
