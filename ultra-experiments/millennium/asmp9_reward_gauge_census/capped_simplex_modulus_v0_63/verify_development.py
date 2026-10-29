"""Import-independent exact development audit for ASMP-9 v0.63."""

from __future__ import annotations

import json
from fractions import Fraction as Q
from itertools import combinations


CAPS = (Q(2, 5), Q(3, 5), Q(2, 5))
GAMMAS = (Q(1, 4096), Q(3, 1600), Q(1, 200), Q(1, 50))


def ratio(left, right):
    return max(
        max(a / b, b / a)
        for a, b in zip(left, right)
    )


def tv(left, right):
    return sum(abs(a - b) for a, b in zip(left, right)) / 2


def supports():
    answer = []
    for size in range(1, 4):
        for support in combinations(range(3), size):
            if sum((CAPS[index] for index in support), Q(0)) < 1:
                answer.append(support)
    return tuple(answer)


def support_bound(gamma, support):
    cap_sum = sum((CAPS[index] for index in support), Q(0))
    return max(
        1 + gamma / cap_sum,
        (1 - cap_sum) / (1 - cap_sum - gamma),
    )


def main():
    checks = {
        "gamma_cells": 0,
        "primal_checks": 0,
        "support_checks": 0,
        "common_observation_checks": 0,
    }
    for gamma in GAMMAS:
        left = (Q(2, 5), Q(3, 10), Q(3, 10))
        right = (
            Q(2, 5) + gamma,
            Q(3, 10) - gamma / 2,
            Q(3, 10) - gamma / 2,
        )
        expected_delta = gamma
        expected_lambda = 1 + Q(5, 2) * gamma
        assert tv(left, right) == expected_delta
        assert ratio(left, right) == expected_lambda
        checks["primal_checks"] += 2

        bounds = {
            support: support_bound(gamma, support)
            for support in supports()
        }
        assert min(bounds.values()) == expected_lambda
        assert {
            sum((CAPS[index] for index in support), Q(0))
            for support in supports()
        } == {Q(2, 5), Q(3, 5), Q(4, 5)}
        checks["support_checks"] += len(bounds)

        epsilon = gamma / (1 + gamma)
        observed = tuple(
            max(a, b) / (1 + gamma)
            for a, b in zip(left, right)
        )
        assert sum(observed, Q(0)) == 1
        for clean in (left, right):
            contaminant = tuple(
                (
                    observed[index] - (1 - epsilon) * clean[index]
                )
                / epsilon
                for index in range(3)
            )
            assert min(contaminant) >= 0
            assert sum(contaminant, Q(0)) == 1
        checks["common_observation_checks"] += 2

        lower = 1 / expected_lambda
        joint = tuple(
            lower * max(a, b)
            for a, b in zip(left, right)
        )
        for clean in (left, right):
            recording = tuple(
                joint[index] / clean[index]
                for index in range(3)
            )
            assert all(lower <= value <= 1 for value in recording)
        checks["common_observation_checks"] += 2
        checks["gamma_cells"] += 1

    result = {
        **checks,
        "registered": False,
        "status": "development_checks_passed",
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

