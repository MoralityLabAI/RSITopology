"""Create the outcome-blind ASMP-9 v0.36 registration."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from typing import Any, Mapping


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
DEFAULT_OUTPUT = HERE / "REGISTRATION_v0_36.json"

IMPLEMENTATION_PATHS = {
    "confusability": HERE / "confusability.py",
    "runner": HERE / "run_census.py",
    "verifier": HERE / "verify_result.py",
    "tests": HERE / "test_confusability.py",
    "registration_builder": HERE / "prepare_registration.py",
}

DOCUMENT_PATHS = {
    "protocol": HERE / "PROTOCOL_v0_36.json",
    "theorem_note": HERE / "THEOREM_NOTE_v0_36.md",
    "prior_art": HERE / "PRIOR_ART_v0_36.md",
    "readme": HERE / "README.md",
}


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=REPO,
        text=True,
    ).strip()


def file_record(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return {
        "path": resolved.relative_to(REPO.resolve()).as_posix(),
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def compare_or_fail(path: Path, payload: Mapping[str, Any]) -> None:
    data = canonical_bytes(payload)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"refusing unequal registration: {path}")
        return
    path.write_bytes(data)


def build_registration() -> dict[str, Any]:
    protocol = json.loads(
        DOCUMENT_PATHS["protocol"].read_text(encoding="utf-8")
    )
    commit = git("rev-parse", "HEAD")
    payload: dict[str, Any] = {
        "schema_version": (
            "asmp9_nuisance_confusability_registration_v0_36"
        ),
        "registration_id": "ASMP-9-NUISANCE-CONFUSABILITY-v0.36",
        "status": "registered_not_run",
        "outcomes_consumed": False,
        "git_commit_before_registration": commit,
        "git_branch": git("branch", "--show-current"),
        "implementation_commit_utc": git(
            "show", "-s", "--format=%cI", commit
        ),
        "implementation": {
            name: file_record(path)
            for name, path in IMPLEMENTATION_PATHS.items()
        },
        "documents": {
            name: file_record(path)
            for name, path in DOCUMENT_PATHS.items()
        },
        "frozen_universe": protocol["enumeration"],
        "gates": protocol["fixed_gates"],
        "execution": {
            "command": (
                "python ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "nuisance_confusability_v0_36/run_census.py "
                "--registration ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "nuisance_confusability_v0_36/"
                "REGISTRATION_v0_36.json "
                "--output ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "nuisance_confusability_v0_36/"
                "artifacts_v0_36/RESULT_v0_36.json"
            ),
            "independent_verifier_command": (
                "python ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "nuisance_confusability_v0_36/verify_result.py "
                "--result ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "nuisance_confusability_v0_36/"
                "artifacts_v0_36/RESULT_v0_36.json "
                "--output ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/"
                "nuisance_confusability_v0_36/"
                "artifacts_v0_36/VERIFY_v0_36.json"
            ),
        },
        "resource_envelope": {
            "execution": "cpu_only_exact_enumeration",
            "expected_wall_time_seconds_upper": 120,
            "expected_peak_python_bytes_upper": 536870912,
            "note": (
                "These are registered reporting bounds, not operating-system "
                "hard caps. Exceedance invalidates the corresponding gate."
            ),
        },
        "environment": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
        },
        "claim_boundary": protocol["claim_boundary"],
    }
    payload["registration_content_sha256"] = hashlib.sha256(
        canonical_bytes(payload)
    ).hexdigest()
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if git("status", "--porcelain"):
        raise RuntimeError("registration requires a clean prereveal worktree")
    payload = build_registration()
    compare_or_fail(args.output.resolve(), payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
