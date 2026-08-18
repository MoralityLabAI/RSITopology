"""Verifier-only repair for the valid registered ASMP-9 v0.48 null."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from run_confirmation_v0_48 import (
    WORKERS,
    build_scientific_payload,
    canonical_json_bytes,
    compare_or_write,
    sha256_file,
    validate_source_hashes,
)


HERE = Path(__file__).resolve().parent
INSTRUMENT_GATES = (
    "P0",
    "S0",
    "U0",
    "E0",
    "D0",
    "L0",
    "C0",
    "A0",
    "RESOURCE",
)


def instrument_valid(gates: dict[str, bool]) -> bool:
    return all(gates.get(name, False) for name in INSTRUMENT_GATES)


def adjudication_valid(result: dict) -> bool:
    gates = result["gates"]
    if not instrument_valid(gates):
        return False
    expected_status = (
        "decision_dependent_evidence_ordering_established"
        if gates.get("X0", False)
        else "decision_dependent_ordering_not_established"
    )
    return result["status"] == expected_status


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repair-registration",
        type=Path,
        default=HERE / "registration_v0_48_1.json",
    )
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_48.json",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=HERE / "artifacts_v0_48",
    )
    parser.add_argument(
        "--original-verification",
        type=Path,
        default=HERE / "VERIFY_RESULT_v0_48.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "VERIFY_RESULT_v0_48_1.json",
    )
    args = parser.parse_args()

    repair_registration_bytes = (
        args.repair_registration.resolve().read_bytes()
    )
    repair_registration = json.loads(repair_registration_bytes)
    registration_path = args.registration.resolve()
    artifact_dir = args.artifact_dir.resolve()
    result_path = artifact_dir / "result_v0_48.json"
    experiment_path = artifact_dir / "experiment_rows_v0_48.json"
    subset_path = artifact_dir / "subset_bounds_v0_48.json"

    registration_bytes = registration_path.read_bytes()
    registration = json.loads(registration_bytes)
    result = json.loads(result_path.read_bytes())
    recorded_experiment = json.loads(experiment_path.read_bytes())
    recorded_subset = json.loads(subset_path.read_bytes())
    original = json.loads(
        args.original_verification.resolve().read_bytes()
    )

    source_match, source_checks = validate_source_hashes(registration)
    replay_scientific, replay_experiment, replay_subset = (
        build_scientific_payload(WORKERS)
    )
    scientific_match = (
        canonical_json_bytes(replay_scientific)
        == canonical_json_bytes(result["scientific"])
    )
    experiment_match = (
        canonical_json_bytes(replay_experiment)
        == canonical_json_bytes(recorded_experiment)
    )
    subset_match = (
        canonical_json_bytes(replay_subset)
        == canonical_json_bytes(recorded_subset)
    )
    registration_match = result["registration_sha256"] == hashlib.sha256(
        registration_bytes
    ).hexdigest()
    repair_sources_match = all(
        sha256_file(HERE.parents[3] / relative) == expected
        for relative, expected in repair_registration[
            "source_sha256"
        ].items()
    )
    repair_intent_match = (
        repair_registration["version"] == "0.48.1"
        and repair_registration["status"]
        == "registered_after_outcome_for_verifier_only"
        and repair_registration["expected_recorded_status"]
        == result["status"]
        and repair_registration["expected_prediction_gate_X0"]
        == result["gates"]["X0"]
        and not repair_registration["scientific_changes_permitted"]
    )
    original_failure_diagnosed = (
        original["scientific_payload_match"]
        and original["experiment_rows_match"]
        and original["subset_bounds_match"]
        and original["registration_hash_match"]
        and original["source_hashes_match"]
        and not original["all_recorded_gates_pass"]
        and not original["ok"]
        and original["recorded_status"]
        == "decision_dependent_ordering_not_established"
    )
    adjudication_match = adjudication_valid(result)
    ok = all(
        (
            source_match,
            repair_sources_match,
            repair_intent_match,
            scientific_match,
            experiment_match,
            subset_match,
            registration_match,
            original_failure_diagnosed,
            adjudication_match,
        )
    )
    payload = {
        "schema": "asmp9-v0.48.1-independent-verification-v1",
        "ok": ok,
        "repair_registration_sha256": hashlib.sha256(
            repair_registration_bytes
        ).hexdigest(),
        "registration_hash_match": registration_match,
        "registered_source_hashes_match": source_match,
        "repair_source_hashes_match": repair_sources_match,
        "repair_intent_match": repair_intent_match,
        "scientific_payload_match": scientific_match,
        "experiment_rows_match": experiment_match,
        "subset_bounds_match": subset_match,
        "instrument_valid": instrument_valid(result["gates"]),
        "status_mapping_match": adjudication_match,
        "original_verifier_failure_diagnosed": (
            original_failure_diagnosed
        ),
        "recorded_status": result["status"],
        "prediction_gate_X0": result["gates"]["X0"],
        "artifact_sha256": {
            path.name: sha256_file(path)
            for path in (result_path, experiment_path, subset_path)
        },
        "source_checks": source_checks,
    }
    compare_or_write(args.output.resolve(), canonical_json_bytes(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(not ok)


if __name__ == "__main__":
    main()
