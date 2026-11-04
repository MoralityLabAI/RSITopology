from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import networkx as nx


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V022 = HERE.parent / "uniform_above_floor_v0_22"
V020 = HERE.parent / "block_factorization_v0_20"
sys.path.insert(0, str(V022))
sys.path.insert(0, str(V020))

from block_factorization import availability as ternary_availability  # noqa: E402
from uniform_above_floor import (  # noqa: E402
    backman_parameters,
    backman_tutte_availability,
    microtrial_availability,
    tutte_subset_evaluation,
    weighted_availability_exhaustive,
)


EXPECTED_ALLOWED = [
    "For every fixed r>=2, exact evaluation of the declared uniform "
    "allocation on finite simple biconnected blocks is #P-hard under "
    "polynomial-time Turing reductions, by Tutte block "
    "multiplicativity and explicit bridge factors.",
    "For fixed r, the common-denominator microtrial numerator is "
    "#P-complete under polynomial-time Turing reductions.",
    "The r=2 minimal uniform above-floor cell evaluates T_G(2/3,4) "
    "times a known nonzero rational prefactor.",
]
EXPECTED_FORBIDDEN = [
    "Maximin allocation is #P-hard.",
    "Uniform allocation is optimal on arbitrary biconnected blocks.",
    "Nonuniform counts or arbitrary endpoint probabilities are classified.",
    "The Backman formula or the Tutte hard curve is new.",
]


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


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


def write_json_exclusive(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def graph_parts(
    raw: dict[str, Any],
) -> tuple[int, tuple[tuple[int, int], ...]]:
    return int(raw["node_count"]), tuple(
        tuple(edge) for edge in raw["edges"]
    )


def nx_graph(
    node_count: int, edges: tuple[tuple[int, int], ...]
) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(node_count))
    graph.add_edges_from(edges)
    return graph


def prior_graphs(registry: dict[str, Any]) -> Iterable[nx.Graph]:
    for record in registry["records"]:
        yield nx_graph(
            int(record["node_count"]),
            tuple(tuple(edge) for edge in record["edges"]),
        )


def validate_registration(
    path: Path,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    registration = json.loads(path.read_text(encoding="utf-8"))
    for relative, expected in registration["sealed_files"].items():
        sealed = REPO / relative
        if not sealed.is_file() or sha256(sealed) != expected:
            raise RuntimeError(f"sealed hash mismatch: {relative}")
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(
            encoding="utf-8"
        )
    )
    return registration, protocol, sha256(path)


def predecessor_check(protocol: dict[str, Any]) -> dict[str, Any]:
    record = protocol["predecessor_record"]
    hashes: dict[str, bool] = {}
    for kind in (
        "registration",
        "result",
        "run_receipt",
        "independent_verification",
    ):
        path = (HERE / record[f"{kind}_path"]).resolve()
        hashes[kind] = (
            path.is_file() and sha256(path) == record[f"{kind}_sha256"]
        )
    predecessor = json.loads(
        (HERE / record["result_path"]).resolve().read_text(encoding="utf-8")
    )
    return {
        "expected_gate_map_matches": (
            predecessor["gate_passes"]
            == record["expected_gate_passes"]
        ),
        "expected_verdict_matches": (
            predecessor["verdict"] == record["expected_verdict"]
        ),
        "hashes": hashes,
        "pass": (
            all(hashes.values())
            and predecessor["gate_passes"]
            == record["expected_gate_passes"]
            and predecessor["verdict"] == record["expected_verdict"]
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)

    started = time.perf_counter()
    registration, protocol, registration_sha = validate_registration(
        args.registration.resolve()
    )
    predecessor = predecessor_check(protocol)
    gates: dict[str, dict[str, Any]] = {}
    gates["G0_registration_and_predecessor_binding"] = {
        "pass": predecessor["pass"],
        "predecessor": predecessor,
        "registration_sha256": registration_sha,
        "sealed_file_count": len(registration["sealed_files"]),
    }

    registry = json.loads(
        (HERE / protocol["freshness_rule"]["burned_registry_path"])
        .read_text(encoding="utf-8")
    )
    old_graphs = list(prior_graphs(registry))
    primary = {
        name: graph_parts(raw)
        for name, raw in protocol["primary_graphs"].items()
    }
    freshness: dict[str, Any] = {}
    for name, (node_count, edges) in primary.items():
        graph = nx_graph(node_count, edges)
        matches = sum(
            old.number_of_nodes() == node_count
            and old.number_of_edges() == len(edges)
            and nx.is_isomorphic(graph, old)
            for old in old_graphs
        )
        freshness[name] = {
            "biconnected": nx.is_biconnected(graph),
            "bridges": len(list(nx.bridges(graph))),
            "edge_count": len(edges),
            "in_v0_20_burned_atlas_envelope": (
                node_count <= 6 and len(edges) <= 9
            ),
            "node_count": node_count,
            "prior_isomorphic_matches": matches,
        }
    names = sorted(primary)
    collisions = sum(
        left_n == right_n
        and len(left_e) == len(right_e)
        and nx.is_isomorphic(
            nx_graph(left_n, left_e), nx_graph(right_n, right_e)
        )
        for left_index, left in enumerate(names)
        for right in names[left_index + 1 :]
        for left_n, left_e in (primary[left],)
        for right_n, right_e in (primary[right],)
    )
    gates["G1_freshness_and_structure"] = {
        "freshness": freshness,
        "pairwise_isomorphism_collisions": collisions,
        "pass": (
            collisions == 0
            and all(
                row["prior_isomorphic_matches"] == 0
                and not row["in_v0_20_burned_atlas_envelope"]
                and row["biconnected"]
                and row["bridges"] == 0
                for row in freshness.values()
            )
        ),
        "prior_graph_record_count": registry["graph_record_count"],
    }

    state_laws: dict[str, Any] = {}
    law_pass = True
    for trial_count in protocol["registered_trial_counts"]:
        z, x_value, y_value = backman_parameters(trial_count)
        law = (z, 1 - 2 * z, z)
        state_laws[str(trial_count)] = {
            "full": fraction_text(law[2]),
            "interior": fraction_text(law[1]),
            "sum": fraction_text(sum(law, Fraction(0))),
            "x": fraction_text(x_value),
            "y": fraction_text(y_value),
            "zero": fraction_text(law[0]),
        }
        law_pass &= (
            sum(law, Fraction(0)) == 1
            and all(value >= 0 for value in law)
        )
    gates["G2_state_law_and_semantics"] = {
        "interior_semantics": (
            "bidirected edge; equivalent to Backman-unoriented for "
            "the no-directed-cut liveness predicate"
        ),
        "pass": law_pass,
        "state_laws": state_laws,
    }

    cells: dict[str, Any] = {}
    identity_pass = True
    curve_pass = True
    numerator_pass = True
    for graph_name, (node_count, edges) in primary.items():
        graph_cells: dict[str, Any] = {}
        for trial_count in protocol["registered_trial_counts"]:
            z, x_value, y_value = backman_parameters(trial_count)
            direct = weighted_availability_exhaustive(
                node_count, edges, trial_count
            )
            formula = backman_tutte_availability(
                node_count, edges, trial_count
            )
            tutte_value = tutte_subset_evaluation(
                node_count, edges, x_value, y_value
            )
            denominator = 2 ** (trial_count * len(edges))
            scaled_numerator = direct * denominator
            graph_cells[str(trial_count)] = {
                "availability": fraction_text(direct),
                "common_denominator": denominator,
                "microtrial_numerator": scaled_numerator.numerator,
                "point": [
                    fraction_text(x_value),
                    fraction_text(y_value),
                ],
                "prefactor_formula": fraction_text(formula),
                "trial_count": trial_count,
                "tutte_value": fraction_text(tutte_value),
                "z": fraction_text(z),
            }
            identity_pass &= direct == formula
            curve_pass &= (
                (x_value - 1) * (y_value - 1) == -1
                and 0 < x_value < 1 < y_value
            )
            numerator_pass &= (
                scaled_numerator.denominator == 1
                and 0 <= scaled_numerator <= denominator
            )
        cells[graph_name] = graph_cells

    gates["G3_weighted_tutte_identity"] = {
        "cell_count": sum(len(rows) for rows in cells.values()),
        "pass": identity_pass,
    }
    two_point = backman_parameters(2)[1:]
    gates["G4_hard_curve_and_fixed_points"] = {
        "all_points_on_h_minus_one": curve_pass,
        "nonexception_rule": (
            "all registered points have 0<x<1<y and therefore avoid "
            "the JVW special points and easy H_1 curve"
        ),
        "pass": (
            curve_pass
            and two_point == (Fraction(2, 3), Fraction(4))
        ),
        "r2_point": [
            fraction_text(two_point[0]),
            fraction_text(two_point[1]),
        ],
    }

    micro_name = "complete_5"
    micro_n, micro_edges = primary[micro_name]
    micro = microtrial_availability(micro_n, micro_edges, 2)
    direct_micro_cell = Fraction(cells[micro_name]["2"]["availability"])
    gates["G5_minimal_above_floor_microtrial"] = {
        "enumerated_trial_matrices": 2 ** (2 * len(micro_edges)),
        "graph": micro_name,
        "microtrial_availability": fraction_text(micro),
        "pass": micro == direct_micro_cell,
        "status_census_availability": fraction_text(direct_micro_cell),
    }

    labels = {
        "all_zero": (0,) * len(micro_edges),
        "all_one": (1,) * len(micro_edges),
        "alternating": tuple(
            index % 2 for index in range(len(micro_edges))
        ),
    }
    epsilon = Fraction(1, 2)
    counts = (2,) * len(micro_edges)
    label_values: dict[str, str] = {}
    for label_name, pattern in labels.items():
        probabilities = tuple(
            epsilon if label == 0 else 1 - epsilon for label in pattern
        )
        label_values[label_name] = fraction_text(
            ternary_availability(
                micro_n,
                micro_edges,
                counts,
                probabilities,
                blockwise=False,
            )
        )
    gates["G6_endpoint_label_invariance"] = {
        "label_values": label_values,
        "pass": (
            len(set(label_values.values())) == 1
            and Fraction(next(iter(label_values.values())))
            == direct_micro_cell
        ),
    }
    gates["G7_exact_numerator_ledger"] = {
        "cell_count": sum(len(rows) for rows in cells.values()),
        "pass": numerator_pass,
        "witness_encoding": (
            "r|E| fair binary trial bits; residual liveness checked "
            "by directed reachability"
        ),
    }

    statement = protocol["complexity_statement"]
    gates["G8_structured_complexity_attribution"] = {
        "allowed_exact_match": statement["allowed"] == EXPECTED_ALLOWED,
        "forbidden_exact_match": (
            statement["forbidden"] == EXPECTED_FORBIDDEN
        ),
        "pass": (
            statement["allowed"] == EXPECTED_ALLOWED
            and statement["forbidden"] == EXPECTED_FORBIDDEN
        ),
        "proof_source": (
            "Backman weighted partial orientations plus "
            "Jaeger-Vertigan-Welsh and Tutte block multiplicativity; "
            "the finite run is not the proof"
        ),
    }

    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    caps = protocol["resource_caps"]
    environment_lock = json.loads(
        (HERE / protocol["environment_lock_path"]).read_text(
            encoding="utf-8"
        )
    )
    runtime_environment = {
        "implementation": platform.python_implementation(),
        "networkx": nx.__version__,
        "platform": platform.platform(),
        "python": platform.python_version(),
    }
    environment_matches = runtime_environment == environment_lock
    gates["G9_resource_and_scope"] = {
        "claim_boundary": protocol["claim_boundary"],
        "environment_lock": environment_lock,
        "environment_matches": environment_matches,
        "gpu_used": False,
        "pass": (
            elapsed <= caps["wall_seconds"]
            and peak <= caps["peak_resident_bytes"]
            and not caps["gpu_allowed"]
            and environment_matches
        ),
        "peak_resident_bytes": peak,
        "runtime_environment": runtime_environment,
        "wall_seconds": elapsed,
    }

    gate_passes = {
        gate: bool(gates[gate]["pass"]) for gate in protocol["gate_ids"]
    }
    if (
        not gate_passes["G0_registration_and_predecessor_binding"]
        or not gate_passes["G9_resource_and_scope"]
    ):
        verdict = protocol["verdict_map"][
            "binding_or_resource_gate_fails"
        ]
    elif not all(gate_passes.values()):
        verdict = protocol["verdict_map"][
            "any_substantive_gate_fails"
        ]
    else:
        verdict = protocol["verdict_map"]["all_gates_pass"]

    result = {
        "cells": cells,
        "claim_boundary": protocol["claim_boundary"],
        "gate_passes": gate_passes,
        "gates": gates,
        "protocol_id": protocol["protocol_id"],
        "registration_sha256": registration_sha,
        "verdict": verdict,
    }
    result_path = output / "result_v0_22_1.json"
    write_json_exclusive(result_path, result)
    receipt = {
        "command": (
            "python run_verification_v0_22_1.py --registration "
            "registration_v0_22_1.json --output-dir artifacts_v0_22_1"
        ),
        "completed_at_utc": utc_now(),
        "git_commit": git("rev-parse", "HEAD"),
        "gpu_used": False,
        "peak_resident_bytes": peak,
        "platform": platform.platform(),
        "protocol_sha256": sha256(HERE / "protocol_v0_22_1.json"),
        "python": platform.python_version(),
        "registration_sha256": registration_sha,
        "result_sha256": sha256(result_path),
        "wall_seconds": elapsed,
    }
    write_json_exclusive(
        output / "run_receipt_v0_22_1.json", receipt
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
