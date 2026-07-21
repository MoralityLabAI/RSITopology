"""Exact finite-sample design calculations for the ASMP-11 v0.2 pilot."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class ExactTestDesign:
    query_count: int
    samples_per_query: int
    cutoff: int
    null_tail: Fraction
    familywise_error_upper: Fraction
    signal_power_lower: Fraction

    @property
    def total_samples(self) -> int:
        return self.query_count * self.samples_per_query


@dataclass(frozen=True)
class AccessPlan:
    name: str
    observation_order: int
    intervention_width: int
    query_count: int
    coverage: str


def two_sided_binomial_tail(samples: int, cutoff: int, plus_probability: Fraction) -> Fraction:
    """P[X <= cutoff or X >= samples-cutoff] for X~Bin(samples,p)."""

    if samples < 1:
        raise ValueError("samples must be positive")
    if cutoff < 0:
        return Fraction(0)
    if 2 * cutoff >= samples:
        return Fraction(1)
    numerator_probability = plus_probability.numerator
    denominator_probability = plus_probability.denominator
    minus_probability = denominator_probability - numerator_probability
    numerator = 0
    for successes in range(cutoff + 1):
        numerator += (
            comb(samples, successes)
            * numerator_probability**successes
            * minus_probability ** (samples - successes)
        )
    for successes in range(samples - cutoff, samples + 1):
        numerator += (
            comb(samples, successes)
            * numerator_probability**successes
            * minus_probability ** (samples - successes)
        )
    return Fraction(numerator, denominator_probability**samples)


def most_permissive_cutoff(samples: int, query_count: int, alpha: Fraction) -> int | None:
    """Largest symmetric cutoff whose exact union-bound FWER is <= alpha."""

    accepted = None
    for cutoff in range((samples - 1) // 2 + 1):
        null_tail = two_sided_binomial_tail(samples, cutoff, Fraction(1, 2))
        if query_count * null_tail <= alpha:
            accepted = cutoff
        else:
            break
    return accepted


def find_exact_design(
    query_count: int,
    flip_rate: Fraction,
    alpha: Fraction,
    target_power: Fraction,
    sample_cap: int,
) -> ExactTestDesign | None:
    """Find the minimum samples/query satisfying exact conservative bounds."""

    if query_count < 1:
        raise ValueError("query_count must be positive")
    if not 0 <= flip_rate < Fraction(1, 2):
        raise ValueError("flip_rate must lie in [0,1/2)")
    signal_plus_probability = Fraction(1) - flip_rate
    for samples in range(1, sample_cap + 1):
        cutoff = most_permissive_cutoff(samples, query_count, alpha)
        if cutoff is None:
            continue
        null_tail = two_sided_binomial_tail(samples, cutoff, Fraction(1, 2))
        signal_power = two_sided_binomial_tail(samples, cutoff, signal_plus_probability)
        if signal_power >= target_power:
            return ExactTestDesign(
                query_count=query_count,
                samples_per_query=samples,
                cutoff=cutoff,
                null_tail=null_tail,
                familywise_error_upper=query_count * null_tail,
                signal_power_lower=signal_power,
            )
    return None


def boundary_plans(n: int, k: int) -> tuple[AccessPlan, ...]:
    """Complete nonadaptive plans with r+s=k and all-+1 assignments."""

    plans = []
    for intervention_width in range(k + 1):
        observation_order = k - intervention_width
        query_count = comb(n, intervention_width) * comb(
            n - intervention_width, observation_order
        )
        plans.append(
            AccessPlan(
                name=f"boundary_s{intervention_width}",
                observation_order=observation_order,
                intervention_width=intervention_width,
                query_count=query_count,
                coverage="uniform_all_k_supports",
            )
        )
    return tuple(plans)


def containment_plans(n: int, k: int) -> tuple[AccessPlan, ...]:
    """Order-zero plans querying every fixed set of a given width.

    A query on I is live whenever the unknown support T is contained in I.
    Querying every I of width s therefore gives uniform support coverage for
    every s>=k.  At s=n this becomes the universal full clamp.
    """

    return tuple(
        AccessPlan(
            name="full_clamp" if width == n else f"containment_s{width}",
            observation_order=0,
            intervention_width=width,
            query_count=comb(n, width),
            coverage="uniform_all_k_supports",
        )
        for width in range(k, n + 1)
    )


def all_registered_plans(n: int, k: int) -> tuple[AccessPlan, ...]:
    unique: dict[tuple[int, int, int], AccessPlan] = {}
    for plan in (*boundary_plans(n, k), *containment_plans(n, k)):
        key = (plan.observation_order, plan.intervention_width, plan.query_count)
        unique.setdefault(key, plan)
    return tuple(unique.values())
