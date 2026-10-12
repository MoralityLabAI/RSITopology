"""Memoized independent cycle-total census for ASMP-9 v0.19.2."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

from finite_cactus_design import (
    balanced_allocation,
    bounded_compositions,
    cycle_worst_direct,
    product_fraction,
)


@dataclass(frozen=True)
class CachedExhaustiveResult:
    value: Fraction
    cycle_totals: tuple[tuple[int, ...], ...]
    allocations_evaluated: int
    independent_cycle_values_evaluated: int


def optimize_cycle_totals_cached_independent(
    cycle_lengths: Sequence[int],
    total_budget: int,
    epsilon: Fraction,
    bridge_count: int = 0,
) -> CachedExhaustiveResult:
    """Exhaust cycle-total vectors while memoizing exact local minima.

    The local table is independent of the compact Bellman factor: every entry
    is computed by enumerating all ``2**length`` endpoint-label assignments
    through ``cycle_worst_direct``.
    """

    lengths = tuple(int(length) for length in cycle_lengths)
    if not lengths or any(length < 3 for length in lengths):
        raise ValueError("cycle lengths must all be at least three")
    if bridge_count < 0:
        raise ValueError("bridge_count must be nonnegative")
    cycle_budget = int(total_budget) - bridge_count
    if cycle_budget < sum(lengths):
        raise ValueError("budget cannot supply one trial to every edge")

    local: dict[tuple[int, int], Fraction] = {}

    def local_value(length: int, total: int) -> Fraction:
        key = (length, total)
        if key not in local:
            local[key] = cycle_worst_direct(
                balanced_allocation(total, length), epsilon
            )[0]
        return local[key]

    rows: list[tuple[Fraction, tuple[int, ...]]] = []
    for totals in bounded_compositions(cycle_budget, lengths):
        rows.append(
            (
                product_fraction(
                    local_value(length, total)
                    for length, total in zip(
                        lengths, totals, strict=True
                    )
                ),
                totals,
            )
        )
    if not rows:
        raise ValueError("no feasible allocation")
    maximum = max(value for value, _ in rows)
    return CachedExhaustiveResult(
        value=maximum,
        cycle_totals=tuple(
            totals for value, totals in rows if value == maximum
        ),
        allocations_evaluated=len(rows),
        independent_cycle_values_evaluated=len(local),
    )
