"""Build compare-or-fail run receipt and release manifest for v0.42.1."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


BASE = Path(__file__).resolve().parent
PARENT = BASE.parent / "finite_sample_risk_access_v0_42"
ASMP9 = BASE.parent
RESULT = BASE / "artifacts_v0_42_1" / "RESULT_v0_42_1.json"
VERIFY = BASE / "VERIFY_RESULT_v0_42_1.json"
REGISTRATION = BASE / "registration_v0_42_1.json"
RECEIPT = BASE / "RUN_RECEIPT_v0_42_1.json"
MANIFEST = BASE / "RELEASE_MANIFEST_v0_42_1.json"


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_once(path: Path, payload: object) -> None:
    content = canonical_bytes(payload)
    if path.exists():
        if path.read_bytes() != content:
            raise FileExistsError(f"{path} exists with different bytes")
        return
    with path.open("xb") as handle:
        handle.write(content)


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=BASE,
        text=True,
    ).strip()


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    verify = json.loads(VERIFY.read_text(encoding="utf-8"))
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if result["status"] != (
        "finite_sample_sequential_risk_access_"
        "confirmation_established"
    ):
        raise ValueError("result status is not releasable")
    if not all(result["gates"].values()):
        raise ValueError("not every registered gate passed")
    if verify["status"] != "independent_replay_passed":
        raise ValueError("independent replay did not pass")
    receipt = {
        "protocol_id": result["protocol_id"],
        "version": "0.42.1",
        "repair_implementation_commit": registration[
            "implementation_commit"
        ],
        "repair_registration_commit": git_head(),
        "parent_failed_registration_sha256": result[
            "parent_failed_registration_sha256"
        ],
        "registration_sha256": sha256_file(REGISTRATION),
        "result_file_sha256": sha256_file(RESULT),
        "result_content_sha256": result["result_content_sha256"],
        "verify_file_sha256": sha256_file(VERIFY),
        "status": result["status"],
        "gates": result["gates"],
        "elapsed_seconds": result["elapsed_seconds"],
        "peak_working_set_bytes": result["peak_working_set_bytes"],
        "commands": {
            "execute": (
                "python ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "finite_sample_risk_access_v0_42_1/"
                "execute_confirmation_v0_42_1.py"
            ),
            "verify": (
                "python ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "finite_sample_risk_access_v0_42_1/"
                "verify_result_v0_42_1.py"
            ),
        },
    }
    write_once(RECEIPT, receipt)
    files = (
        PARENT / "FAILED_EXECUTION_v0_42.json",
        PARENT / "FAILED_EXECUTION_v0_42.md",
        PARENT / "PRIOR_ART_GATE_v0_42.md",
        PARENT / "PROTOCOL_v0_42.md",
        PARENT / "THEOREM_DRAFT_v0_42.md",
        PARENT / "confirmation.stderr.log",
        PARENT / "finite_sample_access.py",
        PARENT / "registration_v0_42.json",
        PARENT / "sampled_confirmation.py",
        ASMP9 / "README.md",
        ASMP9 / "RESOLUTION_OBLIGATION_MATRIX_v0_42.md",
        BASE / "PROTOCOL_AMENDMENT_v0_42_1.md",
        BASE / "RESULT_v0_42_1.md",
        BASE / "build_release_v0_42_1.py",
        BASE / "environment_lock_v0_42_1.json",
        BASE / "execute_confirmation_v0_42_1.py",
        BASE / "protocol_v0_42_1.json",
        BASE / "register_v0_42_1.py",
        BASE / "registration_v0_42_1.json",
        BASE / "test_repair_v0_42_1.py",
        BASE / "verify_result_v0_42_1.py",
        BASE / "write_environment_lock_v0_42_1.py",
        RESULT,
        VERIFY,
        RECEIPT,
    )
    manifest = {
        "protocol_id": result["protocol_id"],
        "version": "0.42.1",
        "file_count": len(files),
        "files": {
            str(path.relative_to(ASMP9)).replace("\\", "/"): {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in files
        },
    }
    write_once(MANIFEST, manifest)
    print(RECEIPT)
    print(MANIFEST)


if __name__ == "__main__":
    main()
