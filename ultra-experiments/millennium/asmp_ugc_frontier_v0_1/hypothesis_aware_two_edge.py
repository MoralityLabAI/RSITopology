"""BM-07: hypothesis-aware adversarial readout on a two-edge gain cycle.

Exact closed-form minimax for a 2-cycle of *parallel constraint occurrences*
over K=F2^s, q=2^s. Fresh uniform vertex labelings emit two Boolean
satisfaction bits. A readout mask M is independent of the current clean
vector but its distribution MAY depend on the hidden flat/nonflat hypothesis,
the chosen externally known shift, and earlier episode transcripts.
Each coordinate's conditional mask-flip probability is <= eta.

For a single episode with equal priors:
  min_{Q0,Q1} TV(P0*Q0, P1*Q1)
    = max(0,1-4 eta)           when q=2
    = max(0,2/q-2 eta)         when q>=4.
Exact constructive mask channels are returned below.

A mixed/unequal-edge bit is an information-bearing event for all q.
When the gap is positive, testing its frequency across independent fresh
labelings gives a composite robust authorization test even with adaptive
hypothesis-dependent mask choices, assuming the conditional error cap.
No hypothesis-blind noise assumption is used.

All arithmetic is exact Fraction. The result is an elementary special
case of adversarial-channel symmetrization, not a general ASMP solution.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb

try:
    from .frontier_bounds import full_cycle_law, tv_distance
    from .correlated_minimax import apply_correlated_mask, mask_marginals
except ImportError:
    from frontier_bounds import full_cycle_law, tv_distance
    from correlated_minimax import apply_correlated_mask, mask_marginals

Mask = tuple[bool, bool]
Law = dict[Mask, Fraction]


def validate(q: int, eta: Fraction) -> Fraction:
    if q < 2 or q & (q-1):
        raise ValueError("q must be 2^s for positive integer s")
    eta = Fraction(eta)
    if not 0 <= eta <= 1:
        raise ValueError("per-bit error cap must be in [0,1]")
    return eta


def erasure_threshold(q: int) -> Fraction:
    validate(q, Fraction(0))
    return Fraction(1,4) if q == 2 else Fraction(1,q)


def hypothesis_aware_minimax_tv(q: int, eta: Fraction) -> Fraction:
    eta = validate(q,eta)
    return max(Fraction(0),
               1-4*eta if q==2 else Fraction(2,q)-2*eta)


def hypothesis_blind_minimax_tv(q: int, eta: Fraction) -> Fraction:
    """Earlier common-channel benchmark for two edge indicators."""
    eta = validate(q,eta)
    return Fraction(2,q)*max(Fraction(0),1-4*eta)


def extremal_hypothesis_aware_masks(q: int, eta: Fraction) -> tuple[Law,Law]:
    """A least-favorable exact readout channel pair.

    q>=4:
      flat: no flip 1-2r, flip first r, flip second r
      nonflat: no flip 1-r, flip both r
      r=min(eta,1/q).
    q=2:
      same one-hot mask law under both hypotheses with r=min(eta,1/4).
    """
    eta = validate(q,eta)
    r = min(eta,erasure_threshold(q))
    z=(False,False)
    one=(True,False)
    two=(False,True)
    both=(True,True)
    flat={z:1-2*r,one:r,two:r}
    frustrated=(dict(flat) if q==2 else {z:1-r,both:r})
    flat={k:Fraction(v) for k,v in flat.items() if v}
    frustrated={k:Fraction(v) for k,v in frustrated.items() if v}
    for law in (flat,frustrated):
        if any(x>eta for x in mask_marginals(law)):
            raise AssertionError("error-mask witness violates cap")
    return flat,frustrated


def extremal_output_laws(q: int, eta: Fraction) -> tuple[Law,Law]:
    m0,m1=extremal_hypothesis_aware_masks(q,eta)
    return (
        apply_correlated_mask(full_cycle_law(2,q,flat=True),m0),
        apply_correlated_mask(full_cycle_law(2,q,flat=False),m1),
    )


def exact_extremal_tv(q: int, eta: Fraction) -> Fraction:
    a,b=extremal_output_laws(q,eta)
    return tv_distance(a,b)


def mixed_event_probabilities(q: int, eta: Fraction) -> tuple[Fraction,Fraction]:
    """Sharp bounds for one observed unequal-bit indicator.

    Under flat: P(mixed | history,H0) <= a = 2eta.
    Under nonflat: P(mixed | history,H1) >= b =
       1-2eta when q=2, and 2/q when q>=4.

    Both extreme values are simultaneously attained by the extremal
    channels when eta < the erasure threshold. These bounds presume
    fresh uniform labelings and error masks independent of each current
    clean vector.
    """
    eta=validate(q,eta)
    if eta>=erasure_threshold(q):
        raise ValueError("no positive guaranteed mixed-event separation")
    a=2*eta
    b=(1-2*eta) if q==2 else Fraction(2,q)
    if a>=b:
        raise AssertionError("positive-gap regime violated")
    return a,b


def binomial_at_least(n: int, threshold: int, p: Fraction) -> Fraction:
    """P[Bin(n,p) >= threshold] with exact rational arithmetic."""
    p=Fraction(p)
    if n<0 or not 0<=p<=1:
        raise ValueError("n>=0, 0<=p<=1 required")
    return sum((
        Fraction(comb(n,k))*p**k*(1-p)**(n-k)
        for k in range(max(0,threshold),n+1)
    ),Fraction(0))


def mixed_count_composite_bounds(
    q: int,eta: Fraction,samples: int,threshold: int
) -> tuple[Fraction,Fraction]:
    """Sharp conditional-adversary FP/FN bounds for fixed-count decision.

    Declare NONFLAT when at least threshold observed episodes have two
    unequal satisfaction bits. A conditional Hoeffding/stochastic-order
    coupling shows:
       FP <= P[Bin(N,a)>=threshold],
       FN <= P[Bin(N,b)<threshold],
    with (a,b)=mixed_event_probabilities(q,eta). The stationary extremal
    pair achieves both bounds, so they are exact for this rule.
    """
    if samples<1 or not 0<=threshold<=samples+1:
        raise ValueError("samples>=1; threshold in [0,samples+1]")
    a,b=mixed_event_probabilities(q,eta)
    return binomial_at_least(samples,threshold,a),(
        1-binomial_at_least(samples,threshold,b)
    )


def best_deterministic_mixed_threshold(
    q: int,eta: Fraction,samples: int
) -> tuple[int,Fraction,Fraction]:
    """Minimize the larger worst-case FP/FN bound over integer thresholds."""
    best=None
    for threshold in range(samples+2):
        fp,fn=mixed_count_composite_bounds(q,eta,samples,threshold)
        candidate=(max(fp,fn),fp+fn,threshold,fp,fn)
        if best is None or candidate<best:
            best=candidate
    if best is None:
        raise AssertionError("threshold search empty")
    return best[2],best[3],best[4]


def adaptive_erasure_output_law(q: int,eta: Fraction,hidden_h: int,action_x: int) -> Law:
    """One-episode attack against known-shift active holonomy tomography.

    If h==x, use the hypothesis-aware flat error mask, else the nonflat
    mask. At eta>=1/q for q>=4 the output law is IDENTICAL for every
    hidden h and action x, so all adaptive action/transcript experiments
    remain uninformative by induction.
    """
    validate(q,eta)
    if not 0<=hidden_h<q or not 0<=action_x<q:
        raise ValueError("hidden h and chosen shift within alphabet required")
    flat,nonflat=extremal_output_laws(q,eta)
    return flat if hidden_h==action_x else nonflat
