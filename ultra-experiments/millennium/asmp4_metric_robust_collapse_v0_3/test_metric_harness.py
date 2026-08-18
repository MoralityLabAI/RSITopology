from __future__ import annotations

import math

from metric_harness import (
    bilateral_copy_metric_report,
    bilateral_fixed_fifo_delay_report,
    comb_language,
    comb_metric_gap,
    exhaustive_binary_language_census,
    one_sided_normal_form_gap_report,
    plan_index_language,
    prefix_rounding_language,
    prefix_rounding_separation_report,
    skew_language,
    skew_metric_separation_report,
    transcript_tree_metrics,
    verification_payload,
)


def test_comb_has_linear_language_and_exponential_worst_path_branching():
    for horizon in range(1, 9):
        metrics = transcript_tree_metrics(comb_language(horizon))
        assert metrics["language_count"] == horizon + 1
        assert metrics["branch_product"] == 2**horizon
        assert metrics["language_bits"] == math.log2(horizon + 1)
        assert metrics["branch_bits"] == horizon


def test_every_binary_language_through_horizon_four_obeys_tree_domination():
    census = exhaustive_binary_language_census()
    assert census["checked_languages"] == 65809
    assert census["horizon_histogram"] == {
        "0": 1,
        "1": 3,
        "2": 15,
        "3": 255,
        "4": 65535,
    }
    assert census["pass"] is True


def test_symbol_relabeling_and_bilateral_copy_preserve_metrics():
    assert bilateral_copy_metric_report()["pass"] is True


def test_one_sided_normal_form_restrictions_produce_both_strict_gap_directions():
    for horizon in range(2, 9):
        plan = transcript_tree_metrics(plan_index_language(horizon))
        comb = transcript_tree_metrics(comb_language(horizon))
        assert plan["language_count"] == comb["language_count"] == horizon + 1
        assert plan["branch_product"] == horizon + 1
        assert comb["branch_product"] == 2**horizon
        assert comb["branch_bits"] > plan["branch_bits"]
    report = one_sided_normal_form_gap_report()
    assert report["sensor_computation_restriction"] == {
        "read_branch_bits": 2.0,
        "write_branch_bits": 1.0,
        "strict_read_gap": True,
    }
    assert report["pass"] is True


def test_bilateral_normal_forms_preserve_trees_and_plant_inputs_with_fifo_delays():
    report = bilateral_fixed_fifo_delay_report()
    assert len(report["rows"]) == 96
    assert report["pass"] is True


def test_skew_tree_separates_terminal_prefix_and_uniform_branch_costs():
    for depth in range(2, 9):
        metrics = transcript_tree_metrics(skew_language(depth))
        assert metrics["language_count"] == 2**depth + 2
        assert metrics["prefix_worst_bits"] == depth + 1
        assert metrics["branch_bits"] == depth + math.log2(3)
        assert (
            metrics["language_bits"]
            < metrics["prefix_worst_bits"]
            < metrics["branch_bits"]
        )
    assert skew_metric_separation_report()["pass"] is True


def test_sequential_prefix_rounding_gives_the_opposite_three_metric_order():
    metrics = transcript_tree_metrics(prefix_rounding_language())
    assert metrics["language_bits"] == 2
    assert metrics["branch_bits"] == math.log2(6)
    assert metrics["prefix_worst_bits"] == 3
    assert (
        metrics["language_bits"] < metrics["branch_bits"] < metrics["prefix_worst_bits"]
    )
    assert prefix_rounding_separation_report()["pass"] is True


def test_comb_asymptotics_and_verification_gates():
    gap = comb_metric_gap()
    assert gap["rows"][-1]["language_rate"] < 0.06
    assert gap["rows"][-1]["branch_rate"] == 1.0
    payload = verification_payload()
    assert payload["pass"] is True
    assert all(payload["gates"].values())
