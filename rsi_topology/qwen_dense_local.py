"""Frozen prompt-corpus helpers for the dense-local Qwen geometry run."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any, Mapping, Sequence

from .godel_capture import (
    generate_prompt_manifest,
    sha256_file,
    validate_prompt_manifest,
)


PROTOCOL_ID = "qwen08_dense_local_holonomy_v0_1"


def load_dense_protocol(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("unexpected dense-local protocol")
    if value.get("status") != "registered_not_run":
        raise ValueError("dense-local protocol is not in its registered prereveal state")
    if value.get("new_invariant_levels") is not False:
        raise ValueError("dense-local protocol introduces an invariant level")
    return value


def prompt_byte_set(value: Mapping[str, Any]) -> set[bytes]:
    rows = value.get("rows")
    if not isinstance(rows, list):
        raise ValueError("prompt artifact has no row list")
    result = {str(row.get("prompt", "")).encode("utf-8") for row in rows}
    if b"" in result:
        raise ValueError("prompt artifact contains an empty prompt")
    return result


def generate_dense_manifest(
    *, protocol_path: str | Path
) -> dict[str, Any]:
    path = Path(protocol_path)
    protocol = load_dense_protocol(path)
    design = protocol["prompt_design"]
    value = generate_prompt_manifest(
        protocol_sha256=sha256_file(path),
        seed=int(design["seed"]),
        families=tuple(map(str, design["families"])),
        subconditions_per_family=int(design["subconditions_per_family"]),
        context_shards=int(design["context_shards"]),
        prompts_per_half=int(
            design["prompts_per_subcondition_per_half_per_shard"]
        ),
    )
    # Several task generators have deliberately small semantic support (for
    # example, affine starts repeat).  The registered dense design calls for
    # prompt replicas, not duplicated byte strings.  Add an opaque,
    # label-agnostic nonce so every activation is a distinct context without
    # changing the task or answer key.  Hashing the prompt ID removes readable
    # family/shard structure from the nonce itself.
    seed = int(design["seed"])
    for row in value["rows"]:
        payload = f"{seed}\0{row['prompt_id']}".encode("utf-8")
        nonce = hashlib.sha256(payload).hexdigest()[:20]
        row["prompt"] = f"{row['prompt']} Opaque sample nonce: {nonce}."
    value["dense_replica_disambiguation"] = {
        "kind": "sha256_seed_and_prompt_id_prefix",
        "hex_characters": 20,
        "semantic_role": "label-agnostic context nonce; excluded from answer key",
    }
    validate_dense_manifest(value, protocol_path=path)
    return value


def validate_dense_manifest(
    value: Mapping[str, Any],
    *,
    protocol_path: str | Path,
    separation_artifacts: Sequence[Mapping[str, Any]] = (),
) -> None:
    path = Path(protocol_path)
    protocol = load_dense_protocol(path)
    design = protocol["prompt_design"]
    validate_prompt_manifest(value)
    expected = {
        "protocol_sha256": sha256_file(path),
        "seed": int(design["seed"]),
        "families": list(map(str, design["families"])),
        "subconditions_per_family": int(design["subconditions_per_family"]),
        "context_shards": int(design["context_shards"]),
        "prompts_per_subcondition_per_half_per_shard": int(
            design["prompts_per_subcondition_per_half_per_shard"]
        ),
        "prompt_count": int(design["prompts_per_state"]),
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            raise ValueError(f"dense prompt manifest differs at {key}")
    dense = prompt_byte_set(value)
    if len(dense) != int(value["prompt_count"]):
        raise ValueError("dense prompt bytes are not unique")
    for artifact in separation_artifacts:
        overlap = dense & prompt_byte_set(artifact)
        if overlap:
            raise ValueError(
                f"dense prompt corpus overlaps a registered prior split ({len(overlap)})"
            )


def separation_receipt(
    value: Mapping[str, Any],
    *,
    compared_paths: Sequence[str | Path],
) -> dict[str, Any]:
    dense = prompt_byte_set(value)
    comparisons = []
    for raw_path in compared_paths:
        path = Path(raw_path).resolve()
        artifact = json.loads(path.read_text(encoding="utf-8-sig"))
        overlap = dense & prompt_byte_set(artifact)
        comparisons.append(
            {
                "path": str(path),
                "sha256": sha256_file(path),
                "prompt_count": len(prompt_byte_set(artifact)),
                "byte_identical_overlap_count": len(overlap),
            }
        )
    return {
        "schema_version": "qwen08_dense_local_prompt_separation_v0_1",
        "dense_prompt_count": len(dense),
        "comparisons": comparisons,
        "passed": all(
            row["byte_identical_overlap_count"] == 0 for row in comparisons
        ),
    }
