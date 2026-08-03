#!/usr/bin/env python3
"""Build a prospective registration after the source-freeze commit exists."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from release_contract import (
    BOUND_SOURCES,
    CLAIM_BOUNDARY,
    FROZEN_CLAIM_GRID,
    MATHEMATICAL_PROTOCOL_ID,
    REGISTRATION_FILENAME,
    REGISTRATION_SCHEMA,
    RELEASE_ID,
)


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_lf_text(path: Path, payload: str) -> None:
    """Write hash-bound UTF-8 text with repository-stable LF bytes."""

    path.write_text(payload, encoding="utf-8", newline="\n")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite(token: str) -> None:
    raise ValueError(f"non-finite JSON number: {token}")


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_unique_object,
        parse_constant=_reject_nonfinite,
    )


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def resolve_commit(reference: str) -> str:
    commit = git("rev-parse", "--verify", f"{reference}^{{commit}}")
    if len(commit) != 40 or any(
        character not in "0123456789abcdef" for character in commit
    ):
        raise RuntimeError(f"source commit is not a full Git object id: {commit}")
    return commit


def committed_source_bindings(
    source_commit: str,
) -> tuple[dict[str, str], dict[str, str]]:
    """Return SHA-256 and Git OID maps after matching every working source."""

    repo_root = Path(git("rev-parse", "--show-toplevel"))
    missing = []
    changed = []
    source_hashes: dict[str, str] = {}
    blob_oids: dict[str, str] = {}
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
        committed_sha256 = hashlib.sha256(committed).hexdigest()
        if not path.is_file() or committed_sha256 != sha256(path):
            changed.append(relative)
            continue
        source_hashes[name] = committed_sha256
        blob_oid = git("rev-parse", f"{source_commit}:{relative}")
        if (
            len(blob_oid) != 40
            or any(character not in "0123456789abcdef" for character in blob_oid)
            or git("cat-file", "-t", blob_oid) != "blob"
        ):
            raise RuntimeError(f"registered source is not a full Git blob: {relative}")
        blob_oids[name] = blob_oid
    if missing or changed:
        raise RuntimeError(
            f"source commit does not bind current sources; missing={missing}, changed={changed}"
        )
    if set(source_hashes) != set(BOUND_SOURCES) or set(blob_oids) != set(BOUND_SOURCES):
        raise RuntimeError("source binding maps are incomplete")
    return source_hashes, blob_oids


def build_registration(source_commit: str) -> dict[str, Any]:
    source_commit = resolve_commit(source_commit)
    source_hashes, blob_oids = committed_source_bindings(source_commit)
    manifest = load_json(ROOT / "experiment_v0_2_1.json")
    claim_grid = manifest["asmp11"]
    if claim_grid != FROZEN_CLAIM_GRID:
        raise RuntimeError("manifest claim grid differs from the exact v0.2.1.2 grid")
    if claim_grid.get("release_id") != RELEASE_ID:
        raise RuntimeError("manifest release id does not match the v0.2.1.2 contract")
    if claim_grid.get("protocol_id") != MATHEMATICAL_PROTOCOL_ID:
        raise RuntimeError("manifest mathematical protocol id changed")
    manifest_sha256 = sha256(ROOT / "experiment_v0_2_1.json")
    prior_anchor_sha256 = sha256(ROOT / "prior_anchor_v0_2.json")
    if source_hashes["experiment_v0_2_1.json"] != manifest_sha256:
        raise RuntimeError(
            "manifest working bytes differ from the committed source blob"
        )
    if source_hashes["prior_anchor_v0_2.json"] != prior_anchor_sha256:
        raise RuntimeError(
            "prior-anchor working bytes differ from the committed source blob"
        )
    return {
        "schema_version": REGISTRATION_SCHEMA,
        "release_id": RELEASE_ID,
        "protocol_id": MATHEMATICAL_PROTOCOL_ID,
        "registered_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "prospective_registration_before_claim_grid_execution",
        "proposed_asmp_id": "ASMP-11",
        "source_commit": source_commit,
        "source_hashes": source_hashes,
        "source_git_blob_oids": blob_oids,
        "manifest_path": "experiment_v0_2_1.json",
        "manifest_sha256": manifest_sha256,
        "prior_anchor_path": "prior_anchor_v0_2.json",
        "prior_anchor_sha256": prior_anchor_sha256,
        "claim_grid": claim_grid,
        "claim_boundary": CLAIM_BOUNDARY,
        "output_policy": "write_once_non_aliasing",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", default=None)
    parser.add_argument("--output", type=Path, default=ROOT / REGISTRATION_FILENAME)
    args = parser.parse_args()
    source_commit = args.source_commit or git("rev-parse", "HEAD")
    output = args.output.resolve()
    if output != (ROOT / REGISTRATION_FILENAME).resolve():
        raise ValueError("v0.2.1.2 registration must use its exact release path")
    if output.exists():
        raise FileExistsError(f"registration is write-once: {output}")
    registration = build_registration(source_commit)
    write_lf_text(output, json.dumps(registration, indent=2, sort_keys=True) + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
