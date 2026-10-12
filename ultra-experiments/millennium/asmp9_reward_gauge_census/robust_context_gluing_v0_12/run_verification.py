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

from experiment import run_exact_witness, run_fresh_cells


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
        if not psapi.GetProcessMemoryInfo(
            process, ctypes.byref(counters), counters.cb
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


def render_report(result: dict[str, Any]) -> str:
    fresh = result["fresh_cells"]
    lines = [
        "# ASMP-9 robust contextual scalar-gluing verification v0.12",
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
            "## Exact conditioning witness",
            "",
            "- obstruction dimension: "
            + str(
                result["exact_witness"]["certificate"][
                    "obstruction_dimension"
                ]
            ),
            "- shortest amplification squared: "
            + result["exact_witness"]["certificate"][
                "short_amplification_squared"
            ],
            "- robust amplification squared: "
            + result["exact_witness"]["certificate"][
                "robust_amplification_squared"
            ],
            "",
            "## Fresh five-item cells",
            "",
            f"- cells: {fresh['actual_count']}",
            "- obstruction dimensions: "
            + json.dumps(fresh["dimension_distribution"], sort_keys=True),
            "- conditioning-suboptimal shortest bases: "
            + str(fresh["shortest_suboptimal_count"]),
            "- maximum amplification ratio: "
            + f"{fresh['maximum_amplification_ratio']:.9f}",
            "",
            "## Claim boundary",
            "",
            result["claim_boundary"],
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
    exact = run_exact_witness()
    fresh = run_fresh_cells(protocol["fresh_cells"])
    elapsed_before_gate = time.perf_counter() - started
    peak_bytes = peak_resident_bytes()
    limits = protocol["resource_limits"]
    observed_dimensions = {
        int(value) for value in fresh["dimension_distribution"]
    }
    expected_dimensions = set(
        protocol["fresh_cells"]["expected_obstruction_dimensions"]
    )
    exact_protocol = protocol["exact_witness"]
    certificate = exact["certificate"]
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_exact_counterexample": (
            exact["exact_match"]
            and certificate["item_count"] == exact_protocol["item_count"]
            and certificate["context_count"]
            == exact_protocol["context_count"]
            and certificate["obstruction_dimension"]
            == exact_protocol["expected_obstruction_dimension"]
            and certificate["short_amplification_squared"]
            == exact_protocol["expected_short_amplification_squared"]
            and certificate["robust_amplification_squared"]
            == exact_protocol["expected_robust_amplification_squared"]
        ),
        "G2_nested_geometry": (
            fresh["dimension_mismatch_count"] == 0
            and fresh["pythagorean_mismatch_count"] == 0
            and fresh["shared_control_mismatch_count"] == 0
            and fresh["local_projection_mismatch_count"] == 0
            and fresh["locally_scalar_gluing_positive_count"] > 0
        ),
        "G3_exact_repair_radius": (
            fresh["radius_optimality_mismatch_count"] == 0
        ),
        "G4_query_count_lower_bound": (
            fresh["underquery_mismatch_count"] == 0
        ),
        "G5_orthonormal_optimum": (
            fresh["orthonormal_mismatch_count"] == 0
            and fresh["normalized_bound_mismatch_count"] == 0
        ),
        "G6_fresh_coverage": (
            fresh["actual_count"] == protocol["fresh_cells"]["count"]
            and observed_dimensions == expected_dimensions
        ),
        "G7_simple_cycle_basis": (
            fresh["cycle_basis_mismatch_count"] == 0
        ),
        "G8_conditioning_separation_liveness": (
            fresh["shortest_suboptimal_count"] > 0
            and fresh["maximum_amplification_ratio"] > 1.0
        ),
        "G9_resource_envelope": (
            bool(limits["cpu_only"])
            and elapsed_before_gate <= limits["maximum_wall_seconds"]
            and peak_bytes
            <= int(float(limits["maximum_ram_gib"]) * (1024**3))
        ),
    }
    if list(gates) != list(protocol["gate_ids"]):
        raise RuntimeError("runtime gate universe differs from protocol")
    verdict = (
        protocol["success_verdict"]
        if all(gates.values())
        else "robust_context_gluing_geometry_not_verified_v0_12"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "elapsed_seconds": elapsed_before_gate,
        "resource_observation": {
            "gpu_used": False,
            "peak_resident_bytes": peak_bytes,
            "maximum_ram_bytes": int(
                float(limits["maximum_ram_gib"]) * (1024**3)
            ),
            "maximum_wall_seconds": limits["maximum_wall_seconds"],
        },
        "binding_checks": binding,
        "exact_witness": exact,
        "fresh_cells": fresh,
        "gates": gates,
        "verdict": verdict,
        "claim_boundary": protocol["claim_boundary"],
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_12.json"
    report_path = args.output_dir / "RESULT_v0_12.md"
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
    write_json(args.output_dir / "receipt_v0_12.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
