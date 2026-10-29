from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SEALED_NAMES = (
    "DEVELOPMENT_NOTE_v0_31.md",
    "PRIOR_ART_GATE_v0_31.md",
    "README.md",
    "THEOREM_DRAFT_v0_31.md",
    "__init__.py",
    "environment_lock_v0_31.json",
    "joint_approximate.py",
    "protocol_v0_31.json",
    "register_v0_31.py",
    "run_verification_v0_31.py",
    "test_joint_approximate.py",
    "test_protocol_v0_31.py",
    "verify_result_v0_31.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("tracked tree must be clean before registration")
    sealed = {}
    for name in SEALED_NAMES:
        path = HERE / name
        relative = path.relative_to(REPO).as_posix()
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", relative],
            cwd=REPO,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        sealed[relative] = sha256(path)
    registration = {
        "implementation_commit": git("rev-parse", "HEAD"),
        "protocol_path": (HERE / "protocol_v0_31.json")
        .relative_to(REPO)
        .as_posix(),
        "registered_at_utc": utc_now(),
        "registration_id": "ASMP-9-JOINT-APPROXIMATE-v0.31-registration",
        "sealed_files": sealed,
    }
    write_json_exclusive(args.output, registration)
    print(
        json.dumps(
            {
                "implementation_commit": registration["implementation_commit"],
                "registration_sha256": sha256(args.output),
                "sealed_file_count": len(sealed),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
