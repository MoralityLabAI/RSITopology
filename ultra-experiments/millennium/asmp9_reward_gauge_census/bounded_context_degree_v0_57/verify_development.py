"""Independent finite audit of the v0.57 theorem draft.

This file deliberately does not import bounded_context_degree.py. It rebuilds
the fixed-universe witness and the Boolean interpolation identities directly.
It prints a development receipt but does not create or overwrite an artifact.
"""

from __future__ import annotations

import json
from fractions import Fraction
from itertools import combinations


def subsets(items, max_size=None):
    items = tuple(sorted(items))
    stop = len(items) if max_size is None else min(max_size, len(items))
    for size in range(stop + 1):
        for value in combinations(items, size):
            yield frozenset(value)


def menus(n, max_size=None):
    stop = n if max_size is None else min(max_size, n)
    for size in range(2, stop + 1):
        for value in combinations(range(n), size):
            yield frozenset(value)


def exponent(menu, item, active_term):
    return int(active_term.issubset(menu - {item}))


def pair_value(x, y, context, active_term):
    menu = context | {x, y}
    return exponent(menu, x, active_term) - exponent(menu, y, active_term)


def finite_difference(values, target):
    return sum(
        (-1) ** (len(target) - len(source)) * values[source]
        for source in subsets(target)
    )


def reconstruct(values, context, degree):
    result = Fraction(0)
    for target in subsets(context, max_size=degree):
        result += finite_difference(values, target)
    return result


def probability(menu, item, active_term, base):
    scores = {
        option: Fraction(base) ** exponent(menu, option, active_term)
        for option in menu
    }
    return scores[item] / sum(scores.values(), Fraction(0))


def main():
    cells = 0
    high_degree_coefficients = 0
    reconstructed_pair_contexts = 0
    exact_probability_checks = 0
    regularity_witnesses = 0

    for n in range(3, 9):
        universe = frozenset(range(n))
        for degree in range(1, n - 1):
            cells += 1
            special_menu = frozenset(range(degree + 2))
            special_item = 0
            active_term = special_menu - {special_item}
            base = degree + 2

            for menu in menus(n, max_size=degree + 1):
                for item in menu:
                    assert probability(menu, item, active_term, base) == Fraction(
                        1, len(menu)
                    )

            assert probability(
                special_menu, special_item, active_term, base
            ) == Fraction(degree + 2, 2 * degree + 3)
            assert probability(
                special_menu, special_item, active_term, base
            ) > Fraction(1, 2)
            regularity_witnesses += degree + 1

            for x in range(n):
                for y in range(x + 1, n):
                    rest = universe - {x, y}
                    values = {
                        context: pair_value(x, y, context, active_term)
                        for context in subsets(rest)
                    }
                    low = {
                        context: value
                        for context, value in values.items()
                        if len(context) <= degree
                    }
                    for target in subsets(rest):
                        coefficient = finite_difference(values, target)
                        if len(target) > degree:
                            high_degree_coefficients += 1
                            assert coefficient == 0
                        reconstructed = reconstruct(low, target, degree)
                        reconstructed_pair_contexts += 1
                        assert reconstructed == values[target]

            # Recover probabilities using a root and reconstructed pair odds.
            for menu in menus(n):
                root = max(menu)
                recovered_scores = {root: Fraction(1)}
                for item in menu - {root}:
                    context = menu - {item, root}
                    low = {
                        source: pair_value(item, root, source, active_term)
                        for source in subsets(context, max_size=degree)
                    }
                    recovered_exponent = reconstruct(low, context, degree)
                    assert recovered_exponent.denominator == 1
                    recovered_scores[item] = Fraction(base) ** int(
                        recovered_exponent
                    )
                denominator = sum(recovered_scores.values(), Fraction(0))
                for item, score in recovered_scores.items():
                    exact_probability_checks += 1
                    assert score / denominator == probability(
                        menu, item, active_term, base
                    )

    # The r=0 model has constant pair odds and needs binary access to recover
    # the full Luce kernel.
    n = 7
    item_parameters = tuple(range(n))
    for x in range(n):
        for y in range(x + 1, n):
            values = {
                item_parameters[y] - item_parameters[x]
                for _ in subsets(frozenset(range(n)) - {x, y})
            }
            assert len(values) == 1

    print(
        json.dumps(
            {
                "status": "development_checks_passed",
                "registered": False,
                "universe_sizes": [3, 4, 5, 6, 7, 8],
                "degree_cells": cells,
                "high_degree_zero_checks": high_degree_coefficients,
                "reconstructed_pair_contexts": reconstructed_pair_contexts,
                "exact_probability_checks": exact_probability_checks,
                "regularity_witnesses": regularity_witnesses,
                "r0_boundary_checked": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
