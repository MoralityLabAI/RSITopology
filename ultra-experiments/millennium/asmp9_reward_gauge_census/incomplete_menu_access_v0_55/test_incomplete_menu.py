from fractions import Fraction as Q

from incomplete_menu import (
    ABC,
    ALL_MENUS,
    L,
    N,
    R,
    compatible_tiers,
    full_grid,
    full_status,
    make_kernel,
    menu_domains,
    nonluce_rum_completion,
    nonrum_completion,
    project,
    rum_completion,
    scalar_completion,
)


def uniform_luce():
    return make_kernel(
        Q(1, 2), Q(1, 2), Q(1, 2), (Q(1, 3), Q(1, 3), Q(1, 3))
    )


def test_all_proper_domains_admit_all_three_tiers_from_uniform_luce():
    scalar = uniform_luce()
    for domain in menu_domains():
        if set(domain) == set(ALL_MENUS):
            continue
        partial = project(scalar, domain)
        weights = scalar_completion(partial, domain)
        assert weights is not None
        middle = nonluce_rum_completion(partial, domain, weights)
        none = nonrum_completion(partial, domain)
        assert full_status(scalar) == L
        assert full_status(middle) == R
        assert full_status(none) == N
        assert compatible_tiers(partial, domain) == (L, R, N)


def test_partial_regularity_violation_refutes_every_rum_completion():
    full = make_kernel(
        Q(1, 2), Q(1, 2), Q(1, 2), (Q(3, 4), Q(1, 8), Q(1, 8))
    )
    domain = (("a", "b"), ABC)
    partial = project(full, domain)
    assert rum_completion(partial, domain) is None
    assert compatible_tiers(partial, domain) == (N,)


def test_cyclic_pairs_are_rum_compatible_but_not_scalar():
    full = make_kernel(
        Q(2, 3), Q(1, 3), Q(2, 3), (Q(1, 3), Q(1, 3), Q(1, 3))
    )
    domain = (("a", "b"), ("a", "c"), ("b", "c"))
    partial = project(full, domain)
    assert scalar_completion(partial, domain) is None
    assert rum_completion(partial, domain) is not None
    assert compatible_tiers(partial, domain) == (R, N)


def test_full_domain_returns_one_tier():
    statuses = {full_status(kernel) for kernel in full_grid()}
    assert statuses == {L, R, N}
    for kernel in full_grid():
        assert compatible_tiers(kernel, ALL_MENUS) == (full_status(kernel),)


def test_domain_lattice_has_fifteen_nonempty_members():
    assert sum(1 for _ in menu_domains()) == 15

