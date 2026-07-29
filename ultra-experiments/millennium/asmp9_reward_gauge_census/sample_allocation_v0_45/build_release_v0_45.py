"""Build write-once receipts and manifest for ASMP-9 v0.45."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ASMP9 = HERE.parent
REPO = HERE.parents[3]


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


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def main() -> None:
    registration = HERE / "registration_v0_45.json"
    result = HERE / "artifacts_v0_45" / "RESULT_v0_45.json"
    verification = HERE / "VERIFY_RESULT_v0_45.json"
    result_payload = json.loads(result.read_text(encoding="utf-8"))
    verification_payload = json.loads(
        verification.read_text(encoding="utf-8")
    )
    registered = json.loads(
        registration.read_text(encoding="utf-8")
    )
    if (
        result_payload["status"]
        != "decision_directed_sample_allocation_established"
    ):
        raise RuntimeError("result is not release-eligible")
    if verification_payload["status"] != "independent_replay_passed":
        raise RuntimeError("independent replay did not pass")
    if not all(result_payload["gates"].values()):
        raise RuntimeError("one or more gates failed")

    receipt = {
        "protocol_id": (
            "asmp9-decision-directed-sample-allocation-v0.45"
        ),
        "version": "0.45",
        "status": result_payload["status"],
        "implementation_commit": registered["implementation_commit"],
        "registration_commit": git("rev-parse", "HEAD"),
        "registration_sha256": sha256(registration),
        "result_sha256": sha256(result),
        "verification_sha256": sha256(verification),
        "gates": result_payload["gates"],
        "elapsed_seconds": result_payload["resource"][
            "elapsed_seconds"
        ],
        "peak_aggregate_working_set_bytes": result_payload[
            "resource"
        ]["peak_aggregate_working_set_bytes"],
        "commands": {
            "execute": (
                "python ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/sample_allocation_v0_45/"
                "run_confirmation_v0_45.py"
            ),
            "verify": (
                "python ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/sample_allocation_v0_45/"
                "verify_result_v0_45.py"
            ),
        },
    }
    receipt_path = HERE / "RUN_RECEIPT_v0_45.json"
    compare_or_write(receipt_path, canonical(receipt))

    files = [
        ASMP9 / "README.md",
        ASMP9 / "RESOLUTION_OBLIGATION_MATRIX_v0_45.md",
        HERE / "PRIOR_ART_GATE_v0_45.md",
        HERE / "PROTOCOL_v0_45.md",
        HERE / "THEOREM_DRAFT_v0_45.md",
        HERE / "RESULT_v0_45.md",
        HERE / "environment_lock_v0_45.json",
        HERE / "allocation_design.py",
        HERE / "audit_formula_universe.py",
        HERE / "test_allocation_design.py",
        HERE / "run_confirmation_v0_45.py",
        HERE / "verify_result_v0_45.py",
        HERE / "register_v0_45.py",
        HERE / "registration_v0_45.json",
        result,
        verification,
        HERE / "build_release_v0_45.py",
        receipt_path,
    ]
    manifest = {
        "protocol_id": (
            "asmp9-decision-directed-sample-allocation-v0.45"
        ),
        "version": "0.45",
        "files": {
            path.relative_to(REPO).as_posix(): {
                "bytes": len(path.read_bytes()),
                "sha256": sha256(path),
            }
            for path in sorted(files)
        },
    }
    compare_or_write(
        HERE / "RELEASE_MANIFEST_v0_45.json",
        canonical(manifest),
    )
    print(
        json.dumps(
            {
                "receipt": receipt_path.relative_to(REPO).as_posix(),
                "manifest_files": len(files),
                "registration_commit": receipt[
                    "registration_commit"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
