"""BM-03: exact iid inference for Boolean cycle monitors.

A cycle has q labels, length ell, and either zero or nonzero holonomy.
Fresh independent uniform vertex labelings produce complete Boolean edge
satisfaction vectors. Optional independent binary-symmetric bit readout
errors have known rate eta. The number K of unsatisfied bits is sufficient
for the balanced/nonbalanced likelihood ratio, even after iid readout noise.

All finite probabilities and Bayes risks use exact Fractions. The method
enumerates count histograms, not vertex labels. It makes no claim about
physical source validity, adaptive state changes, or correlated errors.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb, factorial, prod


def cycle_failure_count_law(length: int, q: int, *, flat: bool) -> tuple[Fraction, ...]:
    """P(number of unsatisfied bits=k) for a uniform-label simple cycle."""
    if length < 1 or q < 2:
        raise ValueError("positive cycle length and alphabet size >=2 required")
    denominator = q ** (length - 1)
    distribution = []
    for k in range(length + 1):
        numerator = (q - 1) ** k + ((q - 1) if flat else -1) * (-1) ** k
        if numerator % q:
            raise AssertionError("character count is not integral")
        multiplicity = numerator // q
        if multiplicity < 0:
            raise AssertionError("negative cycle residual multiplicity")
        distribution.append(Fraction(comb(length, k) * multiplicity, denominator))
    if sum(distribution) != 1:
        raise AssertionError("cycle probabilities do not sum to one")
    return tuple(distribution)


def noisy_failure_count_law(
    length: int, q: int, *, flat: bool, flip_probability: Fraction
) -> tuple[Fraction, ...]:
    """Exact failure-count law after independent readout flips on each bit.

    Conditioned on j true failures, each stays a failure with probability
    1-eta; each of the other ell-j success bits flips with probability eta.
    The output failure-count law remains exchangeable.
    """
    eta = Fraction(flip_probability)
    if not 0 <= eta <= 1:
        raise ValueError("flip_probability must lie in [0,1]")
    base = cycle_failure_count_law(length, q, flat=flat)
    out = [Fraction(0)] * (length + 1)
    for j, prior in enumerate(base):
        if not prior:
            continue
        for k in range(length + 1):
            conditional = Fraction(0)
            # u of the j true failures stay failures;
            # v = k-u originally satisfied edges become failures.
            for u in range(max(0, k - (length - j)), min(j, k) + 1):
                v = k - u
                conditional += (
                    comb(j, u) * (1 - eta) ** u * eta ** (j - u)
                    * comb(length - j, v) * eta ** v
                    * (1 - eta) ** (length - j - v)
                )
            out[k] += prior * conditional
    if sum(out) != 1 or any(p < 0 for p in out):
        raise AssertionError("invalid noise-convolved cycle distribution")
    return tuple(out)


def _compositions(total: int, bins: int):
    if bins == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for other in _compositions(total - first, bins - 1):
            yield (first,) + other


def exact_iid_bayes_error(
    flat_count_law: tuple[Fraction, ...],
    frustrated_count_law: tuple[Fraction, ...],
    samples: int,
    *,
    max_histograms: int = 20000,
) -> Fraction:
    """Minimum equal-prior error for N iid full Boolean-pattern observations.

    The per-episode count k of unsatisfied edges is sufficient. Enumerate
    the multinomial histograms of k across N episodes. For each histogram
    take the smaller of the two exact likelihoods.
    """
    if samples < 1 or max_histograms < 1:
        raise ValueError("samples and max_histograms must be positive")
    if len(flat_count_law) != len(frustrated_count_law) or not flat_count_law:
        raise ValueError("both hypotheses must have the same count alphabet")
    if (sum(flat_count_law) != 1 or sum(frustrated_count_law) != 1
        or any(v < 0 for v in flat_count_law + frustrated_count_law)):
        raise ValueError("each count law must be a probability distribution")
    bins = len(flat_count_law)
    histogram_count = comb(samples + bins - 1, bins - 1)
    if histogram_count > max_histograms:
        raise ValueError("histogram enumeration exceeds registered budget")
    factorial_samples = factorial(samples)
    overlap = Fraction(0)
    for histogram in _compositions(samples, bins):
        coefficient = factorial_samples // prod(factorial(n) for n in histogram)
        p0 = coefficient * prod(p ** count for p, count in zip(flat_count_law, histogram))
        p1 = coefficient * prod(p ** count for p, count in zip(frustrated_count_law, histogram))
        overlap += min(p0, p1)
    return overlap / 2


def cycle_iid_bayes_error(
    length: int,
    q: int,
    samples: int,
    *,
    flip_probability: Fraction = Fraction(0),
    max_histograms: int = 20000,
) -> Fraction:
    """Optimal Bayes error for full-pattern balanced vs nonbalanced observations."""
    eta = Fraction(flip_probability)
    p0 = noisy_failure_count_law(length, q, flat=True, flip_probability=eta)
    p1 = noisy_failure_count_law(length, q, flat=False, flip_probability=eta)
    return exact_iid_bayes_error(p0, p1, samples, max_histograms=max_histograms)


def binary_parity_signal(length: int, flip_probability: Fraction) -> Fraction:
    """Absolute per-episode parity bias for q=2, with known eta."""
    eta = Fraction(flip_probability)
    if length < 1 or not 0 <= eta <= 1:
        raise ValueError("positive cycle length and valid flip probability required")
    return abs(1 - 2 * eta) ** length


def binary_optimal_iid_bayes_error(
    length: int, flip_probability: Fraction, samples: int
) -> Fraction:
    """Closed exact binomial-tail risk, equivalent to the full-pattern LRT."""
    if samples < 1:
        raise ValueError("at least one observation required")
    t = binary_parity_signal(length, flip_probability)
    success_bit_prob = (1 + t) / 2
    error = Fraction(0)
    for votes in range(samples + 1):
        mass = (
            comb(samples, votes) * success_bit_prob ** votes
            * (1 - success_bit_prob) ** (samples - votes)
        )
        if 2 * votes < samples:
            error += mass
        elif 2 * votes == samples:
            error += mass / 2
    return error


def binary_hellinger_necessary_samples(
    length: int,
    flip_probability: Fraction,
    target_error: Fraction,
    *,
    max_samples: int = 10000,
) -> int | None:
    """Exact affinity-based necessary N for equal-prior Bayes error <= target.

    If t=|1-2eta|^ell, per-episode affinity is sqrt(1-t²); tensor product
    affinity squared is (1-t²)^N. Using TV <= sqrt(1-affinity²) requires
       (1-t²)^N <= 4 target_error (1-target_error).
    Returns None if eta=1/2 (no finite N can identify). Raises on budget cap.
    """
    target = Fraction(target_error)
    if not 0 < target < Fraction(1, 2) or max_samples < 1:
        raise ValueError("target_error in (0,1/2), max_samples >=1 required")
    t = binary_parity_signal(length, flip_probability)
    if t == 0:
        return None
    if t == 1:
        return 1
    base = 1 - t * t
    threshold = 4 * target * (1 - target)
    lo, hi = 0, 1
    while base ** hi > threshold:
        lo = hi
        hi *= 2
        if hi > max_samples:
            hi = max_samples
            if base ** hi > threshold:
                raise ValueError("required Hellinger lower bound exceeds max_samples")
            break
    while hi - lo > 1:
        middle = (lo + hi) // 2
        if base ** middle <= threshold:
            hi = middle
        else:
            lo = middle
    return hi
