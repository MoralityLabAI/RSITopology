"""Seal the rendered six-artifact proposal-recursion methods protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SIX_ARTIFACTS = (
    "protocols/proposal_recursive_improvement_v1.json",
    "protocols/proposal_recursive_prompt_families_v1.json",
    "protocols/proposal_recursive_ordering_split_v1.json",
    "protocols/proposal_recursive_ordering_generator_v1.json",
    "protocols/proposal_recursive_compute_ledger_v1.json",
    "protocols/proposal_recursive_gate_evaluator_v1.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_once_or_equal(path: Path, payload: Any) -> None:
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() != encoded:
            raise FileExistsError(f"write-once seal differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)


def seal(root: Path, artifact_dir: Path) -> dict[str, Any]:
    validation_path = artifact_dir / "render_validation_receipt.json"
    environment_path = artifact_dir / "environment_lock.json"
    extracted_path = artifact_dir / "proposal_recursive_improvement_v1.extracted.txt"
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if validation.get("status") != "passed":
        raise ValueError("render validation did not pass")
    required = [
        *SIX_ARTIFACTS,
        "docs/PROPOSAL_RECURSIVE_IMPROVEMENT_PROTOCOL_V1.md",
        "output/pdf/proposal_recursive_improvement_protocol_v1.pdf",
        "schemas/proposal_recursive_formula_sentinels_v1.json",
        "rsi_topology/recursive_gate.py",
        "scripts/evaluate_recursive_gates.py",
        "scripts/build_recursive_improvement_pdf.py",
        "scripts/validate_recursive_improvement_spec.py",
        "tests/test_recursive_gate.py",
    ]
    files = {name: root / name for name in required}
    files.update(
        {
            "artifacts/proposal_recursive_improvement_v1/environment_lock.json": environment_path,
            "artifacts/proposal_recursive_improvement_v1/proposal_recursive_improvement_v1.extracted.txt": extracted_path,
            "artifacts/proposal_recursive_improvement_v1/render_validation_receipt.json": validation_path,
        }
    )
    missing = [name for name, path in files.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"seal inputs missing: {missing}")
    for name in SIX_ARTIFACTS:
        payload = json.loads((root / name).read_text(encoding="utf-8"))
        if not str(payload.get("status", "")).startswith("frozen"):
            raise ValueError(f"artifact is not frozen: {name}")
    hashes = {name: sha256_file(path) for name, path in sorted(files.items())}
    expected = validation["sha256"]
    reconciliation = {
        "source_markdown": hashes[
            "docs/PROPOSAL_RECURSIVE_IMPROVEMENT_PROTOCOL_V1.md"
        ]
        == expected["source_markdown"],
        "rendered_pdf": hashes[
            "output/pdf/proposal_recursive_improvement_protocol_v1.pdf"
        ]
        == expected["rendered_pdf"],
        "extracted_text": hashes[
            "artifacts/proposal_recursive_improvement_v1/proposal_recursive_improvement_v1.extracted.txt"
        ]
        == expected["extracted_text"],
        "sentinel_schema": hashes[
            "schemas/proposal_recursive_formula_sentinels_v1.json"
        ]
        == expected["sentinel_schema"],
        "environment_lock": hashes[
            "artifacts/proposal_recursive_improvement_v1/environment_lock.json"
        ]
        == expected["environment_lock"],
    }
    if not all(reconciliation.values()):
        raise ValueError(f"render receipt reconciliation failed: {reconciliation}")
    manifest = {
        "schema_version": "proposal_recursive_protocol_seal_v1",
        "status": "sealed",
        "sealed_on": "2026-07-14",
        "protocol_version": "1.0.0",
        "six_artifact_count": len(SIX_ARTIFACTS),
        "six_artifacts": list(SIX_ARTIFACTS),
        "total_instrument_decision_mapping": True,
        "alpha_spending_registered": False,
        "extension_path": "fresh_disjoint_holdouts_only",
        "render_reconciliation": reconciliation,
        "file_sha256": hashes,
    }
    write_once_or_equal(artifact_dir / "seal_manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("artifacts/proposal_recursive_improvement_v1"),
    )
    args = parser.parse_args()
    root = args.root.resolve()
    artifact_dir = (
        args.artifact_dir.resolve()
        if args.artifact_dir.is_absolute()
        else (root / args.artifact_dir).resolve()
    )
    manifest = seal(root, artifact_dir)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "files": len(manifest["file_sha256"]),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
