from fractions import Fraction
from itertools import combinations

from bounded_context_degree import (
    kernel_from_lambdas,
    interpolation_coefficient,
    interpolation_linf_norm,
    max_pair_degree,
    menus,
    mobius_transform,
    observed_pair_exponents,
    pair_exponent,
    reconstruct_degree_r,
    reconstruct_kernel,
    regularity_violations,
    sharp_witness,
    subsets,
    uniform_kernel,
    zeta_value,
)


def test_exact_mobius_reconstruction_for_independent_polynomials():
    universe = frozenset(range(7))
    for degree in range(5):
        coefficients = {}
        for term in subsets(universe, max_size=degree):
            coefficients[term] = Fraction(
                (-1) ** len(term) * (1 + sum(term) + 2 * len(term)),
                3,
            )
        values = {
            context: zeta_value(coefficients, context) for context in subsets(universe)
        }
        recovered = mobius_transform(values, universe)
        assert all(
            recovered[term] == coefficients.get(term, Fraction(0))
            for term in subsets(universe)
        )
        observed = {
            context: value
            for context, value in values.items()
            if len(context) <= degree
        }
        assert all(
            reconstruct_degree_r(observed, context, degree) == values[context]
            for context in subsets(universe)
        )


def test_interpolation_error_constant_is_exact_and_attained():
    for context_size in range(1, 10):
        context = frozenset(range(context_size))
        for degree in range(context_size):
            observed = {}
            expected_norm = 0
            for source in subsets(context, max_size=degree):
                coefficient = interpolation_coefficient(
                    context_size, degree, len(source)
                )
                expected_norm += abs(coefficient)
                # This adversarial error pattern attains the operator norm.
                observed[source] = 1 if coefficient >= 0 else -1
            # Coefficients depend only on the cardinality of the observed
            # subset. Check one direct impulse at each cardinality rather than
            # redundantly recomputing every symmetric impulse.
            for observed_size in range(degree + 1):
                source = frozenset(range(observed_size))
                coefficient = interpolation_coefficient(
                    context_size, degree, observed_size
                )
                impulse = {
                    other: int(other == source)
                    for other in subsets(context, max_size=degree)
                }
                assert (
                    reconstruct_degree_r(impulse, context, degree) == coefficient
                )
            assert interpolation_linf_norm(context_size, degree) == expected_norm
            assert (
                reconstruct_degree_r(observed, context, degree) == expected_norm
            )


def test_fixed_universe_sharp_witness_all_registered_development_cells():
    for n in range(3, 9):
        for degree in range(1, n - 1):
            base, active_term, special_menu, special_item, kernel = sharp_witness(
                n, degree
            )
            uniform = uniform_kernel(n)
            assert base == degree + 2
            assert len(active_term) == degree + 1
            assert len(special_menu) == degree + 2

            for menu in menus(n, max_size=degree + 1):
                for item in menu:
                    assert kernel[(menu, item)] == uniform[(menu, item)]

            assert kernel[(special_menu, special_item)] > Fraction(1, 2)
            for other in special_menu - {special_item}:
                binary = frozenset({special_item, other})
                assert kernel[(binary, special_item)] == Fraction(1, 2)

            lambdas = {active_term: 1}
            assert max_pair_degree(n, degree, lambdas) <= degree
            violations = regularity_violations(kernel, n)
            assert any(
                small == frozenset({special_item, other})
                and large == special_menu
                and item == special_item
                for other in special_menu - {special_item}
                for small, large, item, _, _ in violations
            )


def test_exact_full_kernel_reconstruction_on_fixed_universe_witnesses():
    for n in range(3, 8):
        for degree in range(1, n - 1):
            base, active_term, _, _, kernel = sharp_witness(n, degree)
            lambdas = {active_term: 1}
            observed = observed_pair_exponents(n, degree, lambdas)
            assert reconstruct_kernel(n, degree, base, observed) == kernel


def test_general_integer_context_scores_reconstruct_exactly():
    n = 7
    for degree in (1, 2, 3):
        terms = list(combinations(range(n), degree + 1))
        lambdas = {
            frozenset(term): ((index * 5 + 3) % 7) - 3
            for index, term in enumerate(terms)
        }
        base = 3
        kernel = kernel_from_lambdas(n, degree, base, lambdas)
        observed = observed_pair_exponents(n, degree, lambdas)
        assert reconstruct_kernel(n, degree, base, observed) == kernel
        assert max_pair_degree(n, degree, lambdas) <= degree


def test_pair_exponent_has_the_registered_pure_degree_formula():
    n = 7
    degree = 3
    lambdas = {
        frozenset(term): index - 5
        for index, term in enumerate(combinations(range(n), degree + 1))
    }
    for x in range(n):
        for y in range(n):
            if x == y:
                continue
            rest = frozenset(range(n)) - {x, y}
            for context in subsets(rest):
                expected = sum(
                    lambdas.get(term | {y}, 0) - lambdas.get(term | {x}, 0)
                    for term in subsets(context)
                    if len(term) == degree
                )
                assert pair_exponent(x, y, context, degree, lambdas) == expected


def test_degree_zero_boundary_is_luce_and_binary_access_reconstructs():
    n = 6
    degree = 0
    lambdas = {
        frozenset({item}): coefficient
        for item, coefficient in enumerate((0, 1, -1, 2, -2, 3))
    }
    base = 2
    kernel = kernel_from_lambdas(n, degree, base, lambdas)
    observed = observed_pair_exponents(n, degree, lambdas)
    assert max_pair_degree(n, degree, lambdas) == 0
    assert reconstruct_kernel(n, degree, base, observed) == kernel

    # Degree-zero pair odds are independent of all remaining menu context.
    for x in range(n):
        for y in range(n):
            if x == y:
                continue
            rest = frozenset(range(n)) - {x, y}
            values = {
                pair_exponent(x, y, context, degree, lambdas)
                for context in subsets(rest)
            }
            assert len(values) == 1
