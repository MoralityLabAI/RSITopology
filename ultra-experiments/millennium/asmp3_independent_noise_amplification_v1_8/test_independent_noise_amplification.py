from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from build_release_manifest import verify_manifest
from independent_noise_amplification import (
    ETA_REGISTRY,
    amplification_row,
    bayes_error,
    build_result,
    enumerated_total_variation,
    odd_step_gain,
    response_probability,
    verifier_value,
)
from verify_independent_noise_amplification import verify


Q = Fraction
HERE = Path(__file__).resolve().parent


def test_invalid_depth_and_rate_are_rejected() -> None:
    for depth, eta in ((0, Q(1, 5)), (3, Q(-1, 5)), (3, Q(3, 5))):
        with pytest.raises(ValueError):
            bayes_error(depth, eta)
    with pytest.raises(ValueError):
        odd_step_gain(0, Q(1, 5))


def test_response_distributions_normalize() -> None:
    for depth in range(1, 9):
        for eta in (Q(1, 5), Q(1, 3)):
            for truth in (0, 1):
                total = sum(
                    (
                        response_probability(format(index, f"0{depth}b"), truth, eta)
                        for index in range(1 << depth)
                    ),
                    Q(0),
                )
                assert total == 1


def test_depth_one_and_two_do_not_amplify() -> None:
    for eta in ETA_REGISTRY:
        assert bayes_error(1, eta) == eta
        assert bayes_error(2, eta) == eta
        assert verifier_value(1, eta) == verifier_value(2, eta) == 1 - 2 * eta


def test_even_depth_equals_preceding_odd_depth() -> None:
    for eta in ETA_REGISTRY:
        for m in range(1, 17):
            assert bayes_error(2 * m, eta) == bayes_error(2 * m - 1, eta)


def test_odd_step_gain_formula_is_exact_and_positive() -> None:
    for eta in ETA_REGISTRY:
        for m in range(1, 17):
            observed = bayes_error(2 * m, eta) - bayes_error(2 * m + 1, eta)
            assert observed == odd_step_gain(m, eta)
            assert observed > 0


def test_word_enumeration_matches_binomial_total_variation() -> None:
    for eta in (Q(1, 5), Q(1, 3), Q(2, 5)):
        for depth in range(1, 9):
            assert enumerated_total_variation(depth, eta) == verifier_value(depth, eta)


def test_error_is_monotone_in_legal_iid_rate() -> None:
    for depth in range(1, 17):
        rates = tuple(Q(step, 20) for step in range(11))
        errors = tuple(bayes_error(depth, rate) for rate in rates)
        assert all(left <= right for left, right in zip(errors, errors[1:]))


def test_bhattacharyya_squared_bound_is_exactly_checked() -> None:
    for eta in ETA_REGISTRY:
        for depth in range(1, 65):
            row = amplification_row(depth, eta)
            assert row["bound_holds"]
            assert Q(row["bayes_error_squared"]) <= Q(
                row["bhattacharyya_squared_upper_bound"]
            )


def test_independence_strictly_beats_persistent_noise_after_depth_two() -> None:
    for eta in ETA_REGISTRY:
        baseline = 1 - 2 * eta
        for depth in range(3, 17):
            assert verifier_value(depth, eta) > baseline


def test_exact_correlation_class_witness() -> None:
    row = amplification_row(9, Q(1, 5))
    assert row["bayes_error"] == "7649/390625"
    assert row["value"] == "375327/390625"
    assert row["persistent_correlated_value"] == "3/5"


def test_registry_and_all_producer_gates_pass() -> None:
    result = build_result()
    assert len(result["amplification_rows"]) == 448
    assert len(result["word_enumeration_audit"]) == 30
    assert len(result["rate_adversary_audit"]) == 112
    assert len(result["parity_recurrence_audit"]) == 217
    assert result["certified"]
    assert len(result["gates"]) == 9
    assert all(result["gates"].values())


def test_clean_room_checker_passes() -> None:
    result = verify()
    assert result["passed"]
    assert result["check_count"] == 8
    assert all(result["checks"].values())


def test_compositional_and_correlation_boundaries_are_explicit() -> None:
    theorem = (HERE / "INDEPENDENT_NOISE_AMPLIFICATION_THEOREM_v1_8.md").read_text(
        encoding="utf-8"
    )
    audit = (HERE / "COMPLETION_AUDIT_v1_8.md").read_text(encoding="utf-8")
    assert "Correlation-class separation" in theorem
    assert "Query-cost and compositional boundary" in theorem
    assert "transcript-conditional independence" in audit


def test_release_manifest_matches() -> None:
    assert verify_manifest()
