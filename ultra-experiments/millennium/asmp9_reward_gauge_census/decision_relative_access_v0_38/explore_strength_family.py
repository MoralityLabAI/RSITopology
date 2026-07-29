"""Burned sweep of the symmetric two-target-query family."""

from __future__ import annotations

import json
from fractions import Fraction as Q

from relative_deficiency import (
    independent_binary_product,
    ordinary_deficiency,
    optimized_value_gap,
    policy_regret_problem,
    relative_deficiency,
)


CASES = (
    (Q(2, 3), Q(1, 3)),
    (Q(3, 4), Q(1, 4)),
    (Q(4, 5), Q(1, 5)),
    (Q(3, 5), Q(2, 5)),
)


def qstr(value: Q) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def run_case(high: Q, low: Q) -> dict:
    occupancies = (
        (Q(1), Q(0), Q(0)),
        (Q(0), Q(1), Q(0)),
        (Q(0), Q(0), Q(1)),
    )
    problem = policy_regret_problem("three_policy_regret", occupancies, occupancies)
    q0 = (high, low, low)
    q1 = (low, high, low)
    full = independent_binary_product((q0, q1))
    source = independent_binary_product((q1,))
    relative = relative_deficiency(source, full, (problem,))
    ordinary = ordinary_deficiency(source, full)
    return {
        "high": qstr(high),
        "low": qstr(low),
        "gap": qstr(high - low),
        "half_gap": qstr((high - low) / 2),
        "optimized_value_gap": qstr(
            optimized_value_gap(source, full, (problem,))
        ),
        "target_relative_deficiency": qstr(relative.epsilon),
        "ordinary_target_deficiency": qstr(ordinary.epsilon),
    }


def build_result() -> dict:
    return {
        "status": "burned_development_only",
        "rows": [run_case(high, low) for high, low in CASES],
    }


if __name__ == "__main__":
    print(json.dumps(build_result(), indent=2, sort_keys=True))

