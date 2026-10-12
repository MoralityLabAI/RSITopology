"""Sealed executor for ASMP-9 decision-relative access v0.38."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import psutil

from confirmation import run_confirmation


BASE = Path(__file__).resolve().parent


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_registration(registration_path: Path) -> dict:
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    if registration.get("status") != "registered_prereveal":
        raise ValueError("registration is not in registered_prereveal state")
    if registration.get("protocol_id") != (
        "asmp9-decision-relative-access-v0.38"
    ):
        raise ValueError("wrong protocol id")
    files = registration.get("sealed_files")
    if not isinstance(files, dict) or not files:
        raise ValueError("registration has no sealed file map")
    for relative_path, expected_hash in sorted(files.items()):
        path = BASE / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"sealed file missing: {relative_path}")
        observed = sha256_file(path)
        if observed != expected_hash:
            raise ValueError(
                f"sealed hash mismatch for {relative_path}: "
                f"{observed} != {expected_hash}"
            )
    preflight = registration.get("preflight")
    if (
        not isinstance(preflight, dict)
        or preflight.get("status") != "pass"
        or preflight.get("tests_passed") != 16
    ):
        raise ValueError("registered preflight is absent or did not pass")
    return registration


def peak_working_set_bytes() -> int:
    memory = psutil.Process(os.getpid()).memory_info()
    return int(getattr(memory, "peak_wset", memory.rss))


def execute(registration_path: Path, output_path: Path) -> dict:
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite {output_path}")
    registration = validate_registration(registration_path)
    registration_hash = sha256_file(registration_path)
    start = time.perf_counter()
    result = run_confirmation()
    elapsed = time.perf_counter() - start
    peak = peak_working_set_bytes()

    expected_cells = {
        (high, low, nuisance)
        for high, low in registration["confirmation_grid"]["strengths"]
        for nuisance in registration["confirmation_grid"][
            "nuisance_one_probabilities"
        ]
    }
    observed_cells = {
        (
            row["high"],
            row["low"],
            row["nuisance_one_probability"],
        )
        for row in result["rows"]
    }
    r0 = (
        result["row_count"] == 6
        and len(result["rows"]) == 6
        and observed_cells == expected_cells
    )
    ceilings = registration["resource_ceiling"]
    resource_pass = (
        elapsed <= ceilings["max_wall_seconds"]
        and peak <= ceilings["max_peak_working_set_bytes"]
    )
    all_gates = {
        "P0": True,
        "S0": True,
        "R0": r0,
        **result["gates"],
        "RESOURCE": resource_pass,
    }
    payload = {
        "protocol_id": registration["protocol_id"],
        "registration_file_sha256": registration_hash,
        "registration_implementation_commit": registration[
            "implementation_commit"
        ],
        "elapsed_seconds": elapsed,
        "peak_working_set_bytes": peak,
        "resource_ceiling": ceilings,
        "gates": all_gates,
        "rows": result["rows"],
        "status": (
            "finite_decision_relative_access_threshold_established"
            if all(all_gates.values())
            else "registered_gate_failed"
        ),
    }
    payload["result_content_sha256"] = sha256_bytes(canonical_bytes(payload))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("xb") as handle:
        handle.write(canonical_bytes(payload))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registration",
        type=Path,
        default=BASE / "registration_v0_38.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE / "artifacts_v0_38" / "RESULT_v0_38.json",
    )
    args = parser.parse_args()
    payload = execute(args.registration.resolve(), args.output.resolve())
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
