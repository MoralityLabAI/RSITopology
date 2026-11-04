from fractions import Fraction

from experiment import (
    balanced_allocation,
    exact_allocation_optima,
    exhaustive_vertex_minimum_equal,
    minimal_equal_trials,
    sharp_min_availability,
    v014_crude_lower_bound,
)


def test_sharp_formula_matches_all_endpoint_counts() -> None:
    for k in range(3, 9):
        for n in range(1, 6):
            for epsilon in (
                Fraction(1, 10),
                Fraction(1, 5),
                Fraction(1, 4),
            ):
                formula = sharp_min_availability(k, n, epsilon)
                exhaustive, witnesses = exhaustive_vertex_minimum_equal(
                    k, n, epsilon
                )
                assert formula == exhaustive
                assert witnesses == sorted({k // 2, k - k // 2})


def test_exact_trial_threshold_straddles_target() -> None:
    for k in (3, 4, 6, 8):
        for epsilon in (Fraction(1, 10), Fraction(1, 4)):
            for target in (Fraction(4, 5), Fraction(19, 20)):
                threshold = minimal_equal_trials(k, epsilon, target)
                assert threshold is not None
                assert (
                    sharp_min_availability(k, threshold, epsilon)
                    >= target
                )
                if threshold > 1:
                    assert (
                        sharp_min_availability(
                            k, threshold - 1, epsilon
                        )
                        < target
                    )


def test_zero_interior_has_no_uniform_availability() -> None:
    for k in (3, 4, 8):
        for n in (1, 10, 100):
            assert sharp_min_availability(k, n, Fraction(0)) == 0
        assert minimal_equal_trials(k, Fraction(0), Fraction(1, 2)) is None


def test_sharp_minimum_dominates_v014_crude_bound() -> None:
    for k in range(3, 9):
        for n in range(1, 6):
            for epsilon in (Fraction(1, 20), Fraction(1, 10)):
                assert sharp_min_availability(
                    k, n, epsilon
                ) >= v014_crude_lower_bound(k, n, epsilon)


def test_balanced_allocation_constructor() -> None:
    assert balanced_allocation(17, 5) == (3, 3, 3, 4, 4)
    assert balanced_allocation(12, 4) == (3, 3, 3, 3)


def test_bounded_exact_allocation_cells_favor_balance() -> None:
    for k in (3, 4):
        for epsilon in (Fraction(1, 10), Fraction(1, 4)):
            for extra in range(0, 6):
                record = exact_allocation_optima(k + extra, k, epsilon)
                assert record["balanced_is_optimal"]
