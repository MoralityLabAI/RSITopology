from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SEALED_PATHS = (
    HERE.parent / "FAILURE_v0_31.md",
    HERE.parent / "failure_receipt_v0_31.json",
    HERE.parent / "registration_v0_31.json",
    HERE.parent / "run_verification_v0_31.py",
    HERE.parent / "verify_result_v0_31.py",
    HERE / "README.md",
    HERE / "__init__.py",
    HERE / "environment_lock_v0_31_1.json",
    HERE / "protocol_v0_31_1.json",
    HERE / "register_repair_v0_31_1.py",
    HERE / "run_repair_v0_31_1.py",
    HERE / "test_repair_v0_31_1.py",
    HERE / "verify_repair_v0_31_1.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("tracked tree must be clean before repair registration")
    sealed = {}
    for path in SEALED_PATHS:
        relative = path.relative_to(REPO).as_posix()
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", relative],
            cwd=REPO,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        sealed[relative] = sha256(path)
    value = {
        "implementation_commit": git("rev-parse", "HEAD"),
        "protocol_path": (HERE / "protocol_v0_31_1.json")
        .relative_to(REPO)
        .as_posix(),
        "registered_at_utc": utc_now(),
        "registration_id": (
            "ASMP-9-JOINT-APPROXIMATE-v0.31.1-resource-repair-registration"
        ),
        "sealed_files": sealed,
    }
    write_json_exclusive(args.output, value)
    print(
        json.dumps(
            {
                "implementation_commit": value["implementation_commit"],
                "registration_sha256": sha256(args.output),
                "sealed_file_count": len(sealed),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
