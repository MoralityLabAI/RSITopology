"""BM-07/T2: explicit hypothesis-aware erasure on a simple gain cycle.

For a cycle of length L>=2 and finite abelian gain group size q=2^s>=4,
let X be the full Boolean vector of satisfied edges under a *fresh uniform*
vertex labeling. If flat vs frustrated readout mask distributions may depend
on the true hypothesis (but remain independent of the current clean X),
the following symmetric parity-class masks produce IDENTICAL output laws.

Let D=(q-2)^L + [(q-1) if L even else 1]*2^L and a=q/D.
Under flat use every nonzero mask of parity opposite to L with mass a
per mask; under frustrated use every nonzero mask of parity equal to L
with mass a per mask. Put all remaining mass on the zero mask.
Every bit has marginal flip probability eta=2^(L-2)*a in BOTH worlds.
The mask distributions are legal for q>=4.

This is a CONSTRUCTIVE SUFFICIENT erasure threshold; its optimality for
general L has not been proved by this module. For L=2 and q>=4 it matches
the exact minimax threshold from hypothesis_aware_two_edge.py.

When q>4 fixed and L grows, eta is asymptotically
(q/4)*(2/(q-2))^L, exponentially smaller than the common-channel
erasure threshold 1/(2L). This is a special-case symmetrizability
construction for a frozen statistical experiment, not a physical
attack or agent monitoring guarantee.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product

try:
    from .frontier_bounds import full_cycle_law, tv_distance
    from .correlated_minimax import apply_correlated_mask, mask_marginals
except ImportError:
    from frontier_bounds import full_cycle_law, tv_distance
    from correlated_minimax import apply_correlated_mask, mask_marginals


def erasure_mask_atom(length: int, q: int) -> Fraction:
    """Per-mask nonzero probability in the parity-class erasure construction."""
    if length < 2 or q < 4 or q & (q-1):
        raise ValueError("seed construction requires L>=2 and q=2^s>=4")
    denominator=(q-2)**length + ((q-1) if length%2==0 else 1)*2**length
    return Fraction(q,denominator)


def erasure_per_bit_cap(length: int,q: int) -> Fraction:
    """Exact per-coordinate marginal error in both hypothesis-dependent laws."""
    return 2**(length-2)*erasure_mask_atom(length,q)


def common_erasure_per_bit_cap(length: int) -> Fraction:
    """Hypothesis-blind common-channel threshold under equal per-bit caps."""
    if length<1:
        raise ValueError("cycle length must be positive")
    return Fraction(1,2*length)


def erasure_parity_class_masks(length: int,q: int):
    """Return exact (flat-mask, frustrated-mask) probability distributions.

    Each distribution is invariant under permutations of edge coordinates.
    It is independent of the current clean labeling, yet the adversary
    is allowed to choose it depending on the hidden hypothesis.
    """
    a=erasure_mask_atom(length,q)
    zero=(False,)*length
    masks=tuple(product((False,True),repeat=length))
    flat_class=1-(length%2)
    frust_class=length%2

    def make(parity):
        selected=tuple(mask for mask in masks
                       if any(mask) and sum(mask)%2 == parity)
        pzero=1-len(selected)*a
        if pzero<0:
            raise AssertionError("negative unflipped mass")
        law={zero:pzero}
        law.update({mask:a for mask in selected})
        return {mask:Fraction(p) for mask,p in law.items() if p}

    flat=make(flat_class)
    frustrated=make(frust_class)
    expected=erasure_per_bit_cap(length,q)
    for law in (flat,frustrated):
        marginals=mask_marginals(law)
        if marginals!=(expected,)*length:
            raise AssertionError("one-coordinate cap mismatch")
    return flat,frustrated


def equalized_output_laws(length: int,q: int):
    """Two complete masked observation distributions (must agree exactly)."""
    m0,m1=erasure_parity_class_masks(length,q)
    out0=apply_correlated_mask(full_cycle_law(length,q,flat=True),m0)
    out1=apply_correlated_mask(full_cycle_law(length,q,flat=False),m1)
    if out0 != out1:
        raise AssertionError("hypothesis-aware symmetrization failed")
    if tv_distance(out0,out1):
        raise AssertionError("output TV must be zero")
    return out0,out1


def active_erased_cycle_response(
    length: int, q: int, hidden_h: int, chosen_shift: int
):
    """Exact conditional output law for a known-shift active experiment.

    The returned law is the same under every unknown holonomy h if
    monitoring permits hypothesis-aware masks at the constructed cap.
    """
    if not 0<=hidden_h<q or not 0<=chosen_shift<q:
        raise ValueError("hidden/controlled gain must lie in K=F2^s")
    a,b=equalized_output_laws(length,q)
    return a if hidden_h==chosen_shift else b
