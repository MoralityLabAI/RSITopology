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

from experiment import fraction_record, parse_fraction, run_registry


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


def summarize_records(
    records: list[dict[str, Any]],
    *,
    alpha: Fraction,
    balanced_nuisance: str,
    extreme_nuisance: str,
    interior_nuisance: str,
    interior_epsilon: Fraction,
    ratio_ceiling: Fraction,
) -> dict[str, Any]:
    null_records = [
        record for record in records if record["odds_ratio"] == "1/1"
    ]
    positive_records = [
        record for record in records if record["odds_ratio"] != "1/1"
    ]
    interior_records = [
        record
        for record in positive_records
        if record["nuisance_ratio"] == interior_nuisance
    ]
    interior_checks = []
    for record in interior_records:
        k = int(record["cycle_length"])
        n = int(record["trials_per_edge"])
        availability_floor = (
            1 - (1 - interior_epsilon) ** n
        ) ** k
        minimum_gain = parse_fraction(
            record["minimum_informative_power_gain"]["fraction"]
        )
        excess = parse_fraction(record["excess_power"]["fraction"])
        fixed_lower_bound = availability_floor * minimum_gain
        actual_epsilon = parse_fraction(
            record["epsilon_actual"]["fraction"]
        )
        interior_checks.append(
            {
                "cycle_length": k,
                "trials_per_edge": n,
                "odds_ratio": record["odds_ratio"],
                "nuisance_ratio": record["nuisance_ratio"],
                "declared_epsilon": fraction_record(interior_epsilon),
                "actual_epsilon": record["epsilon_actual"],
                "fixed_availability_lower_bound": fraction_record(
                    availability_floor
                ),
                "minimum_informative_power_gain": record[
                    "minimum_informative_power_gain"
                ],
                "fixed_excess_lower_bound": fraction_record(
                    fixed_lower_bound
                ),
                "epsilon_floor_holds": (
                    actual_epsilon >= interior_epsilon
                ),
                "positive_bound_holds": (
                    0 < fixed_lower_bound <= excess
                ),
            }
        )
    grouped: dict[tuple[int, int, str], dict[str, dict[str, Any]]] = {}
    for record in positive_records:
        key = (
            record["cycle_length"],
            record["trials_per_edge"],
            record["odds_ratio"],
        )
        grouped.setdefault(key, {})[record["nuisance_ratio"]] = record
    endpoint_pairs = []
    for key, by_nuisance in sorted(grouped.items()):
        balanced = by_nuisance[balanced_nuisance]
        extreme = by_nuisance[extreme_nuisance]
        balanced_excess = parse_fraction(
            balanced["excess_power"]["fraction"]
        )
        extreme_excess = parse_fraction(
            extreme["excess_power"]["fraction"]
        )
        endpoint_pairs.append(
            {
                "cycle_length": key[0],
                "trials_per_edge": key[1],
                "odds_ratio": key[2],
                "balanced_availability": balanced[
                    "availability_alternative"
                ],
                "extreme_availability": extreme[
                    "availability_alternative"
                ],
                "balanced_excess_power": balanced["excess_power"],
                "extreme_excess_power": extreme["excess_power"],
                "excess_ratio_below_ceiling": (
                    extreme_excess
                    < ratio_ceiling * balanced_excess
                ),
                "availability_strictly_lower": (
                    parse_fraction(
                        extreme["availability_alternative"]["fraction"]
                    )
                    < parse_fraction(
                        balanced["availability_alternative"]["fraction"]
                    )
                ),
                "excess_strictly_lower": (
                    extreme_excess < balanced_excess
                ),
                "ratio_decimal": float(
                    extreme_excess / balanced_excess
                ),
            }
        )
    return {
        "null_cell_count": len(null_records),
        "positive_cell_count": len(positive_records),
        "interior_control_count": len(interior_checks),
        "interior_checks": interior_checks,
        "endpoint_pairs": endpoint_pairs,
        "null_control_mismatch_count": sum(
            record["unconditional_power_all"]["fraction"]
            != f"{alpha.numerator}/{alpha.denominator}"
            or record["excess_power"]["fraction"] != "0/1"
            or record["minimum_informative_power_gain"]["fraction"]
            != "0/1"
            for record in null_records
        ),
        "nonpositive_excess_count": sum(
            record["excess_power"]["decimal"] <= 0
            for record in positive_records
        ),
        "nonpositive_interior_bound_count": sum(
            record["epsilon_actual"]["decimal"] <= 0
            or record["minimum_informative_power_gain"]["decimal"] <= 0
            or record["excess_interior_lower_bound"]["decimal"] <= 0
            for record in positive_records
        ),
        "fixed_interior_mismatch_count": sum(
            not check["epsilon_floor_holds"]
            or not check["positive_bound_holds"]
            for check in interior_checks
        ),
        "endpoint_collapse_mismatch_count": sum(
            not pair["availability_strictly_lower"]
            or not pair["excess_strictly_lower"]
            or not pair["excess_ratio_below_ceiling"]
            for pair in endpoint_pairs
        ),
        "maximum_endpoint_ratio": max(
            pair["ratio_decimal"] for pair in endpoint_pairs
        ),
    }


def evaluate_scientific_gates(
    registry: dict[str, Any],
    summary: dict[str, Any],
    protocol: dict[str, Any],
) -> dict[str, bool]:
    expected_cells = math_product(
        len(protocol["fresh_registry"][name])
        for name in (
            "cycle_lengths",
            "trials_per_edge",
            "odds_ratios",
            "nuisance_ratios",
        )
    )
    return {
        "G1_fiber_partition_and_mass": (
            registry["cell_count"] == expected_cells
            and registry["mass_normalization_mismatch_count"] == 0
            and all(
                record["fiber_count"] > 0
                and record["informative_fiber_count"] > 0
                for record in registry["records"]
            )
        ),
        "G2_availability_formula": (
            registry["availability_formula_mismatch_count"] == 0
        ),
        "G3_exact_conditional_size": (
            registry["conditional_size_mismatch_count"] == 0
        ),
        "G4_excess_factorization": (
            registry["excess_decomposition_mismatch_count"] == 0
        ),
        "G5_no_go_upper_bound": (
            registry["upper_bound_mismatch_count"] == 0
            and summary["nonpositive_excess_count"] == 0
        ),
        "G6_interior_sufficiency": (
            registry["interior_lower_bound_mismatch_count"] == 0
            and summary["nonpositive_interior_bound_count"] == 0
            and summary["interior_control_count"] > 0
            and summary["fixed_interior_mismatch_count"] == 0
        ),
        "G7_null_control": (
            summary["null_cell_count"] > 0
            and summary["null_control_mismatch_count"] == 0
        ),
        "G8_extreme_nuisance_collapse": (
            len(summary["endpoint_pairs"]) > 0
            and summary["endpoint_collapse_mismatch_count"] == 0
        ),
    }


def render_report(result: dict[str, Any]) -> str:
    registry = result["registry"]
    summary = result["summary"]
    powers = [
        record["unconditional_power_all"]["decimal"]
        for record in registry["records"]
        if record["odds_ratio"] != "1/1"
    ]
    lines = [
        "# ASMP-9 unconditional availability verification v0.14",
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
            "## Fresh exact registry",
            "",
            f"- cells: {registry['cell_count']}",
            f"- null controls: {summary['null_cell_count']}",
            f"- positive-alternative cells: {summary['positive_cell_count']}",
            "- fixed-interior positive controls: "
            + str(summary["interior_control_count"]),
            "- fixed-interior mismatches: "
            + str(summary["fixed_interior_mismatch_count"]),
            "- availability-formula mismatches: "
            + str(registry["availability_formula_mismatch_count"]),
            "- mass-normalization mismatches: "
            + str(registry["mass_normalization_mismatch_count"]),
            "- excess-factorization mismatches: "
            + str(registry["excess_decomposition_mismatch_count"]),
            "- interior-bound mismatches: "
            + str(registry["interior_lower_bound_mismatch_count"]),
            "- maximum extreme/balanced excess ratio: "
            + f"{summary['maximum_endpoint_ratio']:.12g}",
            "- positive-alternative unconditional power range: "
            + f"[{min(powers):.9f}, {max(powers):.9f}]",
            "",
            "Conditional exactness is preserved at every nuisance value. "
            "The registered collapse is entirely an unconditional "
            "availability effect.",
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
    registry = run_registry(protocol["fresh_registry"])
    summary = summarize_records(
        registry["records"],
        alpha=parse_fraction(protocol["fresh_registry"]["alpha"]),
        balanced_nuisance=protocol["balanced_nuisance_ratio"],
        extreme_nuisance=protocol["extreme_nuisance_ratio"],
        interior_nuisance=protocol["interior_nuisance_ratio"],
        interior_epsilon=parse_fraction(
            protocol["interior_probability_floor"]
        ),
        ratio_ceiling=parse_fraction(
            protocol["maximum_extreme_to_balanced_excess_ratio"]
        ),
    )
    elapsed = time.perf_counter() - started
    peak_bytes = peak_resident_bytes()
    limits = protocol["resource_limits"]
    scientific_gates = evaluate_scientific_gates(
        registry, summary, protocol
    )
    gates = {
        "G0_registration_binding": all(binding.values()),
        **scientific_gates,
        "G9_resource_and_scope": (
            bool(limits["cpu_only"])
            and elapsed <= limits["maximum_wall_seconds"]
            and peak_bytes
            <= int(float(limits["maximum_ram_gib"]) * (1024**3))
            and bool(protocol["claim_boundary"])
        ),
    }
    if list(gates) != list(protocol["gate_ids"]):
        raise RuntimeError("runtime gate universe differs from protocol")
    verdict = (
        protocol["success_verdict"]
        if all(gates.values())
        else "unconditional_nuisance_frontier_not_verified_v0_14"
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
        "registry": registry,
        "summary": summary,
        "gates": gates,
        "verdict": verdict,
        "claim_boundary": protocol["claim_boundary"],
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result_v0_14.json"
    report_path = args.output_dir / "RESULT_v0_14.md"
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
    write_json(args.output_dir / "receipt_v0_14.json", receipt)
    print(json.dumps({"gates": gates, "verdict": verdict}, indent=2))
    raise SystemExit(0 if all(gates.values()) else 1)


def math_product(values: Any) -> int:
    result = 1
    for value in values:
        result *= int(value)
    return result


if __name__ == "__main__":
    main()
