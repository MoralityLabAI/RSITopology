"""Build the deterministic proposal-recursion methods and gate-result bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from typing import Any


RELEASE_FILES = (
    "docs/PROPOSAL_RECURSIVE_IMPROVEMENT_PROTOCOL_V1.md",
    "output/pdf/proposal_recursive_improvement_protocol_v1.pdf",
    "protocols/proposal_recursive_improvement_v1.json",
    "protocols/proposal_recursive_prompt_families_v1.json",
    "protocols/proposal_recursive_ordering_split_v1.json",
    "protocols/proposal_recursive_ordering_generator_v1.json",
    "protocols/proposal_recursive_compute_ledger_v1.json",
    "protocols/proposal_recursive_gate_evaluator_v1.json",
    "protocols/qwen_soft_atlas_measurement_v1.json",
    "schemas/proposal_recursive_formula_sentinels_v1.json",
    "rsi_topology/recursive_gate.py",
    "scripts/build_recursive_improvement_pdf.py",
    "scripts/validate_recursive_improvement_spec.py",
    "scripts/evaluate_recursive_gates.py",
    "scripts/run_soft_atlas_measurement.py",
    "scripts/seal_recursive_improvement_protocol.py",
    "scripts/package_recursive_measurement_release.py",
    "tests/test_recursive_gate.py",
    "artifacts/proposal_recursive_improvement_v1/environment_lock.json",
    "artifacts/proposal_recursive_improvement_v1/proposal_recursive_improvement_v1.extracted.txt",
    "artifacts/proposal_recursive_improvement_v1/render_validation_receipt.json",
    "artifacts/proposal_recursive_improvement_v1/seal_manifest.json",
    "artifacts/qwen_soft_atlas_measurement_v1/measurement_edges.csv",
    "artifacts/qwen_soft_atlas_measurement_v1/measurement_gate_report.md",
    "artifacts/qwen_soft_atlas_measurement_v1/measurement_gate_result.json",
    "artifacts/qwen_soft_atlas_measurement_v1/prompt_family_sufficiency.json",
    "artifacts/qwen_soft_atlas_measurement_v1/run_receipt.json",
    "artifacts/qwen_soft_atlas_measurement_v1/soft_atlas_profile.csv",
    "reports/qwen_soft_atlas_measurement_v1.md",
    "reports/proposal_recursion_completion_audit_20260714.md",
)

VISUAL_SOURCE = Path(
    ".codex/visualizations/2026/07/14/019f487e-9757-7b31-a841-76d7a2d756d5/soft-atlas-measurement-boundary.html"
)
VISUAL_ARCHIVE_NAME = "visualizations/soft-atlas-measurement-boundary.html"


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
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def verify_receipts(root: Path) -> None:
    seal = json.loads(
        (root / "artifacts/proposal_recursive_improvement_v1/seal_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    if seal.get("status") != "sealed" or not all(seal["render_reconciliation"].values()):
        raise ValueError("methods seal is not valid")
    receipt_path = root / "artifacts/qwen_soft_atlas_measurement_v1/run_receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("status") != "complete":
        raise ValueError("measurement receipt is incomplete")
    output_dir = receipt_path.parent
    for name, expected in receipt["output_sha256"].items():
        if sha256_file(output_dir / name) != expected:
            raise ValueError(f"measurement output hash mismatch: {name}")
    protocol_path = root / "protocols/qwen_soft_atlas_measurement_v1.json"
    if sha256_file(protocol_path) != receipt["protocol_sha256"]:
        raise ValueError("measurement protocol hash mismatch")


def package(root: Path, output: Path) -> tuple[Path, str]:
    verify_receipts(root)
    files = {name: root / name for name in RELEASE_FILES}
    files[VISUAL_ARCHIVE_NAME] = root / VISUAL_SOURCE
    missing = [name for name, path in files.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"release inputs missing: {missing}")
    result = json.loads(
        (root / "artifacts/qwen_soft_atlas_measurement_v1/measurement_gate_result.json").read_text(
            encoding="utf-8"
        )
    )
    manifest = {
        "schema_version": "proposal_recursive_measurement_release_v1",
        "release_date": "2026-07-14",
        "methods_status": "sealed",
        "measurement_decision": result["measurement_component"]["gate_record"][
            "gate_decision"
        ],
        "overall_G1": result["overall_G1"]["gate_decision"],
        "prompt_corpus_decision": result["prompt_corpus_decision"],
        "recursive_experiment_authorized": False,
        "file_sha256": {
            name: sha256_file(path) for name, path in sorted(files.items())
        },
    }
    manifest_bytes = canonical_json_bytes(manifest)
    manifest_path = root / "artifacts/qwen_soft_atlas_measurement_v1/release_manifest.json"
    write_once_or_equal(manifest_path, manifest_bytes)
    files["artifacts/qwen_soft_atlas_measurement_v1/release_manifest.json"] = manifest_path

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(files.items()):
            info = zipfile.ZipInfo(name.replace("\\", "/"), date_time=(2026, 7, 14, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    data = temporary.read_bytes()
    temporary.unlink()
    write_once_or_equal(output, data)
    digest = hashlib.sha256(data).hexdigest()
    write_once_or_equal(output.with_suffix(output.suffix + ".sha256"), f"{digest}  {output.name}\n".encode("ascii"))
    return output, digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("RSITopology_recursive_protocol_and_measurement_v1_20260714.zip"),
    )
    parser.add_argument("--copy-to", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output_path, digest = package(root, output)
    if args.copy_to is not None:
        destination = args.copy_to.resolve()
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output_path, destination / output_path.name)
        shutil.copy2(
            output_path.with_suffix(output_path.suffix + ".sha256"),
            destination / (output_path.name + ".sha256"),
        )
    print(json.dumps({"zip": str(output_path), "sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
