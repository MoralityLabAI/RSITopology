"""Write-once runner for ASMP-7 causal adaptive suppression v0.4."""

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
from pathlib import Path
from types import ModuleType


HERE = Path(os.path.abspath(__file__)).parent
ARTIFACT_DIRECTORY = HERE.parent / "artifacts_v0_4_adaptive_suppression"
FROZEN_SOURCE_FILES = (
    "PROTOCOL_v0_4.md",
    "README.md",
    "SOURCE_FREEZE.md",
    "adaptive_suppression.py",
    "manifest_v0_4.json",
    "run.py",
    "test_adaptive_suppression.py",
    "verify_independent.py",
)
GIT_EXECUTABLE = shutil.which("git")


def require_isolated_safe_path() -> None:
    if not (_sys.flags.isolated and getattr(_sys.flags, "safe_path", False)):
        raise SystemExit(
            "refusing unsafe launch before imports; invoke with `python -I run.py ...`"
        )
    _sys.dont_write_bytecode = True


def _is_reparse_point(path: Path) -> bool:
    metadata = path.lstat()
    attributes = getattr(metadata, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return path.is_symlink() or bool(attributes & flag)


def preflight_live_source_inventory() -> None:
    entries = {entry.name: entry for entry in HERE.iterdir()}
    expected = set(FROZEN_SOURCE_FILES)
    invalid = [
        name
        for name in sorted(expected & set(entries))
        if _is_reparse_point(entries[name]) or not entries[name].is_file()
    ]
    if _is_reparse_point(HERE) or set(entries) != expected or invalid:
        raise SystemExit(
            "refusing live source inventory before local import: "
            f"missing={sorted(expected - set(entries))}, "
            f"unexpected={sorted(set(entries) - expected)}, invalid={invalid}"
        )


def _git_environment() -> dict[str, str]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    return environment


def _git(args: list[str], *, cwd: Path, input_bytes: bytes | None = None) -> bytes:
    if GIT_EXECUTABLE is None:
        raise SystemExit("trusted Git executable is unavailable")
    return subprocess.run(
        [GIT_EXECUTABLE, *args],
        cwd=cwd,
        env=_git_environment(),
        input=input_bytes,
        check=True,
        capture_output=True,
    ).stdout


def bootstrap_source_snapshot(
    source_commit: str,
) -> tuple[dict[str, object], dict[str, bytes]]:
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise SystemExit("source commit must be a full lowercase 40-hex commit")
    root = Path(
        os.path.abspath(
            _git(["rev-parse", "--show-toplevel"], cwd=HERE)
            .decode("utf-8")
            .strip()
        )
    )
    cursor = HERE
    while True:
        if _is_reparse_point(cursor):
            raise SystemExit(f"source ancestry contains reparse point: {cursor}")
        if cursor == root:
            break
        if cursor.parent == cursor or root not in cursor.parents:
            raise SystemExit("source directory is outside the reported repository root")
        cursor = cursor.parent

    git_directory = Path(
        os.path.abspath(
            _git(["rev-parse", "--absolute-git-dir"], cwd=root)
            .decode("utf-8")
            .strip()
        )
    )
    grafts = git_directory / "info" / "grafts"
    if grafts.exists() and grafts.stat().st_size:
        raise SystemExit("refusing repository with legacy Git grafts")
    if _git(["for-each-ref", "--format=%(refname)", "refs/replace"], cwd=root).strip():
        raise SystemExit("refusing repository with Git replacement refs")
    if _git(["rev-parse", "--is-shallow-repository"], cwd=root).strip() != b"false":
        raise SystemExit("refusing shallow repository for source provenance")
    if _git(["cat-file", "-t", source_commit], cwd=root).strip() != b"commit":
        raise SystemExit("source object is not a commit")
    resolved = _git(
        ["rev-parse", "--verify", f"{source_commit}^{{commit}}"], cwd=root
    ).decode("ascii").strip()
    if resolved != source_commit:
        raise SystemExit("source commit did not resolve exactly")
    ancestry = subprocess.run(
        [GIT_EXECUTABLE, "merge-base", "--is-ancestor", source_commit, "HEAD"],
        cwd=root,
        env=_git_environment(),
        capture_output=True,
    )
    if ancestry.returncode != 0:
        raise SystemExit("source commit is not an ancestor of HEAD")

    relative_directory = HERE.relative_to(root)
    directory_path = relative_directory.as_posix()
    listed = _git(
        ["ls-tree", "-r", "--name-only", source_commit, "--", directory_path],
        cwd=root,
    ).decode("utf-8")
    expected_paths = {
        (relative_directory / filename).as_posix()
        for filename in FROZEN_SOURCE_FILES
    }
    if {line for line in listed.splitlines() if line} != expected_paths:
        raise SystemExit("source commit does not contain the exact eight-file set")

    source_files: dict[str, dict[str, str]] = {}
    source_snapshot: dict[str, bytes] = {}
    for filename in FROZEN_SOURCE_FILES:
        relative_path = (relative_directory / filename).as_posix()
        tree_line = _git(
            ["ls-tree", source_commit, "--", relative_path], cwd=root
        ).decode("utf-8").strip()
        metadata, listed_path = tree_line.split("\t", 1)
        mode, kind, blob_oid = metadata.split()
        if listed_path != relative_path or mode != "100644" or kind != "blob":
            raise SystemExit(f"source entry is not a regular blob: {filename}")
        current = (HERE / filename).read_bytes()
        committed = _git(["show", f"{source_commit}:{relative_path}"], cwd=root)
        current_oid = _git(["hash-object", "--stdin"], cwd=root, input_bytes=current)
        current_oid_text = current_oid.decode("ascii").strip()
        if current != committed or current_oid_text != blob_oid:
            raise SystemExit(f"working source differs from commit: {filename}")
        source_snapshot[filename] = current
        source_files[filename] = {
            "git_blob_oid": current_oid_text,
            "sha256": hashlib.sha256(current).hexdigest(),
        }
    return (
        {
            "repo_relative_directory": directory_path,
            "source_commit": source_commit,
            "source_commit_is_ancestor_of_head": True,
            "source_commit_type": "commit",
            "source_files": source_files,
        },
        source_snapshot,
    )


def bootstrap_source_commit_binding(source_commit: str) -> dict[str, object]:
    binding, _ = bootstrap_source_snapshot(source_commit)
    return binding


def load_primary_module(source_bytes: bytes) -> ModuleType:
    source_path = HERE / "adaptive_suppression.py"
    module = ModuleType("_asmp7_v04_frozen_primary")
    module.__file__ = str(source_path)
    module.__package__ = ""
    code = compile(source_bytes, str(source_path), "exec", dont_inherit=True)
    exec(code, module.__dict__)
    return module


def validate_output_path(path: Path) -> Path:
    destination = Path(os.path.abspath(os.fspath(path)))
    artifact_directory = Path(os.path.abspath(os.fspath(ARTIFACT_DIRECTORY)))
    if destination.parent != artifact_directory:
        raise SystemExit(
            "refusing output outside the frozen sibling artifact directory"
        )
    try:
        destination.lstat()
    except FileNotFoundError:
        return destination
    except OSError as error:
        raise SystemExit(f"cannot inspect output path: {destination}") from error
    raise SystemExit(f"refusing occupied write-once output path: {destination}")


def validate_manifest_path(path: Path) -> None:
    manifest_path = Path(os.path.abspath(os.fspath(path)))
    frozen_path = Path(os.path.abspath(os.fspath(HERE / "manifest_v0_4.json")))
    if manifest_path != frozen_path:
        raise SystemExit("refusing a manifest outside the frozen source snapshot")


def main() -> None:
    require_isolated_safe_path()
    preflight_live_source_inventory()
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--manifest", type=Path, default=HERE / "manifest_v0_4.json")
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTIFACT_DIRECTORY / "result_v0_4.json",
    )
    args = parser.parse_args()
    output_path = validate_output_path(args.output)
    validate_manifest_path(args.manifest)
    source_binding, source_snapshot = bootstrap_source_snapshot(args.source_commit)
    primary = load_primary_module(source_snapshot["adaptive_suppression.py"])
    manifest = primary.load_json_bytes_strict(source_snapshot["manifest_v0_4.json"])
    if not isinstance(manifest, dict):
        raise SystemExit("frozen manifest root is not an object")
    primary.validate_manifest_binding(manifest)
    result = primary.compile_result(manifest, source_binding)
    try:
        primary.write_once_json(
            output_path, result, max_bytes=manifest["budget"]["max_result_bytes"]
        )
    except primary.ResourceStop as error:
        raise SystemExit(
            f"refusing artifact before path creation; no artifact written: {error}"
        ) from error
    print(output_path)


if __name__ == "__main__":
    main()
