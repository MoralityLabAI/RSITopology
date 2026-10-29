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

from decision_relevance import (
    decision_gauge_valid,
    dot,
    evaluate_plugin_policy,
    quotient_residual,
    scaled_cardinal_target,
    squared_norm,
    subtract,
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


def vectors(values):
    return tuple(tuple(Fraction(str(entry)) for entry in row) for row in values)


def vector(values):
    return tuple(Fraction(str(entry)) for entry in values)


def evaluate_cell(cell):
    return evaluate_plugin_policy(
        vectors(cell["policy_occupancies"]),
        vector(cell["true_reward"]),
        vector(cell["estimated_reward"]),
        vectors(cell["gauge_basis"]),
    )


def jsonable(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(item) for item in value]
    return value


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
    fresh = protocol["fresh_validation"]
    gates: dict[str, dict[str, Any]] = {}
    gates["G0_registration_binding"] = {
        "pass": True,
        "registration_sha256": registration_hash,
        "sealed_file_count": len(registration["sealed_files"]),
    }

    positive_names = (
        "nonzero_regret_cell",
        "zero_regret_cell",
        "sharp_cell",
        "strict_margin_cell",
        "equality_margin_cell",
        "composition_cell",
    )
    gauge_checks = {
        name: decision_gauge_valid(
            vectors(fresh[name]["policy_occupancies"]),
            vectors(fresh[name]["gauge_basis"]),
        )
        for name in positive_names
    }
    invalid_cell = fresh["invalid_gauge_cell"]
    invalid_gauge_valid = decision_gauge_valid(
        vectors(invalid_cell["policy_occupancies"]),
        vectors(invalid_cell["gauge_basis"]),
    )
    gates["G1_decision_gauge_precondition"] = {
        "invalid_control_rejected": not invalid_gauge_valid,
        "pass": all(gauge_checks.values()) and not invalid_gauge_valid,
        "positive_cell_count": len(gauge_checks),
    }

    nonzero = evaluate_cell(fresh["nonzero_regret_cell"])
    zero = evaluate_cell(fresh["zero_regret_cell"])
    regret_bound_pass = (
        nonzero["certificate_available"]
        and nonzero["regret"] > 0
        and nonzero["global_bound_valid"]
        and nonzero["selected_bound_valid"]
        and zero["certificate_available"]
        and zero["regret"] == 0
        and zero["global_bound_valid"]
        and zero["selected_bound_valid"]
    )
    gates["G2_quotient_regret_bound"] = {
        "nonzero_regret": str(nonzero["regret"]),
        "pass": regret_bound_pass,
        "zero_regret": str(zero["regret"]),
    }

    sharp = evaluate_cell(fresh["sharp_cell"])
    sharp_pass = (
        sharp["regret"] > 0
        and sharp["regret"] * sharp["regret"]
        == sharp["selected_bound_squared"]
        == sharp["global_bound_squared"]
    )
    gates["G3_sharpness_witness"] = {
        "bound_squared": str(sharp["selected_bound_squared"]),
        "pass": sharp_pass,
        "regret": str(sharp["regret"]),
    }

    strict = evaluate_cell(fresh["strict_margin_cell"])
    equality = evaluate_cell(fresh["equality_margin_cell"])
    equality_rows = [
        row
        for row in equality["margin_rows"]
        if row["margin"] * row["margin"]
        == equality["delta_squared"] * row["difference_squared"]
    ]
    margin_pass = (
        strict["policy_identity_certified"]
        and not equality["policy_identity_certified"]
        and len(equality_rows) > 0
    )
    gates["G4_policy_identity_margin"] = {
        "equality_controls": len(equality_rows),
        "pass": margin_pass,
        "strict_certified": strict["policy_identity_certified"],
    }

    invalid_result = evaluate_cell(invalid_cell)
    invalid_pass = invalid_result == {
        "status": "decision_gauge_invalid",
        "certificate_available": False,
    }
    gates["G5_invalid_gauge_abstention"] = {
        "pass": invalid_pass,
        "status": invalid_result["status"],
    }

    scale_cell = fresh["scale_cell"]
    scale_rows = scaled_cardinal_target(
        vectors(scale_cell["policy_occupancies"]),
        vector(scale_cell["reward"]),
        int(scale_cell["evaluated_policy"]),
        vector(scale_cell["scale_factors"]),
        Fraction(str(scale_cell["fixed_regret_threshold"])),
    )
    scale_pass = (
        len({row["optimal_policy"] for row in scale_rows}) == 1
        and {row["fixed_threshold_pass"] for row in scale_rows}
        == {True, False}
        and len(
            {
                row["regret"] / row["scale"]
                for row in scale_rows
            }
        )
        == 1
    )
    gates["G6_scale_target_bifurcation"] = {
        "fixed_threshold_outcomes": sorted(
            row["fixed_threshold_pass"] for row in scale_rows
        ),
        "pass": scale_pass,
        "shared_optimal_policy": scale_rows[0]["optimal_policy"],
    }

    composition_cell = fresh["composition_cell"]
    composition = evaluate_cell(composition_cell)
    measurement = vectors(composition_cell["measurement_matrix"])
    true_reward = vector(composition_cell["true_reward"])
    estimated_reward = vector(composition_cell["estimated_reward"])
    observed_error = tuple(
        dot(row, estimated_reward) - dot(row, true_reward)
        for row in measurement
    )
    registered_error = vector(composition_cell["measurement_error"])
    sigma_squared = Fraction(composition_cell["sigma_min_squared"])
    residual = quotient_residual(
        estimated_reward,
        true_reward,
        vectors(composition_cell["gauge_basis"]),
    )
    measurement_error_squared = squared_norm(registered_error)
    predicted_delta_squared = measurement_error_squared / sigma_squared
    predicted_regret_bound_squared = (
        composition["diameter_squared"] * predicted_delta_squared
    )
    composition_pass = (
        observed_error == registered_error
        and squared_norm(residual) <= predicted_delta_squared
        and composition["regret"] * composition["regret"]
        <= predicted_regret_bound_squared
        and composition["regret"] > 0
    )
    gates["G7_measurement_to_decision_composition"] = {
        "observed_regret": str(composition["regret"]),
        "pass": composition_pass,
        "predicted_regret_bound_squared": str(
            predicted_regret_bound_squared
        ),
        "quotient_error_squared": str(squared_norm(residual)),
    }

    identifiers = sorted(row["identifier"] for row in protocol["prior_art"])
    required = sorted(
        [
            "ASMP-9-v0.28",
            "ICML-2004-Abbeel-Ng",
            "PMLR:139:5496-5505",
            "PMLR:162:4618-4629",
            "PMLR:202:32033-32058",
            "PMLR:235:60957-61020",
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

    gate_passes = {name: bool(row["pass"]) for name, row in gates.items()}
    if not gate_passes["G0_registration_binding"] or not gate_passes[
        "G9_resource_and_scope"
    ]:
        verdict_key = "binding_or_resource_gate_fails"
    elif all(gate_passes.values()):
        verdict_key = "all_gates_pass"
    else:
        verdict_key = "any_substantive_gate_fails"
    result = {
        "cell_results": {
            "composition": jsonable(composition),
            "equality_margin": jsonable(equality),
            "invalid_gauge": jsonable(invalid_result),
            "nonzero_regret": jsonable(nonzero),
            "sharp": jsonable(sharp),
            "strict_margin": jsonable(strict),
            "zero_regret": jsonable(zero),
        },
        "gate_passes": gate_passes,
        "gates": gates,
        "protocol_id": protocol["protocol_id"],
        "registration_sha256": registration_hash,
        "scale_rows": jsonable(scale_rows),
        "verdict": protocol["verdict_map"][verdict_key],
    }
    args.output_dir.mkdir(parents=True)
    result_path = args.output_dir / "result_v0_29.json"
    receipt_path = args.output_dir / "run_receipt_v0_29.json"
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
