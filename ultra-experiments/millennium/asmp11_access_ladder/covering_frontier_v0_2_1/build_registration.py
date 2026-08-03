#!/usr/bin/env python3
"""Build a prospective registration after the source-freeze commit exists."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BOUND_SOURCES = (
    "README.md",
    "PROTOCOL_v0_2_1.md",
    "SERIALIZATION_REPAIR_v0_2_1_1.md",
    "experiment_v0_2_1.json",
    "prior_anchor_v0_2.json",
    "crossover_frontier.py",
    "run.py",
    "build_registration.py",
    "verify_result.py",
    "test_crossover_frontier.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_lf_text(path: Path, payload: str) -> None:
    """Write hash-bound UTF-8 text with repository-stable LF bytes."""

    path.write_text(payload, encoding="utf-8", newline="\n")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def ensure_commit_binds_sources(source_commit: str) -> None:
    repo_root = Path(git("rev-parse", "--show-toplevel"))
    missing = []
    changed = []
    for name in BOUND_SOURCES:
        path = ROOT / name
        relative = path.relative_to(repo_root).as_posix()
        try:
            git("cat-file", "-e", f"{source_commit}:{relative}")
        except subprocess.CalledProcessError:
            missing.append(relative)
            continue
        committed = subprocess.check_output(
            ["git", "show", f"{source_commit}:{relative}"], cwd=ROOT
        )
        if hashlib.sha256(committed).hexdigest() != sha256(path):
            changed.append(relative)
    if missing or changed:
        raise RuntimeError(
            f"source commit does not bind current sources; missing={missing}, changed={changed}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", default=None)
    parser.add_argument("--output", type=Path, default=ROOT / "registration_v0_2_1.json")
    args = parser.parse_args()
    source_commit = args.source_commit or git("rev-parse", "HEAD")
    ensure_commit_binds_sources(source_commit)
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"registration is write-once: {output}")
    manifest = json.loads((ROOT / "experiment_v0_2_1.json").read_text(encoding="utf-8"))
    registration = {
        "schema_version": "asmp11_intermediate_crossover_registration_v0_2_1",
        "protocol_id": manifest["asmp11"]["protocol_id"],
        "registered_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "prospective_registration_before_claim_grid_execution",
        "proposed_asmp_id": "ASMP-11",
        "source_commit": source_commit,
        "source_hashes": {name: sha256(ROOT / name) for name in BOUND_SOURCES},
        "manifest_sha256": sha256(ROOT / "experiment_v0_2_1.json"),
        "prior_anchor_sha256": sha256(ROOT / "prior_anchor_v0_2.json"),
        "claim_grid": manifest["asmp11"],
        "claim_boundary": "Finite bounds-aware crossover surface for the transparent parity oracle only.",
        "output_policy": "write_once_non_aliasing",
    }
    write_lf_text(output, json.dumps(registration, indent=2, sort_keys=True) + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
