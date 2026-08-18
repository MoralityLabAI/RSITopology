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
from fractions import Fraction
from pathlib import Path
from typing import Any

from experiment import (
    allocation_census,
    balanced_allocation,
    balanced_worst_closed,
    fraction_record,
    minimal_total_trials,
    pair_constants,
    parse_fraction,
    smoothing_certificate,
    worst_endpoint_availability,
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


def build_pair_records(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    registry = protocol["pair_registry"]
    records = []
    for epsilon_text in registry["epsilon"]:
        epsilon = parse_fraction(epsilon_text)
        for a in registry["a"]:
            for difference in registry["differences"]:
                b = a + difference
                for other_values in registry["other_count_tuples"]:
                    other_counts = tuple(other_values)
                    for other_labels in itertools.product(
                        (0, 1), repeat=len(other_counts)
                    ):
                        U, V, W = pair_constants(
                            other_counts, epsilon, other_labels
                        )
                        record = smoothing_certificate(
                            a, b, epsilon, U, V, W
                        )
                        record["other_counts"] = list(other_counts)
                        record["other_labels"] = list(other_labels)
                        records.append(record)
    return records


def build_global_records(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    registry = protocol["global_allocation_registry"]
    return [
        allocation_census(k + extra, k, parse_fraction(epsilon))
        for k in registry["cycle_lengths"]
        for epsilon in registry["epsilon"]
        for extra in registry["extra_total_trials"]
    ]


def build_compact_records(
    protocol: dict[str, Any]
) -> list[dict[str, Any]]:
    registry = protocol["compact_value_registry"]
    records = []
    for k in registry["cycle_lengths"]:
        for epsilon_text in registry["epsilon"]:
            epsilon = parse_fraction(epsilon_text)
            for extra in registry["extra_total_trials"]:
                total = k + extra
                closed, witnesses = balanced_worst_closed(
                    total, k, epsilon
                )
                exhaustive, endpoint_witnesses = (
                    worst_endpoint_availability(
                        balanced_allocation(total, k), epsilon
                    )
                )
                records.append(
                    {
                        "cycle_length": k,
                        "total_trials": total,
                        "epsilon": fraction_record(epsilon),
                        "closed": fraction_record(closed),
                        "exhaustive": fraction_record(exhaustive),
                        "compact_witnesses": [
                            list(witness) for witness in witnesses
                        ],
                        "endpoint_witness_count": len(
                            endpoint_witnesses
                        ),
                        "matches": closed == exhaustive,
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
                threshold = minimal_total_trials(k, epsilon, target)
                if threshold is None:
                    raise AssertionError("positive interior has no threshold")
                values = [
                    balanced_worst_closed(total, k, epsilon)[0]
                    for total in range(k, threshold + 1)
                ]
                predecessor = (
                    Fraction(0)
                    if threshold == k
                    else values[-2]
                )
                current = values[-1]
                records.append(
                    {
                        "cycle_length": k,
                        "epsilon": fraction_record(epsilon),
                        "delta": fraction_record(delta),
                        "target": fraction_record(target),
                        "minimum_total_trials": threshold,
                        "predecessor": fraction_record(predecessor),
                        "current": fraction_record(current),
                        "straddles": predecessor < target <= current,
                        "traversed_values_monotone": all(
                            left <= right
                            for left, right in zip(values, values[1:])
                        ),
                    }
                )
    return records


def build_boundary_records(
    protocol: dict[str, Any]
) -> dict[str, list[dict[str, Any]]]:
    registry = protocol["negative_boundary_registry"]
    zero = []
    for k in registry["epsilon_zero_cycle_lengths"]:
        total = 3 * k + 5
        counts = balanced_allocation(total, k)
        value, _ = worst_endpoint_availability(counts, Fraction(0))
        zero.append(
            {
                "cycle_length": k,
                "total_trials": total,
                "allocation": list(counts),
                "worst": fraction_record(value),
                "is_zero": value == 0,
            }
        )
    k_two = []
    for epsilon_text in registry["k_two_epsilon"]:
        epsilon = parse_fraction(epsilon_text)
        for total in registry["k_two_totals"]:
            record = allocation_census(total, 2, epsilon)
            k_two.append(
                {
                    "epsilon": fraction_record(epsilon),
                    "total_trials": total,
                    "allocation_count": record["allocation_count"],
                    "optimizer_count": len(record["optimizers"]),
                    "all_allocations_optimal": (
                        len(record["optimizers"])
                        == record["allocation_count"]
                    ),
                }
            )
    return {"epsilon_zero": zero, "k_two": k_two}


def evaluate_gates(
    *,
    protocol: dict[str, Any],
    binding: dict[str, bool],
    pairs: list[dict[str, Any]],
    global_records: list[dict[str, Any]],
    compact: list[dict[str, Any]],
    thresholds: list[dict[str, Any]],
    boundaries: dict[str, list[dict[str, Any]]],
    elapsed_seconds: float,
    peak_bytes: int,
) -> dict[str, bool]:
    pair_keys = {
        (
            row["epsilon"]["fraction"],
            row["a"],
            row["b"],
            tuple(row["other_counts"]),
            tuple(row["other_labels"]),
        )
        for row in pairs
    }
    global_keys = {
        (
            row["cycle_length"],
            row["epsilon"]["fraction"],
            row["total_trials"],
        )
        for row in global_records
    }
    compact_keys = {
        (
            row["cycle_length"],
            row["epsilon"]["fraction"],
            row["total_trials"],
        )
        for row in compact
    }
    threshold_keys = {
        (
            row["cycle_length"],
            row["epsilon"]["fraction"],
            row["delta"]["fraction"],
        )
        for row in thresholds
    }
    caps = protocol["resource_caps"]
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_registry_completeness": (
            len(pairs) == len(pair_keys) == 504
            and len(global_records) == len(global_keys) == 16
            and len(compact) == len(compact_keys) == 12
            and len(thresholds) == len(threshold_keys) == 36
            and len(boundaries["epsilon_zero"]) == 2
            and len(boundaries["k_two"]) == 4
        ),
        "G2_pair_reduction": all(
            row["branch_formula_matches_direct"]
            and row["same_decomposition_holds"]
            and row["opposite_decomposition_holds"]
            for row in pairs
        ),
        "G3_same_branch_smoothing": all(
            row["same_strictly_improves"] for row in pairs
        ),
        "G4_opposite_branch_smoothing": all(
            row["opposite_strictly_improves"]
            and row["minimum_strictly_improves"]
            and row["D_is_invariant"]
            and row["E_is_nondecreasing"]
            and row["pair_products_nondecrease"]
            for row in pairs
        ),
        "G5_global_balanced_optimum": all(
            row["balanced_is_unique_modulo_permutation"]
            and row["all_smoothing_steps_strict"]
            for row in global_records
        ),
        "G6_compact_value_formula": all(
            row["matches"] for row in compact
        ),
        "G7_total_budget_threshold": all(
            row["straddles"] and row["traversed_values_monotone"]
            for row in thresholds
        ),
        "G8_negative_boundaries": (
            all(row["is_zero"] for row in boundaries["epsilon_zero"])
            and all(
                row["all_allocations_optimal"]
                and row["optimizer_count"] > 1
                for row in boundaries["k_two"]
            )
        ),
        "G9_resource_and_scope": (
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
    gate_rows = "\n".join(
        f"- `{name}`: **{'PASS' if passed else 'FAIL'}**"
        for name, passed in result["gates"].items()
    )
    threshold_rows = "\n".join(
        "| {k} | {epsilon} | {target:.6f} | {total} |".format(
            k=row["cycle_length"],
            epsilon=row["epsilon"]["fraction"],
            target=row["target"]["decimal"],
            total=row["minimum_total_trials"],
        )
        for row in result["threshold_records"]
    )
    return f"""# ASMP-9 balanced maximin design v0.16 result

## Verdict

`{result["verdict"]}`

## Gates

{gate_rows}

## Fresh exact cells

- pairwise games: {len(result["pair_records"])}
- global allocation cells: {len(result["global_records"])}
- compact-value cells: {len(result["compact_records"])}
- total-budget thresholds: {len(result["threshold_records"])}
- negative-boundary cells: {result["summary"]["boundary_cell_count"]}

All quantities are exact rational values. Decimals are display aids.

## Exact total-budget thresholds

| `k` | `epsilon` | target | minimum total trials |
| ---: | ---: | ---: | ---: |
{threshold_rows}

## Interpretation

Counts differing by at most one were the unique maximin allocation up to edge
permutation in every fresh global cell. More importantly, the registered
pairwise identities verify the analytic Robin-Hood proof rather than inferring
the theorem from this census.

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
    pairs = build_pair_records(protocol)
    global_records = build_global_records(protocol)
    compact = build_compact_records(protocol)
    thresholds = build_threshold_records(protocol)
    boundaries = build_boundary_records(protocol)
    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    gates = evaluate_gates(
        protocol=protocol,
        binding=binding,
        pairs=pairs,
        global_records=global_records,
        compact=compact,
        thresholds=thresholds,
        boundaries=boundaries,
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
        "pair_records": pairs,
        "global_records": global_records,
        "compact_records": compact,
        "threshold_records": thresholds,
        "boundary_records": boundaries,
        "summary": {
            "pair_cell_count": len(pairs),
            "global_cell_count": len(global_records),
            "compact_cell_count": len(compact),
            "threshold_cell_count": len(thresholds),
            "boundary_cell_count": (
                len(boundaries["epsilon_zero"])
                + len(boundaries["k_two"])
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
    result_path = args.output_dir / "result_v0_16.json"
    report_path = args.output_dir / "RESULT_v0_16.md"
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
    write_json(args.output_dir / "receipt_v0_16.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
