"""Hash-sealed sampled executor for ASMP-9 finite risk access v0.42."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import time

import psutil

from sampled_confirmation import (
    run_sampled_confirmation,
    seed_from_registration_bytes,
)


BASE = Path(__file__).resolve().parent
PROTOCOL_ID = "asmp9-finite-sample-risk-access-v0.42"
EXPECTED_TESTS = 22


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
    registration_bytes = registration_path.read_bytes()
    registration = json.loads(registration_bytes)
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
    return registration


def peak_working_set_bytes() -> int:
    memory = psutil.Process(os.getpid()).memory_info()
    return int(getattr(memory, "peak_wset", memory.rss))


def resolve_status(gates: dict[str, bool]) -> str:
    if gates.get("H0") is False:
        return "not_established_by_registered_channel_event"
    if gates.get("H0") is True and gates.get("C0") is False:
        return "theorem_or_implementation_failure"
    if gates and all(gates.values()):
        return (
            "finite_sample_sequential_risk_access_"
            "confirmation_established"
        )
    return "registered_gate_failed"


def derive_gates(result: dict, registration: dict, elapsed: float, peak: int):
    arms = {
        (row["decision_problem"], row["mode"]): row
        for row in result["arms"]
    }
    exact_keys = {
        ("4_class_identification", "adaptive"),
        ("4_class_identification", "open_loop"),
        ("root_group_asymmetric", "adaptive"),
        ("root_group_asymmetric", "open_loop"),
    }
    sampling = result["sampling_receipt"]
    u0 = (
        set(sampling) == {"root_q", "left_q", "right_q"}
        and all(
            len(row["flip_counts_by_target"]) == 4
            and row["pooled_trials"] == 192000
            and row["pooled_flips"]
            == sum(row["flip_counts_by_target"])
            for row in sampling.values()
        )
    )
    decisions = {
        key: row["decision"] for key, row in arms.items()
    }
    ceiling = registration["resource_ceiling"]
    return {
        "P0": True,
        "S0": True,
        "U0": u0,
        "H0": bool(result["simultaneous_channel_event_holds"]),
        "C0": bool(result["all_true_deficiencies_contained"]),
        "A0": (
            decisions.get(("4_class_identification", "adaptive"))
            == "pass"
            and decisions.get(
                ("4_class_identification", "open_loop")
            )
            == "fail"
        ),
        "D0": (
            decisions.get(("root_group_asymmetric", "adaptive"))
            == "pass"
            and decisions.get(
                ("root_group_asymmetric", "open_loop")
            )
            == "pass"
        ),
        "R0": set(arms) == exact_keys and len(result["arms"]) == 4,
        "RESOURCE": (
            elapsed <= ceiling["max_wall_seconds"]
            and peak <= ceiling["max_peak_working_set_bytes"]
        ),
    }


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
            name: float(value)
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
        default=BASE / "registration_v0_42.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE / "artifacts_v0_42" / "RESULT_v0_42.json",
    )
    args = parser.parse_args()
    payload = execute(args.registration.resolve(), args.output.resolve())
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
