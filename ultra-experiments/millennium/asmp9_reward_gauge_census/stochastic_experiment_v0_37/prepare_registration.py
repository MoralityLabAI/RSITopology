"""Create the outcome-blind ASMP-9 v0.37 registration."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from typing import Any, Mapping

import numpy
import scipy


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
DEFAULT_OUTPUT = HERE / "REGISTRATION_v0_37.json"

IMPLEMENTATION_PATHS = {
    "exact_lp": HERE / "experiment.py",
    "development_runner": HERE / "run_development.py",
    "registered_runner": HERE / "run_registered.py",
    "replay_verifier": HERE / "verify_registered.py",
    "math_tests": HERE / "test_experiment.py",
    "registration_tests": HERE / "test_registered.py",
    "registration_builder": HERE / "prepare_registration.py",
}

DOCUMENT_PATHS = {
    "protocol": HERE / "PROTOCOL_v0_37.json",
    "development_note": HERE / "DEVELOPMENT_NOTE_v0_37.md",
    "development_result": HERE / "DEVELOPMENT_RESULT_v0_37.md",
    "development_artifact": HERE / "DEVELOPMENT_RESULT_v0_37.json",
    "prior_art": HERE / "PRIOR_ART_GATE_v0_37.md",
    "readme": HERE / "README.md",
}

SOURCE_PATHS = {
    "v0_36_result": (
        REPO
        / "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "nuisance_confusability_v0_36/RESULT_v0_36.md"
    ),
    "v0_36_registration": (
        REPO
        / "ultra-experiments/millennium/asmp9_reward_gauge_census/"
        "nuisance_confusability_v0_36/REGISTRATION_v0_36.json"
    ),
}


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=REPO, text=True
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
        "schema_version": "asmp9_stochastic_experiment_registration_v0_37",
        "registration_id": "ASMP-9-STOCHASTIC-EXPERIMENT-v0.37",
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
        "sources": {
            name: file_record(path)
            for name, path in SOURCE_PATHS.items()
        },
        "experiment_class": protocol["experiment_class"],
        "estimands": protocol["estimands"],
        "solver_contract": protocol["solver_contract"],
        "gates": protocol["fixed_gates"],
        "resource_envelope": protocol["resource_envelope"],
        "environment": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "numpy_version": numpy.__version__,
            "scipy_version": scipy.__version__,
        },
        "execution": {
            "runner": (
                "python ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/stochastic_experiment_v0_37/"
                "run_registered.py --registration ultra-experiments/"
                "millennium/asmp9_reward_gauge_census/"
                "stochastic_experiment_v0_37/REGISTRATION_v0_37.json "
                "--output ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/stochastic_experiment_v0_37/"
                "artifacts_v0_37/RESULT_v0_37.json"
            ),
            "verifier": (
                "python ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/stochastic_experiment_v0_37/"
                "verify_registered.py --result ultra-experiments/"
                "millennium/asmp9_reward_gauge_census/"
                "stochastic_experiment_v0_37/artifacts_v0_37/"
                "RESULT_v0_37.json --output ultra-experiments/millennium/"
                "asmp9_reward_gauge_census/stochastic_experiment_v0_37/"
                "artifacts_v0_37/VERIFY_v0_37.json"
            ),
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
