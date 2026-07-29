from fractions import Fraction as Q

import general_incomplete as gi


def test_random_utility_polytope_has_full_checked_affine_rank():
    for n in (3, 4, 5):
        assert gi.random_utility_affine_rank(n) == gi.ambient_dimension(n)


def test_adjacent_swap_zeta_system_is_exactly_invertible():
    for width in range(6):
        matrix = gi.subset_zeta_matrix(width)
        assert gi.exact_rank(matrix) == 1 << width


def test_dimension_gap_is_strict_on_all_small_proper_domains():
    for n in (3, 4):
        for observed in gi.proper_domains(n):
            assert gi.dimension_gap(n, observed) > 0


def test_constructive_nonrum_completion_on_all_small_proper_domains():
    for n in (3, 4):
        source = gi.uniform_kernel(n)
        for observed in gi.proper_domains(n):
            completion = gi.construct_nonrum_completion(n, observed, source)
            assert gi.regularity_violations(n, completion)
            for menu in observed:
                for choice in menu:
                    assert completion[(menu, choice)] == source[(menu, choice)]
            for menu in gi.menus(n):
                assert sum(completion[(menu, x)] for x in menu) == 1
                assert all(completion[(menu, x)] > 0 for x in menu)


def test_dimension_formula_examples():
    n = 5
    connected = ((0, 1), (1, 2), (2, 3), (3, 4))
    assert gi.luce_fiber_dimension(n, connected) == 0
    assert gi.dimension_gap(n, connected) > 0

    disconnected = ((0, 1), (2, 3))
    assert gi.luce_fiber_dimension(n, disconnected) == 2
    assert gi.dimension_gap(n, disconnected) > 0


def test_regularization_witness_uses_exact_rationals():
    completion = gi.construct_nonrum_completion(3, ())
    assert all(isinstance(value, Q) for value in completion.values())


def test_witness_preserves_nonuniform_luce_observations():
    n = 4
    weights = (Q(1), Q(2), Q(3), Q(5))
    source = {
        (menu, choice): weights[choice] / sum(weights[x] for x in menu)
        for menu in gi.menus(n)
        for choice in menu
    }
    universe = gi.menus(n)
    for missing in universe:
        observed = tuple(menu for menu in universe if menu != missing)
        completion = gi.construct_nonrum_completion(n, observed, source)
        assert gi.regularity_violations(n, completion)
        assert all(
            completion[(menu, choice)] == source[(menu, choice)]
            for menu in observed
            for choice in menu
        )
