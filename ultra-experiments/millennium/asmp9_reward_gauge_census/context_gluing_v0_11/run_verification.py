from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Any

from experiment import (
    run_minimality_controls,
    run_random_cells,
    run_tuple_census,
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
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


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
        process = kernel32.GetCurrentProcess()
        if not psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb):
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
        "tracked_tree_clean": not git("status", "--porcelain", "--untracked-files=no"),
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
        checks[f"hash:{relative_path}"] = sha256(REPO / relative_path) == expected
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"registration validation failed: {failed!r}")
    return registration_commit, checks


def render_report(result: dict[str, Any]) -> str:
    census = result["tuple_census"]
    random_cells = result["random_cells"]
    lines = [
        "# ASMP-9 contextual scalar-gluing verification v0.11",
        "",
        f"**Verdict:** `{result['verdict']}`",
        "",
        "## Gates",
        "",
    ]
    for name, passed in result["gates"].items():
        lines.append(f"- **{name}:** {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Exact three-context census",
            "",
            f"- graph tuples: {census['tuple_count']}",
            "- mixed-rank distribution: "
            + json.dumps(census["mixed_cycle_rank_distribution"], sort_keys=True),
            f"- live tuples: {census['live_tuple_count']}",
            "- forced-by-design tuples: " + str(census["forced_by_design_tuple_count"]),
            "",
            "## Seeded decision cells",
            "",
            f"- cells: {random_cells['actual_count']}",
            "- status counts: "
            + json.dumps(random_cells["status_counts"], sort_keys=True),
            "",
            "## Claim boundary",
            "",
            "Exact finite real-valued context-labelled graph theorem; not",
            "ordinal rationalizability, finite-sample preference estimation,",
            "human/model evidence, infinite-history analysis, or ASMP-9",
            "resolution.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(
            f"refusing to overwrite output directory: {args.output_dir}"
        )
    registration_path = args.registration.resolve()
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    started = time.perf_counter()
    registration_commit, binding = validate_registration(
        registration_path, registration
    )

    census = run_tuple_census(protocol["tuple_census"])
    random_cells = run_random_cells(protocol["random_cells"])
    minimality = run_minimality_controls(protocol["minimality_controls"])
    elapsed_before_gate = time.perf_counter() - started
    peak_bytes = peak_resident_bytes()
    limits = protocol["resource_limits"]
    census_ranks = {int(key) for key in census["mixed_cycle_rank_distribution"]}
    expected_ranks = set(protocol["tuple_census"]["expected_mixed_ranks"])
    random_items = {int(key) for key in random_cells["item_distribution"]}
    random_contexts = {int(key) for key in random_cells["context_distribution"]}
    expected_items = set(
        range(
            protocol["random_cells"]["minimum_items"],
            protocol["random_cells"]["maximum_items"] + 1,
        )
    )
    expected_contexts = set(
        range(
            protocol["random_cells"]["minimum_contexts"],
            protocol["random_cells"]["maximum_contexts"] + 1,
        )
    )
    statuses = set(random_cells["status_counts"]) | set(minimality["status_counts"])
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_exact_census": (
            census["tuple_count"] == protocol["tuple_census"]["expected_tuple_count"]
            and census["rank_formula_mismatch_count"] == 0
        ),
        "G2_census_liveness": (
            census_ranks == expected_ranks
            and census["live_tuple_count"] > 0
            and census["forced_by_design_tuple_count"] > 0
        ),
        "G3_seeded_coverage": (
            random_cells["actual_count"] == protocol["random_cells"]["count"]
            and random_items == expected_items
            and random_contexts == expected_contexts
        ),
        "G4_quotient_and_sharpness": (
            random_cells["rank_formula_mismatch_count"] == 0
            and random_cells["basis_dimension_mismatch_count"] == 0
            and random_cells["sharpness_mismatch_count"] == 0
        ),
        "G5_shared_controls": (random_cells["shared_control_mismatch_count"] == 0),
        "G6_nongluing_controls": (
            random_cells["witness_existence_mismatch_count"] == 0
            and random_cells["exact_decision_mismatch_count"] == 0
            and random_cells["status_counts"].get("shared_scalar_refuted", 0) > 0
        ),
        "G7_local_failure_and_status_liveness": (
            random_cells["local_failure_control_count"] > 0
            and random_cells["local_failure_mismatch_count"] == 0
            and statuses == set(protocol["allowed_statuses"])
        ),
        "G8_minimality": (
            minimality["one_item_mismatch_count"] == 0
            and minimality["one_context_mismatch_count"] == 0
            and minimality["minimal_two_item_two_context_witness_passed"]
        ),
        "G9_resource_envelope": (
            bool(limits["cpu_only"])
            and elapsed_before_gate <= limits["maximum_wall_seconds"]
            and peak_bytes <= int(float(limits["maximum_ram_gib"]) * (1024**3))
        ),
    }
    if list(gates) != list(protocol["gate_ids"]):
        raise RuntimeError("runtime gate universe differs from frozen protocol")
    verdict = (
        protocol["success_verdict"]
        if all(gates.values())
        else "finite_contextual_scalar_gluing_geometry_not_verified"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "elapsed_seconds": elapsed_before_gate,
        "resource_observation": {
            "gpu_used": False,
            "peak_resident_bytes": peak_bytes,
            "maximum_ram_bytes": int(float(limits["maximum_ram_gib"]) * (1024**3)),
            "maximum_wall_seconds": limits["maximum_wall_seconds"],
        },
        "binding_checks": binding,
        "tuple_census": census,
        "random_cells": random_cells,
        "minimality_controls": minimality,
        "gates": gates,
        "verdict": verdict,
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_11.json"
    report_path = args.output_dir / "RESULT_v0_11.md"
    write_json(result_path, result)
    write_text(report_path, render_report(result))
    receipt = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "implementation_commit": registration["implementation_commit"],
        "elapsed_seconds": result["elapsed_seconds"],
        "output_hashes": {
            result_path.name: sha256(result_path),
            report_path.name: sha256(report_path),
        },
    }
    write_json(args.output_dir / "receipt_v0_11.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
