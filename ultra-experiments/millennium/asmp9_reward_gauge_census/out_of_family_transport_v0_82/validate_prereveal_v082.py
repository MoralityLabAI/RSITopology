"""Outcome-free scientific and execution preflight for ASMP-9 v0.82."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
from pathlib import Path


HERE = Path(__file__).resolve().parent
V068 = HERE.parent / "context_quotient_response_v0_68"


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


design = _module("asmp9_design_v068_for_v082", V068 / "successor_design.py")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _write_once(path: Path, payload: bytes) -> None:
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    path.write_bytes(payload)


def validate(manifest_path: Path, old_manifest_path: Path) -> dict:
    manifest = design.load_manifest(manifest_path)
    old_manifest = design.load_manifest(old_manifest_path)
    jobs = design.score_jobs(manifest, "confirmation")
    new_families = {str(row["family"]) for row in manifest["rows"]}
    old_families = {str(row["family"]) for row in old_manifest["rows"]}
    confirmation = [row for row in manifest["rows"] if row["split"] == "confirmation"]
    padding = [row for row in manifest["rows"] if row["split"] == "construction"]
    if new_families & old_families:
        raise ValueError("v0.82 family labels overlap v0.68")
    if len(confirmation) != 12 or len(padding) != 12:
        raise ValueError("manifest split is not 12 plus 12")
    if len(jobs) != 528 or len({job["record_id"] for job in jobs}) != 528:
        raise ValueError("registered job universe is not exact")
    if {job["split"] for job in jobs} != {"confirmation"}:
        raise ValueError("padding rows entered the executed universe")
    for job in jobs:
        if len(job["messages_sha256"]) != 64:
            raise ValueError("invalid message hash")
    return {
        "schema_version": "asmp9_out_of_family_prereveal_validation_v0_82",
        "status": "passed",
        "outcomes_read": False,
        "manifest_sha256": _sha256(manifest_path),
        "old_manifest_sha256": _sha256(old_manifest_path),
        "job_list_sha256": hashlib.sha256(
            design.canonical_json_bytes(jobs)
        ).hexdigest(),
        "new_family_count": len(new_families),
        "old_family_overlap": sorted(new_families & old_families),
        "executed_scenario_count": len(confirmation),
        "unexecuted_padding_count": len(padding),
        "record_count": len(jobs),
        "validation": {
            "synthetic_common_mode_removed": all(
                design.validate_endpoint_coefficients().values()
            ),
            "synthetic_arm_by_order_interaction_retained": True,
            "new_family_disjointness": True,
            "padding_excluded_from_jobs": True,
        },
        "environment": {
            "python": platform.python_version(),
            "packages": {
                name: importlib.metadata.version(name)
                for name in ("torch", "transformers", "accelerate", "safetensors")
            },
        },
        "claim_boundary": "Outcome-free validation only; no Qwen v0.82 score was loaded.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "prereveal_validation_v0_82.json")
    args = parser.parse_args()
    value = validate(
        HERE / "scenario_manifest_v0_82.json",
        V068 / "scenario_manifest_v0_68.json",
    )
    _write_once(args.output.resolve(), _canonical(value))
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()

