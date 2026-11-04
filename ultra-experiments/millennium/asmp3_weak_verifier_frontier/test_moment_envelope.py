from fractions import Fraction

from moment_envelope import (
    AUDIT_GRID,
    COMMON_SHOCK,
    LIMIT,
    LOWER_BREAK,
    RHO_ZERO_FAIL,
    UNIVERSAL_FAIL_BOUNDARY,
    build_result,
    everywhere_failing_tail,
    everywhere_failing_witness,
    exact_vertex_envelope,
    lower_dual,
    minimum_tail_value,
    minimum_witness,
    rho_zero_upper_dual,
    tail,
    validate_law,
)


def test_lower_dual_and_sharp_witness() -> None:
    assert all(lower_dual(s) <= (1 if s >= 5 else 0) for s in range(10))
    for rho in AUDIT_GRID:
        law = minimum_witness(rho)
        validate_law(law, rho)
        assert tail(law) == minimum_tail_value(rho)


def test_rho_zero_upper_dual_is_sharp() -> None:
    assert all(rho_zero_upper_dual(s) >= (1 if s >= 5 else 0) for s in range(10))
    validate_law(RHO_ZERO_FAIL, Fraction(0))
    assert tail(RHO_ZERO_FAIL) == Fraction(8, 75)


def test_continuous_failing_family_closes_underdetermined_region() -> None:
    for rho in AUDIT_GRID:
        law = everywhere_failing_witness(rho)
        validate_law(law, rho)
        assert tail(law) == everywhere_failing_tail(rho) > LIMIT


def test_common_shock_endpoint() -> None:
    validate_law(COMMON_SHOCK, Fraction(1))
    assert tail(COMMON_SHOCK) == Fraction(1, 5)


def test_universal_failure_boundary_is_exact() -> None:
    assert minimum_tail_value(LOWER_BREAK) == 0
    assert minimum_tail_value(UNIVERSAL_FAIL_BOUNDARY) == LIMIT
    assert minimum_tail_value(UNIVERSAL_FAIL_BOUNDARY + Fraction(1, 10**6)) > LIMIT


def test_vertex_enumeration_matches_analytic_minimum() -> None:
    for rho in AUDIT_GRID:
        minimum, maximum = exact_vertex_envelope(rho)
        assert minimum == minimum_tail_value(rho)
        assert maximum >= everywhere_failing_tail(rho)


def test_complete_result_certifies() -> None:
    result = build_result()
    assert result["certified"] is True
    assert result["classification"]["universally_pass"] == "empty"

