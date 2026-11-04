"""Import-independent development verifier for ASMP-9 v0.60."""

from __future__ import annotations

import json
import math
from fractions import Fraction
from itertools import product


def positive_simplex(denominator, dimension):
    for numerators in product(range(1, denominator), repeat=dimension):
        if sum(numerators) == denominator:
            yield tuple(Fraction(value, denominator) for value in numerators)


def main():
    preselection_checks = 0
    kernels = (
        (
            (Fraction(1, 2), Fraction(1, 2)),
            (Fraction(1, 3), Fraction(2, 3)),
            (Fraction(1, 5), Fraction(2, 5), Fraction(2, 5)),
        ),
        (
            (Fraction(2, 3), Fraction(1, 3)),
            (Fraction(3, 4), Fraction(1, 4)),
            (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)),
        ),
    )
    selections = (
        (Fraction(2, 7), Fraction(0), Fraction(5, 7)),
        (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)),
    )
    for kernel in kernels:
        for selection in selections:
            joint = tuple(
                tuple(menu_probability * response for response in menu)
                for menu_probability, menu in zip(selection, kernel)
            )
            recovered_selection = tuple(sum(menu) for menu in joint)
            assert recovered_selection == selection
            for probability, clean, menu_joint in zip(selection, kernel, joint):
                if probability == 0:
                    continue
                recovered = tuple(value / probability for value in menu_joint)
                assert recovered == clean
            preselection_checks += 1

    confounding_checks = 0
    distributions = tuple(positive_simplex(7, 3))
    target = (Fraction(1, 3),) * 3
    for left in distributions:
        for right in distributions:
            largest_rate = min(
                tuple(source / q for source, q in zip(left, target))
                + tuple(source / q for source, q in zip(right, target))
            )
            record_rate = min(Fraction(1), largest_rate) / 2
            left_recording = tuple(
                record_rate * q / source
                for source, q in zip(left, target)
            )
            right_recording = tuple(
                record_rate * q / source
                for source, q in zip(right, target)
            )
            assert min(left_recording + right_recording) > 0
            assert max(left_recording + right_recording) <= 1
            left_joint = tuple(
                source * recording
                for source, recording in zip(left, left_recording)
            )
            right_joint = tuple(
                source * recording
                for source, recording in zip(right, right_recording)
            )
            assert left_joint == right_joint
            assert sum(left_joint) == record_rate
            assert tuple(value / record_rate for value in left_joint) == target
            confounding_checks += 1

    correction_checks = 0
    for clean in distributions:
        record_rate = Fraction(1, 7)
        largest_allowed = min(
            source / q for source, q in zip(clean, target)
        )
        if record_rate > largest_allowed:
            continue
        recording = tuple(
            record_rate * q / source
            for source, q in zip(clean, target)
        )
        joint = tuple(
            source * probability
            for source, probability in zip(clean, recording)
        )
        recovered = tuple(
            mass / probability
            for mass, probability in zip(joint, recording)
        )
        assert recovered == clean
        correction_checks += 1

    bounded_radius_checks = 0
    for left in distributions:
        for right in distributions:
            required = max(
                max(a / b, b / a)
                for a, b in zip(left, right)
            )
            for lower, upper in (
                (Fraction(1), Fraction(1)),
                (Fraction(3, 4), Fraction(1)),
                (Fraction(1, 2), Fraction(1)),
                (Fraction(1, 4), Fraction(3, 4)),
            ):
                overlaps = required <= upper / lower
                intervals_overlap = all(
                    max(lower * a, lower * b)
                    <= min(upper * a, upper * b)
                    for a, b in zip(left, right)
                )
                assert overlaps == intervals_overlap
                if overlaps:
                    joint = tuple(
                        max(lower * a, lower * b)
                        for a, b in zip(left, right)
                    )
                    left_recording = tuple(
                        mass / clean
                        for mass, clean in zip(joint, left)
                    )
                    right_recording = tuple(
                        mass / clean
                        for mass, clean in zip(joint, right)
                    )
                    assert all(
                        lower <= value <= upper
                        for value in left_recording + right_recording
                    )
                bounded_radius_checks += 1

    margin_radius_checks = 0
    for gamma in (0.01, 0.05, 0.2, 0.5):
        ratio = (2 + gamma) / (2 - gamma)
        assert math.isclose(
            2 * math.tanh(math.log(ratio) / 2),
            gamma,
            rel_tol=1e-12,
        )
        margin_radius_checks += 1

    witness_radius_checks = 0
    for gamma in (Fraction(1, 1000), Fraction(1, 250), Fraction(1, 125)):
        left = (Fraction(2, 5), Fraction(2, 5), Fraction(1, 5))
        right = (
            Fraction(2, 5) + 2 * gamma,
            Fraction(2, 5) - 2 * gamma,
            Fraction(1, 5),
        )
        required = max(
            max(a / b, b / a)
            for a, b in zip(left, right)
        )
        assert required == 1 / (1 - 5 * gamma)
        witness_radius_checks += 1

    rate_checks = 0
    probability_floor = 0.2
    gamma_for_upper = 0.2
    response_delta = 0.025
    coordinate_count = 9
    clean_tolerance = probability_floor * (
        1 - math.exp(-math.atanh(gamma_for_upper / 6))
    )
    per_menu_count = math.ceil(
        math.log(2 * coordinate_count / response_delta)
        / (2 * clean_tolerance**2)
    )
    assert per_menu_count == 76_463
    expected_totals = {
        0.25: 611_704,
        0.10: 1_529_260,
        0.05: 3_058_520,
        0.01: 15_292_600,
        0.001: 152_926_000,
    }
    for selection_floor, expected in expected_totals.items():
        total = math.ceil(
            max(
                2 * per_menu_count / selection_floor,
                8
                / selection_floor
                * math.log(4 / 0.025),
            )
        )
        assert total == expected
        rate_checks += 1

    lower_rate_checks = 0
    gamma = 1 / 250
    informative_kl = -2 / 5 * math.log1p(-25 * gamma * gamma)
    previous = None
    for selection_floor in (0.25, 0.10, 0.05, 0.01, 0.001):
        bound = (
            2 * (1 - 2 * 0.1) ** 2
            / (selection_floor * informative_kl)
        )
        if previous is not None:
            previous_floor, previous_bound = previous
            assert math.isclose(
                bound / previous_bound,
                previous_floor / selection_floor,
                rel_tol=1e-12,
            )
        previous = selection_floor, bound
        lower_rate_checks += 1

    tier_handoff_checks = 0
    handoff = {
        (False, False): ("N",),
        (True, False): ("R", "N"),
        (True, True): ("L", "R", "N"),
    }
    for (has_rum, has_luce), tiers in handoff.items():
        assert (has_luce <= has_rum) or (has_luce is False)
        assert len(tiers) in (1, 2, 3)
        tier_handoff_checks += 1

    print(
        json.dumps(
            {
                "bounded_radius_checks": bounded_radius_checks,
                "confounding_checks": confounding_checks,
                "correction_checks": correction_checks,
                "lower_rate_checks": lower_rate_checks,
                "margin_radius_checks": margin_radius_checks,
                "preselection_checks": preselection_checks,
                "rate_checks": rate_checks,
                "registered": False,
                "status": "development_checks_passed",
                "tier_handoff_checks": tier_handoff_checks,
                "witness_radius_checks": witness_radius_checks,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
