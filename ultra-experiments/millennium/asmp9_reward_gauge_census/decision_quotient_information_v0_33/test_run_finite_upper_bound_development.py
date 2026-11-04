from __future__ import annotations

import pytest

from .run_finite_upper_bound_development import build_report


def test_finite_upper_report_brackets_native_registry_complexity() -> None:
    report = build_report()
    certificate = report["constructive_upper_certificate"]
    comparison = report["lower_upper_comparison_at_base"]
    assert certificate["total_queries"] == 3324
    assert certificate["return_samples"] == 64
    assert certificate["mechanics_samples"] == 64
    assert certificate["mixture_samples"] == 3196
    assert certificate["uniform_delta_correct_on_registered_registry"]
    assert all(
        row["strictly_below_delta"]
        for row in certificate["errors"].values()
    )
    assert comparison["change_of_measure_expected_query_lower_bound"] == (
        pytest.approx(1538.6941488690566, abs=1e-12)
    )
    assert comparison["upper_to_lower_ratio"] == pytest.approx(
        2.1602733736546322,
        abs=1e-12,
    )
    assert not any(report["claim_boundary"].values())
