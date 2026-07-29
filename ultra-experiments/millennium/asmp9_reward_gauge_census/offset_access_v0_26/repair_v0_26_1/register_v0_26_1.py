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
LOCAL_NAMES = (
    "README.md",
    "adjudicate_v0_26_1.py",
    "protocol_v0_26_1.json",
    "register_v0_26_1.py",
    "test_repair_v0_26_1.py",
    "verify_repair_v0_26_1.py",
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
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("tracked tree must be clean before registration")

    protocol = json.loads((HERE / "protocol_v0_26_1.json").read_text())
    paths = [HERE / name for name in LOCAL_NAMES] + [
        REPO / source["path"]
        for source in protocol["source_artifacts"].values()
    ]
    sealed = {}
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
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
        "protocol_path": (HERE / "protocol_v0_26_1.json")
        .relative_to(REPO)
        .as_posix(),
        "registered_at_utc": utc_now(),
        "registration_id": "ASMP-9-OFFSET-ACCESS-v0.26.1-registration",
        "sealed_files": sealed,
    }
    write_json_exclusive(output, registration)
    print(
        json.dumps(
            {
                "implementation_commit": registration["implementation_commit"],
                "registration_sha256": sha256(output),
                "sealed_file_count": len(sealed),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
