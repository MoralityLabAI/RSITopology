"""Isolated write-once runner for the ASMP-5 v0.4 noisy-anchor grid."""

from __future__ import annotations

import sys as _sys


if __name__ == "__main__" and not (
    _sys.flags.isolated and getattr(_sys.flags, "safe_path", False)
):
    raise SystemExit(
        "refusing unsafe launch before imports; invoke with `python -I run.py ...`"
    )
if __name__ == "__main__":
    _sys.dont_write_bytecode = True


import argparse
import hashlib
import os
import re
import shutil
import stat
import subprocess
import time
import tracemalloc
from pathlib import Path
from types import ModuleType
from typing import Any


HERE = Path(os.path.abspath(__file__)).parent
ARTIFACT_DIRECTORY = HERE.parent / "artifacts_v0_4_dynamic_noisy_anchor"
SOURCE_FILES = (
    "PROTOCOL_v0_4.md",
    "README.md",
    "SOURCE_FREEZE.md",
    "manifest_v0_4.json",
    "noisy_anchor.py",
    "run.py",
    "test_noisy_anchor.py",
    "verify_independent.py",
)
PREDECESSOR_COMMIT = "61a2f802adb4c4b5f06272d97d9de888413d5352"
GIT = shutil.which("git")


def require_isolated() -> None:
    if not (_sys.flags.isolated and getattr(_sys.flags, "safe_path", False)):
        raise SystemExit(
            "refusing unsafe launch before imports; invoke with `python -I run.py ...`"
        )
    _sys.dont_write_bytecode = True


def _is_reparse(path: Path) -> bool:
    metadata = path.lstat()
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(getattr(metadata, "st_file_attributes", 0) & flag)


def preflight_inventory() -> None:
    entries = {entry.name: entry for entry in HERE.iterdir()}
    expected = set(SOURCE_FILES)
    invalid = [
        name
        for name in sorted(expected & set(entries))
        if _is_reparse(entries[name]) or not entries[name].is_file()
    ]
    if _is_reparse(HERE) or set(entries) != expected or invalid:
        raise SystemExit(
            "refusing live source inventory: "
            f"missing={sorted(expected-set(entries))}, "
            f"unexpected={sorted(set(entries)-expected)}, invalid={invalid}"
        )


def _git_env() -> dict[str, str]:
    environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    return environment


def _git(args: list[str], cwd: Path, input_bytes: bytes | None = None) -> bytes:
    if GIT is None:
        raise SystemExit("trusted Git executable unavailable")
    return subprocess.run(
        [GIT, *args],
        cwd=cwd,
        env=_git_env(),
        input=input_bytes,
        check=True,
        capture_output=True,
    ).stdout


def _repository_root() -> Path:
    return Path(
        os.path.abspath(
            _git(["rev-parse", "--show-toplevel"], HERE).decode("utf-8").strip()
        )
    )


def _validate_repository(root: Path) -> None:
    git_directory = Path(
        os.path.abspath(
            _git(["rev-parse", "--absolute-git-dir"], root).decode().strip()
        )
    )
    grafts = git_directory / "info" / "grafts"
    if grafts.exists() and grafts.stat().st_size:
        raise SystemExit("legacy Git grafts are forbidden")
    if _git(["for-each-ref", "--format=%(refname)", "refs/replace"], root).strip():
        raise SystemExit("Git replacement refs are forbidden")
    if _git(["rev-parse", "--is-shallow-repository"], root).strip() != b"false":
        raise SystemExit("shallow repository is forbidden")


def bootstrap_source_snapshot(
    source_commit: str,
) -> tuple[dict[str, Any], dict[str, bytes], Path]:
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise SystemExit("source commit must be full lowercase 40-hex")
    root = _repository_root()
    _validate_repository(root)
    if _git(["cat-file", "-t", source_commit], root).strip() != b"commit":
        raise SystemExit("source object is not a commit")
    if _git(["rev-parse", "--verify", f"{source_commit}^{{commit}}"], root).decode().strip() != source_commit:
        raise SystemExit("source commit did not resolve exactly")
    ancestry = subprocess.run(
        [GIT, "merge-base", "--is-ancestor", source_commit, "HEAD"],
        cwd=root,
        env=_git_env(),
        capture_output=True,
    )
    if ancestry.returncode:
        raise SystemExit("source commit is not an ancestor of HEAD")
    relative = HERE.relative_to(root)
    listed = _git(
        ["ls-tree", "-r", "--name-only", source_commit, "--", relative.as_posix()],
        root,
    ).decode()
    expected_paths = {(relative / name).as_posix() for name in SOURCE_FILES}
    if {line for line in listed.splitlines() if line} != expected_paths:
        raise SystemExit("source commit does not contain the exact eight-file set")
    snapshot: dict[str, bytes] = {}
    files: dict[str, dict[str, str]] = {}
    for name in SOURCE_FILES:
        path = (relative / name).as_posix()
        tree_line = _git(["ls-tree", source_commit, "--", path], root).decode().strip()
        metadata, listed_path = tree_line.split("\t", 1)
        mode, kind, oid = metadata.split()
        if listed_path != path or mode != "100644" or kind != "blob":
            raise SystemExit(f"source entry is not a regular blob: {name}")
        live = (HERE / name).read_bytes()
        committed = _git(["show", f"{source_commit}:{path}"], root)
        live_oid = _git(["hash-object", "--stdin"], root, live).decode().strip()
        if live != committed or live_oid != oid:
            raise SystemExit(f"working source differs from source commit: {name}")
        snapshot[name] = live
        files[name] = {
            "git_blob_oid": oid,
            "sha256": hashlib.sha256(live).hexdigest(),
        }
    return (
        {
            "pass": True,
            "source_commit": source_commit,
            "source_commit_type": "commit",
            "source_commit_is_ancestor_of_head": True,
            "repo_relative_directory": relative.as_posix(),
            "files": files,
        },
        snapshot,
        root,
    )


def load_primary(payload: bytes) -> ModuleType:
    module = ModuleType("_asmp5_v04_frozen_primary")
    source_path = HERE / "noisy_anchor.py"
    module.__file__ = str(source_path)
    module.__package__ = ""
    exec(compile(payload, str(source_path), "exec", dont_inherit=True), module.__dict__)
    return module


def predecessor_binding(
    manifest: dict[str, Any], source_commit: str, root: Path, primary: ModuleType
) -> dict[str, Any]:
    declaration = manifest["predecessor_binding"]
    if declaration["commit"] != PREDECESSOR_COMMIT:
        raise SystemExit("predecessor commit mismatch")
    if subprocess.run(
        [GIT, "merge-base", "--is-ancestor", PREDECESSOR_COMMIT, source_commit],
        cwd=root,
        env=_git_env(),
        capture_output=True,
    ).returncode:
        raise SystemExit("predecessor is not an ancestor of source commit")
    observed: dict[str, str] = {}
    payloads: dict[str, bytes] = {}
    for record in declaration["files"]:
        payload = _git(["show", f"{PREDECESSOR_COMMIT}:{record['path']}"], root)
        digest = hashlib.sha256(payload).hexdigest()
        if digest != record["sha256"]:
            raise SystemExit(f"predecessor hash mismatch: {record['path']}")
        observed[record["path"]] = digest
        payloads[record["path"]] = payload
    receipt_path = next(path for path in payloads if path.endswith("synthesis_receipt_v0_3.json"))
    receipt = primary.load_json_bytes_strict(payloads[receipt_path])
    if receipt.get("pass") is not True or receipt.get("binding_match") is not True:
        raise SystemExit("predecessor synthesis receipt is not passing")
    return {
        "pass": True,
        "commit": PREDECESSOR_COMMIT,
        "files": observed,
        "receipt_pass": True,
        "receipt_binding_match": True,
    }


def validate_output(path: Path) -> Path:
    destination = Path(os.path.abspath(path))
    expected_parent = Path(os.path.abspath(ARTIFACT_DIRECTORY))
    if destination.parent != expected_parent:
        raise SystemExit("refusing output outside frozen sibling artifact directory")
    if destination.exists():
        raise SystemExit("refusing to overwrite existing evidence")
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTIFACT_DIRECTORY / "result_v0_4.json",
    )
    return parser.parse_args()


def main() -> None:
    require_isolated()
    args = parse_args()
    preflight_inventory()
    destination = validate_output(args.output)
    source_binding, snapshot, root = bootstrap_source_snapshot(args.source_commit)
    primary = load_primary(snapshot["noisy_anchor.py"])
    manifest = primary.load_json_bytes_strict(snapshot["manifest_v0_4.json"])
    primary.validate_manifest(manifest)
    upstream = predecessor_binding(manifest, args.source_commit, root, primary)
    tracemalloc.start()
    started_ns = time.monotonic_ns()
    try:
        result = primary.compile_result(manifest, source_binding, upstream)
        elapsed_ns = time.monotonic_ns() - started_ns
        _, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    if elapsed_ns > manifest["budget"]["max_wall_seconds"] * 1_000_000_000:
        raise SystemExit("wall limit exceeded; no artifact written")
    if peak_bytes > manifest["budget"]["max_traced_python_mib"] * 1024 * 1024:
        raise SystemExit("traced-Python memory limit exceeded; no artifact written")
    if len(primary.canonical_json(result).encode("utf-8")) > manifest["budget"]["max_artifact_bytes"]:
        raise SystemExit("artifact byte limit exceeded; no artifact written")
    primary.write_once_json(destination, result)
    print(destination)


if __name__ == "__main__":
    main()
