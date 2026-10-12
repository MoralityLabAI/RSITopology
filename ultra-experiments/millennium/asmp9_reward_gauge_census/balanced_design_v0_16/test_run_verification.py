from __future__ import annotations

import json
from fractions import Fraction

from verify_result import (
    availability,
    balanced,
    compact_value,
    local_values,
    worst,
)


def test_independent_local_reduction_and_smoothing() -> None:
    epsilon = Fraction(1, 5)
    before = local_values(
        2, 8, epsilon, Fraction(3, 5), Fraction(4, 5), Fraction(1, 5)
    )
    after = local_values(
        3, 7, epsilon, Fraction(3, 5), Fraction(4, 5), Fraction(1, 5)
    )
    assert before[2] == min(before[:2])
    assert after[2] == min(after[:2])
    assert after[0] > before[0]
    assert after[1] > before[1]


def test_independent_compact_formula() -> None:
    epsilon = Fraction(1, 6)
    counts = balanced(13, 5)
    assert compact_value(13, 5, epsilon) == worst(counts, epsilon)


def test_availability_is_label_complement_invariant() -> None:
    counts = (2, 3, 5, 7)
    labels = (0, 1, 1, 0)
    complement = tuple(1 - label for label in labels)
    epsilon = Fraction(1, 4)
    assert availability(counts, epsilon, labels) == availability(
        counts, epsilon, complement
    )


def test_protocol_registry_is_disjoint_from_development_values() -> None:
    from run_verification import HERE

    protocol = json.loads(
        (HERE / "protocol_v0_16.json").read_text(encoding="utf-8")
    )
    assert set(protocol["pair_registry"]["epsilon"]).isdisjoint(
        {"1/100", "1/20", "1/8", "1/5", "1/3", "1/2"}
    )
    assert set(protocol["pair_registry"]["a"]).isdisjoint(range(1, 7))
    assert set(protocol["pair_registry"]["differences"]).isdisjoint(
        range(2, 8)
    )
    assert set(
        protocol["global_allocation_registry"]["extra_total_trials"]
    ).isdisjoint(range(0, 11))
    assert set(protocol["threshold_registry"]["delta"]).isdisjoint(
        {"1/5", "1/20", "1/100"}
    )
