"""Exact finite-alphabet ASMP-6 collusion/audit frontier.

This module intentionally works with opaque symbols.  It measures a registered
finite channel and does not generate linguistic encoders or token mappings.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Iterable, Sequence


ALPHABET_SIZE = 4
DENOMINATOR = 4
COVER = (Fraction(1, 4),) * ALPHABET_SIZE
DELTA_GRID = (Fraction(0), Fraction(1, 8), Fraction(1, 4), Fraction(1, 2))
AUDIT_CHARGE_GRID = tuple(range(ALPHABET_SIZE + 1))
COVERTNESS_REGIMES = ("mixture", "per_message")


Distribution = tuple[Fraction, ...]
CountDistribution = tuple[int, ...]
AuditMap = tuple[int, ...]


@dataclass(frozen=True)
class FrontierCell:
    covertness_regime: str
    delta: Fraction
    audit_charge: int
    minimax_error: Fraction
    eligible_code_count: int
    optimal_code_count: int
    optimal_code_hashes: tuple[str, ...]


def weak_compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for head in range(total + 1):
        for tail in weak_compositions(total - head, parts - 1):
            yield (head, *tail)


def encoder_laws() -> tuple[CountDistribution, ...]:
    return tuple(weak_compositions(DENOMINATOR, ALPHABET_SIZE))


def as_distribution(counts: CountDistribution) -> Distribution:
    if len(counts) != ALPHABET_SIZE or any(value < 0 for value in counts):
        raise ValueError("invalid count distribution")
    if sum(counts) != DENOMINATOR:
        raise ValueError("count distribution has the wrong denominator")
    return tuple(Fraction(value, DENOMINATOR) for value in counts)


def total_variation(left: Sequence[Fraction], right: Sequence[Fraction]) -> Fraction:
    if len(left) != len(right):
        raise ValueError("distribution dimensions differ")
    return sum((abs(a - b) for a, b in zip(left, right)), Fraction(0)) / 2


def mixture(p0: Sequence[Fraction], p1: Sequence[Fraction]) -> Distribution:
    return tuple((a + b) / 2 for a, b in zip(p0, p1))


def covertness(
    p0: Sequence[Fraction], p1: Sequence[Fraction], regime: str
) -> Fraction:
    if regime == "mixture":
        return total_variation(mixture(p0, p1), COVER)
    if regime == "per_message":
        return max(total_variation(p0, COVER), total_variation(p1, COVER))
    raise ValueError(f"unknown covertness regime: {regime}")


def chi_squared(
    numerator_law: Sequence[Fraction], denominator_law: Sequence[Fraction]
) -> Fraction | None:
    """Return chi^2(P||Q), or None when P is not supported by Q."""

    total = Fraction(0)
    for p, q in zip(numerator_law, denominator_law):
        if q == 0:
            if p != 0:
                return None
            continue
        total += (p - q) ** 2 / q
    return total


def audit_maps() -> tuple[AuditMap, ...]:
    return tuple(product(range(ALPHABET_SIZE), repeat=ALPHABET_SIZE))


def audit_charge(mapping: AuditMap) -> int:
    return sum(int(source != target) for source, target in enumerate(mapping))


def pushforward_counts(counts: CountDistribution, mapping: AuditMap) -> CountDistribution:
    if len(mapping) != ALPHABET_SIZE or any(
        target < 0 or target >= ALPHABET_SIZE for target in mapping
    ):
        raise ValueError("invalid audit map")
    output = [0] * ALPHABET_SIZE
    for source, count in enumerate(counts):
        output[mapping[source]] += count
    return tuple(output)


def minimax_binary_error(p0: Sequence[Fraction], p1: Sequence[Fraction]) -> Fraction:
    """Exact minimax error for a randomized binary decoder.

    The decision probability q_y may lie in [0,1].  A vertex optimum has every
    q_y integral except possibly one coordinate.  Enumerating those vertices
    gives an exact rational answer without a floating-point LP solver.
    """

    dimension = len(p0)
    if dimension != len(p1):
        raise ValueError("distribution dimensions differ")

    candidates: list[tuple[Fraction, ...]] = []
    for bits in product((Fraction(0), Fraction(1)), repeat=dimension):
        candidates.append(bits)

    for free_index in range(dimension):
        fixed_indices = [index for index in range(dimension) if index != free_index]
        for fixed_bits in product((Fraction(0), Fraction(1)), repeat=dimension - 1):
            q = [Fraction(0)] * dimension
            for index, bit in zip(fixed_indices, fixed_bits):
                q[index] = bit
            fixed_sum = sum(
                ((p0[index] + p1[index]) * q[index] for index in fixed_indices),
                Fraction(0),
            )
            coefficient = p0[free_index] + p1[free_index]
            if coefficient == 0:
                continue
            free_value = (Fraction(1) - fixed_sum) / coefficient
            if 0 <= free_value <= 1:
                q[free_index] = free_value
                candidates.append(tuple(q))

    best = Fraction(1)
    for q in candidates:
        error0 = sum((probability * decision for probability, decision in zip(p0, q)), Fraction(0))
        error1 = Fraction(1) - sum(
            (probability * decision for probability, decision in zip(p1, q)), Fraction(0)
        )
        best = min(best, max(error0, error1))
    return best


def code_fingerprint(p0_counts: CountDistribution, p1_counts: CountDistribution) -> str:
    """Stable opaque identifier; result artifacts never serialize codebooks."""

    import hashlib

    payload = ",".join(map(str, (*p0_counts, *p1_counts))).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def exact_frontier() -> tuple[FrontierCell, ...]:
    laws = encoder_laws()
    maps = audit_maps()
    risk_cache = {
        (left, right): minimax_binary_error(as_distribution(left), as_distribution(right))
        for left in laws
        for right in laws
    }

    code_rows: list[dict[str, object]] = []
    for p0_counts in laws:
        p0 = as_distribution(p0_counts)
        for p1_counts in laws:
            p1 = as_distribution(p1_counts)
            exact_charge_risks = [Fraction(0)] * (ALPHABET_SIZE + 1)
            for mapping in maps:
                charge = audit_charge(mapping)
                pushed = (
                    pushforward_counts(p0_counts, mapping),
                    pushforward_counts(p1_counts, mapping),
                )
                exact_charge_risks[charge] = max(exact_charge_risks[charge], risk_cache[pushed])
            worst_through_charge: list[Fraction] = []
            running = Fraction(0)
            for risk in exact_charge_risks:
                running = max(running, risk)
                worst_through_charge.append(running)
            code_rows.append(
                {
                    "mixture": covertness(p0, p1, "mixture"),
                    "per_message": covertness(p0, p1, "per_message"),
                    "risk": tuple(worst_through_charge),
                    "hash": code_fingerprint(p0_counts, p1_counts),
                }
            )

    cells: list[FrontierCell] = []
    for regime in COVERTNESS_REGIMES:
        for delta in DELTA_GRID:
            eligible = [row for row in code_rows if row[regime] <= delta]
            if not eligible:
                raise AssertionError("registered grid unexpectedly has no eligible code")
            for charge in AUDIT_CHARGE_GRID:
                optimum = min(row["risk"][charge] for row in eligible)  # type: ignore[index]
                hashes = tuple(sorted(row["hash"] for row in eligible if row["risk"][charge] == optimum))  # type: ignore[index]
                cells.append(
                    FrontierCell(
                        covertness_regime=regime,
                        delta=delta,
                        audit_charge=charge,
                        minimax_error=optimum,
                        eligible_code_count=len(eligible),
                        optimal_code_count=len(hashes),
                        optimal_code_hashes=hashes,
                    )
                )
    return tuple(cells)


def registered_controls() -> dict[str, bool]:
    laws = encoder_laws()
    maps = audit_maps()
    identical = (1, 1, 1, 1)
    identical_risk = minimax_binary_error(as_distribution(identical), as_distribution(identical))
    constant_maps = [mapping for mapping in maps if len(set(mapping)) == 1]
    constant_map_kills = all(
        minimax_binary_error(
            as_distribution(pushforward_counts(left, mapping)),
            as_distribution(pushforward_counts(right, mapping)),
        )
        == Fraction(1, 2)
        for left in laws
        for right in laws
        for mapping in constant_maps
    )
    return {
        "unique_response_null": identical_risk == Fraction(1, 2),
        "full_collapse_audit": constant_map_kills,
        "registered_law_count": len(laws) == 35,
        "registered_code_count": len(laws) ** 2 == 1225,
        "registered_audit_count": len(maps) == 256,
    }


def exact_fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}
