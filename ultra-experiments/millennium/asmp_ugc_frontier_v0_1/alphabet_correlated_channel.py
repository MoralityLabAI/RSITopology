"""BM-06: alphabet-general correlated Boolean cycle readout theorem.

For any finite abelian gain group of order q>=2, the flat-versus-nonflat
joint distribution difference on Boolean cycle-satisfaction bits is a
one-dimensional parity Fourier character. A common mask distribution on
the Boolean bits, independent of the clean observation and identical for
both hypotheses, scales this difference by E[(-1)^popcount(mask)].

Under independently registered per-coordinate mask-marginal caps eta_i,
one-hot masks attain the worst *single-episode equal-prior Bayes risk*,
including exact zero-information at sum eta_i>=1/2.

The common-channel assumption is essential. The separately defined
parity-only composite (type-I,type-II) region is solved by exact rational
2D polygon clipping via candidate boundary intersections.

This code uses exact Fractions and targets one observation episode only.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations

try:
    from .frontier_bounds import full_cycle_law, tv_distance
    from .correlated_minimax import apply_correlated_mask, mask_marginals
except ImportError:
    from frontier_bounds import full_cycle_law, tv_distance
    from correlated_minimax import apply_correlated_mask, mask_marginals


def _caps(values: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    caps = tuple(Fraction(x) for x in values)
    if not caps or any(not 0 <= cap <= 1 for cap in caps):
        raise ValueError("need nonempty per-edge probability caps in [0,1]")
    return caps


def common_mask_parity(mask_law: dict[tuple[bool, ...], Fraction]) -> Fraction:
    """Pr(odd mask) for a valid normalized mask law."""
    mask_marginals(mask_law)
    return sum((p for mask, p in mask_law.items() if sum(mask) & 1),
               Fraction(0))


def extremal_common_mask(
    marginal_caps: tuple[Fraction, ...],
) -> dict[tuple[bool, ...], Fraction]:
    """A legal one-hot mask minimizing single-shot flat/nonflat TV.

    The tie-breaking is deterministic: spend the first edges' caps first.
    """
    caps = _caps(marginal_caps)
    ell = len(caps)
    remaining = min(Fraction(1, 2), sum(caps, Fraction(0)))
    law: dict[tuple[bool, ...], Fraction] = {
        (False,) * ell: 1 - remaining
    }
    for j, cap in enumerate(caps):
        amount = min(remaining, cap)
        if amount:
            law[tuple(k == j for k in range(ell))] = amount
            remaining -= amount
    if remaining:
        raise AssertionError("one-hot allocation failed")
    if any(actual > bound for actual, bound in zip(
        mask_marginals(law), caps
    )):
        raise AssertionError("mask exceeds per-edge cap")
    return law


def cycle_difference_character(
    length: int, q: int,
) -> dict[tuple[bool, ...], Fraction]:
    """Exact signed P_flat(bits)-P_frustrated(bits)."""
    a = full_cycle_law(length, q, flat=True)
    b = full_cycle_law(length, q, flat=False)
    keys = a.keys() | b.keys()
    return {bits: a.get(bits, Fraction(0)) - b.get(bits, Fraction(0))
            for bits in keys}


def exact_masked_tv(
    length: int, q: int, mask_law: dict[tuple[bool, ...], Fraction]
) -> Fraction:
    """Full-pattern TV, direct from the two convolutions, independent oracle."""
    if any(len(mask) != length for mask in mask_law):
        raise ValueError("mask length must equal cycle length")
    a = apply_correlated_mask(full_cycle_law(length,q,flat=True),mask_law)
    b = apply_correlated_mask(full_cycle_law(length,q,flat=False),mask_law)
    return tv_distance(a,b)


def parity_channel_tv(
    length: int, q: int, mask_law: dict[tuple[bool, ...], Fraction]
) -> Fraction:
    """Fourier-character prediction for a common mask channel."""
    if any(len(mask) != length for mask in mask_law):
        raise ValueError("mask length must equal cycle length")
    p = common_mask_parity(mask_law)
    return Fraction(2,q)**(length-1)*abs(1-2*p)


def one_shot_minimax_tv(
    q: int, marginal_caps: tuple[Fraction, ...]
) -> Fraction:
    """Smallest possible full-pattern TV under a common unknown mask law."""
    caps = _caps(marginal_caps)
    return Fraction(2,q)**(len(caps)-1)*max(
        Fraction(0), 1-2*sum(caps, Fraction(0))
    )


def one_shot_minimax_bayes_error(
    q: int, marginal_caps: tuple[Fraction, ...]
) -> Fraction:
    """Equal-prior randomized-minimax error, common hypothesis-blind mask.

    Test: declare flat when the number of observed failures is even.
    This is simultaneously a Bayes-optimal one-shot rule for every common
    channel with parity-flip probability <=1/2. The extremal one-hot law
    supplies a matching adversarial lower bound.
    """
    return (1-one_shot_minimax_tv(q,marginal_caps))/2


def clean_even_probabilities(length: int, q: int) -> tuple[Fraction, Fraction]:
    """Pr(even number of failures | flat/nonflat), direct exact law oracle."""
    out = []
    for flat in (True, False):
        law = full_cycle_law(length,q,flat=flat)
        out.append(sum((p for bits,p in law.items()
                        if bits.count(False) % 2 == 0), Fraction(0)))
    return tuple(out)  # type: ignore[return-value]


def parity_test_error_bounds(
    q: int, marginal_caps: tuple[Fraction, ...],
    decide_nonflat_if_even: Fraction,
    decide_nonflat_if_odd: Fraction,
) -> tuple[Fraction, Fraction]:
    """Robust (false nonflat | flat, false flat | nonflat) for parity test.

    Decision probabilities can be rational/randomized. Maxima over the
    **common** mask law occur at endpoint p_odd=0 or p_odd=p_star.
    Guarantees remain valid separately for either fixed hypothesis if the
    adversary selects its common mask law before seeing that hypothesis.
    """
    caps = _caps(marginal_caps)
    a,b = Fraction(decide_nonflat_if_even),Fraction(decide_nonflat_if_odd)
    if not 0 <= a <= 1 or not 0 <= b <= 1:
        raise ValueError("decision probabilities must be in [0,1]")
    even0,even1 = clean_even_probabilities(len(caps),q)
    pstar = min(Fraction(1,2),sum(caps, Fraction(0)))
    fp=Fraction(0)
    fn=Fraction(0)
    for p in (Fraction(0),pstar):
        f0=even0*(1-p)+(1-even0)*p
        f1=even1*(1-p)+(1-even1)*p
        fp=max(fp, a*f0+b*(1-f0))
        fn=max(fn, (1-a)*f1+(1-b)*(1-f1))
    return fp,fn


def feasible_parity_composite_test(
    q: int,
    marginal_caps: tuple[Fraction, ...],
    max_false_positive: Fraction,
    max_false_negative: Fraction,
) -> tuple[Fraction,Fraction] | None:
    """Exact LP feasibility for randomized parity-only (alpha,beta) constraints.

    The feasible set is a closed polygon in (a,b) in [0,1]^2 with four
    linear error inequalities, one at p=0 and one at p=pstar under both
    hypotheses. A nonempty bounded polygon has a vertex at the intersection
    of two of these lines. All such intersections are checked exactly.

    Returned (a,b) is a concrete test; None means infeasible **among
    parity-only tests**. Full-pattern randomized composite tests can do
    better under asymmetric error targets.
    """
    caps = _caps(marginal_caps)
    alpha,beta = Fraction(max_false_positive),Fraction(max_false_negative)
    if not 0 <= alpha <= 1 or not 0 <= beta <= 1:
        raise ValueError("error targets must be in [0,1]")
    e0,e1=clean_even_probabilities(len(caps),q)
    pstar=min(Fraction(1,2),sum(caps,Fraction(0)))
    # A*a+B*b <= C.
    constraints=[
        (-1,0,Fraction(0)), (1,0,Fraction(1)),
        (0,-1,Fraction(0)), (0,1,Fraction(1)),
    ]
    for p in (Fraction(0),pstar):
        a0=e0*(1-p)+(1-e0)*p
        a1=e1*(1-p)+(1-e1)*p
        constraints.append((a0,1-a0,alpha))
        constraints.append((-a1,-(1-a1), beta-1))
    for (a,b,c),(d,e,f) in combinations(constraints,2):
        determinant=a*e-b*d
        if determinant==0:
            continue
        u=Fraction(c*e-b*f,determinant)
        v=Fraction(a*f-c*d,determinant)
        if all(aa*u+bb*v<=cc for aa,bb,cc in constraints):
            if parity_test_error_bounds(q,caps,u,v)[0]<=alpha and (
                parity_test_error_bounds(q,caps,u,v)[1]<=beta
            ):
                return u,v
    return None
