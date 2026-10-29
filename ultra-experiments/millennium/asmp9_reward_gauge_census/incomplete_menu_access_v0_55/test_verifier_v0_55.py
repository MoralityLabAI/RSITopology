from fractions import Fraction as Q

from verify_theorems_v0_55 import (
    ABC,
    L,
    N,
    R,
    full_status,
    kernel,
    nonrum_extension,
    positive_nonluce_rum_exists,
    projection,
    rum_basic_mixtures,
    scalar_weights,
)


def uniform():
    return kernel(
        Q(1, 2), Q(1, 2), Q(1, 2), (Q(1, 3), Q(1, 3), Q(1, 3))
    )


def test_independent_scalar_partial_has_nonluce_rum_witness():
    domain = (("a", "b"),)
    partial = projection(uniform(), domain)
    mixtures = rum_basic_mixtures(partial, domain)
    weights = scalar_weights(partial, domain)
    assert weights is not None
    assert positive_nonluce_rum_exists(mixtures, weights)


def test_independent_nonrum_completion_is_exact():
    domain = (("a", "b"),)
    partial = projection(uniform(), domain)
    completed = nonrum_extension(partial, domain)
    assert projection(completed, domain) == partial
    assert full_status(completed) == N


def test_independent_observed_violation_refutes_rum():
    bad = kernel(
        Q(1, 2), Q(1, 2), Q(1, 2), (Q(3, 4), Q(1, 8), Q(1, 8))
    )
    domain = (("a", "b"), ABC)
    assert rum_basic_mixtures(projection(bad, domain), domain) == ()


def test_independent_complete_controls_cover_all_tiers():
    scalar = uniform()
    middle = kernel(
        Q(2, 3), Q(1, 3), Q(2, 3), (Q(1, 3), Q(1, 3), Q(1, 3))
    )
    bad = kernel(
        Q(1, 2), Q(1, 2), Q(1, 2), (Q(3, 4), Q(1, 8), Q(1, 8))
    )
    assert (full_status(scalar), full_status(middle), full_status(bad)) == (
        L, R, N
    )
