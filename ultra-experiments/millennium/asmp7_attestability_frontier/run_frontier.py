from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from attestability import (
    THETA_GRID,
    evaluate_gates,
    fraction_text,
    minimum_channels,
    pareto_frontier,
    test_to_record,
    validate_orbit,
    validate_trace_witness,
)


HERE = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def validate_registration(registration: dict[str, object]) -> None:
    for relative, expected_hash in registration["sealed_files"].items():
        actual = sha256_file(HERE / relative)
        if actual != expected_hash:
            raise RuntimeError(f"sealed hash mismatch for {relative}: {actual} != {expected_hash}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, default=HERE / "registration_v0_1.json")
    parser.add_argument("--output-dir", type=Path, default=HERE / "artifacts_v0_1")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    registration = json.loads(args.registration.read_text(encoding="utf-8"))
    validate_registration(registration)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / "result.json"
    receipt_path = args.output_dir / "receipt.json"
    if (result_path.exists() or receipt_path.exists()) and not args.force:
        raise RuntimeError("output exists; use --force for an explicit replay")

    orbit = validate_orbit()
    trace = validate_trace_witness()
    channels = minimum_channels()
    frontier = pareto_frontier(channels)
    gates = evaluate_gates(orbit, trace, channels, frontier)
    instrument_gates = ("T0_finite_orbit_integrity", "T1_trace_impossibility", "P0_sufficient_statistic", "U0_uniform_composite", "F0_frontier_integrity")
    instrument_valid = all(gates[name]["pass"] for name in instrument_gates)
    scientific_pass = gates["A0_privacy_kill"]["pass"] and gates["A1_charged_audit_liveness"]["pass"] and gates["E0_exhaustive_liveness"]["pass"]
    verdict = (
        "invalid_instrument"
        if not instrument_valid
        else "exact_finite_trace_impossibility_and_charged_audit_frontier_established"
        if scientific_pass
        else "registered_directional_gate_failure"
    )

    result = {
        "experiment_id": registration["experiment_id"],
        "verdict": verdict,
        "evidence_class": "exact_finite_rational",
        "orbit": orbit,
        "trace_impossibility": trace,
        "minimum_channels": {
            fraction_text(theta): test_to_record(channels[theta]) for theta in THETA_GRID
        },
        "pareto_frontier": [test_to_record(test) for test in frontier],
        "gates": gates,
        "claim_boundary": registration["claim_boundary"],
    }
    write_json(result_path, result)

    receipt = {
        "experiment_id": registration["experiment_id"],
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "registration_sha256": sha256_file(args.registration),
        "result_sha256": sha256_file(result_path),
        "sealed_files": registration["sealed_files"],
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "arithmetic": "stdlib fractions.Fraction",
            "gpu": "not used",
        },
    }
    write_json(receipt_path, receipt)
    print(json.dumps({"verdict": verdict, "gates": gates}, indent=2))


if __name__ == "__main__":
    main()

