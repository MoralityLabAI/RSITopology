from fractions import Fraction as Q
import math

import pytest

from finite_sample_access import (
    DeficiencyInterval,
    access_decision,
    burned_centered_calibration,
    deficiency_interval,
    loss_spans,
    policy_risk_radii,
    required_samples_per_target_shared_binary,
    shared_binary_flip_radius,
    simultaneous_weissman_radii,
    weissman_tv_radius,
)


def test_weissman_radius_decreases_with_samples():
    assert weissman_tv_radius(3, 10000, 0.01) < weissman_tv_radius(
        3, 1000, 0.01
    )


def test_high_precision_radius_is_outward_from_direct_float_formula():
    radius = shared_binary_flip_radius(3, 4, 4800, 0.05)
    direct = math.sqrt(math.log(120.0) / (2.0 * 4 * 4800))
    assert radius >= direct


def test_singleton_outcome_channel_has_zero_radius():
    assert weissman_tv_radius(1, 10, 0.01) == 0.0


def test_simultaneous_cell_universe_is_exact():
    radii = simultaneous_weissman_radii(
        {"a": 2, "b": 3},
        {"a": 1000, "b": 2000},
        alpha=0.05,
    )
    assert set(radii) == {"a", "b"}
    assert radii["a"] > 0


def test_simultaneous_radii_reject_mismatched_cell_universes():
    with pytest.raises(
        ValueError, match="outcome and sample cell universes differ"
    ):
        simultaneous_weissman_radii(
            {"a": 2},
            {"b": 1000},
            alpha=0.05,
        )


def test_loss_spans_remove_targetwise_constants():
    assert loss_spans(
        (
            (Q(5), Q(7), Q(6)),
            (Q(3), Q(3), Q(3)),
        )
    ) == (Q(2), Q(0))


def test_exact_zero_span_stays_exactly_zero():
    result = policy_risk_radii(
        ((Q(4), Q(4)),),
        2,
        ("q0",),
        {(0, "q0"): 0.2},
    )
    assert result == (0.0,)


def test_policy_radius_scales_with_horizon_and_loss_span():
    losses = ((Q(0), Q(1)), (Q(0), Q(2)))
    radii = {
        (0, "q0"): 0.01,
        (0, "q1"): 0.02,
        (1, "q0"): 0.03,
        (1, "q1"): 0.01,
    }
    result = policy_risk_radii(losses, 2, ("q0", "q1"), radii)
    assert result[0] > 0.04
    assert result[0] < 0.040000000000001
    assert result[1] > 0.12
    assert result[1] < 0.120000000000001


def test_deficiency_interval_adds_source_and_reference_radii():
    interval = deficiency_interval(
        0.4,
        (0.01, 0.02),
        (0.03, 0.01),
        alpha=0.05,
    )
    assert interval.half_width > 0.04
    assert interval.half_width < 0.040000000000001
    assert interval.lower < 0.36
    assert interval.upper > 0.44


def test_deficiency_interval_clips_to_declared_range():
    interval = deficiency_interval(
        0.01,
        (0.2,),
        (0.0,),
        alpha=0.05,
    )
    assert interval.lower == 0.0
    assert interval.upper > 0.21


def test_gate_boundaries_are_strict_and_equality_is_inconclusive():
    interval = DeficiencyInterval(0.4, 0.3, 0.5, 0.1, 0.95)
    assert access_decision(interval, 0.5) == "inconclusive"
    assert access_decision(
        DeficiencyInterval(0.3, 0.2, 0.4, 0.1, 0.95), 0.5
    ) == "pass"
    assert access_decision(
        DeficiencyInterval(0.7, 0.6, 0.8, 0.1, 0.95), 0.5
    ) == "fail"


def test_shared_binary_sample_floor_is_minimal():
    floor = required_samples_per_target_shared_binary(
        gap=0.02,
        horizon=2,
        query_count=3,
        targets=4,
        alpha=0.05,
    )
    at_floor = 2 * shared_binary_flip_radius(3, 4, floor, 0.05)
    before = 2 * shared_binary_flip_radius(3, 4, floor - 1, 0.05)
    assert at_floor < 0.02
    assert before >= 0.02


def test_centered_calibration_has_registered_convergence_pattern():
    result = burned_centered_calibration()
    states = [
        (
            row["arms"]["adaptive"]["decision"],
            row["arms"]["open_loop"]["decision"],
        )
        for row in result["rows"]
    ]
    assert states == [
        ("inconclusive", "inconclusive"),
        ("pass", "inconclusive"),
        ("pass", "fail"),
    ]


def test_two_estimated_sides_require_more_samples():
    one = required_samples_per_target_shared_binary(
        0.03, 2, 3, 4, 0.05, estimated_sides=1
    )
    two = required_samples_per_target_shared_binary(
        0.03, 2, 3, 4, 0.05, estimated_sides=2
    )
    assert two > one
    at_floor = 4 * shared_binary_flip_radius(6, 4, two, 0.05)
    before = 4 * shared_binary_flip_radius(6, 4, two - 1, 0.05)
    assert at_floor < 0.03
    assert before >= 0.03
