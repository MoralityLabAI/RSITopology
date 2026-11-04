from fractions import Fraction

from critical_rho import (
    LOWER,
    THRESHOLD_POLYNOMIAL,
    UPPER,
    characterization,
    evaluate,
    polynomial_residual,
    root_count,
)
from frontier import ERROR_LIMIT, RHO_GRID, majority_error


def test_threshold_polynomial_identity_is_exact() -> None:
    for rho in tuple(RHO_GRID) + (LOWER, UPPER):
        assert majority_error(9, 1, rho) - ERROR_LIMIT == polynomial_residual(rho)


def test_unique_root_on_physical_interval() -> None:
    assert root_count(THRESHOLD_POLYNOMIAL, Fraction(0), Fraction(1)) == 1


def test_twelve_decimal_isolating_interval() -> None:
    assert UPPER - LOWER == Fraction(1, 10**12)
    assert root_count(THRESHOLD_POLYNOMIAL, LOWER, UPPER) == 1
    assert evaluate(THRESHOLD_POLYNOMIAL, LOWER) > 0
    assert evaluate(THRESHOLD_POLYNOMIAL, UPPER) < 0


def test_characterization_is_certified() -> None:
    result = characterization()
    assert result["certified"] is True
    assert "pairwise rho alone" in result["claim_boundary"]
    assert result["configuration"]["parameterization"].startswith("kappa=")
