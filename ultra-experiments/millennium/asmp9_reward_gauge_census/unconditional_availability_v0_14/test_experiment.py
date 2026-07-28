from fractions import Fraction

from experiment import (
    all_outcomes,
    availability_formula,
    canonical_fiber_key,
    drift_odds,
    fiber_members,
    run_cell,
)


def test_canonical_fibers_partition_cycle_counts() -> None:
    for k in (3, 4, 5):
        for n in (1, 2, 3):
            groups = {}
            for outcome in all_outcomes(k, n):
                key = canonical_fiber_key(outcome)
                groups.setdefault(key, []).append(outcome)
            for key, outcomes in groups.items():
                assert sorted(outcomes) == sorted(fiber_members(key, n))


def test_availability_formula_matches_exact_enumeration() -> None:
    for k in (3, 4):
        for n in (1, 2, 3):
            for nuisance in (Fraction(1), Fraction(2), Fraction(16)):
                record = run_cell(
                    k, n, Fraction(2), nuisance, Fraction(1, 20)
                )
                assert record["availability_formula_matches"]


def test_exact_size_excess_decomposition_and_bound() -> None:
    for nuisance in (Fraction(1), Fraction(4), Fraction(256)):
        record = run_cell(
            4, 3, Fraction(2), nuisance, Fraction(1, 20)
        )
        assert record["all_conditional_sizes_exact"]
        assert record["unconditional_size_all"]["fraction"] == "1/20"
        assert record["excess_decomposition_matches"]
        assert record["upper_bound_holds"]
        assert record["interior_lower_bound_holds"]


def test_zero_circulation_has_no_power_gain() -> None:
    record = run_cell(4, 2, Fraction(1), Fraction(8), Fraction(1, 20))
    assert record["excess_power"]["fraction"] == "0/1"
    assert record["unconditional_power_all"]["fraction"] == "1/20"
    assert record["minimum_informative_power_gain"]["fraction"] == "0/1"


def test_extreme_scalar_nuisance_erodes_availability_and_power_gain() -> None:
    balanced = run_cell(4, 3, Fraction(2), Fraction(1), Fraction(1, 20))
    extreme = run_cell(
        4, 3, Fraction(2), Fraction(256), Fraction(1, 20)
    )
    assert (
        extreme["availability_alternative"]["decimal"]
        < balanced["availability_alternative"]["decimal"]
    )
    assert (
        extreme["excess_power"]["decimal"]
        < balanced["excess_power"]["decimal"]
    )
    assert (
        balanced["minimum_informative_power_gain"]["decimal"] > 0
    )


def test_drift_family_is_exact_scalar_gradient() -> None:
    for k in (3, 4, 8):
        for nuisance in (Fraction(1), Fraction(3, 2), Fraction(256)):
            odds = drift_odds(k, nuisance)
            product = Fraction(1)
            for value in odds:
                product *= value
            assert product == 1
            assert 0 <= availability_formula(2, odds) <= 1
