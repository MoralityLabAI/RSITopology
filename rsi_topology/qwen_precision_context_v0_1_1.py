"""Exact-equivalent, resumable compute path for the v0.1 precision study.

This module changes no scientific decision.  It evaluates the rank-one SVD
through its sample-space Gram matrix, preserves the registered RNG call order,
and stores immutable hash-chained outer-bootstrap blocks.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

from . import qwen_precision_context as reference
from .godel_capture import canonical_json_bytes, sha256_file, write_once_or_equal


AMENDMENT_ID = "qwen08_l19_precision_context_compute_v0_1_1"
CHECKPOINT_SCHEMA = "qwen08_l19_precision_context_checkpoint_v0_1_1"
DEFAULT_BLOCK_SIZE = 16
DEFAULT_GAP_TOLERANCE = 1e-12


def load_amendment(path: str | Path) -> dict[str, Any]:
    amendment_path = Path(path).resolve()
    value = json.loads(amendment_path.read_text(encoding="utf-8-sig"))
    if value.get("protocol_id") != AMENDMENT_ID:
        raise ValueError("unexpected compute amendment")
    if value.get("status") != "registered_not_run":
        raise ValueError("compute amendment is not prereveal")
    parent = value.get("amends", {})
    if parent.get("protocol_id") != reference.PROTOCOL_ID:
        raise ValueError("compute amendment binds the wrong scientific protocol")
    if int(value["checkpoint_contract"]["outer_replicates_per_block"]) != DEFAULT_BLOCK_SIZE:
        raise ValueError("checkpoint block size differs from implementation")
    return value


def validate_amendment(
    amendment_path: str | Path, *, scientific_protocol_path: str | Path
) -> dict[str, Any]:
    value = load_amendment(amendment_path)
    if value["amends"]["protocol_sha256"] != sha256_file(Path(scientific_protocol_path)):
        raise ValueError("amendment scientific-protocol hash differs")
    return value


def _class_means(features: np.ndarray, labels: np.ndarray) -> np.ndarray:
    labels = np.asarray(labels, dtype=object)
    classes, inverse = np.unique(labels, return_inverse=True)
    if len(classes) < 2:
        raise ValueError("between-class basis requires at least two classes")
    indicator = np.zeros((len(labels), len(classes)), dtype=np.float64)
    indicator[np.arange(len(labels)), inverse] = 1.0
    counts = indicator.sum(axis=0)
    if np.any(counts <= 0):
        raise ValueError("empty class in between-class basis")
    return (np.asarray(features, dtype=np.float64).T @ indicator / counts).T


def _grouped_class_means(features: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Fast means for the registered bootstrap's sorted balanced strata."""

    labels = np.asarray(labels, dtype=object)
    classes = sorted(map(str, np.unique(labels)))
    groups = []
    cursor = 0
    for label in classes:
        count = int(np.sum(labels == label))
        block = labels[cursor : cursor + count]
        if count <= 0 or not np.all(block == label):
            return _class_means(features, labels)
        groups.append(np.asarray(features[cursor : cursor + count], dtype=np.float64).mean(axis=0))
        cursor += count
    if cursor != len(labels):
        return _class_means(features, labels)
    return np.stack(groups)


def _basis_from_means(
    means: np.ndarray,
    *,
    fallback_features: np.ndarray,
    fallback_labels: np.ndarray,
    relative_gap_tolerance: float = DEFAULT_GAP_TOLERANCE,
) -> np.ndarray:
    centered = np.asarray(means, dtype=np.float64) - np.mean(means, axis=0, keepdims=True)
    scaled = centered / np.sqrt(float(len(centered)))
    gram = scaled @ scaled.T
    eigenvalues, eigenvectors = np.linalg.eigh(gram)
    top = float(eigenvalues[-1])
    runner_up = float(eigenvalues[-2]) if len(eigenvalues) > 1 else 0.0
    relative_gap = (top - runner_up) / max(abs(top), np.finfo(np.float64).tiny)
    if not np.isfinite(top) or top <= 0.0 or relative_gap <= relative_gap_tolerance:
        basis, _ = reference._between_class_scatter_basis(
            np.asarray(fallback_features), np.asarray(fallback_labels), 1
        )
        return np.asarray(basis[:, 0], dtype=np.float64)
    vector = scaled.T @ eigenvectors[:, -1]
    vector /= np.sqrt(top)
    vector /= np.linalg.norm(vector)
    return vector


def _basis_for_half(
    features: np.ndarray,
    labels: np.ndarray,
    *,
    grouped: bool,
    relative_gap_tolerance: float = DEFAULT_GAP_TOLERANCE,
) -> np.ndarray:
    means = (
        _grouped_class_means(features, labels)
        if grouped
        else _class_means(features, labels)
    )
    return _basis_from_means(
        means,
        fallback_features=features,
        fallback_labels=labels,
        relative_gap_tolerance=relative_gap_tolerance,
    )


def rank_one_retention_fast(
    features: np.ndarray,
    labels: np.ndarray,
    halves: np.ndarray,
    *,
    grouped: bool = False,
    relative_gap_tolerance: float = DEFAULT_GAP_TOLERANCE,
) -> float:
    bases = []
    for half in reference.HALVES:
        mask = np.asarray(halves) == half
        bases.append(
            _basis_for_half(
                np.asarray(features)[mask],
                np.asarray(labels, dtype=object)[mask],
                grouped=grouped,
                relative_gap_tolerance=relative_gap_tolerance,
            )
        )
    return float(abs(np.dot(bases[0], bases[1])) ** 2)


def complete_margin_draw_fast(
    *,
    feature_by_precision: Mapping[str, np.ndarray],
    labels: np.ndarray,
    halves: np.ndarray,
    inner_replicates: int,
    rng: np.random.Generator,
    strict_margin: float,
) -> dict[str, float]:
    # Generate draws in the exact v0.1 call order, then evaluate their linear
    # algebra as one CPU batch.  No numerical operation below consumes RNG.
    indices_batch = []
    permuted_batch = []
    for _ in range(inner_replicates):
        indices = reference._stratified_bootstrap_indices(labels, halves, rng)
        selected_labels = np.asarray(labels, dtype=object)[indices]
        selected_halves = np.asarray(halves)[indices]
        permuted = reference._matched_permuted_labels(selected_labels, selected_halves, rng)
        indices_batch.append(indices)
        permuted_batch.append(permuted)
    index_array = np.stack(indices_batch)
    selected_labels = np.asarray(labels, dtype=object)[index_array[0]]
    selected_halves = np.asarray(halves)[index_array[0]]
    classes = sorted(map(str, np.unique(selected_labels)))
    half_names = sorted(map(str, np.unique(selected_halves)))
    if tuple(half_names) != reference.HALVES:
        raise ValueError("batched margin requires the registered two halves")
    per_class = None
    for half in half_names:
        counts = [int(np.sum((selected_halves == half) & (selected_labels == label))) for label in classes]
        if len(set(counts)) != 1 or counts[0] <= 0:
            raise ValueError("batched margin requires balanced registered strata")
        if per_class is None:
            per_class = counts[0]
        elif per_class != counts[0]:
            raise ValueError("registered halves have unequal stratum sizes")
    assert per_class is not None
    code = {label: index for index, label in enumerate(classes)}
    permuted_codes = np.asarray(
        [[code[str(label)] for label in row] for row in permuted_batch], dtype=np.int64
    ).reshape(inner_replicates, 2, len(classes) * per_class)
    identity = np.eye(len(classes), dtype=np.float64)
    indicators = identity[permuted_codes]
    real: dict[str, np.ndarray] = {}
    null: dict[str, np.ndarray] = {}
    for precision in reference.PRECISIONS:
        selected = np.asarray(feature_by_precision[precision])[index_array]
        grouped_values = selected.reshape(
            inner_replicates, 2, len(classes), per_class, selected.shape[-1]
        )
        real_means = grouped_values.mean(axis=3, dtype=np.float64)
        flat_values = grouped_values.reshape(
            inner_replicates, 2, len(classes) * per_class, selected.shape[-1]
        )
        null_means = (
            np.einsum("bhnd,bhnc->bhcd", flat_values, indicators, optimize=True)
            / float(per_class)
        )
        real[precision] = _batch_retention_from_means(real_means)
        null[precision] = _batch_retention_from_means(null_means)
    return {
        precision: float(
            np.quantile(real[precision], 0.05, method="linear")
            - np.quantile(null[precision], 0.95, method="linear")
            - strict_margin
        )
        for precision in reference.PRECISIONS
    }


def _batch_retention_from_means(
    means: np.ndarray,
    *,
    relative_gap_tolerance: float = DEFAULT_GAP_TOLERANCE,
) -> np.ndarray:
    """Evaluate rank-one lineage for B x 2 x classes x dimensions means."""

    centered = np.asarray(means, dtype=np.float64) - np.mean(
        means, axis=2, keepdims=True
    )
    scaled = centered / np.sqrt(float(means.shape[2]))
    gram = np.einsum("bhcd,bhed->bhce", scaled, scaled, optimize=True)
    eigenvalues, eigenvectors = np.linalg.eigh(gram)
    top = eigenvalues[:, :, -1]
    runner_up = eigenvalues[:, :, -2]
    relative_gap = (top - runner_up) / np.maximum(
        np.abs(top), np.finfo(np.float64).tiny
    )
    bad = (~np.isfinite(top)) | (top <= 0.0) | (relative_gap <= relative_gap_tolerance)
    safe_top = np.where(bad, 1.0, top)
    vectors = np.einsum(
        "bhcd,bhc->bhd", scaled, eigenvectors[:, :, :, -1], optimize=True
    ) / np.sqrt(safe_top)[..., None]
    for draw, half in np.argwhere(bad):
        # This is exactly the reference thin-SVD construction, applied only at
        # the amendment's registered degeneracy boundary.
        _, _, right_t = np.linalg.svd(scaled[draw, half], full_matrices=False)
        vectors[draw, half] = right_t[0]
    vectors /= np.linalg.norm(vectors, axis=-1, keepdims=True)
    return np.abs(np.einsum("bd,bd->b", vectors[:, 0], vectors[:, 1])) ** 2


def _cell_slug(key: tuple[str, str, str, str]) -> str:
    readable = "__".join(item.replace(".", "-") for item in key)
    digest = hashlib.sha256("\0".join(key).encode("utf-8")).hexdigest()[:12]
    return f"{readable}__{digest}"


def _checkpoint_hash(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _load_checkpoint_chain(
    directory: Path,
    *,
    key: tuple[str, str, str, str],
    binding_sha256: str,
) -> tuple[list[float], dict[str, Any] | None, str | None]:
    values: list[float] = []
    rng_state = None
    previous_hash = None
    expected_start = 0
    for path in sorted(directory.glob("block_*.json")):
        item = json.loads(path.read_text(encoding="utf-8-sig"))
        if item.get("schema_version") != CHECKPOINT_SCHEMA:
            raise ValueError(f"checkpoint schema differs: {path}")
        if tuple(map(str, item.get("cell", ()))) != key:
            raise ValueError(f"checkpoint cell differs: {path}")
        if item.get("binding_sha256") != binding_sha256:
            raise ValueError(f"checkpoint binding differs: {path}")
        if item.get("previous_checkpoint_sha256") != previous_hash:
            raise ValueError(f"checkpoint chain is broken: {path}")
        if int(item.get("outer_start", -1)) != expected_start:
            raise ValueError(f"checkpoint range is not contiguous: {path}")
        block_values = list(map(float, item.get("delta_values", ())))
        if int(item.get("outer_stop", -1)) != expected_start + len(block_values):
            raise ValueError(f"checkpoint range length differs: {path}")
        values.extend(block_values)
        expected_start += len(block_values)
        rng_state = item.get("post_block_rng_state")
        previous_hash = _checkpoint_hash(item)
    return values, rng_state, previous_hash


def paired_complete_margin_summary_resumable(
    *,
    raw_cells: Mapping[
        tuple[str, str, str, str],
        Mapping[str, tuple[np.ndarray, np.ndarray, np.ndarray]],
    ],
    gate_filtrations: Mapping[tuple[str, str, str, str, str], Any],
    protocol: Mapping[str, Any],
    seed: int,
    checkpoint_dir: str | Path,
    binding_sha256: str,
    block_size: int = DEFAULT_BLOCK_SIZE,
    progress: Callable[[Mapping[str, Any]], None] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    config = protocol["primary_comparison"]
    outer_replicates = int(config["paired_bootstrap_outer_replicates"])
    inner_replicates = int(config["paired_bootstrap_inner_replicates"])
    strict_margin = float(protocol["primary_object"]["minimum_strict_null_margin"])
    checkpoint_root = Path(checkpoint_dir).resolve()
    checkpoint_root.mkdir(parents=True, exist_ok=True)
    deltas: dict[tuple[str, str, str, str], np.ndarray] = {}
    for key in sorted(raw_cells):
        payload = raw_cells[key]
        four_features, labels, halves = payload["4bit"]
        full_features, full_labels, full_halves = payload["float16"]
        if not np.array_equal(labels, full_labels) or not np.array_equal(halves, full_halves):
            raise ValueError(f"prompt-label alignment differs across precision: {key}")
        cell_dir = checkpoint_root / _cell_slug(key)
        cell_dir.mkdir(parents=True, exist_ok=True)
        completed, rng_state, previous_hash = _load_checkpoint_chain(
            cell_dir, key=key, binding_sha256=binding_sha256
        )
        if len(completed) > outer_replicates:
            raise ValueError(f"checkpoint exceeds registered replicate count: {key}")
        rng = np.random.default_rng(reference._stable_seed(seed, *key, "nested-paired"))
        if rng_state is not None:
            rng.bit_generator.state = rng_state
        while len(completed) < outer_replicates:
            start = len(completed)
            stop = min(start + block_size, outer_replicates)
            block_values = []
            for _ in range(start, stop):
                outer = reference._stratified_bootstrap_indices(labels, halves, rng)
                margins = complete_margin_draw_fast(
                    feature_by_precision={
                        "4bit": four_features[outer],
                        "float16": full_features[outer],
                    },
                    labels=np.asarray(labels, dtype=object)[outer],
                    halves=np.asarray(halves)[outer],
                    inner_replicates=inner_replicates,
                    rng=rng,
                    strict_margin=strict_margin,
                )
                block_values.append(margins["float16"] - margins["4bit"])
            item = {
                "schema_version": CHECKPOINT_SCHEMA,
                "binding_sha256": binding_sha256,
                "cell": list(key),
                "outer_start": start,
                "outer_stop": stop,
                "delta_values": block_values,
                "post_block_rng_state": rng.bit_generator.state,
                "previous_checkpoint_sha256": previous_hash,
            }
            path = cell_dir / f"block_{start:04d}_{stop:04d}.json"
            write_once_or_equal(path, canonical_json_bytes(item))
            previous_hash = _checkpoint_hash(item)
            completed.extend(block_values)
            if progress is not None:
                progress(
                    {
                        "event": "checkpoint",
                        "cell": list(key),
                        "outer_completed": stop,
                        "outer_total": outer_replicates,
                        "checkpoint_path": str(path),
                        "checkpoint_sha256": previous_hash,
                    }
                )
        deltas[key] = np.asarray(completed, dtype=np.float64)
    return _summarize_deltas(
        deltas=deltas,
        gate_filtrations=gate_filtrations,
        outer_replicates=outer_replicates,
        inner_replicates=inner_replicates,
        sentinel=protocol["sentinel"],
    )


def _summarize_deltas(
    *,
    deltas: Mapping[tuple[str, str, str, str], np.ndarray],
    gate_filtrations: Mapping[tuple[str, str, str, str, str], Any],
    outer_replicates: int,
    inner_replicates: int,
    sentinel: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = []
    for key in sorted(deltas):
        state, site, shard, family = key
        values = deltas[key]
        lower = float(np.quantile(values, 0.05, method="linear"))
        upper = float(np.quantile(values, 0.95, method="linear"))
        four_pass = bool(gate_filtrations[("4bit", *key)].objects[0].passed)
        full_pass = bool(gate_filtrations[("float16", *key)].objects[0].passed)
        if full_pass and four_pass and lower <= 0.0 <= upper:
            category = "precision_robust"
        elif full_pass and not four_pass and lower > 0.0:
            category = "degraded_under_precision"
        elif four_pass and not full_pass and upper < 0.0:
            category = "precision_specific"
        else:
            category = "inconclusive"
        rows.append(
            {
                "state": state,
                "site": site,
                "context_shard": shard,
                "behavior_family": family,
                "float16_minus_fourbit_complete_margin_point": float(np.median(values)),
                "float16_minus_fourbit_complete_margin_lower_95": lower,
                "float16_minus_fourbit_complete_margin_upper_95": upper,
                "fourbit_gate_pass": four_pass,
                "float16_gate_pass": full_pass,
                "precision_classification": category,
                "paired_outer_bootstrap_replicates": outer_replicates,
                "paired_inner_replicates": inner_replicates,
            }
        )
    sentinel_key = (
        str(sentinel["state"]),
        str(sentinel["site"]),
        str(sentinel["context_shard"]),
        str(sentinel["family"]),
    )
    if sentinel_key not in deltas:
        raise ValueError("sentinel is absent from paired universe")
    comparator = [values for key, values in deltas.items() if key != sentinel_key]
    if not comparator:
        raise ValueError("interaction contrast has no non-sentinel cells")
    interaction = deltas[sentinel_key] - np.median(np.stack(comparator), axis=0)
    sentinel_row = next(
        row
        for row in rows
        if (row["state"], row["site"], row["context_shard"], row["behavior_family"])
        == sentinel_key
    )
    return rows, {
        "sentinel": {
            "state": sentinel_key[0],
            "site": sentinel_key[1],
            "context_shard": sentinel_key[2],
            "behavior_family": sentinel_key[3],
        },
        "contrast": "sentinel complete-margin delta minus per-draw median non-sentinel complete-margin delta",
        "point": float(np.median(interaction)),
        "lower_95": float(np.quantile(interaction, 0.05, method="linear")),
        "upper_95": float(np.quantile(interaction, 0.95, method="linear")),
        "passes_precision_specificity_requirement": bool(
            np.quantile(interaction, 0.05, method="linear") > 0.0
        ),
        "sentinel_precision_classification": sentinel_row["precision_classification"],
        "paired_outer_bootstrap_replicates": outer_replicates,
        "paired_inner_replicates": inner_replicates,
    }


def analyze_precision_context_v0_1_1(
    *,
    amendment_path: str | Path,
    protocol_path: str | Path,
    manifest_path: str | Path,
    fourbit_indices: Mapping[str, str | Path],
    float16_indices: Mapping[str, str | Path],
    output_dir: str | Path,
    progress: Callable[[Mapping[str, Any]], None] | None = None,
) -> dict[str, Any]:
    validate_amendment(amendment_path, scientific_protocol_path=protocol_path)
    binding = hashlib.sha256(
        canonical_json_bytes(
            {
                "amendment_sha256": sha256_file(Path(amendment_path)),
                "protocol_sha256": sha256_file(Path(protocol_path)),
                "manifest_sha256": sha256_file(Path(manifest_path)),
                "fourbit_indices": {
                    key: sha256_file(Path(path)) for key, path in sorted(fourbit_indices.items())
                },
                "float16_indices": {
                    key: sha256_file(Path(path)) for key, path in sorted(float16_indices.items())
                },
            }
        )
    ).hexdigest()
    output = Path(output_dir).resolve()
    original = reference._paired_complete_margin_summary

    def replacement(**kwargs: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        return paired_complete_margin_summary_resumable(
            **kwargs,
            checkpoint_dir=output / "checkpoints",
            binding_sha256=binding,
            progress=progress,
        )

    reference._paired_complete_margin_summary = replacement
    try:
        result = reference.analyze_precision_context(
            protocol_path=protocol_path,
            manifest_path=manifest_path,
            fourbit_indices=fourbit_indices,
            float16_indices=float16_indices,
            output_dir=output,
        )
    finally:
        reference._paired_complete_margin_summary = original
    # Keep the scientific result byte-compatible with v0.1.  The additive
    # compute amendment and checkpoint binding live in the run receipt.
    return result
