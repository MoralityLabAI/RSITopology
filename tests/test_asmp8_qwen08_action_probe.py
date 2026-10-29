from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MANIFEST = _load(
    "asmp8_action_manifest",
    ROOT / "scripts" / "build_asmp8_qwen08_action_probe_manifest.py",
)
RUNNER = _load(
    "asmp8_action_runner", ROOT / "scripts" / "run_qwen08_action_probe.py"
)
FEATURES = _load(
    "asmp8_action_features",
    ROOT / "scripts" / "build_asmp8_qwen08_action_probe_features.py",
)


def source_manifest():
    payload = {
        "actions": ["alpha", "beta", "gamma", "delta"],
        "application": "app",
        "context": "context",
        "proposer_scores": [
            {"action": "alpha", "score": 0.1},
            {"action": "beta", "score": 0.7},
            {"action": "gamma", "score": 0.3},
            {"action": "delta", "score": 0.2},
        ],
        "skill": "skill",
        "source_repo": "repo",
    }
    prompt = MANIFEST.SOURCE_PREFIX + MANIFEST.canonical_bytes(payload).decode().strip()
    return {
        "schema_version": "fixture",
        "manifest_semantic_sha256": "source-semantic",
        "benchmark_seed": 7,
        "applications": ["app"],
        "outcomes_consumed": False,
        "rows": [
            {
                "row_id": "row-0",
                "application": "app",
                "geometry_half": "construction",
                "prompt": prompt,
                "prompt_sha256": "source-prompt",
            }
        ],
    }


def test_manifest_is_outcome_blind_and_labels_original_order():
    manifest = MANIFEST.build_probe_manifest(source_manifest(), "source-sha")
    row = manifest["rows"][0]
    assert manifest["outcomes_consumed"] is False
    assert row["action_labels"] == {
        "A": "alpha",
        "B": "beta",
        "C": "gamma",
        "D": "delta",
    }
    assert "optimal_action" not in row["prompt"]
    assert row["prompt"].endswith("\nAnswer:")


def test_extracts_complete_post_sampling_distribution():
    payload = {
        "completion_probabilities": [
            {
                "token": "B",
                "prob": 0.4,
                "top_probs": [
                    {"token": "A", "prob": 0.1},
                    {"token": "B", "prob": 0.4},
                    {"token": "C", "prob": 0.3},
                    {"token": "D", "prob": 0.2},
                ],
            }
        ]
    }
    values = RUNNER.extract_choice_distribution(payload)
    assert values == pytest.approx({"A": 0.1, "B": 0.4, "C": 0.3, "D": 0.2})
    payload["completion_probabilities"][0]["top_probs"].pop()
    with pytest.raises(ValueError, match="incomplete"):
        RUNNER.extract_choice_distribution(payload)


def test_plan_requires_two_cold_starts():
    manifest = MANIFEST.build_probe_manifest(source_manifest(), "source-sha")
    plan = RUNNER.build_plan(manifest, 2)
    assert plan["item_count"] == 2
    assert [item["planned_epoch"] for item in plan["items"]] == [0, 1]
    with pytest.raises(ValueError, match="two"):
        RUNNER.build_plan(manifest, 1)


def test_feature_builder_enforces_repeatability_and_maps_probe_action():
    manifest = MANIFEST.build_probe_manifest(source_manifest(), "source-sha")
    records = []
    for epoch in (0, 1):
        records.append(
            {
                "row_id": "row-0",
                "planned_epoch": epoch,
                "choice_probabilities": {
                    "A": 0.1,
                    "B": 0.4,
                    "C": 0.3,
                    "D": 0.2,
                },
            }
        )
    rows = FEATURES.build_feature_rows(
        manifest,
        records,
        probability_tolerance=1e-7,
        sum_tolerance=1e-7,
    )
    assert rows[0]["proxy_selected_action"] == "beta"
    assert rows[0]["probe_selected_action"] == "beta"
    assert rows[0]["probe_probability_margin"] == pytest.approx(0.1)

    records[1]["choice_probabilities"]["B"] = 0.4001
    records[1]["choice_probabilities"]["D"] = 0.1999
    with pytest.raises(ValueError, match="repeat tolerance"):
        FEATURES.build_feature_rows(
            manifest,
            records,
            probability_tolerance=1e-7,
            sum_tolerance=1e-7,
        )
