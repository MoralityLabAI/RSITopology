from __future__ import annotations

import random

import sympy as sp

from joint_linear_quotient import (
    analyze_joint_quotient,
    canonical_fixtures,
    rational_matrix,
    stability_certificate,
)


def test_full_common_mode_identifies_reward_quotient() -> None:
    analysis = analyze_joint_quotient(
        *canonical_fixtures()["full_common_mode"]
    )
    assert analysis.exactly_identifies_reward_quotient
    assert analysis.target_quotient_dimension == 2
    assert analysis.effective_rank == 2
    assert analysis.joint_kernel_dimension == 1
    assert analysis.visible_gauge_rank == 0
    assert analysis.non_gauge_witness is None


def test_partial_common_mode_has_non_gauge_witness() -> None:
    analysis = analyze_joint_quotient(
        *canonical_fixtures()["partial_common_mode"]
    )
    assert not analysis.exactly_identifies_reward_quotient
    assert analysis.effective_output_dimension == 1
    assert analysis.target_quotient_dimension == 2
    assert analysis.non_gauge_witness is not None
    witness = analysis.non_gauge_witness
    measurement, _, nuisance = canonical_fixtures()["partial_common_mode"]
    assert nuisance.row_join(measurement * witness).rank() == nuisance.rank()


def test_forced_quotient_removes_visible_gauge_leakage() -> None:
    analysis = analyze_joint_quotient(
        *canonical_fixtures()["gauge_leaking_but_complete"]
    )
    assert not analysis.gauge_respecting_before_forced_quotient
    assert analysis.visible_gauge_rank == 1
    assert analysis.exactly_identifies_reward_quotient
    assert analysis.effective_rank == 3


def test_confounded_fixture_reports_expected_kernel_witness() -> None:
    measurement, gauge, nuisance = canonical_fixtures()[
        "non_gauge_confounded"
    ]
    analysis = analyze_joint_quotient(measurement, gauge, nuisance)
    expected = rational_matrix([[-1], [-1], [1], [0]])
    assert not analysis.exactly_identifies_reward_quotient
    joint_output_nuisance = nuisance.row_join(measurement * gauge)
    assert joint_output_nuisance.row_join(
        measurement * expected
    ).rank() == joint_output_nuisance.rank()
    assert analysis.joint_kernel_basis.row_join(expected).rank() == (
        analysis.joint_kernel_basis.rank()
    )


def test_identified_estimands_annihilate_joint_kernel() -> None:
    for measurement, gauge, nuisance in canonical_fixtures().values():
        analysis = analyze_joint_quotient(measurement, gauge, nuisance)
        assert (
            analysis.identified_estimand_basis.T
            * analysis.joint_kernel_basis
        ).is_zero_matrix
        assert analysis.identified_estimand_basis.rank() == (
            analysis.effective_rank
        )


def test_exact_kernel_rank_condition_on_seeded_integer_registry() -> None:
    rng = random.Random(6901)
    for _ in range(128):
        reward_dimension = rng.choice((3, 4, 5))
        measurement_dimension = rng.choice((2, 3, 4, 5, 6))
        measurement = sp.Matrix(
            measurement_dimension,
            reward_dimension,
            [rng.randint(-2, 2) for _ in range(
                measurement_dimension * reward_dimension
            )],
        )
        gauge = sp.Matrix(
            reward_dimension,
            1,
            [rng.randint(-1, 1) for _ in range(reward_dimension)],
        )
        if gauge.is_zero_matrix:
            gauge[0, 0] = 1
        nuisance = sp.Matrix(
            measurement_dimension,
            1,
            [rng.randint(-1, 1) for _ in range(measurement_dimension)],
        )
        if nuisance.is_zero_matrix:
            nuisance[0, 0] = 1

        analysis = analyze_joint_quotient(measurement, gauge, nuisance)
        # Independent construction: solve A h - N u - A G v = 0, then
        # project the expanded nullspace onto its reward coordinates.
        expanded = measurement.row_join(-nuisance).row_join(
            -(measurement * gauge)
        )
        projected = [
            vector[:reward_dimension, :]
            for vector in expanded.nullspace()
            if not vector[:reward_dimension, :].is_zero_matrix
        ]
        projected_kernel = (
            sp.Matrix.hstack(*projected)
            if projected
            else sp.zeros(reward_dimension, 0)
        )
        independent_kernel_dimension = projected_kernel.rank()
        assert (
            analysis.joint_kernel_dimension
            == independent_kernel_dimension
        )
        expected = (
            independent_kernel_dimension == analysis.gauge_rank
        )
        assert analysis.exactly_identifies_reward_quotient == expected


def test_stability_certificate_is_finite_only_when_identified() -> None:
    full = stability_certificate(
        *canonical_fixtures()["full_common_mode"]
    )
    partial = stability_certificate(
        *canonical_fixtures()["partial_common_mode"]
    )
    assert full["sigma_min"] is not None
    assert full["sigma_min"] > 0
    assert full["sharp_inverse_lipschitz_constant"] >= 1
    assert partial["sigma_min"] is None
    assert partial["sharp_inverse_lipschitz_constant"] is None


def test_effective_output_dimension_is_a_sharp_rank_obstruction() -> None:
    for measurement, gauge, nuisance in canonical_fixtures().values():
        analysis = analyze_joint_quotient(measurement, gauge, nuisance)
        assert analysis.effective_rank <= analysis.effective_output_dimension
        assert analysis.effective_rank <= analysis.target_quotient_dimension
        if (
            analysis.effective_output_dimension
            < analysis.target_quotient_dimension
        ):
            assert not analysis.exactly_identifies_reward_quotient
