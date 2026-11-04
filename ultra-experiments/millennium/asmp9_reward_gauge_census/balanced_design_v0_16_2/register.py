from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
V016 = HERE.parent / "balanced_design_v0_16"
V0161 = HERE.parent / "balanced_design_v0_16_1"
REPO = HERE.parents[3]

LOCAL_NAMES = (
    "PROTOCOL_v0_16_2.md",
    "README.md",
    "environment_v0_16_2.json",
    "protocol_v0_16_2.json",
    "register.py",
    "run_verification.py",
    "test_protocol.py",
    "test_threshold_search.py",
    "threshold_search.py",
    "verify_result.py",
)

BASE_NAMES = (
    "PRIOR_ART_GATE_v0_16.md",
    "RUN_ABORT_v0_16.json",
    "RUN_ABORT_v0_16.md",
    "THEOREM_v0_16.md",
    "experiment.py",
    "protocol_v0_16.json",
    "registration_v0_16.json",
    "run_verification.py",
    "verify_result.py",
)

V0161_NAMES = (
    "PROTOCOL_v0_16_1.md",
    "REGISTERED_PROGRESS_v0_16_1.json",
    "REGISTERED_START_v0_16_1.json",
    "RUN_ABORT_v0_16_1.json",
    "RUN_ABORT_v0_16_1.md",
    "protocol_v0_16_1.json",
    "registration_v0_16_1.json",
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

    paths = (
        [HERE / name for name in LOCAL_NAMES]
        + [V016 / name for name in BASE_NAMES]
        + [V0161 / name for name in V0161_NAMES]
    )
    sealed = {}
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        sealed[path.relative_to(REPO).as_posix()] = sha256(path)

    protocol_path = HERE / "protocol_v0_16_2.json"
    registration = {
        "registration_id": (
            "ASMP-9-BALANCED-MAXIMIN-DESIGN-v0.16.2-registration"
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
