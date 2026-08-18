from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from rsi_topology.godel_capture import sha256_file
from rsi_topology.qwen_state_capture import (
    STATE_CAPTURE_SCHEMA,
    expected_state_capture_keys,
    resolve_unique_module,
    state_capture_chunk_id,
    validate_state_capture_index,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = json.loads(
    (ROOT / "protocols" / "qwen_holonomy_causal_transfer_v0_1.json").read_text(
        encoding="utf-8"
    )
)
GEOMETRY = json.loads(
    (ROOT / "protocols" / "godel_globes_prompt_manifest_v0_1.json").read_text(
        encoding="utf-8"
    )
)


class Wrapper:
    def __init__(self, named):
        self._named = named

    def named_modules(self):
        return iter(self._named)


def test_module_resolution_accepts_exact_and_unique_wrapper_suffix():
    target = object()
    exact = SimpleNamespace(model=SimpleNamespace(layer=target))
    assert resolve_unique_module(exact, "model.layer") is target

    wrapped = Wrapper([("base_model.model.model.layer", target)])
    assert resolve_unique_module(wrapped, "model.layer") is target
    with pytest.raises(ValueError, match="2 modules"):
        resolve_unique_module(
            Wrapper([("a.model.layer", target), ("b.model.layer", object())]),
            "model.layer",
        )


def test_expected_state_capture_universe_is_state_site_shard_half():
    keys = expected_state_capture_keys(
        state_id="base",
        sites=("model.layers.11", "model.layers.15"),
        context_shards=3,
    )
    assert len(keys) == 12
    assert len(set(keys)) == 12
    assert state_capture_chunk_id(
        "base", "model.layers.11", "shard-00", "construction"
    ).startswith("base--model__layers")


def test_state_capture_index_requires_exact_chunks_and_finite_arrays(tmp_path: Path):
    protocol = json.loads(json.dumps(PROTOCOL))
    protocol["development_model"]["activation_sites"] = [
        "model.layers.11"
    ]
    geometry = json.loads(json.dumps(GEOMETRY))
    geometry["context_shards"] = 2
    chunks = []
    for _state, site, shard, half in expected_state_capture_keys(
        state_id="base",
        sites=protocol["development_model"]["activation_sites"],
        context_shards=2,
    ):
        relative = Path("chunks") / f"{shard}--{half}.npz"
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        values = np.ones((3, 7), dtype=np.float32)
        np.savez(path, activations=values)
        chunks.append(
            {
                "chunk_id": state_capture_chunk_id("base", site, shard, half),
                "state_id": "base",
                "site_id": site,
                "context_shard": shard,
                "half": half,
                "path": relative.as_posix(),
                "sha256": sha256_file(path),
                "prompt_ids": [f"p{index}" for index in range(3)],
                "row_count": 3,
                "ambient_dimension": 7,
                "dtype": "float32",
            }
        )
    value = {
        "schema_version": STATE_CAPTURE_SCHEMA,
        "state_id": "base",
        "chunks": chunks,
    }
    index = tmp_path / "state_capture_index.json"
    index.write_text(json.dumps(value), encoding="utf-8")
    validate_state_capture_index(
        value,
        protocol=protocol,
        geometry_manifest=geometry,
        index_path=index,
    )
    value["chunks"] = value["chunks"][:-1]
    with pytest.raises(ValueError, match="universe incomplete"):
        validate_state_capture_index(
            value,
            protocol=protocol,
            geometry_manifest=geometry,
            index_path=index,
        )
