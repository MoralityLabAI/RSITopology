"""Pair-view analysis over sealed Qwen state-capture indices.

The live capture protocol stores one complete index per model state.  The
existing Godel analysis is deliberately a two-axis instrument, so this module
constructs three immutable base-to-adapter pair views without copying or
rewriting activation arrays.  Every pair index binds the source index hashes
and every source chunk is revalidated before analysis.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .godel_analysis import analyze_godel_capture, write_analysis_bundle
from .godel_capture import (
    CaptureChunk,
    CaptureStore,
    canonical_json_bytes,
    canonical_json_sha256,
    sha256_file,
    write_once_or_equal,
)
from .qwen_state_capture import (
    load_causal_protocol,
    validate_state_capture_index,
)


ANALYSIS_PROTOCOL_ID = "qwen08_holonomy_geometry_analysis_v0_1"
DENSE_ANALYSIS_PROTOCOL_ID = "qwen08_dense_local_holonomy_analysis_v0_1"
SUPPORTED_ANALYSIS_PROTOCOL_IDS = {
    ANALYSIS_PROTOCOL_ID,
    DENSE_ANALYSIS_PROTOCOL_ID,
}
PAIR_INDEX_SCHEMA = "qwen08_holonomy_pair_capture_index_v0_1"


def load_analysis_protocol(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if value.get("protocol_id") not in SUPPORTED_ANALYSIS_PROTOCOL_IDS:
        raise ValueError("unexpected Qwen geometry-analysis protocol")
    if value.get("new_invariant_levels") is not False:
        raise ValueError("analysis protocol introduces an invariant level")
    pairs = value.get("state_pairs")
    if not isinstance(pairs, list) or not pairs:
        raise ValueError("analysis protocol has no state pairs")
    seen: set[tuple[str, str]] = set()
    states = set(value.get("state_capture_indices", {}))
    for raw in pairs:
        pair = tuple(map(str, raw))
        if len(pair) != 2 or pair[0] == pair[1]:
            raise ValueError("state pairs must contain two distinct states")
        if pair in seen or not set(pair) <= states:
            raise ValueError("unknown or duplicate state pair")
        seen.add(pair)
    return value


def pair_slug(pair: Sequence[str]) -> str:
    if len(pair) != 2:
        raise ValueError("pair must have length two")
    return f"{pair[0]}--vs--{pair[1]}".replace("/", "_").replace("\\", "_")


def pair_analysis_protocol(
    registration: Mapping[str, Any], pair: Sequence[str]
) -> dict[str, Any]:
    """Return the exact protocol view consumed by ``godel_analysis``."""

    pair_tuple = tuple(map(str, pair))
    registered = {tuple(map(str, item)) for item in registration["state_pairs"]}
    if pair_tuple not in registered:
        raise ValueError("pair is not registered")
    return {
        "protocol_id": f"{registration['protocol_id']}:{pair_slug(pair_tuple)}",
        "runtime_precisions": list(pair_tuple),
        "candidate_sites": list(registration["candidate_sites"]),
        "primary_object": dict(registration["primary_object"]),
        "instrument_calibration": dict(registration["instrument_calibration"]),
        "graph": dict(registration["graph"]),
        "holonomy": dict(registration["holonomy"]),
        "corotation": dict(registration["corotation"]),
        "gauge_preflight": dict(registration["gauge_preflight"]),
        "sectioning": dict(registration["sectioning"]),
        "aggregate_identity_gate": dict(registration["aggregate_identity_gate"]),
        "consumer_rules": dict(registration["consumer_rules"]),
        "claim_boundary": str(registration["claim_boundary"]),
        "analysis_registration_protocol_id": str(registration["protocol_id"]),
    }


def _resolve_bound_path(raw: str, *, root: Path) -> Path:
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def validate_registered_inputs(
    *, registration_path: str | Path, repository_root: str | Path
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Path]]:
    registration_path = Path(registration_path).resolve()
    root = Path(repository_root).resolve()
    registration = load_analysis_protocol(registration_path)

    capture_entry = registration["capture_protocol"]
    capture_path = _resolve_bound_path(str(capture_entry["path"]), root=root)
    if sha256_file(capture_path) != str(capture_entry["sha256"]):
        raise ValueError("capture protocol hash mismatch")
    capture_protocol = load_causal_protocol(capture_path)

    scientific_entry = registration.get("scientific_protocol")
    scientific_hash = None
    if scientific_entry is not None:
        scientific_path = _resolve_bound_path(
            str(scientific_entry["path"]), root=root
        )
        scientific_hash = sha256_file(scientific_path)
        if scientific_hash != str(scientific_entry["sha256"]):
            raise ValueError("scientific protocol hash mismatch")

    manifest_entry = registration["prompt_manifest"]
    manifest_path = _resolve_bound_path(str(manifest_entry["path"]), root=root)
    if sha256_file(manifest_path) != str(manifest_entry["sha256"]):
        raise ValueError("prompt manifest hash mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))

    paths: dict[str, Path] = {}
    for state_id, entry in registration["state_capture_indices"].items():
        path = _resolve_bound_path(str(entry["path"]), root=root)
        if sha256_file(path) != str(entry["sha256"]):
            raise ValueError(f"state capture index hash mismatch: {state_id}")
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("state_id") != state_id:
            raise ValueError(f"state capture ID mismatch: {state_id}")
        validate_state_capture_index(
            value,
            protocol=capture_protocol,
            geometry_manifest=manifest,
            index_path=path,
        )
        if value.get("protocol_sha256") != str(capture_entry["sha256"]):
            raise ValueError(f"state capture protocol binding mismatch: {state_id}")
        if value.get("geometry_manifest_sha256") != str(manifest_entry["sha256"]):
            raise ValueError(f"state capture manifest binding mismatch: {state_id}")
        if scientific_hash is not None:
            scientific = value.get("scientific_protocol")
            if not isinstance(scientific, Mapping) or scientific.get(
                "sha256"
            ) != scientific_hash:
                raise ValueError(
                    f"state capture scientific binding mismatch: {state_id}"
                )
        paths[state_id] = path
    return registration, capture_protocol, manifest, paths


def build_pair_store(
    *,
    registration: Mapping[str, Any],
    registration_path: str | Path,
    manifest: Mapping[str, Any],
    state_index_paths: Mapping[str, Path],
    pair: Sequence[str],
    output_dir: str | Path,
) -> CaptureStore:
    pair_tuple = tuple(map(str, pair))
    protocol_view = pair_analysis_protocol(registration, pair_tuple)
    chunks: dict[tuple[str, str, str, str], CaptureChunk] = {}
    source_indices: dict[str, dict[str, str]] = {}
    pair_rows: list[dict[str, Any]] = []
    for state_id in pair_tuple:
        index_path = state_index_paths[state_id]
        value = json.loads(index_path.read_text(encoding="utf-8"))
        source_indices[state_id] = {
            "path": str(index_path),
            "sha256": sha256_file(index_path),
        }
        for row in value["chunks"]:
            key = (
                state_id,
                str(row["site_id"]),
                str(row["context_shard"]),
                str(row["half"]),
            )
            if key in chunks:
                raise ValueError(f"duplicate pair chunk key: {key}")
            chunk_path = (index_path.parent / str(row["path"])).resolve()
            chunk = CaptureChunk(
                chunk_id=str(row["chunk_id"]),
                runtime_precision=state_id,
                site_id=key[1],
                context_shard=key[2],
                half=key[3],
                path=chunk_path,
                sha256=str(row["sha256"]),
                prompt_ids=tuple(map(str, row["prompt_ids"])),
                row_count=int(row["row_count"]),
                ambient_dimension=int(row["ambient_dimension"]),
                dtype=str(row["dtype"]),
            )
            chunks[key] = chunk
            pair_rows.append(
                {
                    "state_id": state_id,
                    "chunk_id": chunk.chunk_id,
                    "site_id": chunk.site_id,
                    "context_shard": chunk.context_shard,
                    "half": chunk.half,
                    "source_index_sha256": source_indices[state_id]["sha256"],
                    "chunk_sha256": chunk.sha256,
                    "row_count": chunk.row_count,
                    "ambient_dimension": chunk.ambient_dimension,
                }
            )

    expected_count = (
        len(pair_tuple)
        * len(registration["candidate_sites"])
        * int(manifest["context_shards"])
        * 2
    )
    if len(chunks) != expected_count:
        raise ValueError("pair view does not cover the exact chunk universe")
    pair_index = {
        "schema_version": PAIR_INDEX_SCHEMA,
        "analysis_registration_sha256": sha256_file(registration_path),
        "pair_protocol_canonical_sha256": canonical_json_sha256(protocol_view),
        "state_pair": list(pair_tuple),
        "source_state_indices": source_indices,
        "prompt_manifest_sha256": str(registration["prompt_manifest"]["sha256"]),
        "outcomes_read": False,
        "weight_mutation": False,
        "chunks": sorted(
            pair_rows,
            key=lambda item: (
                item["state_id"],
                item["site_id"],
                item["context_shard"],
                item["half"],
            ),
        ),
    }
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    index_path = output / "pair_capture_index.json"
    write_once_or_equal(index_path, canonical_json_bytes(pair_index))
    return CaptureStore(index_path=index_path, index=pair_index, chunks=chunks)


def analyze_registered_pairs(
    *,
    registration_path: str | Path,
    repository_root: str | Path,
    output_dir: str | Path,
    seed: int,
    selected_pair: Sequence[str] | None = None,
) -> dict[str, Any]:
    registration, _, manifest, state_paths = validate_registered_inputs(
        registration_path=registration_path,
        repository_root=repository_root,
    )
    pairs = [tuple(map(str, item)) for item in registration["state_pairs"]]
    if selected_pair is not None:
        selected = tuple(map(str, selected_pair))
        if selected not in pairs:
            raise ValueError("selected pair is not registered")
        pairs = [selected]
    output = Path(output_dir).resolve()
    pair_receipts: list[dict[str, Any]] = []
    for pair_index, pair in enumerate(pairs):
        pair_dir = output / pair_slug(pair)
        store = build_pair_store(
            registration=registration,
            registration_path=registration_path,
            manifest=manifest,
            state_index_paths=state_paths,
            pair=pair,
            output_dir=pair_dir,
        )
        protocol_view = pair_analysis_protocol(registration, pair)
        result = analyze_godel_capture(
            store=store,
            manifest=manifest,
            protocol=protocol_view,
            seed=int(seed) + pair_index * 100003,
        )
        result["analysis_registration_sha256"] = sha256_file(registration_path)
        result["state_pair"] = list(pair)
        result["source_state_indices"] = store.index["source_state_indices"]
        release = write_analysis_bundle(pair_dir, result)
        pair_receipts.append(
            {
                "state_pair": list(pair),
                "pair_capture_index_sha256": sha256_file(store.index_path),
                "release_manifest_sha256": sha256_file(pair_dir / "release_manifest.json"),
                "release_manifest_payload_sha256": release["manifest_payload_sha256"],
                "summary": result["summary"],
            }
        )
    composite = {
        "schema_version": "qwen08_holonomy_geometry_composite_v0_1",
        "analysis_registration_sha256": sha256_file(registration_path),
        "pair_receipts": pair_receipts,
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
        "claim_boundary": registration["claim_boundary"],
    }
    output.mkdir(parents=True, exist_ok=True)
    name = "composite_receipt.json" if selected_pair is None else f"{pair_slug(pairs[0])}_receipt.json"
    write_once_or_equal(output / name, canonical_json_bytes(composite))
    return composite
