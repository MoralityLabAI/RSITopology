"""BM-05: robust binary holonomy monitoring with correlated readout noise.

Finite minimax theorem. In each episode the clean binary-cycle edge vector is
uniform on its even or odd parity coset. An adversary may choose a joint error
mask distribution whose per-coordinate flip probabilities are <= eta, with the
mask independent of the current clean vector. Under the *conditional* version
the bound applies after every observed history and for each hypothesis.

Union bound: Pr(odd error parity | history) <= L*eta. The least-favorable
mask either has no errors or flips exactly one uniformly selected bit,
attaining p_star=min(L*eta,1/2). It makes all output information besides
parity uninformative. Across episodes with conditional budgets, majority
vote is minimax (couple its errors to iid Bernoulli(p_star)). If error
allowances hold only marginally across the entire trajectory, a shared
latent burst prevents consistent recovery even after infinitely many episodes.

This is a precise access/noise model, not a claim about real-world monitor
independence, authorized restorations or semantic safety.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb


def parity_flip_budget(length: int, marginal_cap: Fraction) -> Fraction:
    """Sharp maximum useful parity crossover, capped at one half."""
    eta = Fraction(marginal_cap)
    if length < 1 or not 0 <= eta <= 1:
        raise ValueError("length positive and marginal_cap in [0,1] required")
    return min(Fraction(1, 2), length * eta)


def least_favorable_masks(
    length: int, marginal_cap: Fraction
) -> dict[tuple[bool, ...], Fraction]:
    """An explicit legal mask law attaining worst-case parity indistinguishability.

    With probability 1-p, every bit is correct; with probability p, one
    uniformly chosen bit is flipped. Each bit has error probability p/L <= eta.
    """
    p = parity_flip_budget(length, marginal_cap)
    zeros = (False,) * length
    law = {zeros: 1 - p}
    for i in range(length):
        mask = tuple(j == i for j in range(length))
        law[mask] = p / length
    return {mask: Fraction(prob) for mask, prob in law.items() if prob > 0}


def mask_marginals(
    masks: dict[tuple[bool, ...], Fraction]
) -> tuple[Fraction, ...]:
    if not masks:
        raise ValueError("mask law must be nonempty")
    length = len(next(iter(masks)))
    if (any(len(mask) != length or prob < 0 for mask, prob in masks.items())
        or sum(masks.values()) != 1):
        raise ValueError("invalid probability distribution on fixed-size masks")
    return tuple(
        sum((prob for mask, prob in masks.items() if mask[i]), Fraction(0))
        for i in range(length)
    )


def apply_correlated_mask(
    law: dict[tuple[bool, ...], Fraction],
    masks: dict[tuple[bool, ...], Fraction],
) -> dict[tuple[bool, ...], Fraction]:
    """Full-pattern channel, used for independent exact oracle comparisons."""
    if not law or not masks:
        raise ValueError("input and mask laws must be nonempty")
    n = len(next(iter(law)))
    if any(len(bits) != n or p < 0 for bits, p in law.items()):
        raise ValueError("invalid input bit-vector distribution")
    if sum(law.values()) != 1:
        raise ValueError("input mass must sum to 1")
    if any(len(mask) != n for mask in masks):
        raise ValueError("mask/input dimension mismatch")
    mask_marginals(masks)
    out: dict[tuple[bool, ...], Fraction] = {}
    for bits, probability in law.items():
        for mask, q in masks.items():
            observed = tuple(x != flip for x, flip in zip(bits, mask))
            out[observed] = out.get(observed, Fraction(0)) + probability * q
    return {bits: p for bits, p in out.items() if p > 0}


def minimum_guaranteed_parity_signal(
    length: int, marginal_cap: Fraction
) -> Fraction:
    return 1 - 2 * parity_flip_budget(length, marginal_cap)


def binary_majority_error_from_signal(signal: Fraction, episodes: int) -> Fraction:
    """Exact equal-prior minimax error of N iid opposite Bernoulli parity laws."""
    t = Fraction(signal)
    if not 0 <= t <= 1 or episodes < 1:
        raise ValueError("signal in [0,1] and episodes >=1 required")
    probability_correct = (1 + t) / 2
    return sum((
        comb(episodes, k) * probability_correct**k
        * (1 - probability_correct)**(episodes - k)
        * (1 if 2 * k < episodes else Fraction(1, 2) if 2*k == episodes else 0)
        for k in range(episodes + 1)
    ), Fraction(0))


def conditional_minimax_error(
    length: int, marginal_cap: Fraction, episodes: int
) -> Fraction:
    """Exact minimax over per-history independent-current-sample error masks.

    Nature may correlate bit errors within an episode and choose a new law
    after every observed history. The per-bit marginal constraint must hold
    conditional on the history and the hypothesis. The binary parity-majority
    test is minimax for this stated class.
    """
    return binary_majority_error_from_signal(
        minimum_guaranteed_parity_signal(length, marginal_cap), episodes
    )


def marginal_only_persistent_burst_floor(
    length: int, marginal_cap: Fraction
) -> Fraction:
    """Bayes error floor when one legal hidden noise mask persists for all episodes.

    A single draw of the least-favorable zero/one-bit mask is reused across
    every fresh clean-label episode. Each reported vector has the same
    (possibly flipped) parity, and repeated observations cannot identify
    whether the shared mask was odd. This is a *lower bound* on the minimax
    risk of the broader marginal-only class, not its exact supremum.
    """
    return parity_flip_budget(length, marginal_cap)


def restoration_observation_class(
    h: int, drift: int, action: int, alphabet: int
) -> int:
    """Observable effective holonomy h XOR latent restoration drift XOR action."""
    if alphabet < 2 or alphabet & (alphabet - 1) or any(
        not 0 <= x < alphabet for x in (h, drift, action)
    ):
        raise ValueError("alphabet must be F2^s, elements within group range")
    return h ^ drift ^ action


def conditional_false_restoration_union_bound(
    per_step_false_accept: tuple[Fraction, ...]
) -> Fraction:
    """Bonferroni budget for independently anchored state-restoration attestations.

    Each input is an upper bound on the probability that an un-restored state
    gets a passing audit after step i, possibly conditional on earlier
    successful audits. User must separately establish the bound from a
    trusted measurement/certificate. No assumption of independent failures.
    """
    values = tuple(Fraction(v) for v in per_step_false_accept)
    if any(not 0 <= v <= 1 for v in values):
        raise ValueError("conditional false-accept bounds must lie in [0,1]")
    return min(Fraction(1), sum(values, Fraction(0)))
