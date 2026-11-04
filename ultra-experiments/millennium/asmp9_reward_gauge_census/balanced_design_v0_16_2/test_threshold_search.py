from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "balanced_design_v0_16"
sys.path.insert(0, str(BASE))

from experiment import minimal_total_trials  # noqa: E402
from threshold_search import logarithmic_total_threshold


def test_logarithmic_search_matches_burned_linear_cells() -> None:
    for length in (3, 5, 8):
        for epsilon in (
            Fraction(1, 20),
            Fraction(1, 8),
            Fraction(1, 4),
        ):
            for target in (
                Fraction(4, 5),
                Fraction(19, 20),
                Fraction(99, 100),
            ):
                expected = minimal_total_trials(
                    length, epsilon, target
                )
                record = logarithmic_total_threshold(
                    length, epsilon, target
                )
                assert record is not None
                assert record["minimum_total_trials"] == expected
                assert record["straddles"]
                assert record["within_evaluation_bound"]
                assert record["traversed_values_monotone"]
                assert (
                    len(record["evaluated_points"])
                    == record["exact_evaluation_count"]
                )


def test_zero_interior_is_unavailable() -> None:
    assert (
        logarithmic_total_threshold(
            5, Fraction(0), Fraction(9, 10)
        )
        is None
    )


def test_search_uses_logarithmically_many_exact_evaluations() -> None:
    record = logarithmic_total_threshold(
        11, Fraction(1, 50), Fraction(999, 1000)
    )
    assert record is not None
    assert record["minimum_total_trials"] > 1000
    assert record["exact_evaluation_count"] < 40
    assert record["within_evaluation_bound"]
