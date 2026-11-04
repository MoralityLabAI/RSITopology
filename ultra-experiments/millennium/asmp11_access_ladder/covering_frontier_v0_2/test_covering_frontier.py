from fractions import Fraction
from math import comb

from covering_frontier import (
    counting_lower_bound,
    find_exact_design,
    schoenheim_lower_bound,
    solve_covering,
    verify_cover,
    worst_case_adaptive_covering_lemma_holds,
)


def test_boundary_and_full_clamp_covering_numbers() -> None:
    for n, k in ((6, 2), (7, 3), (8, 4)):
        boundary = solve_covering(n, k, k, time_limit_seconds=10)
        full = solve_covering(n, n, k, time_limit_seconds=10)
        assert boundary.optimum == comb(n, k)
        assert full.optimum == 1


def test_known_pair_cover_small_case() -> None:
    # Three triples cover all six pairs of K4.
    solution = solve_covering(4, 3, 2, time_limit_seconds=10)
    assert solution.optimum == 3
    assert verify_cover(4, 3, 2, solution.selected_blocks)


def test_lower_bounds_do_not_exceed_certified_optimum() -> None:
    for n, s, k in ((6, 3, 2), (7, 4, 3), (8, 5, 3)):
        solution = solve_covering(n, s, k, time_limit_seconds=10)
        assert counting_lower_bound(n, s, k) <= solution.optimum
        assert schoenheim_lower_bound(n, s, k) <= solution.optimum


def test_exact_finite_sample_design() -> None:
    design = find_exact_design(10, Fraction(3, 20), Fraction(1, 20), Fraction(9, 10), 500)
    assert design is not None
    assert design.familywise_error_upper <= Fraction(1, 20)
    assert design.signal_power_lower >= Fraction(9, 10)


def test_all_negative_path_requires_cover() -> None:
    incomplete = ((0, 1, 2),)
    complete = solve_covering(5, 3, 2, time_limit_seconds=10).selected_blocks
    assert not worst_case_adaptive_covering_lemma_holds(5, 3, 2, incomplete)
    assert worst_case_adaptive_covering_lemma_holds(5, 3, 2, complete)
