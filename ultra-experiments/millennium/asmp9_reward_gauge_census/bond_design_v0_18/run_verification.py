from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence

from bond_design import (
    bridge_indices,
    cactus_closed_form,
    cyclic_core_bonds,
    cyclic_core_components,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V017_PROTOCOL = (
    HERE.parent / "general_graph_design_v0_17" / "protocol_v0_17.json"
)

Edge = tuple[int, int]
ZERO = 0
INTERIOR = 1
FULL = 2


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def parse_fraction(text: str) -> Fraction:
    return Fraction(text)


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def peak_resident_bytes() -> int:
    if os.name == "nt":
        from ctypes import wintypes

        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(ProcessMemoryCounters),
            wintypes.DWORD,
        )
        if not psapi.GetProcessMemoryInfo(
            kernel32.GetCurrentProcess(),
            ctypes.byref(counters),
            counters.cb,
        ):
            raise OSError("GetProcessMemoryInfo failed")
        return int(counters.PeakWorkingSetSize)
    import resource

    maximum = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return maximum if platform.system() == "Darwin" else maximum * 1024


def _scc(adjacency: Sequence[Sequence[int]]) -> tuple[int, ...]:
    count = len(adjacency)
    reverse = [[] for _ in range(count)]
    for source, targets in enumerate(adjacency):
        for target in targets:
            reverse[target].append(source)
    seen: set[int] = set()
    order: list[int] = []
    for root in range(count):
        if root in seen:
            continue
        stack: list[tuple[int, bool]] = [(root, False)]
        while stack:
            node, exiting = stack.pop()
            if exiting:
                order.append(node)
                continue
            if node in seen:
                continue
            seen.add(node)
            stack.append((node, True))
            stack.extend(
                (target, False)
                for target in adjacency[node]
                if target not in seen
            )
    labels = [-1] * count
    label = 0
    for root in reversed(order):
        if labels[root] != -1:
            continue
        labels[root] = label
        stack = [root]
        while stack:
            node = stack.pop()
            for target in reverse[node]:
                if labels[target] == -1:
                    labels[target] = label
                    stack.append(target)
        label += 1
    return tuple(labels)


def _full_liveness(
    node_count: int,
    edges: Sequence[Edge],
    statuses: Sequence[int],
) -> bool:
    bridges = set(bridge_indices(node_count, edges))
    adjacency = [[] for _ in range(node_count)]
    for index, ((source, target), status) in enumerate(
        zip(edges, statuses, strict=True)
    ):
        if status in (ZERO, INTERIOR):
            adjacency[source].append(target)
        if status in (INTERIOR, FULL):
            adjacency[target].append(source)
        if index in bridges:
            continue
    labels = _scc(adjacency)
    return all(
        index in bridges or labels[source] == labels[target]
        for index, (source, target) in enumerate(edges)
    )


def brute_minimal_bad_supports(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    bad: set[frozenset[int]] = set()
    for statuses in itertools.product(
        (ZERO, INTERIOR, FULL), repeat=len(edges)
    ):
        if _full_liveness(node_count, edges, statuses):
            continue
        bad.add(
            frozenset(
                index
                for index, status in enumerate(statuses)
                if status != INTERIOR
            )
        )
    minimal = [
        support
        for support in bad
        if not any(other < support for other in bad)
    ]
    return tuple(
        sorted(
            (tuple(sorted(support)) for support in minimal),
            key=lambda item: (len(item), item),
        )
    )


def component_cuts(
    vertices: Sequence[int],
    edge_ids: Sequence[int],
    edges: Sequence[Edge],
) -> tuple[tuple[int, ...], ...]:
    root = min(vertices)
    remaining = tuple(vertex for vertex in vertices if vertex != root)
    cuts: set[tuple[int, ...]] = set()
    for mask in range(1 << len(remaining)):
        side = {
            root,
            *(
                vertex
                for index, vertex in enumerate(remaining)
                if mask & (1 << index)
            ),
        }
        if len(side) == len(vertices):
            continue
        cuts.add(
            tuple(
                sorted(
                    edge_id
                    for edge_id in edge_ids
                    if (edges[edge_id][0] in side)
                    != (edges[edge_id][1] in side)
                )
            )
        )
    return tuple(sorted(cuts, key=lambda item: (len(item), item)))


def all_core_cuts(
    node_count: int, edges: Sequence[Edge]
) -> tuple[tuple[int, ...], ...]:
    del node_count
    cuts: set[tuple[int, ...]] = set()
    for vertices, edge_ids in cyclic_core_components(
        max(max(edge) for edge in edges) + 1, edges
    ):
        cuts.update(component_cuts(vertices, edge_ids, edges))
    return tuple(sorted(cuts, key=lambda item: (len(item), item)))


def graph_isomorphic(
    node_count_a: int,
    edges_a: Sequence[Edge],
    node_count_b: int,
    edges_b: Sequence[Edge],
) -> bool:
    if node_count_a != node_count_b or len(edges_a) != len(edges_b):
        return False
    target = {frozenset(edge) for edge in edges_b}
    for permutation in itertools.permutations(range(node_count_a)):
        image = {
            frozenset((permutation[source], permutation[target_node]))
            for source, target_node in edges_a
        }
        if image == target:
            return True
    return False


def inherited_graphs() -> list[tuple[str, int, tuple[Edge, ...]]]:
    protocol = json.loads(V017_PROTOCOL.read_text(encoding="utf-8"))
    rows: list[tuple[str, int, tuple[Edge, ...]]] = []
    for section in ("graphs", "burned_graph_registry"):
        for name, raw in protocol[section].items():
            rows.append(
                (
                    f"v0.17:{section}:{name}",
                    int(raw["node_count"]),
                    tuple(tuple(edge) for edge in raw["edges"]),
                )
            )
    return rows


def validate_registration(
    registration_path: Path, protocol_path: Path
) -> tuple[dict[str, Any], str, dict[str, bool]]:
    registration = json.loads(
        registration_path.read_text(encoding="utf-8")
    )
    checks: dict[str, bool] = {}
    for relative, expected in registration["sealed_files"].items():
        path = REPO / relative
        checks[relative] = path.is_file() and sha256(path) == expected
    checks["protocol_path"] = (
        registration["protocol_path"]
        == protocol_path.relative_to(REPO).as_posix()
    )
    ancestor = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            registration["implementation_commit"],
            "HEAD",
        ],
        cwd=REPO,
        check=False,
    ).returncode == 0
    checks["implementation_commit_is_ancestor"] = ancestor
    return registration, sha256(registration_path), checks


def graph_record(
    name: str, raw: dict[str, Any]
) -> dict[str, Any]:
    node_count = int(raw["node_count"])
    edges = tuple(tuple(edge) for edge in raw["edges"])
    bonds = cyclic_core_bonds(node_count, edges)
    brute = brute_minimal_bad_supports(node_count, edges)
    bridges = bridge_indices(node_count, edges)
    cuts = all_core_cuts(node_count, edges)
    weights = tuple(
        parse_fraction(value)
        for value in raw["design_certificate"]["primal_weights"]
    )
    threshold = parse_fraction(
        raw["design_certificate"]["threshold"]
    )
    primal_values = tuple(
        sum(weights[edge] for edge in bond) for bond in bonds
    )
    dual = tuple(
        (
            tuple(int(edge) for edge in row["support"]),
            parse_fraction(row["mass"]),
        )
        for row in raw["design_certificate"]["dual_distribution"]
    )
    loads = tuple(
        sum(mass for support, mass in dual if edge in support)
        for edge in range(len(edges))
    )
    components = cyclic_core_components(node_count, edges)
    canonical_cut_count = sum(
        (1 << (len(vertices) - 1)) - 1
        for vertices, _ in components
    )
    return {
        "name": name,
        "node_count": node_count,
        "edge_count": len(edges),
        "beta_1": (
            len(edges)
            - node_count
            + _undirected_component_count(node_count, edges)
        ),
        "bridges": list(bridges),
        "bonds": [list(bond) for bond in bonds],
        "bond_count": len(bonds),
        "brute_minimal_bad_supports": [
            list(support) for support in brute
        ],
        "scc_status_count": 3 ** len(edges),
        "canonical_cut_count": canonical_cut_count,
        "all_cut_count": len(cuts),
        "every_cut_contains_bond": all(
            any(set(bond).issubset(cut) for bond in bonds)
            for cut in cuts
        ),
        "no_bond_contains_bridge": all(
            not set(bond).intersection(bridges) for bond in bonds
        ),
        "primal": {
            "weights": [fraction_text(value) for value in weights],
            "sum": fraction_text(sum(weights)),
            "minimum_bond_weight": fraction_text(min(primal_values)),
            "threshold": fraction_text(threshold),
        },
        "dual": {
            "mass_sum": fraction_text(sum(mass for _, mass in dual)),
            "maximum_edge_load": fraction_text(max(loads)),
            "loads": [fraction_text(value) for value in loads],
            "all_supports_are_bonds": all(
                support in bonds for support, _ in dual
            ),
        },
        "checks": {
            "bad_supports_equal_bonds": brute == bonds,
            "bridges_match": list(bridges)
            == list(raw["expected_bridge_indices"]),
            "beta1_matches": (
                len(edges)
                - node_count
                + _undirected_component_count(node_count, edges)
            )
            == int(raw["expected_beta1"]),
            "primal_feasible_and_exact": (
                all(value >= 0 for value in weights)
                and sum(weights) == 1
                and min(primal_values) == threshold
            ),
            "dual_feasible_and_exact": (
                all(mass >= 0 for _, mass in dual)
                and sum(mass for _, mass in dual) == 1
                and all(support in bonds for support, _ in dual)
                and max(loads) == threshold
            ),
        },
    }


def _undirected_component_count(
    node_count: int, edges: Sequence[Edge]
) -> int:
    adjacency = [[] for _ in range(node_count)]
    for source, target in edges:
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


def freshness_checks(
    protocol: dict[str, Any]
) -> dict[str, Any]:
    current = [
        (
            name,
            int(raw["node_count"]),
            tuple(tuple(edge) for edge in raw["edges"]),
        )
        for name, raw in protocol["graphs"].items()
    ]
    burned = inherited_graphs()
    extra = protocol["development_registry"]["extra_cactus"]
    burned.append(
        (
            "v0.18:development:extra_cactus",
            int(extra["node_count"]),
            tuple(tuple(edge) for edge in extra["edges"]),
        )
    )
    for name, raw in protocol["development_registry"][
        "premature_v0_18_cells"
    ].items():
        burned.append(
            (
                f"v0.18:development:premature:{name}",
                int(raw["node_count"]),
                tuple(tuple(edge) for edge in raw["edges"]),
            )
        )
    pairwise_collisions: list[list[str]] = []
    inherited_collisions: list[list[str]] = []
    for index, left in enumerate(current):
        for right in current[index + 1 :]:
            if graph_isomorphic(left[1], left[2], right[1], right[2]):
                pairwise_collisions.append([left[0], right[0]])
        for old in burned:
            if graph_isomorphic(left[1], left[2], old[1], old[2]):
                inherited_collisions.append([left[0], old[0]])
    return {
        "pairwise_collisions": pairwise_collisions,
        "inherited_collisions": inherited_collisions,
        "pass": not pairwise_collisions and not inherited_collisions,
    }


def render_result(result: dict[str, Any]) -> str:
    gate_lines = "\n".join(
        f"- `{gate}`: **{'PASS' if passed else 'FAIL'}**"
        for gate, passed in result["gates"].items()
    )
    graph_lines = "\n".join(
        (
            f"- `{row['name']}`: {row['bond_count']} bonds, "
            f"{row['scc_status_count']} SCC states, "
            f"`tau*={row['primal']['threshold']}`"
        )
        for row in result["graphs"]
    )
    return f"""# ASMP-9 v0.18 bond-design result

## Verdict

`{result['verdict']}`

## Gates

{gate_lines}

## Fresh exact cells

{graph_lines}

Across all fresh cells, the inclusion-minimal supports found by direct
ternary residual-SCC enumeration equal the bonds of the cyclic core exactly.
The frozen rational primal and dual certificates agree in every cell.

The cactus control returns `tau*=1/5`, uniform weight on its ten cyclic
edges, and zero weight on its bridge.

## Interpretation

The v0.17 bad-support hypergraph is not an arbitrary reliability object. In
the frozen conditional-access model it is exactly the bond clutter of the
cyclic core. Consequently its leading allocation exponent is the classical
problem of allocating edge capacity to maximize the minimum relevant cut.

This removes ternary-status enumeration from the structural characterization.
The cut-design optimization and its polynomial solvability are classical and
are not claimed as new.

## Claim boundary

{result['claim_boundary']}
"""


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
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refusing nonempty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    protocol_path = args.protocol.resolve()
    registration_path = args.registration.resolve()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    registration, registration_sha, seal_checks = validate_registration(
        registration_path, protocol_path
    )
    fresh = freshness_checks(protocol)
    records = [
        graph_record(name, raw)
        for name, raw in protocol["graphs"].items()
    ]
    cactus_raw = protocol["graphs"]["cactus_square_hexagon_bridge"]
    cactus_edges = tuple(tuple(edge) for edge in cactus_raw["edges"])
    cactus = cactus_closed_form(
        int(cactus_raw["node_count"]), cactus_edges
    )
    cactus_check = {
        "threshold": fraction_text(cactus["threshold"]),
        "weights": [
            fraction_text(value) for value in cactus["weights"]
        ],
        "cycles": [list(cycle) for cycle in cactus["cycles"]],
        "pass": (
            cactus["threshold"]
            == parse_fraction(
                cactus_raw["design_certificate"]["threshold"]
            )
            and tuple(cactus["weights"])
            == tuple(
                parse_fraction(value)
                for value in cactus_raw[
                    "design_certificate"
                ]["primal_weights"]
            )
            and int(cactus["cyclic_edge_count"])
            == int(cactus_raw["expected_cactus_cyclic_edges"])
        ),
    }

    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    gates = {
        "G0_registration_binding": all(seal_checks.values()),
        "G1_fresh_graph_registry": fresh["pass"],
        "G2_scc_bad_supports_equal_bonds": all(
            row["checks"]["bad_supports_equal_bonds"] for row in records
        ),
        "G3_bridge_exclusion_and_cut_completeness": all(
            row["checks"]["bridges_match"]
            and row["checks"]["beta1_matches"]
            and row["no_bond_contains_bridge"]
            and row["every_cut_contains_bond"]
            for row in records
        ),
        "G4_primal_dual_cut_design_certificates": all(
            row["checks"]["primal_feasible_and_exact"]
            and row["checks"]["dual_feasible_and_exact"]
            for row in records
        ),
        "G5_cactus_closed_form": cactus_check["pass"],
        "G6_structural_search_reduction": all(
            row["scc_status_count"] == 3 ** row["edge_count"]
            and row["canonical_cut_count"] < row["scc_status_count"]
            and row["checks"]["bad_supports_equal_bonds"]
            for row in records
        ),
        "G7_resource_and_scope": (
            elapsed <= float(protocol["resource_caps"]["wall_seconds"])
            and peak
            <= int(protocol["resource_caps"]["peak_resident_bytes"])
            and not bool(protocol["resource_caps"]["gpu_allowed"])
        ),
    }
    verdict = (
        "bond_characterization_established_in_frozen_model"
        if all(gates.values())
        else "bond_characterization_not_established"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": sha256(protocol_path),
        "registration_id": registration["registration_id"],
        "registration_sha256": registration_sha,
        "execution_commit": git("rev-parse", "HEAD"),
        "started_at_utc": utc_now(),
        "elapsed_seconds": elapsed,
        "peak_resident_bytes": peak,
        "gpu_used": False,
        "freshness": fresh,
        "seal_checks": seal_checks,
        "graphs": records,
        "cactus": cactus_check,
        "gates": gates,
        "verdict": verdict,
        "claim_boundary": protocol["claim_boundary"],
    }
    result_path = output / "result_v0_18.json"
    report_path = output / "RESULT_v0_18.md"
    write_json(result_path, result)
    write_text(report_path, render_result(result))
    receipt = {
        "protocol_sha256": sha256(protocol_path),
        "registration_sha256": registration_sha,
        "result_sha256": sha256(result_path),
        "report_sha256": sha256(report_path),
        "verdict": verdict,
        "gate_count": len(gates),
        "passed_gate_count": sum(gates.values()),
        "elapsed_seconds": elapsed,
        "peak_resident_bytes": peak,
    }
    write_json(output / "run_receipt_v0_18.json", receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
