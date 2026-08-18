"""Exact graph-cohomology reward-gauge census for ASMP-9."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import platform
import subprocess
import time
import tracemalloc
from collections import Counter, deque
from io import StringIO
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SEALED_NAMES = (
    "protocol_v0_1.json",
    "run.py",
    "verify_result.py",
    "test_reward_gauge.py",
    "README.md",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to overwrite non-identical artifact: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def git(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=text
    )


def bind_committed_inputs(paths: Sequence[Path]) -> dict[str, Any]:
    commit = git("rev-parse", "HEAD").stdout.strip()
    tracked_diff = git("diff", "--binary", "HEAD", "--", text=False).stdout
    if tracked_diff:
        raise ValueError("tracked diff is nonempty at registered run start")
    bindings: dict[str, Any] = {}
    for path in paths:
        relative = path.resolve().relative_to(REPO_ROOT).as_posix()
        if git("status", "--porcelain", "--", relative).stdout.strip():
            raise ValueError(f"sealed input is dirty or untracked: {relative}")
        working = path.read_bytes()
        committed = git("show", f"HEAD:{relative}", text=False).stdout
        if working != committed:
            raise ValueError(f"sealed input differs from HEAD: {relative}")
        bindings[relative] = {
            "sha256": hashlib.sha256(working).hexdigest(),
            "git_blob": git("rev-parse", f"HEAD:{relative}").stdout.strip(),
        }
    return {
        "commit": commit,
        "tracked_diff_sha256": hashlib.sha256(tracked_diff).hexdigest(),
        "sealed_inputs": bindings,
    }


class UnionFind:
    def __init__(self, count: int) -> None:
        self.parent = list(range(count))
        self.components = count

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, first: int, second: int) -> bool:
        left = self.find(first)
        right = self.find(second)
        if left == right:
            return False
        if left > right:
            left, right = right, left
        self.parent[right] = left
        self.components -= 1
        return True


def edge_universe(vertex_count: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(vertex_count), 2))


def edges_from_mask(vertex_count: int, mask: int) -> tuple[tuple[int, int], ...]:
    universe = edge_universe(vertex_count)
    return tuple(edge for index, edge in enumerate(universe) if mask & (1 << index))


def spanning_forest(
    vertex_count: int, edges: Sequence[tuple[int, int]]
) -> tuple[tuple[tuple[int, int], ...], int]:
    union_find = UnionFind(vertex_count)
    forest = []
    for edge in edges:
        if union_find.union(*edge):
            forest.append(edge)
    return tuple(forest), union_find.components


def incidence_matrix(vertex_count: int, edges: Sequence[tuple[int, int]]) -> np.ndarray:
    matrix = np.zeros((vertex_count, len(edges)), dtype=np.int64)
    for index, (source, target) in enumerate(edges):
        matrix[source, index] = -1
        matrix[target, index] = 1
    return matrix


def tree_path(
    vertex_count: int,
    forest: Sequence[tuple[int, int]],
    start: int,
    target: int,
) -> list[int]:
    adjacency: list[list[int]] = [[] for _ in range(vertex_count)]
    for left, right in forest:
        adjacency[left].append(right)
        adjacency[right].append(left)
    queue = deque([start])
    parent = {start: None}
    while queue:
        current = queue.popleft()
        if current == target:
            break
        for neighbor in adjacency[current]:
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)
    if target not in parent:
        raise ValueError("chord endpoints are not connected in the spanning forest")
    path = []
    current: int | None = target
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


def fundamental_cycle_matrix(
    vertex_count: int,
    edges: Sequence[tuple[int, int]],
    forest: Sequence[tuple[int, int]],
) -> np.ndarray:
    edge_index = {edge: index for index, edge in enumerate(edges)}
    forest_set = set(forest)
    chords = [edge for edge in edges if edge not in forest_set]
    cycles = np.zeros((len(chords), len(edges)), dtype=np.int64)
    for row_index, (source, target) in enumerate(chords):
        cycles[row_index, edge_index[(source, target)]] = 1
        # Close source->target with the unique forest path target->source.
        path = tree_path(vertex_count, forest, target, source)
        for left, right in zip(path, path[1:]):
            canonical = (min(left, right), max(left, right))
            direction = 1 if (left, right) == canonical else -1
            cycles[row_index, edge_index[canonical]] += direction
    return cycles


def analyze_graph(vertex_count: int, edges: Sequence[tuple[int, int]]) -> dict[str, Any]:
    forest, components = spanning_forest(vertex_count, edges)
    incidence = incidence_matrix(vertex_count, edges)
    cycles = fundamental_cycle_matrix(vertex_count, edges, forest)
    edge_count = len(edges)
    beta = edge_count - vertex_count + components
    boundary = incidence @ cycles.T
    annihilation = cycles @ incidence.T
    full_kernel_dimension = edge_count - beta
    shaping_dimension = vertex_count - components
    reduced_kernel_dimension = edge_count - (beta - 1) if beta > 0 else None
    return {
        "vertices": vertex_count,
        "edges": edge_count,
        "components": components,
        "beta_1": beta,
        "forest_edges": len(forest),
        "cycle_rows": int(cycles.shape[0]),
        "boundary_zero": bool(np.all(boundary == 0)),
        "gauge_annihilation_zero": bool(np.all(annihilation == 0)),
        "full_kernel_dimension": full_kernel_dimension,
        "shaping_dimension": shaping_dimension,
        "reduced_kernel_dimension": reduced_kernel_dimension,
    }


def ordinal_counterexample() -> dict[str, Any]:
    vertex_count = 3
    edges = ((0, 1), (0, 2), (1, 2))
    forest, _ = spanning_forest(vertex_count, edges)
    incidence = incidence_matrix(vertex_count, edges)
    cycles = fundamental_cycle_matrix(vertex_count, edges, forest)
    cycle = cycles[0]
    reward_one = cycle.copy()
    reward_two = 2 * cycle
    return_one = int(cycle @ reward_one)
    return_two = int(cycle @ reward_two)
    difference_return = int(cycle @ (reward_two - reward_one))
    same_ordinal = int(np.sign(return_one)) == int(np.sign(return_two))
    non_gauge_equivalent = difference_return != 0
    return {
        "edges": [list(edge) for edge in edges],
        "cycle": cycle.tolist(),
        "reward_one": reward_one.tolist(),
        "reward_two": reward_two.tolist(),
        "exact_returns": [return_one, return_two],
        "ordinal_signs": [int(np.sign(return_one)), int(np.sign(return_two))],
        "difference_cycle_return": difference_return,
        "cycle_boundary": (incidence @ cycle).tolist(),
        "same_ordinal_observation": same_ordinal,
        "non_gauge_equivalent": non_gauge_equivalent,
        "pass": same_ordinal and non_gauge_equivalent and return_one != return_two,
    }


def csv_bytes(records: Iterable[dict[str, Any]], fields: Sequence[str]) -> bytes:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in records:
        writer.writerow(record)
    return buffer.getvalue().encode("utf-8")


def analyze(protocol: dict[str, Any]) -> dict[str, Any]:
    minimum = int(protocol["census"]["minimum_vertices"])
    maximum = int(protocol["census"]["maximum_vertices"])
    per_n = Counter()
    beta_histogram = Counter()
    component_histogram = Counter()
    graph_count = 0
    failures: dict[str, list[dict[str, Any]]] = {
        "cycle_rank": [],
        "boundary": [],
        "annihilation": [],
        "threshold": [],
        "forest": [],
    }
    cyclic_graphs = 0
    acyclic_graphs = 0
    for vertex_count in range(minimum, maximum + 1):
        universe_size = len(edge_universe(vertex_count))
        for mask in range(1 << universe_size):
            edges = edges_from_mask(vertex_count, mask)
            record = analyze_graph(vertex_count, edges)
            graph_count += 1
            per_n[vertex_count] += 1
            beta_histogram[(vertex_count, record["beta_1"])] += 1
            component_histogram[(vertex_count, record["components"])] += 1
            expected_beta = record["edges"] - record["vertices"] + record["components"]
            if record["cycle_rows"] != expected_beta or record["beta_1"] != expected_beta:
                failures["cycle_rank"].append({"n": vertex_count, "mask": mask, **record})
            if not record["boundary_zero"]:
                failures["boundary"].append({"n": vertex_count, "mask": mask, **record})
            if not record["gauge_annihilation_zero"]:
                failures["annihilation"].append({"n": vertex_count, "mask": mask, **record})
            if record["beta_1"] > 0:
                cyclic_graphs += 1
                if not (
                    record["full_kernel_dimension"] == record["shaping_dimension"]
                    and record["reduced_kernel_dimension"] == record["shaping_dimension"] + 1
                ):
                    failures["threshold"].append({"n": vertex_count, "mask": mask, **record})
            else:
                acyclic_graphs += 1
                if not (
                    record["cycle_rows"] == 0
                    and record["full_kernel_dimension"] == record["shaping_dimension"]
                ):
                    failures["forest"].append({"n": vertex_count, "mask": mask, **record})

    expected_total = int(protocol["census"]["expected_graph_count"])
    ordinal = ordinal_counterexample()
    expected_per_n = {
        vertex_count: 1 << len(edge_universe(vertex_count))
        for vertex_count in range(minimum, maximum + 1)
    }
    gates = {
        "G1_complete_graph_census": {
            "pass": graph_count == expected_total and dict(per_n) == expected_per_n,
            "observed": graph_count,
            "expected": expected_total,
            "per_n": {str(key): value for key, value in sorted(per_n.items())},
        },
        "G2_cycle_rank_identity": {
            "pass": not failures["cycle_rank"] and not failures["boundary"],
            "cycle_rank_failures": len(failures["cycle_rank"]),
            "boundary_failures": len(failures["boundary"]),
        },
        "G3_gauge_annihilation": {
            "pass": not failures["annihilation"],
            "failures": len(failures["annihilation"]),
        },
        "G4_exact_access_threshold": {
            "pass": cyclic_graphs > 0 and not failures["threshold"],
            "cyclic_graphs": cyclic_graphs,
            "failures": len(failures["threshold"]),
        },
        "G5_tree_and_forest_negative_control": {
            "pass": acyclic_graphs > 0 and not failures["forest"],
            "acyclic_graphs": acyclic_graphs,
            "failures": len(failures["forest"]),
        },
        "G6_ordinal_access_counterexample": {
            "pass": bool(ordinal["pass"]),
            "exact_returns": ordinal["exact_returns"],
            "ordinal_signs": ordinal["ordinal_signs"],
            "difference_cycle_return": ordinal["difference_cycle_return"],
        },
    }
    verdict = "exact_finite_reward_gauge_access_threshold_seed_established" if all(
        record["pass"] for record in gates.values()
    ) else "registered_seed_failed"
    histogram_rows = [
        {"vertices": vertex_count, "beta_1": beta, "graph_count": count}
        for (vertex_count, beta), count in sorted(beta_histogram.items())
    ]
    component_rows = [
        {"vertices": vertex_count, "components": components, "graph_count": count}
        for (vertex_count, components), count in sorted(component_histogram.items())
    ]
    return {
        "verdict": verdict,
        "gates": gates,
        "census": {
            "graph_count": graph_count,
            "cyclic_graphs": cyclic_graphs,
            "acyclic_graphs": acyclic_graphs,
            "beta_histogram": histogram_rows,
            "component_histogram": component_rows,
        },
        "ordinal_counterexample": ordinal,
        "failure_examples": {key: value[:3] for key, value in failures.items()},
        "claim_boundary": protocol["claim_boundary"],
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# ASMP-9 reward-gauge graph census — Result",
        "",
        f"**Verdict:** `{result['verdict']}`",
        "",
        "## Gates",
        "",
    ]
    for name, record in result["gates"].items():
        lines.append(f"- **{name}:** {'PASS' if record['pass'] else 'FAIL'}")
    counterexample = result["ordinal_counterexample"]
    lines.extend(
        [
            "",
            "## Exact census",
            "",
            f"All {result['census']['graph_count']:,} labelled simple graphs on two through six vertices were checked.",
            f"The census contained {result['census']['cyclic_graphs']:,} graphs with loop access and {result['census']['acyclic_graphs']:,} forests with beta_1=0.",
            "",
            "For exact real-valued loop returns, the fundamental-cycle query count equals `beta_1 = m-n+c`. The full query kernel has dimension `n-c`, exactly the potential-shaping subspace; removing one independent loop query leaves one additional unidentified quotient direction.",
            "",
            "## Access-model counterexample",
            "",
            f"On the triangle, rewards `{counterexample['reward_one']}` and `{counterexample['reward_two']}` have exact loop returns {counterexample['exact_returns']} but identical ordinal signs {counterexample['ordinal_signs']}. Their difference has nonzero loop return {counterexample['difference_cycle_return']}, so it is not a potential-shaping coboundary.",
            "",
            "Therefore the exact-query threshold may not be transferred to ordinal preferences without an additional theorem.",
            "",
            "## Claim boundary",
            "",
            result["claim_boundary"]["established_on_pass"],
            "",
            "Not established:",
            "",
        ]
    )
    lines.extend(f"- {claim}" for claim in result["claim_boundary"]["not_established"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=HERE / "protocol_v0_1.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.resolve().read_text(encoding="utf-8"))
    output_dir = args.output_dir.resolve()

    tracemalloc.start()
    start = time.perf_counter()
    binding = bind_committed_inputs([HERE / name for name in SEALED_NAMES])
    result = analyze(protocol)
    elapsed = time.perf_counter() - start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    result["gates"] = {"G0_registration_binding": {"pass": True, **binding}, **result["gates"]}
    result["resources"] = {
        "wall_seconds": elapsed,
        "python_peak_bytes": peak_bytes,
        "wall_ceiling": protocol["resource_ceiling"]["wall_seconds"],
        "memory_ceiling": protocol["resource_ceiling"]["python_peak_bytes"],
    }
    if elapsed > float(protocol["resource_ceiling"]["wall_seconds"]) or peak_bytes > int(protocol["resource_ceiling"]["python_peak_bytes"]):
        result["verdict"] = "invalid_resource_cap"

    result_path = output_dir / "result_v0_1.json"
    beta_path = output_dir / "beta_histogram_v0_1.csv"
    component_path = output_dir / "component_histogram_v0_1.csv"
    report_path = output_dir / "RESULT_v0_1.md"
    write_once(result_path, canonical_json(result).encode("utf-8"))
    write_once(
        beta_path,
        csv_bytes(result["census"]["beta_histogram"], ("vertices", "beta_1", "graph_count")),
    )
    write_once(
        component_path,
        csv_bytes(result["census"]["component_histogram"], ("vertices", "components", "graph_count")),
    )
    write_once(report_path, render_report(result).encode("utf-8"))
    receipt = {
        "schema_version": "asmp9_reward_gauge_census_receipt_v0_1",
        "protocol_id": protocol["protocol_id"],
        "verdict": result["verdict"],
        "binding": binding,
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform()},
        "resources": result["resources"],
        "outputs": {
            path.name: {"sha256": sha256_file(path), "bytes": path.stat().st_size}
            for path in (result_path, beta_path, component_path, report_path)
        },
    }
    write_once(output_dir / "receipt_v0_1.json", canonical_json(receipt).encode("utf-8"))
    print(canonical_json({"verdict": result["verdict"], "gates": result["gates"], "resources": result["resources"]}))
    return 0 if not result["verdict"].startswith("invalid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
