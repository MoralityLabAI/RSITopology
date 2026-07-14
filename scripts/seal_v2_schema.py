"""Create the write-once v2 schema environment and pre-anchor payload."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


V2_FILES = (
    "protocols/proposal_recursive_composite_gate_v2.json",
    "protocols/proposal_recursive_anchor_sandwich_v2.json",
    "rsi_topology/composite_gate_v2.py",
    "rsi_topology/anchor_guard_v2.py",
    "scripts/record_ots_anchor.py",
    "scripts/seal_v2_schema.py",
    "scripts/v2_release_guard.py",
    "tests/test_composite_gate_v2.py",
    "tests/test_anchor_guard_v2.py",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_once_or_equal(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"write-once schema artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def seal(root: Path, output_dir: Path, ots_package_json: Path | None) -> dict[str, Any]:
    files = {name: root / name for name in V2_FILES}
    missing = [name for name, path in files.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"v2 schema files missing: {missing}")
    node_version = subprocess.run(
        ["node", "--version"], check=True, capture_output=True, text=True
    ).stdout.strip()
    ots_client = None
    if ots_package_json is not None:
        package = json.loads(ots_package_json.read_text(encoding="utf-8"))
        ots_client = {
            "name": package["name"],
            "version": package["version"],
            "package_json_sha256": sha256_file(ots_package_json),
        }
    environment = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "node_version": node_version,
        "packages": {
            "numpy": version("numpy"),
            "pytest": version("pytest"),
        },
        "ots_client": ots_client,
    }
    environment_path = output_dir / "environment_lock.json"
    write_once_or_equal(environment_path, canonical_json_bytes(environment))
    environment_name = output_dir.relative_to(root).as_posix() + "/environment_lock.json"
    payload_files = {
        **{name: sha256_file(path) for name, path in sorted(files.items())},
        environment_name: sha256_file(environment_path),
    }
    payload = {
        "schema_version": "proposal_recursive_v2_0_3_schema_anchor_payload_v1",
        "status": "sealed_pending_external_anchor",
        "created_on": "2026-07-14",
        "anchor_purpose": "schema_chronology_only",
        "environment_lock_included": True,
        "file_sha256": payload_files,
        "source_data_access_authorized": False,
        "authorization_condition": "never_from_this_schema_anchor; a later run-specific pre-anchor with anchor_purpose=run_authorization is required",
    }
    payload_path = output_dir / "schema_anchor_payload.json"
    payload_bytes = canonical_json_bytes(payload)
    write_once_or_equal(payload_path, payload_bytes)
    manifest = {
        "schema_version": "proposal_recursive_v2_0_3_schema_seal_v1",
        "status": "sealed_pending_external_anchor",
        "schema_anchor_payload_sha256": hashlib.sha256(payload_bytes).hexdigest(),
        "file_count": len(payload_files),
        "file_sha256": payload_files,
    }
    write_once_or_equal(output_dir / "schema_seal_manifest.json", canonical_json_bytes(manifest))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/proposal_recursive_v2_schema"),
    )
    parser.add_argument("--ots-package-json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir.is_absolute()
        else (root / args.output_dir).resolve()
    )
    package_json = (
        None if args.ots_package_json is None else args.ots_package_json.resolve()
    )
    manifest = seal(root, output_dir, package_json)
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
