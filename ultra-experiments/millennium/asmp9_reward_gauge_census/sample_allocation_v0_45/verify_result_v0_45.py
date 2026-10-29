"""Independent deterministic replay for ASMP-9 v0.45."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent

from run_confirmation_v0_45 import (  # noqa: E402
    PROTOCOL_ID,
    VERSION,
    build_scientific_payload,
    scientific_gates,
    sha256_bytes,
    total_status,
    validate_source_hashes,
)


def verify(
    registration_path: Path,
    result_path: Path,
    workers: int,
) -> dict:
    registration_bytes = registration_path.read_bytes()
    registration = json.loads(registration_bytes)
    result = json.loads(result_path.read_bytes())
    source_match, source_rows = validate_source_hashes(registration)
    replay_scientific = build_scientific_payload(workers)
    replay_gates = scientific_gates(replay_scientific)
    gate_matches = {
        name: result["gates"].get(name) == value
        for name, value in replay_gates.items()
    }
    checks = {
        "protocol_id": result.get("protocol_id") == PROTOCOL_ID,
        "version": result.get("version") == VERSION,
        "registration_sha256": (
            result.get("registration_sha256")
            == sha256_bytes(registration_bytes)
        ),
        "source_hashes": source_match,
        "scientific_payload": (
            replay_scientific == result["scientific"]
        ),
        "scientific_gates": all(gate_matches.values()),
    }
    status_mapping = result["status"] == total_status(
        result["gates"]
    )
    passed = all(checks.values()) and status_mapping
    return {
        "status": (
            "independent_replay_passed"
            if passed
            else "independent_replay_failed"
        ),
        "checks": checks,
        "status_mapping": status_mapping,
        "gate_matches": gate_matches,
        "source_checks": source_rows,
        "workers": workers,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_45.json",
    )
    parser.add_argument(
        "--result",
        type=Path,
        default=HERE / "artifacts_v0_45" / "RESULT_v0_45.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "VERIFY_RESULT_v0_45.json",
    )
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    payload = verify(
        args.registration.resolve(),
        args.result.resolve(),
        args.workers,
    )
    args.output.write_bytes(
        (
            json.dumps(payload, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(
        payload["status"] != "independent_replay_passed"
    )


if __name__ == "__main__":
    main()
