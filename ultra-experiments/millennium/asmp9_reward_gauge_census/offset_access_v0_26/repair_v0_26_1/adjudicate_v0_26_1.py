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
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
ORIGINAL_SCIENTIFIC_GATES = {
    "G0_registration_binding",
    "G1_freshness_and_structure",
    "G2_population_recovery",
    "G3_sharp_dyadic_query_bound",
    "G4_restricted_offset_obstruction",
    "G5_bounded_error_finite_sample_rule",
    "G6_flat_link_no_uniform_rate",
    "G7_no_offset_control",
    "G8_sample_certificate",
    "G10_resource_and_scope",
}


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
            raise RuntimeError(f"repair sealed hash mismatch: {relative}")
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
        (REPO / registration["protocol_path"]).read_text()
    )
    return registration, protocol, sha256(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("tracked tree must be clean before adjudication")

    started = time.perf_counter()
    started_at = utc_now()
    registration, protocol, registration_hash = validate_registration(
        args.registration.resolve()
    )
    gates: dict[str, dict[str, Any]] = {}
    gates["R0_repair_registration_binding"] = {
        "pass": True,
        "registration_sha256": registration_hash,
        "sealed_file_count": len(registration["sealed_files"]),
    }

    sources = protocol["source_artifacts"]
    source_hashes = {
        name: sha256(REPO / source["path"])
        for name, source in sources.items()
    }
    source_binding = all(
        source_hashes[name] == source["sha256"]
        for name, source in sources.items()
    )
    gates["R1_immutable_source_binding"] = {
        "pass": source_binding,
        "source_hashes": source_hashes,
    }

    original_result = json.loads(
        (REPO / sources["result"]["path"]).read_text()
    )
    original_protocol = json.loads(
        (REPO / sources["protocol"]["path"]).read_text()
    )
    original_registration = json.loads(
        (REPO / sources["original_registration"]["path"]).read_text()
    )
    independent = json.loads(
        (REPO / sources["independent_verification"]["path"]).read_text()
    )

    original_gate_passes = original_result["gate_passes"]
    scientific_pass = (
        set(original_gate_passes) == ORIGINAL_SCIENTIFIC_GATES | {
            "G9_prior_art_and_claim_boundary"
        }
        and all(original_gate_passes[name] for name in ORIGINAL_SCIENTIFIC_GATES)
    )
    gates["R2_original_scientific_gates"] = {
        "original_gate_passes": original_gate_passes,
        "pass": scientific_pass,
    }

    false_independent_checks = sorted(
        name for name, passed in independent["checks"].items() if not passed
    )
    isolated = (
        original_gate_passes["G9_prior_art_and_claim_boundary"] is False
        and original_result["verdict"]
        == original_protocol["verdict_map"]["any_substantive_gate_fails"]
        and false_independent_checks == ["all_gates_pass", "verdict"]
        and independent["pass"] is False
    )
    gates["R3_original_failure_isolation"] = {
        "false_independent_checks": false_independent_checks,
        "original_verdict": original_result["verdict"],
        "pass": isolated,
    }

    actual_identifiers = sorted(
        item["identifier"] for item in original_protocol["prior_art"]
    )
    required_identifiers = sorted(protocol["required_prior_art_identifiers"])
    prior_relative = sources["prior_art_audit"]["path"]
    original_prior_seal = original_registration["sealed_files"].get(
        prior_relative
    )
    structural_prior = (
        actual_identifiers == required_identifiers
        and original_prior_seal == sources["prior_art_audit"]["sha256"]
        and original_registration["sealed_files"].get(
            sources["protocol"]["path"]
        )
        == sources["protocol"]["sha256"]
    )
    gates["R4_structural_prior_art_gate"] = {
        "actual_identifiers": actual_identifiers,
        "pass": structural_prior,
        "required_identifiers": required_identifiers,
    }

    original_allowed = original_protocol["structured_claims"]["allowed"]
    original_forbidden = original_protocol["structured_claims"]["forbidden"]
    claim_pass = (
        len(original_allowed) == 5
        and len(original_forbidden) == 7
        and "ASMP-9 is resolved." in original_forbidden
        and "no novelty is claimed" in original_protocol["claim_boundary"]
        and "known reward-unit intervention"
        in original_protocol["claim_boundary"]
        and "V0.26 itself passed."
        in protocol["structured_claims"]["forbidden"]
        and "V0.26.1 generated fresh scientific evidence."
        in protocol["structured_claims"]["forbidden"]
    )
    gates["R5_claim_boundary"] = {"pass": claim_pass}

    derived = all(
        gates[name]["pass"]
        for name in (
            "R0_repair_registration_binding",
            "R1_immutable_source_binding",
            "R2_original_scientific_gates",
            "R3_original_failure_isolation",
            "R4_structural_prior_art_gate",
            "R5_claim_boundary",
        )
    )
    gates["R6_derived_adjudication"] = {"pass": derived}

    elapsed = time.perf_counter() - started
    peak = peak_resident_bytes()
    caps = protocol["resource_caps"]
    resource_pass = (
        not caps["gpu_allowed"]
        and elapsed <= caps["wall_seconds"]
        and peak <= caps["peak_resident_bytes"]
    )
    gates["R7_resource_and_scope"] = {
        "gpu_used": False,
        "pass": resource_pass,
        "peak_resident_bytes": peak,
        "wall_seconds": elapsed,
    }

    gate_passes = {name: bool(record["pass"]) for name, record in gates.items()}
    verdict = protocol["verdict_map"][
        "all_gates_pass" if all(gate_passes.values()) else "any_gate_fails"
    ]
    result = {
        "gate_passes": gate_passes,
        "gates": gates,
        "original_result_sha256": sources["result"]["sha256"],
        "original_verdict_preserved": original_result["verdict"],
        "protocol_id": protocol["protocol_id"],
        "registration_sha256": registration_hash,
        "repair_kind": "mechanical_re_adjudication_no_new_scientific_run",
        "verdict": verdict,
    }
    args.output_dir.mkdir(parents=True)
    result_path = args.output_dir / "result_v0_26_1.json"
    receipt_path = args.output_dir / "run_receipt_v0_26_1.json"
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
