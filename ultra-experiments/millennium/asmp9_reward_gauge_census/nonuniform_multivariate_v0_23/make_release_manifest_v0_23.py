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
PREDECESSOR = HERE.parent / "uniform_above_floor_v0_22_1"
AUDITS = (
    HERE.parent / "RESOLUTION_AUDIT_v0_22_1.md",
    HERE.parent / "RESOLUTION_AUDIT_v0_23.md",
)
FELLOWSHIP = REPO / "docs/ILIAD_FELLOWSHIP_RESEARCH_LINKS_20260727.md"
PROGRAM_README = HERE.parent / "README.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
    ).strip()


def write_json_exclusive(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("tracked tree must be clean")

    files = [
        path
        for root in (PREDECESSOR, HERE)
        for path in root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.resolve() != output
    ]
    files.extend((*AUDITS, FELLOWSHIP, PROGRAM_README))
    unique = sorted({path.resolve() for path in files})
    manifest = {
        "created_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "file_count": len(unique),
        "files": {
            path.relative_to(REPO).as_posix(): sha256(path)
            for path in unique
        },
        "release_commit": git("rev-parse", "HEAD"),
        "release_id": "ASMP-9-NONUNIFORM-MULTIVARIATE-v0.23-release",
        "scope": (
            "v0.22.1 predecessor, registered v0.23 protocol and exact "
            "artifacts, independent verification, resolution audits, "
            "program map, and fellowship dossier"
        ),
    }
    write_json_exclusive(output, manifest)
    print(
        json.dumps(
            {
                "file_count": manifest["file_count"],
                "release_commit": manifest["release_commit"],
                "sha256": sha256(output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
