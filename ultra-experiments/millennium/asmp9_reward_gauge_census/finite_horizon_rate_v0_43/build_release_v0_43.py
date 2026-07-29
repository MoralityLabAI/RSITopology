"""Build compare-or-fail receipt and manifest for ASMP-9 v0.43."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ASMP9 = HERE.parent
REPO = HERE.parents[3]

IMPLEMENTATION_COMMIT = "6319aad7fdb1fef94d1c25abe1d2d6cc56680b07"
REGISTRATION_COMMIT = "f20705d22a99072c3d61b0c43ba483d43d176385"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def compare_or_write(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise RuntimeError(f"write-once mismatch: {path}")
        return
    path.write_bytes(data)


def main() -> None:
    registration = HERE / "registration_v0_43.json"
    result = HERE / "artifacts_v0_43" / "RESULT_v0_43.json"
    verification = HERE / "VERIFY_RESULT_v0_43.json"
    result_payload = json.loads(result.read_text(encoding="utf-8"))
    verification_payload = json.loads(
        verification.read_text(encoding="utf-8")
    )
    if (
        result_payload["status"]
        != "finite_horizon_rate_characterization_established"
    ):
        raise RuntimeError("result status is not release-eligible")
    if verification_payload["status"] != "independent_replay_passed":
        raise RuntimeError("independent replay did not pass")

    receipt = {
        "protocol_id": "asmp9-finite-horizon-rate-v0.43",
        "version": "0.43",
        "status": result_payload["status"],
        "implementation_commit": IMPLEMENTATION_COMMIT,
        "registration_commit": REGISTRATION_COMMIT,
        "registration_sha256": sha256(registration),
        "result_sha256": sha256(result),
        "verification_sha256": sha256(verification),
        "gates": result_payload["gates"],
        "elapsed_seconds": result_payload["resource"]["elapsed_seconds"],
        "peak_working_set_bytes": result_payload["resource"][
            "peak_working_set_bytes"
        ],
        "commands": {
            "execute": (
                "python ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/finite_horizon_rate_v0_43/"
                "run_confirmation_v0_43.py"
            ),
            "verify": (
                "python ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/finite_horizon_rate_v0_43/"
                "verify_result_v0_43.py"
            ),
        },
    }
    receipt_path = HERE / "RUN_RECEIPT_v0_43.json"
    compare_or_write(receipt_path, canonical(receipt))

    files = [
        ASMP9 / "README.md",
        ASMP9 / "RESOLUTION_OBLIGATION_MATRIX_v0_43.md",
        HERE / "PRIOR_ART_GATE_v0_43.md",
        HERE / "PROTOCOL_v0_43.md",
        HERE / "THEOREM_DRAFT_v0_43.md",
        HERE / "RESULT_v0_43.md",
        HERE / "environment_lock_v0_43.json",
        HERE / "rate_theorem.py",
        HERE / "test_rate_theorem.py",
        HERE / "run_confirmation_v0_43.py",
        HERE / "verify_result_v0_43.py",
        HERE / "registration_v0_43.json",
        result,
        verification,
        HERE / "build_release_v0_43.py",
        receipt_path,
    ]
    manifest = {
        "protocol_id": "asmp9-finite-horizon-rate-v0.43",
        "version": "0.43",
        "files": {
            path.relative_to(REPO).as_posix(): {
                "bytes": len(path.read_bytes()),
                "sha256": sha256(path),
            }
            for path in sorted(files)
        },
    }
    compare_or_write(
        HERE / "RELEASE_MANIFEST_v0_43.json",
        canonical(manifest),
    )
    print(
        json.dumps(
            {
                "receipt": receipt_path.relative_to(REPO).as_posix(),
                "manifest_files": len(files),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
