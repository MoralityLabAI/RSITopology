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
    registration = json.loads(
        args.registration.read_text(encoding="utf-8")
    )
    result = json.loads(
        (args.artifact_dir / "result_v0_6.json").read_text(encoding="utf-8")
    )
    receipt = json.loads(
        (args.artifact_dir / "receipt_v0_6.json").read_text(encoding="utf-8")
    )
    checks = {
        "registration_hash": sha256(args.registration)
        == result["registration_sha256"]
        == receipt["registration_sha256"],
        "sealed_inputs": all(
            sha256(REPO / path) == expected
            for path, expected in registration["sealed_files"].items()
        ),
        "output_hashes": all(
            sha256(args.artifact_dir / name) == expected
            for name, expected in receipt["output_hashes"].items()
        ),
        "all_gates_pass": all(result["gates"].values()),
        "verdict": result["verdict"]
        == "discounted_shaping_gain_quotient_implementation_verified",
    }
    verdict = "verified" if all(checks.values()) else "not_verified"
    print(json.dumps({"checks": checks, "verdict": verdict}, indent=2))
    raise SystemExit(0 if verdict == "verified" else 1)


if __name__ == "__main__":
    main()
