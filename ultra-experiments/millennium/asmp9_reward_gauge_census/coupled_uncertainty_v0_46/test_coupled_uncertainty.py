from __future__ import annotations

from decimal import Decimal, localcontext
from fractions import Fraction as Q
from pathlib import Path
import sys

import pytest


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from coupled_uncertainty import (  # noqa: E402
    _registered_tree_classification_upper,
    blackwell_postprocessing_flip,
    ceil_grid,
    certified_minimax_classification,
    exact_channel_deficiency,
    exp_neg_fraction_bounds,
    fast_prior_lower_bound,
    flip_probability_bounds,
    floor_grid,
    monomial_values,
    optimize_coupled_minimax_classification,
    optimize_coupled_root_group,
    prior_lower_bound,
    product_box_control,
    rational_simplex,
    registered_tree_bounds,
    symbolic_classification_policies,
    symmetric_flip_queries,
)


def test_rational_exponential_bracket_contains_decimal_reference():
    for value in (Q(1, 10), Q(1), Q(5)):
        lower, upper = exp_neg_fraction_bounds(value)
        with localcontext() as context:
            context.prec = 80
            reference = (-Decimal(value.numerator) / value.denominator).exp()
        assert Decimal(lower.numerator) / lower.denominator <= reference
        assert reference <= Decimal(upper.numerator) / upper.denominator
        assert upper - lower <= Q(1, 10**15)


def test_grid_rounding_is_outward():
    value = Q(1, 3)
    assert floor_grid(value, 3) == Q(333, 1000)
    assert ceil_grid(value, 3) == Q(167, 500)


@pytest.mark.parametrize("samples", (1, 17, 20, 26, 58))
def test_flip_probability_bounds_are_narrow_and_ordered(samples):
    bounds = flip_probability_bounds(samples)
    assert Q(0) <= bounds.lower <= bounds.upper <= Q(1, 2)
    assert bounds.upper - bounds.lower <= Q(1, 10**12)


def test_symbolic_policy_library_is_frozen_and_degree_two():
    policies = symbolic_classification_policies()
    assert policies.shape == (3748, 4, 10)
    assert not policies.flags.writeable
    assert monomial_values((Q(1, 4), Q(1, 3), Q(1, 5)))[0] == 1


@pytest.mark.parametrize(
    "probabilities",
    (
        (Q(0), Q(0), Q(0)),
        (Q(1, 4), Q(1, 4), Q(1, 4)),
        (Q(1, 4), Q(1, 3), Q(1, 3)),
    ),
)
def test_symbolic_minimax_matches_inherited_exact_compiler(probabilities):
    inherited = exact_channel_deficiency(
        probabilities, "branch_classification"
    )
    symbolic = certified_minimax_classification(probabilities)["risk"]
    assert symbolic == inherited


def test_mixed_reliability_requires_full_adaptive_minimax_game():
    probabilities = (Q(1, 4), Q(1, 3), Q(1, 5))
    exact = certified_minimax_classification(probabilities)
    assert exact["risk"] == Q(307, 647)
    assert exact["risk"] < _registered_tree_classification_upper(
        probabilities
    )


def test_integer_prior_bound_matches_fraction_reference():
    probabilities = (Q(1, 4), Q(1, 3), Q(1, 5))
    prior = rational_simplex(
        (
            0.37248840803709427,
            0.37248840803709427,
            0.14786192684183413,
            0.10716125708397733,
        )
    )
    assert fast_prior_lower_bound(
        probabilities, prior
    ) == prior_lower_bound(probabilities, prior)


def test_small_budget_global_optima_are_uniquely_certified():
    classification = optimize_coupled_minimax_classification(18)
    group = optimize_coupled_root_group(18)
    assert classification["candidate"].allocation == (16, 1, 1)
    assert classification["unique_certified"]
    assert classification["certified_unique_gap"] > 0
    assert group["candidate"][0] == (16, 1, 1)
    assert group["unique_certified"]
    assert group["certified_unique_gap"] > 0


def test_blackwell_postprocessing_composes_symmetric_flips():
    lower = Q(1, 5)
    upper = Q(1, 3)
    extra = blackwell_postprocessing_flip(lower, upper)
    assert lower + extra - 2 * lower * extra == upper
    assert Q(0) <= extra <= Q(1, 2)


def test_product_box_control_is_exact():
    control = product_box_control()
    assert control["vertices"] == 16
    assert control["match"]


def test_exact_group_channel_at_registered_point():
    probabilities = (Q(1, 4), Q(1, 3), Q(1, 3))
    assert exact_channel_deficiency(
        probabilities, "root_group"
    ) == Q(1, 4)


@pytest.mark.parametrize(
    "call,args",
    (
        (exp_neg_fraction_bounds, (Q(-1),)),
        (registered_tree_bounds, ((20, 20), "root_group")),
        (symmetric_flip_queries, ((Q(3, 4), Q(0), Q(0)),)),
        (blackwell_postprocessing_flip, (Q(1, 3), Q(1, 4))),
    ),
)
def test_invalid_inputs_fail_closed(call, args):
    with pytest.raises(ValueError):
        call(*args)
