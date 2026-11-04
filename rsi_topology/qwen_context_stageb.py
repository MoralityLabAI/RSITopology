"""Fresh context-restricted Qwen sign-percolation confirmation.

The module keeps capture validation, pair construction, and the Stage-B gate
in one target-blind path.  It consumes activations only; no generated answers,
causal outcomes, gradients, or weight mutations enter the analysis.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.stats import beta

from .godel_analysis import analyze_godel_capture, write_analysis_bundle
from .godel_capture import (
    CaptureChunk,
    CaptureStore,
    canonical_json_bytes,
    generate_prompt_manifest,
    prompt_rows_for_chunk,
    sha256_file,
    validate_prompt_manifest,
    write_once_or_equal,
)
from .percolation import lineage_percolation_curve, percolation_phase_point
from .qwen_state_capture import STATE_CAPTURE_SCHEMA


PROTOCOL_ID = "qwen08_context_stageb_v0_1"
PAIR_INDEX_SCHEMA = "qwen08_context_stageb_pair_index_v0_1"
RESULT_SCHEMA = "qwen08_context_stageb_result_v0_1"


def load_protocol(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if value.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("unexpected context Stage-B protocol")
    if value.get("status") != "registered_not_run":
        raise ValueError("Stage-B protocol is not in its prereveal state")
    if value.get("new_invariant_levels") is not False:
        raise ValueError("Stage B introduces an invariant level")
    if value.get("outcomes_consumed") is not False:
        raise ValueError("Stage B is not target-blind")
    return value


def _prompt_bytes(value: Mapping[str, Any]) -> set[bytes]:
    rows = value.get("rows")
    if not isinstance(rows, list):
        raise ValueError("prompt artifact has no row list")
    result = {str(row.get("prompt", "")).encode("utf-8") for row in rows}
    if b"" in result:
        raise ValueError("prompt artifact contains an empty prompt")
    return result


def generate_manifest(*, protocol_path: str | Path) -> dict[str, Any]:
    path = Path(protocol_path)
    protocol = load_protocol(path)
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
    seed = int(design["seed"])
    for row in value["rows"]:
        payload = f"{seed}\0stage-b\0{row['prompt_id']}".encode("utf-8")
        nonce = hashlib.sha256(payload).hexdigest()[:20]
        row["prompt"] = f"{row['prompt']} Opaque Stage-B nonce: {nonce}."
        shard = str(row["context_shard"])
        row["context_neighborhood"] = (
            "old_shard_02" if shard in ("shard-00", "shard-01") else "old_shard_03"
        )
    value["stage_b_context_design"] = {
        "kind": "fresh_replicates_in_two_preregistered_context_neighborhoods",
        "context_neighborhoods": design["context_neighborhoods"],
        "nonce": "sha256(seed,stage-b,prompt_id) first 20 hex characters",
    }
    validate_manifest(value, protocol_path=path)
    return value


def validate_manifest(
    value: Mapping[str, Any],
    *,
    protocol_path: str | Path,
    separation_artifacts: Sequence[Mapping[str, Any]] = (),
) -> None:
    path = Path(protocol_path)
    protocol = load_protocol(path)
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
            raise ValueError(f"Stage-B prompt manifest differs at {key}")
    rows = value["rows"]
    if len(_prompt_bytes(value)) != len(rows):
        raise ValueError("Stage-B prompt bytes are not unique")
    neighborhoods = design["context_neighborhoods"]
    expected_shards = {
        shard: label for label, shards in neighborhoods.items() for shard in shards
    }
    if set(expected_shards) != {
        f"shard-{index:02d}" for index in range(int(design["context_shards"]))
    }:
        raise ValueError("context neighborhoods do not partition the shard universe")
    for row in rows:
        if row.get("context_neighborhood") != expected_shards[row["context_shard"]]:
            raise ValueError("row context-neighborhood assignment differs")
    fresh = _prompt_bytes(value)
    for artifact in separation_artifacts:
        overlap = fresh & _prompt_bytes(artifact)
        if overlap:
            raise ValueError(f"Stage-B corpus overlaps a prior split ({len(overlap)})")


def separation_receipt(
    manifest: Mapping[str, Any], *, compared_paths: Sequence[str | Path]
) -> dict[str, Any]:
    fresh = _prompt_bytes(manifest)
    rows = []
    for raw in compared_paths:
        path = Path(raw).resolve()
        prior = json.loads(path.read_text(encoding="utf-8-sig"))
        rows.append(
            {
                "path": str(path),
                "sha256": sha256_file(path),
                "prompt_count": len(_prompt_bytes(prior)),
                "byte_identical_overlap_count": len(fresh & _prompt_bytes(prior)),
            }
        )
    return {
        "schema_version": "qwen08_context_stageb_prompt_separation_v0_1",
        "fresh_prompt_count": len(fresh),
        "comparisons": rows,
        "passed": all(row["byte_identical_overlap_count"] == 0 for row in rows),
    }


def _expected_keys(
    *, state_id: str, sites: Sequence[str], context_shards: int
) -> set[tuple[str, str, str, str]]:
    return {
        (state_id, site, f"shard-{shard:02d}", half)
        for site in sites
        for shard in range(context_shards)
        for half in ("construction", "geometry_validation")
    }


def validate_capture_index(
    *,
    index_path: str | Path,
    protocol_path: str | Path,
    manifest_path: str | Path,
    state_id: str,
    sites: Sequence[str],
    quantization: str,
    causal_protocol_sha256: str,
) -> tuple[dict[str, Any], dict[tuple[str, str, str, str], CaptureChunk]]:
    protocol_path = Path(protocol_path).resolve()
    manifest_path = Path(manifest_path).resolve()
    index_path = Path(index_path).resolve()
    protocol = load_protocol(protocol_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest, protocol_path=protocol_path)
    value = json.loads(index_path.read_text(encoding="utf-8"))
    if value.get("schema_version") != STATE_CAPTURE_SCHEMA:
        raise ValueError("invalid Stage-B capture-index schema")
    if value.get("state_id") != state_id or value.get("quantization") != quantization:
        raise ValueError("Stage-B capture state or quantization differs")
    if value.get("protocol_sha256") != causal_protocol_sha256:
        raise ValueError("Stage-B capture causal-protocol binding differs")
    if value.get("geometry_manifest_sha256") != sha256_file(manifest_path):
        raise ValueError("Stage-B capture manifest binding differs")
    scientific = value.get("scientific_protocol")
    if not isinstance(scientific, Mapping) or scientific.get("protocol_id") != PROTOCOL_ID:
        raise ValueError("Stage-B scientific binding is absent")
    if scientific.get("sha256") != sha256_file(protocol_path):
        raise ValueError("Stage-B scientific protocol changed")
    registered_sites = set(protocol["main_capture"]["sites"]) | set(
        protocol["precision_control"]["sites"]
    )
    if not set(sites) <= registered_sites:
        raise ValueError("capture index requests unregistered Stage-B sites")
    expected = _expected_keys(
        state_id=state_id,
        sites=sites,
        context_shards=int(manifest["context_shards"]),
    )
    chunks: dict[tuple[str, str, str, str], CaptureChunk] = {}
    ids: set[str] = set()
    for row in value.get("chunks", ()):
        key = (
            str(row.get("state_id")),
            str(row.get("site_id")),
            str(row.get("context_shard")),
            str(row.get("half")),
        )
        chunk_id = str(row.get("chunk_id", ""))
        if key not in expected or key in chunks or not chunk_id or chunk_id in ids:
            raise ValueError("Stage-B capture chunk universe is invalid")
        ids.add(chunk_id)
        path = (index_path.parent / str(row["path"])).resolve()
        if not path.is_file() or sha256_file(path) != row.get("sha256"):
            raise ValueError(f"Stage-B capture chunk missing or changed: {chunk_id}")
        prompt_ids = tuple(
            str(item["prompt_id"])
            for item in prompt_rows_for_chunk(
                manifest, context_shard=key[2], half=key[3]
            )
        )
        if tuple(map(str, row.get("prompt_ids", ()))) != prompt_ids:
            raise ValueError(f"Stage-B prompt order differs: {chunk_id}")
        with np.load(path, allow_pickle=False) as archive:
            if set(archive.files) != {"activations"}:
                raise ValueError(f"Stage-B chunk keys differ: {chunk_id}")
            array = np.asarray(archive["activations"])
        expected_shape = (len(prompt_ids), int(row["ambient_dimension"]))
        if array.shape != expected_shape or not np.all(np.isfinite(array)):
            raise ValueError(f"Stage-B chunk shape or finiteness differs: {chunk_id}")
        chunks[key] = CaptureChunk(
            chunk_id=chunk_id,
            runtime_precision=state_id,
            site_id=key[1],
            context_shard=key[2],
            half=key[3],
            path=path,
            sha256=str(row["sha256"]),
            prompt_ids=prompt_ids,
            row_count=len(prompt_ids),
            ambient_dimension=int(row["ambient_dimension"]),
            dtype=str(row["dtype"]),
        )
    if set(chunks) != expected:
        raise ValueError("Stage-B capture index is incomplete")
    return value, chunks


def build_pair_store(
    *,
    protocol_path: str | Path,
    manifest_path: str | Path,
    state_index_paths: Mapping[str, str | Path],
    sites: Sequence[str],
    quantization: str,
    causal_protocol_sha256: str,
    output_dir: str | Path,
) -> CaptureStore:
    protocol = load_protocol(protocol_path)
    states = tuple(map(str, protocol["states"]))
    if set(state_index_paths) != set(states):
        raise ValueError("Stage-B pair does not cover the exact state universe")
    chunks: dict[tuple[str, str, str, str], CaptureChunk] = {}
    sources: dict[str, dict[str, str]] = {}
    for state in states:
        path = Path(state_index_paths[state]).resolve()
        _, state_chunks = validate_capture_index(
            index_path=path,
            protocol_path=protocol_path,
            manifest_path=manifest_path,
            state_id=state,
            sites=sites,
            quantization=quantization,
            causal_protocol_sha256=causal_protocol_sha256,
        )
        sources[state] = {"path": str(path), "sha256": sha256_file(path)}
        for key, chunk in state_chunks.items():
            if key in chunks:
                raise ValueError("duplicate Stage-B pair chunk")
            chunks[key] = chunk
    pair_index = {
        "schema_version": PAIR_INDEX_SCHEMA,
        "scientific_protocol_sha256": sha256_file(protocol_path),
        "prompt_manifest_sha256": sha256_file(manifest_path),
        "quantization": quantization,
        "states": list(states),
        "sites": list(sites),
        "source_state_indices": sources,
        "outcomes_consumed": False,
        "weight_mutation_performed": False,
    }
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    index_path = output / "pair_capture_index.json"
    write_once_or_equal(index_path, canonical_json_bytes(pair_index))
    return CaptureStore(index_path=index_path, index=pair_index, chunks=chunks)


def analysis_view(
    protocol: Mapping[str, Any], *, sites: Sequence[str], quantization: str
) -> dict[str, Any]:
    return {
        "protocol_id": f"{PROTOCOL_ID}:{quantization}",
        "runtime_precisions": list(protocol["states"]),
        "candidate_sites": list(sites),
        "primary_object": {
            "kind": protocol["primary_object"]["kind"],
            "ranks": list(protocol["primary_object"]["ranks"]),
            "bootstrap_replicates": int(
                protocol["primary_object"]["bootstrap_replicates"]
            ),
            "minimum_strict_null_margin": float(
                protocol["primary_object"]["minimum_strict_null_margin"]
            ),
        },
        "instrument_calibration": {
            "required_margin": float(
                protocol["primary_object"]["minimum_strict_null_margin"]
            )
        },
        "graph": {
            "lineage_floor": float(protocol["graph"]["lineage_floor"]),
        },
        "holonomy": {
            "prompt_resampling_replicates": int(
                protocol["holonomy"]["prompt_resampling_replicates"]
            ),
            "budget": dict(protocol["holonomy"]["budget"]),
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


def _edge_class(edge_id: str) -> str:
    return "checkpoint" if ":precision:" in edge_id else "context"


def _cp_upper(reversals: int, trials: int, alpha: float) -> float:
    if trials < 1 or reversals < 0 or reversals > trials:
        raise ValueError("invalid Clopper-Pearson counts")
    if reversals == trials:
        return 1.0
    return float(beta.ppf(1.0 - alpha, reversals + 1, trials - reversals))


def summarize_geometry(
    result: Mapping[str, Any], *, protocol: Mapping[str, Any]
) -> dict[str, Any]:
    floor = float(protocol["percolation_gate"]["lineage_floor"])
    replicates = int(protocol["holonomy"]["prompt_resampling_replicates"])
    alpha = float(protocol["holonomy"]["w1_gate"]["alpha"])
    upper_limit = float(
        protocol["holonomy"]["w1_gate"][
            "maximum_reversal_probability_upper_95"
        ]
    )
    site_rows = []
    for graph in result["graphs"]:
        site = str(graph["site"])
        edges = [
            row for row in result["edge_receipts"] if str(row["edge_id"]).startswith(site + ":")
        ]
        loops = [row for row in result["loop_receipts"] if row["site"] == site]
        nodes = sorted(
            {
                str(row[key])
                for row in edges
                for key in ("source_node", "target_node")
            }
        )
        edge_signs = {
            str(row["edge_id"]): (
                1 if float(row["geometry_validation_transport_det"]) >= 0.0 else -1
            )
            for row in edges
        }
        curve = lineage_percolation_curve(
            edges=edges,
            loops=loops,
            registered_nodes=nodes,
            edge_classes={str(row["edge_id"]): _edge_class(str(row["edge_id"])) for row in edges},
        )
        phase = percolation_phase_point(
            edges=edges,
            loops=loops,
            registered_nodes=nodes,
            edge_signs=edge_signs,
            lineage_floor=floor,
        )
        loop_rows = []
        for loop in loops:
            probability = float(loop["bootstrap_orientation_reversal_probability"])
            reversals = int(round(probability * replicates))
            upper = _cp_upper(reversals, replicates, alpha)
            admitted = bool(loop["admitted_by_bifiltration"])
            passed = bool(
                admitted
                and float(loop["det_h"]) > 0.0
                and loop["construction_validation_agreement"]
                and upper <= upper_limit
            )
            loop_rows.append(
                {
                    "loop_id": loop["loop_id"],
                    "admitted": admitted,
                    "det_h": loop["det_h"],
                    "construction_validation_agreement": loop[
                        "construction_validation_agreement"
                    ],
                    "bootstrap_reversal_count": reversals,
                    "bootstrap_replicates": replicates,
                    "reversal_probability_upper_95": upper,
                    "w1_generator_pass": passed,
                }
            )
        admitted_rows = [row for row in loop_rows if row["admitted"]]
        site_rows.append(
            {
                "site": site,
                "rank": graph["rank"],
                "curve": curve.to_dict(),
                "phase_at_registered_floor": phase.to_dict(),
                "admitted_generator_count": len(admitted_rows),
                "w1_gate_passed": bool(
                    admitted_rows and all(row["w1_generator_pass"] for row in admitted_rows)
                ),
                "loops": loop_rows,
            }
        )
    coherent_sites = [
        row
        for row in site_rows
        if row["phase_at_registered_floor"]["phase"] == "coherent"
        and row["phase_at_registered_floor"]["beta_1"] > 0
        and row["w1_gate_passed"]
    ]
    return {
        "site_results": site_rows,
        "coherent_w1_site_count": len(coherent_sites),
        "main_gate_passed": bool(coherent_sites),
    }


def precision_comparison(
    main: Mapping[str, Any], control: Mapping[str, Any], *, site: str
) -> dict[str, Any]:
    def site_record(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
        return next((row for row in value["site_results"] if row["site"] == site), None)

    left, right = site_record(main), site_record(control)
    if left is None or right is None:
        return {"status": "unavailable", "passed": False, "reason": "site_graph_missing"}
    left_loops = {row["loop_id"]: row for row in left["loops"] if row["admitted"]}
    right_loops = {row["loop_id"]: row for row in right["loops"] if row["admitted"]}
    common = sorted(set(left_loops) & set(right_loops))
    sign_agreement = all(
        (float(left_loops[key]["det_h"]) >= 0.0)
        == (float(right_loops[key]["det_h"]) >= 0.0)
        for key in common
    )
    phases = (
        left["phase_at_registered_floor"]["phase"],
        right["phase_at_registered_floor"]["phase"],
    )
    passed = bool(common and sign_agreement and phases == ("coherent", "coherent"))
    return {
        "status": "passed" if passed else "failed",
        "passed": passed,
        "site": site,
        "common_admitted_loop_ids": common,
        "determinant_sign_agreement": sign_agreement,
        "main_phase": phases[0],
        "float16_phase": phases[1],
    }


def analyze_stage_b(
    *,
    protocol_path: str | Path,
    causal_protocol_path: str | Path,
    manifest_path: str | Path,
    main_indices: Mapping[str, str | Path],
    control_indices: Mapping[str, str | Path],
    output_dir: str | Path,
    seed: int,
) -> dict[str, Any]:
    protocol = load_protocol(protocol_path)
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    causal_hash = sha256_file(causal_protocol_path)
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    validate_manifest(manifest, protocol_path=protocol_path)
    main_sites = tuple(protocol["main_capture"]["sites"])
    control_sites = tuple(protocol["precision_control"]["sites"])
    main_store = build_pair_store(
        protocol_path=protocol_path,
        manifest_path=manifest_path,
        state_index_paths=main_indices,
        sites=main_sites,
        quantization=str(protocol["main_capture"]["quantization"]),
        causal_protocol_sha256=causal_hash,
        output_dir=output / "main_4bit",
    )
    control_store = build_pair_store(
        protocol_path=protocol_path,
        manifest_path=manifest_path,
        state_index_paths=control_indices,
        sites=control_sites,
        quantization=str(protocol["precision_control"]["quantization"]),
        causal_protocol_sha256=causal_hash,
        output_dir=output / "control_float16",
    )
    main_result = analyze_godel_capture(
        store=main_store,
        manifest=manifest,
        protocol=analysis_view(protocol, sites=main_sites, quantization="4bit"),
        seed=seed,
    )
    control_result = analyze_godel_capture(
        store=control_store,
        manifest=manifest,
        protocol=analysis_view(protocol, sites=control_sites, quantization="float16"),
        seed=seed,
    )
    main_result["scientific_protocol_file_sha256"] = sha256_file(protocol_path)
    control_result["scientific_protocol_file_sha256"] = sha256_file(protocol_path)
    write_analysis_bundle(output / "main_4bit", main_result)
    write_analysis_bundle(output / "control_float16", control_result)
    main_summary = summarize_geometry(main_result, protocol=protocol)
    control_summary = summarize_geometry(control_result, protocol=protocol)
    precision = precision_comparison(
        main_summary, control_summary, site=str(control_sites[0])
    )
    if not main_result["instrument_calibration_passed_all_ranks"]:
        decision = "invalid_instrument_or_provenance"
    elif main_summary["main_gate_passed"]:
        decision = (
            "out_of_sample_w1_and_coherent_phase_supported"
            if precision["passed"]
            else "main_result_only_precision_stability_not_established"
        )
    elif not any(row["admitted_generator_count"] for row in main_summary["site_results"]):
        decision = "not_established_holonomy_unavailable"
    elif any(not row["w1_gate_passed"] for row in main_summary["site_results"] if row["admitted_generator_count"]):
        decision = "fresh_w1_prediction_failed"
    else:
        decision = "not_established_lineage_disconnected_at_frozen_floor"
    result = {
        "schema_version": RESULT_SCHEMA,
        "scientific_protocol_sha256": sha256_file(protocol_path),
        "causal_protocol_sha256": causal_hash,
        "prompt_manifest_sha256": sha256_file(manifest_path),
        "main_pair_index_sha256": sha256_file(main_store.index_path),
        "control_pair_index_sha256": sha256_file(control_store.index_path),
        "main": main_summary,
        "precision_control": {"geometry": control_summary, "comparison": precision},
        "decision": decision,
        "outcomes_consumed": False,
        "generation": False,
        "gradients": False,
        "weight_mutation": False,
        "new_invariant_levels": False,
        "claim_boundary": protocol["claim_boundary"],
    }
    write_once_or_equal(output / "stage_b_result.json", canonical_json_bytes(result))
    return result

