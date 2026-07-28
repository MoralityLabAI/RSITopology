from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import subprocess
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

from experiment import (
    exact_allocation_optima,
    exhaustive_vertex_minimum_equal,
    fraction_record,
    minimal_equal_trials,
    one_sided_drift_availability,
    parse_fraction,
    sharp_min_availability,
    v014_crude_lower_bound,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


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
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
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


def validate_registration(
    path: Path, registration: dict[str, Any]
) -> tuple[str, dict[str, bool]]:
    relative = path.resolve().relative_to(REPO).as_posix()
    registration_commit = git("log", "-1", "--format=%H", "--", relative)
    checks = {
        "head_is_registration_commit": (
            git("rev-parse", "HEAD") == registration_commit
        ),
        "tracked_tree_clean": not git(
            "status", "--porcelain", "--untracked-files=no"
        ),
        "implementation_is_ancestor": subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                registration["implementation_commit"],
                registration_commit,
            ],
            cwd=REPO,
            check=False,
        ).returncode
        == 0,
    }
    for relative_path, expected in registration["sealed_files"].items():
        checks[f"hash:{relative_path}"] = (
            sha256(REPO / relative_path) == expected
        )
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"registration validation failed: {failed!r}")
    return registration_commit, checks


def build_theorem_records(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    registry = protocol["theorem_registry"]
    records = []
    for k in registry["cycle_lengths"]:
        for n in registry["trials_per_edge"]:
            for epsilon_text in registry["epsilon"]:
                epsilon = parse_fraction(epsilon_text)
                formula = sharp_min_availability(k, n, epsilon)
                exhaustive, witnesses = exhaustive_vertex_minimum_equal(
                    k, n, epsilon
                )
                drift = one_sided_drift_availability(k, n, epsilon)
                crude = v014_crude_lower_bound(k, n, epsilon)
                expected = sorted({k // 2, k - k // 2})
                records.append(
                    {
                        "cycle_length": k,
                        "trials_per_edge": n,
                        "epsilon": fraction_record(epsilon),
                        "sharp_minimum": fraction_record(formula),
                        "exhaustive_vertex_minimum": fraction_record(
                            exhaustive
                        ),
                        "minimizing_low_edge_counts": witnesses,
                        "expected_low_edge_counts": expected,
                        "formula_matches": formula == exhaustive,
                        "witnesses_match": witnesses == expected,
                        "v014_crude_bound": fraction_record(crude),
                        "sharp_dominates_crude": formula >= crude,
                        "one_low_drift": fraction_record(drift),
                        "sharp_strictly_below_drift": formula < drift,
                    }
                )
    return records


def build_threshold_records(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    registry = protocol["threshold_registry"]
    records = []
    for k in registry["cycle_lengths"]:
        for epsilon_text in registry["epsilon"]:
            epsilon = parse_fraction(epsilon_text)
            for delta_text in registry["delta"]:
                delta = parse_fraction(delta_text)
                target = 1 - delta
                threshold = minimal_equal_trials(k, epsilon, target)
                if threshold is None:
                    raise AssertionError("positive interior has no threshold")
                current = sharp_min_availability(k, threshold, epsilon)
                predecessor = (
                    Fraction(0)
                    if threshold == 1
                    else sharp_min_availability(k, threshold - 1, epsilon)
                )
                records.append(
                    {
                        "cycle_length": k,
                        "epsilon": fraction_record(epsilon),
                        "delta": fraction_record(delta),
                        "target": fraction_record(target),
                        "minimum_trials_per_edge": threshold,
                        "predecessor_availability": fraction_record(
                            predecessor
                        ),
                        "threshold_availability": fraction_record(current),
                        "threshold_straddles_target": (
                            predecessor < target <= current
                        ),
                    }
                )
    return records


def build_zero_interior_records(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    registry = protocol["zero_interior_registry"]
    records = []
    for k in registry["cycle_lengths"]:
        for n in registry["trials_per_edge"]:
            value = sharp_min_availability(k, n, Fraction(0))
            records.append(
                {
                    "cycle_length": k,
                    "trials_per_edge": n,
                    "minimum_availability": fraction_record(value),
                    "is_zero": value == 0,
                }
            )
    return records


def build_allocation_records(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    registry = protocol["allocation_registry"]
    records = []
    for k in registry["cycle_lengths"]:
        for epsilon_text in registry["epsilon"]:
            epsilon = parse_fraction(epsilon_text)
            for extra in registry["extra_total_trials"]:
                records.append(
                    exact_allocation_optima(k + extra, k, epsilon)
                )
    return records


def unique_cell_count(
    records: list[dict[str, Any]], fields: tuple[str, ...]
) -> int:
    return len(
        {
            tuple(
                (
                    record[field]["fraction"]
                    if isinstance(record[field], dict)
                    and "fraction" in record[field]
                    else record[field]
                )
                for field in fields
            )
            for record in records
        }
    )


def evaluate_gates(
    *,
    protocol: dict[str, Any],
    binding: dict[str, bool],
    theorem: list[dict[str, Any]],
    thresholds: list[dict[str, Any]],
    zero: list[dict[str, Any]],
    allocations: list[dict[str, Any]],
    elapsed_seconds: float,
    peak_bytes: int,
) -> dict[str, bool]:
    theorem_unique = unique_cell_count(
        theorem, ("cycle_length", "trials_per_edge", "epsilon")
    )
    threshold_unique = unique_cell_count(
        thresholds, ("cycle_length", "epsilon", "delta")
    )
    zero_unique = unique_cell_count(
        zero, ("cycle_length", "trials_per_edge")
    )
    allocation_unique = unique_cell_count(
        allocations, ("cycle_length", "epsilon", "total_trials")
    )
    caps = protocol["resource_caps"]
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_registry_completeness": (
            len(theorem) == theorem_unique == 36
            and len(thresholds) == threshold_unique == 48
            and len(zero) == zero_unique == 6
            and len(allocations) == allocation_unique == 32
        ),
        "G2_exact_minimax_formula": all(
            row["formula_matches"] for row in theorem
        ),
        "G3_balanced_endpoint_witness": all(
            row["witnesses_match"] for row in theorem
        ),
        "G4_bound_and_drift_controls": all(
            row["sharp_dominates_crude"]
            and row["sharp_strictly_below_drift"]
            for row in theorem
        ),
        "G5_exact_trial_threshold": all(
            row["threshold_straddles_target"] for row in thresholds
        ),
        "G6_zero_interior_control": all(row["is_zero"] for row in zero),
        "G7_finite_allocation_falsification": all(
            row["balanced_is_optimal"] for row in allocations
        ),
        "G8_resource_and_scope": (
            not caps["gpu_allowed"]
            and elapsed_seconds <= caps["wall_seconds"]
            and peak_bytes <= caps["peak_resident_bytes"]
            and bool(protocol["claim_boundary"])
        ),
    }
    if list(gates) != protocol["gate_ids"]:
        raise RuntimeError("runtime gate universe differs from protocol")
    return gates


def render_report(result: dict[str, Any]) -> str:
    gates = "\n".join(
        f"- `{name}`: **{'PASS' if passed else 'FAIL'}**"
        for name, passed in result["gates"].items()
    )
    threshold_rows = sorted(
        result["threshold_records"],
        key=lambda row: (
            row["cycle_length"],
            row["epsilon"]["decimal"],
            row["delta"]["decimal"],
        ),
    )
    examples = "\n".join(
        "| {cycle_length} | {epsilon} | {target:.6f} | {n} |".format(
            cycle_length=row["cycle_length"],
            epsilon=row["epsilon"]["fraction"],
            target=row["target"]["decimal"],
            n=row["minimum_trials_per_edge"],
        )
        for row in threshold_rows
    )
    return f"""# ASMP-9 sharp interior availability v0.15 result

## Verdict

`{result["verdict"]}`

All quantities are exact rationals; decimals are display aids.

## Gates

{gates}

## Fresh exact registry

- theorem cells: {len(result["theorem_records"])}
- threshold cells: {len(result["threshold_records"])}
- zero-interior controls: {len(result["zero_interior_records"])}
- unequal-allocation cells: {len(result["allocation_records"])}

## Exact threshold table

| cycle length | epsilon | target availability | minimum trials/edge |
| ---: | ---: | ---: | ---: |
{examples}

## Unequal allocation

Balanced integer allocation was an optimizer in
{result["summary"]["balanced_allocation_pass_count"]} of
{len(result["allocation_records"])} fresh finite cells.

This is a finite falsification result only. It does not prove that balanced
allocation is optimal for arbitrary cycle length, interior, or total budget.

## Resources

- elapsed seconds: {result["resources"]["elapsed_seconds"]:.6f}
- peak resident bytes: {result["resources"]["peak_resident_bytes"]}
- GPU used: false

## Claim boundary

{result["claim_boundary"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(
            f"refusing to overwrite output directory: {args.output_dir}"
        )

    started = time.perf_counter()
    registration_path = args.registration.resolve()
    registration = json.loads(
        registration_path.read_text(encoding="utf-8")
    )
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    registration_commit, binding = validate_registration(
        registration_path, registration
    )

    theorem = build_theorem_records(protocol)
    thresholds = build_threshold_records(protocol)
    zero = build_zero_interior_records(protocol)
    allocations = build_allocation_records(protocol)
    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    gates = evaluate_gates(
        protocol=protocol,
        binding=binding,
        theorem=theorem,
        thresholds=thresholds,
        zero=zero,
        allocations=allocations,
        elapsed_seconds=elapsed,
        peak_bytes=peak,
    )
    verdict = (
        "registered_exact_result_passed"
        if all(gates.values())
        else "registered_exact_result_failed"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "implementation_commit": registration["implementation_commit"],
        "verdict": verdict,
        "gates": gates,
        "binding_checks": binding,
        "theorem_records": theorem,
        "threshold_records": thresholds,
        "zero_interior_records": zero,
        "allocation_records": allocations,
        "summary": {
            "balanced_allocation_pass_count": sum(
                row["balanced_is_optimal"] for row in allocations
            ),
            "theorem_formula_mismatch_count": sum(
                not row["formula_matches"] for row in theorem
            ),
            "threshold_mismatch_count": sum(
                not row["threshold_straddles_target"]
                for row in thresholds
            ),
        },
        "resources": {
            "elapsed_seconds": elapsed,
            "peak_resident_bytes": peak,
            "gpu_used": False,
        },
        "claim_boundary": protocol["claim_boundary"],
    }

    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_15.json"
    report_path = args.output_dir / "RESULT_v0_15.md"
    write_json(result_path, result)
    write_text(report_path, render_report(result))
    receipt = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "implementation_commit": registration["implementation_commit"],
        "verdict": verdict,
        "output_hashes": {
            result_path.name: sha256(result_path),
            report_path.name: sha256(report_path),
        },
        "resources": result["resources"],
    }
    write_json(args.output_dir / "receipt_v0_15.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
