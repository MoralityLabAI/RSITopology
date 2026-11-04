from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from boundary_frontier import (
    M_CAP,
    certificate_record,
    compute_surface,
    descriptive_log_fit,
    evaluate_surface_gates,
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
    for relative, expected in registration["sealed_files"].items():
        actual = sha256_file(HERE / relative)
        if actual != expected:
            raise RuntimeError(f"sealed hash mismatch for {relative}: {actual} != {expected}")


def write_csv(path: Path, records: list[dict[str, object]]) -> None:
    columns = [
        "k1",
        "theta",
        "forbidden_class_size",
        "boundary_role",
        "delta",
        "delta_float",
        "status",
        "m_star",
        "normal_reference_m",
        "normal_residual",
        "cutoff",
        "fp_float",
        "fn_float",
        "predecessor_fn_float",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, default=HERE / "registration_v0_2.json")
    parser.add_argument("--output-dir", type=Path, default=HERE / "artifacts_v0_2")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    registration = json.loads(args.registration.read_text(encoding="utf-8"))
    validate_registration(registration)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / "result.json"
    table_path = args.output_dir / "frontier.csv"
    receipt_path = args.output_dir / "receipt.json"
    if any(path.exists() for path in (result_path, table_path, receipt_path)) and not args.force:
        raise RuntimeError("output exists; use --force for an explicit replay")

    certificates = compute_surface()
    records = [certificate_record(certificate) for certificate in certificates]
    gates = evaluate_surface_gates(certificates)
    instrument_names = (
        "E0_exact_adjacency",
        "R0_v0_1_reproduction",
        "C0_class_census",
        "O0_order",
        "B0_boundary_label",
    )
    instrument_valid = all(gates[name]["pass"] for name in instrument_names)
    verdict = (
        "invalid_instrument"
        if not instrument_valid
        else "exact_boundary_degradation_surface_established"
        if gates["S0_surface_liveness"]["pass"]
        else "registered_surface_incomplete"
    )
    result = {
        "experiment_id": registration["experiment_id"],
        "verdict": verdict,
        "evidence_class": "exact_finite_rational_with_descriptive_float_fit",
        "uniform_m_cap": M_CAP,
        "gates": gates,
        "descriptive_log_fit": descriptive_log_fit(records),
        "records": records,
        "claim_boundary": registration["claim_boundary"],
    }
    write_json(result_path, result)
    write_csv(table_path, records)
    receipt = {
        "experiment_id": registration["experiment_id"],
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "registration_sha256": sha256_file(args.registration),
        "result_sha256": sha256_file(result_path),
        "frontier_csv_sha256": sha256_file(table_path),
        "sealed_files": registration["sealed_files"],
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "scipy_role": "candidate_location_only",
            "gate_arithmetic": "integer binomial numerators and fractions.Fraction",
            "gpu": "not used",
        },
    }
    write_json(receipt_path, receipt)
    print(json.dumps({"verdict": verdict, "gates": gates, "fit": result["descriptive_log_fit"]}, indent=2))


if __name__ == "__main__":
    main()

