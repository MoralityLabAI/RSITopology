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

from behavioral_rectangle import (
    acquire_rectangle,
    additive_decomposition,
    audit_mixture_affinity,
    box_support,
    centered_dyadic_grid,
    certify_rectangle,
    cross_difference_matrix,
    flatten,
    interaction_residuals,
    majority_error_probability,
    minimum_odd_repeats,
    omission_witness,
    rational_rank,
    row_local_coordinates,
    standard_gamble_response,
)


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def q(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if hasattr(value, "__dataclass_fields__"):
        return {
            key: jsonable(getattr(value, key))
            for key in value.__dataclass_fields__
        }
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(item) for item in value]
    return value


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

        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(Counters),
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


def validate_registration(path: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    registration = json.loads(path.read_text(encoding="utf-8"))
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
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    return registration, protocol, sha256(path)


def pairwise_order(values: tuple[Fraction, ...]) -> tuple[int, ...]:
    return tuple(
        (left > right) - (left < right)
        for left in values
        for right in values
    )


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

    primary = protocol["primary_fixture"]
    values = tuple(
        tuple(q(value) for value in row) for row in primary["values"]
    )
    depth = int(primary["bisection_depth"])
    acquired = acquire_rectangle(values, depth)
    estimates = tuple(
        tuple(cell.estimate for cell in row) for row in acquired
    )
    query_count = sum(cell.query_count for row in acquired for cell in row)
    exact_recovery = estimates == values
    grid = set(centered_dyadic_grid(depth))
    on_grid = all(value in grid for value in flatten(values))
    binary_equality = standard_gamble_response(Fraction(1, 2), Fraction(1, 2))
    transcript_lower_bound = len(flatten(values)) * depth
    gates["G1_population_acquisition"] = {
        "binary_equality_branch": binary_equality,
        "exact_recovery": exact_recovery,
        "on_centered_grid": on_grid,
        "pass": (
            exact_recovery
            and on_grid
            and query_count == 48
            and transcript_lower_bound == 48
            and binary_equality == -1
        ),
        "population_query_count": query_count,
        "transcript_lower_bound": transcript_lower_bound,
    }

    matrix = cross_difference_matrix(
        int(primary["row_count"]), int(primary["column_count"])
    )
    additive_residuals = interaction_residuals(values)
    interactive = [list(row) for row in values]
    interaction_row, interaction_column = primary["interaction_cell"]
    interactive[interaction_row][interaction_column] += q(
        primary["interaction_amplitude"]
    )
    interactive = tuple(tuple(row) for row in interactive)
    interactive_residuals = interaction_residuals(interactive)
    gates["G2_rectangle_algebra"] = {
        "additive_decomposition_available": (
            additive_decomposition(values) is not None
        ),
        "additive_residuals": additive_residuals,
        "interaction_residuals": interactive_residuals,
        "operator_rank": rational_rank(matrix),
        "operator_shape": [len(matrix), len(matrix[0])],
        "pass": (
            rational_rank(matrix) == 6
            and all(value == 0 for value in additive_residuals)
            and any(value != 0 for value in interactive_residuals)
            and additive_decomposition(values) is not None
            and additive_decomposition(interactive) is None
        ),
    }

    omissions = []
    for omitted in range(len(flatten(values))):
        witness = omission_witness(3, 4, omitted, Fraction(1, 7))
        residuals = interaction_residuals(witness)
        observed_zero = all(
            value == 0
            for index, value in enumerate(flatten(witness))
            if index != omitted
        )
        omissions.append(
            {
                "nonadditive": any(value != 0 for value in residuals),
                "observed_cells_unchanged": observed_zero,
                "omitted_index": omitted,
            }
        )
    gates["G3_complete_coverage"] = {
        "omission_count": len(omissions),
        "pass": len(omissions) == 12
        and all(
            row["nonadditive"] and row["observed_cells_unchanged"]
            for row in omissions
        ),
        "witnesses": omissions,
    }

    continuous = protocol["continuous_control"]
    continuous_acquired = acquire_rectangle(
        values, int(continuous["bisection_depth"])
    )
    continuous_estimates = tuple(
        tuple(cell.estimate for cell in row)
        for row in continuous_acquired
    )
    continuous_widths = tuple(
        tuple(cell.radius for cell in row)
        for row in continuous_acquired
    )
    coverage = all(
        cell.lower <= value <= cell.upper
        for row_values, row_cells in zip(values, continuous_acquired)
        for value, cell in zip(row_values, row_cells)
    )
    direction = tuple(q(value) for value in continuous["direction"])
    structured_support = box_support(
        matrix, flatten(continuous_widths), direction
    )
    coordinate_supports = tuple(
        box_support(
            matrix,
            flatten(continuous_widths),
            tuple(
                Fraction(1 if candidate == index else 0)
                for candidate in range(len(matrix))
            ),
        )
        for index in range(len(matrix))
    )
    independent_support = sum(
        (
            abs(coefficient) * max(coordinate_supports)
            for coefficient in direction
        ),
        Fraction(0),
    )
    gates["G4_shared_uncertainty_geometry"] = {
        "cell_coverage": coverage,
        "coordinate_supports": coordinate_supports,
        "direction": direction,
        "independent_residual_support": independent_support,
        "pass": (
            coverage
            and structured_support
            == q(continuous["expected_coordinate_support"])
            and independent_support
            == q(continuous["expected_independent_residual_support"])
            and structured_support < independent_support
        ),
        "structured_support": structured_support,
    }

    additive_certificate = certify_rectangle(
        continuous_estimates,
        continuous_widths,
        q(continuous["tolerance"]),
    )
    zero_widths = tuple(
        tuple(Fraction(0) for _ in row) for row in interactive
    )
    interaction_certificate = certify_rectangle(
        interactive, zero_widths, Fraction(0)
    )
    inconclusive_certificate = certify_rectangle(
        ((0, 0), (0, Fraction(3, 4))),
        ((Fraction(1, 8), Fraction(1, 8)),) * 2,
        Fraction(1, 2),
    )
    gates["G5_three_state_semantics"] = {
        "additive": additive_certificate.decision,
        "inconclusive": inconclusive_certificate.decision,
        "interaction": interaction_certificate.decision,
        "pass": (
            additive_certificate.decision
            == "approximately_additive_certified"
            and interaction_certificate.decision == "interaction_certified"
            and inconclusive_certificate.decision == "inconclusive"
        ),
    }

    mixture_results = {}
    for name, cell in protocol["mixture_controls"].items():
        mixture_results[name] = audit_mixture_affinity(
            first_estimate=q(cell["first"]),
            second_estimate=q(cell["second"]),
            mixture_estimate=q(cell["mixture"]),
            first_weight=q(cell["first_weight"]),
            first_width=q(cell.get("first_width", "0")),
            second_width=q(cell.get("second_width", "0")),
            mixture_width=q(cell.get("mixture_width", "0")),
            tolerance=q(cell["tolerance"]),
        )
    gates["G6_mixture_affinity_liveness"] = {
        "controls": mixture_results,
        "pass": (
            mixture_results["consistent"].decision
            == "mixture_affinity_certified"
            and mixture_results["distorted"].decision
            == "mixture_affinity_rejected"
            and mixture_results["uncertain"].decision == "inconclusive"
        ),
    }

    no_go = protocol["no_go_controls"]
    ordinal_additive = tuple(
        tuple(q(value) for value in row)
        for row in no_go["ordinal_additive"]
    )
    ordinal_interactive = tuple(
        tuple(q(value) for value in row)
        for row in no_go["ordinal_interactive"]
    )
    row_additive = tuple(
        tuple(q(value) for value in row)
        for row in no_go["row_local_additive"]
    )
    row_interactive = tuple(
        tuple(q(value) for value in row)
        for row in no_go["row_local_interactive"]
    )
    ordinal_same = pairwise_order(flatten(ordinal_additive)) == pairwise_order(
        flatten(ordinal_interactive)
    )
    row_local_same = row_local_coordinates(
        row_additive
    ) == row_local_coordinates(row_interactive)
    gates["G7_access_no_go"] = {
        "ordinal_additive_residual": interaction_residuals(ordinal_additive),
        "ordinal_interactive_residual": interaction_residuals(
            ordinal_interactive
        ),
        "ordinal_transcript_equal": ordinal_same,
        "pass": (
            ordinal_same
            and row_local_same
            and additive_decomposition(ordinal_additive) is not None
            and additive_decomposition(ordinal_interactive) is None
            and additive_decomposition(row_additive) is not None
            and additive_decomposition(row_interactive) is None
        ),
        "row_local_coordinates_equal": row_local_same,
    }

    finite = protocol["finite_sample"]
    correct_probability = q(finite["correct_probability_floor"])
    family_error = q(finite["family_error"])
    repeats = minimum_odd_repeats(
        int(finite["population_query_count"]),
        correct_probability,
        family_error,
    )
    family_bound = int(finite["population_query_count"]) * (
        majority_error_probability(repeats, correct_probability)
    )
    previous_bound = int(finite["population_query_count"]) * (
        majority_error_probability(repeats - 2, correct_probability)
    )
    chance_unavailable = False
    try:
        minimum_odd_repeats(
            int(finite["population_query_count"]),
            Fraction(1, 2),
            family_error,
        )
    except ValueError:
        chance_unavailable = True
    gates["G8_finite_sample"] = {
        "chance_unavailable": chance_unavailable,
        "family_bound": family_bound,
        "minimum_odd_repeats": repeats,
        "pass": (
            repeats == int(finite["registered_minimum_odd_repeats"])
            and family_bound <= family_error
            and previous_bound > family_error
            and chance_unavailable
        ),
        "previous_odd_bound": previous_bound,
    }

    shared_column_degrees = tuple(
        sum(1 for row in matrix if row[column] != 0)
        for column in range(len(matrix[0]))
    )
    handoff = {
        "cell_widths": flatten(continuous_widths),
        "residual_centers": interaction_residuals(continuous_estimates),
        "semantic_incidence": matrix,
        "shared_column_degrees": shared_column_degrees,
    }
    gates["G9_v031_handoff"] = {
        "pass": (
            len(matrix) == 6
            and len(matrix[0]) == 12
            and any(degree > 1 for degree in shared_column_degrees)
            and structured_support
            == q(continuous["expected_coordinate_support"])
        ),
        "shared_cell_count": sum(
            1 for degree in shared_column_degrees if degree > 1
        ),
    }

    prior_text = (HERE / "PRIOR_ART_GATE_v0_32.md").read_text(
        encoding="utf-8"
    )
    theorem_text = (HERE / "THEOREM_DRAFT_v0_32.md").read_text(
        encoding="utf-8"
    )
    required_prior = (
        "Herstein",
        "Luce",
        "Torrance",
        "Wakker",
        "Chen",
        "No novelty claim",
    )
    required_scope = (
        "does not",
        "expected utility",
        "context-varying anchors",
        "ASMP-9",
    )
    gates["G10_prior_art_and_claim_boundary"] = {
        "pass": all(token in prior_text for token in required_prior)
        and all(token in theorem_text for token in required_scope),
        "prior_tokens": required_prior,
        "scope_tokens": required_scope,
    }

    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    caps = protocol["resource_caps"]
    gates["G11_resource_and_scope"] = {
        "gpu_used": False,
        "pass": (
            not caps["gpu_allowed"]
            and elapsed <= caps["wall_seconds"]
            and peak <= caps["peak_resident_bytes"]
        ),
        "peak_resident_bytes": peak,
        "wall_seconds": elapsed,
    }

    all_pass = all(row["pass"] for row in gates.values())
    result = {
        "gates": gates,
        "handoff": handoff,
        "mixture_controls": mixture_results,
        "primary": {
            "acquired_intervals": acquired,
            "additive_certificate": additive_certificate,
            "interaction_certificate": interaction_certificate,
            "operator": matrix,
            "population_query_count": query_count,
            "transcript_lower_bound": transcript_lower_bound,
            "values": values,
        },
        "protocol_id": protocol["protocol_id"],
        "resource": {
            "gpu_used": False,
            "peak_resident_bytes": peak,
            "wall_seconds": elapsed,
        },
        "verdict": protocol["verdicts"]["pass" if all_pass else "fail"],
    }

    args.output_dir.mkdir(parents=True)
    result_path = args.output_dir / "result_v0_32.json"
    receipt_path = args.output_dir / "run_receipt_v0_32.json"
    write_json_exclusive(result_path, jsonable(result))
    receipt = {
        "finished_at_utc": utc_now(),
        "implementation_commit": registration["implementation_commit"],
        "protocol_sha256": sha256(REPO / registration["protocol_path"]),
        "registered_at_utc": registration["registered_at_utc"],
        "registration_sha256": registration_hash,
        "result_sha256": sha256(result_path),
        "run_commit": git("rev-parse", "HEAD"),
        "started_at_utc": started_at,
        "verdict": result["verdict"],
    }
    write_json_exclusive(receipt_path, receipt)
    print(json.dumps(jsonable(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
