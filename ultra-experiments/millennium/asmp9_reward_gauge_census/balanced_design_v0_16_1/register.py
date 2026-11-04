from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "balanced_design_v0_16"
REPO = HERE.parents[3]

LOCAL_NAMES = (
    "PROTOCOL_v0_16_1.md",
    "README.md",
    "environment_v0_16_1.json",
    "protocol_v0_16_1.json",
    "register.py",
    "run_verification.py",
    "test_protocol.py",
    "verify_result.py",
)

BASE_NAMES = (
    "PRIOR_ART_GATE_v0_16.md",
    "RUN_ABORT_v0_16.json",
    "RUN_ABORT_v0_16.md",
    "THEOREM_v0_16.md",
    "experiment.py",
    "run_verification.py",
    "verify_result.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def write_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite registration: {output}")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("tracked tree must be clean before registration")

    paths = [HERE / name for name in LOCAL_NAMES] + [
        BASE / name for name in BASE_NAMES
    ]
    sealed = {}
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        sealed[path.relative_to(REPO).as_posix()] = sha256(path)

    protocol_path = HERE / "protocol_v0_16_1.json"
    registration = {
        "registration_id": (
            "ASMP-9-BALANCED-MAXIMIN-DESIGN-v0.16.1-registration"
        ),
        "registered_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "implementation_commit": git("rev-parse", "HEAD"),
        "protocol_path": protocol_path.relative_to(REPO).as_posix(),
        "sealed_files": sealed,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, registration)
    print(
        json.dumps(
            {
                "implementation_commit": registration[
                    "implementation_commit"
                ],
                "registration_sha256": sha256(output),
                "sealed_file_count": len(sealed),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
