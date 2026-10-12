from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from efficiency import empirical_bernstein_envelopes, movement_partial_census, run_efficiency


HERE = Path(__file__).resolve().parent


def protocol():
    return json.loads((HERE / "protocol_v0_5.json").read_text(encoding="utf-8"))


def test_empirical_bernstein_envelope_is_nonincreasing():
    errors = np.resize(np.array([-0.05, 0.0, 0.05]), 64)
    values = empirical_bernstein_envelopes(errors, [32, 64, 128], 16, 3, 0.05)
    assert np.all(np.diff(values["u1"], axis=0) <= 1e-15)
    assert np.all(np.diff(values["u2"], axis=0) <= 1e-15)


def test_partial_census_ends_at_exact_gain_and_is_monotone():
    p0 = np.full(4, 0.25)
    policy = np.array([0.0, 0.0, 0.0, 1.0])
    errors = np.array([0.1, -0.2, 0.3, 0.0])
    crossing, margins, exact = movement_partial_census(policy, p0, errors, 0.5)
    assert np.all(np.diff(margins) >= -1e-15)
    assert abs(margins[-1] - exact) < 1e-15
    assert crossing is not None


def test_small_efficiency_replay_is_sound_and_exact():
    result, conditions, rows, cdf = run_efficiency(protocol(), streams_override=32)
    assert len(conditions) == 3
    assert len(rows) == 60
    assert len(cdf) == 960
    assert result["gates"]["G2_conditional_soundness"]["pass"]
    assert result["gates"]["G3_monotone_dynamics"]["pass"]
    assert result["gates"]["G4_partial_census_exactness"]["pass"]
