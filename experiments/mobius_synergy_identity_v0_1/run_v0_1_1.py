"""Provenance-hardened, write-once runner for the frozen Mobius v0.1 analysis."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
from typing import Any, Mapping

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run as parent  # noqa: E402

AMENDMENT_PATH = HERE / "protocol_v0_1_1_amendment.json"
REGISTRATION_PATH = HERE / "registration_v0_1_1.json"
SOURCE_PATHS = (HERE / "mobius.py", HERE / "run.py", Path(__file__).resolve())


def _load_json(path: Path) -> dict[str, Any]:
    return parent.load_json(path)


def _canonical(value: object) -> bytes:
    return parent.canonical_json_bytes(value) + b"\n"


def _write_once(path: Path, value: object) -> None:
    parent.write_once_or_equal(path, _canonical(value))


def environment_identity() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
    }


def _resolved_child(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"capture chunk escapes capture root: {relative}") from exc
    return candidate


def validate_indexed_chunks(capture_index_path: Path) -> dict[str, Any]:
    """Recompute every indexed chunk claim from the sealed NPZ bytes."""

    capture_index_path = capture_index_path.resolve()
    index = _load_json(capture_index_path)
    chunks = index.get("chunks")
    if not isinstance(chunks, list) or not chunks:
        raise ValueError("capture index has no chunk universe")
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    checked: list[dict[str, Any]] = []
    for raw in chunks:
        if not isinstance(raw, Mapping):
            raise ValueError("capture chunk entry is not an object")
        chunk_id = str(raw.get("chunk_id", ""))
        relative = str(raw.get("path", ""))
        if not chunk_id or chunk_id in seen_ids:
            raise ValueError(f"missing or duplicate chunk_id: {chunk_id!r}")
        if not relative or relative in seen_paths:
            raise ValueError(f"missing or duplicate chunk path: {relative!r}")
        seen_ids.add(chunk_id)
        seen_paths.add(relative)
        path = _resolved_child(capture_index_path.parent, relative)
        if not path.is_file():
            raise FileNotFoundError(f"indexed chunk is missing: {path}")
        observed_hash = parent.sha256_file(path)
        if observed_hash != str(raw.get("sha256", "")):
            raise ValueError(f"indexed chunk hash mismatch: {chunk_id}")
        prompt_ids = [str(value) for value in raw.get("prompt_ids", [])]
        if not prompt_ids or len(prompt_ids) != len(set(prompt_ids)):
            raise ValueError(f"chunk prompt IDs are empty or duplicated: {chunk_id}")
        with np.load(path, allow_pickle=False) as archive:
            if archive.files != ["activations"]:
                raise ValueError(f"unexpected NPZ members: {chunk_id}")
            activations = np.asarray(archive["activations"])
        expected_shape = (
            int(raw.get("row_count", -1)),
            int(raw.get("ambient_dimension", -1)),
        )
        if activations.shape != expected_shape or activations.ndim != 2:
            raise ValueError(f"indexed chunk shape mismatch: {chunk_id}")
        if len(prompt_ids) != activations.shape[0]:
            raise ValueError(f"chunk prompt/activation row mismatch: {chunk_id}")
        if str(activations.dtype) != str(raw.get("dtype", "")):
            raise ValueError(f"indexed chunk dtype mismatch: {chunk_id}")
        if not np.isfinite(activations).all():
            raise ValueError(f"indexed chunk contains nonfinite values: {chunk_id}")
        checked.append(
            {
                "chunk_id": chunk_id,
                "path": relative,
                "sha256": observed_hash,
                "shape": list(activations.shape),
                "dtype": str(activations.dtype),
            }
        )
    return {
        "schema_version": "mobius_capture_chunk_validation_v0_1_1",
        "capture_index_path": str(capture_index_path),
        "capture_index_sha256": parent.sha256_file(capture_index_path),
        "chunk_count": len(checked),
        "all_indexed_chunks_valid": True,
        "chunks": checked,
    }


def validate_v0_1_1_registration(path: Path) -> tuple[dict[str, Any], Path, Path]:
    path = path.resolve()
    value = _load_json(path)
    if path != REGISTRATION_PATH.resolve():
        raise ValueError("claim runner requires the canonical v0.1.1 registration")
    if value.get("status") != "registered_before_claim_eligible_analysis":
        raise ValueError("v0.1.1 registration status is not admissible")
    if value.get("amendment_sha256") != parent.sha256_file(AMENDMENT_PATH):
        raise ValueError("registered amendment hash mismatch")
    if value.get("parent_registration_sha256") != parent.sha256_file(HERE / "registration.json"):
        raise ValueError("registered parent registration hash mismatch")
    for source in SOURCE_PATHS:
        if value.get("source_sha256", {}).get(source.name) != parent.sha256_file(source):
            raise ValueError(f"registered source hash mismatch: {source.name}")
    expected_environment = value.get("environment_lock")
    if expected_environment != environment_identity():
        raise ValueError("registered analysis environment mismatch")
    _, capture, prompts = parent.validate_registration(HERE / "registration.json")
    if value.get("capture_index_sha256") != parent.sha256_file(capture):
        raise ValueError("v0.1.1 capture-index hash mismatch")
    if value.get("prompt_manifest_sha256") != parent.sha256_file(prompts):
        raise ValueError("v0.1.1 prompt-manifest hash mismatch")
    return value, capture, prompts


def _artifact_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): parent.sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "release_manifest_v0_1_1.json"
    }


def analyze(args: argparse.Namespace) -> None:
    registration, capture, prompts = validate_v0_1_1_registration(args.registration)
    protocol = _load_json(parent.PROTOCOL_PATH)
    parent.validate_input_contract(_load_json(capture), _load_json(prompts), protocol)
    final = args.output_dir.resolve()
    staging = final.with_name(final.name + ".staging-v0_1_1")
    if final.exists():
        raise FileExistsError(f"write-once final output already exists: {final}")
    if staging.exists():
        raise FileExistsError(f"staging output already exists; audit before retry: {staging}")
    staging.mkdir(parents=True)
    started = datetime.now(timezone.utc).isoformat()
    try:
        chunk_receipt = validate_indexed_chunks(capture)
        _write_once(staging / "input_chunk_validation.json", chunk_receipt)
        _write_once(staging / "environment_lock.json", environment_identity())
        summary = parent.run_analysis(
            capture_index_path=capture,
            prompt_manifest_path=prompts,
            output_dir=staging,
            protocol=protocol,
            claim_level="registered_real_model_analysis_v0_1_1",
            smoke=False,
        )
        run_receipt = {
            "schema_version": "mobius_synergy_identity_run_receipt_v0_1_1",
            "status": "completed",
            "started_utc": started,
            "completed_utc": datetime.now(timezone.utc).isoformat(),
            "registration_sha256": parent.sha256_file(args.registration.resolve()),
            "registration_source_commit": registration["registration_source_commit"],
            "capture_chunk_count": chunk_receipt["chunk_count"],
            "outcomes_consumed": False,
            "weight_mutation_performed": False,
            "confirmatory_decision": summary["confirmatory_decision"],
        }
        _write_once(staging / "run_receipt_v0_1_1.json", run_receipt)
        manifest = {
            "schema_version": "mobius_synergy_identity_release_v0_1_1",
            "status": "sealed_complete",
            "artifacts": _artifact_hashes(staging),
        }
        _write_once(staging / "release_manifest_v0_1_1.json", manifest)
        staging.replace(final)
    except Exception:
        _write_once(
            staging / "FAILED.json",
            {
                "schema_version": "mobius_synergy_identity_failed_run_v0_1_1",
                "started_utc": started,
                "failed_utc": datetime.now(timezone.utc).isoformat(),
                "final_output_was_written": False,
            },
        )
        raise
    print(json.dumps(summary, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--registration", type=Path, required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    value.set_defaults(function=analyze)
    return value


def main() -> None:
    args = parser().parse_args()
    args.function(args)


if __name__ == "__main__":
    main()
