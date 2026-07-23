from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).parents[1] / "scripts" / "run_qwen08_completion_audits.py"
SPEC = importlib.util.spec_from_file_location("run_qwen08_completion_audits", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_extract_probability_from_current_post_sampling_schema() -> None:
    assert MODULE.extract_probability({"probs": [{"prob": 0.25}]}) == 0.25


def test_extract_probability_from_current_logprob_schema() -> None:
    observed = MODULE.extract_probability({"probs": [{"logprob": math.log(0.4)}]})
    assert observed is not None
    assert abs(observed - 0.4) < 1e-12


def test_extract_probability_from_legacy_nested_schema() -> None:
    payload = {"completion_probabilities": [{"probs": [{"prob": 0.75}]}]}
    assert MODULE.extract_probability(payload) == 0.75


def test_thermal_window_pauses_until_resume_threshold(monkeypatch, tmp_path: Path) -> None:
    temperatures = iter([85.0, 84.0, 80.0])
    monkeypatch.setattr(MODULE, "gpu_temperature_c", lambda: next(temperatures))
    monkeypatch.setattr(MODULE.time, "sleep", lambda _: None)
    args = SimpleNamespace(
        thermal_pause_temperature=85.0,
        thermal_resume_temperature=80.0,
        thermal_poll_seconds=0.001,
    )
    progress = {
        "thermal_pause_count": 0,
        "thermal_pause_seconds": 0.0,
        "thermal_poll_count": 0,
        "maximum_runner_observed_temperature_c": 0.0,
    }
    events_path = tmp_path / "events.jsonl"
    progress_path = tmp_path / "progress.json"

    MODULE.wait_for_thermal_window(args, events_path, progress_path, progress)

    assert progress["thermal_pause_count"] == 1
    assert progress["thermal_poll_count"] == 2
    assert progress["maximum_runner_observed_temperature_c"] == 85.0
    events = [
        json.loads(line)
        for line in events_path.read_text(encoding="utf-8").splitlines()
    ]
    assert [event["event"] for event in events] == [
        "thermal_pause_start",
        "thermal_pause_end",
    ]


def test_thermal_window_does_not_pause_below_threshold(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(MODULE, "gpu_temperature_c", lambda: 84.0)
    args = SimpleNamespace(
        thermal_pause_temperature=85.0,
        thermal_resume_temperature=80.0,
        thermal_poll_seconds=0.001,
    )
    progress = {
        "thermal_pause_count": 0,
        "thermal_pause_seconds": 0.0,
        "thermal_poll_count": 0,
        "maximum_runner_observed_temperature_c": 0.0,
    }

    MODULE.wait_for_thermal_window(
        args,
        tmp_path / "events.jsonl",
        tmp_path / "progress.json",
        progress,
    )

    assert progress["thermal_pause_count"] == 0
    assert progress["maximum_runner_observed_temperature_c"] == 84.0
    assert not (tmp_path / "events.jsonl").exists()


def test_atomic_json_retries_transient_windows_file_lock(
    monkeypatch, tmp_path: Path
) -> None:
    output_path = tmp_path / "progress.json"
    original_replace = Path.replace
    attempts = {"count": 0}

    def intermittently_locked(source: Path, target: Path) -> Path:
        attempts["count"] += 1
        if attempts["count"] <= 2:
            raise PermissionError("simulated Windows reader lock")
        return original_replace(source, target)

    monkeypatch.setattr(Path, "replace", intermittently_locked)
    monkeypatch.setattr(MODULE.time, "sleep", lambda _: None)

    MODULE.atomic_json(output_path, {"completed_audits": 100})

    assert attempts["count"] == 3
    assert json.loads(output_path.read_text(encoding="utf-8")) == {
        "completed_audits": 100
    }


def test_default_thermal_check_size_is_positive() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'parser.add_argument("--thermal-check-every", type=int, default=20)' in source
    assert "min(args.thermal_check_every, args.parallel)" in source
