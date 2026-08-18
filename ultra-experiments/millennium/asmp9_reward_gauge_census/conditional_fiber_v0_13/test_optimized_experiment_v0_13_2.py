from conditional_fiber import enumerate_fibers, incidence_rows
from optimized_experiment_v0_13_1 import run_power_calibration_streaming
from optimized_experiment_v0_13_2 import (
    direct_zero_balance_fiber,
    run_power_calibration_streaming_direct,
)


def test_direct_cycle_fiber_matches_exhaustive_burned_cells() -> None:
    for k in (3, 4, 6, 8):
        edges = [(index, (index + 1) % k) for index in range(k)]
        rows = incidence_rows(k, edges)
        for n in (1, 2, 3):
            exhaustive = enumerate_fibers([n] * k, rows)[(0,) * k]
            assert direct_zero_balance_fiber(k, n) == exhaustive


def test_v0132_power_matches_v0131_on_burned_cells() -> None:
    spec = {
        "alpha": "1/20",
        "lower_power": "39/50",
        "upper_power": "41/50",
        "formula_trials_per_edge": 2,
        "cells": [
            {
                "cycle_length": 4,
                "odds_ratio": "2/1",
                "trials_per_edge": 207,
            }
        ],
    }
    old = run_power_calibration_streaming(spec)
    new = run_power_calibration_streaming_direct(spec)
    assert old["records"][0]["boundary"] == new["records"][0]["boundary"]
    assert (
        old["records"][0]["exact_power"]["decimal_30"]
        == new["records"][0]["exact_power"]["decimal_30"]
    )
    assert old["power_band_mismatch_count"] == new[
        "power_band_mismatch_count"
    ]
