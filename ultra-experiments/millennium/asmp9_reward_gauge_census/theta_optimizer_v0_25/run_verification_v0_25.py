from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterator, Sequence

from theta_optimizer import (
    build_theta_graph,
    flatten_balanced_allocation,
    optimize_theta,
    predecessor_availability,
    smooth_within_path,
    theta_availability_from_path_counts,
    theta_numerator_from_path_counts,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

EXPECTED_ALLOWED = [
    "The registered four-state formula exactly computes strong "
    "availability on the fresh generalized-theta cells at epsilon=1/2.",
    "Every global optimizer in the declared generalized-theta class "
    "balances counts within each individual path.",
    "Enumerating balanced path totals returns the exact global "
    "optimizer; for fixed path count it is polynomial in the numerical "
    "budget and pseudopolynomial in binary-encoded N.",
    "This is a conservative ASMP specialization in a classical "
    "reliability-allocation neighborhood; no novelty claim is "
    "registered.",
]
EXPECTED_FORBIDDEN = [
    "All series-parallel or arbitrary biconnected blocks are solved.",
    "The optimizer is polynomial in binary input length or "
    "fixed-parameter tractable in k plus log N.",
    "All edges or all path totals are globally balanced.",
    "Exact optimizer search is hard, approximation is hard, or no "
    "better algorithm exists.",
    "The result covers arbitrary epsilon, adaptive allocation, "
    "dependent responses, response misspecification, behavioral "
    "reward identification, or general inverse reinforcement learning.",
    "Classical majorization, Schur-convex allocation, "
    "active-redundancy theory, or pseudopolynomial reliability "
    "allocation is new.",
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

    usage = resource.getrusage(resource.RUSAGE_SELF)
    return int(usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024))


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def fraction_record(value: Fraction) -> dict[str, int]:
    return {
        "denominator": value.denominator,
        "numerator": value.numerator,
    }


def validate_registration(
    path: Path,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    registration = json.loads(path.read_text(encoding="utf-8"))
    for relative, expected in registration["sealed_files"].items():
        actual = sha256(REPO / relative)
        if actual != expected:
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
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    return registration, protocol, sha256(path)


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
    paths: list[tuple[int, ...]] = []
    for length in lengths:
        paths.append(tuple(flat[offset : offset + length]))
        offset += length
    if offset != len(flat):
        raise ValueError("flat count dimension does not match path lengths")
    return tuple(paths)


def path_balanced(paths: Sequence[Sequence[int]]) -> bool:
    return all(max(path) - min(path) <= 1 for path in paths)


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

    fresh_formula = protocol["fresh_validation"]["formula_cells"]
    fresh_optimizer = protocol["fresh_validation"]["optimizer_cells"]
    burned = {
        (
            tuple(cell["path_lengths"]),
            int(cell["total_budget"]),
        )
        for cell in protocol["freshness_rule"]["burned_cells"]
    }
    all_lengths = [
        tuple(cell["path_lengths"])
        for cell in fresh_formula + fresh_optimizer
    ]
    fresh_pairs = {
        (tuple(cell["path_lengths"]), int(cell["total_budget"]))
        for cell in fresh_optimizer
    }
    structure_pass = (
        all(len(lengths) >= 3 for lengths in all_lengths)
        and all(lengths.count(1) <= 1 for lengths in all_lengths)
        and not (fresh_pairs & burned)
    )
    gates["G1_freshness_and_structure"] = {
        "burned_overlap": [
            {"path_lengths": list(lengths), "total_budget": budget}
            for lengths, budget in sorted(fresh_pairs & burned)
        ],
        "fresh_formula_cell_count": len(fresh_formula),
        "fresh_optimizer_cell_count": len(fresh_optimizer),
        "pass": structure_pass,
    }

    formula_rows: list[dict[str, Any]] = []
    for cell in fresh_formula:
        lengths = tuple(cell["path_lengths"])
        paths = tuple(tuple(path) for path in cell["path_counts"])
        graph = build_theta_graph(lengths)
        flat = tuple(count for path in paths for count in path)
        closed_form = theta_availability_from_path_counts(paths)
        predecessor = predecessor_availability(graph, flat)
        formula_rows.append(
            {
                "closed_form": fraction_record(closed_form),
                "equal": closed_form == predecessor,
                "name": cell["name"],
                "path_lengths": list(lengths),
                "predecessor": fraction_record(predecessor),
                "total_trials": sum(flat),
            }
        )
    gates["G2_path_state_formula"] = {
        "cell_count": len(formula_rows),
        "pass": all(row["equal"] for row in formula_rows),
    }

    smoothing = protocol["fresh_validation"]["smoothing_cell"]
    smoothing_lengths = tuple(smoothing["path_lengths"])
    smoothing_values = tuple(smoothing["count_values"])
    smoothing_comparisons = 0
    minimum_improvement: int | None = None
    smoothing_pass = True
    for flat in itertools.product(
        smoothing_values, repeat=sum(smoothing_lengths)
    ):
        paths = split_paths(flat, smoothing_lengths)
        before = theta_numerator_from_path_counts(paths)
        for path_index, path in enumerate(paths):
            for high_index in range(len(path)):
                for low_index in range(len(path)):
                    if path[high_index] < path[low_index] + 2:
                        continue
                    after_paths = smooth_within_path(
                        paths, path_index, high_index, low_index
                    )
                    improvement = (
                        theta_numerator_from_path_counts(after_paths) - before
                    )
                    smoothing_comparisons += 1
                    minimum_improvement = (
                        improvement
                        if minimum_improvement is None
                        else min(minimum_improvement, improvement)
                    )
                    smoothing_pass &= improvement > 0
    gates["G3_strict_path_smoothing"] = {
        "comparison_count": smoothing_comparisons,
        "minimum_improvement": minimum_improvement,
        "pass": smoothing_pass and smoothing_comparisons > 0,
    }

    optimizer_rows: list[dict[str, Any]] = []
    reduced_exact = True
    composition_exact = True
    every_full_optimum_balanced = True
    for cell in fresh_optimizer:
        lengths = tuple(cell["path_lengths"])
        total_budget = int(cell["total_budget"])
        edge_count = sum(lengths)
        full_maximum: int | None = None
        full_optimizer_count = 0
        full_balanced_count = 0
        full_cell_count = 0
        for flat in positive_compositions(total_budget, edge_count):
            full_cell_count += 1
            paths = split_paths(flat, lengths)
            numerator = theta_numerator_from_path_counts(paths)
            if full_maximum is None or numerator > full_maximum:
                full_maximum = numerator
                full_optimizer_count = 1
                full_balanced_count = int(path_balanced(paths))
            elif numerator == full_maximum:
                full_optimizer_count += 1
                full_balanced_count += int(path_balanced(paths))
        if full_maximum is None:
            raise AssertionError("full enumeration returned no cells")

        reduced = optimize_theta(lengths, total_budget)
        expected_compositions = math.comb(
            total_budget - edge_count + len(lengths) - 1,
            len(lengths) - 1,
        )
        exact = reduced.numerator == full_maximum
        count_exact = reduced.composition_count == expected_compositions
        all_balanced = full_balanced_count == full_optimizer_count
        reduced_allocations_balanced = all(
            path_balanced(
                split_paths(
                    flatten_balanced_allocation(lengths, totals),
                    lengths,
                )
            )
            for totals in reduced.path_totals
        )
        reduced_exact &= exact
        composition_exact &= count_exact
        every_full_optimum_balanced &= (
            all_balanced and reduced_allocations_balanced
        )
        optimizer_rows.append(
            {
                "composition_count": reduced.composition_count,
                "composition_count_exact": count_exact,
                "expected_composition_count": expected_compositions,
                "full_cell_count": full_cell_count,
                "full_cell_count_expected": math.comb(
                    total_budget - 1, edge_count - 1
                ),
                "full_maximum_numerator": full_maximum,
                "full_optimizer_count": full_optimizer_count,
                "full_optimizers_path_balanced": all_balanced,
                "name": cell["name"],
                "path_lengths": list(lengths),
                "reduced_exact": exact,
                "reduced_maximum_numerator": reduced.numerator,
                "reduced_path_totals": [
                    list(totals) for totals in reduced.path_totals
                ],
                "total_budget": total_budget,
            }
        )
    gates["G4_reduced_optimizer_exactness"] = {
        "cell_count": len(optimizer_rows),
        "pass": reduced_exact,
    }
    gates["G5_composition_count"] = {
        "cell_count": len(optimizer_rows),
        "pass": composition_exact,
    }
    gates["G6_optimizer_path_balance"] = {
        "cell_count": len(optimizer_rows),
        "pass": every_full_optimum_balanced,
    }

    claims = protocol["structured_claims"]
    prior_text = (HERE / "PRIOR_ART_GATE_v0_25.md").read_text(
        encoding="utf-8"
    )
    attribution_pass = (
        claims["allowed"] == EXPECTED_ALLOWED
        and claims["forbidden"] == EXPECTED_FORBIDDEN
        and "No novelty claim is registered" in prior_text
        and "Primary-source dispositions" in prior_text
        and "ASMP-9" in protocol["claim_boundary"]
    )
    gates["G7_prior_art_and_claim_boundary"] = {
        "allowed_exact": claims["allowed"] == EXPECTED_ALLOWED,
        "forbidden_exact": claims["forbidden"] == EXPECTED_FORBIDDEN,
        "no_novelty_claim": "No novelty claim is registered" in prior_text,
        "pass": attribution_pass,
    }

    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    caps = protocol["resource_caps"]
    gates["G8_resource_and_scope"] = {
        "gpu_used": False,
        "pass": (
            elapsed <= caps["wall_seconds"]
            and peak <= caps["peak_resident_bytes"]
        ),
        "peak_resident_bytes": peak,
        "wall_seconds": elapsed,
    }

    gate_passes = {
        gate_id: bool(record["pass"]) for gate_id, record in gates.items()
    }
    if set(gate_passes) != set(protocol["gate_ids"]):
        raise RuntimeError("gate universe differs from protocol")
    if not gate_passes["G0_registration_binding"] or not gate_passes[
        "G8_resource_and_scope"
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
        "completed_at_utc": utc_now(),
        "formula_rows": formula_rows,
        "gate_passes": gate_passes,
        "gates": gates,
        "optimizer_rows": optimizer_rows,
        "protocol_id": protocol["protocol_id"],
        "registration_sha256": registration_sha,
        "verdict": verdict,
    }
    output_dir.mkdir(parents=True)
    result_path = output_dir / "result_v0_25.json"
    write_json_exclusive(result_path, result)
    receipt = {
        "command": (
            "python run_verification_v0_25.py --registration "
            "registration_v0_25.json --output-dir artifacts_v0_25"
        ),
        "completed_at_utc": result["completed_at_utc"],
        "execution_commit": git("rev-parse", "HEAD"),
        "peak_resident_bytes": peak,
        "protocol_sha256": sha256(HERE / "protocol_v0_25.json"),
        "registration_sha256": registration_sha,
        "result_sha256": sha256(result_path),
        "started_at_utc": started_at,
        "wall_seconds": elapsed,
    }
    write_json_exclusive(
        output_dir / "run_receipt_v0_25.json", receipt
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
