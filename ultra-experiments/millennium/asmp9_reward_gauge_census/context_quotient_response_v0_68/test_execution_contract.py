import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent


def _module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


design = _module("asmp9_design_execution_test", "successor_design.py")
runner = _module("asmp9_runner_execution_test", "run_qwen_v068.py")
analyzer = _module("asmp9_analyzer_execution_test", "analyze_v068.py")


def _manifest() -> dict:
    return design.load_manifest(HERE / "scenario_manifest_v0_68.json")


def _synthetic_records() -> list[dict]:
    records = []
    for job in design.score_jobs(_manifest(), "construction"):
        target = job["target"]
        direction = 0.0 if target is None else (1.0 if target == 0 else -1.0)
        arm_shift = {
            "baseline": 0.0,
            "balanced": 0.0,
            "balanced_washout": 0.0,
            "label": 0.1 * direction,
            "content": 1.1 * direction,
            "content_washout": 0.0,
            "repeated_content": 1.1 * direction,
        }[job["arm"]]
        canonical_score = 0.25 + arm_shift
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
                "model_input_sha256": "0" * 64,
                "prompt_token_count": 100,
            }
        )
    return records


def test_scored_record_validator_rejects_arithmetic_and_identity_changes() -> None:
    job = design.score_jobs(_manifest(), "construction")[0]
    record = _synthetic_records()[0]
    runner.validate_scored_record(record, job)
    bad = dict(record)
    bad["raw_log_odds_a_over_b"] += 1.0
    with pytest.raises(ValueError):
        runner.validate_scored_record(bad, job)
    bad = dict(record)
    bad["repeat_index"] = 99
    with pytest.raises(ValueError):
        runner.validate_scored_record(bad, job)


def test_analyzer_writes_total_construction_decision(
    tmp_path: Path, monkeypatch
) -> None:
    registration_path = tmp_path / "registration.json"
    registration_path.write_text("{}\n", encoding="utf-8")
    registration = {
        "phase": "construction",
    }
    monkeypatch.setattr(
        analyzer.runner,
        "_validate_registration",
        lambda _: (registration, {}, _manifest()),
    )
    result_dir = tmp_path / "result"
    units = result_dir / "work_units"
    rendered = result_dir / "rendered_inputs"
    units.mkdir(parents=True)
    rendered.mkdir(parents=True)
    records = _synthetic_records()
    for record in records:
        text = record["semantic_id"]
        rendered_path = rendered / (
            hashlib.sha256(record["record_id"].encode("utf-8")).hexdigest()
            + ".txt"
        )
        rendered_path.write_text(text, encoding="utf-8")
        record["model_input_sha256"] = analyzer.runner.sha256(rendered_path)
        unit_path = units / (
            hashlib.sha256(record["record_id"].encode("utf-8")).hexdigest()
            + ".json"
        )
        unit_path.write_text(
            json.dumps({"record": record}) + "\n", encoding="utf-8"
        )
    completion = {
        "status": "completed",
        "registration_sha256": analyzer.runner.sha256(registration_path),
    }
    (result_dir / "completion_summary.json").write_text(
        json.dumps(completion) + "\n", encoding="utf-8"
    )
    output = tmp_path / "analysis"
    monkeypatch.setattr(
        "sys.argv",
        [
            "analyze_v068.py",
            "--registration",
            str(registration_path),
            "--result-dir",
            str(result_dir),
            "--output-dir",
            str(output),
        ],
    )
    analyzer.main()
    decision = json.loads(
        (output / "decision.json").read_text(encoding="utf-8")
    )
    assert decision["local_confirmation_authorized"]
    assert decision["decision"] in {
        "local_confirmation_authorized",
        "local_and_global_confirmation_authorized",
    }
    receipt = json.loads(
        (output / "analysis_receipt.json").read_text(encoding="utf-8")
    )
    assert receipt["records"]["count"] == 528
    assert receipt["decision"]["sha256"] == analyzer.runner.sha256(
        output / "decision.json"
    )


def test_confirmation_registration_requires_a_decision_argument() -> None:
    parser_source = (
        HERE / "prepare_execution_registration.py"
    ).read_text(encoding="utf-8")
    assert 'args.phase != "construction"' in parser_source
    assert "confirmation requires a construction decision" in parser_source
    assert '"protocol_amendment"' in parser_source


def test_runner_requires_amended_registration_and_protocol_hash() -> None:
    source = (HERE / "run_qwen_v068.py").read_text(encoding="utf-8")
    assert "execution_registration_v0_68_1" in source
    assert '"protocol_amendment"' in source


def test_prereveal_binds_prompt_dependency_and_synthetic_controls() -> None:
    source = (HERE / "validate_prereveal_v068.py").read_text(encoding="utf-8")
    assert "physical_dynamic_bridge_v0_67" in source
    assert "synthetic_common_mode_removed" in source
    assert "synthetic_arm_by_order_interaction_retained" in source
