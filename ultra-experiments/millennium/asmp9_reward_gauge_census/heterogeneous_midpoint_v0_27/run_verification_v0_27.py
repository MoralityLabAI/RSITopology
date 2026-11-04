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
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from midpoint_access import (
    effective_thresholds,
    expected_rounds,
    factorize_thresholds,
    graph_invariants,
    link_probability,
    maximum_bisection_error,
    reparameterize_arbitrary_midpoints,
    robust_reconstruction_check,
    spanning_forest_partition,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


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
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def peak_resident_bytes() -> int:
    if os.name == "nt":
        from ctypes import wintypes

        class Counters(ctypes.Structure):
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

        value = Counters()
        value.cb = ctypes.sizeof(value)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(Counters),
            wintypes.DWORD,
        )
        if not psapi.GetProcessMemoryInfo(
            kernel32.GetCurrentProcess(), ctypes.byref(value), value.cb
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(value.PeakWorkingSetSize)
    import resource

    usage = resource.getrusage(resource.RUSAGE_SELF)
    return int(usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024))


def validate_registration(path: Path):
    registration = json.loads(path.read_text())
    for relative, expected in registration["sealed_files"].items():
        if sha256(REPO / relative) != expected:
            raise RuntimeError(f"sealed hash mismatch: {relative}")
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
    protocol = json.loads((REPO / registration["protocol_path"]).read_text())
    return registration, protocol, sha256(path)


def fraction_strings(values):
    return tuple(Fraction(value) for value in values)


def graph_edges(cell):
    return tuple(tuple(edge) for edge in cell["edges"])


def graph_thresholds(cell):
    items = fraction_strings(cell["item_values"])
    contexts = fraction_strings(cell["context_values"])
    return tuple(items[item] - contexts[context] for item, context in graph_edges(cell))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("tracked tree must be clean before execution")

    started = time.perf_counter()
    started_at = utc_now()
    registration, protocol, registration_hash = validate_registration(
        args.registration.resolve()
    )
    gates: dict[str, dict[str, Any]] = {}
    gates["G0_registration_binding"] = {
        "pass": True,
        "registration_sha256": registration_hash,
        "sealed_file_count": len(registration["sealed_files"]),
    }
    fresh = protocol["fresh_validation"]

    localization = fresh["localization_cell"]
    radius = Fraction(localization["radius"])
    tolerance = Fraction(localization["tolerance"])
    denominator = int(localization["denominator"])
    limit = int(radius * denominator)
    targets = tuple(Fraction(value, denominator) for value in range(-limit, limit + 1))
    maximum_error, maximum_queries = maximum_bisection_error(
        targets, radius, tolerance
    )
    link_mismatches = 0
    link_checks = 0
    for cell in fresh["link_shape_cells"]:
        for numerator in range(-97, 98):
            value = numerator / 23
            probability = link_probability(
                cell["shape"], value, float(cell["scale"])
            )
            observed = (probability > 0.5) - (probability < 0.5)
            expected = (value > 0) - (value < 0)
            link_checks += 1
            link_mismatches += observed != expected
    shared_pass = (
        maximum_error <= tolerance
        and maximum_queries <= expected_rounds(radius, tolerance)
        and link_mismatches == 0
    )
    gates["G1_shared_midpoint_link_shape"] = {
        "checked_thresholds": len(targets),
        "link_checks": link_checks,
        "link_mismatches": link_mismatches,
        "maximum_error": str(maximum_error),
        "maximum_queries": maximum_queries,
        "pass": shared_pass,
    }

    witness = fresh["arbitrary_midpoint_witness"]
    witness_edges = graph_edges(witness)
    original_items = fraction_strings(witness["original_items"])
    alternative_items = fraction_strings(witness["alternative_items"])
    biases = fraction_strings(witness["biases"])
    shifted = reparameterize_arbitrary_midpoints(
        original_items, alternative_items, witness_edges, biases
    )
    original_thresholds = effective_thresholds(
        original_items, witness_edges, biases
    )
    alternative_thresholds = effective_thresholds(
        alternative_items, witness_edges, shifted
    )
    obstruction_pass = (
        original_items != alternative_items
        and original_thresholds == alternative_thresholds
    )
    gates["G2_arbitrary_midpoint_obstruction"] = {
        "edge_count": len(witness_edges),
        "maximum_item_displacement": str(
            max(abs(left - right) for left, right in zip(original_items, alternative_items))
        ),
        "pass": obstruction_pass,
        "thresholds_identical": original_thresholds == alternative_thresholds,
    }

    graph_rows = []
    factorization_pass = True
    liveness_pass = True
    ledger_pass = True
    cell_by_name = {}
    for cell in fresh["graph_cells"]:
        cell_by_name[cell["name"]] = cell
        edges = graph_edges(cell)
        invariants = graph_invariants(
            int(cell["num_items"]), int(cell["num_contexts"]), edges
        )
        thresholds = graph_thresholds(cell)
        factorization = factorize_thresholds(
            int(cell["num_items"]),
            int(cell["num_contexts"]),
            edges,
            thresholds,
        )
        forest, chords = spanning_forest_partition(
            int(cell["num_items"]), int(cell["num_contexts"]), edges
        )
        expected = {key: int(value) for key, value in cell["expected"].items()}
        invariant_match = invariants == expected
        ledger_match = (
            len(forest) == invariants["incidence_rank"]
            and len(chords) == invariants["cycle_rank"]
        )
        if chords:
            changed = list(thresholds)
            changed[edges.index(chords[0])] += Fraction(1, 29)
            perturbed = factorize_thresholds(
                int(cell["num_items"]),
                int(cell["num_contexts"]),
                edges,
                changed,
            )
            status = "live_refutation_observed"
            liveness_cell_pass = not perturbed.consistent
        else:
            changed = list(thresholds)
            changed[-1] += Fraction(1, 29)
            perturbed = factorize_thresholds(
                int(cell["num_items"]),
                int(cell["num_contexts"]),
                edges,
                changed,
            )
            status = "factorization_unavailable_by_design"
            liveness_cell_pass = perturbed.consistent
        row_pass = (
            invariant_match
            and factorization.consistent
            and ledger_match
            and liveness_cell_pass
        )
        factorization_pass &= invariant_match and factorization.consistent
        liveness_pass &= liveness_cell_pass
        ledger_pass &= ledger_match
        graph_rows.append(
            {
                "factorization_consistent": factorization.consistent,
                "invariants": invariants,
                "ledger_match": ledger_match,
                "liveness_status": status,
                "name": cell["name"],
                "pass": row_pass,
            }
        )
    gates["G3_context_factorization_and_gauge"] = {
        "pass": factorization_pass,
        "row_count": len(graph_rows),
    }
    gates["G4_cycle_liveness"] = {
        "pass": liveness_pass,
        "unavailable_cell_count": sum(
            row["liveness_status"] == "factorization_unavailable_by_design"
            for row in graph_rows
        ),
    }
    gates["G5_forest_chord_ledger"] = {"pass": ledger_pass}

    robust_rows = []
    robust_pass = True
    for robust_cell in fresh["robust_cells"]:
        cell = cell_by_name[robust_cell["graph_name"]]
        parameters = tuple(float(Fraction(value)) for value in cell["item_values"]) + tuple(
            float(Fraction(value)) for value in cell["context_values"]
        )
        check = robust_reconstruction_check(
            int(cell["num_items"]),
            int(cell["num_contexts"]),
            graph_edges(cell),
            parameters,
            tuple(float(value) for value in robust_cell["edge_error"]),
        )
        robust_pass &= bool(check["pass"])
        robust_rows.append({"graph_name": cell["name"], **check})
    gates["G6_robust_spectral_bound"] = {
        "pass": robust_pass,
        "row_count": len(robust_rows),
    }

    identifiers = sorted(row["identifier"] for row in protocol["prior_art"])
    required = sorted(
        [
            "ASMP-9-v0.11-v0.12",
            "ASMP-9-v0.26.2",
            "doi:10.1007/BF02293919",
            "doi:10.1007/s10107-010-0419-x",
            "doi:10.1093/biomet/asm029",
        ]
    )
    claim_pass = (
        identifiers == required
        and len(protocol["structured_claims"]["allowed"]) == 5
        and len(protocol["structured_claims"]["forbidden"]) == 6
        and "ASMP-9 is resolved."
        in protocol["structured_claims"]["forbidden"]
        and "no novelty is claimed" in protocol["claim_boundary"]
    )
    gates["G7_prior_art_and_claim_boundary"] = {
        "identifiers": identifiers,
        "pass": claim_pass,
    }

    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    caps = protocol["resource_caps"]
    resource_pass = (
        not caps["gpu_allowed"]
        and elapsed <= caps["wall_seconds"]
        and peak <= caps["peak_resident_bytes"]
    )
    gates["G8_resource_and_scope"] = {
        "gpu_used": False,
        "pass": resource_pass,
        "peak_resident_bytes": peak,
        "wall_seconds": elapsed,
    }

    gate_passes = {name: bool(record["pass"]) for name, record in gates.items()}
    binding_fail = not gate_passes["G0_registration_binding"]
    resource_fail = not gate_passes["G8_resource_and_scope"]
    if binding_fail or resource_fail:
        verdict_key = "binding_or_resource_gate_fails"
    elif all(gate_passes.values()):
        verdict_key = "all_gates_pass"
    else:
        verdict_key = "any_substantive_gate_fails"
    result = {
        "gate_passes": gate_passes,
        "gates": gates,
        "graph_rows": graph_rows,
        "protocol_id": protocol["protocol_id"],
        "registration_sha256": registration_hash,
        "robust_rows": robust_rows,
        "verdict": protocol["verdict_map"][verdict_key],
    }
    args.output_dir.mkdir(parents=True)
    result_path = args.output_dir / "result_v0_27.json"
    receipt_path = args.output_dir / "run_receipt_v0_27.json"
    write_json_exclusive(result_path, result)
    receipt = {
        "finished_at_utc": utc_now(),
        "implementation_commit": registration["implementation_commit"],
        "peak_resident_bytes": peak,
        "protocol_sha256": sha256(REPO / registration["protocol_path"]),
        "registration_sha256": registration_hash,
        "result_sha256": sha256(result_path),
        "run_commit": git("rev-parse", "HEAD"),
        "started_at_utc": started_at,
        "wall_seconds": elapsed,
    }
    write_json_exclusive(receipt_path, receipt)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

