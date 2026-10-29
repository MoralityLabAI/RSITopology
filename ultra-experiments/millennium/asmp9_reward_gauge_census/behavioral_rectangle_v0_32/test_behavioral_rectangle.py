from __future__ import annotations

from fractions import Fraction
from itertools import product

import pytest

from .behavioral_rectangle import (
    acquire_rectangle,
    additive_decomposition,
    audit_mixture_affinity,
    bisect_standard_gamble,
    box_support,
    centered_dyadic_grid,
    certify_rectangle,
    cross_difference_matrix,
    flatten,
    interaction_residuals,
    majority_error_probability,
    minimum_odd_repeats,
    omission_witness,
    rational_rank,
    row_local_coordinates,
    standard_gamble_response,
)


def test_centered_grid_has_exact_depth_localization() -> None:
    for depth in range(1, 7):
        for value in centered_dyadic_grid(depth):
            result = bisect_standard_gamble(value, depth)
            assert result.query_count == depth
            assert result.lower < value < result.upper
            assert result.upper - result.lower == Fraction(1, 2**depth)
            assert abs(result.estimate - value) == 0


def test_population_oracle_is_binary_at_equality() -> None:
    assert standard_gamble_response(Fraction(1, 2), Fraction(1, 2)) == -1


def test_additive_rectangle_and_interaction_are_separated() -> None:
    additive = (
        (Fraction(1, 16), Fraction(5, 16), Fraction(9, 16)),
        (Fraction(3, 16), Fraction(7, 16), Fraction(11, 16)),
        (Fraction(5, 16), Fraction(9, 16), Fraction(13, 16)),
    )
    assert interaction_residuals(additive) == (0, 0, 0, 0)
    decomposition = additive_decomposition(additive)
    assert decomposition is not None

    interactive = [list(row) for row in additive]
    interactive[2][2] += Fraction(1, 8)
    assert interaction_residuals(interactive)[-1] == Fraction(1, 8)
    assert additive_decomposition(interactive) is None


def test_cross_difference_operator_has_full_row_rank() -> None:
    matrix = cross_difference_matrix(3, 4)
    assert len(matrix) == 6
    assert len(matrix[0]) == 12
    assert rational_rank(matrix) == 6


def test_acquired_rectangle_preserves_shared_cell_geometry() -> None:
    values = (
        (Fraction(1, 32), Fraction(9, 32), Fraction(17, 32)),
        (Fraction(5, 32), Fraction(13, 32), Fraction(21, 32)),
        (Fraction(9, 32), Fraction(17, 32), Fraction(25, 32)),
    )
    acquired = acquire_rectangle(values, depth=4)
    estimates = tuple(tuple(cell.estimate for cell in row) for row in acquired)
    widths = tuple(tuple(cell.radius for cell in row) for row in acquired)
    certificate = certify_rectangle(estimates, widths, tolerance=Fraction(1, 8))
    assert certificate.decision == "approximately_additive_certified"
    assert all(row.support == Fraction(1, 8) for row in certificate.residuals)


def test_three_state_certificate_semantics() -> None:
    zero_widths = ((0, 0), (0, 0))
    assert (
        certify_rectangle(((0, 0), (0, 0)), zero_widths, 0).decision
        == "approximately_additive_certified"
    )
    assert (
        certify_rectangle(((0, 0), (0, 1)), zero_widths, Fraction(1, 2)).decision
        == "interaction_certified"
    )
    uncertain = certify_rectangle(
        ((0, 0), (0, Fraction(3, 4))),
        ((Fraction(1, 8),) * 2,) * 2,
        Fraction(1, 2),
    )
    assert uncertain.decision == "inconclusive"


def test_mixture_affinity_has_pass_reject_and_inconclusive_states() -> None:
    consistent = audit_mixture_affinity(
        first_estimate=Fraction(1, 4),
        second_estimate=Fraction(3, 4),
        mixture_estimate=Fraction(7, 12),
        first_weight=Fraction(1, 3),
        first_width=0,
        second_width=0,
        mixture_width=0,
        tolerance=0,
    )
    assert consistent.residual == 0
    assert consistent.decision == "mixture_affinity_certified"

    distorted = audit_mixture_affinity(
        first_estimate=Fraction(1, 4),
        second_estimate=Fraction(3, 4),
        mixture_estimate=Fraction(2, 3),
        first_weight=Fraction(1, 3),
        first_width=0,
        second_width=0,
        mixture_width=0,
        tolerance=Fraction(1, 24),
    )
    assert distorted.residual == Fraction(1, 12)
    assert distorted.decision == "mixture_affinity_rejected"

    uncertain = audit_mixture_affinity(
        first_estimate=Fraction(1, 4),
        second_estimate=Fraction(3, 4),
        mixture_estimate=Fraction(2, 3),
        first_weight=Fraction(1, 3),
        first_width=Fraction(1, 48),
        second_width=Fraction(1, 48),
        mixture_width=Fraction(1, 48),
        tolerance=Fraction(1, 16),
    )
    assert uncertain.decision == "inconclusive"


def test_support_formula_is_attained_by_a_box_vertex() -> None:
    matrix = cross_difference_matrix(2, 3)
    widths = (Fraction(1, 10), Fraction(1, 20), Fraction(1, 30)) * 2
    direction = (Fraction(2), Fraction(-3))
    formula = box_support(matrix, widths, direction)
    brute_force = max(
        sum(
            direction[row]
            * sum(
                matrix[row][column] * signs[column] * widths[column]
                for column in range(len(widths))
            )
            for row in range(len(matrix))
        )
        for signs in product((-1, 1), repeat=len(widths))
    )
    assert formula == brute_force


def test_ordinal_only_witness_preserves_order_but_breaks_additivity() -> None:
    additive = (
        (Fraction(0), Fraction(1, 3)),
        (Fraction(2, 3), Fraction(1)),
    )
    transformed = tuple(tuple(Fraction(value) ** 2 for value in row) for row in additive)
    assert sorted(flatten(additive)) == list(flatten(additive))
    assert sorted(flatten(transformed)) == list(flatten(transformed))
    assert interaction_residuals(additive) == (0,)
    assert interaction_residuals(transformed) == (Fraction(4, 9),)


def test_row_local_rulers_do_not_glue_cardinal_scale() -> None:
    additive = (
        (Fraction(0), Fraction(1, 4), Fraction(1, 2)),
        (Fraction(1, 3), Fraction(7, 12), Fraction(5, 6)),
    )
    interactive = (
        (Fraction(0), Fraction(1, 4), Fraction(1, 2)),
        (Fraction(1, 2), Fraction(2, 3), Fraction(5, 6)),
    )
    assert row_local_coordinates(additive) == row_local_coordinates(interactive)
    assert additive_decomposition(additive) is not None
    assert additive_decomposition(interactive) is None


def test_every_omitted_cell_has_an_interaction_witness() -> None:
    rows = 3
    columns = 4
    for omitted in range(rows * columns):
        witness = omission_witness(rows, columns, omitted, Fraction(1, 7))
        assert any(value != 0 for value in interaction_residuals(witness))
        observed = [
            value
            for index, value in enumerate(flatten(witness))
            if index != omitted
        ]
        assert observed == [0] * (rows * columns - 1)


def test_exact_majority_repeat_gate_is_minimal() -> None:
    query_count = 48
    family_error = Fraction(1, 100)
    repeats = minimum_odd_repeats(query_count, Fraction(3, 4), family_error)
    assert query_count * majority_error_probability(repeats, Fraction(3, 4)) <= family_error
    if repeats > 1:
        assert (
            query_count
            * majority_error_probability(repeats - 2, Fraction(3, 4))
            > family_error
        )


def test_chance_responses_have_no_finite_repeat_certificate() -> None:
    with pytest.raises(ValueError, match="no finite guarantee"):
        minimum_odd_repeats(48, Fraction(1, 2), Fraction(1, 100))
