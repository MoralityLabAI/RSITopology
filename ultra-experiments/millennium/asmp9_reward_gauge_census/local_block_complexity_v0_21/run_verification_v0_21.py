from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
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

from local_block_complexity import (
    asmp_count_floor_availability,
    asmp_count_floor_numerator,
    biconnected_edge_blocks,
    bridge_indices,
    count_floor_allocation,
    count_totally_cyclic_orientations,
    tutte_02_block_product,
    tutte_02_deletion_contraction,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
V020 = HERE.parent / "block_factorization_v0_20"
sys.path.insert(0, str(V020))
from block_factorization import availability as ternary_availability  # noqa: E402


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
        handle.write(
            json.dumps(value, indent=2, sort_keys=True) + "\n"
        )


def graph_parts(raw: dict[str, Any]) -> tuple[int, tuple[tuple[int, int], ...]]:
    return int(raw["node_count"]), tuple(
        tuple(edge) for edge in raw["edges"]
    )


def graph_nx(
    node_count: int, edges: tuple[tuple[int, int], ...]
) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(node_count))
    graph.add_edges_from(edges)
    return graph


def prior_graphs(registry: dict[str, Any]) -> Iterable[nx.Graph]:
    for record in registry["records"]:
        yield graph_nx(
            int(record["node_count"]),
            tuple(tuple(edge) for edge in record["edges"]),
        )


def exact_positive_compositions(total: int, parts: int) -> list[tuple[int, ...]]:
    if parts == 0:
        return [()] if total == 0 else []
    if total < parts:
        return []
    return [
        tuple(
            right - left
            for left, right in zip(
                (-1,) + separators,
                separators + (total - 1,),
                strict=True,
            )
        )
        for separators in itertools.combinations(
            range(total - 1), parts - 1
        )
    ]


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def validate_registration(
    registration_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    registration = json.loads(
        registration_path.read_text(encoding="utf-8")
    )
    for relative, expected in registration["sealed_files"].items():
        path = REPO / relative
        if not path.is_file() or sha256(path) != expected:
            raise RuntimeError(f"sealed hash mismatch: {relative}")
    protocol_path = REPO / registration["protocol_path"]
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    return registration, protocol, sha256(registration_path)


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
    gates: dict[str, dict[str, Any]] = {}

    gates["G0_registration_binding"] = {
        "pass": True,
        "registration_sha256": registration_sha,
        "sealed_file_count": len(registration["sealed_files"]),
    }

    registry = json.loads(
        (HERE / protocol["freshness_rule"]["burned_registry_path"])
        .read_text(encoding="utf-8")
    )
    old_graphs = list(prior_graphs(registry))
    primary_graphs: dict[
        str, tuple[int, tuple[tuple[int, int], ...]]
    ] = {
        name: graph_parts(raw)
        for name, raw in protocol["primary_graphs"].items()
    }
    all_registered_raw = {
        **protocol["primary_graphs"],
        "bridge_scope": protocol["controls"]["bridge_scope"],
        "block_product": protocol["controls"]["block_product"],
    }
    freshness: dict[str, Any] = {}
    for name, raw in all_registered_raw.items():
        node_count, edges = graph_parts(raw)
        graph = graph_nx(node_count, edges)
        matches = sum(
            prior.number_of_nodes() == node_count
            and prior.number_of_edges() == len(edges)
            and nx.is_isomorphic(graph, prior)
            for prior in old_graphs
        )
        freshness[name] = {
            "biconnected": nx.is_biconnected(graph),
            "bridge_count": len(list(nx.bridges(graph))),
            "edge_count": len(edges),
            "node_count": node_count,
            "prior_isomorphic_matches": matches,
        }
    names = sorted(primary_graphs)
    primary_pair_collisions = 0
    for left_index, left in enumerate(names):
        for right in names[left_index + 1 :]:
            ln, le = primary_graphs[left]
            rn, re = primary_graphs[right]
            if (
                ln == rn
                and len(le) == len(re)
                and nx.is_isomorphic(graph_nx(ln, le), graph_nx(rn, re))
            ):
                primary_pair_collisions += 1
    bridge_raw = protocol["controls"]["bridge_scope"]
    product_raw = protocol["controls"]["block_product"]
    product_node_count, product_edges = graph_parts(product_raw)
    product_blocks = biconnected_edge_blocks(
        product_node_count, product_edges
    )
    freshness_pass = (
        all(item["prior_isomorphic_matches"] == 0 for item in freshness.values())
        and primary_pair_collisions == 0
        and all(
            freshness[name]["biconnected"] for name in primary_graphs
        )
        and freshness["bridge_scope"]["bridge_count"]
        == bridge_raw["expected_bridge_count"]
        and sum(len(block) > 1 for block in product_blocks)
        == product_raw["expected_nontrivial_block_count"]
    )
    gates["G1_freshness_and_structure"] = {
        "freshness": freshness,
        "pairwise_primary_isomorphism_collisions": (
            primary_pair_collisions
        ),
        "pass": freshness_pass,
        "prior_graph_record_count": registry["graph_record_count"],
        "product_blocks": [list(block) for block in product_blocks],
    }

    primary_results: dict[str, Any] = {}
    for name, (node_count, edges) in primary_graphs.items():
        tutte = tutte_02_deletion_contraction(node_count, edges)
        orientations = count_totally_cyclic_orientations(
            node_count, edges
        )
        asmp = asmp_count_floor_numerator(node_count, edges)
        availability_value = asmp_count_floor_availability(
            node_count, edges
        )
        primary_results[name] = {
            "allocation": list(
                count_floor_allocation(len(edges), len(edges))
            ),
            "asmp_numerator": asmp,
            "availability": fraction_text(availability_value),
            "denominator_unreduced": 2 ** len(edges),
            "edge_count": len(edges),
            "total_orientation_count": 2 ** len(edges),
            "totally_cyclic_orientation_count": orientations,
            "tutte_02": tutte,
        }

    g2_pass = all(
        row["tutte_02"] == row["totally_cyclic_orientation_count"]
        for row in primary_results.values()
    )
    gates["G2_tutte_exhaustive_equality"] = {
        "pass": g2_pass,
        "per_graph": {
            name: {
                "totally_cyclic_orientation_count": row[
                    "totally_cyclic_orientation_count"
                ],
                "tutte_02": row["tutte_02"],
            }
            for name, row in primary_results.items()
        },
    }
    g3_pass = all(
        row["asmp_numerator"] == row["tutte_02"]
        for row in primary_results.values()
    )
    gates["G3_asmp_boundary_identity"] = {
        "pass": g3_pass,
        "per_graph": {
            name: {
                "asmp_numerator": row["asmp_numerator"],
                "tutte_02": row["tutte_02"],
            }
            for name, row in primary_results.items()
        },
    }

    small_name = "subdivided_k4_star"
    small_node_count, small_edges = primary_graphs[small_name]
    counts = (1,) * len(small_edges)
    epsilon = Fraction(1, 2)
    label_patterns = {
        "all_zero": (0,) * len(small_edges),
        "all_one": (1,) * len(small_edges),
        "alternating": tuple(
            index % 2 for index in range(len(small_edges))
        ),
    }
    label_values: dict[str, str] = {}
    for label_name, labels in label_patterns.items():
        probabilities = tuple(
            epsilon if label == 0 else 1 - epsilon
            for label in labels
        )
        label_values[label_name] = fraction_text(
            ternary_availability(
                small_node_count,
                small_edges,
                counts,
                probabilities,
                blockwise=False,
            )
        )
    normalized = all(
        Fraction(row["availability"])
        == Fraction(row["tutte_02"], row["denominator_unreduced"])
        for row in primary_results.values()
    )
    label_invariant = (
        len(set(label_values.values())) == 1
        and Fraction(next(iter(label_values.values())))
        == Fraction(primary_results[small_name]["availability"])
    )
    gates["G4_normalization_and_label_invariance"] = {
        "label_values": label_values,
        "normalization_exact": normalized,
        "pass": normalized and label_invariant,
    }

    composition_counts: dict[str, int] = {}
    design_value_match = True
    for name, (_, edges) in primary_graphs.items():
        compositions = exact_positive_compositions(
            len(edges), len(edges)
        )
        composition_counts[name] = len(compositions)
        design_value_match &= (
            len(compositions) == 1
            and compositions[0]
            == tuple(primary_results[name]["allocation"])
        )
    gates["G5_unique_count_floor_design_value"] = {
        "exact_positive_composition_counts": composition_counts,
        "pass": design_value_match,
        "value_equals_unique_allocation_availability": (
            design_value_match
        ),
    }

    bridge_node_count, bridge_edges = graph_parts(bridge_raw)
    bridge_tutte = tutte_02_deletion_contraction(
        bridge_node_count, bridge_edges
    )
    bridge_orientation_count = count_totally_cyclic_orientations(
        bridge_node_count, bridge_edges
    )
    bridge_asmp = asmp_count_floor_numerator(
        bridge_node_count, bridge_edges
    )
    wheel_count = primary_results["wheel_7"]["tutte_02"]
    bridge_availability = asmp_count_floor_availability(
        bridge_node_count, bridge_edges
    )
    wheel_availability = Fraction(
        primary_results["wheel_7"]["availability"]
    )
    gates["G6_bridge_scope_control"] = {
        "asmp_numerator": bridge_asmp,
        "bridge_indices": sorted(
            bridge_indices(bridge_node_count, bridge_edges)
        ),
        "pass": (
            bridge_tutte == 0
            and bridge_orientation_count == 0
            and bridge_asmp == 2 * wheel_count
            and bridge_availability == wheel_availability
        ),
        "quotient_availability": fraction_text(bridge_availability),
        "totally_cyclic_orientation_count": bridge_orientation_count,
        "tutte_02": bridge_tutte,
    }

    product_tutte = tutte_02_deletion_contraction(
        product_node_count, product_edges
    )
    product_exhaustive = count_totally_cyclic_orientations(
        product_node_count, product_edges
    )
    product_asmp = asmp_count_floor_numerator(
        product_node_count, product_edges
    )
    product_block = tutte_02_block_product(
        product_node_count, product_edges
    )
    gates["G7_block_product_and_localization"] = {
        "asmp_numerator": product_asmp,
        "block_product_tutte_02": product_block,
        "biconnected_oracle_calls": sum(
            len(block) > 1 for block in product_blocks
        ),
        "localization_reduction": (
            "bridge test; biconnected decomposition; one oracle call "
            "per nontrivial block; integer product"
        ),
        "pass": (
            product_tutte
            == product_exhaustive
            == product_asmp
            == product_block
        ),
        "totally_cyclic_orientation_count": product_exhaustive,
        "tutte_02": product_tutte,
    }

    allowed = protocol["complexity_statement"]["allowed"]
    forbidden = protocol["complexity_statement"]["forbidden"]
    gates["G8_complexity_attribution"] = {
        "allowed_statement_count": len(allowed),
        "forbidden_statement_count": len(forbidden),
        "pass": (
            len(protocol["prior_art"]) == 3
            and len(allowed) == 3
            and len(forbidden) == 4
            and "#P-complete" in allowed[0]
            and "Optimizer search" in forbidden[1]
        ),
        "proof_source": (
            "Las Vergnas identity plus Jaeger-Vertigan-Welsh "
            "graphic Tutte dichotomy; finite run is not the proof"
        ),
    }

    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    caps = protocol["resource_caps"]
    gates["G9_resource_and_scope"] = {
        "claim_boundary": protocol["claim_boundary"],
        "gpu_used": False,
        "pass": (
            elapsed <= caps["wall_seconds"]
            and peak <= caps["peak_resident_bytes"]
            and not caps["gpu_allowed"]
        ),
        "peak_resident_bytes": peak,
        "wall_seconds": elapsed,
    }

    gate_passes = {
        gate: bool(record["pass"]) for gate, record in gates.items()
    }
    substantive = [
        gate
        for gate in protocol["gate_ids"][1:9]
        if not gate_passes[gate]
    ]
    if not gate_passes["G0_registration_binding"] or not gate_passes[
        "G9_resource_and_scope"
    ]:
        verdict = protocol["verdict_map"][
            "binding_or_resource_gate_fails"
        ]
    elif substantive:
        verdict = protocol["verdict_map"][
            "any_substantive_identity_gate_fails"
        ]
    else:
        verdict = protocol["verdict_map"]["all_gates_pass"]

    result = {
        "claim_boundary": protocol["claim_boundary"],
        "gate_passes": gate_passes,
        "gates": gates,
        "primary_results": primary_results,
        "protocol_id": protocol["protocol_id"],
        "registration_sha256": registration_sha,
        "verdict": verdict,
    }
    result_path = output / "result_v0_21.json"
    write_json_exclusive(result_path, result)
    receipt = {
        "command": (
            "python run_verification_v0_21.py --registration "
            "registration_v0_21.json --output-dir artifacts_v0_21"
        ),
        "completed_at_utc": utc_now(),
        "git_commit": git("rev-parse", "HEAD"),
        "gpu_used": False,
        "peak_resident_bytes": peak,
        "platform": platform.platform(),
        "protocol_sha256": sha256(HERE / "protocol_v0_21.json"),
        "python": platform.python_version(),
        "registration_sha256": registration_sha,
        "result_sha256": sha256(result_path),
        "wall_seconds": elapsed,
    }
    write_json_exclusive(output / "run_receipt_v0_21.json", receipt)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
