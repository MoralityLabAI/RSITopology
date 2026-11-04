"""Hash-sealed executor for ASMP-9 sequential risk access v0.41."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import time

import psutil

from confirmation import run_confirmation


BASE = Path(__file__).resolve().parent
PROTOCOL_ID = "asmp9-sequential-risk-access-v0.41"


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
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
    if registration.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("wrong protocol id")
    sealed = registration.get("sealed_files")
    if not isinstance(sealed, dict) or not sealed:
        raise ValueError("registration has no sealed files")
    for relative_path, expected in sorted(sealed.items()):
        path = BASE / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"sealed file missing: {relative_path}")
        observed = sha256_file(path)
        if observed != expected:
            raise ValueError(
                f"sealed hash mismatch for {relative_path}: "
                f"{observed} != {expected}"
            )
    preflight = registration.get("preflight")
    if (
        not isinstance(preflight, dict)
        or preflight.get("status") != "pass"
        or preflight.get("tests_passed") != 14
    ):
        raise ValueError("registered preflight did not pass")
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
    r0 = (
        set(result["query_channels"])
        == {"root_q", "left_q", "right_q"}
        and len(result["classification_cells"]) == 6
        and len(result["group_cells"]) == 2
    )
    ceiling = registration["resource_ceiling"]
    resource_pass = (
        elapsed <= ceiling["max_wall_seconds"]
        and peak <= ceiling["max_peak_working_set_bytes"]
    )
    gates = {
        "P0": True,
        "S0": True,
        "R0": r0,
        **result["gates"],
        "RESOURCE": resource_pass,
    }
    payload = {
        "protocol_id": PROTOCOL_ID,
        "registration_file_sha256": registration_hash,
        "registration_implementation_commit": registration[
            "implementation_commit"
        ],
        "elapsed_seconds": elapsed,
        "peak_working_set_bytes": peak,
        "resource_ceiling": ceiling,
        "gates": gates,
        "query_channels": result["query_channels"],
        "classification_cells": result["classification_cells"],
        "group_cells": result["group_cells"],
        "adaptivity_gap": result["adaptivity_gap"],
        "status": (
            "finite_sequential_risk_access_characterization_established"
            if all(gates.values())
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
        default=BASE / "registration_v0_41.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE / "artifacts_v0_41" / "RESULT_v0_41.json",
    )
    args = parser.parse_args()
    payload = execute(args.registration.resolve(), args.output.resolve())
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
