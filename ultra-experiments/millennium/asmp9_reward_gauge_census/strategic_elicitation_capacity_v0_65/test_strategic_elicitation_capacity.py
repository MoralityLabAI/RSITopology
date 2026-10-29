from fractions import Fraction
from itertools import combinations
from math import factorial

import pytest

from strategic_elicitation_capacity import (
    all_pairs,
    best_report_indices,
    brute_force_capacity,
    full_domain_capacity,
    minimum_pair_lottery_support,
    pair_lottery_regret,
    pair_lottery_strictly_elicits_all,
    rankings,
    revealed_pair_class_size,
    report_top_best_response_multiplicity,
    report_top_outcome_map,
    sharp_uniform_incentive_margin,
    strict_capacity,
    strictly_incentive_identifies,
    uniform_pair_weights,
    validate_pair_weights,
    validate_types,
    weakly_truthful,
)


def type_domains(n):
    types = rankings(n)
    for size in range(1, len(types) + 1):
        for indices in combinations(range(len(types)), size):
            yield tuple(types[index] for index in indices)


def test_capacity_formula_matches_every_small_direct_mechanism_domain():
    for n in (2, 3):
        for domain in type_domains(n):
            capacity, witness = strict_capacity(domain)
            assert capacity == brute_force_capacity(domain)
            selected_types = tuple(domain[index] for index, _ in witness)
            outcome_map = tuple(outcome for _, outcome in witness)
            assert strictly_incentive_identifies(selected_types, outcome_map)


def test_full_strict_ranking_domain_capacity_is_outcome_count():
    for n in range(2, 8):
        assert full_domain_capacity(n) == n
        assert len(rankings(n)) == factorial(n)


def test_report_top_is_weakly_truthful_but_not_identifying():
    for n in range(2, 8):
        types = rankings(n)
        outcome_map = report_top_outcome_map(types)
        assert weakly_truthful(types, outcome_map)
        assert report_top_best_response_multiplicity(n) == factorial(n - 1)
        assert strictly_incentive_identifies(types, outcome_map) == (n == 2)


def test_duplicate_outcomes_cannot_support_strict_identification():
    domain = ((0, 1, 2), (1, 0, 2))
    assert strictly_incentive_identifies(domain, (0, 1))
    assert not strictly_incentive_identifies(domain, (0, 0))


def test_best_response_sets_expose_behavioral_ambiguity():
    types = rankings(3)
    outcome_map = report_top_outcome_map(types)
    for ranking in types:
        best = best_report_indices(ranking, outcome_map)
        assert len(best) == 2
        assert {
            types[index][0]
            for index in best
        } == {ranking[0]}


def test_commit_then_random_pair_strictly_elicits_full_ranking():
    for n in range(2, 6):
        weights = uniform_pair_weights(n)
        assert pair_lottery_strictly_elicits_all(n, weights)
        for true_ranking in rankings(n):
            utilities = [Fraction(0) for _ in range(n)]
            for position, outcome in enumerate(true_ranking):
                utilities[outcome] = Fraction(n - position, n)
            for report in rankings(n):
                regret = pair_lottery_regret(
                    true_ranking,
                    report,
                    utilities,
                    weights,
                )
                assert regret >= 0
                assert (regret == 0) == (report == true_ranking)


def test_every_missing_pair_has_a_zero_regret_adjacent_swap():
    for n in range(3, 8):
        pairs = all_pairs(n)
        for missing_pair in pairs:
            retained = tuple(pair for pair in pairs if pair != missing_pair)
            weights = {
                pair: Fraction(1, len(retained))
                for pair in retained
            }
            assert not pair_lottery_strictly_elicits_all(n, weights)

            first, second = missing_pair
            remainder = tuple(
                outcome
                for outcome in range(n)
                if outcome not in missing_pair
            )
            true_ranking = (first, second, *remainder)
            report = (second, first, *remainder)
            utilities = [Fraction(0) for _ in range(n)]
            for position, outcome in enumerate(true_ranking):
                utilities[outcome] = Fraction(n - position, n)
            assert (
                pair_lottery_regret(
                    true_ranking,
                    report,
                    utilities,
                    weights,
                )
                == 0
            )


def test_uniform_pair_margin_is_sharp_under_gap_normalization():
    for n in range(2, 8):
        gap = Fraction(1, n)
        true_ranking = tuple(range(n))
        report = (1, 0, *range(2, n))
        utilities = tuple(
            Fraction(n - outcome, n)
            for outcome in range(n)
        )
        observed = pair_lottery_regret(
            true_ranking,
            report,
            utilities,
            uniform_pair_weights(n),
        )
        expected = gap / minimum_pair_lottery_support(n)
        assert observed == expected
        assert sharp_uniform_incentive_margin(n, gap) == expected


def test_revealing_one_pair_before_response_does_not_identify_ranking():
    for n in range(2, 8):
        class_size = revealed_pair_class_size(n)
        assert class_size == factorial(n) // 2
        assert (class_size > 1) == (n >= 3)


def test_invalid_objects_fail_closed():
    with pytest.raises(ValueError):
        rankings(1)
    with pytest.raises(ValueError):
        validate_types(())
    with pytest.raises(ValueError):
        validate_types(((0, 0),))
    with pytest.raises(ValueError):
        strictly_incentive_identifies(((0, 1),), ())
    with pytest.raises(ValueError):
        strictly_incentive_identifies(((0, 1),), (2,))
    with pytest.raises(ValueError):
        validate_pair_weights(3, {})
    with pytest.raises(ValueError):
        validate_pair_weights(3, {(1, 0): Fraction(1)})
    with pytest.raises(ValueError):
        validate_pair_weights(3, {(0, 1): Fraction(1, 2)})
    with pytest.raises(ValueError):
        pair_lottery_regret(
            (0, 1, 2),
            (0, 1, 2),
            (0, 1, 2),
            uniform_pair_weights(3),
        )
    with pytest.raises(ValueError):
        sharp_uniform_incentive_margin(3, Fraction(3, 4))
