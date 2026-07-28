from experiment import run_power_calibration
from optimized_experiment_v0_13_1 import run_power_calibration_streaming


def test_optimized_power_matches_literal_burned_cells() -> None:
    spec = {
        "alpha": "1/20",
        "lower_power": "1/20",
        "upper_power": "1/1",
        "formula_trials_per_edge": 2,
        "cells": [
            {
                "cycle_length": 3,
                "odds_ratio": "3/2",
                "trials_per_edge": 7,
            },
            {
                "cycle_length": 4,
                "odds_ratio": "2/1",
                "trials_per_edge": 9,
            },
        ],
    }
    literal = run_power_calibration(spec)
    optimized = run_power_calibration_streaming(spec)
    assert literal["formula_mismatch_count"] == optimized[
        "formula_mismatch_count"
    ]
    assert literal["likelihood_ratio_mismatch_count"] == optimized[
        "likelihood_ratio_mismatch_count"
    ]
    assert literal["size_mismatch_count"] == optimized[
        "size_mismatch_count"
    ]
    for old, new in zip(
        literal["records"], optimized["records"], strict=True
    ):
        assert old["boundary"] == new["boundary"]
        assert abs(
            old["exact_power"]["decimal"]
            - new["exact_power"]["decimal"]
        ) < 1e-15
