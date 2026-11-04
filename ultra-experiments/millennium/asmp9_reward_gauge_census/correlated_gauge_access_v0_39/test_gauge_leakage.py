from fractions import Fraction as Q

from gauge_leakage import (
    certify_gauge_leakage,
    gauge_leakage_radius,
    intervene_on_gauge,
)


def test_half_range_is_exact_gauge_leakage_radius():
    probabilities = (Q(4, 5), Q(1, 5), Q(1, 2))
    certificate = certify_gauge_leakage(probabilities)
    assert certificate.analytic_radius == Q(3, 10)
    assert certificate.decision_relative_radius == Q(3, 10)
    assert certificate.ordinary_radius == Q(3, 10)
    assert certificate.reverse_decision_relative == 0
    assert certificate.reverse_ordinary == 0


def test_target_independence_is_exact_ancillarity_condition():
    probabilities = (Q(2, 3),) * 3
    certificate = certify_gauge_leakage(probabilities)
    assert certificate.analytic_radius == 0
    assert certificate.decision_relative_radius == 0
    assert certificate.ordinary_radius == 0


def test_intervention_erases_observational_gauge_leakage():
    observational = (Q(4, 5), Q(1, 5), Q(1, 2))
    intervened = intervene_on_gauge(observational, Q(2, 7))
    assert observational != intervened
    assert intervened == (Q(2, 7),) * 3
    assert gauge_leakage_radius(intervened) == 0
    assert certify_gauge_leakage(intervened).decision_relative_radius == 0
