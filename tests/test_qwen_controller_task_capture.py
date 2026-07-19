from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from rsi_topology.godel_capture import sha256_file
from rsi_topology.qwen_controller_task_capture import (
    INDEX_SCHEMA,
    expected_chunk_keys,
    load_protocol,
    validate_capture_index,
    validate_prompt_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "protocols" / "qwen08_controller_task_capture_v0_1.json"
GYM = Path(r"C:\projects\HybridTRMLDT\ldt_trm_research_gym_v0_0_2\ldt_trm_research_gym")
MANIFEST = GYM / "data" / "bridge" / "qwen08_controller_task_prompt_manifest_v0_1.json"


def test_registered_controller_task_manifest_and_protocol_are_cross_bound():
    protocol = load_protocol(PROTOCOL)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate_prompt_manifest(manifest, protocol=protocol)

    assert protocol["capture_contract"]["expected_chunk_count"] == 36
    assert len(expected_chunk_keys(protocol)) == 36
    assert sha256_file(MANIFEST) == protocol["controller_study"]["prompt_manifest_file_sha256"]
    assert manifest["manifest_semantic_sha256"] == protocol["controller_study"]["prompt_manifest_semantic_sha256"]
    assert protocol["outcomes_consumed"] is False
    assert protocol["capture_contract"]["logits_materialized"] is False


def test_capture_index_validates_complete_write_once_grid(tmp_path: Path):
    protocol = load_protocol(PROTOCOL)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    chunks = []
    for application, half, site in sorted(expected_chunk_keys(protocol)):
        rows = [row for row in manifest["rows"] if row["application"] == application and row["geometry_half"] == half]
        relative = Path("chunks") / f"{application}-{half}-{site.rsplit('.', 1)[-1]}.npz"
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            np.savez_compressed(handle, activations=np.zeros((32, 8), dtype=np.float32))
        chunks.append(
            {
                "application": application,
                "geometry_half": half,
                "site": site,
                "path": relative.as_posix(),
                "sha256": sha256_file(path),
                "row_ids": [row["row_id"] for row in rows],
                "row_count": 32,
                "ambient_dimension": 8,
            }
        )
    value = {
        "schema_version": INDEX_SCHEMA,
        "protocol_id": protocol["protocol_id"],
        "study_config_sha256": protocol["controller_study"]["config_sha256"],
        "prompt_manifest_semantic_sha256": manifest["manifest_semantic_sha256"],
        "chunks": chunks,
        "outcomes_consumed": False,
        "generation": False,
        "logits_materialized": False,
        "gradients": False,
        "weight_mutation": False,
    }
    index = tmp_path / "state_capture_index.json"
    validate_capture_index(value, protocol=protocol, manifest=manifest, index_path=index)

    value["chunks"].pop()
    with pytest.raises(ValueError, match="complete registered chunk grid"):
        validate_capture_index(value, protocol=protocol, manifest=manifest)


def test_capture_entrypoint_uses_base_model_and_is_fail_closed():
    source = (ROOT / "scripts" / "capture_qwen08_controller_tasks.py").read_text(encoding="utf-8")
    prepare = (ROOT / "scripts" / "prepare_qwen08_controller_task_capture.py").read_text(encoding="utf-8")
    assert "base_model(**tokens" in source
    assert "logits_materialized\": False" in source
    assert "caps_confirmed_by_user" in source
    assert "requires --confirm-caps" in prepare
    assert "clean committed RSITopology worktree" in prepare
