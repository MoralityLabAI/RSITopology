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

from experiment import run_fresh_liveness, run_power_calibration


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


def render_report(result: dict[str, Any]) -> str:
    liveness = result["liveness"]
    calibration = result["power_calibration"]
    powers = [
        record["exact_power"]["decimal"] for record in calibration["records"]
    ]
    lines = [
        "# ASMP-9 conditional-fiber quotient verification v0.13",
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
            "## Fresh conditional-fiber census",
            "",
            f"- graphs: {liveness['graph_count']}",
            f"- graph/sample cells: {liveness['cell_count']}",
            "- gauge-factor mismatches: "
            + str(liveness["gauge_factor_mismatch_count"]),
            "- normalized-law mismatches: "
            + str(liveness["normalized_law_mismatch_count"]),
            "- rank-above-cycle-rank mismatches: "
            + str(liveness["rank_upper_mismatch_count"]),
            "",
            "## Fresh conditional-power calibration",
            "",
            f"- cells: {calibration['cell_count']}",
            f"- minimum exact power: {min(powers):.9f}",
            f"- maximum exact power: {max(powers):.9f}",
            "- exact-size mismatches: "
            + str(calibration["size_mismatch_count"]),
            "- formula mismatches: "
            + str(calibration["formula_mismatch_count"]),
            "",
            "The registered sample counts are calibration points, not "
            "monotone critical thresholds.",
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
    liveness = run_fresh_liveness(protocol["fresh_liveness_graphs"])
    calibration = run_power_calibration(protocol["power_calibration"])
    elapsed = time.perf_counter() - started
    peak_bytes = peak_resident_bytes()
    limits = protocol["resource_limits"]
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_graph_arithmetic": (
            liveness["graph_arithmetic_mismatch_count"] == 0
            and liveness["mass_mismatch_count"] == 0
        ),
        "G2_scalar_nuisance_cancellation": (
            liveness["gauge_factor_mismatch_count"] == 0
            and liveness["normalized_law_mismatch_count"] == 0
        ),
        "G3_visible_quotient": (
            liveness["rank_upper_mismatch_count"] == 0
            and liveness["missing_full_rank_graph_count"] == 0
            and liveness["missing_deficient_graph_count"] == 0
        ),
        "G4_nonvacuous_statuses": (
            liveness["zero_full_mass_graph_count"] == 0
            and liveness["zero_deficient_mass_graph_count"] == 0
        ),
        "G5_one_cycle_formula": (
            calibration["formula_mismatch_count"] == 0
        ),
        "G6_exact_conditional_test": (
            calibration["likelihood_ratio_mismatch_count"] == 0
            and calibration["size_mismatch_count"] == 0
            and calibration["nonpositive_power_gain_count"] == 0
        ),
        "G7_fresh_power_calibration": (
            calibration["cell_count"]
            == len(protocol["power_calibration"]["cells"])
            and calibration["power_band_mismatch_count"] == 0
        ),
        "G8_claim_boundary_telemetry": (
            all(
                "full_quotient_mass" in record
                and "deficient_mass" in record
                for record in liveness["records"]
            )
            and all(
                record.get("scope")
                == "conditional_on_zero_vertex_balance"
                for record in calibration["records"]
            )
            and bool(calibration["nonmonotonicity_warning"])
        ),
        "G9_resource_envelope": (
            bool(limits["cpu_only"])
            and elapsed <= limits["maximum_wall_seconds"]
            and peak_bytes
            <= int(float(limits["maximum_ram_gib"]) * (1024**3))
        ),
    }
    if list(gates) != list(protocol["gate_ids"]):
        raise RuntimeError("runtime gate universe differs from protocol")
    verdict = (
        protocol["success_verdict"]
        if all(gates.values())
        else "conditional_fiber_cycle_quotient_not_verified_v0_13"
    )
    result = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "binding_checks": binding,
        "elapsed_seconds": elapsed,
        "resource_observation": {
            "gpu_used": False,
            "peak_resident_bytes": peak_bytes,
            "maximum_ram_bytes": int(
                float(limits["maximum_ram_gib"]) * (1024**3)
            ),
            "maximum_wall_seconds": limits["maximum_wall_seconds"],
        },
        "liveness": liveness,
        "power_calibration": calibration,
        "gates": gates,
        "verdict": verdict,
        "claim_boundary": protocol["claim_boundary"],
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_13.json"
    report_path = args.output_dir / "RESULT_v0_13.md"
    write_json(result_path, result)
    write_text(report_path, render_report(result))
    receipt = {
        "protocol_id": protocol["protocol_id"],
        "registration_commit": registration_commit,
        "registration_sha256": sha256(registration_path),
        "implementation_commit": registration["implementation_commit"],
        "elapsed_seconds": elapsed,
        "output_hashes": {
            result_path.name: sha256(result_path),
            report_path.name: sha256(report_path),
        },
    }
    write_json(args.output_dir / "receipt_v0_13.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
