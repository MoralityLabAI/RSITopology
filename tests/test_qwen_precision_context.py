from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from rsi_topology.qwen_precision_context import (
    _complete_margin_draw,
    _holonomy_diagnostic,
    _rank_one_retention,
    generate_manifest,
    precision_manifest_pair_receipt,
    prompt_separation_receipt,
    validate_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "protocols" / "qwen08_l19_precision_context_v0_1.json"
STAGE_B = ROOT / "protocols" / "qwen08_context_stageb_prompt_manifest_v0_1.json"


def test_manifest_is_deterministic_fresh_and_precision_identical() -> None:
    first = generate_manifest(protocol_path=PROTOCOL)
    second = generate_manifest(protocol_path=PROTOCOL)
    assert first == second
    validate_manifest(first, protocol_path=PROTOCOL)
    assert first["prompt_count"] == 2304
    assert first["prompts_per_subcondition_per_half_per_shard"] == 32
    separation = prompt_separation_receipt(first, compared_manifest_paths=[STAGE_B])
    assert separation["passed"] is True
    assert separation["comparisons"][0]["byte_identical_overlap_count"] == 0
    pair = precision_manifest_pair_receipt(first)
    assert pair["identical_except_runtime_precision"] is True
    assert {
        row["prompt_payload_sha256"] for row in pair["precision_views"].values()
    } == {pair["common_prompt_payload_sha256"]}


def _features(seed: int = 7) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    classes, samples, dimension = 9, 16, 32
    labels = np.asarray(
        [f"class-{class_index:02d}" for _half in range(2) for class_index in range(classes) for _ in range(samples)]
    )
    halves = np.asarray(
        [half for half in ("construction", "geometry_validation") for _class in range(classes) for _ in range(samples)]
    )
    code_left, _ = np.linalg.qr(rng.normal(size=(classes, 4)), mode="reduced")
    codes = code_left @ np.diag([1.35, 1.20, 1.10, 1.00])
    codes -= np.mean(codes, axis=0, keepdims=True)
    stable, _ = np.linalg.qr(rng.normal(size=(dimension, 4)), mode="reduced")
    unstable_a, _ = np.linalg.qr(rng.normal(size=(dimension, 4)), mode="reduced")
    unstable_b, _ = np.linalg.qr(rng.normal(size=(dimension, 4)), mode="reduced")
    full = np.empty((len(labels), dimension), dtype=np.float64)
    four = np.empty_like(full)
    cursor = 0
    for half_index in range(2):
        for class_index in range(classes):
            for _ in range(samples):
                full[cursor] = 7.0 * (stable @ codes[class_index]) + rng.normal(scale=0.35, size=dimension)
                frame = unstable_a if half_index == 0 else unstable_b
                four[cursor] = 7.0 * (frame @ codes[class_index]) + rng.normal(scale=0.35, size=dimension)
                cursor += 1
    return {"4bit": four, "float16": full}, labels, halves


def test_complete_margin_draw_recovers_precision_conditioned_support() -> None:
    features, labels, halves = _features()
    margins = _complete_margin_draw(
        feature_by_precision=features,
        labels=labels,
        halves=halves,
        inner_replicates=32,
        rng=np.random.default_rng(19),
        strict_margin=0.02,
    )
    assert margins["float16"] > 0.02
    assert margins["4bit"] < 0.0
    assert margins["float16"] - margins["4bit"] > 0.10


def test_rank_one_retention_is_sign_gauge_invariant() -> None:
    features, labels, halves = _features(11)
    original = _rank_one_retention(features["float16"], labels, halves)
    # A global sign is a basis gauge change and cannot alter the line object.
    negated = _rank_one_retention(-features["float16"], labels, halves)
    assert np.isclose(original, negated, atol=1e-12)


def test_rank_one_holonomy_is_diagnostic_and_suppresses_angles() -> None:
    result = {
        "loop_receipts": [
            {"loop_id": "clean", "site": "model.layers.19", "rank": 1, "det_h": 1.0, "orientation_flag": False},
            {"loop_id": "reversing", "site": "model.layers.19", "rank": 1, "det_h": -1.0, "orientation_flag": True},
            {"loop_id": "rank-two", "site": "model.layers.19", "rank": 2, "det_h": 1.0, "orientation_flag": False},
        ]
    }
    rows = _holonomy_diagnostic(result, precision="4bit")
    assert [row["loop_id"] for row in rows] == ["clean", "reversing"]
    assert all(row["canonical_angles_degrees"] is None for row in rows)
    assert rows[0]["status"] == "orientable_rank_one_diagnostic"
    assert rows[1]["status"] == "orientation_reversal_error"
    assert all(row["claim_role"] == "diagnostic_only_no_new_attestation_level" for row in rows)


def test_protocol_is_outcome_free_and_has_no_new_invariant_level() -> None:
    value = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert value["outcomes_consumed"] is False
    assert value["generation"] is False
    assert value["gradients"] is False
    assert value["weight_mutation"] is False
    assert value["new_invariant_levels"] is False
