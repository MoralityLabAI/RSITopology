from __future__ import annotations

import pytest

from scripts.generate_recursive_patchwise_holdout_v2 import (
    FAMILIES,
    PER_FAMILY_SPLIT,
    SPLITS,
    generate,
)
from scripts.score_recursive_patchwise_holdout_v2 import normalize_response, score


def test_holdout_is_deterministic_unique_and_balanced() -> None:
    first_manifest, first_key = generate()
    second_manifest, second_key = generate()
    assert first_manifest == second_manifest
    assert first_key == second_key
    assert first_manifest["prompt_count"] == len(FAMILIES) * len(SPLITS) * PER_FAMILY_SPLIT
    prompts = first_manifest["prompts"]
    assert len({row["prompt_id"] for row in prompts}) == len(prompts)
    assert len({row["prompt"] for row in prompts}) == len(prompts)
    for family in FAMILIES:
        for split in SPLITS:
            rows = [
                row
                for row in prompts
                if row["behavior_family"] == family and row["split"] == split
            ]
            assert len(rows) == PER_FAMILY_SPLIT
    for split in SPLITS:
        graph_answers = [
            item["answer"]
            for item in first_key["answers"].values()
            if item["behavior_family"] == "graph_reachability" and item["split"] == split
        ]
        assert sorted(graph_answers) == ["NO", "NO", "YES", "YES"]


def test_frozen_scorer_is_exact_and_split_scoped() -> None:
    manifest, answer_key = generate()
    selector_ids = [
        row["prompt_id"] for row in manifest["prompts"] if row["split"] == "selector"
    ]
    predictions = {
        prompt_id: f"ANSWER={answer_key['answers'][prompt_id]['answer']}"
        for prompt_id in selector_ids
    }
    result = score(
        manifest=manifest,
        answer_key=answer_key,
        predictions=predictions,
        split="selector",
    )
    assert result["accuracy"] == 1.0
    assert set(result["accuracy_by_family"]) == set(FAMILIES)
    with pytest.raises(ValueError, match="exactly cover"):
        score(
            manifest=manifest,
            answer_key=answer_key,
            predictions={key: value for key, value in predictions.items() if key != selector_ids[0]},
            split="selector",
        )
    assert normalize_response("The answer is 4") == "__INVALID_RESPONSE_CONTRACT__"
    assert normalize_response("ANSWER=4\nextra") == "__INVALID_RESPONSE_CONTRACT__"


def test_answer_key_hash_is_bound_to_public_manifest() -> None:
    manifest, answer_key = generate()
    prompt_id = next(iter(answer_key["answers"]))
    answer_key["answers"][prompt_id]["answer"] = "tampered"
    predictions = {
        row["prompt_id"]: "ANSWER=unused"
        for row in manifest["prompts"]
        if row["split"] == "audit"
    }
    with pytest.raises(ValueError, match="does not match"):
        score(
            manifest=manifest,
            answer_key=answer_key,
            predictions=predictions,
            split="audit",
        )
