"""Import-independent finite audit of the v0.62 exact modulus slice."""

from __future__ import annotations

from fractions import Fraction as Q
from itertools import permutations
import json


RANKINGS = tuple(permutations(range(3)))
GAMMAS = (Q(1, 4096), Q(3, 1600), Q(1, 200), Q(1, 128))


def induced(weights):
    menus = ((0, 1), (0, 2), (1, 2), (0, 1, 2))
    return {
        (menu, item): sum(
            weight
            for ranking, weight in zip(RANKINGS, weights)
            if next(x for x in ranking if x in menu) == item
        )
        for menu in menus
        for item in menu
    }


def tv(left, right):
    return sum(abs(a - b) for a, b in zip(left, right)) / 2


def main():
    tier_checks = 0
    modulus_checks = 0
    corruption_checks = 0
    for gamma in GAMMAS:
        for t in (Q(0), gamma / 4, gamma / 2):
            weights = (
                Q(1, 5) + t,
                Q(1, 5) - t,
                Q(1, 5),
                Q(1, 5) - t,
                Q(0),
                Q(1, 5) + t,
            )
            kernel = induced(weights)
            assert tuple(
                kernel[((0, 1, 2), item)] for item in range(3)
            ) == (Q(2, 5), Q(2, 5) - t, Q(1, 5) + t)
            tier_checks += 1

        t_star = Q(5, 2) * gamma * gamma
        p = (Q(2, 5), Q(2, 5) - t_star, Q(1, 5) + t_star)
        q = (Q(2, 5) + gamma, Q(2, 5) - gamma, Q(1, 5))
        assert tv(p, q) == gamma
        ratios = [max(a / b, b / a) for a, b in zip(p, q)]
        expected_ratio = 1 + Q(5, 2) * gamma
        assert max(ratios) == expected_ratio
        assert ratios[0] == ratios[1] == expected_ratio
        assert ratios[2] <= expected_ratio
        modulus_checks += 1

        epsilon = gamma / (1 + gamma)
        observed = [(1 - epsilon) * max(a, b) for a, b in zip(p, q)]
        observed[0] += 1 - sum(observed)
        for clean in (p, q):
            bad = tuple(
                (value - (1 - epsilon) * source) / epsilon
                for value, source in zip(observed, clean)
            )
            assert min(bad) >= 0 and sum(bad) == 1

        lower = 1 / expected_ratio
        joint = tuple(max(lower * a, lower * b) for a, b in zip(p, q))
        for clean in (p, q):
            recording = tuple(value / source for value, source in zip(joint, clean))
            assert min(recording) >= lower and max(recording) <= 1
        corruption_checks += 1

    print(
        json.dumps(
            {
                "corruption_checks": corruption_checks,
                "gamma_cells": len(GAMMAS),
                "modulus_checks": modulus_checks,
                "registered": False,
                "status": "development_checks_passed",
                "tier_checks": tier_checks,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

