from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_verification import load_json, repo_root, sha256_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    registration_path = args.registration.resolve()
    artifact_dir = args.artifact_dir.resolve()
    registration = load_json(registration_path)
    result = load_json(artifact_dir / "result_v0_4.json")
    receipt = load_json(artifact_dir / "receipt_v0_4.json")
    checks = {
        "registration_hash": (
            result["registration_sha256"]
            == receipt["registration_sha256"]
            == sha256_file(registration_path)
        ),
        "sealed_inputs": all(
            sha256_file(repo_root() / relative) == expected
            for relative, expected in registration["sealed_files"].items()
        ),
        "output_hashes": all(
            sha256_file(artifact_dir / name) == expected
            for name, expected in receipt["output_hashes"].items()
        ),
        "all_gates_pass": all(result["gates"].values()),
        "verdict": (
            result["verdict"]
            == "sharp_exact_tie_width_theorem_implementation_verified"
        ),
    }
    print(
        json.dumps(
            {
                "verdict": (
                    "verified" if all(checks.values()) else "verification_failed"
                ),
                "checks": checks,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

