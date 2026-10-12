from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from coverage_robustness import build_result, validate_protocol


HERE = Path(__file__).resolve().parent
SOURCE_FILES = (
    "protocol_v0_3.json",
    "PROTOCOL_v0_3.md",
    "README.md",
    "coverage_robustness.py",
    "run.py",
    "verify_result.py",
    "test_coverage_robustness.py",
)
PROTOCOL_PATH = HERE / "protocol_v0_3.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=HERE / "artifacts_v0_3")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    result_path = args.output_dir / "result.json"
    receipt_path = args.output_dir / "receipt.json"
    if (result_path.exists() or receipt_path.exists()) and not args.force:
        raise RuntimeError("output exists; use --force for an explicit replay")

    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    protocol_binding = validate_protocol(protocol)
    result = build_result()
    write_json(result_path, result)
    receipt = {
        "schema_version": "asmp7_coverage_robustness_run_receipt_v0_3_1",
        "experiment_id": result["experiment_id"],
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "result_sha256": sha256_file(result_path),
        "source_hashes": {name: sha256_file(HERE / name) for name in SOURCE_FILES},
        "protocol_binding": protocol_binding,
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "arithmetic": "integer binomial masses and fractions.Fraction",
            "gpu": "not used",
        },
    }
    write_json(receipt_path, receipt)
    print(
        json.dumps(
            {
                "task_result": result["task_result"],
                "measurement_reliability": result["measurement_reliability"],
                "claim_support": result["claim_support"],
                "operational_decision": result["operational_decision"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
