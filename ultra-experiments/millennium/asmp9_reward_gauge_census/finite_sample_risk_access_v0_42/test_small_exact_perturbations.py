"""Exact small-registry checks of the v0.42 perturbation theorem."""

from fractions import Fraction as Q
from pathlib import Path
import sys


BASE = Path(__file__).resolve().parent
V41 = BASE.parent / "sequential_risk_access_v0_41"
if str(V41) not in sys.path:
    sys.path.insert(0, str(V41))

from confirmation import noisy_binary_query  # noqa: E402
from sequential_access import (  # noqa: E402
    adaptive_upper_generators,
    classification_problem,
    directed_upper_deficiency,
    nonadaptive_upper_generators,
)


def _deficiency(error: Q, horizon: int, adaptive: bool) -> Q:
    query = noisy_binary_query("q", (0, 1), error)
    problem = classification_problem(2)
    compiler = (
        adaptive_upper_generators
        if adaptive
        else nonadaptive_upper_generators
    )
    generators = compiler((query,), problem, horizon)
    return directed_upper_deficiency(
        generators,
        ((Q(0), Q(0)),),
    ).epsilon


def test_exact_deficiency_perturbations_obey_policy_uniform_bound():
    errors = (Q(1, 10), Q(1, 5), Q(3, 10))
    for horizon in (0, 1, 2):
        for adaptive in (False, True):
            for true_error in errors:
                for empirical_error in errors:
                    true_value = _deficiency(
                        true_error, horizon, adaptive
                    )
                    empirical_value = _deficiency(
                        empirical_error, horizon, adaptive
                    )
                    radius = min(
                        Q(1),
                        horizon
                        * abs(true_error - empirical_error),
                    )
                    assert (
                        abs(true_value - empirical_value) <= radius
                    )
