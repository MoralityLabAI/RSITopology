from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import networkx as nx

from nonuniform_multivariate import (
    K4_EDGES,
    K4_HIGH_EDGES,
    K4_LOW_EDGES,
    direct_nonuniform_availability,
    k4_balanced_closed_form,
    k4_balanced_counts,
    k4_balanced_minus_trap_gap,
    k4_m_concavity_deficit,
    k4_neighbor_gap_certificate,
    k4_opposite_pair_numerator,
    k4_trap_closed_form,
    k4_trap_counts,
    multivariate_coefficient,
    multivariate_tutte_availability,
    one_unit_exchange_neighbors,
    oriented_completion_count,
    trial_numerator,
    uniform_backman_availability,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

EXPECTED_ALLOWED = [
    "At epsilon=1/2, arbitrary positive integer edge counts on a "
    "finite simple biconnected block have the exact edge-multivariate "
    "q=-1 representation stated in the protocol.",
    "For every integer s>=2, the registered K4 trap is a strict "
    "one-unit-exchange local maximum but the balanced allocation at "
    "the same total count has strictly greater availability.",
    "The registered K4 pair gives an explicit violation of the "
    "M-concavity exchange axiom, so one-unit exchange ascent has no "
    "general global-optimality guarantee for this frozen ASMP "
    "objective.",
    "The multivariate identity is a prior-art-derived ASMP "
    "access-model specialization, not a new graph polynomial.",
]
EXPECTED_FORBIDDEN = [
    "The global maximin optimizer is classified on arbitrary "
    "biconnected blocks.",
    "Exact optimizer search is NP-hard or no polynomial-time optimizer "
    "exists.",
    "The trap gives a global approximation lower bound.",
    "The result covers arbitrary epsilon, adaptive allocation, "
    "dependent responses, response misspecification, behavioral "
    "reward identification, or general IRL.",
    "The multivariate Tutte polynomial, weighted partial-orientation "
    "calculus, or M-concavity theory is new.",
    "ASMP-9 is resolved.",
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
            raise ctypes.WinError(ctypes.get_last_error())
        return int(counters.PeakWorkingSetSize)
    import resource

    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(usage * (1 if sys.platform == "darwin" else 1024))


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def fraction_record(value: Any) -> dict[str, int]:
    return {
        "denominator": int(value.denominator),
        "numerator": int(value.numerator),
    }


def validate_registration(
    path: Path,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    registration = json.loads(path.read_text(encoding="utf-8"))
    for relative, expected in registration["sealed_files"].items():
        actual = sha256(REPO / relative)
        if actual != expected:
            raise RuntimeError(f"sealed hash mismatch: {relative}")
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            registration["implementation_commit"],
            "HEAD",
        ],
        cwd=REPO,
        check=True,
    )
    return registration, protocol, sha256(path)


def graph_from(raw: dict[str, Any]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(raw["node_count"]))
    graph.add_edges_from(raw["edges"])
    return graph


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(output_dir)
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("tracked tree must be clean before execution")

    started_at = utc_now()
    started = time.perf_counter()
    registration, protocol, registration_sha = validate_registration(
        args.registration.resolve()
    )
    gates: dict[str, dict[str, Any]] = {}

    gates["G0_registration_binding"] = {
        "pass": True,
        "registration_sha256": registration_sha,
        "sealed_file_count": len(registration["sealed_files"]),
    }

    raw_graph = protocol["fresh_validation"]["graph"]
    graph = graph_from(raw_graph)
    registry_path = (
        HERE / protocol["freshness_rule"]["burned_registry_path"]
    ).resolve()
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    old_graphs = [
        graph_from(record) for record in registry["records"]
    ]
    is_fresh = not any(
        len(old) == len(graph)
        and old.number_of_edges() == graph.number_of_edges()
        and nx.is_isomorphic(old, graph)
        for old in old_graphs
    )
    structure_pass = (
        nx.is_biconnected(graph)
        and not list(nx.bridges(graph))
        and nx.number_of_selfloops(graph) == 0
        and graph.number_of_edges() == len(set(graph.edges()))
        and is_fresh
    )
    gates["G1_freshness_and_structure"] = {
        "biconnected": nx.is_biconnected(graph),
        "bridges": [list(edge) for edge in nx.bridges(graph)],
        "edge_count": graph.number_of_edges(),
        "fresh_against_registry": is_fresh,
        "node_count": graph.number_of_nodes(),
        "pass": structure_pass,
        "registry_sha256": sha256(registry_path),
    }

    node_count = raw_graph["node_count"]
    edges = tuple(tuple(edge) for edge in raw_graph["edges"])
    primary_rows: list[dict[str, Any]] = []
    for name, raw_counts in protocol["fresh_validation"]["counts"].items():
        counts = tuple(raw_counts)
        direct = direct_nonuniform_availability(
            node_count, edges, counts
        )
        multivariate = multivariate_tutte_availability(
            node_count, edges, counts
        )
        primary_rows.append(
            {
                "counts": list(counts),
                "direct": fraction_record(direct),
                "equal": direct == multivariate,
                "multivariate": fraction_record(multivariate),
                "name": name,
                "total_trials": sum(counts),
                "trial_numerator": trial_numerator(
                    node_count, edges, counts
                ),
            }
        )
    gates["G2_multivariate_identity"] = {
        "cell_count": len(primary_rows),
        "pass": all(row["equal"] for row in primary_rows),
    }

    coefficient_rows: list[dict[str, Any]] = []
    for mask in protocol["fresh_validation"]["coefficient_masks"]:
        interior = tuple(
            index
            for index in range(len(edges))
            if (mask >> index) & 1
        )
        direct_count = oriented_completion_count(
            node_count, edges, interior
        )
        coefficient = multivariate_coefficient(
            node_count, edges, interior
        )
        coefficient_rows.append(
            {
                "coefficient": coefficient,
                "direct_completion_count": direct_count,
                "equal": coefficient == direct_count,
                "interior_edge_indices": list(interior),
                "mask": mask,
            }
        )
    gates["G3_coefficientwise_identity"] = {
        "cell_count": len(coefficient_rows),
        "pass": all(row["equal"] for row in coefficient_rows),
    }

    uniform_rows: list[dict[str, Any]] = []
    for trial_count in protocol["fresh_validation"]["uniform_counts"]:
        counts = (trial_count,) * len(edges)
        multivariate = multivariate_tutte_availability(
            node_count, edges, counts
        )
        ordinary = uniform_backman_availability(
            node_count, edges, trial_count
        )
        uniform_rows.append(
            {
                "backman": fraction_record(ordinary),
                "equal": multivariate == ordinary,
                "multivariate": fraction_record(multivariate),
                "trial_count": trial_count,
            }
        )
    gates["G4_uniform_specialization"] = {
        "cell_count": len(uniform_rows),
        "pass": all(row["equal"] for row in uniform_rows),
    }

    k4_rows: list[dict[str, Any]] = []
    all_closed = True
    all_local = True
    all_suboptimal = True
    all_m_concavity = True
    for s in protocol["k4_family"]["fresh_numeric_checks"]:
        t = 2**s
        trap = k4_trap_counts(s)
        balanced = k4_balanced_counts(s)
        trap_value = trial_numerator(4, K4_EDGES, trap)
        balanced_value = trial_numerator(4, K4_EDGES, balanced)
        trap_closed = k4_trap_closed_form(t)
        balanced_closed = k4_balanced_closed_form(t)
        pair_closed = k4_opposite_pair_numerator(
            t // 2, t, 2 * t
        )
        balanced_gap = balanced_value - trap_value
        gap_closed = k4_balanced_minus_trap_gap(t)

        neighbor_rows: list[dict[str, Any]] = []
        for donor, recipient, counts in one_unit_exchange_neighbors(
            trap, floor=1
        ):
            label, certified_gap = k4_neighbor_gap_certificate(
                donor, recipient, t
            )
            observed_gap = trap_value - trial_numerator(
                4, K4_EDGES, counts
            )
            neighbor_rows.append(
                {
                    "certified_gap": certified_gap,
                    "class": label,
                    "donor": donor,
                    "equal": observed_gap == certified_gap,
                    "observed_gap": observed_gap,
                    "positive": observed_gap > 0,
                    "recipient": recipient,
                }
            )
        local_pass = all(
            row["equal"] and row["positive"] for row in neighbor_rows
        )

        exchange_rows: list[dict[str, Any]] = []
        for high in sorted(K4_HIGH_EDGES):
            for low in sorted(K4_LOW_EDGES):
                x_exchange = list(trap)
                y_exchange = list(balanced)
                x_exchange[high] -= 1
                x_exchange[low] += 1
                y_exchange[high] += 1
                y_exchange[low] -= 1
                observed = (
                    trap_value
                    + balanced_value
                    - trial_numerator(4, K4_EDGES, x_exchange)
                    - trial_numerator(4, K4_EDGES, y_exchange)
                )
                expected = k4_m_concavity_deficit(t)
                exchange_rows.append(
                    {
                        "deficit": observed,
                        "equal": observed == expected,
                        "high_edge": high,
                        "low_edge": low,
                        "positive": observed > 0,
                    }
                )
        m_pass = all(
            row["equal"] and row["positive"] for row in exchange_rows
        )
        closed_pass = (
            trap_value == trap_closed == pair_closed
            and balanced_value == balanced_closed
        )
        suboptimal_pass = balanced_gap == gap_closed > 0
        all_closed &= closed_pass
        all_local &= local_pass
        all_suboptimal &= suboptimal_pass
        all_m_concavity &= m_pass
        k4_rows.append(
            {
                "balanced_counts": list(balanced),
                "balanced_minus_trap_gap": balanced_gap,
                "balanced_numerator": balanced_value,
                "closed_form_pass": closed_pass,
                "exchange_rows": exchange_rows,
                "local_pass": local_pass,
                "m_concavity_pass": m_pass,
                "neighbor_class_count": len(
                    {row["class"] for row in neighbor_rows}
                ),
                "neighbor_count": len(neighbor_rows),
                "neighbor_minimum_gap": min(
                    row["observed_gap"] for row in neighbor_rows
                ),
                "s": s,
                "suboptimal_pass": suboptimal_pass,
                "t": t,
                "trap_counts": list(trap),
                "trap_numerator": trap_value,
            }
        )
    gates["G5_k4_closed_forms"] = {"pass": all_closed}
    gates["G6_strict_local_maximum"] = {"pass": all_local}
    gates["G7_strict_suboptimality"] = {"pass": all_suboptimal}
    gates["G8_m_concavity_violation"] = {
        "pass": all_m_concavity
    }

    structured = protocol["structured_claims"]
    attribution_pass = (
        structured["allowed"] == EXPECTED_ALLOWED
        and structured["forbidden"] == EXPECTED_FORBIDDEN
        and "does not classify the global maximin optimizer"
        in protocol["claim_boundary"]
        and "ASMP-9" in protocol["claim_boundary"]
    )
    gates["G9_structured_attribution"] = {
        "allowed_exact": structured["allowed"] == EXPECTED_ALLOWED,
        "forbidden_exact": structured["forbidden"] == EXPECTED_FORBIDDEN,
        "pass": attribution_pass,
    }

    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    caps = protocol["resource_caps"]
    gates["G10_resource_and_scope"] = {
        "gpu_used": False,
        "pass": (
            elapsed <= caps["wall_seconds"]
            and peak <= caps["peak_resident_bytes"]
        ),
        "peak_resident_bytes": peak,
        "wall_seconds": elapsed,
    }

    gate_passes = {
        gate: bool(record["pass"]) for gate, record in gates.items()
    }
    if set(gate_passes) != set(protocol["gate_ids"]):
        raise RuntimeError("gate universe differs from protocol")
    if not gate_passes["G0_registration_binding"] or not gate_passes[
        "G10_resource_and_scope"
    ]:
        verdict = protocol["verdict_map"][
            "binding_or_resource_gate_fails"
        ]
    elif all(gate_passes.values()):
        verdict = protocol["verdict_map"]["all_gates_pass"]
    else:
        verdict = protocol["verdict_map"][
            "any_substantive_gate_fails"
        ]

    result = {
        "coefficient_rows": coefficient_rows,
        "completed_at_utc": utc_now(),
        "gate_passes": gate_passes,
        "gates": gates,
        "k4_rows": k4_rows,
        "primary_rows": primary_rows,
        "protocol_id": protocol["protocol_id"],
        "registration_sha256": registration_sha,
        "uniform_rows": uniform_rows,
        "verdict": verdict,
    }
    output_dir.mkdir(parents=True)
    result_path = output_dir / "result_v0_23.json"
    write_json_exclusive(result_path, result)
    receipt = {
        "command": (
            "python run_verification_v0_23.py --registration "
            "registration_v0_23.json --output-dir artifacts_v0_23"
        ),
        "completed_at_utc": result["completed_at_utc"],
        "execution_commit": git("rev-parse", "HEAD"),
        "peak_resident_bytes": peak,
        "protocol_sha256": sha256(HERE / "protocol_v0_23.json"),
        "registration_sha256": registration_sha,
        "result_sha256": sha256(result_path),
        "started_at_utc": started_at,
        "wall_seconds": elapsed,
    }
    write_json_exclusive(
        output_dir / "run_receipt_v0_23.json", receipt
    )
    print(
        json.dumps(
            {
                "gate_passes": gate_passes,
                "result_sha256": receipt["result_sha256"],
                "verdict": verdict,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
