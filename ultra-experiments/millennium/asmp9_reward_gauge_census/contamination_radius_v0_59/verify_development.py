"""Import-independent development verifier for ASMP-9 v0.59."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from itertools import product
from math import comb


def simplex(denominator, dimension):
    for numerators in product(range(denominator + 1), repeat=dimension):
        if sum(numerators) == denominator:
            yield tuple(Fraction(value, denominator) for value in numerators)


def tv(left, right):
    return sum(abs(a - b) for a, b in zip(left, right)) / 2


def condition(s, r):
    if s <= r:
        return 1
    return sum(
        comb(s, u) * comb(s - u - 1, r - u)
        for u in range(r + 1)
    )


def main():
    overlap_checks = 0
    construction_checks = 0
    distributions = tuple(simplex(5, 3))
    for left in distributions:
        for right in distributions:
            distance = tv(left, right)
            threshold = distance / (1 + distance)
            for epsilon in (
                Fraction(0),
                threshold / 2,
                threshold,
                (threshold + 1) / 2,
            ):
                overlap = (1 - epsilon) * distance <= epsilon
                assert overlap == (epsilon >= threshold)
                overlap_checks += 1
                if not overlap or epsilon == 0:
                    continue
                observed = [
                    (1 - epsilon) * max(a, b)
                    for a, b in zip(left, right)
                ]
                observed[0] += 1 - sum(observed)
                left_bad = tuple(
                    (value - (1 - epsilon) * clean) / epsilon
                    for value, clean in zip(observed, left)
                )
                right_bad = tuple(
                    (value - (1 - epsilon) * clean) / epsilon
                    for value, clean in zip(observed, right)
                )
                assert min(left_bad) >= 0 and sum(left_bad) == 1
                assert min(right_bad) >= 0 and sum(right_bad) == 1
                assert tuple(
                    (1 - epsilon) * clean + epsilon * bad
                    for clean, bad in zip(left, left_bad)
                ) == tuple(observed)
                assert tuple(
                    (1 - epsilon) * clean + epsilon * bad
                    for clean, bad in zip(right, right_bad)
                ) == tuple(observed)
                construction_checks += 1

    kernel_checks = 0
    kernels = (
        (
            (Fraction(1, 2), Fraction(1, 2)),
            (Fraction(3, 5), Fraction(1, 5), Fraction(1, 5)),
        ),
        (
            (Fraction(1, 2), Fraction(1, 2)),
            (Fraction(2, 5), Fraction(2, 5), Fraction(1, 5)),
        ),
    )
    kernel_distance = max(
        tv(left_menu, right_menu)
        for left_menu, right_menu in zip(*kernels)
    )
    assert kernel_distance == Fraction(1, 5)
    kernel_threshold = kernel_distance / (1 + kernel_distance)
    assert kernel_threshold == Fraction(1, 6)
    for epsilon, expected in (
        (Fraction(1, 7), False),
        (Fraction(1, 6), True),
        (Fraction(1, 5), True),
    ):
        assert ((1 - epsilon) * kernel_distance <= epsilon) is expected
        kernel_checks += 1

    witness_checks = 0
    for gamma in (Fraction(1, 1000), Fraction(1, 250), Fraction(1, 125)):
        left = (Fraction(2, 5), Fraction(2, 5), Fraction(1, 5))
        right = (
            Fraction(2, 5) + 2 * gamma,
            Fraction(2, 5) - 2 * gamma,
            Fraction(1, 5),
        )
        assert tv(left, right) == 2 * gamma
        epsilon = 2 * gamma / (1 + 2 * gamma)
        observed = tuple(
            value / (1 + 2 * gamma)
            for value in (Fraction(2, 5) + 2 * gamma, Fraction(2, 5), Fraction(1, 5))
        )
        assert observed == tuple(
            (1 - epsilon) * clean + epsilon * bad
            for clean, bad in zip(left, (1, 0, 0))
        )
        assert observed == tuple(
            (1 - epsilon) * clean + epsilon * bad
            for clean, bad in zip(right, (0, 1, 0))
        )
        witness_checks += 1

    modulus_checks = 0
    for n in range(3, 11):
        for degree in range(n - 1):
            maximum = max(condition(s, degree) for s in range(n - 1))
            for probability_floor, gamma in ((0.2, 0.2), (0.05, 0.1)):
                observed_gap = probability_floor * (
                    1 - math.exp(-math.atanh(gamma / 2) / maximum)
                )
                epsilon = observed_gap / (1 + observed_gap)
                assert math.isclose(
                    epsilon / (1 - epsilon),
                    observed_gap,
                    rel_tol=1e-12,
                    abs_tol=1e-15,
                )
                modulus_checks += 1

    sampling_cells = (
        (3, 1, 0.20, 0.20, 0.05, 68_407, 121_613, 1_094_512),
        (5, 1, 0.05, 0.10, 0.01, 166_308_762, 295_660_022, 2_660_940_192),
        (
            6,
            2,
            0.02,
            0.05,
            0.05,
            45_274_968_354,
            80_488_832_628,
            724_399_493_649,
        ),
        (
            8,
            4,
            0.01,
            0.02,
            0.01,
            91_037_884_048_966,
            161_845_127_198_162,
            1_456_606_144_783_453,
        ),
    )
    table_checks = 0
    for (
        n,
        degree,
        probability_floor,
        gamma,
        delta,
        expected_n0,
        expected_n25,
        expected_n75,
    ) in sampling_cells:
        maximum = max(condition(s, degree) for s in range(n - 1))
        clean_tolerance = probability_floor * (
            1 - math.exp(-math.atanh(gamma / 6) / maximum)
        )
        coordinates = sum(
            size * comb(n, size)
            for size in range(2, min(n, degree + 2) + 1)
        )
        counts = []
        for fraction in (0.0, 0.25, 0.75):
            sampling_tolerance = clean_tolerance * (1 - fraction)
            real_bound = math.log(2 * coordinates / delta) / (
                2 * sampling_tolerance**2
            )
            counts.append(math.floor(real_bound) + 1)
        assert tuple(counts) == (expected_n0, expected_n25, expected_n75)
        table_checks += 1

    sampling_checks = 0
    for n, degree, probability_floor, gamma, delta in (
        cell[:5] for cell in sampling_cells[:3]
    ):
        maximum = max(condition(s, degree) for s in range(n - 1))
        clean_tolerance = probability_floor * (
            1 - math.exp(-math.atanh(gamma / 6) / maximum)
        )
        epsilon = clean_tolerance / 4
        sampling_tolerance = clean_tolerance - epsilon
        coordinates = sum(
            size * comb(n, size)
            for size in range(2, min(n, degree + 2) + 1)
        )
        real_bound = math.log(2 * coordinates / delta) / (
            2 * sampling_tolerance**2
        )
        count = math.floor(real_bound) + 1
        empirical_error = math.sqrt(
            math.log(2 * coordinates / delta) / (2 * count)
        )
        total_error = epsilon + empirical_error
        assert total_error < clean_tolerance
        log_error = -2 * maximum * math.log(
            1 - total_error / probability_floor
        )
        l1_bound = 2 * math.tanh(log_error / 2)
        assert l1_bound < gamma / 3
        sampling_checks += 1

    print(
        json.dumps(
            {
                "status": "development_checks_passed",
                "registered": False,
                "overlap_checks": overlap_checks,
                "construction_checks": construction_checks,
                "kernel_checks": kernel_checks,
                "witness_checks": witness_checks,
                "modulus_checks": modulus_checks,
                "sampling_checks": sampling_checks,
                "table_checks": table_checks,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
