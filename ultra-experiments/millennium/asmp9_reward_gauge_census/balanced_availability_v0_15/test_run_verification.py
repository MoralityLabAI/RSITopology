from __future__ import annotations

import json
from fractions import Fraction

from verify_result import (
    independent_allocation_optimum,
    independent_availability,
    independent_sharp,
)


def test_independent_sharp_matches_explicit_middle_vertex() -> None:
    k = 7
    n = 5
    epsilon = Fraction(1, 5)
    direct = independent_availability(
        (n,) * k,
        (epsilon,) * (k // 2)
        + (1 - epsilon,) * (k - k // 2),
    )
    assert independent_sharp(k, n, epsilon) == direct


def test_independent_allocation_optimum_accepts_balancing_cell() -> None:
    optimum, balanced = independent_allocation_optimum(
        8, 4, Fraction(1, 5)
    )
    assert optimum == balanced


def test_protocol_json_has_nine_unique_gates() -> None:
    from run_verification import HERE

    protocol = json.loads(
        (HERE / "protocol_v0_15.json").read_text(encoding="utf-8")
    )
    assert len(protocol["gate_ids"]) == 9
    assert len(set(protocol["gate_ids"])) == 9


def test_fresh_registry_is_disjoint_from_burned_core_values() -> None:
    from run_verification import HERE

    protocol = json.loads(
        (HERE / "protocol_v0_15.json").read_text(encoding="utf-8")
    )
    assert set(protocol["theorem_registry"]["cycle_lengths"]).isdisjoint(
        range(3, 11)
    )
    assert set(protocol["theorem_registry"]["trials_per_edge"]).isdisjoint(
        range(1, 9)
    )
    assert set(protocol["theorem_registry"]["epsilon"]).isdisjoint(
        {"1/20", "1/10", "1/5", "1/4", "2/5"}
    )
    assert set(protocol["threshold_registry"]["delta"]).isdisjoint(
        {"1/5", "1/10", "1/20", "1/100"}
    )
    assert set(protocol["allocation_registry"]["epsilon"]).isdisjoint(
        {"1/20", "1/10", "1/5", "1/4", "2/5", "3/20", "3/10"}
    )
