"""Versioned parser repair for ASMP-9 v0.42.1 confirmation."""

from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys
import time


BASE = Path(__file__).resolve().parent
PARENT = BASE.parent / "finite_sample_risk_access_v0_42"
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

from execute_confirmation_v0_42 import (  # noqa: E402
    canonical_bytes,
    derive_gates,
    peak_working_set_bytes,
    resolve_status,
    sha256_bytes,
    sha256_file,
)
from sampled_confirmation import run_sampled_confirmation  # noqa: E402


PROTOCOL_ID = "asmp9-finite-sample-risk-access-v0.42.1"
EXPECTED_TESTS = 26


def parse_registered_fraction(value: object) -> float:
    """Parse the registered exact-rational JSON representation."""

    try:
        rational = Q(str(value))
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(
            f"invalid registered rational value: {value!r}"
        ) from error
    if rational < 0:
        raise ValueError("registered margin cannot be negative")
    return float(rational)


def seed_from_registration_bytes(registration_bytes: bytes) -> bytes:
    return hashlib.sha256(
        registration_bytes
        + b"\0asmp9-v0.42.1-sampled-confirmation"
    ).digest()


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
        path = (BASE / relative_path).resolve()
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
        or preflight.get("tests_passed") != EXPECTED_TESTS
    ):
        raise ValueError("registered preflight did not pass")
    sampling = registration.get("sampling")
    if (
        not isinstance(sampling, dict)
        or sampling.get("samples_per_target_query") != 48000
        or sampling.get("targets") != 4
    ):
        raise ValueError("registered sample universe changed")
    for value in registration.get("practical_margins", {}).values():
        parse_registered_fraction(value)
    return registration


def execute(registration_path: Path, output_path: Path) -> dict:
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite {output_path}")
    registration_bytes = registration_path.read_bytes()
    registration = validate_registration(registration_path)
    seed = seed_from_registration_bytes(registration_bytes)
    start = time.perf_counter()
    result = run_sampled_confirmation(
        samples_per_target=registration["sampling"][
            "samples_per_target_query"
        ],
        seed=seed,
        alpha=registration["confidence"]["alpha"],
        practical_margins={
            name: parse_registered_fraction(value)
            for name, value in registration[
                "practical_margins"
            ].items()
        },
    )
    elapsed = time.perf_counter() - start
    peak = peak_working_set_bytes()
    gates = derive_gates(result, registration, elapsed, peak)
    payload = {
        "protocol_id": PROTOCOL_ID,
        "parent_failed_registration_sha256": registration[
            "parent_failed_registration_sha256"
        ],
        "registration_file_sha256": sha256_file(registration_path),
        "registration_implementation_commit": registration[
            "implementation_commit"
        ],
        "elapsed_seconds": elapsed,
        "peak_working_set_bytes": peak,
        "resource_ceiling": registration["resource_ceiling"],
        "sampling": result,
        "gates": gates,
        "status": resolve_status(gates),
    }
    payload["result_content_sha256"] = sha256_bytes(
        canonical_bytes(payload)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("xb") as handle:
        handle.write(canonical_bytes(payload))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registration",
        type=Path,
        default=BASE / "registration_v0_42_1.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE / "artifacts_v0_42_1" / "RESULT_v0_42_1.json",
    )
    args = parser.parse_args()
    payload = execute(args.registration.resolve(), args.output.resolve())
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
