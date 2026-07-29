from fractions import Fraction

import pytest

from .joint_approximate import (
    build_joint_certificate,
    certificate_support,
    dot,
    evaluate_policy_family,
    identity,
    matmul,
    measurement_from_sources,
    nuisance_projector,
    quotient_analysis_map,
    realized_direction_audit,
    support_witness,
)


def base_fixture():
    design = (
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (2, 1),
        (1, 2),
    )
    context = (
        (1, 0),
        (1, 0),
        (1, 0),
        (0, 1),
        (0, 1),
        (0, 1),
    )
    semantic = (
        (1, -1, 0, 0),
        (1, 0, -1, 0),
        (1, 0, 0, -1),
        (0, 1, -1, 0),
        (0, 1, 0, -1),
        (0, 0, 1, -1),
    )
    return design, context, semantic


def test_context_projection_and_left_inverse_are_exact():
    design, context, _ = base_fixture()
    access = quotient_analysis_map(design, context)
    assert access["available"]
    assert access["projected_rank"] == 2
    assert matmul(access["analysis_map"], design) == identity(2)
    assert matmul(access["analysis_map"], context) == (
        (0, 0),
        (0, 0),
    )


def test_context_confounding_is_unavailable():
    design = ((1,), (1,), (0,), (0,))
    context = ((1, 0), (1, 0), (0, 1), (0, 1))
    access = quotient_analysis_map(design, context)
    assert not access["available"]
    assert access["status"] == "context_confounded"
    assert access["projected_rank"] == 0


def test_projector_is_idempotent_and_annihilates_context():
    _, context, _ = base_fixture()
    projector = nuisance_projector(context)
    assert matmul(projector, projector) == projector
    assert matmul(projector, context) == (
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
    )


def test_joint_realization_is_covered_in_registered_directions():
    design, context, semantic = base_fixture()
    theta = (Fraction(7, 5), Fraction(-4, 5))
    values = measurement_from_sources(
        design,
        context,
        theta,
        (Fraction(2, 7), Fraction(-3, 11)),
        (
            (Fraction(1, 100), 0),
            (0, Fraction(-1, 120)),
            (Fraction(1, 140), Fraction(1, 150)),
            (Fraction(-1, 110), 0),
            (0, Fraction(1, 130)),
            (Fraction(1, 160), Fraction(-1, 170)),
        ),
        (Fraction(1, 200),) * 6,
        (
            Fraction(1, 180),
            Fraction(-1, 190),
            Fraction(1, 210),
            Fraction(-1, 220),
            Fraction(1, 230),
            Fraction(-1, 240),
        ),
        semantic,
        (
            Fraction(1, 250),
            Fraction(-1, 260),
            Fraction(1, 270),
            Fraction(-1, 280),
        ),
    )
    certificate = build_joint_certificate(
        design,
        context,
        values,
        (Fraction(1, 200),) * 6,
        (Fraction(1, 175),) * 6,
        (Fraction(1, 90),) * 6,
        semantic,
        (Fraction(1, 240),) * 4,
    )
    assert certificate["certificate_available"]
    assert certificate["mechanical_gain"] < 1
    audits = realized_direction_audit(
        certificate,
        theta,
        ((1, 0), (0, 1), (1, 1), (2, -3)),
    )
    assert all(row["covered"] for row in audits)


def test_contraction_boundary_is_unavailable():
    certificate = build_joint_certificate(
        ((1,),),
        ((),),
        (0,),
        (0,),
        (0,),
        (1,),
        ((),),
        (),
    )
    assert certificate["status"] == "mechanical_contraction_unavailable"
    assert certificate["mechanical_gain"] == 1


def test_support_witness_attains_exact_zonotope_support():
    design, context, semantic = base_fixture()
    certificate = build_joint_certificate(
        design,
        context,
        (0, 1, -1, 0, 1, -1),
        (Fraction(1, 20),) * 6,
        (Fraction(1, 30),) * 6,
        (Fraction(1, 50),) * 6,
        semantic,
        (Fraction(1, 40),) * 4,
    )
    witness = support_witness(certificate, (3, -2))
    assert witness["attained_support"] == certificate_support(
        certificate, (3, -2)
    )


def test_policy_decision_uses_strict_support_margin():
    design, context, semantic = base_fixture()
    certificate = build_joint_certificate(
        design,
        context,
        (0, 2, -1, 0, 2, -1),
        (Fraction(1, 100),) * 6,
        (Fraction(1, 120),) * 6,
        (Fraction(1, 200),) * 6,
        semantic,
        (Fraction(1, 150),) * 4,
    )
    result = evaluate_policy_family(
        certificate,
        ((0, 0), (1, 0), (0, 1), (1, 1)),
    )
    assert result["available"]
    assert result["policy_identity_certified"]
    assert result["robust_regret_bound"] == 0


def test_policy_equality_is_inconclusive():
    certificate = build_joint_certificate(
        ((1,), (-1,)),
        ((), ()),
        (1, -1),
        (1, 1),
        (0, 0),
        (0, 0),
        ((), ()),
        (),
    )
    uncertainty = certificate_support(certificate, (1,))
    result = evaluate_policy_family(
        certificate,
        ((0,), (1,)),
    )
    assert certificate["theta_hat"][0] == uncertainty
    assert not result["policy_identity_certified"]
    assert any(row["lower_margin"] == 0 for row in result["margin_rows"])


def test_invalid_source_dimensions_are_rejected():
    design, context, semantic = base_fixture()
    with pytest.raises(ValueError):
        build_joint_certificate(
            design,
            context,
            (0,) * 6,
            (0,) * 5,
            (0,) * 6,
            (0,) * 6,
            semantic,
            (0,) * 4,
        )


def test_semantic_incidence_preserves_shared_cell_correlation():
    certificate = build_joint_certificate(
        ((1,), (-1,)),
        ((), ()),
        (1, -1),
        (0, 0),
        (0, 0),
        (0, 0),
        ((1, -1), (1, -1)),
        (Fraction(1, 10), Fraction(1, 10)),
    )
    # Identical semantic rows are removed by the antisymmetric analysis map.
    assert certificate_support(certificate, (1,)) == 0
