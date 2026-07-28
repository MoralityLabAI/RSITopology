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
from fractions import Fraction

from experiment import (
    run_deterministic_census,
    run_stochastic_cells,
    run_structured_cells,
    run_trajectory_census,
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
    """Return the current process peak resident/working-set size."""
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
        succeeded = psapi.GetProcessMemoryInfo(
            process, ctypes.byref(counters), counters.cb
        )
        if not succeeded:
            raise OSError("GetProcessMemoryInfo failed")
        return int(counters.PeakWorkingSetSize)

    import resource

    maximum = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # Linux reports KiB; macOS reports bytes.
    return maximum if platform.system() == "Darwin" else maximum * 1024


def validate_registration(
    path: Path, registration: dict[str, Any]
) -> tuple[str, dict[str, bool]]:
    relative = path.resolve().relative_to(REPO).as_posix()
    registration_commit = git("log", "-1", "--format=%H", "--", relative)
    checks = {
        "head_is_registration_commit": git("rev-parse", "HEAD")
        == registration_commit,
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
        checks[f"hash:{relative_path}"] = sha256(REPO / relative_path) == expected
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"registration validation failed: {failed!r}")
    return registration_commit, checks


def render_report(result: dict[str, Any]) -> str:
    deterministic = result["deterministic_census"]
    lines = [
        "# ASMP-9 finite-MDP access verification v0.10",
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
            "## Deterministic transition census",
            "",
            f"- kernels: {deterministic['count']}",
            f"- connected successor graphs: {deterministic['connected_count']}",
            "- ambiguity distribution: "
            + json.dumps(deterministic["component_distribution"], sort_keys=True),
            "",
            "## Structured access result",
            "",
            "One entropy-regularized policy leaves S shaping dimensions.",
            "A connected second transition environment or a distinct discount",
            "reduces the common ambiguity to one global constant. The matched",
            "deterministic-policy pair remains nonidentifying.",
            "",
            "## Claim boundary",
            "",
            "Exact finite specialization of established entropy-regularized",
            "IRL identifiability; not finite-sample policy estimation, general",
            "environment design, passive trajectory IRL, or ASMP-9 resolution.",
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

    deterministic = run_deterministic_census(
        protocol["deterministic_census"]
    )
    stochastic = run_stochastic_cells(protocol["stochastic_cells"])
    structured = run_structured_cells(protocol["structured_cells"])
    trajectory = run_trajectory_census(protocol["trajectory_census"])

    deterministic_distribution = {
        int(key): value
        for key, value in deterministic["component_distribution"].items()
    }
    structured_rows = structured["rows"]
    stochastic_states = {
        int(key) for key in stochastic["state_distribution"]
    }
    stochastic_actions = {
        int(key) for key in stochastic["action_distribution"]
    }
    stochastic_discounts = set(stochastic["discount_distribution"])
    expected_states = set(
        range(
            int(protocol["stochastic_cells"]["minimum_states"]),
            int(protocol["stochastic_cells"]["maximum_states"]) + 1,
        )
    )
    expected_actions = set(
        range(
            int(protocol["stochastic_cells"]["minimum_actions"]),
            int(protocol["stochastic_cells"]["maximum_actions"]) + 1,
        )
    )
    expected_discounts = {
        str(Fraction(value))
        for value in protocol["stochastic_cells"]["discounts"]
    }
    elapsed_before_gate = time.perf_counter() - started
    peak_bytes = peak_resident_bytes()
    limits = protocol["resource_limits"]
    gates = {
        "G0_registration_binding": all(binding.values()),
        "G1_stochastic_coverage_and_shaping_injectivity": (
            stochastic["actual_count"]
            == int(protocol["stochastic_cells"]["count"])
            and stochastic_states == expected_states
            and stochastic_actions == expected_actions
            and stochastic_discounts == expected_discounts
            and stochastic["shaping_rank_mismatch_count"] == 0
        ),
        "G2_stochastic_intersection_formula": stochastic[
            "intersection_mismatch_count"
        ]
        == 0,
        "G3_deterministic_component_theorem": (
            deterministic["count"]
            == protocol["deterministic_census"]["expected_count"]
            and deterministic["rank_mismatch_count"] == 0
            and deterministic["intersection_mismatch_count"] == 0
        ),
        "G4_deterministic_liveness": (
            set(deterministic_distribution)
            == set(
                range(1, protocol["deterministic_census"]["state_count"] + 1)
            )
            and deterministic["connected_count"] > 0
            and sum(
                value
                for key, value in deterministic_distribution.items()
                if key > 1
            )
            > 0
        ),
        "G5_transition_discount_threshold": (
            structured["mismatch_count"] == 0
            and all(
                row["single_environment_ambiguity"] == row["state_count"]
                and row["transition_pair_ambiguity"] == 1
                and row["same_discount_pair_ambiguity"]
                == row["state_count"]
                and row["distinct_discount_pair_ambiguity"] == 1
                for row in structured_rows
            )
        ),
        "G6_deterministic_policy_obstruction": all(
            row["deterministic_witness_passed"] for row in structured_rows
        ),
        "G7_trajectory_component_theorem": (
            trajectory["graph_count"]
            == protocol["trajectory_census"]["expected_graph_count"]
            and trajectory["component_mismatch_count"] == 0
        ),
        "G8_trajectory_sharpness": (
            trajectory["minimum_connected_queries"]
            == protocol["trajectory_census"][
                "expected_minimum_connected_queries"
            ]
            and trajectory["connected_by_query_count"].get(
                protocol["trajectory_census"][
                    "expected_minimum_connected_queries"
                ],
                0,
            )
            > 0
        ),
        "G9_access_separation": all(
            row["transition_pair_ambiguity"] == 1
            and row["deterministic_witness_passed"]
            for row in structured_rows
        ),
        "G10_resource_envelope": (
            bool(limits["cpu_only"])
            and elapsed_before_gate <= float(limits["maximum_wall_seconds"])
            and peak_bytes
            <= int(float(limits["maximum_ram_gib"]) * (1024**3))
        ),
    }
    if list(gates) != list(protocol["gate_ids"]):
        raise RuntimeError("runtime gate universe differs from frozen protocol")
    verdict = (
        protocol["success_verdict"]
        if all(gates.values())
        else "finite_mdp_environment_access_geometry_not_verified"
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
            "maximum_wall_seconds": float(
                limits["maximum_wall_seconds"]
            ),
        },
        "binding_checks": binding,
        "deterministic_census": deterministic,
        "stochastic_cells": stochastic,
        "structured_cells": structured,
        "trajectory_census": trajectory,
        "gates": gates,
        "verdict": verdict,
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_10.json"
    report_path = args.output_dir / "RESULT_v0_10.md"
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
    write_json(args.output_dir / "receipt_v0_10.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


if __name__ == "__main__":
    main()
