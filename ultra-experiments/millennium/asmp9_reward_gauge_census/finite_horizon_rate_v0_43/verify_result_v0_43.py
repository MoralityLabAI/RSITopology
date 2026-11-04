"""Independent deterministic replay for the ASMP-9 v0.43 result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent

from run_confirmation_v0_43 import (  # noqa: E402
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
) -> dict:
    registration_bytes = registration_path.read_bytes()
    registration = json.loads(registration_bytes)
    result = json.loads(result_path.read_bytes())
    source_match, source_rows = validate_source_hashes(registration)
    replay_scientific = build_scientific_payload()
    replay_gates = scientific_gates(replay_scientific)

    scientific_match = replay_scientific == result["scientific"]
    gate_matches = {
        name: result["gates"].get(name) == value
        for name, value in replay_gates.items()
    }
    structural = {
        "protocol_id": result.get("protocol_id") == PROTOCOL_ID,
        "version": result.get("version") == VERSION,
        "registration_sha256": (
            result.get("registration_sha256")
            == sha256_bytes(registration_bytes)
        ),
        "source_hashes": source_match,
        "scientific_payload": scientific_match,
        "scientific_gates": all(gate_matches.values()),
    }
    recorded_gates = result["gates"]
    status_match = result["status"] == total_status(recorded_gates)
    all_pass = all(structural.values()) and status_match
    return {
        "status": (
            "independent_replay_passed"
            if all_pass
            else "independent_replay_failed"
        ),
        "checks": structural,
        "status_mapping": status_match,
        "gate_matches": gate_matches,
        "source_checks": source_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registration",
        type=Path,
        default=HERE / "registration_v0_43.json",
    )
    parser.add_argument(
        "--result",
        type=Path,
        default=HERE / "artifacts_v0_43" / "RESULT_v0_43.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "VERIFY_RESULT_v0_43.json",
    )
    args = parser.parse_args()
    payload = verify(
        args.registration.resolve(), args.result.resolve()
    )
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    raise SystemExit(payload["status"] != "independent_replay_passed")


if __name__ == "__main__":
    main()
