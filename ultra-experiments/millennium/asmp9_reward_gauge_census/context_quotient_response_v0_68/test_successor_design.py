import copy
import importlib.util
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "asmp9_successor_design_v068", HERE / "successor_design.py"
)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def _manifest() -> dict:
    return module.load_manifest(HERE / "scenario_manifest_v0_68.json")


def _records(effect: float = 1.0) -> list[dict]:
    records = []
    for job in module.score_jobs(_manifest(), "construction"):
        target = job["target"]
        direction = 0.0 if target is None else (1.0 if target == 0 else -1.0)
        arm_shift = {
            "baseline": 0.0,
            "balanced": 0.0,
            "balanced_washout": 0.0,
            "label": 0.1 * direction,
            "content": (0.1 + effect) * direction,
            "content_washout": 0.0,
            "repeated_content": (0.1 + effect) * direction,
        }[job["arm"]]
        canonical_score = 0.3 + arm_shift
        raw = (
            canonical_score
            if int(job["display_order"]) == 0
            else -canonical_score
        )
        records.append(
            {
                **{key: value for key, value in job.items() if key != "messages"},
                "logp_a": raw / 2.0,
                "logp_b": -raw / 2.0,
                "raw_log_odds_a_over_b": raw,
                "model_input_sha256": job["messages_sha256"],
                "prompt_token_count": 100,
            }
        )
    return records


def test_job_universe_has_exact_singleton_repeats() -> None:
    jobs = module.score_jobs(_manifest(), "construction")
    assert len(jobs) == 528
    semantic = {}
    for job in jobs:
        semantic.setdefault(job["semantic_id"], []).append(job)
    assert len(semantic) == 264
    assert all(
        {job["repeat_index"] for job in pair} == {0, 1}
        and len({job["messages_sha256"] for job in pair}) == 1
        for pair in semantic.values()
    )


def test_positive_fixture_passes_local_and_restores() -> None:
    result = module.analyze_records(_records(), _manifest(), "construction")
    assert result["instrument"]["mechanical_repeat_status"] == "passed"
    assert result["instrument"]["quotient_admission_status"] == "passed"
    assert result["local_specificity"]["scenario_successes"] == 12
    assert (
        result["local_specificity"]["status"]
        == "local_response_family_established"
    )
    assert result["local_specificity"]["exact_scenario_sign_flip"][
        "randomizations"
    ] == 4096
    assert (
        result["local_specificity"]["exact_scenario_sign_flip"]["exact_p"]
        <= 0.05
    )
    assert result["terminal"]["counts"]["restored"] == 24


def test_context_heterogeneity_can_fail_globality_without_killing_local() -> None:
    records = _records()
    changed_scenario = _manifest()["rows"][0]["scenario_id"]
    for record in records:
        if (
            record["scenario_id"] == changed_scenario
            and record["target"] is not None
            and record["arm"] == "content"
        ):
            direction = 1.0 if int(record["target"]) == 0 else -1.0
            canonical_addition = 2.0 * direction
            raw_addition = (
                canonical_addition
                if int(record["display_order"]) == 0
                else -canonical_addition
            )
            record["logp_a"] += raw_addition / 2.0
            record["logp_b"] -= raw_addition / 2.0
            record["raw_log_odds_a_over_b"] += raw_addition
    result = module.analyze_records(records, _manifest(), "construction")
    assert (
        result["local_specificity"]["status"]
        == "local_response_family_established"
    )
    assert (
        result["global_specificity"]["status"]
        == "context_conditioning_required"
    )


def test_repeat_mismatch_invalidates_local_gate() -> None:
    records = _records()
    records[0]["raw_log_odds_a_over_b"] += 0.1
    result = module.analyze_records(records, _manifest(), "construction")
    assert result["instrument"]["mechanical_repeat_status"] == "failed"
    assert (
        result["local_specificity"]["status"]
        == "local_response_family_not_established"
    )


def test_order_interaction_is_not_averaged_away() -> None:
    records = _records()
    scenario = _manifest()["rows"][0]["scenario_id"]
    for record in records:
        if (
            record["scenario_id"] == scenario
            and record["target"] == 0
            and record["arm"] == "content"
            and record["display_order"] == 1
        ):
            # Flip the canonical content effect for both exact repeats.
            record["logp_a"] += 2.0
            record["logp_b"] -= 2.0
            record["raw_log_odds_a_over_b"] += 4.0
    result = module.analyze_records(records, _manifest(), "construction")
    assert not result["local_specificity"]["scenario_success_by_id"][scenario]


def test_missing_or_duplicate_records_fail_closed() -> None:
    records = _records()
    with pytest.raises(ValueError):
        module.analyze_records(records[:-1], _manifest(), "construction")
    duplicate = copy.deepcopy(records)
    duplicate[-1] = copy.deepcopy(duplicate[0])
    with pytest.raises(ValueError):
        module.analyze_records(duplicate, _manifest(), "construction")
