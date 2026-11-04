from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    registration_path = args.registration.resolve()
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    artifact_dir = args.artifact_dir.resolve()
    result = json.loads(
        (artifact_dir / "result_v0_11_1.json").read_text(encoding="utf-8")
    )
    receipt = json.loads(
        (artifact_dir / "receipt_v0_11_1.json").read_text(encoding="utf-8")
    )
    protocol = json.loads(
        (REPO / registration["protocol_path"]).read_text(encoding="utf-8")
    )
    checks = {
        "registration_hash": (
            sha256(registration_path)
            == receipt["registration_sha256"]
            == result["registration_sha256"]
        ),
        "sealed_inputs": all(
            sha256(REPO / relative) == expected
            for relative, expected in registration["sealed_files"].items()
        ),
        "output_hashes": all(
            sha256(artifact_dir / name) == expected
            for name, expected in receipt["output_hashes"].items()
        ),
        "output_hash_universe": set(receipt["output_hashes"])
        == {"result_v0_11_1.json", "RESULT_v0_11_1.md"},
        "protocol_identity": (
            result["protocol_id"] == receipt["protocol_id"] == protocol["protocol_id"]
        ),
        "registration_commit": (
            result["registration_commit"] == receipt["registration_commit"]
        ),
        "implementation_commit": (
            receipt["implementation_commit"] == registration["implementation_commit"]
        ),
        "binding_checks": all(result["binding_checks"].values()),
        "all_gates_pass": all(result["gates"].values()),
        "verdict": result["verdict"] == protocol["success_verdict"],
    }
    verdict = "verified" if all(checks.values()) else "invalid"
    print(json.dumps({"checks": checks, "verdict": verdict}, indent=2))
    raise SystemExit(0 if verdict == "verified" else 1)


if __name__ == "__main__":
    main()
