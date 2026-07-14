"""Create the deterministic locked v2.0.3 harness preparation kit."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.run_preparation_v2 import (
    canonical_json_bytes,
    readiness_report,
    runtime_environment,
    sha256_file,
    write_once_or_equal,
)


LOCKED_FILES = (
    "docs/RECURSIVE_HARNESS_V2_RUN_PREPARATION.md",
    "protocols/proposal_recursive_anchor_sandwich_v2.json",
    "protocols/proposal_recursive_composite_gate_v2.json",
    "protocols/proposal_recursive_run_preparation_qwen17_v2_0_3.json",
    "schemas/proposal_recursive_run_registration_v2.schema.json",
    "schemas/recursive_harness_event_v2.schema.json",
    "schemas/recursive_harness_summary_v2.schema.json",
    "schemas/recursive_harness_event_v2.example.jsonl",
    "schemas/recursive_harness_summary_v2.example.json",
    "rsi_topology/anchor_guard_v2.py",
    "rsi_topology/composite_gate_v2.py",
    "rsi_topology/run_preparation_v2.py",
    "scripts/record_ots_anchor.py",
    "scripts/seal_v2_schema.py",
    "scripts/v2_release_guard.py",
    "scripts/prepare_recursive_run_v2.py",
    "scripts/authorize_recursive_run_v2.py",
    "scripts/launch_recursive_harness_v2.ps1",
    "scripts/package_recursive_harness_v2.py",
    "tests/test_anchor_guard_v2.py",
    "tests/test_composite_gate_v2.py",
    "tests/test_run_preparation_v2.py",
    "artifacts/proposal_recursive_run_preparation_qwen17_v2_0_3/readiness_v2/readiness_report.json",
    "reports/proposal_recursive_v2_schema_and_anchor_20260714.md",
    "RSITopology_recursive_v2_schema_anchor_20260714.zip",
    "RSITopology_recursive_v2_schema_anchor_20260714.zip.sha256",
)


def package(root: Path, output: Path) -> tuple[Path, str]:
    files = {name: root / name for name in LOCKED_FILES}
    missing = [name for name, path in files.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"locked harness inputs missing: {missing}")
    registration = json.loads(
        files["protocols/proposal_recursive_run_preparation_qwen17_v2_0_3.json"].read_text(
            encoding="utf-8"
        )
    )
    readiness = readiness_report(registration)
    recorded_readiness = json.loads(
        files[
            "artifacts/proposal_recursive_run_preparation_qwen17_v2_0_3/readiness_v2/readiness_report.json"
        ].read_text(encoding="utf-8")
    )
    if readiness != recorded_readiness:
        raise ValueError("recorded readiness report differs from executable evaluator")
    schema_package = files["RSITopology_recursive_v2_schema_anchor_20260714.zip"]
    if sha256_file(schema_package) != "4a2896019e53573265ea6f9f247891a72bbfb378cd178e9377b29e0fe1e2e49f":
        raise ValueError("locked scientific schema package differs")

    lock_dir = root / "artifacts/proposal_recursive_harness_v2_0_3_lock"
    environment_path = lock_dir / "preparation_environment_lock.json"
    write_once_or_equal(environment_path, canonical_json_bytes(runtime_environment()))
    files[environment_path.relative_to(root).as_posix()] = environment_path
    manifest = {
        "schema_version": "proposal_recursive_harness_lock_v1",
        "scientific_schema_version": "2.0.3",
        "operational_preparation_version": "0.1.0",
        "locked_on": "2026-07-14",
        "status": "locked_preparation_not_run_authorization",
        "scientific_schema_package_sha256": sha256_file(schema_package),
        "parent_v1_gate_decision": "fail",
        "run_readiness_status": readiness["status"],
        "run_readiness_blockers": readiness["blockers"],
        "scientific_run_authorized": False,
        "file_sha256": {name: sha256_file(path) for name, path in sorted(files.items())},
    }
    manifest_path = lock_dir / "lock_manifest.json"
    write_once_or_equal(manifest_path, canonical_json_bytes(manifest))
    files[manifest_path.relative_to(root).as_posix()] = manifest_path

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    with zipfile.ZipFile(
        temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name, path in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 7, 14, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(
                info,
                path.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
    data = temporary.read_bytes()
    temporary.unlink()
    write_once_or_equal(output, data)
    digest = hashlib.sha256(data).hexdigest()
    sidecar = output.with_suffix(output.suffix + ".sha256")
    write_once_or_equal(sidecar, f"{digest}  {output.name}\n".encode("ascii"))
    return output, digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("RSITopology_recursive_harness_v2_0_3_locked_20260714.zip"),
    )
    parser.add_argument("--copy-to", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output, digest = package(root, args.output.resolve())
    if args.copy_to is not None:
        destination = args.copy_to.resolve()
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, destination / output.name)
        shutil.copy2(
            output.with_suffix(output.suffix + ".sha256"),
            destination / (output.name + ".sha256"),
        )
    print(json.dumps({"zip": str(output), "sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
