"""BM-04: exact finite adaptive active-cycle monitor design.

Hidden numerical holonomy h is uniform on K=F2^s with q candidates.
In each independent episode the monitor chooses a known edge shift x,
then gets a full Boolean cycle pattern under a fresh uniform vertex labeling.
The observation is reduced to its sufficient failure count k. Conditional
on h=x the count law is flat, otherwise it is nonflat, optionally followed
by iid bit-readout flips at known rate eta.

This solves a deliberately tiny, predeclared finite Bayesian design game.
It is an exact policy calculation, not a universal monitoring theorem.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

try:
    from .finite_sample_monitor import noisy_failure_count_law
except ImportError:
    from finite_sample_monitor import noisy_failure_count_law


def _priors(q: int, length: int, eta: Fraction):
    if q < 2 or q > 4 or length < 1 or length > 4:
        raise ValueError("seed budget: 2<=q<=4, 1<=length<=4")
    eta = Fraction(eta)
    if not 0 <= eta <= 1:
        raise ValueError("readout flip probability must lie in [0,1]")
    return (
        noisy_failure_count_law(length, q, flat=True, flip_probability=eta),
        noisy_failure_count_law(length, q, flat=False, flip_probability=eta),
    )


def adaptive_success_probability(
    q: int, length: int, episodes: int,
    *, flip_probability: Fraction = Fraction(0)
) -> Fraction:
    """Exact optimal equal-prior probability of identifying h adaptively.

    Unnormalized posterior weights w_h initially all equal 1. The value
    V(w,N) is the expected (unconditional) winning posterior mass:
       V(w,0)=max_h w_h
       V(w,N)=max_x sum_k V((w_h p(k|h,x))_h,N-1).
    The result is V((1,...,1),N)/q. Sorting posterior weights is a valid
    symmetry quotient because all interventions x in K are available.
    """
    if episodes < 0 or episodes > 6:
        raise ValueError("seed budget: 0<=episodes<=6")
    p0, p1 = _priors(q, length, flip_probability)

    @lru_cache(maxsize=None)
    def solve(weights: tuple[Fraction, ...], remaining: int) -> Fraction:
        if remaining == 0:
            return max(weights)
        score = Fraction(0)
        for candidate in range(q):
            total = Fraction(0)
            for k in range(length + 1):
                next_weights = tuple(sorted(
                    w * (p0[k] if h == candidate else p1[k])
                    for h, w in enumerate(weights)
                ))
                if any(next_weights):
                    total += solve(next_weights, remaining - 1)
            score = max(score, total)
        return score

    return solve((Fraction(1),) * q, episodes) / q


def _nonincreasing_partitions(total: int, bins: int, upper: int | None = None):
    if bins == 0:
        if total == 0:
            yield ()
        return
    maximum = total if upper is None else min(total, upper)
    for n in range(maximum, -1, -1):
        for other in _nonincreasing_partitions(total - n, bins - 1, n):
            yield (n,) + other


def fixed_schedule_success_probability(
    q: int, length: int, episodes: int,
    *, flip_probability: Fraction = Fraction(0)
) -> tuple[Fraction, tuple[int, ...]]:
    """Best nonadaptive schedule among all q-arm visit-count allocations.

    Order of independent observations does not affect the likelihood, so
    a fixed schedule is fully specified up to symmetry by its nonincreasing
    arm-count vector. Exhaustive dynamic evaluation returns the best schedule.
    """
    if episodes < 0 or episodes > 6:
        raise ValueError("seed budget: 0<=episodes<=6")
    p0, p1 = _priors(q, length, flip_probability)
    winner = Fraction(-1)
    best_allocation: tuple[int, ...] = ()
    for allocation in _nonincreasing_partitions(episodes, q):
        schedule = tuple(x for x, n in enumerate(allocation) for _ in range(n))

        @lru_cache(maxsize=None)
        def solve(weights: tuple[Fraction, ...], index: int) -> Fraction:
            if index == episodes:
                return max(weights)
            x = schedule[index]
            return sum((
                solve(tuple(
                    w * (p0[k] if h == x else p1[k])
                    for h, w in enumerate(weights)
                ), index + 1)
                for k in range(length + 1)
            ), Fraction(0))

        success = solve((Fraction(1),) * q, 0) / q
        if success > winner:
            winner, best_allocation = success, allocation
    return winner, best_allocation


def optimal_second_shift_actions(
    q: int, length: int, observed_failures: int,
    *, flip_probability: Fraction = Fraction(0)
) -> tuple[int, ...]:
    """Optimal second x after first query x=0, with two episodes total.

    Returns ALL maximizers in 0..q-1, so ties are explicit.
    """
    p0, p1 = _priors(q, length, flip_probability)
    if not 0 <= observed_failures <= length:
        raise ValueError("failure count outside cycle length")
    weights = (p0[observed_failures],) + (p1[observed_failures],) * (q - 1)
    scores = []
    for candidate in range(q):
        score = sum((
            max(weights[h] * (p0[k] if h == candidate else p1[k])
                for h in range(q))
            for k in range(length + 1)
        ), Fraction(0))
        scores.append(score)
    highest = max(scores)
    return tuple(x for x, score in enumerate(scores) if score == highest)
