from fractions import Fraction

from experiment import fraction_certificate, run_fresh_liveness, run_power_calibration


def test_fraction_certificate_preserves_small_exact_values() -> None:
    certificate = fraction_certificate(Fraction(3, 7))
    assert certificate["fraction"] == "3/7"
    assert certificate["decimal"] == 3 / 7


def test_fresh_liveness_small_cycle_has_both_statuses() -> None:
    result = run_fresh_liveness(
        [
            {
                "name": "test_cycle",
                "node_count": 3,
                "edges": [[0, 1], [1, 2], [2, 0]],
                "expected_beta1": 1,
                "trials_per_edge": [1, 2],
            }
        ]
    )
    assert result["graph_arithmetic_mismatch_count"] == 0
    assert result["gauge_factor_mismatch_count"] == 0
    assert result["normalized_law_mismatch_count"] == 0
    assert result["missing_full_rank_graph_count"] == 0
    assert result["missing_deficient_graph_count"] == 0


def test_power_calibration_checks_exact_formula_and_size() -> None:
    result = run_power_calibration(
        {
            "alpha": "1/20",
            "lower_power": "1/20",
            "upper_power": "1/1",
            "formula_trials_per_edge": 2,
            "cells": [
                {
                    "cycle_length": 3,
                    "odds_ratio": "2/1",
                    "trials_per_edge": 5,
                }
            ],
        }
    )
    assert result["formula_mismatch_count"] == 0
    assert result["likelihood_ratio_mismatch_count"] == 0
    assert result["size_mismatch_count"] == 0
    assert result["nonpositive_power_gain_count"] == 0
    assert result["power_band_mismatch_count"] == 0
