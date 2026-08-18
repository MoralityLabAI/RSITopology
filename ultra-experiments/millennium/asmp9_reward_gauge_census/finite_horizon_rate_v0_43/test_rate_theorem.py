from __future__ import annotations

from fractions import Fraction as Q
from pathlib import Path
import sys

import pytest


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
V41 = PARENT / "sequential_risk_access_v0_41"
for path in (HERE, V41):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from rate_theorem import (  # noqa: E402
    adaptive_kl_risk_radius,
    bernoulli_chi_square,
    block_deficiency_interval,
    block_hoeffding_radius,
    no_linear_horizon_witness_ratio,
    required_block_samples,
    sentinel_deficiency,
    sentinel_derivative_magnitude,
    two_point_certificate,
)
from sequential_access import (  # noqa: E402
    QueryChannel,
    adaptive_upper_generators,
    classification_problem,
    directed_upper_deficiency,
)


def sentinel_query(p: Q) -> QueryChannel:
    return QueryChannel(
        "sentinel",
        (
            (Q(1), Q(0)),
            (Q(1) - p, p),
        ),
    )


@pytest.mark.parametrize("horizon", range(1, 7))
@pytest.mark.parametrize("p", (Q(0), Q(1, 8), Q(1, 4), Q(1, 3), Q(1)))
def test_closed_form_matches_exact_policy_compiler(horizon: int, p: Q):
    source = adaptive_upper_generators(
        (sentinel_query(p),),
        classification_problem(2),
        horizon,
    )
    reference = ((Q(0), Q(0)),)
    exact = directed_upper_deficiency(source, reference).epsilon
    assert exact == sentinel_deficiency(horizon, p)


@pytest.mark.parametrize("horizon", (2, 3, 4, 8, 16, 32, 64, 128))
@pytest.mark.parametrize("epsilon", (Q(1, 32), Q(1, 16), Q(1, 8), Q(1, 4)))
def test_two_point_certificate_is_exact(horizon: int, epsilon: Q):
    certificate = two_point_certificate(horizon, epsilon)
    assert epsilon / 16 <= certificate.deficiency_gap <= epsilon
    assert (
        certificate.chi_square_upper_on_kl
        <= 4 * epsilon**2 / horizon
    )
    assert certificate.le_cam_sample_floor >= 1


def test_derivative_has_horizon_order_on_registered_window():
    for horizon in (2, 3, 4, 8, 16, 32, 64, 128):
        for numerator in range(2, 7):
            p = Q(numerator, 8 * horizon)
            derivative = sentinel_derivative_magnitude(horizon, p)
            assert derivative >= Q(horizon, 16)
            assert derivative <= horizon


def test_exact_chi_square_orientation_and_boundary():
    assert bernoulli_chi_square(Q(1, 4), Q(1, 2)) == Q(1, 4)
    with pytest.raises(ValueError):
        bernoulli_chi_square(Q(0), Q(0))


def test_chain_rule_pinsker_radius_and_no_linear_witness():
    assert adaptive_kl_risk_radius(0, 1.0) == 0.0
    assert adaptive_kl_risk_radius(8, 0.01) == pytest.approx(0.2)
    ratios = [
        no_linear_horizon_witness_ratio(horizon, 4.0)
        for horizon in (2, 8, 32, 128)
    ]
    assert ratios == sorted(ratios, reverse=True)
    assert ratios[-1] < ratios[0] / 4


def test_block_rate_is_linear_in_horizon():
    rows = [
        required_block_samples(horizon, 1 / 16, 0.05)
        for horizon in (8, 16, 32, 64, 128)
    ]
    assert len({row["blocks"] for row in rows}) == 1
    assert [row["raw_samples"] for row in rows] == [
        row["horizon"] * row["blocks"] for row in rows
    ]
    assert len(
        {
            round(row["normalized_samples_gap_squared_over_h"], 14)
            for row in rows
        }
    ) == 1


def test_block_interval_contains_transformed_event_interval():
    result = block_deficiency_interval(70, 100, 0.05)
    assert 0 <= result["lower"] <= result["point"] <= result["upper"] <= 0.5
    assert result["all_zero_probability_radius"] == block_hoeffding_radius(
        100, 0.05
    )


@pytest.mark.parametrize(
    "call,args",
    (
        (sentinel_deficiency, (0, Q(1, 2))),
        (sentinel_deficiency, (1, Q(2))),
        (two_point_certificate, (1, Q(1, 8))),
        (two_point_certificate, (2, Q(1, 2))),
        (adaptive_kl_risk_radius, (1, -1.0)),
        (block_hoeffding_radius, (0, 0.05)),
        (required_block_samples, (2, 0.0, 0.05)),
        (block_deficiency_interval, (2, 1, 0.05)),
    ),
)
def test_invalid_inputs_fail_closed(call, args):
    with pytest.raises(ValueError):
        call(*args)
