from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "balanced_design_v0_16"
sys.path.insert(0, str(BASE))
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

from experiment import balanced_worst_closed, fraction_record  # noqa: E402


def logarithmic_total_threshold(
    length: int,
    epsilon: Fraction,
    target: Fraction,
    maximum_total: int = 10_000_000,
) -> dict[str, Any] | None:
    if length < 3:
        raise ValueError("length must be at least three")
    if not 0 <= epsilon <= Fraction(1, 2):
        raise ValueError("epsilon must lie in [0,1/2]")
    if not 0 <= target < 1:
        raise ValueError("target must lie in [0,1)")
    if epsilon == 0:
        return None

    cache: dict[int, Fraction] = {}

    def evaluate(total: int) -> Fraction:
        if total not in cache:
            cache[total] = balanced_worst_closed(
                total, length, epsilon
            )[0]
        return cache[total]

    minimum_value = evaluate(length)
    bracket_history = [
        {
            "total": length,
            "value": fraction_record(minimum_value),
            "passes": minimum_value >= target,
        }
    ]
    if minimum_value >= target:
        selected = length
    else:
        low = length
        high = 2 * length
        while high <= maximum_total:
            value = evaluate(high)
            bracket_history.append(
                {
                    "total": high,
                    "value": fraction_record(value),
                    "passes": value >= target,
                }
            )
            if value >= target:
                break
            low = high
            high *= 2
        else:
            return None

        while high - low > 1:
            middle = (low + high) // 2
            value = evaluate(middle)
            if value >= target:
                high = middle
            else:
                low = middle
        selected = high

    current = evaluate(selected)
    predecessor = (
        Fraction(0)
        if selected == length
        else evaluate(selected - 1)
    )
    evaluated_points = [
        {
            "total": total,
            "value": fraction_record(value),
            "passes": value >= target,
        }
        for total, value in sorted(cache.items())
    ]
    traversed_values_monotone = all(
        left["value"]["decimal"] <= right["value"]["decimal"]
        and cache[left["total"]] <= cache[right["total"]]
        for left, right in zip(
            evaluated_points, evaluated_points[1:], strict=False
        )
    )
    return {
        "cycle_length": length,
        "epsilon": fraction_record(epsilon),
        "target": fraction_record(target),
        "minimum_total_trials": selected,
        "predecessor": fraction_record(predecessor),
        "current": fraction_record(current),
        "straddles": predecessor < target <= current,
        "bracket_history": bracket_history,
        "evaluated_points": evaluated_points,
        "exact_evaluation_count": len(cache),
        "logarithmic_evaluation_bound": (
            3 + 2 * max(1, selected.bit_length())
        ),
        "within_evaluation_bound": (
            len(cache) <= 3 + 2 * max(1, selected.bit_length())
        ),
        "traversed_values_monotone": traversed_values_monotone,
    }
