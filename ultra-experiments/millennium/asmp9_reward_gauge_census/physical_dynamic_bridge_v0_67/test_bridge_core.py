from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("bridge_core_v067", HERE / "bridge_core.py")
assert SPEC and SPEC.loader
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


def manifest():
    return core.load_manifest(HERE / "scenario_manifest_v0_67.json")


def _synthetic_records(split: str, *, replay_failure: bool = False):
    rows = core.score_jobs(manifest(), split)
    scenario_ids = sorted({row["scenario_id"] for row in rows})
    bad_scenario = scenario_ids[-1]
    result = []
    for job in rows:
        arm = job["arm"]
        target = job["target"]
        base = 0.40
        if arm in {"baseline", "fresh_reset", "balanced"}:
            z = base
        elif arm == "balanced_washout":
            z = base + 0.02
        elif arm == "label":
            direction = 1.0 if target == 0 else -1.0
            z = base + direction * 0.05
        elif arm == "content":
            direction = 1.0 if target == 0 else -1.0
            z = base + direction * 0.80
        elif arm == "content_washout":
            direction = 1.0 if target == 0 else -1.0
            z = base + 0.02 + direction * 0.01
        elif arm == "repeated_content":
            direction = 1.0 if target == 0 else -1.0
            z = base + direction * 1.20
        else:  # pragma: no cover
            raise AssertionError(arm)
        if (
            replay_failure
            and split == "confirmation"
            and job["scenario_id"] == bad_scenario
            and arm == "repeated_content"
            and target == 1
        ):
            z = 0.40
        order_bias = 0.01 if job["display_order"] == 0 else -0.01
        canonical = z + order_bias
        raw = canonical if job["display_order"] == 0 else -canonical
        result.append(
            {
                **{key: value for key, value in job.items() if key != "messages"},
                "logp_a": -1.0 + 0.5 * raw,
                "logp_b": -1.0 - 0.5 * raw,
                "raw_log_odds_a_over_b": raw,
            }
        )
    return result


def test_manifest_is_paired_and_complete():
    value = manifest()
    assert len(value["rows"]) == 20
    assert len({row["family"] for row in value["rows"]}) == 10
    for family in {row["family"] for row in value["rows"]}:
        assert {
            row["split"] for row in value["rows"] if row["family"] == family
        } == {"construction", "confirmation"}


def test_job_count_and_ids_are_unique():
    for split in ("construction", "confirmation"):
        jobs = core.score_jobs(manifest(), split)
        assert len(jobs) == 240
        assert len({job["record_id"] for job in jobs}) == 240
        assert {job["display_order"] for job in jobs} == {0, 1}


def test_canonical_target_letter_swaps_with_display_order():
    row = manifest()["rows"][0]
    forward = core.build_messages(manifest(), row, "content", 0, 0)
    reverse = core.build_messages(manifest(), row, "content", 1, 0)
    assert "option A" in forward[2]["content"]
    assert "option B" in reverse[2]["content"]
    assert row["option_0"] in forward[2]["content"]
    assert row["option_0"] in reverse[2]["content"]


def test_order_symmetrization_recovers_canonical_score():
    records = [
        {
            "scenario_id": "s",
            "family": "f",
            "split": "construction",
            "arm": "baseline",
            "target": None,
            "display_order": 0,
            "raw_log_odds_a_over_b": 0.7,
            "logp_a": -0.3,
            "logp_b": -1.0,
        },
        {
            "scenario_id": "s",
            "family": "f",
            "split": "construction",
            "arm": "baseline",
            "target": None,
            "display_order": 1,
            "raw_log_odds_a_over_b": -0.5,
            "logp_a": -1.0,
            "logp_b": -0.5,
        },
    ]
    summary = core.summarize_orders(records)[("s", "baseline", None)]
    assert summary["z_sym"] == pytest.approx(0.6)
    assert summary["order_half_range"] == pytest.approx(0.1)


def test_construction_envelope_is_derived_without_outcome_tuning():
    calibration = core.derive_construction_calibration(
        _synthetic_records("construction")
    )
    assert calibration["epsilon_measurement"] == pytest.approx(0.01)
    assert calibration["epsilon_restore"] == pytest.approx(0.02)
    assert calibration["transition_model"]["status"] == "established_on_construction"
    assert calibration["derivation"]["quantile_selection"] == "none; simultaneous maximum envelope"


def test_confirmation_separates_effect_restoration_and_transducer_status():
    construction = _synthetic_records("construction")
    calibration = core.derive_construction_calibration(construction)
    result = core.analyze_records(_synthetic_records("confirmation"), calibration)
    assert result["instrument"]["fresh_reset_status"] == "passed"
    assert result["instrument"]["order_stability_status"] == "passed"
    assert result["context_effect"]["status"] == "content_specific_effect_established"
    assert result["terminal"]["counts"] == {
        "restored": 20,
        "persistent": 0,
        "inconclusive": 0,
    }
    assert result["created_consensus"]["eligible_opposed_stable_cells"] == 10
    assert result["created_consensus"]["strict_flips"] == 10
    assert result["transducer"]["status"] == "held_out_replay_passed"


def test_transducer_failure_does_not_erase_descriptive_context_effect():
    calibration = core.derive_construction_calibration(
        _synthetic_records("construction")
    )
    result = core.analyze_records(
        _synthetic_records("confirmation", replay_failure=True), calibration
    )
    assert result["context_effect"]["status"] == "content_specific_effect_established"
    assert result["transducer"]["status"] == "latent_state_model_not_established_replay_failure"
    assert result["transducer"]["failures"]


def test_incomplete_order_pair_is_rejected():
    rows = _synthetic_records("construction")
    with pytest.raises(ValueError, match="incomplete display-order pair"):
        core.summarize_orders(rows[:-1])


def test_duplicate_order_pair_is_rejected():
    rows = _synthetic_records("construction")
    with pytest.raises(ValueError, match="duplicate order record"):
        core.summarize_orders(rows + [dict(rows[0])])


def test_resumable_record_must_bind_job_and_arithmetic():
    job = core.score_jobs(manifest(), "construction")[0]
    record = {
        **{key: value for key, value in job.items() if key != "messages"},
        "prompt_token_count": 42,
        "logp_a": -0.25,
        "logp_b": -1.0,
        "raw_log_odds_a_over_b": 0.75,
        "model_input_sha256": "a" * 64,
    }
    core.validate_scored_record(record, job)
    wrong = dict(record, arm="content")
    with pytest.raises(ValueError, match="differs from registered job"):
        core.validate_scored_record(wrong, job)
    wrong = dict(record, raw_log_odds_a_over_b=0.74)
    with pytest.raises(ValueError, match="arithmetic mismatch"):
        core.validate_scored_record(wrong, job)
