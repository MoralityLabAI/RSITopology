from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ordinal_frontier import sha256_file  # noqa: E402
from run import compute_experiment, load_json, repo_root  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()

    registration_path = args.registration.resolve()
    artifact_dir = args.artifact_dir.resolve()
    registration = load_json(registration_path)
    receipt = load_json(artifact_dir / "receipt_v0_2.json")
    result = load_json(artifact_dir / "result_v0_2.json")

    checks: dict[str, bool] = {}
    checks["registration_hash"] = (
        receipt["registration_sha256"] == sha256_file(registration_path)
        == result["registration_sha256"]
    )
    checks["sealed_inputs"] = all(
        sha256_file(repo_root() / relative) == expected
        for relative, expected in registration["sealed_files"].items()
    )
    checks["output_hashes"] = all(
        sha256_file(artifact_dir / name) == expected
        for name, expected in receipt["outputs"].items()
    )

    protocol = load_json(repo_root() / registration["protocol_path"])
    cells, thresholds, gates, verdict = compute_experiment(protocol)
    checks["recomputed_verdict"] = verdict == result["verdict"]
    checks["recomputed_gates"] = gates == result["gates"]
    checks["recomputed_thresholds"] = thresholds == result["thresholds"]

    with (artifact_dir / "frontier_cells_v0_2.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        stored_cells = list(csv.DictReader(handle))
    checks["cell_count"] = len(stored_cells) == len(cells) == result["cell_count"]

    payload = {
        "verdict": "verified" if all(checks.values()) else "verification_failed",
        "checks": checks,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

