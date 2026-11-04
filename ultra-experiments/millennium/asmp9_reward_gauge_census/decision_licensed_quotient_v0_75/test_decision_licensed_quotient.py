from __future__ import annotations

import sympy as sp

from decision_licensed_quotient import (
    analyze_decision_licensed_quotient,
    matrix,
    occupancy_difference_matrix,
)


def test_decision_gauge_is_derived_from_policy_occupancies() -> None:
    occupancies = matrix(((1, 0), (0, 1)))
    decision = occupancy_difference_matrix(occupancies)
    assert decision == matrix(((-1, 1),))
    analysis = analyze_decision_licensed_quotient(
        occupancies,
        matrix(((-1, 1),)),
        sp.zeros(1, 0),
    )
    assert analysis.gauge_basis == matrix(((1,), (1,)))
    assert analysis.decision_rank == 1
    assert analysis.gauge_dimension == 1


def test_contrast_measurement_exactly_identifies_all_policy_margins() -> None:
    analysis = analyze_decision_licensed_quotient(
        matrix(((1, 0), (0, 1))),
        matrix(((-1, 1),)),
        sp.zeros(1, 0),
    )
    assert analysis.exactly_identifies_decision_quotient
    assert analysis.effective_measurement_rank == 1
    assert analysis.non_gauge_witness is None


def test_full_measurement_with_common_output_nuisance_is_exact() -> None:
    analysis = analyze_decision_licensed_quotient(
        matrix(((1, 0), (0, 1))),
        sp.eye(2),
        matrix(((1,), (1,))),
    )
    assert analysis.exactly_identifies_decision_quotient
    assert analysis.effective_measurement_rank == 1


def test_gauge_only_measurement_emits_non_gauge_witness() -> None:
    analysis = analyze_decision_licensed_quotient(
        matrix(((1, 0), (0, 1))),
        matrix(((1, 1),)),
        sp.zeros(1, 0),
    )
    assert not analysis.exactly_identifies_decision_quotient
    assert analysis.effective_measurement_rank == 0
    assert analysis.non_gauge_witness is not None
    assert not (analysis.decision_matrix * analysis.non_gauge_witness).is_zero_matrix


def test_three_policy_full_rank_decision_has_no_additive_gauge() -> None:
    analysis = analyze_decision_licensed_quotient(
        matrix(((0, 0), (1, 0), (0, 1))),
        sp.eye(2),
        sp.zeros(2, 0),
    )
    assert analysis.decision_rank == 2
    assert analysis.gauge_dimension == 0
    assert analysis.exactly_identifies_decision_quotient


def test_duplicate_policy_does_not_change_decision_gauge() -> None:
    base = analyze_decision_licensed_quotient(
        matrix(((1, 0), (0, 1))),
        matrix(((-1, 1),)),
        sp.zeros(1, 0),
    )
    duplicate = analyze_decision_licensed_quotient(
        matrix(((1, 0), (0, 1), (1, 0))),
        matrix(((-1, 1),)),
        sp.zeros(1, 0),
    )
    assert duplicate.decision_rank == base.decision_rank
    assert duplicate.gauge_dimension == base.gauge_dimension
    assert duplicate.exactly_identifies_decision_quotient


def test_dimension_mismatch_is_rejected() -> None:
    try:
        analyze_decision_licensed_quotient(
            matrix(((1, 0), (0, 1))),
            matrix(((1, 0, 0),)),
            sp.zeros(1, 0),
        )
    except ValueError as error:
        assert "different dimensions" in str(error)
    else:
        raise AssertionError("dimension mismatch was accepted")
