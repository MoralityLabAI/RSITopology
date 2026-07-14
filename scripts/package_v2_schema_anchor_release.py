"""Package the v2.0.3 gate schema, anchor audit trail, and v1 forward proof."""

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

from rsi_topology.composite_gate_v2 import total_mapping_table


CORE_FILES = (
    "protocols/proposal_recursive_composite_gate_v2.json",
    "protocols/proposal_recursive_anchor_sandwich_v2.json",
    "rsi_topology/composite_gate_v2.py",
    "rsi_topology/anchor_guard_v2.py",
    "scripts/record_ots_anchor.py",
    "scripts/seal_v2_schema.py",
    "scripts/v2_release_guard.py",
    "tests/test_composite_gate_v2.py",
    "tests/test_anchor_guard_v2.py",
    "reports/proposal_recursive_v2_schema_and_anchor_20260714.md",
    "reports/v1_forward_anchor_and_legibility_addendum_20260714.md",
    "RSITopology_recursive_protocol_and_measurement_v1_20260714.zip",
    "RSITopology_recursive_protocol_and_measurement_v1_20260714.zip.sha256",
    "RSITopology_recursive_protocol_and_measurement_v1_20260714.zip.ots",
)

ARTIFACT_DIRS = (
    "artifacts/v1_forward_anchor_20260714",
    "artifacts/v1_forward_anchor_20260714_v2",
    "artifacts/proposal_recursive_v2_schema",
    "artifacts/proposal_recursive_v2_0_1_schema",
    "artifacts/proposal_recursive_v2_0_2_schema",
    "artifacts/proposal_recursive_v2_0_3_schema",
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
            raise FileExistsError(f"write-once release differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def collect_files(root: Path) -> dict[str, Path]:
    files = {name: root / name for name in CORE_FILES}
    for directory_name in ARTIFACT_DIRS:
        directory = root / directory_name
        if not directory.is_dir():
            raise FileNotFoundError(directory)
        for path in directory.rglob("*"):
            if path.is_file():
                files[path.relative_to(root).as_posix()] = path
    missing = [name for name, path in files.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"release files missing: {missing}")
    return files


def verify(root: Path) -> None:
    protocol = json.loads(
        (root / "protocols/proposal_recursive_composite_gate_v2.json").read_text(
            encoding="utf-8"
        )
    )
    if protocol["version"] != "2.0.3":
        raise ValueError("wrong composite-gate version")
    if protocol["mapping_table"] != total_mapping_table():
        raise ValueError("registered 25-cell table differs from evaluator")

    schema_dir = root / "artifacts/proposal_recursive_v2_0_3_schema"
    seal = json.loads((schema_dir / "schema_seal_manifest.json").read_text(encoding="utf-8"))
    payload = schema_dir / "schema_anchor_payload.json"
    if sha256_file(payload) != seal["schema_anchor_payload_sha256"]:
        raise ValueError("v2.0.3 schema payload differs from seal")
    for name, expected in seal["file_sha256"].items():
        if sha256_file(root / name) != expected:
            raise ValueError(f"v2.0.3 sealed file differs: {name}")
    schema_anchor = json.loads(
        (schema_dir / "schema_anchor/anchor_receipt.json").read_text(encoding="utf-8")
    )
    if schema_anchor["anchor_role"] != "schema_chronology":
        raise ValueError("v2.0.3 anchor has the wrong role")
    if schema_anchor["target_sha256"] != sha256_file(payload):
        raise ValueError("v2.0.3 anchor does not bind schema payload")
    if schema_anchor["proof_sha256"] != sha256_file(
        schema_dir / "schema_anchor_payload.json.ots"
    ):
        raise ValueError("v2.0.3 proof differs from receipt")

    v1_zip = root / "RSITopology_recursive_protocol_and_measurement_v1_20260714.zip"
    v1_proof = v1_zip.with_suffix(v1_zip.suffix + ".ots")
    v1_anchor = json.loads(
        (root / "artifacts/v1_forward_anchor_20260714_v2/anchor_receipt.json").read_text(
            encoding="utf-8"
        )
    )
    if v1_anchor["target_sha256"] != sha256_file(v1_zip):
        raise ValueError("v1 forward anchor does not bind release")
    if v1_anchor["proof_sha256"] != sha256_file(v1_proof):
        raise ValueError("v1 forward proof differs from receipt")


def package(root: Path, output: Path) -> tuple[Path, str]:
    verify(root)
    files = collect_files(root)
    manifest = {
        "schema_version": "proposal_recursive_v2_0_3_schema_anchor_release_v1",
        "release_date": "2026-07-14",
        "v2_schema_version": "2.0.3",
        "v2_schema_anchor_status": "calendar_submitted_pending_bitcoin",
        "v2_run_authorized": False,
        "v1_chronology_limitation": "forward_anchor_only_cannot_prove_protocol_predated_run",
        "file_sha256": {name: sha256_file(path) for name, path in sorted(files.items())},
    }
    manifest_bytes = canonical_json_bytes(manifest)
    manifest_path = root / "artifacts/proposal_recursive_v2_0_3_schema/release_manifest.json"
    write_once_or_equal(manifest_path, manifest_bytes)
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
        default=Path("RSITopology_recursive_v2_schema_anchor_20260714.zip"),
    )
    parser.add_argument("--copy-to", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output, digest = package(root, output)
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
