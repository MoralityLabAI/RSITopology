"""Exact development helpers for ASMP-9 bounded context degree v0.57.

The numerical representation uses integer exponents of a common positive base
instead of floating-point logarithms. Boolean Mobius statements are therefore
checked exactly, while the induced choice probabilities are Fractions.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb
from typing import Dict, FrozenSet, Iterable, Iterator, Mapping, Tuple


Context = FrozenSet[int]
Menu = FrozenSet[int]
PairContext = Tuple[int, int, Context]
KernelKey = Tuple[Menu, int]


def subsets(items: Iterable[int], max_size: int | None = None) -> Iterator[Context]:
    ordered = tuple(sorted(items))
    stop = len(ordered) if max_size is None else min(max_size, len(ordered))
    for size in range(stop + 1):
        for subset in combinations(ordered, size):
            yield frozenset(subset)


def menus(n: int, max_size: int | None = None) -> Iterator[Menu]:
    stop = n if max_size is None else min(max_size, n)
    for size in range(2, stop + 1):
        for menu in combinations(range(n), size):
            yield frozenset(menu)


def mobius_transform(values: Mapping[Context, int | Fraction], universe: Context) -> Dict[Context, Fraction]:
    """Return exact Boolean Mobius coefficients on every subset of universe."""

    coefficients: Dict[Context, Fraction] = {}
    for target in subsets(universe):
        total = Fraction(0)
        for source in subsets(target):
            sign = -1 if (len(target) - len(source)) % 2 else 1
            total += sign * Fraction(values[source])
        coefficients[target] = total
    return coefficients


def zeta_value(coefficients: Mapping[Context, int | Fraction], context: Context) -> Fraction:
    return sum(
        (Fraction(value) for term, value in coefficients.items() if term.issubset(context)),
        Fraction(0),
    )


def reconstruct_degree_r(
    observed_values: Mapping[Context, int | Fraction],
    context: Context,
    degree: int,
) -> Fraction:
    """Interpolate one degree-at-most-r Boolean function from lower layers."""

    low_coefficients: Dict[Context, Fraction] = {}
    for target in subsets(context, max_size=degree):
        total = Fraction(0)
        for source in subsets(target):
            if source not in observed_values:
                raise KeyError(f"missing observed context {sorted(source)}")
            sign = -1 if (len(target) - len(source)) % 2 else 1
            total += sign * Fraction(observed_values[source])
        low_coefficients[target] = total
    return zeta_value(low_coefficients, context)


def interpolation_coefficient(context_size: int, degree: int, observed_size: int) -> int:
    """Coefficient of one observed value in extrapolation to a larger context."""

    if not 0 <= observed_size <= degree < context_size:
        raise ValueError("requires 0 <= observed_size <= degree < context_size")
    return (-1) ** (degree - observed_size) * comb(
        context_size - observed_size - 1,
        degree - observed_size,
    )


def interpolation_linf_norm(context_size: int, degree: int) -> int:
    """Exact l_infinity-to-absolute-error norm of Boolean extrapolation."""

    if context_size <= degree:
        return 1
    return sum(
        comb(context_size, observed_size)
        * abs(interpolation_coefficient(context_size, degree, observed_size))
        for observed_size in range(degree + 1)
    )


def score_exponent(
    menu: Menu,
    item: int,
    degree: int,
    lambdas: Mapping[Context, int],
) -> int:
    """Contextual score exponent used by the fixed-universe witness."""

    if item not in menu:
        raise ValueError("item must belong to menu")
    context = menu - {item}
    order = degree + 1
    return sum(
        coefficient
        for term, coefficient in lambdas.items()
        if len(term) == order and term.issubset(context)
    )


def pair_exponent(
    x: int,
    y: int,
    context: Context,
    degree: int,
    lambdas: Mapping[Context, int],
) -> int:
    """Formal base-b log odds for the contextual-score construction."""

    if x == y or x in context or y in context:
        raise ValueError("pair and context must be disjoint")
    menu = context | {x, y}
    return score_exponent(menu, x, degree, lambdas) - score_exponent(
        menu, y, degree, lambdas
    )


def kernel_from_lambdas(
    n: int,
    degree: int,
    base: int,
    lambdas: Mapping[Context, int],
) -> Dict[KernelKey, Fraction]:
    if base <= 1:
        raise ValueError("base must exceed one")
    kernel: Dict[KernelKey, Fraction] = {}
    for menu in menus(n):
        scores = {
            item: Fraction(base) ** score_exponent(menu, item, degree, lambdas)
            for item in menu
        }
        denominator = sum(scores.values(), Fraction(0))
        for item, score in scores.items():
            kernel[(menu, item)] = score / denominator
    return kernel


def uniform_kernel(n: int) -> Dict[KernelKey, Fraction]:
    return {
        (menu, item): Fraction(1, len(menu))
        for menu in menus(n)
        for item in menu
    }


def sharp_witness(
    n: int,
    degree: int,
) -> tuple[int, Context, Menu, int, Dict[KernelKey, Fraction]]:
    """Return the exact Luce-vs-non-RUM lower witness for degree >= 1."""

    if degree < 1 or n < degree + 2:
        raise ValueError("sharp tier witness requires n >= degree+2 and degree >= 1")
    special_menu = frozenset(range(degree + 2))
    special_item = 0
    active_term = special_menu - {special_item}
    base = degree + 2
    lambdas = {active_term: 1}
    return (
        base,
        active_term,
        special_menu,
        special_item,
        kernel_from_lambdas(n, degree, base, lambdas),
    )


def observed_pair_exponents(
    n: int,
    degree: int,
    lambdas: Mapping[Context, int],
) -> Dict[PairContext, int]:
    """All pairwise exponent values on contexts through the degree layer."""

    result: Dict[PairContext, int] = {}
    universe = frozenset(range(n))
    for x in range(n):
        for y in range(n):
            if x == y:
                continue
            rest = universe - {x, y}
            for context in subsets(rest, max_size=degree):
                result[(x, y, context)] = pair_exponent(
                    x, y, context, degree, lambdas
                )
    return result


def reconstruct_kernel(
    n: int,
    degree: int,
    base: int,
    observed: Mapping[PairContext, int | Fraction],
) -> Dict[KernelKey, Fraction]:
    """Recover every menu probability from contexts of size at most degree."""

    reconstructed: Dict[KernelKey, Fraction] = {}
    for menu in menus(n):
        root = max(menu)
        scores: Dict[int, Fraction] = {root: Fraction(1)}
        for item in menu - {root}:
            target_context = menu - {item, root}
            low_values = {
                context: observed[(item, root, context)]
                for context in subsets(target_context, max_size=degree)
            }
            exponent = reconstruct_degree_r(low_values, target_context, degree)
            if exponent.denominator != 1:
                raise ValueError("formal exponent is not integral")
            scores[item] = Fraction(base) ** int(exponent)
        denominator = sum(scores.values(), Fraction(0))
        for item, score in scores.items():
            reconstructed[(menu, item)] = score / denominator
    return reconstructed


def max_pair_degree(
    n: int,
    degree: int,
    lambdas: Mapping[Context, int],
) -> int:
    """Compute the largest nonzero Mobius order of the formal pair log odds."""

    universe = frozenset(range(n))
    maximum = -1
    for x in range(n):
        for y in range(x + 1, n):
            rest = universe - {x, y}
            values = {
                context: pair_exponent(x, y, context, degree, lambdas)
                for context in subsets(rest)
            }
            coefficients = mobius_transform(values, rest)
            nonzero = [len(term) for term, value in coefficients.items() if value]
            if nonzero:
                maximum = max(maximum, max(nonzero))
    return maximum


def regularity_violations(
    kernel: Mapping[KernelKey, Fraction],
    n: int,
) -> list[tuple[Menu, Menu, int, Fraction, Fraction]]:
    """List strict violations p(x|large) <= p(x|small)."""

    violations: list[tuple[Menu, Menu, int, Fraction, Fraction]] = []
    all_menus = tuple(menus(n))
    for small in all_menus:
        for large in all_menus:
            if not small < large:
                continue
            for item in small:
                p_large = kernel[(large, item)]
                p_small = kernel[(small, item)]
                if p_large > p_small:
                    violations.append((small, large, item, p_small, p_large))
    return violations
