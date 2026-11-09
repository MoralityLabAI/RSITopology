"""BM-06: exact composite false-positive/false-negative cycle decision rules.

The clean full Boolean pattern law is exchangeable and its likelihood ratio
depends only on the count k of unsatisfied edges. Neyman-Pearson thresholding
on p_nonflat(k)/p_flat(k) gives the complete randomized ROC frontier.

The minimum maximum of the two conditional error probabilities is achieved
where the threshold-rule false-positive and false-negative rates cross.
This is a clean-readout fixed-cycle result. The correlated-mask robust
decision region is handled separately by alphabet_correlated_channel.py.
"""
from __future__ import annotations

from fractions import Fraction

try:
    from .finite_sample_monitor import cycle_failure_count_law
except ImportError:
    from finite_sample_monitor import cycle_failure_count_law


def clean_count_composite_errors(
    length: int, q: int, nonflat_probabilities: tuple[Fraction, ...],
) -> tuple[Fraction, Fraction]:
    """Exact FP and FN for randomized count-based test."""
    probs = tuple(Fraction(x) for x in nonflat_probabilities)
    if len(probs) != length+1 or any(not 0 <= x <= 1 for x in probs):
        raise ValueError("one valid randomized action for each failure count needed")
    p0 = cycle_failure_count_law(length,q,flat=True)
    p1 = cycle_failure_count_law(length,q,flat=False)
    false_positive=sum((u*v for u,v in zip(probs,p0)),Fraction(0))
    false_negative=sum(((1-u)*v for u,v in zip(probs,p1)),Fraction(0))
    return false_positive,false_negative


def clean_minimax_composite_rule(
    length: int, q: int
) -> tuple[Fraction, tuple[Fraction, ...]]:
    """One-shot minimax worst-hypothesis error and exact Neyman-Pearson rule.

    Decisions have probability a_k of declaring nonflat given k failures.
    The monotone likelihood-ratio ordering is calculated directly from the
    exact count laws. Walk the ROC frontier until FP=FN and randomize on
    at most one likelihood-ratio class.
    """
    p0=cycle_failure_count_law(length,q,flat=True)
    p1=cycle_failure_count_law(length,q,flat=False)
    order=sorted(
        range(length+1),
        key=lambda k: (
            1 if p0[k]==0 and p1[k]>0 else 0,
            p1[k]/p0[k] if p0[k] else Fraction(0)
        ),
        reverse=True,
    )
    fp,fn=Fraction(0),Fraction(1)
    decision=[Fraction(0)]*(length+1)
    for k in order:
        if p0[k]+p1[k]==0:
            continue
        if fp+p0[k] <= fn-p1[k]:
            decision[k]=Fraction(1)
            fp+=p0[k]
            fn-=p1[k]
        else:
            weight=(fn-fp)/(p0[k]+p1[k])
            if not 0 <= weight <= 1:
                raise AssertionError("threshold crossing outside [0,1]")
            decision[k]=weight
            fp+=weight*p0[k]
            fn-=weight*p1[k]
            break
    if fp!=fn:
        raise AssertionError("a normalized ROC frontier must cross FP=FN")
    verified=clean_count_composite_errors(length,q,tuple(decision))
    if verified != (fp,fn):
        raise AssertionError("independent error reconstruction disagrees")
    return fp,tuple(decision)
