"""Fresh paired precision/context identity experiment for Qwen0.8B.

This module deliberately reuses the Stage-B measurement primitive without
changing its rank-support gate.  It adds a *paired* bootstrap only as evidence
about a four-bit-versus-float16 difference at a preregistered L19 sentinel.
No behavioral outcomes, generations, gradients, or weight edits are accepted.
"""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .discovery import (
    _between_class_scatter_basis,
    discover_between_class_rank_filtration,
    subspace_lineage,
)
from .godel_analysis import _node_features, analyze_godel_capture
from .godel_capture import (
    CaptureChunk,
    CaptureStore,
    canonical_json_bytes,
    canonical_json_sha256,
    generate_prompt_manifest,
    prompt_rows_for_chunk,
    sha256_file,
    validate_prompt_manifest,
    write_once_or_equal,
)
from .qwen_state_capture import STATE_CAPTURE_SCHEMA


PROTOCOL_ID = "qwen08_l19_precision_context_v0_1"
MANIFEST_SCHEMA = "qwen08_l19_precision_context_prompt_manifest_v0_1"
PAIR_INDEX_SCHEMA = "qwen08_l19_precision_context_pair_index_v0_1"
RESULT_SCHEMA = "qwen08_l19_precision_context_result_v0_1"
PRECISIONS = ("4bit", "float16")
STATES = ("base", "naive_qlora")
HALVES = ("construction", "geometry_validation")


def load_protocol(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("unexpected precision/context protocol")
    if value.get("status") != "registered_not_run":
        raise ValueError("precision/context protocol is not prereveal")
    if value.get("outcomes_consumed") is not False:
        raise ValueError("precision/context protocol is not outcome-free")
    if value.get("new_invariant_levels") is not False:
        raise ValueError("precision/context protocol introduces an invariant level")
    if tuple(map(str, value.get("sites", ()))) != (
        "model.layers.19",
        "model.layers.23",
    ):
        raise ValueError("precision/context site universe differs")
    if tuple(map(str, value.get("model_lock", {}).get("states", ()))) != STATES:
        raise ValueError("precision/context state universe differs")
    return value


def _prompt_bytes(value: Mapping[str, Any]) -> set[bytes]:
    rows = value.get("rows")
    if not isinstance(rows, list):
        raise ValueError("prompt artifact has no row list")
    result = {str(row.get("prompt", "")).encode("utf-8") for row in rows}
    if b"" in result or len(result) != len(rows):
        raise ValueError("prompt bytes are empty or non-unique")
    return result


def generate_manifest(*, protocol_path: str | Path) -> dict[str, Any]:
    """Generate the exact Stage-B grammar with a fresh, frozen seed."""

    path = Path(protocol_path).resolve()
    protocol = load_protocol(path)
    design = protocol["prompt_design"]
    value = generate_prompt_manifest(
        protocol_sha256=sha256_file(path),
        seed=int(design["seed"]),
        families=tuple(map(str, design["families"])),
        subconditions_per_family=int(design["subconditions_per_family"]),
        context_shards=int(design["context_shards"]),
        prompts_per_half=int(design["prompts_per_subcondition_per_half_per_shard"]),
    )
    # Preserve the Stage-B nonce construction and placement exactly.
    seed = int(design["seed"])
    for row in value["rows"]:
        nonce = hashlib.sha256(
            f"{seed}\0{design['nonce_namespace']}\0{row['prompt_id']}".encode("utf-8")
        ).hexdigest()[:20]
        row["prompt"] = f"{row['prompt']} Opaque Stage-B nonce: {nonce}."
        shard = str(row["context_shard"])
        row["context_neighborhood"] = (
            "old_shard_02" if shard in ("shard-00", "shard-01") else "old_shard_03"
        )
    value["schema_version"] = MANIFEST_SCHEMA
    value["protocol_id"] = PROTOCOL_ID
    value["precision_pair"] = {
        "conditions": list(PRECISIONS),
        "same_prompt_bytes_required": True,
        "same_order_required": True,
        "same_tokenization_contract_required": True,
        "metadata_only_difference": "runtime_precision",
    }
    validate_manifest(value, protocol_path=path)
    return value


def validate_manifest(value: Mapping[str, Any], *, protocol_path: str | Path) -> None:
    """Validate the fresh factorial prompt universe and precision pairing."""

    protocol = load_protocol(protocol_path)
    design = protocol["prompt_design"]
    if value.get("schema_version") != MANIFEST_SCHEMA:
        raise ValueError("invalid precision/context manifest schema")
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("precision/context manifest protocol mismatch")
    # The shared core validator continues to audit answer keys, but geometry
    # code never reads them after this validation step.
    core = dict(value)
    core["schema_version"] = "godel_globes_prompt_manifest_v0_1"
    core["protocol_id"] = "godel_globes_falsification_v0_1"
    validate_prompt_manifest(core)
    expected = {
        "protocol_sha256": sha256_file(Path(protocol_path)),
        "seed": int(design["seed"]),
        "families": list(map(str, design["families"])),
        "subconditions_per_family": int(design["subconditions_per_family"]),
        "context_shards": int(design["context_shards"]),
        "prompts_per_subcondition_per_half_per_shard": int(
            design["prompts_per_subcondition_per_half_per_shard"]
        ),
        "prompt_count": int(design["prompts_per_state"]),
    }
    for key, target in expected.items():
        if value.get(key) != target:
            raise ValueError(f"precision/context manifest differs at {key}")
    expected_neighborhoods = design["context_neighborhoods"]
    observed_neighborhoods = {
        str(row["context_shard"]): str(row.get("context_neighborhood", ""))
        for row in value["rows"]
    }
    expected_by_shard = {
        shard: label
        for label, shards in expected_neighborhoods.items()
        for shard in shards
    }
    if observed_neighborhoods != expected_by_shard:
        raise ValueError("context-neighborhood mapping differs")
    pair = value.get("precision_pair")
    if not isinstance(pair, Mapping) or tuple(pair.get("conditions", ())) != PRECISIONS:
        raise ValueError("precision pair metadata is incomplete")
    _prompt_bytes(value)


def prompt_separation_receipt(
    manifest: Mapping[str, Any], *, compared_manifest_paths: Sequence[str | Path]
) -> dict[str, Any]:
    fresh = _prompt_bytes(manifest)
    comparisons = []
    for raw in compared_manifest_paths:
        path = Path(raw).resolve()
        prior = json.loads(path.read_text(encoding="utf-8-sig"))
        comparisons.append(
            {
                "path": str(path),
                "sha256": sha256_file(path),
                "prompt_count": len(_prompt_bytes(prior)),
                "byte_identical_overlap_count": len(fresh & _prompt_bytes(prior)),
            }
        )
    return {
        "schema_version": "qwen08_l19_precision_context_prompt_separation_v0_1",
        "fresh_prompt_count": len(fresh),
        "comparisons": comparisons,
        "passed": all(item["byte_identical_overlap_count"] == 0 for item in comparisons),
    }


def precision_manifest_pair_receipt(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Seal the identical prompt payload consumed by both precision arms."""

    payload = [
        {
            "prompt_id": str(row["prompt_id"]),
            "prompt": str(row["prompt"]),
            "behavior_family": str(row["behavior_family"]),
            "context_shard": str(row["context_shard"]),
            "half": str(row["half"]),
        }
        for row in manifest["rows"]
    ]
    payload_hash = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    views = {
        precision: {
            "runtime_precision": precision,
            "prompt_payload_sha256": payload_hash,
            "prompt_count": len(payload),
            "tokenization_contract": "same tokenizer source, order, final non-padding token rule",
        }
        for precision in PRECISIONS
    }
    return {
        "schema_version": "qwen08_l19_precision_context_manifest_pair_v0_1",
        "common_prompt_payload_sha256": payload_hash,
        "precision_views": views,
        "identical_except_runtime_precision": all(
            view["prompt_payload_sha256"] == payload_hash for view in views.values()
        ),
    }


def _expected_capture_keys(
    *, state: str, sites: Sequence[str], context_shards: int
) -> set[tuple[str, str, str, str]]:
    return {
        (state, site, f"shard-{index:02d}", half)
        for site in sites
        for index in range(context_shards)
        for half in HALVES
    }


def validate_capture_index(
    *,
    index_path: str | Path,
    protocol_path: str | Path,
    manifest_path: str | Path,
    state: str,
    precision: str,
) -> tuple[dict[str, Any], dict[tuple[str, str, str, str], CaptureChunk]]:
    """Validate a capture arm against its exact fresh-prompt universe."""

    protocol_path = Path(protocol_path).resolve()
    manifest_path = Path(manifest_path).resolve()
    index_path = Path(index_path).resolve()
    protocol = load_protocol(protocol_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    validate_manifest(manifest, protocol_path=protocol_path)
    value = json.loads(index_path.read_text(encoding="utf-8-sig"))
    if value.get("schema_version") != STATE_CAPTURE_SCHEMA:
        raise ValueError("invalid precision/context capture-index schema")
    if value.get("state_id") != state or value.get("quantization") != precision:
        raise ValueError("capture state or precision differs")
    for field in ("outcomes_read", "outcomes_consumed", "generation", "gradients", "weight_mutation"):
        if value.get(field) is not False:
            raise ValueError(f"capture does not declare {field}=false")
    if value.get("protocol_sha256") != protocol["model_lock"]["causal_protocol_sha256"]:
        raise ValueError("capture causal-protocol binding differs")
    if value.get("geometry_manifest_sha256") != sha256_file(manifest_path):
        raise ValueError("capture manifest binding differs")
    scientific = value.get("scientific_protocol")
    if not isinstance(scientific, Mapping) or scientific.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("precision/context scientific binding is absent")
    if scientific.get("sha256") != sha256_file(protocol_path):
        raise ValueError("precision/context scientific protocol changed")
    expected = _expected_capture_keys(
        state=state,
        sites=tuple(map(str, protocol["sites"])),
        context_shards=int(manifest["context_shards"]),
    )
    observed: dict[tuple[str, str, str, str], CaptureChunk] = {}
    seen_ids: set[str] = set()
    for row in value.get("chunks", ()):  # type: ignore[union-attr]
        key = (
            str(row.get("state_id")),
            str(row.get("site_id")),
            str(row.get("context_shard")),
            str(row.get("half")),
        )
        chunk_id = str(row.get("chunk_id", ""))
        if key not in expected or key in observed or not chunk_id or chunk_id in seen_ids:
            raise ValueError("capture chunk universe is invalid")
        seen_ids.add(chunk_id)
        file_path = (index_path.parent / str(row.get("path", ""))).resolve()
        if not file_path.is_file() or sha256_file(file_path) != row.get("sha256"):
            raise ValueError(f"capture chunk missing or changed: {chunk_id}")
        expected_prompt_ids = tuple(
            str(item["prompt_id"])
            for item in prompt_rows_for_chunk(
                manifest, context_shard=key[2], half=key[3]
            )
        )
        if tuple(map(str, row.get("prompt_ids", ()))) != expected_prompt_ids:
            raise ValueError(f"capture prompt order differs: {chunk_id}")
        with np.load(file_path, allow_pickle=False) as archive:
            if set(archive.files) != {"activations"}:
                raise ValueError(f"capture archive keys differ: {chunk_id}")
            values = np.asarray(archive["activations"])
        if values.shape != (len(expected_prompt_ids), int(row.get("ambient_dimension", 0))):
            raise ValueError(f"capture shape differs: {chunk_id}")
        if not np.all(np.isfinite(values)):
            raise ValueError(f"capture contains nonfinite activations: {chunk_id}")
        observed[key] = CaptureChunk(
            chunk_id=chunk_id,
            runtime_precision=state,
            site_id=key[1],
            context_shard=key[2],
            half=key[3],
            path=file_path,
            sha256=str(row["sha256"]),
            prompt_ids=expected_prompt_ids,
            row_count=len(expected_prompt_ids),
            ambient_dimension=int(row["ambient_dimension"]),
            dtype=str(row["dtype"]),
        )
    if set(observed) != expected:
        raise ValueError("capture chunk universe is incomplete")
    return value, observed


def build_pair_store(
    *,
    protocol_path: str | Path,
    manifest_path: str | Path,
    precision: str,
    state_index_paths: Mapping[str, str | Path],
    output_dir: str | Path,
) -> CaptureStore:
    """Create a validated state-pair store for one runtime precision."""

    if precision not in PRECISIONS:
        raise ValueError("unknown precision")
    if set(state_index_paths) != set(STATES):
        raise ValueError("pair does not cover the exact state universe")
    chunks: dict[tuple[str, str, str, str], CaptureChunk] = {}
    sources: dict[str, dict[str, str]] = {}
    for state in STATES:
        index_path = Path(state_index_paths[state]).resolve()
        _, arm_chunks = validate_capture_index(
            index_path=index_path,
            protocol_path=protocol_path,
            manifest_path=manifest_path,
            state=state,
            precision=precision,
        )
        sources[state] = {"path": str(index_path), "sha256": sha256_file(index_path)}
        for key, chunk in arm_chunks.items():
            if key in chunks:
                raise ValueError("duplicate capture chunk in state pair")
            chunks[key] = chunk
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    index = {
        "schema_version": PAIR_INDEX_SCHEMA,
        "precision": precision,
        "states": list(STATES),
        "sites": ["model.layers.19", "model.layers.23"],
        "source_state_indices": sources,
        "protocol_sha256": sha256_file(Path(protocol_path)),
        "prompt_manifest_sha256": sha256_file(Path(manifest_path)),
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
    }
    index_path = output / "pair_capture_index.json"
    write_once_or_equal(index_path, canonical_json_bytes(index))
    return CaptureStore(index_path=index_path, index=index, chunks=chunks)


def _analysis_view(protocol: Mapping[str, Any], *, precision: str) -> dict[str, Any]:
    """Adapt the existing Stage-B geometry implementation without relaxing it."""

    primary = protocol["primary_object"]
    return {
        "protocol_id": f"{PROTOCOL_ID}:{precision}",
        "runtime_precisions": list(STATES),
        "candidate_sites": list(protocol["sites"]),
        "primary_object": {
            "kind": primary["kind"],
            "ranks": [1],
            "bootstrap_replicates": int(primary["bootstrap_replicates"]),
            "minimum_strict_null_margin": float(primary["minimum_strict_null_margin"]),
        },
        "instrument_calibration": {
            "required_margin": float(primary["minimum_strict_null_margin"]),
        },
        "graph": {"lineage_floor": 0.9},
        "holonomy": {
            "prompt_resampling_replicates": int(primary["bootstrap_replicates"]),
            "budget": {"maximum_canonical_angle_degrees": 5.0, "maximum_identity_loss": 0.05},
        },
        "corotation": {"status": "not_identifiable_single_family"},
        "gauge_preflight": {"reframings": 32, "tolerance": 1e-8},
        "sectioning": {
            "budgets": [0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5],
            "shard_prefixes": [2, 4],
            "navigation_ceiling_per_family": 40,
        },
        "aggregate_identity_gate": {
            "minimum_physical_sites": 1,
            "minimum_behavior_families": 1,
        },
        "consumer_rules": {
            "signed_intervention": "holonomy_clean",
            "energy_reward": "lineage_certified",
            "all_other_uses": "engineering_evidence",
        },
        "claim_boundary": protocol["claim_boundary"],
    }


def _stable_seed(base_seed: int, *values: str) -> int:
    payload = "\0".join(map(str, values)).encode("utf-8")
    return (base_seed + int.from_bytes(hashlib.sha256(payload).digest()[:4], "big")) % (
        2**32
    )


def _rank_one_filtration(
    *,
    store: CaptureStore,
    manifest: Mapping[str, Any],
    precision: str,
    state: str,
    site: str,
    shard: str,
    replicates: int,
    seed: int,
    required_margin: float,
) -> Any:
    """Run the exact Stage-B rank-one estimator for one physical cell."""

    features, labels, halves = _node_features(
        store,
        manifest,
        runtime=state,
        site=site,
        family="graph_reachability",
        shard=shard,
    )
    # `precision` intentionally does not enter the seed: aligned conditions
    # therefore use identical within-class bootstrap draws.
    return discover_between_class_rank_filtration(
        features=features,
        family_labels=labels,
        construction_halves=halves,
        maximum_rank=1,
        replicates=replicates,
        seed=seed,
        minimum_strict_margin=required_margin,
    )


def _support_record(
    *,
    precision: str,
    state: str,
    site: str,
    shard: str,
    filtration: Any,
    role: str,
) -> dict[str, Any]:
    item = filtration.objects[0]
    boundary = float(
        item.permutation_null_retention_upper_95 + item.minimum_strict_margin
    )
    observed = float(item.retention_lower_95)
    observed_raw = float(item.lineage["worst_direction_retention"])
    # The empirical permutation p-value is descriptive only.  The frozen
    # decision is the conservative lower/upper-quantile margin below.
    p_value = float(
        (1 + np.sum(item.permutation_null_retentions >= observed_raw))
        / (1 + len(item.permutation_null_retentions))
    )
    return {
        "precision": precision,
        "state": state,
        "site": site,
        "context_shard": shard,
        "behavior_family": "graph_reachability",
        "role": role,
        "rank": 1,
        "support_statistic": "minimum_edge_worst_direction_retention",
        "retention_observed": observed_raw,
        "retention_lower_95": observed,
        "permutation_null_retention_upper_95": float(
            item.permutation_null_retention_upper_95
        ),
        "minimum_strict_null_margin": float(item.minimum_strict_margin),
        "registered_null_boundary": boundary,
        "signed_support_margin": float(observed - boundary),
        "matched_random_label_p_value_descriptive": p_value,
        "passed_matched_random_label_gate": bool(item.passed),
        "bootstrap_replicates": int(len(item.bootstrap_retentions)),
        "permutation_replicates": int(len(item.permutation_null_retentions)),
        "basis_hashes": [
            hashlib.sha256(np.asarray(basis, dtype="<f8").tobytes()).hexdigest()
            for basis in item.basis_by_half
        ],
    }


def _stratified_bootstrap_indices(
    labels: np.ndarray, halves: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    """Resample prompt IDs jointly inside frozen half × subcondition strata."""

    selected: list[int] = []
    for half in sorted(map(str, np.unique(halves))):
        half_members = np.flatnonzero(halves == half)
        for label in sorted(map(str, np.unique(labels[half_members]))):
            members = half_members[labels[half_members] == label]
            selected.extend(rng.choice(members, size=len(members), replace=True).tolist())
    return np.asarray(selected, dtype=np.int64)


def _matched_permuted_labels(
    labels: np.ndarray, halves: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    """Permute labels inside each half once, then reuse them across precision."""

    result = np.asarray(labels, dtype=object).copy()
    for half in sorted(map(str, np.unique(halves))):
        members = np.flatnonzero(halves == half)
        result[members] = result[members][rng.permutation(len(members))]
    return result


def _rank_one_retention(features: np.ndarray, labels: np.ndarray, halves: np.ndarray) -> float:
    bases = []
    for half in ("construction", "geometry_validation"):
        mask = halves == half
        basis, _ = _between_class_scatter_basis(features[mask], labels[mask], 1)
        bases.append(basis)
    return float(subspace_lineage(bases[0], bases[1])["worst_direction_retention"])


def _complete_margin_draw(
    *,
    feature_by_precision: Mapping[str, np.ndarray],
    labels: np.ndarray,
    halves: np.ndarray,
    inner_replicates: int,
    rng: np.random.Generator,
    strict_margin: float,
) -> dict[str, float]:
    """Recompute the whole gate functional for one outer paired resample."""

    real: dict[str, list[float]] = {precision: [] for precision in PRECISIONS}
    null: dict[str, list[float]] = {precision: [] for precision in PRECISIONS}
    for _ in range(inner_replicates):
        indices = _stratified_bootstrap_indices(labels, halves, rng)
        selected_labels = labels[indices]
        selected_halves = halves[indices]
        # Permute after the balanced draw so the null preserves the exact
        # selected class counts in each half.
        permuted = _matched_permuted_labels(selected_labels, selected_halves, rng)
        for precision in PRECISIONS:
            values = feature_by_precision[precision]
            real[precision].append(
                _rank_one_retention(values[indices], selected_labels, selected_halves)
            )
            null[precision].append(
                _rank_one_retention(values[indices], permuted, selected_halves)
            )
    return {
        precision: float(
            np.quantile(real[precision], 0.05, method="linear")
            - np.quantile(null[precision], 0.95, method="linear")
            - strict_margin
        )
        for precision in PRECISIONS
    }


def _paired_complete_margin_summary(
    *,
    raw_cells: Mapping[tuple[str, str, str, str], Mapping[str, tuple[np.ndarray, np.ndarray, np.ndarray]]],
    gate_filtrations: Mapping[tuple[str, str, str, str, str], Any],
    protocol: Mapping[str, Any],
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Nested, prompt-ID-paired bootstrap of the complete gate margin M."""

    config = protocol["primary_comparison"]
    outer_replicates = int(config["paired_bootstrap_outer_replicates"])
    inner_replicates = int(config["paired_bootstrap_inner_replicates"])
    strict_margin = float(protocol["primary_object"]["minimum_strict_null_margin"])
    deltas: dict[tuple[str, str, str, str], np.ndarray] = {}
    for key in sorted(raw_cells):
        payload = raw_cells[key]
        four_features, labels, halves = payload["4bit"]
        full_features, full_labels, full_halves = payload["float16"]
        if not np.array_equal(labels, full_labels) or not np.array_equal(halves, full_halves):
            raise ValueError(f"prompt-label alignment differs across precision: {key}")
        rng = np.random.default_rng(_stable_seed(seed, *key, "nested-paired"))
        values = np.empty(outer_replicates, dtype=np.float64)
        for replicate in range(outer_replicates):
            outer = _stratified_bootstrap_indices(labels, halves, rng)
            margins = _complete_margin_draw(
                feature_by_precision={
                    "4bit": four_features[outer],
                    "float16": full_features[outer],
                },
                labels=labels[outer],
                halves=halves[outer],
                inner_replicates=inner_replicates,
                rng=rng,
                strict_margin=strict_margin,
            )
            values[replicate] = margins["float16"] - margins["4bit"]
        deltas[key] = values
    rows: list[dict[str, Any]] = []
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
    sentinel = protocol["sentinel"]
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
    interaction_lower = float(np.quantile(interaction, 0.05, method="linear"))
    interaction_upper = float(np.quantile(interaction, 0.95, method="linear"))
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
        "lower_95": interaction_lower,
        "upper_95": interaction_upper,
        "passes_precision_specificity_requirement": bool(interaction_lower > 0.0),
        "sentinel_precision_classification": sentinel_row["precision_classification"],
        "paired_outer_bootstrap_replicates": outer_replicates,
        "paired_inner_replicates": inner_replicates,
    }


def _holonomy_diagnostic(
    result: Mapping[str, Any], *, precision: str) -> list[dict[str, Any]]:
    """Keep rank-one signs as diagnostics; fail closed on orientation reversal."""

    rows: list[dict[str, Any]] = []
    for loop in result.get("loop_receipts", ()):  # full graph output is diagnostic
        if int(loop.get("rank", 0)) != 1:
            continue
        reversing = bool(loop.get("orientation_flag")) or float(loop.get("det_h", 0.0)) < 0
        rows.append(
            {
                "precision": precision,
                "loop_id": loop.get("loop_id"),
                "site": loop.get("site"),
                "rank": 1,
                "det_h": float(loop.get("det_h", 0.0)),
                "orientation_reversal_error": reversing,
                "canonical_angles_degrees": None,
                "status": "orientation_reversal_error" if reversing else "orientable_rank_one_diagnostic",
                "claim_role": "diagnostic_only_no_new_attestation_level",
            }
        )
    return rows


def analyze_precision_context(
    *,
    protocol_path: str | Path,
    manifest_path: str | Path,
    fourbit_indices: Mapping[str, str | Path],
    float16_indices: Mapping[str, str | Path],
    output_dir: str | Path,
) -> dict[str, Any]:
    """Run the fixed outcome-free paired measurement analysis."""

    protocol_path = Path(protocol_path).resolve()
    manifest_path = Path(manifest_path).resolve()
    protocol = load_protocol(protocol_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    validate_manifest(manifest, protocol_path=protocol_path)
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    stores = {
        "4bit": build_pair_store(
            protocol_path=protocol_path,
            manifest_path=manifest_path,
            precision="4bit",
            state_index_paths=fourbit_indices,
            output_dir=output / "fourbit",
        ),
        "float16": build_pair_store(
            protocol_path=protocol_path,
            manifest_path=manifest_path,
            precision="float16",
            state_index_paths=float16_indices,
            output_dir=output / "float16",
        ),
    }
    primary = protocol["primary_object"]
    seed = int(protocol["prompt_design"]["seed"])
    required_margin = float(primary["minimum_strict_null_margin"])
    support: dict[tuple[str, str, str, str, str], Any] = {}
    support_rows: list[dict[str, Any]] = []
    # The original gate is always evaluated first.  Raw L19 data are then
    # retained only for the separately registered nested paired bootstrap.
    raw_cells: dict[
        tuple[str, str, str, str], dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]
    ] = defaultdict(dict)
    for precision, store in stores.items():
        for state in STATES:
            for site in protocol["sites"]:
                for shard_index in range(int(manifest["context_shards"])):
                    shard = f"shard-{shard_index:02d}"
                    common_seed = _stable_seed(seed, state, site, shard, "rank-one")
                    key = (precision, state, site, shard, "graph_reachability")
                    gate_filtration = _rank_one_filtration(
                        store=store,
                        manifest=manifest,
                        precision=precision,
                        state=state,
                        site=site,
                        shard=shard,
                        replicates=int(primary["bootstrap_replicates"]),
                        seed=common_seed,
                        required_margin=required_margin,
                    )
                    support[key] = gate_filtration
                    role = "sentinel" if key[1:] == (
                        protocol["sentinel"]["state"],
                        protocol["sentinel"]["site"],
                        protocol["sentinel"]["context_shard"],
                        protocol["sentinel"]["family"],
                    ) else "control_or_background"
                    support_rows.append(
                        _support_record(
                            precision=precision,
                            state=state,
                            site=site,
                            shard=shard,
                            filtration=gate_filtration,
                            role=role,
                        )
                    )
                    if site == "model.layers.19":
                        raw_cells[(state, site, shard, "graph_reachability")][
                            precision
                        ] = _node_features(
                            store,
                            manifest,
                            runtime=state,
                            site=site,
                            family="graph_reachability",
                            shard=shard,
                        )
    if any(set(value) != set(PRECISIONS) for value in raw_cells.values()):
        raise ValueError("paired precision raw-cell universe differs")
    paired_rows, interaction = _paired_complete_margin_summary(
        raw_cells=raw_cells,
        gate_filtrations=support,
        protocol=protocol,
        seed=_stable_seed(seed, "paired-complete-margin"),
    )
    diagnostic_results = {
        precision: analyze_godel_capture(
            store=store,
            manifest=manifest,
            protocol=_analysis_view(protocol, precision=precision),
            seed=seed,
        )
        for precision, store in stores.items()
    }
    diagnostics = [
        row
        for precision, result in diagnostic_results.items()
        for row in _holonomy_diagnostic(result, precision=precision)
    ]
    sentinel_support = {
        row["precision"]: row
        for row in support_rows
        if row["role"] == "sentinel"
    }
    if set(sentinel_support) != set(PRECISIONS):
        raise ValueError("sentinel support records are incomplete")
    instrument_valid = all(
        bool(item["instrument_calibration_passed_all_ranks"])
        for item in diagnostic_results.values()
    )
    if not instrument_valid:
        final_category = "invalid_capture_pair_or_negative_control_failure"
    elif (
        sentinel_support["float16"]["passed_matched_random_label_gate"]
        and not sentinel_support["4bit"]["passed_matched_random_label_gate"]
        and interaction["passes_precision_specificity_requirement"]
    ):
        final_category = "sentinel_degraded_under_precision_replicated"
    else:
        final_category = "sentinel_not_reproduced_or_not_precision_specific"
    result = {
        "schema_version": RESULT_SCHEMA,
        "protocol_id": PROTOCOL_ID,
        "protocol_sha256": sha256_file(protocol_path),
        "prompt_manifest_sha256": sha256_file(manifest_path),
        "prompt_manifest_pair": precision_manifest_pair_receipt(manifest),
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
        "support_records": support_rows,
        "paired_precision_records": paired_rows,
        "sentinel_interaction": interaction,
        "rank_one_holonomy_diagnostics": diagnostics,
        "diagnostic_geometry_summaries": {
            precision: {
                "claim_role": "diagnostic_only_no_attestation_output",
                "graph_count": int(result["summary"]["graph_count"]),
                "no_supported_grid_count": int(
                    result["summary"]["no_supported_grid_count"]
                ),
                "beta_1_zero_grid_count": int(
                    result["summary"]["beta_1_zero_grid_count"]
                ),
                "rank_one_loop_count": sum(
                    row["precision"] == precision for row in diagnostics
                ),
                "orientation_reversal_error_count": sum(
                    row["precision"] == precision
                    and row["orientation_reversal_error"]
                    for row in diagnostics
                ),
                "instrument_calibration_passed": bool(
                    result["instrument_calibration_passed_all_ranks"]
                ),
            }
            for precision, result in diagnostic_results.items()
        },
        "result_category": final_category,
        "claim_boundary": protocol["claim_boundary"],
    }
    write_once_or_equal(output / "analysis_result.json", canonical_json_bytes(result))
    return result
