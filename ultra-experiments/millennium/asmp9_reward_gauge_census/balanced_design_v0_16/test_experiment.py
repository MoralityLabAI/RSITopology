from fractions import Fraction

from experiment import (
    allocation_census,
    balanced_allocation,
    balanced_worst_closed,
    local_branches,
    minimal_total_trials,
    pair_constants,
    smoothing_certificate,
    worst_endpoint_availability,
)


def test_pair_branch_formula_matches_four_direct_labels() -> None:
    epsilon = Fraction(1, 5)
    U, V, W = pair_constants((2, 5), epsilon, (0, 1))
    record = smoothing_certificate(1, 5, epsilon, U, V, W)
    assert record["branch_formula_matches_direct"]
    assert record["same_decomposition_holds"]
    assert record["opposite_decomposition_holds"]


def test_both_pair_branches_improve_strictly() -> None:
    epsilon = Fraction(1, 7)
    U, V, W = pair_constants((1, 3, 4), epsilon, (0, 1, 0))
    record = smoothing_certificate(2, 8, epsilon, U, V, W)
    assert record["same_strictly_improves"]
    assert record["opposite_strictly_improves"]
    assert record["minimum_strictly_improves"]
    assert record["D_is_invariant"]
    assert record["pair_products_nondecrease"]


def test_global_smoothing_improves_worst_case() -> None:
    epsilon = Fraction(1, 4)
    before, _ = worst_endpoint_availability((1, 2, 7), epsilon)
    after, _ = worst_endpoint_availability((2, 2, 6), epsilon)
    assert after > before


def test_balanced_allocation_is_unique_in_exact_cell() -> None:
    record = allocation_census(12, 5, Fraction(1, 5))
    assert record["balanced_allocation"] == [2, 2, 2, 3, 3]
    assert record["balanced_is_unique_modulo_permutation"]
    assert record["all_smoothing_steps_strict"]


def test_zero_interior_destroys_uniqueness() -> None:
    left, _ = worst_endpoint_availability((1, 1, 6), Fraction(0))
    balanced, _ = worst_endpoint_availability((2, 3, 3), Fraction(0))
    assert left == balanced == 0


def test_k_two_opposite_branch_can_be_sum_only() -> None:
    epsilon = Fraction(1, 5)
    first = local_branches(
        1, 5, epsilon, Fraction(1), Fraction(1), Fraction(1)
    )
    second = local_branches(
        2, 4, epsilon, Fraction(1), Fraction(1), Fraction(1)
    )
    assert first["D"] == second["D"]


def test_balanced_constructor() -> None:
    assert balanced_allocation(17, 6) == (2, 3, 3, 3, 3, 3)


def test_closed_balanced_value_matches_full_label_enumeration() -> None:
    epsilon = Fraction(1, 6)
    closed, _ = balanced_worst_closed(17, 6, epsilon)
    exhaustive, _ = worst_endpoint_availability(
        balanced_allocation(17, 6), epsilon
    )
    assert closed == exhaustive


def test_total_budget_threshold_straddles_target() -> None:
    epsilon = Fraction(1, 5)
    target = Fraction(19, 20)
    threshold = minimal_total_trials(5, epsilon, target)
    assert threshold is not None
    current, _ = balanced_worst_closed(threshold, 5, epsilon)
    predecessor, _ = balanced_worst_closed(
        threshold - 1, 5, epsilon
    )
    assert predecessor < target <= current
