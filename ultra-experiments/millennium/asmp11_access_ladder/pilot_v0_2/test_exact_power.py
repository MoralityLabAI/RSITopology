from fractions import Fraction
from math import comb

from exact_power import (
    boundary_plans,
    containment_plans,
    find_exact_design,
    most_permissive_cutoff,
    two_sided_binomial_tail,
)


def test_fair_coin_two_sided_tail() -> None:
    assert two_sided_binomial_tail(4, 0, Fraction(1, 2)) == Fraction(1, 8)
    assert two_sided_binomial_tail(4, 1, Fraction(1, 2)) == Fraction(5, 8)


def test_cutoff_obeys_exact_union_bound() -> None:
    cutoff = most_permissive_cutoff(20, 10, Fraction(1, 20))
    assert cutoff is not None
    tail = two_sided_binomial_tail(20, cutoff, Fraction(1, 2))
    assert 10 * tail <= Fraction(1, 20)
    next_tail = two_sided_binomial_tail(20, cutoff + 1, Fraction(1, 2))
    assert 10 * next_tail > Fraction(1, 20)


def test_design_is_minimal_in_samples_per_query() -> None:
    design = find_exact_design(1, Fraction(1, 20), Fraction(1, 20), Fraction(9, 10), 100)
    assert design is not None
    assert design.familywise_error_upper <= Fraction(1, 20)
    assert design.signal_power_lower >= Fraction(9, 10)
    if design.samples_per_query > 1:
        assert find_exact_design(
            1,
            Fraction(1, 20),
            Fraction(1, 20),
            Fraction(9, 10),
            design.samples_per_query - 1,
        ) is None


def test_boundary_query_counts_never_beat_pure_observation() -> None:
    for n, k in ((8, 3), (12, 4), (20, 6)):
        plans = boundary_plans(n, k)
        pure = plans[0]
        assert pure.query_count == comb(n, k)
        assert all(plan.query_count >= pure.query_count for plan in plans)


def test_full_clamp_is_one_query_but_uses_width_n() -> None:
    for n, k in ((8, 3), (12, 4), (20, 6)):
        plans = containment_plans(n, k)
        assert plans[-1].query_count == 1
        assert plans[-1].intervention_width == n
