from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


FEATURES = _load(
    "asmp8_features", ROOT / "scripts" / "build_asmp8_qwen08_control_gate_features.py"
)
ANALYSIS = _load(
    "asmp8_control_gate", ROOT / "scripts" / "analyze_asmp8_qwen08_control_gate.py"
)


def _manifest():
    prefix = FEATURES.PROMPT_PREFIX
    rows = []
    for index, half in enumerate(("construction", "validation")):
        payload = {
            "actions": ["a", "b"],
            "application": "app",
            "context": "context",
            "proposer_scores": [
                {"action": "a", "score": 0.7},
                {"action": "b", "score": 0.4},
            ],
            "skill": "skill",
            "source_repo": "repo",
        }
        prompt = prefix + FEATURES.canonical_json(payload)
        rows.append(
            {
                "row_id": f"row-{index}",
                "application": "app",
                "geometry_half": half,
                "prompt": prompt,
                "prompt_sha256": "fixture",
            }
        )
    return {"rows": rows}


def test_feature_builder_requires_complete_invariant_census():
    records = []
    for index in range(2):
        for epoch in (0, 1):
            for cached in (False, True):
                records.append(
                    {
                        "phase": "census_crossover",
                        "row_id": f"row-{index}",
                        "tokens": [7],
                        "probability": 0.5 + 0.01 * index,
                        "planned_epoch": epoch,
                        "cache_prompt": cached,
                    }
                )
    rows = FEATURES.build_feature_rows(
        _manifest(), records, probability_tolerance=1e-6
    )
    assert len(rows) == 2
    assert rows[0]["proxy_selected_action"] == "a"
    assert rows[0]["score_margin"] == pytest.approx(0.3)

    records[-1]["probability"] = 0.7
    with pytest.raises(ValueError, match="probability tolerance"):
        FEATURES.build_feature_rows(
            _manifest(), records, probability_tolerance=1e-6
        )


def test_join_rejects_missing_and_duplicate_ids():
    features = [{"row_id": "a", "proxy_selected_action": "x"}]
    outcomes = [{"row_id": "b", "proxy_selected_action": "x"}]
    with pytest.raises(ValueError, match="candidate ID equality"):
        ANALYSIS.joined_rows(features, outcomes)
    with pytest.raises(ValueError, match="duplicate"):
        ANALYSIS.joined_rows(features * 2, [])


def test_selective_risk_auc_rewards_correct_ordering():
    rows = [
        {"row_id": "a", "proxy_regret": 1.0},
        {"row_id": "b", "proxy_regret": 0.5},
        {"row_id": "c", "proxy_regret": 0.0},
    ]
    correct = ANALYSIS.selective_risk_auc(rows, [0.9, 0.5, 0.1])
    reversed_score = ANALYSIS.selective_risk_auc(rows, [0.1, 0.5, 0.9])
    assert correct < reversed_score
