"""Contracts for the task-aligned Qwen controller-stalk capture."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from .godel_capture import sha256_file


PROTOCOL_ID = "qwen08_controller_task_capture_v0_1"
PROMPT_SCHEMA = "qwen08_controller_task_prompt_manifest_v0_1"
INDEX_SCHEMA = "qwen08_controller_task_stalk_index_v0_1"
AUTH_SCHEMA = "qwen_holonomy_state_capture_authorization_v0_1"
AUTH_STATUS = "authorized_for_qwen_controller_task_capture"


def canonical_json_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def load_protocol(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("unexpected controller-task capture protocol")
    for field in ("outcomes_consumed", "generation", "gradients", "weight_mutation", "new_invariant_levels"):
        if value.get(field) is not False:
            raise ValueError(f"capture protocol violates the {field} boundary")
    return value


def validate_prompt_manifest(
    manifest: Mapping[str, Any], *, protocol: Mapping[str, Any]
) -> None:
    study = protocol["controller_study"]
    if manifest.get("schema_version") != PROMPT_SCHEMA:
        raise ValueError("unexpected controller-task prompt schema")
    if manifest.get("study_id") != study["study_id"]:
        raise ValueError("prompt manifest belongs to another study")
    if manifest.get("study_config_sha256") != study["config_sha256"]:
        raise ValueError("prompt manifest study-config binding differs")
    if manifest.get("manifest_semantic_sha256") != study["prompt_manifest_semantic_sha256"]:
        raise ValueError("prompt manifest semantic binding differs")
    rows = manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != int(study["expected_prompt_count"]):
        raise ValueError("prompt manifest count differs")
    ids = [str(row.get("row_id", "")) for row in rows]
    if not all(ids) or len(set(ids)) != len(ids):
        raise ValueError("prompt row IDs must be nonempty and unique")
    counts = Counter((str(row.get("application")), str(row.get("geometry_half"))) for row in rows)
    for application in study["applications"]:
        for half in study["halves"]:
            if counts[(application, half)] != int(study["prompts_per_application_half"]):
                raise ValueError(f"prompt cell count differs: {application}/{half}")
    for row in rows:
        prompt = str(row.get("prompt", ""))
        if sha256(prompt.encode("utf-8")).hexdigest() != row.get("prompt_sha256"):
            raise ValueError("prompt text hash mismatch")
        payload = json.loads(prompt.split("\n", 1)[1])
        if set(payload) != set(manifest["allowed_prompt_fields"]):
            raise ValueError("prompt payload field universe differs")
        if set(payload) & set(manifest["forbidden_prompt_fields"]):
            raise ValueError("prompt payload contains a forbidden field")
    semantic = dict(manifest)
    observed = str(semantic.pop("manifest_semantic_sha256", ""))
    if not observed or canonical_json_sha256(semantic) != observed:
        raise ValueError("prompt manifest semantic hash mismatch")
    for field in ("outcomes_consumed", "generation", "gradients", "weight_mutation"):
        if manifest.get(field) is not False:
            raise ValueError(f"prompt manifest violates the {field} boundary")


def chunk_id(application: str, half: str, site: str) -> str:
    return f"{application}--{half}--{site.replace('.', '__')}"


def expected_chunk_keys(protocol: Mapping[str, Any]) -> set[tuple[str, str, str]]:
    return {
        (str(application), str(half), str(site))
        for application in protocol["controller_study"]["applications"]
        for half in protocol["controller_study"]["halves"]
        for site in protocol["capture_contract"]["sites"]
    }


def validate_capture_index(
    value: Mapping[str, Any],
    *,
    protocol: Mapping[str, Any],
    manifest: Mapping[str, Any],
    index_path: Path | None = None,
) -> None:
    if value.get("schema_version") != INDEX_SCHEMA:
        raise ValueError("unexpected controller-task capture-index schema")
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("capture index belongs to another protocol")
    if value.get("prompt_manifest_semantic_sha256") != manifest.get("manifest_semantic_sha256"):
        raise ValueError("capture index prompt binding differs")
    if value.get("study_config_sha256") != protocol["controller_study"]["config_sha256"]:
        raise ValueError("capture index study binding differs")
    for field in ("outcomes_consumed", "generation", "logits_materialized", "gradients", "weight_mutation"):
        if value.get(field) is not False:
            raise ValueError(f"capture index violates the {field} boundary")
    rows = value.get("chunks")
    if not isinstance(rows, list):
        raise ValueError("capture index chunks are required")
    observed = set()
    row_ids = {str(row["row_id"]) for row in manifest["rows"]}
    base = index_path.resolve().parent if index_path is not None else None
    for row in rows:
        key = (str(row.get("application")), str(row.get("geometry_half")), str(row.get("site")))
        if key in observed:
            raise ValueError(f"duplicate capture chunk: {key}")
        observed.add(key)
        ids = list(map(str, row.get("row_ids", ())))
        if len(ids) != int(protocol["controller_study"]["prompts_per_application_half"]) or not set(ids) <= row_ids:
            raise ValueError("capture chunk row universe differs")
        if int(row.get("ambient_dimension", 0)) <= 0:
            raise ValueError("capture chunk ambient dimension is invalid")
        if base is not None:
            path = base / str(row.get("path", ""))
            if not path.is_file() or sha256_file(path) != row.get("sha256"):
                raise ValueError(f"capture chunk missing or changed: {path}")
            with np.load(path, allow_pickle=False) as archive:
                if set(archive.files) != {"activations"}:
                    raise ValueError("capture chunk array universe differs")
                activations = archive["activations"]
                if activations.shape != (len(ids), int(row["ambient_dimension"])) or activations.dtype != np.float32:
                    raise ValueError("capture chunk shape or dtype differs")
                if not np.isfinite(activations).all():
                    raise ValueError("capture chunk contains non-finite values")
    if observed != expected_chunk_keys(protocol):
        raise ValueError("capture index does not contain the complete registered chunk grid")
    if len(rows) != int(protocol["capture_contract"]["expected_chunk_count"]):
        raise ValueError("capture chunk count differs")


__all__ = [
    "AUTH_SCHEMA",
    "AUTH_STATUS",
    "INDEX_SCHEMA",
    "PROTOCOL_ID",
    "PROMPT_SCHEMA",
    "canonical_json_sha256",
    "chunk_id",
    "expected_chunk_keys",
    "load_protocol",
    "validate_capture_index",
    "validate_prompt_manifest",
]
