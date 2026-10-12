from fractions import Fraction as Q

from randomized_ordering import minimal_randomization_gain_witness
from verify_theorems_v0_51 import (
    independent_certificate_checks,
    monotone_binary_tables,
)


def test_three_outcome_universe_count():
    assert len(monotone_binary_tables(3)) == 19


def test_independent_checks_accept_minimal_certificate():
    certificate = minimal_randomization_gain_witness()
    checks = independent_certificate_checks(certificate)
    assert all(checks.values())


def test_independent_zero_support_count_matches_minimal_game():
    certificate = minimal_randomization_gain_witness()
    matrix = certificate.payoff_matrix
    assert sum(all(entry == 0 for entry in row) for row in matrix) == 0
    assert certificate.randomized_value > 0
