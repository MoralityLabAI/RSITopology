"""Independent replay checks for the ASMP-9 v0.42 sampled result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from execute_confirmation_v0_42 import (
    derive_gates,
    resolve_status,
    sha256_file,
    validate_registration,
)
from sampled_confirmation import (
    run_sampled_confirmation,
    seed_from_registration_bytes,
)


BASE = Path(__file__).resolve().parent


def verify(registration_path: Path, result_path: Path) -> dict:
    registration_bytes = registration_path.read_bytes()
    registration = validate_registration(registration_path)
    stored = json.loads(result_path.read_text(encoding="utf-8"))
    replay = run_sampled_confirmation(
        samples_per_target=registration["sampling"][
            "samples_per_target_query"
        ],
        seed=seed_from_registration_bytes(registration_bytes),
        alpha=registration["confidence"]["alpha"],
        practical_margins={
            name: float(value)
            for name, value in registration[
                "practical_margins"
            ].items()
        },
    )
    replay_gates = derive_gates(
        replay,
        registration,
        elapsed=0.0,
        peak=0,
    )
    nonresource_stored = {
        key: value
        for key, value in stored["gates"].items()
        if key != "RESOURCE"
    }
    nonresource_replay = {
        key: value
        for key, value in replay_gates.items()
        if key != "RESOURCE"
    }
    checks = {
        "registration_hash": (
            stored["registration_file_sha256"]
            == sha256_file(registration_path)
        ),
        "sampled_payload_exact_replay": stored["sampling"] == replay,
        "nonresource_gates_exact_replay": (
            nonresource_stored == nonresource_replay
        ),
        "stored_status_matches_gates": (
            stored["status"] == resolve_status(stored["gates"])
        ),
        "resource_gate_passed": stored["gates"]["RESOURCE"] is True,
    }
    return {
        "status": (
            "independent_replay_passed"
            if all(checks.values())
            else "independent_replay_failed"
        ),
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registration",
        type=Path,
        default=BASE / "registration_v0_42.json",
    )
    parser.add_argument(
        "--result",
        type=Path,
        default=BASE / "artifacts_v0_42" / "RESULT_v0_42.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE / "VERIFY_RESULT_v0_42.json",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    payload = verify(args.registration.resolve(), args.result.resolve())
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["status"] != "independent_replay_passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
