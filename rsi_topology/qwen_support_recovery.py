"""Target-blind sample-support diagnostic after local Qwen rank collapse."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .discovery import discover_between_class_rank_filtration
from .godel_capture import (
    canonical_json_bytes,
    prompt_rows_for_chunk,
    sha256_file,
    write_once_or_equal,
)
from .qwen_geometry_analysis import validate_registered_inputs


PROTOCOL_ID = "qwen08_between_class_support_recovery_v0_1"


def load_protocol(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("unexpected support-recovery protocol")
    if value.get("new_invariant_levels") is not False:
        raise ValueError("support recovery introduces an invariant level")
    return value


def _seed(seed: int, *parts: str) -> int:
    digest = hashlib.sha256("\0".join(parts).encode("utf-8")).digest()
    return (int(seed) + int.from_bytes(digest[:4], "big")) % (2**32)


def cyclic_window(start: int, size: int, total: int = 8) -> tuple[str, ...]:
    if size < 1 or size > total:
        raise ValueError("invalid context-pool size")
    if size == total:
        return tuple(f"shard-{index:02d}" for index in range(total))
    return tuple(f"shard-{(start + offset) % total:02d}" for offset in range(size))


def _chunk_map(index_path: Path) -> dict[tuple[str, str, str], Mapping[str, Any]]:
    value = json.loads(index_path.read_text(encoding="utf-8"))
    result = {}
    for row in value["chunks"]:
        key = (str(row["site_id"]), str(row["context_shard"]), str(row["half"]))
        if key in result:
            raise ValueError("duplicate state chunk")
        result[key] = row
    return result


def _window_features(
    *,
    index_path: Path,
    chunks: Mapping[tuple[str, str, str], Mapping[str, Any]],
    manifest: Mapping[str, Any],
    site: str,
    family: str,
    shards: Sequence[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features: list[np.ndarray] = []
    labels: list[str] = []
    halves: list[str] = []
    for half in ("construction", "geometry_validation"):
        for shard in shards:
            row = chunks[(site, shard, half)]
            path = (index_path.parent / str(row["path"])).resolve()
            with np.load(path, allow_pickle=False) as archive:
                values = np.asarray(archive["activations"], dtype=np.float64)
            prompt_rows = prompt_rows_for_chunk(
                manifest, context_shard=shard, half=half
            )
            selected = [
                index
                for index, prompt in enumerate(prompt_rows)
                if prompt["behavior_family"] == family
            ]
            features.append(values[np.asarray(selected, dtype=np.int64)])
            labels.extend(str(prompt_rows[index]["subcondition_id"]) for index in selected)
            halves.extend([half] * len(selected))
    return np.vstack(features), np.asarray(labels), np.asarray(halves)


def _receipt_summary(receipt: Mapping[str, Any]) -> dict[str, Any]:
    ranks = receipt["rank_receipts"]
    return {
        "supported_rank": int(receipt["supported_rank"]),
        "rank_metrics": [
            {
                "rank": int(row["rank"]),
                "point_worst_direction_retention": float(
                    row["lineage"]["worst_direction_retention"]
                ),
                "point_mean_chordal_lineage": float(
                    row["lineage"]["mean_chordal_lineage"]
                ),
                "retention_lower_95": float(row["retention_lower_95"]),
                "permutation_null_retention_upper_95": float(
                    row["permutation_null_retention_upper_95"]
                ),
                "null_margin": float(row["null_margin"]),
                "passed": bool(row["passed"]),
                "basis_by_half_sha256": list(row["basis_by_half_sha256"]),
            }
            for row in ranks
        ],
    }


def run_support_recovery(
    *,
    protocol_path: str | Path,
    repository_root: str | Path,
    output_dir: str | Path,
    seed: int = 2026071606,
) -> dict[str, Any]:
    protocol_path = Path(protocol_path).resolve()
    protocol = load_protocol(protocol_path)
    parent_entry = protocol["parent_analysis_registration"]
    parent_path = (Path(repository_root) / str(parent_entry["path"])).resolve()
    if sha256_file(parent_path) != str(parent_entry["sha256"]):
        raise ValueError("parent analysis registration hash mismatch")
    parent, _, manifest, state_paths = validate_registered_inputs(
        registration_path=parent_path,
        repository_root=repository_root,
    )
    if tuple(protocol["states"]) != tuple(parent["state_capture_indices"]):
        raise ValueError("support-recovery state universe differs")

    chunk_maps = {state: _chunk_map(state_paths[state]) for state in protocol["states"]}
    windows: list[tuple[int, int, tuple[str, ...], int]] = []
    for size in (2, 4):
        for start in range(8):
            windows.append(
                (
                    size,
                    start,
                    cyclic_window(start, size),
                    int(protocol["support_curve"]["replicates_for_pool_sizes_2_and_4"]),
                )
            )
    windows.append(
        (
            8,
            0,
            cyclic_window(0, 8),
            int(protocol["support_curve"]["replicates_for_pool_size_8"]),
        )
    )

    rows: list[dict[str, Any]] = []
    full_support: dict[tuple[str, str, str], int] = {}
    for state in protocol["states"]:
        for site in protocol["candidate_sites"]:
            for family in protocol["families"]:
                for size, start, shards, replicates in windows:
                    features, labels, halves = _window_features(
                        index_path=state_paths[state],
                        chunks=chunk_maps[state],
                        manifest=manifest,
                        site=site,
                        family=family,
                        shards=shards,
                    )
                    filtration = discover_between_class_rank_filtration(
                        features=features,
                        family_labels=labels,
                        construction_halves=halves,
                        maximum_rank=max(map(int, protocol["ranks"])),
                        replicates=replicates,
                        seed=_seed(seed, state, site, family, str(size), str(start)),
                        minimum_strict_margin=float(
                            protocol["primary_pool"]["minimum_strict_null_margin"]
                        ),
                    )
                    summary = _receipt_summary(filtration.receipt())
                    row = {
                        "state_id": state,
                        "site_id": site,
                        "behavior_family": family,
                        "pool_size": size,
                        "cyclic_start": start,
                        "context_shards": list(shards),
                        "prompts_per_subcondition_per_half": 2 * size,
                        "replicates": replicates,
                        **summary,
                    }
                    rows.append(row)
                    if size == 8:
                        full_support[(state, site, family)] = int(
                            summary["supported_rank"]
                        )

    pair_decisions = []
    for source, target in parent["state_pairs"]:
        common = [
            (site, family, min(full_support[(source, site, family)], full_support[(target, site, family)]))
            for site in protocol["candidate_sites"]
            for family in protocol["families"]
            if full_support[(source, site, family)] > 0
            and full_support[(target, site, family)] > 0
        ]
        distinct_sites = sorted({item[0] for item in common})
        distinct_families = sorted({item[1] for item in common})
        passed = len(distinct_sites) >= 3 and len(distinct_families) >= 2
        pair_decisions.append(
            {
                "state_pair": [source, target],
                "common_passing_cells": [
                    {"site_id": site, "behavior_family": family, "common_rank": rank}
                    for site, family, rank in common
                ],
                "distinct_site_count": len(distinct_sites),
                "distinct_family_count": len(distinct_families),
                "advance_to_denser_local_capture": passed,
            }
        )
    advance = any(row["advance_to_denser_local_capture"] for row in pair_decisions)
    result = {
        "schema_version": "qwen08_between_class_support_recovery_result_v0_1",
        "protocol_sha256": sha256_file(protocol_path),
        "parent_analysis_registration_sha256": sha256_file(parent_path),
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
        "rows": rows,
        "pair_decisions": pair_decisions,
        "branch_decision": (
            "advance_to_denser_local_capture"
            if advance
            else "stop_between_class_local_capture"
        ),
        "claim_boundary": protocol["claim_boundary"],
    }
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    write_once_or_equal(output / "support_recovery_result.json", canonical_json_bytes(result))
    return result
