from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "release_manifest_v0_25.json"

INCLUDED = (
    "DEVELOPMENT_NOTE_v0_25.md",
    "POSTRUN_NOTE_v0_25.md",
    "PRIOR_ART_GATE_v0_25.md",
    "PUBLIC_SUMMARY_v0_25.md",
    "README.md",
    "THEORY_DRAFT_v0_25.md",
    "artifacts_v0_25/independent_verification_v0_25.json",
    "artifacts_v0_25/result_v0_25.json",
    "artifacts_v0_25/run_receipt_v0_25.json",
    "environment_lock_v0_25.json",
    "make_release_manifest_v0_25.py",
    "protocol_v0_25.json",
    "register_v0_25.py",
    "registration_v0_25.json",
    "run_verification_v0_25.py",
    "test_protocol_v0_25.py",
    "test_theta_optimizer_v0_25.py",
    "theta_optimizer.py",
    "verify_result_v0_25.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    missing = [name for name in INCLUDED if not (HERE / name).is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    manifest = {
        "file_count": len(INCLUDED),
        "files": {
            name: sha256(HERE / name)
            for name in sorted(INCLUDED)
        },
        "generated_at_utc": (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        ),
        "manifest_id": "ASMP-9-THETA-OPTIMIZER-v0.25-release",
    }
    with OUTPUT.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "file_count": manifest["file_count"],
                "manifest_sha256": sha256(OUTPUT),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
