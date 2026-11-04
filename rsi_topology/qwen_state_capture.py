"""Contracts for chunked Qwen checkpoint-state activation capture."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .godel_capture import HALVES, sha256_file


STATE_CAPTURE_SCHEMA = "qwen_holonomy_state_capture_index_v0_1"
CAUSAL_PROTOCOL_ID = "qwen_holonomy_causal_transfer_v0_1"


def load_causal_protocol(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if value.get("protocol_id") != CAUSAL_PROTOCOL_ID:
        raise ValueError("unexpected Qwen holonomy causal protocol")
    if value.get("new_invariant_levels") is not False:
        raise ValueError("Qwen causal protocol introduces an invariant level")
    return value


def development_state(protocol: Mapping[str, Any], state_id: str) -> Mapping[str, Any]:
    matches = [
        item
        for item in protocol["development_model"]["states"]
        if item.get("state_id") == state_id
    ]
    if len(matches) != 1:
        raise ValueError(f"unknown or duplicate development state: {state_id}")
    return matches[0]


def validate_development_files(
    protocol: Mapping[str, Any], state_id: str
) -> dict[str, str]:
    model = protocol["development_model"]
    root = Path(model["local_path"])
    hashes: dict[str, str] = {}
    for name, expected in model["base_files"].items():
        path = root / name
        if not path.is_file() or sha256_file(path) != expected:
            raise ValueError(f"development base-file lock mismatch: {name}")
        hashes[f"base:{name}"] = expected
    state = development_state(protocol, state_id)
    if state["kind"] == "peft_adapter":
        adapter = Path(state["path"])
        files = {
            "adapter_model.safetensors": state["adapter_sha256"],
            "adapter_config.json": state["adapter_config_sha256"],
        }
        for name, expected in files.items():
            path = adapter / name
            if not path.is_file() or sha256_file(path) != expected:
                raise ValueError(f"adapter lock mismatch for {state_id}: {name}")
            hashes[f"{state_id}:{name}"] = expected
    return hashes


def state_capture_chunk_id(state_id: str, site: str, shard: str, half: str) -> str:
    return f"{state_id}--{site.replace('.', '__')}--{shard}--{half}"


def expected_state_capture_keys(
    *,
    state_id: str,
    sites: Sequence[str],
    context_shards: int,
) -> tuple[tuple[str, str, str, str], ...]:
    return tuple(
        (state_id, site, f"shard-{shard:02d}", half)
        for site in sites
        for shard in range(context_shards)
        for half in HALVES
    )


def resolve_unique_module(model: Any, registered_path: str) -> Any:
    """Resolve an exact path, then a unique wrapper-prefixed suffix."""

    current = model
    try:
        for token in registered_path.split("."):
            current = current[int(token)] if token.isdigit() else getattr(current, token)
        return current
    except (AttributeError, IndexError, KeyError, TypeError):
        pass
    matches = [
        module
        for name, module in model.named_modules()
        if name == registered_path or name.endswith(f".{registered_path}")
    ]
    if len(matches) != 1:
        raise ValueError(
            f"registered module {registered_path!r} resolved to {len(matches)} modules"
        )
    return matches[0]


def validate_state_capture_index(
    value: Mapping[str, Any],
    *,
    protocol: Mapping[str, Any],
    geometry_manifest: Mapping[str, Any],
    index_path: str | Path | None = None,
) -> None:
    if value.get("schema_version") != STATE_CAPTURE_SCHEMA:
        raise ValueError("invalid state-capture index schema")
    state_id = str(value.get("state_id", ""))
    development_state(protocol, state_id)
    sites = tuple(protocol["development_model"]["activation_sites"])
    expected = set(
        expected_state_capture_keys(
            state_id=state_id,
            sites=sites,
            context_shards=int(geometry_manifest["context_shards"]),
        )
    )
    rows = value.get("chunks")
    if not isinstance(rows, list):
        raise ValueError("state-capture index has no chunks")
    observed: set[tuple[str, str, str, str]] = set()
    chunk_ids: set[str] = set()
    base = Path(index_path).resolve().parent if index_path is not None else None
    for row in rows:
        key = (
            str(row.get("state_id", "")),
            str(row.get("site_id", "")),
            str(row.get("context_shard", "")),
            str(row.get("half", "")),
        )
        if key in observed:
            raise ValueError(f"duplicate state-capture key: {key}")
        observed.add(key)
        chunk_id = str(row.get("chunk_id", ""))
        if not chunk_id or chunk_id in chunk_ids:
            raise ValueError("state-capture chunk IDs must be nonempty and unique")
        chunk_ids.add(chunk_id)
        prompt_ids = row.get("prompt_ids")
        if not isinstance(prompt_ids, list) or len(prompt_ids) != int(
            row.get("row_count", -1)
        ):
            raise ValueError(f"state-capture prompt row mismatch: {chunk_id}")
        if int(row.get("ambient_dimension", 0)) <= 0:
            raise ValueError(f"invalid state-capture ambient dimension: {chunk_id}")
        if base is not None:
            path = base / str(row.get("path", ""))
            if not path.is_file() or sha256_file(path) != row.get("sha256"):
                raise ValueError(f"state-capture chunk missing or changed: {chunk_id}")
            with np.load(path, allow_pickle=False) as archive:
                if set(archive.files) != {"activations"}:
                    raise ValueError(f"invalid state-capture NPZ keys: {chunk_id}")
                activations = archive["activations"]
                if activations.shape != (
                    int(row["row_count"]),
                    int(row["ambient_dimension"]),
                ):
                    raise ValueError(f"state-capture shape mismatch: {chunk_id}")
                if not np.all(np.isfinite(activations)):
                    raise ValueError(f"nonfinite state-capture values: {chunk_id}")
    if observed != expected:
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        raise ValueError(
            f"state-capture universe incomplete: missing={missing[:2]} extra={extra[:2]}"
        )
