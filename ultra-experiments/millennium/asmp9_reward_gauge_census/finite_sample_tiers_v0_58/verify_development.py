"""Independent development verifier for ASMP-9 v0.58."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from itertools import permutations
from math import comb


def induced_choice(weights):
    rankings = tuple(permutations(("a", "b", "c")))
    menus = (("a", "b"), ("a", "c"), ("b", "c"), ("a", "b", "c"))
    return {
        (menu, item): sum(
            weight
            for ranking, weight in zip(rankings, weights)
            if next(x for x in ranking if x in menu) == item
        )
        for menu in menus
        for item in menu
    }


def condition(s, r):
    if s <= r:
        return 1
    return sum(
        comb(s, u) * comb(s - u - 1, r - u) for u in range(r + 1)
    )


def main():
    path_checks = 0
    for denominator in (10**2, 10**3, 10**4, 10**5):
        eta = Fraction(1, denominator)
        weights = (
            Fraction(1, 6),
            Fraction(1, 6) - eta,
            Fraction(1, 6) + eta,
            Fraction(1, 6) - eta,
            Fraction(1, 6) + eta,
            Fraction(1, 6),
        )
        kernel = induced_choice(weights)
        assert all(
            kernel[(menu, item)] == Fraction(1, 2)
            for menu in (("a", "b"), ("a", "c"), ("b", "c"))
            for item in menu
        )
        assert tuple(
            kernel[(("a", "b", "c"), item)] for item in ("a", "b", "c")
        ) == (Fraction(1, 3) - eta, Fraction(1, 3), Fraction(1, 3) + eta)
        path_checks += 1

    boundary_weights = (
        Fraction(1, 5),
        Fraction(1, 5),
        Fraction(1, 5),
        Fraction(1, 5),
        Fraction(0),
        Fraction(1, 5),
    )
    boundary = induced_choice(boundary_weights)
    assert boundary[(("a", "b"), "a")] == boundary[
        (("a", "b", "c"), "a")
    ] == Fraction(2, 5)
    for denominator in (10**2, 10**3, 10**4, 10**5):
        epsilon = Fraction(1, denominator)
        assert boundary[(("a", "b", "c"), "a")] + epsilon > boundary[
            (("a", "b"), "a")
        ]
        path_checks += 1

    margin_lower_bound_checks = 0
    binary_cycle_left = (
        boundary[(("a", "b"), "a")]
        * boundary[(("b", "c"), "b")]
        * boundary[(("a", "c"), "c")]
    )
    binary_cycle_right = (
        boundary[(("a", "b"), "b")]
        * boundary[(("b", "c"), "c")]
        * boundary[(("a", "c"), "a")]
    )
    assert abs(binary_cycle_left - binary_cycle_right) == Fraction(6, 125)
    for gamma in (Fraction(1, 10_000), Fraction(1, 1_000), Fraction(1, 125)):
        epsilon = 2 * gamma
        perturbed = dict(boundary)
        perturbed[(("a", "b", "c"), "a")] += epsilon
        perturbed[(("a", "b", "c"), "b")] -= epsilon
        regularity_violation = (
            perturbed[(("a", "b", "c"), "a")]
            - perturbed[(("a", "b"), "a")]
        )
        assert regularity_violation == 2 * gamma
        divergence = -2 / 5 * math.log1p(-25 * float(gamma) ** 2)
        necessary = math.ceil(2 * 0.9**2 / divergence)
        if necessary > 1:
            lower_error = (
                1 - math.sqrt((necessary - 1) * divergence / 2)
            ) / 2
            assert lower_error > 0.05
        margin_lower_bound_checks += 1

    lower_bound_checks = 0
    for budget in (1, 10, 10**3, 10**6, 10**9):
        for target in (0.01, 0.1, 0.25, 0.49):
            v = 1 - 2 * target
            eta = min(
                1 / 12,
                math.sqrt(-math.expm1(-6 * v * v / budget)) / 6,
            )
            divergence = -budget * math.log1p(-9 * eta * eta) / 3
            lecam = (1 - math.sqrt(divergence / 2)) / 2
            assert lecam > target
            lower_bound_checks += 1

    condition_checks = 0
    for n in range(3, 13):
        for r in range(n - 1):
            values = [condition(s, r) for s in range(n - 1)]
            assert all(value >= 1 for value in values)
            if r == n - 2:
                assert max(values) == 1
            condition_checks += 1

    print(
        json.dumps(
            {
                "status": "development_checks_passed",
                "registered": False,
                "close_path_checks": path_checks,
                "lecam_budget_target_checks": lower_bound_checks,
                "margin_lower_bound_checks": margin_lower_bound_checks,
                "condition_grid_checks": condition_checks,
                "maximum_n": 12,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
