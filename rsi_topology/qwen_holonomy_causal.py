"""Sealed prompt contracts for real-model holonomy causal falsification.

The geometry construction and validation prompts live in the existing Godel
manifest.  This module creates a third, byte-disjoint prompt universe that may
be read only after the geometry-derived loop, direction, norm, and fold table
has been sealed.  It deliberately contains no model-loading code.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .godel_capture import (
    FAMILIES,
    _prompt_for,
    _rng,
    audit_prompt_answer_keys,
    canonical_json_bytes,
    sha256_file,
)


CAUSAL_PROTOCOL_ID = "qwen_holonomy_causal_transfer_v0_1"
CAUSAL_OUTER_SCHEMA = "qwen_holonomy_causal_outer_manifest_v0_1"
CAUSAL_HALF = "causal_outer"


def generate_causal_outer_manifest(
    *,
    protocol_sha256: str,
    geometry_manifest_sha256: str,
    seed: int = 2026071604,
    families: Sequence[str] = FAMILIES,
    subconditions_per_family: int = 9,
    context_shards: int = 8,
    prompts_per_cell: int = 2,
) -> dict[str, Any]:
    """Return a deterministic third split for causal intervention outcomes."""

    if len(protocol_sha256) != 64 or len(geometry_manifest_sha256) != 64:
        raise ValueError("protocol and geometry-manifest hashes must be SHA-256")
    if subconditions_per_family < 2 or subconditions_per_family > 9:
        raise ValueError("subconditions_per_family must lie in [2, 9]")
    if context_shards < 2 or prompts_per_cell < 2:
        raise ValueError("at least two shards and two prompts per cell are required")
    unknown = sorted(set(families) - set(FAMILIES))
    if unknown:
        raise ValueError(f"unknown behavior families: {unknown}")

    rows: list[dict[str, Any]] = []
    for family_index, family in enumerate(families):
        for subcondition in range(subconditions_per_family):
            for shard in range(context_shards):
                for within_cell in range(prompts_per_cell):
                    # The outer offset keeps graph-label parity balanced while
                    # preventing accidental reuse of a construction sample id.
                    sample_index = 100 + 2 * shard + within_cell
                    generator = _rng(
                        seed,
                        family_index,
                        subcondition,
                        shard,
                        sample_index,
                    )
                    prompt, answer, parameters = _prompt_for(
                        family,
                        rng=generator,
                        subcondition=subcondition,
                        sample_index=sample_index,
                    )
                    # A fixed semantic-neutral wrapper guarantees byte-level
                    # split separation even when a small discrete generator
                    # happens to redraw a geometry item.
                    prompt = f"Independent held-out check. {prompt}"
                    rows.append(
                        {
                            "prompt_id": (
                                f"ggc01-{family_index:02d}-{subcondition:02d}-"
                                f"{shard:02d}-{within_cell}"
                            ),
                            "behavior_family": family,
                            "subcondition_id": (
                                f"{family}-condition-{subcondition:02d}"
                            ),
                            "context_shard": f"shard-{shard:02d}",
                            "half": CAUSAL_HALF,
                            "within_cell_index": within_cell,
                            "prompt": prompt,
                            "expected_answer": answer,
                            "response_contract": (
                                "teacher-forced completion of the registered "
                                "ANSWER=<value> string"
                            ),
                            "subcondition_parameters": parameters,
                            "geometry_consumes_expected_answer": False,
                            "geometry_consumes_prompt": False,
                            "candidate_selector_consumes_prompt": False,
                        }
                    )

    value = {
        "schema_version": CAUSAL_OUTER_SCHEMA,
        "protocol_id": CAUSAL_PROTOCOL_ID,
        "protocol_sha256": protocol_sha256,
        "geometry_prompt_manifest_sha256": geometry_manifest_sha256,
        "seed": seed,
        "families": list(families),
        "subconditions_per_family": subconditions_per_family,
        "context_shards": context_shards,
        "halves": [CAUSAL_HALF],
        "prompts_per_subcondition_per_shard": prompts_per_cell,
        "prompt_count": len(rows),
        "geometry_outcomes_unread": True,
        "candidate_table_must_be_hashed_before_prompt_read": True,
        "rows": rows,
    }
    validate_causal_outer_manifest(value)
    return value


def validate_causal_outer_manifest(
    value: Mapping[str, Any],
    *,
    geometry_manifest: Mapping[str, Any] | None = None,
) -> None:
    if value.get("schema_version") != CAUSAL_OUTER_SCHEMA:
        raise ValueError("invalid causal-outer manifest schema")
    if value.get("protocol_id") != CAUSAL_PROTOCOL_ID:
        raise ValueError("causal-outer protocol mismatch")
    if value.get("geometry_outcomes_unread") is not True:
        raise ValueError("geometry outcomes must remain unread")
    if value.get("candidate_table_must_be_hashed_before_prompt_read") is not True:
        raise ValueError("candidate-table prereveal rule is missing")
    if value.get("halves") != [CAUSAL_HALF]:
        raise ValueError("causal manifest must contain only causal_outer")

    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) != int(value.get("prompt_count", -1)):
        raise ValueError("causal prompt_count does not match rows")
    ids = [str(row.get("prompt_id", "")) for row in rows]
    if not all(ids) or len(ids) != len(set(ids)):
        raise ValueError("causal prompt IDs must be nonempty and unique")

    expected = {
        (
            family,
            f"{family}-condition-{condition:02d}",
            f"shard-{shard:02d}",
        )
        for family in value["families"]
        for condition in range(int(value["subconditions_per_family"]))
        for shard in range(int(value["context_shards"]))
    }
    counts: dict[tuple[str, str, str], int] = {}
    for row in rows:
        if row.get("half") != CAUSAL_HALF:
            raise ValueError("non-causal row in causal manifest")
        if row.get("geometry_consumes_expected_answer") is not False:
            raise ValueError("geometry must not consume outer expected answers")
        if row.get("geometry_consumes_prompt") is not False:
            raise ValueError("geometry must not consume outer prompts")
        if row.get("candidate_selector_consumes_prompt") is not False:
            raise ValueError("candidate selector must be blind to outer prompts")
        key = (
            str(row.get("behavior_family")),
            str(row.get("subcondition_id")),
            str(row.get("context_shard")),
        )
        counts[key] = counts.get(key, 0) + 1
    if set(counts) != expected:
        raise ValueError("causal family/subcondition/shard universe differs")
    required = int(value["prompts_per_subcondition_per_shard"])
    if any(count != required for count in counts.values()):
        raise ValueError("causal prompt cells are unbalanced")
    failures = audit_prompt_answer_keys(value)
    if failures:
        raise ValueError(f"causal answer-key audit failed: {failures[:3]}")

    if geometry_manifest is not None:
        geometry_rows = geometry_manifest.get("rows")
        if not isinstance(geometry_rows, list):
            raise ValueError("geometry manifest has no rows")
        geometry_prompts = {str(row.get("prompt", "")) for row in geometry_rows}
        outer_prompts = {str(row.get("prompt", "")) for row in rows}
        overlap = sorted(geometry_prompts & outer_prompts)
        if overlap:
            raise ValueError(
                f"causal and geometry prompt bytes overlap ({len(overlap)} rows)"
            )


def load_and_validate_outer_manifest(
    path: str | Path, *, geometry_manifest_path: str | Path | None = None
) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    geometry = None
    if geometry_manifest_path is not None:
        geometry_path = Path(geometry_manifest_path)
        if sha256_file(geometry_path) != value.get("geometry_prompt_manifest_sha256"):
            raise ValueError("causal manifest does not bind geometry manifest bytes")
        geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    validate_causal_outer_manifest(value, geometry_manifest=geometry)
    return value


def causal_manifest_bytes(value: Mapping[str, Any]) -> bytes:
    validate_causal_outer_manifest(value)
    return canonical_json_bytes(value)
