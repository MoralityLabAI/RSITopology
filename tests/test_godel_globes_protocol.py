from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from rsi_topology.discovery import (
    discover_between_class_rank_filtration,
    discover_between_class_scatter_object,
)
from rsi_topology.godel_analysis import (
    analyze_godel_capture,
    classify_runtime_support,
    write_analysis_bundle,
)
from rsi_topology.godel_capture import (
    build_synthetic_capture,
    canonical_json_sha256,
    generate_prompt_manifest,
    validate_capture_index,
    validate_prompt_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "protocols" / "godel_globes_falsification_v0_1.json"


def protocol() -> dict:
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def small_protocol() -> dict:
    value = protocol()
    value["candidate_sites"] = ["model.layers.16.self_attn.v_proj"]
    value["primary_object"]["ranks"] = [1, 2, 3]
    value["primary_object"]["bootstrap_replicates"] = 32
    value["holonomy"]["prompt_resampling_replicates"] = 32
    value["gauge_preflight"]["reframings"] = 2
    value["aggregate_identity_gate"]["minimum_physical_sites"] = 1
    value["aggregate_identity_gate"]["minimum_behavior_families"] = 1
    return value


def test_production_prompt_manifest_has_exact_fresh_1152_row_universe():
    value = protocol()
    manifest = generate_prompt_manifest(
        protocol_sha256="a" * 64,
        seed=value["prompt_design"]["seed"],
        families=value["prompt_design"]["families"],
        subconditions_per_family=value["prompt_design"]["subconditions_per_family"],
        context_shards=value["prompt_design"]["context_shards"],
        prompts_per_half=value["prompt_design"][
            "prompts_per_subcondition_per_half_per_shard"
        ],
    )

    validate_prompt_manifest(manifest)
    assert manifest["prompt_count"] == 1152
    assert len({row["prompt_id"] for row in manifest["rows"]}) == 1152
    assert {row["half"] for row in manifest["rows"]} == {
        "construction",
        "geometry_validation",
    }
    assert all(row["geometry_consumes_expected_answer"] is False for row in manifest["rows"])
    assert manifest["vpd_selector_audit_outer_excluded"] is True


def test_rank_filtration_matches_individual_rank_objects_on_point_estimates():
    rng = np.random.default_rng(20260716)
    classes = 7
    rank = 4
    dimension = 18
    planted = np.linalg.qr(rng.normal(size=(dimension, rank)), mode="reduced")[0]
    codes = rng.normal(size=(classes, rank))
    features = []
    labels = []
    halves = []
    for half in ("a", "b"):
        for class_index in range(classes):
            features.append(
                3.0 * (planted @ codes[class_index])
                + rng.normal(scale=0.8, size=(12, dimension))
            )
            labels.extend([str(class_index)] * 12)
            halves.extend([half] * 12)
    values = np.vstack(features)
    filtration = discover_between_class_rank_filtration(
        features=values,
        family_labels=labels,
        construction_halves=halves,
        maximum_rank=rank,
        replicates=32,
        seed=33,
    )
    for candidate_rank in range(1, rank + 1):
        individual = discover_between_class_scatter_object(
            features=values,
            family_labels=labels,
            construction_halves=halves,
            rank=candidate_rank,
            replicates=32,
            seed=33,
        )
        shared = filtration.objects[candidate_rank - 1]
        assert shared.lineage == pytest.approx(individual.lineage)
        assert shared.eigenvalues_by_half[0] == pytest.approx(
            individual.eigenvalues_by_half[0]
        )
    assert filtration.receipt()["shared_resampling_draws"] is True


def test_capture_index_enforces_exact_chunk_universe_and_hashes(tmp_path: Path):
    value = small_protocol()
    manifest = generate_prompt_manifest(
        protocol_sha256=canonical_json_sha256(value),
        families=["affine_recurrence"],
        subconditions_per_family=9,
        context_shards=2,
        prompts_per_half=2,
    )
    index_path = build_synthetic_capture(
        output_dir=tmp_path / "capture",
        manifest=manifest,
        protocol=value,
        ambient_dimension=16,
        planted_rank=3,
    )
    store = validate_capture_index(
        index_path=index_path, manifest=manifest, protocol=value
    )
    assert len(store.chunks) == 2 * 1 * 2 * 2

    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["chunks"] = index["chunks"][:-1]
    broken = index_path.parent / "broken_index.json"
    broken.write_text(json.dumps(index), encoding="utf-8")
    with pytest.raises(ValueError, match="incomplete"):
        validate_capture_index(index_path=broken, manifest=manifest, protocol=value)


def test_runtime_precision_status_is_fail_closed():
    assert classify_runtime_support({"full_float32": 3, "full_bfloat16": 2}) == (
        2,
        "cross_runtime_supported",
    )
    assert classify_runtime_support({"full_float32": 3, "full_bfloat16": 0}) == (
        0,
        "runtime_specific_identity",
    )
    assert classify_runtime_support({"full_float32": 0, "full_bfloat16": 0}) == (
        0,
        "no_supported_identity_rank",
    )


def test_end_to_end_smoke_emits_attested_globe_receipts_without_outcomes(tmp_path: Path):
    value = small_protocol()
    manifest = generate_prompt_manifest(
        protocol_sha256=canonical_json_sha256(value),
        families=["affine_recurrence", "symbol_transport"],
        subconditions_per_family=9,
        context_shards=3,
        prompts_per_half=2,
    )
    index_path = build_synthetic_capture(
        output_dir=tmp_path / "capture",
        manifest=manifest,
        protocol=value,
        ambient_dimension=20,
        planted_rank=3,
    )
    store = validate_capture_index(
        index_path=index_path, manifest=manifest, protocol=value
    )
    result = analyze_godel_capture(
        store=store, manifest=manifest, protocol=value, seed=2026071603
    )

    assert result["outcomes_consumed"] is False
    assert result["weight_mutation_performed"] is False
    assert result["instrument_calibration_passed_all_ranks"] is True
    assert result["summary"]["graph_count"] >= 1
    assert result["summary"]["gauge_preflight"]["status"] == "passed"
    assert result["edge_receipts"]
    assert result["loop_receipts"]
    assert result["lineage_certificates"]
    assert {
        item["certification_level"] for item in result["lineage_certificates"]
    } <= {"engineering_evidence", "lineage_certified", "holonomy_clean"}
    assert all("edge_order" in row for row in result["loop_receipts"])
    assert all(
        row["canonical_angles_degrees"] is None
        for row in result["loop_receipts"]
        if row["det_h"] < 0
    )

    release = write_analysis_bundle(tmp_path / "release", result)
    assert len(release["file_sha256"]) == 6
    for name in (
        "edge_receipts.jsonl",
        "loop_receipts.jsonl",
        "lineage_certificates.jsonl",
        "calibration.json",
        "release_manifest.json",
    ):
        assert (tmp_path / "release" / name).is_file()
