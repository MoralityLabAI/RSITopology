"""Write-once environment receipt for the ASMP-9 v0.42 registration."""

from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys


BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "environment_lock_v0_42.json"
PACKAGES = ("numpy", "psutil", "pytest", "scipy")


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=BASE,
        text=True,
    ).strip()


def payload() -> dict:
    return {
        "implementation_commit": git_head(),
        "platform": platform.platform(),
        "python_executable": str(Path(sys.executable).resolve()),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "packages": {
            name: importlib.metadata.version(name) for name in PACKAGES
        },
    }


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def main() -> None:
    content = canonical_bytes(payload())
    if OUTPUT.exists():
        if OUTPUT.read_bytes() != content:
            raise FileExistsError(
                f"environment lock exists with different bytes: {OUTPUT}"
            )
        print(OUTPUT)
        return
    with OUTPUT.open("xb") as handle:
        handle.write(content)
    print(OUTPUT)


if __name__ == "__main__":
    main()
