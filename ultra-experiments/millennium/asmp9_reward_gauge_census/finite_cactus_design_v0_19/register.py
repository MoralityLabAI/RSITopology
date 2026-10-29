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

LOCAL_NAMES = (
    "DEVELOPMENT_NOTE_v0_19.md",
    "PRIOR_ART_GATE_v0_19.md",
    "PROTOCOL_v0_19.md",
    "README.md",
    "THEORY_DRAFT_v0_19.md",
    "finite_cactus_design.py",
    "protocol_v0_19.json",
    "register.py",
    "run_verification.py",
    "test_finite_cactus_design.py",
    "test_protocol.py",
    "verify_result.py",
)

DEPENDENCIES = (
    "ultra-experiments/millennium/"
    "AI_SAFETY_MILLENNIUM_PROBLEMS_v0_1.md",
    "ultra-experiments/millennium/"
    "asmp9_reward_gauge_census/README.md",
    "ultra-experiments/millennium/"
    "asmp9_reward_gauge_census/balanced_design_v0_16/"
    "THEOREM_v0_16.md",
    "ultra-experiments/millennium/"
    "asmp9_reward_gauge_census/balanced_design_v0_16_2/"
    "release_manifest_v0_16_2.json",
    "ultra-experiments/millennium/"
    "asmp9_reward_gauge_census/bond_design_v0_18/"
    "PUBLIC_SUMMARY_v0_18.md",
    "ultra-experiments/millennium/"
    "asmp9_reward_gauge_census/bond_design_v0_18/"
    "release_manifest_v0_18.json",
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
        REPO / relative for relative in DEPENDENCIES
    ]
    sealed: dict[str, str] = {}
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
        "registration_id": (
            "ASMP-9-FINITE-CACTUS-DESIGN-v0.19-registration"
        ),
        "registered_at_utc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "implementation_commit": git("rev-parse", "HEAD"),
        "protocol_path": (
            HERE / "protocol_v0_19.json"
        ).relative_to(REPO).as_posix(),
        "sealed_files": sealed,
    }
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
