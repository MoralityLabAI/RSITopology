from fractions import Fraction as Q

from gauge_leakage import certify_access_alignment


def test_equal_leakage_radius_does_not_imply_equal_access_value():
    high, low = Q(2, 3), Q(1, 3)
    aligned = certify_access_alignment(high, low, "q0")
    redundant = certify_access_alignment(high, low, "q1")
    transverse = certify_access_alignment(high, low, "q2")
    assert {
        aligned.leakage_radius,
        redundant.leakage_radius,
        transverse.leakage_radius,
    } == {Q(1, 6)}
    assert aligned.relative_substitution_deficiency == 0
    assert redundant.relative_substitution_deficiency == Q(1, 6)
    assert transverse.relative_substitution_deficiency == Q(2, 27)


def test_output_reframing_preserves_exact_substitution():
    direct = certify_access_alignment(Q(3, 4), Q(1, 4), "q0")
    complement = certify_access_alignment(
        Q(3, 4), Q(1, 4), "q0_complement"
    )
    assert direct.relative_substitution_deficiency == 0
    assert direct.ordinary_substitution_deficiency == 0
    assert complement.relative_substitution_deficiency == 0
    assert complement.ordinary_substitution_deficiency == 0


def test_intervened_gauge_reverts_to_missing_query_threshold():
    certificate = certify_access_alignment(
        Q(3, 4), Q(1, 4), "constant"
    )
    assert certificate.leakage_radius == 0
    assert certificate.relative_substitution_deficiency == Q(1, 4)
    assert certificate.ordinary_substitution_deficiency == Q(1, 4)


def test_transverse_formula_on_burned_strengths():
    strengths = (
        (Q(2, 3), Q(1, 3)),
        (Q(3, 4), Q(1, 4)),
        (Q(4, 5), Q(1, 5)),
        (Q(3, 5), Q(2, 5)),
    )
    for high, low in strengths:
        certificate = certify_access_alignment(high, low, "q2")
        expected = high * low * (high - low)
        assert certificate.relative_substitution_deficiency == expected
        assert certificate.ordinary_substitution_deficiency == expected
