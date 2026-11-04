from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from itertools import product
from pathlib import Path

from access_ladder import (
    K_GRID,
    N_VARIABLES,
    RESOURCE_GRID,
    benign_action,
    census,
    mechanisms,
    matched_unlabelled_coefficient_spectrum,
    simulator_contains,
    nonzero_signature_entries,
)


ROOT = Path(__file__).resolve().parent
REGISTRATION = ROOT / "registration_v0_1.json"
PROTOCOL = ROOT / "PROTOCOL_v0_1.md"
OUTPUT = ROOT / "artifacts_v0_1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def verify_registration() -> dict[str, object]:
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    for relative, expected in registration["source_hashes"].items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise RuntimeError(f"registration mismatch for {relative}")
    return registration


def main() -> int:
    registration = verify_registration()
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise FileExistsError(f"write-once output is not empty: {OUTPUT}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rows = census()

    benign_match = True
    spectrum_match = True
    simulator_pass = True
    heldout_pass = True
    threshold_pass = True
    for degree in K_GRID:
        ensemble = mechanisms(degree)
        construction = ensemble[::2]
        holdout = ensemble[1::2]
        for mechanism in ensemble:
            spectrum_match &= matched_unlabelled_coefficient_spectrum(mechanism) == (0, 1)
            for bits in product((-1, 1), repeat=N_VARIABLES):
                benign_match &= benign_action(mechanism, bits) == 0
            for weak_order in RESOURCE_GRID:
                for weak_interventions in RESOURCE_GRID:
                    for strong_order in range(weak_order, N_VARIABLES + 1):
                        for strong_interventions in range(weak_interventions, N_VARIABLES + 1):
                            simulator_pass &= simulator_contains(
                                mechanism,
                                weak_order,
                                weak_interventions,
                                strong_order,
                                strong_interventions,
                            )
        for order in RESOURCE_GRID:
            for interventions in RESOURCE_GRID:
                predicted = order + interventions >= degree
                for split in (construction, holdout):
                    visible = [
                        bool(nonzero_signature_entries(item, order, interventions))
                        for item in split
                    ]
                    heldout_pass &= all(visible) if predicted else not any(visible)

    for row in rows:
        threshold_pass &= (row.detector_advantage == int(row.threshold_predicted))

    minimum_resource = {
        str(degree): min(
            row.observation_order + row.intervention_budget
            for row in rows
            if row.degree == degree and row.detector_advantage == 1
        )
        for degree in K_GRID
    }
    gates = {
        "G0_registration_binding": all(
            sha256(ROOT / relative) == expected
            for relative, expected in registration["source_hashes"].items()
        ),
        "G1_complete_census": len(rows) == len(K_GRID) * len(RESOURCE_GRID) ** 2,
        "G2_paired_benign_and_spectrum_match": benign_match and spectrum_match,
        "G3_exact_blindness_below_boundary": all(
            row.detector_advantage == 0 for row in rows if not row.threshold_predicted
        ),
        "G4_exact_detection_at_boundary": all(
            row.detector_advantage == 1 for row in rows if row.threshold_predicted
        ),
        "G5_access_lattice_simulator": simulator_pass,
        "G6_support_holdout": heldout_pass,
        "G7_minimum_total_resource": all(minimum_resource[str(k)] == k for k in K_GRID),
    }
    verdict = "finite_access_ladder_established" if all(gates.values()) else "invalid_or_not_established"

    csv_path = OUTPUT / "access_ladder.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "degree",
            "observation_order",
            "intervention_budget",
            "detector_advantage",
            "query_upper_bound",
            "threshold_predicted",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "degree": row.degree,
                    "observation_order": row.observation_order,
                    "intervention_budget": row.intervention_budget,
                    "detector_advantage": str(row.detector_advantage),
                    "query_upper_bound": row.query_upper_bound,
                    "threshold_predicted": int(row.threshold_predicted),
                }
            )

    result = {
        "schema_version": "asmp11_access_ladder_result_v0_1",
        "verdict": verdict,
        "gates": gates,
        "counts": {
            "planted_mechanisms": sum(len(mechanisms(k)) for k in K_GRID),
            "access_cells": len(rows),
        },
        "minimum_total_resource": minimum_resource,
        "claim_boundary": "Exact Boolean oracle-access instrument only; not a white-box cryptographic lower bound or real-model backdoor result.",
    }
    result_path = OUTPUT / "result.json"
    result_path.write_text(canonical_json(result), encoding="utf-8")
    receipt = {
        "schema_version": "asmp11_access_ladder_receipt_v0_1",
        "registration_sha256": sha256(REGISTRATION),
        "protocol_sha256": sha256(PROTOCOL),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "elapsed_seconds": time.time() - started,
        "environment": {"python": sys.version, "platform": platform.platform(), "cpu_count": os.cpu_count()},
        "outputs": {"access_ladder.csv": sha256(csv_path), "result.json": sha256(result_path)},
    }
    (OUTPUT / "receipt.json").write_text(canonical_json(receipt), encoding="utf-8")
    print(canonical_json({"verdict": verdict, "gates": gates}), end="")
    return 0 if all(gates.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
