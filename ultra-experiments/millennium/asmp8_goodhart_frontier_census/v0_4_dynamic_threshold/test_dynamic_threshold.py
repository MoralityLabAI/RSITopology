from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from dynamic_threshold import nested_envelopes, run_dynamic, summarize_first_crossings


HERE = Path(__file__).resolve().parent


def protocol():
    return json.loads((HERE / "protocol_v0_4.json").read_text(encoding="utf-8"))


def test_nested_envelopes_are_nonincreasing():
    errors = np.resize(np.array([-0.05, 0.0, 0.05]), 64)
    values = nested_envelopes(errors, [8, 16, 32, 64], 32, 7, 0.05)
    assert np.all(np.diff(values["u1"], axis=0) <= 1e-15)
    assert np.all(np.diff(values["u2"], axis=0) <= 1e-15)


def test_crossing_summary_has_no_fraction_gate():
    summary = summarize_first_crossings(np.array([0, 64, 128, 128]), 256)
    assert summary["crossed_streams"] == 3
    assert summary["censored_streams"] == 1
    assert summary["median"] == 128
    assert "pass" not in summary


def test_small_dynamic_replay_is_monotone_and_sound():
    result, conditions, policies, cdf = run_dynamic(protocol(), streams_override=32)
    assert len(conditions) == 3
    assert len(policies) == 60
    assert len(cdf) == 960
    assert result["gates"]["G2_monotone_dynamics"]["pass"]
    assert result["gates"]["G3_conditional_soundness"]["pass"]
    assert result["gates"]["G6_no_reversion"]["pass"]
