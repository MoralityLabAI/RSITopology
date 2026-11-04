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

from offset_access import (
    bounded_error_patterns,
    ceil_log2_fraction,
    flat_link_sup_deviation,
    hoeffding_samples_per_query,
    no_offset_matching_laws,
    no_offset_nonaffine_witness,
    population_bisection,
    population_query_upper_bound,
    rational_link_margin_constant,
    restricted_offset_witness,
    restricted_transcript,
    robust_bisection_with_bounded_probability_error,
    volume_query_lower_bound,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

EXPECTED_ALLOWED = [
    "A known additive-offset channel spanning every admissible indifference "
    "threshold identifies the anchored finite utility vector uniformly over "
    "strictly increasing symmetric links.",
    "The population midpoint-sign query count is sharp on the registered "
    "dyadic cells under the declared coordinate-threshold access grammar.",
    "A restricted offset range leaves a positive minimax error even with "
    "unlimited population queries.",
    "Finite-sample recovery has the registered conservative guarantee under "
    "a known margin envelope, while no uniform finite-sample rate exists over "
    "arbitrarily flat admissible links.",
    "The construction is a conservative specialization of classical "
    "choice-indifference elicitation, bisection, active learning, and "
    "stochastic root finding; no novelty is registered.",
]
EXPECTED_FORBIDDEN = [
    "Ordinary uncalibrated human preference comparisons reveal cardinal "
    "utility scale.",
    "Every environment intervention implements the declared additive offset "
    "in latent reward units.",
    "The result covers context-dependent, item-dependent, nonmonotone, or "
    "midpoint-shifted response links.",
    "The finite-sample upper bound is minimax or has optimal constants.",
    "The result identifies arbitrary MDP rewards from policy behavior or "
    "solves general inverse reinforcement learning.",
    "Classical bisection, willingness-to-pay, choice-indifference, "
    "active-learning, or stochastic-root-finding results are new.",
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
    return {"denominator": value.denominator, "numerator": value.numerator}


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

    fresh = protocol["fresh_validation"]
    burned = protocol["freshness_rule"]["burned_cells"]
    population_pairs = {
        (cell["radius"], cell["tolerance"])
        for cell in fresh["population_cells"]
    }
    robust_pairs = {
        (cell["radius"], cell["tolerance"]) for cell in fresh["robust_cells"]
    }
    restricted_pairs = {
        (cell["radius"], cell["maximum_offset"])
        for cell in fresh["restricted_cells"]
    }
    structure_pass = (
        not population_pairs
        & {
            (cell["radius"], cell["tolerance"])
            for cell in burned["population"]
        }
        and not robust_pairs
        & {
            (cell["radius"], cell["tolerance"])
            for cell in burned["robust"]
        }
        and not restricted_pairs
        & {
            (cell["radius"], cell["maximum_offset"])
            for cell in burned["restricted"]
        }
        and all(
            Fraction(cell["maximum_offset"]) < Fraction(cell["radius"])
            for cell in fresh["restricted_cells"]
        )
    )
    gates["G1_freshness_and_structure"] = {
        "fresh_population_cells": len(population_pairs),
        "fresh_restricted_cells": len(restricted_pairs),
        "fresh_robust_cells": len(robust_pairs),
        "pass": structure_pass,
    }

    population_rows: list[dict[str, Any]] = []
    for cell in fresh["population_cells"]:
        radius = Fraction(cell["radius"])
        tolerance = Fraction(cell["tolerance"])
        denominator = int(cell["denominator"])
        limit = int(radius * denominator)
        maximum_error = Fraction(0)
        maximum_queries = 0
        checked = 0
        for numerator in range(-limit, limit + 1):
            receipt = population_bisection(
                Fraction(numerator, denominator), radius, tolerance
            )
            maximum_error = max(maximum_error, receipt.absolute_error)
            maximum_queries = max(maximum_queries, receipt.query_count)
            checked += 1
        bound = ceil_log2_fraction(radius / tolerance)
        population_rows.append(
            {
                "checked_gap_count": checked,
                "maximum_absolute_error": fraction_record(maximum_error),
                "maximum_query_count": maximum_queries,
                "name": cell["name"],
                "pass": maximum_error <= tolerance and maximum_queries <= bound,
                "registered_query_bound": bound,
            }
        )
    gates["G2_population_recovery"] = {
        "pass": all(row["pass"] for row in population_rows),
        "total_gap_count": sum(
            row["checked_gap_count"] for row in population_rows
        ),
    }

    dyadic_rows: list[dict[str, Any]] = []
    for cell in fresh["dyadic_cells"]:
        dimension = int(cell["dimension"])
        radius = Fraction(cell["radius"])
        tolerance = Fraction(cell["tolerance"])
        upper = population_query_upper_bound(dimension, radius, tolerance)
        lower = volume_query_lower_bound(dimension, radius, tolerance)
        dyadic_rows.append(
            {
                "dimension": dimension,
                "lower_bound": lower,
                "name": cell["name"],
                "pass": lower == upper,
                "upper_bound": upper,
            }
        )
    gates["G3_sharp_dyadic_query_bound"] = {
        "pass": all(row["pass"] for row in dyadic_rows)
    }

    restricted_rows: list[dict[str, Any]] = []
    for cell in fresh["restricted_cells"]:
        radius = Fraction(cell["radius"])
        ceiling = Fraction(cell["maximum_offset"])
        denominator = int(cell["grid_denominator"])
        first, second = restricted_offset_witness(radius, ceiling)
        limit = int(ceiling * denominator)
        offsets = [
            Fraction(value, denominator) for value in range(-limit, limit + 1)
        ]
        first_transcript = restricted_transcript(first, offsets)
        second_transcript = restricted_transcript(second, offsets)
        minimax_error = abs(first - second) / 2
        restricted_rows.append(
            {
                "first_gap": fraction_record(first),
                "grid_query_count": len(offsets),
                "minimax_error_lower_bound": fraction_record(minimax_error),
                "name": cell["name"],
                "pass": (
                    first_transcript == second_transcript
                    and set(first_transcript) == {1}
                    and minimax_error > 0
                ),
                "second_gap": fraction_record(second),
            }
        )
    gates["G4_restricted_offset_obstruction"] = {
        "pass": all(row["pass"] for row in restricted_rows)
    }

    robust_rows: list[dict[str, Any]] = []
    for cell in fresh["robust_cells"]:
        radius = Fraction(cell["radius"])
        tolerance = Fraction(cell["tolerance"])
        denominator = int(cell["gap_denominator"])
        rounds = ceil_log2_fraction(radius / tolerance)
        error_bound = rational_link_margin_constant(radius) * tolerance / 2
        limit = int(radius * denominator)
        checked = 0
        maximum_error = Fraction(0)
        for numerator in range(-limit, limit + 1):
            gap = Fraction(numerator, denominator)
            for errors in bounded_error_patterns(rounds, error_bound):
                receipt = robust_bisection_with_bounded_probability_error(
                    gap, radius, tolerance, errors
                )
                maximum_error = max(maximum_error, receipt.absolute_error)
                checked += 1
        robust_rows.append(
            {
                "checked_paths": checked,
                "error_bound": fraction_record(error_bound),
                "maximum_absolute_error": fraction_record(maximum_error),
                "name": cell["name"],
                "pass": maximum_error <= tolerance,
                "rounds": rounds,
            }
        )
    gates["G5_bounded_error_finite_sample_rule"] = {
        "pass": all(row["pass"] for row in robust_rows),
        "total_checked_paths": sum(row["checked_paths"] for row in robust_rows),
    }

    flat_cell = fresh["flat_link_cell"]
    flat_radius = Fraction(flat_cell["radius"])
    deviations = [
        flat_link_sup_deviation(flat_radius, Fraction(1, 2**power))
        for power in range(
            int(flat_cell["minimum_power"]),
            int(flat_cell["maximum_power"]) + 1,
        )
    ]
    flat_pass = (
        all(left > right for left, right in zip(deviations, deviations[1:]))
        and deviations[-1] < Fraction(flat_cell["final_ceiling"])
    )
    flat_row = {
        "deviations": [fraction_record(value) for value in deviations],
        "final_ceiling": fraction_record(
            Fraction(flat_cell["final_ceiling"])
        ),
        "pass": flat_pass,
    }
    gates["G6_flat_link_no_uniform_rate"] = {"pass": flat_pass}

    no_offset_laws = no_offset_matching_laws()
    no_offset_witness = no_offset_nonaffine_witness()
    source, target = no_offset_witness["source"], no_offset_witness["target"]
    affine = (
        source[1] - source[0] == target[1] - target[0]
        and source[2] == target[2]
    )
    no_offset_pass = (
        bool(no_offset_laws["same_law"])
        and bool(no_offset_laws["admissible_target_knots"])
        and not affine
    )
    no_offset_row = {
        "admissible_target_knots": no_offset_laws[
            "admissible_target_knots"
        ],
        "positive_affine_equivalent": affine,
        "same_population_law": no_offset_laws["same_law"],
    }
    gates["G7_no_offset_control"] = {"pass": no_offset_pass}

    sample_rows: list[dict[str, Any]] = []
    for cell in fresh["sample_bound_cells"]:
        dimension = int(cell["dimension"])
        radius = Fraction(str(cell["radius"]))
        tolerance = Fraction(str(cell["tolerance"]))
        query_count = population_query_upper_bound(
            dimension, radius, tolerance
        )
        repeats = hoeffding_samples_per_query(
            float(cell["kappa"]),
            float(cell["tolerance"]),
            float(cell["exponent"]),
            float(cell["failure_probability"]),
            query_count,
        )
        estimation_error = (
            float(cell["kappa"])
            * float(cell["tolerance"]) ** float(cell["exponent"])
            / 2
        )
        union_failure_bound = (
            2
            * query_count
            * __import__("math").exp(
                -2 * repeats * estimation_error**2
            )
        )
        sample_rows.append(
            {
                "name": cell["name"],
                "pass": (
                    repeats > 0
                    and union_failure_bound
                    <= float(cell["failure_probability"])
                ),
                "population_query_count": query_count,
                "repeats_per_query": repeats,
                "union_failure_bound": union_failure_bound,
            }
        )
    gates["G8_sample_certificate"] = {
        "pass": all(row["pass"] for row in sample_rows)
    }

    prior_text = (HERE / "PRIOR_ART_GATE_v0_26.md").read_text(
        encoding="utf-8"
    )
    claims_pass = (
        protocol["structured_claims"]["allowed"] == EXPECTED_ALLOWED
        and protocol["structured_claims"]["forbidden"] == EXPECTED_FORBIDDEN
        and "choice-indifference" in prior_text
        and "no novelty claim" in prior_text.lower()
        and "known reward-unit intervention" in protocol["claim_boundary"]
    )
    gates["G9_prior_art_and_claim_boundary"] = {"pass": claims_pass}

    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    caps = protocol["resource_caps"]
    resource_pass = (
        not caps["gpu_allowed"]
        and elapsed <= float(caps["wall_seconds"])
        and peak <= int(caps["peak_resident_bytes"])
    )
    gates["G10_resource_and_scope"] = {
        "gpu_used": False,
        "pass": resource_pass,
        "peak_resident_bytes": peak,
        "wall_seconds": elapsed,
    }

    gate_passes = {name: bool(record["pass"]) for name, record in gates.items()}
    if all(gate_passes.values()):
        verdict = protocol["verdict_map"]["all_gates_pass"]
    elif not gate_passes["G0_registration_binding"] or not gate_passes[
        "G10_resource_and_scope"
    ]:
        verdict = protocol["verdict_map"]["binding_or_resource_gate_fails"]
    else:
        verdict = protocol["verdict_map"]["any_substantive_gate_fails"]

    result = {
        "dyadic_rows": dyadic_rows,
        "flat_row": flat_row,
        "gate_passes": gate_passes,
        "gates": gates,
        "no_offset_row": no_offset_row,
        "population_rows": population_rows,
        "protocol_id": protocol["protocol_id"],
        "registration_sha256": registration_sha,
        "restricted_rows": restricted_rows,
        "robust_rows": robust_rows,
        "sample_rows": sample_rows,
        "verdict": verdict,
    }
    output_dir.mkdir(parents=True)
    result_path = output_dir / "result_v0_26.json"
    receipt_path = output_dir / "run_receipt_v0_26.json"
    write_json_exclusive(result_path, result)
    receipt = {
        "finished_at_utc": utc_now(),
        "implementation_commit": registration["implementation_commit"],
        "peak_resident_bytes": peak,
        "protocol_sha256": sha256(REPO / registration["protocol_path"]),
        "registration_sha256": registration_sha,
        "result_sha256": sha256(result_path),
        "run_commit": git("rev-parse", "HEAD"),
        "started_at_utc": started_at,
        "wall_seconds": elapsed,
    }
    write_json_exclusive(receipt_path, receipt)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
