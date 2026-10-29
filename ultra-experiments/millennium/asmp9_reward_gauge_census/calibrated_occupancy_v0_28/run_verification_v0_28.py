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
from math import ceil, log2
from pathlib import Path
from typing import Any

from linear_access import (
    adaptive_transcript_law,
    calibrated_bisect,
    dot,
    known_numeraire_law,
    mdp_query_occupancy_difference,
    population_law,
    q,
    quotient_identifiable,
    quotient_stability,
    rational_rank,
    realize_integer_occupancy_mdp,
    scaled_population_law,
    scaled_reward_known_numeraire_law,
    scaled_unknown_numeraire_law,
    unknown_numeraire_law,
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


def fraction_vector(values):
    return tuple(Fraction(value) for value in values)


def integer_matrix(values):
    return tuple(tuple(int(entry) for entry in row) for row in values)


def fraction_matrix(values):
    return tuple(tuple(Fraction(str(entry)) for entry in row) for row in values)


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

    homogeneous_rows = []
    homogeneous_pass = True
    adaptive_pass = True
    total_transcripts = 0
    for cell in fresh["homogeneous_cells"]:
        matrix = integer_matrix(cell["matrix"])
        reward = fraction_vector(cell["reward"])
        baseline = population_law(matrix, reward)
        cell_law_pass = True
        cell_adaptive_pass = True
        transcript_count = 0

        def policy(history, row_count=len(matrix)):
            score = len(history) + sum(
                (index + 2) * bit for index, bit in enumerate(history)
            )
            return score % row_count

        baseline_transcripts = adaptive_transcript_law(
            matrix, reward, int(cell["adaptive_depth"]), policy
        )
        for alpha_string in cell["scale_factors"]:
            alpha = Fraction(alpha_string)
            cell_law_pass &= baseline == scaled_population_law(
                matrix, reward, alpha
            )
            scaled_reward = tuple(alpha * value for value in reward)
            scaled_transcripts = adaptive_transcript_law(
                matrix,
                scaled_reward,
                int(cell["adaptive_depth"]),
                policy,
                alpha=alpha,
            )
            cell_adaptive_pass &= (
                baseline_transcripts == scaled_transcripts
            )
            transcript_count += len(scaled_transcripts)
        homogeneous_pass &= cell_law_pass
        adaptive_pass &= cell_adaptive_pass
        total_transcripts += transcript_count
        homogeneous_rows.append(
            {
                "adaptive_depth": int(cell["adaptive_depth"]),
                "adaptive_pass": cell_adaptive_pass,
                "law_pass": cell_law_pass,
                "name": cell["name"],
                "transcript_count": transcript_count,
            }
        )
    gates["G1_homogeneous_scale_obstruction"] = {
        "pass": homogeneous_pass,
        "row_count": len(homogeneous_rows),
    }
    gates["G2_adaptive_scale_obstruction"] = {
        "pass": adaptive_pass,
        "total_transcripts": total_transcripts,
    }

    unknown = fresh["unknown_numeraire_cell"]
    unknown_matrix = integer_matrix(unknown["matrix"])
    unknown_reward = fraction_vector(unknown["reward"])
    unknown_offsets = fraction_vector(unknown["offsets"])
    coefficient = Fraction(unknown["coefficient"])
    unknown_baseline = unknown_numeraire_law(
        unknown_matrix, unknown_reward, unknown_offsets, coefficient
    )
    unknown_matches = []
    for alpha_string in unknown["scale_factors"]:
        alpha = Fraction(alpha_string)
        unknown_matches.append(
            unknown_baseline
            == scaled_unknown_numeraire_law(
                unknown_matrix,
                unknown_reward,
                unknown_offsets,
                coefficient,
                alpha,
            )
        )
    gates["G3_unknown_numeraire_control"] = {
        "pass": all(unknown_matches),
        "scale_checks": len(unknown_matches),
    }

    calibrated = fresh["calibrated_numeraire_cell"]
    calibrated_matrix = integer_matrix(calibrated["matrix"])
    calibrated_reward = fraction_vector(calibrated["reward"])
    calibrated_offsets = fraction_vector(calibrated["offsets"])
    calibrated_baseline = known_numeraire_law(
        calibrated_matrix, calibrated_reward, calibrated_offsets
    )
    scale_breaks = []
    for alpha_string in calibrated["scale_factors"]:
        alpha = Fraction(alpha_string)
        scale_breaks.append(
            calibrated_baseline
            != scaled_reward_known_numeraire_law(
                calibrated_matrix,
                calibrated_reward,
                calibrated_offsets,
                alpha,
            )
        )
    radius = Fraction(calibrated["radius"])
    tolerance = Fraction(calibrated["tolerance"])
    maximum_error = Fraction(0)
    maximum_queries = 0
    for row in calibrated_matrix:
        target = dot(row, calibrated_reward)
        estimate, queries = calibrated_bisect(target, radius, tolerance)
        maximum_error = max(maximum_error, abs(estimate - target))
        maximum_queries = max(maximum_queries, queries)
    query_bound = max(0, ceil(log2(float(radius / tolerance))))
    calibrated_pass = (
        all(scale_breaks)
        and maximum_error <= tolerance
        and maximum_queries <= query_bound
    )
    gates["G4_calibrated_numeraire"] = {
        "maximum_localization_error": str(maximum_error),
        "maximum_queries": maximum_queries,
        "pass": calibrated_pass,
        "scale_break_checks": len(scale_breaks),
    }

    mdp_rows = []
    mdp_pass = True
    matrices = [
        (cell["name"], integer_matrix(cell["matrix"]))
        for cell in fresh["homogeneous_cells"]
    ] + [
        ("unknown_numeraire", unknown_matrix),
        ("calibrated_numeraire", calibrated_matrix),
    ]
    for name, matrix in matrices:
        mdp = realize_integer_occupancy_mdp(matrix)
        realized = tuple(
            mdp_query_occupancy_difference(mdp, query_index)
            for query_index in range(len(mdp.queries))
        )
        horizons = {query.horizon for query in mdp.queries}
        row_pass = (
            realized == matrix
            and len(horizons) == 1
            and len(mdp.transitions)
            == 2 * len(mdp.queries) * next(iter(horizons))
        )
        mdp_pass &= row_pass
        mdp_rows.append(
            {
                "fixed_horizon": next(iter(horizons)),
                "name": name,
                "pass": row_pass,
                "query_initial_states": len(mdp.queries),
                "state_count": len(mdp.states),
                "transition_count": len(mdp.transitions),
            }
        )
    gates["G5_finite_mdp_realization"] = {
        "pass": mdp_pass,
        "row_count": len(mdp_rows),
    }

    quotient_rows = []
    quotient_pass = True
    for cell in fresh["quotient_cells"]:
        matrix = fraction_matrix(cell["matrix"])
        gauge = fraction_matrix(cell["gauge_basis"])
        result = quotient_identifiable(matrix, gauge)
        row_pass = (
            result["measurement_rank"] == int(cell["expected_rank"])
            and result["identifiable_modulo_gauge"]
            is bool(cell["expected_identifiable"])
        )
        witness_pass = True
        if "non_gauge_kernel_witness" in cell:
            witness = fraction_vector(cell["non_gauge_kernel_witness"])
            witness_in_kernel = all(dot(row, witness) == 0 for row in matrix)
            gauge_rank = rational_rank(gauge)
            augmented_rank = rational_rank(tuple(gauge) + (witness,))
            witness_pass = (
                witness_in_kernel and augmented_rank == gauge_rank + 1
            )
            row_pass &= witness_pass
        quotient_pass &= row_pass
        quotient_rows.append(
            {
                "identifiable_modulo_gauge": result[
                    "identifiable_modulo_gauge"
                ],
                "measurement_rank": result["measurement_rank"],
                "name": cell["name"],
                "pass": row_pass,
                "witness_pass": witness_pass,
            }
        )
    gates["G6_quotient_criterion"] = {
        "pass": quotient_pass,
        "row_count": len(quotient_rows),
    }

    robust_rows = []
    robust_pass = True
    for cell in fresh["robust_cells"]:
        result = quotient_stability(
            fraction_matrix(cell["matrix"]),
            fraction_matrix(cell["quotient_basis"]),
        )
        row_pass = (
            result["design_rank"] == result["quotient_dimension"]
            and result["sigma_min"] > 0
        )
        robust_pass &= row_pass
        robust_rows.append({"name": cell["name"], "pass": row_pass, **result})
    by_name = {row["name"]: row for row in robust_rows}
    amplification_ratio = (
        by_name["fresh_ill_conditioned"]["amplification"]
        / by_name["fresh_well_conditioned"]["amplification"]
    )
    robust_pass &= amplification_ratio >= float(
        fresh["robust_gate"]["minimum_ill_to_well_amplification_ratio"]
    )
    gates["G7_robust_conditioning"] = {
        "amplification_ratio": amplification_ratio,
        "pass": robust_pass,
        "row_count": len(robust_rows),
    }

    identifiers = sorted(row["identifier"] for row in protocol["prior_art"])
    required = sorted(
        [
            "ASMP-9-v0.10",
            "ASMP-9-v0.26-v0.27",
            "ICML-1999-Ng-Harada-Russell",
            "NeurIPS-2021-671f0311",
            "PMLR:139:5496-5505",
            "PMLR:202:32033-32058",
            "PMLR:235:24808-24828",
            "doi:10.1093/biomet/asm029",
        ]
    )
    claim_pass = (
        identifiers == required
        and len(protocol["structured_claims"]["allowed"]) == 6
        and len(protocol["structured_claims"]["forbidden"]) == 7
        and "ASMP-9 is resolved."
        in protocol["structured_claims"]["forbidden"]
        and "no novelty is claimed" in protocol["claim_boundary"]
    )
    gates["G8_prior_art_and_claim_boundary"] = {
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
    gates["G9_resource_and_scope"] = {
        "gpu_used": False,
        "pass": resource_pass,
        "peak_resident_bytes": peak,
        "wall_seconds": elapsed,
    }

    gate_passes = {name: bool(record["pass"]) for name, record in gates.items()}
    if not gate_passes["G0_registration_binding"] or not gate_passes[
        "G9_resource_and_scope"
    ]:
        verdict_key = "binding_or_resource_gate_fails"
    elif all(gate_passes.values()):
        verdict_key = "all_gates_pass"
    else:
        verdict_key = "any_substantive_gate_fails"
    result = {
        "gate_passes": gate_passes,
        "gates": gates,
        "homogeneous_rows": homogeneous_rows,
        "mdp_rows": mdp_rows,
        "protocol_id": protocol["protocol_id"],
        "quotient_rows": quotient_rows,
        "registration_sha256": registration_hash,
        "robust_rows": robust_rows,
        "verdict": protocol["verdict_map"][verdict_key],
    }
    args.output_dir.mkdir(parents=True)
    result_path = args.output_dir / "result_v0_28.json"
    receipt_path = args.output_dir / "run_receipt_v0_28.json"
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
