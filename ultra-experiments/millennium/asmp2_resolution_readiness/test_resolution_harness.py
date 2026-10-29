from fractions import Fraction

from resolution_harness import (
    DEPLOYMENT_POINT,
    SAFETY_THRESHOLD,
    SOURCES,
    build_result,
    closure_audit,
    exact_countermodel,
    g,
    g_prime,
    joint_pmf,
    p_y,
)


def test_source_worlds_are_exactly_indistinguishable_to_first_order() -> None:
    for theta in SOURCES:
        assert g(theta) == 0
        assert g_prime(theta) == 0
        assert joint_pmf(-1, theta) == joint_pmf(1, theta)


def test_full_local_shift_information_and_finite_curvature() -> None:
    witness = exact_countermodel()
    assert witness["local_certificate_data"]["fisher_total"] == "5/64"
    assert witness["local_certificate_data"]["factor_through_z_score"] == "1/2"
    assert witness["regularity"]["risk_curvature_bound"] == "193/36"
    assert witness["all_gates_passed"]


def test_global_deployment_conflict_is_exact() -> None:
    minus = p_y(-1, DEPLOYMENT_POINT)
    plus = p_y(1, DEPLOYMENT_POINT)
    assert minus == Fraction(7, 16)
    assert plus == Fraction(11, 16)
    assert minus < SAFETY_THRESHOLD < plus
    assert plus - minus == Fraction(1, 4)
    witness = exact_countermodel()
    assert witness["deployment"]["uniform_success_probability_upper_bound"] == "0/1"


def test_authoritative_closure_audit_stops() -> None:
    audit = closure_audit()
    assert audit["decision"] == "stop_definition_not_closed"
    assert audit["all_authoritative_status_checks_passed"]
    assert audit["all_placeholder_checks_passed"]
    assert audit["missing_binding_count"] == 15


def test_result_is_a_scoped_stop_not_a_resolution_claim() -> None:
    result = build_result()
    assert result["stop_is_supported"]
    assert (
        result["decision"]
        == "stop_full_resolution_attempt_pending_successor_definition"
    )
    assert result["problem_resolved"] is False
