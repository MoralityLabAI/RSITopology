from fractions import Fraction

from run import (
    F,
    crossed_gap,
    crossed_law,
    design_rank,
    exact_eigenpair,
    fisher_matrix,
    maximum_on_box,
    matrix_product,
    signed_permutation_matrices,
    transform_points,
    transpose,
    unspanned_gap,
    unspanned_law,
)


AXIS = (
    (F(0), F(0)),
    (F("1/2"), F(0)),
    (F("-1/2"), F(0)),
    (F(0), F("1/2")),
    (F(0), F("-1/2")),
)


def test_axis_worlds_are_exactly_indistinguishable():
    assert all(crossed_law(point, 1) == crossed_law(point, -1) for point in AXIS)


def test_crossed_and_unspanned_ambiguity_have_registered_orders():
    for radius in (F("1/4"), F("1/2"), F(1)):
        assert maximum_on_box(radius, crossed_gap) == radius * radius / 4
        assert maximum_on_box(radius, unspanned_gap) == radius / 4


def test_unspanned_line_is_blind_to_hidden_linear_term():
    line = tuple((theta_1, F(0)) for theta_1 in map(F, ("-1", "-1/2", "0", "1/2", "1")))
    assert design_rank(line) == 1
    assert all(unspanned_law(point, 1) == unspanned_law(point, -1) for point in line)


def test_fisher_matrix_and_exact_eigenpairs():
    fisher = fisher_matrix()
    assert fisher == ((F("5/64"), F("1/64")), (F("1/64"), F("5/64")))
    assert exact_eigenpair(fisher, (F(1), F(-1)), F("1/16"))
    assert exact_eigenpair(fisher, (F(1), F(1)), F("3/32"))


def test_safety_threshold_and_diagonal_gap_are_live():
    plus = crossed_law((F(1), F(1)), 1)[2]
    minus = crossed_law((F(1), F(1)), -1)[2]
    assert plus == F("3/4")
    assert minus == F("1/2")
    assert plus > F("3/5") > minus
    diagonal_gap = crossed_law((F("1/2"), F("1/2")), 1)[2] - crossed_law((F("1/2"), F("1/2")), -1)[2]
    assert diagonal_gap == F("1/16")


def test_all_signed_permutations_preserve_rank_and_fisher_spectrum():
    fisher = fisher_matrix()
    trace = fisher[0][0] + fisher[1][1]
    determinant = fisher[0][0] * fisher[1][1] - fisher[0][1] * fisher[1][0]
    matrices = signed_permutation_matrices()
    assert len(matrices) == 8
    for matrix in matrices:
        assert design_rank(transform_points(matrix, AXIS)) == 2
        transformed = matrix_product(matrix_product(matrix, fisher), transpose(matrix))
        assert transformed[0][0] + transformed[1][1] == trace
        assert transformed[0][0] * transformed[1][1] - transformed[0][1] * transformed[1][0] == determinant


def test_risk_null_quotient_discards_only_missing_nuisance():
    points_3d = tuple((point[0], point[1], Fraction(0)) for point in AXIS)
    points_quotient = tuple((point[0], point[1]) for point in points_3d)
    assert design_rank(points_3d) == 2
    assert design_rank(points_quotient) == 2
