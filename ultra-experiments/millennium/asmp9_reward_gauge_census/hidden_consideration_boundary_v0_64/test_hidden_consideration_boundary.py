from fractions import Fraction
from itertools import combinations

import pytest

from hidden_consideration_boundary import (
    adjacent_swap_witness,
    all_pairs,
    attainable_choices,
    compliance_suite_identifies,
    deterministic_identifiable,
    intervention_separates,
    intervention_family_observation,
    minimum_separating_suite,
    minimum_nonadaptive_pair_queries,
    pair_signature,
    rankings,
    singleton_attention_observation,
    validate_kernel,
)


Q = Fraction


def graph_edge_sets(n):
    edges = all_pairs(n)
    for mask in range(1 << len(edges)):
        yield tuple(
            edge
            for index, edge in enumerate(edges)
            if mask & (1 << index)
        )


def fixture_kernel(n):
    result = {}
    for size in range(1, n + 1):
        for menu in combinations(range(n), size):
            denominator = sum(index + 2 for index, _ in enumerate(menu))
            result[menu] = tuple(
                Q(index + 2, denominator)
                for index, _ in enumerate(menu)
            )
    return result


def test_singleton_attention_collapses_every_ranking():
    for n in range(2, 7):
        kernel = fixture_kernel(n)
        expected = {
            menu: tuple(probabilities)
            for menu, probabilities in kernel.items()
        }
        for ranking in rankings(n):
            assert singleton_attention_observation(ranking, kernel) == expected


def test_randomized_instruction_does_not_repair_unobserved_compliance():
    kernels = {
        "control": fixture_kernel(3),
        "attention_prompt": {
            (0,): (Q(1),),
            (1,): (Q(1),),
            (2,): (Q(1),),
            (0, 1): (Q(1, 4), Q(3, 4)),
            (0, 2): (Q(2, 3), Q(1, 3)),
            (1, 2): (Q(3, 5), Q(2, 5)),
            (0, 1, 2): (Q(1, 6), Q(1, 3), Q(1, 2)),
        },
    }
    outputs = [
        intervention_family_observation(ranking, kernels)
        for ranking in rankings(3)
    ]
    assert all(output == outputs[0] for output in outputs)


def test_complete_pair_family_identifies_every_ranking():
    for n in range(2, 8):
        pairs = all_pairs(n)
        signatures = {
            pair_signature(ranking, pairs)
            for ranking in rankings(n)
        }
        assert len(signatures) == len(rankings(n))
        assert deterministic_identifiable(n, pairs)
        assert len(pairs) == minimum_nonadaptive_pair_queries(n)


def test_general_compliance_correspondence_has_exact_separation_criterion():
    singleton_compliance = ((0,), (1,), (2,))
    full_menu_compliance = ((0, 1, 2),)
    orders = rankings(3)

    assert all(
        attainable_choices(order, singleton_compliance) == (0, 1, 2)
        for order in orders
    )
    assert not compliance_suite_identifies(3, (singleton_compliance,))

    same_top = ((0, 1, 2), (0, 2, 1))
    different_top = ((0, 1, 2), (1, 0, 2))
    assert not intervention_separates(
        *same_top,
        full_menu_compliance,
    )
    assert intervention_separates(
        *different_top,
        full_menu_compliance,
    )
    assert not compliance_suite_identifies(3, (full_menu_compliance,))


def test_exact_pair_interventions_solve_the_separation_cover_sharply():
    for n in range(2, 6):
        candidates = {
            f"{x}-{y}": ((x, y),)
            for x, y in all_pairs(n)
        }
        size, selected = minimum_separating_suite(n, candidates)
        assert size == minimum_nonadaptive_pair_queries(n)
        assert set(selected) == set(candidates)
        assert compliance_suite_identifies(
            n,
            tuple(candidates[name] for name in selected),
        )


def test_every_missing_pair_has_adjacent_swap_witness():
    for n in range(2, 9):
        complete = set(all_pairs(n))
        for missing in complete:
            queries = tuple(sorted(complete - {missing}))
            left, right = adjacent_swap_witness(n, missing)
            assert left != right
            assert pair_signature(left, queries) == pair_signature(
                right,
                queries,
            )
            assert pair_signature(left, (missing,)) != pair_signature(
                right,
                (missing,),
            )


def test_exhaustive_query_graph_census_through_five_items():
    for n in range(2, 6):
        for pairs in graph_edge_sets(n):
            signatures = [
                pair_signature(ranking, pairs)
                for ranking in rankings(n)
            ]
            injective = len(set(signatures)) == len(signatures)
            assert injective == deterministic_identifiable(n, pairs)


def test_invalid_objects_fail_closed():
    with pytest.raises(ValueError):
        minimum_nonadaptive_pair_queries(1)
    with pytest.raises(ValueError):
        adjacent_swap_witness(3, (0, 0))
    with pytest.raises(ValueError):
        validate_kernel({(0, 1): (Q(1, 3), Q(1, 3))})
    with pytest.raises(ValueError):
        validate_kernel({(1, 0): (Q(1, 2), Q(1, 2))})
    with pytest.raises(ValueError):
        attainable_choices((0, 0), ((0,),))
    with pytest.raises(ValueError):
        attainable_choices((0, 1), ((),))
    with pytest.raises(ValueError):
        compliance_suite_identifies(3, (((0, 3),),))
    with pytest.raises(ValueError):
        minimum_separating_suite(
            2,
            {1: ((0, 1),), "1": ((0, 1),)},
        )
