"""Independently replay and verify the ASMP-9 v0.46 result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from run_confirmation_v0_46 import (
    WORKERS,
    build_scientific_payload,
    canonical_json_bytes,
    compare_or_write,
    sha256_file,
    validate_source_hashes,
)


HERE = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_46.json",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=HERE / "artifacts_v0_46",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "VERIFY_RESULT_v0_46.json",
    )
    args = parser.parse_args()

    registration_path = args.registration.resolve()
    artifact_dir = args.artifact_dir.resolve()
    result_path = artifact_dir / "result_v0_46.json"
    coupled_path = artifact_dir / "coupled_rows_v0_46.json"
    rectangle_path = artifact_dir / "rectangle_audit_v0_46.json"

    registration_bytes = registration_path.read_bytes()
    registration = json.loads(registration_bytes)
    result = json.loads(result_path.read_bytes())
    recorded_coupled = json.loads(coupled_path.read_bytes())
    recorded_rectangle = json.loads(rectangle_path.read_bytes())

    source_match, source_checks = validate_source_hashes(registration)
    replay_scientific, replay_coupled, replay_rectangle = (
        build_scientific_payload(WORKERS)
    )
    scientific_match = (
        canonical_json_bytes(replay_scientific)
        == canonical_json_bytes(result["scientific"])
    )
    coupled_match = (
        canonical_json_bytes(replay_coupled)
        == canonical_json_bytes(recorded_coupled)
    )
    rectangle_match = (
        canonical_json_bytes(replay_rectangle)
        == canonical_json_bytes(recorded_rectangle)
    )
    registration_match = result["registration_sha256"] == hashlib.sha256(
        registration_bytes
    ).hexdigest()
    artifact_hashes = {
        path.name: sha256_file(path)
        for path in (result_path, coupled_path, rectangle_path)
    }
    ok = all(
        (
            source_match,
            scientific_match,
            coupled_match,
            rectangle_match,
            registration_match,
            all(result["gates"].values()),
        )
    )
    payload = {
        "schema": "asmp9-v0.46-independent-verification-v1",
        "ok": ok,
        "registration_hash_match": registration_match,
        "source_hashes_match": source_match,
        "scientific_payload_match": scientific_match,
        "coupled_rows_match": coupled_match,
        "rectangle_payload_match": rectangle_match,
        "all_recorded_gates_pass": all(result["gates"].values()),
        "recorded_status": result["status"],
        "artifact_sha256": artifact_hashes,
        "source_checks": source_checks,
    }
    compare_or_write(args.output.resolve(), canonical_json_bytes(payload))
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(not ok)


if __name__ == "__main__":
    main()

