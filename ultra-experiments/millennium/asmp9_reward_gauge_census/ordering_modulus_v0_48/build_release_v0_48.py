"""Build the ASMP-9 v0.48 release manifest after verification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

RELEASE_FILES = (
    "README.md",
    "PRIOR_ART_GATE_v0_48.md",
    "PROTOCOL_v0_48.md",
    "THEOREM_DRAFT_v0_48.md",
    "environment_lock_v0_48.json",
    "ordering_modulus.py",
    "test_ordering_modulus.py",
    "run_confirmation_v0_48.py",
    "verify_result_v0_48.py",
    "registration_v0_48.json",
    "artifacts_v0_48/experiment_rows_v0_48.json",
    "artifacts_v0_48/subset_bounds_v0_48.json",
    "artifacts_v0_48/result_v0_48.json",
    "VERIFY_RESULT_v0_48.json",
    "RESULT_v0_48.md",
    "RUN_RECEIPT_v0_48.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rows = []
    for relative in RELEASE_FILES:
        path = HERE / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    payload = {
        "schema": "asmp9-v0.48-release-manifest-v1",
        "files": rows,
    }
    encoded = (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    output = HERE / "RELEASE_MANIFEST_v0_48.json"
    if output.exists() and output.read_bytes() != encoded:
        raise RuntimeError("release manifest write-once mismatch")
    output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "path": output.relative_to(REPO).as_posix(),
                "files": len(rows),
                "sha256": hashlib.sha256(encoded).hexdigest(),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
