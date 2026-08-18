from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
EXPECTED_ID = "ASMP-9-BEHAVIORAL-RECTANGLE-v0.32-release"
EXPECTED_VERDICT = "behavioral_rectangle_boundary_established_v0_32"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=HERE / "artifacts_v0_32" / "release_manifest_v0_32.json",
    )
    args = parser.parse_args()

    manifest = load(args.manifest)
    registration_path = HERE / "registration_v0_32.json"
    result_path = HERE / "artifacts_v0_32" / "result_v0_32.json"
    receipt_path = HERE / "artifacts_v0_32" / "run_receipt_v0_32.json"
    independent_path = (
        HERE / "artifacts_v0_32" / "independent_verification_v0_32.json"
    )
    registration = load(registration_path)
    result = load(result_path)
    receipt = load(receipt_path)
    independent = load(independent_path)
    artifacts = manifest["artifacts"]
    execution = manifest["execution"]

    checks = {
        "manifest_id": manifest["manifest_id"] == EXPECTED_ID,
        "artifact_count": manifest["artifact_count"] == len(artifacts),
        "paths_are_canonical": all(
            "\\" not in relative
            and not relative.startswith("/")
            and ".." not in Path(relative).parts
            for relative in artifacts
        ),
        "all_artifact_hashes": all(
            (REPO / relative).is_file()
            and sha256(REPO / relative) == expected
            for relative, expected in artifacts.items()
        ),
        "all_registration_seals": all(
            relative in artifacts
            and artifacts[relative] == expected
            and sha256(REPO / relative) == expected
            for relative, expected in registration["sealed_files"].items()
        ),
        "implementation_commit": execution["implementation_commit"]
        == registration["implementation_commit"]
        == receipt["implementation_commit"],
        "registration_commit": execution["registration_commit"]
        == receipt["run_commit"],
        "registration_hash": execution["registration_sha256"]
        == sha256(registration_path)
        == receipt["registration_sha256"],
        "result_hash": execution["result_sha256"]
        == sha256(result_path)
        == receipt["result_sha256"],
        "receipt_hash": execution["run_receipt_sha256"]
        == sha256(receipt_path),
        "independent_hash": execution["independent_verification_sha256"]
        == sha256(independent_path),
        "independent_references": independent["pass"]
        and independent["result_sha256"] == sha256(result_path)
        and independent["receipt_sha256"] == sha256(receipt_path),
        "chronology": registration["registered_at_utc"]
        == receipt["registered_at_utc"]
        < receipt["started_at_utc"]
        <= receipt["finished_at_utc"],
        "verdict": manifest["verdict"]
        == result["verdict"]
        == receipt["verdict"]
        == EXPECTED_VERDICT,
    }
    report = {
        "check_count": len(checks),
        "checks": checks,
        "manifest_sha256": sha256(args.manifest),
        "pass": all(checks.values()),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
