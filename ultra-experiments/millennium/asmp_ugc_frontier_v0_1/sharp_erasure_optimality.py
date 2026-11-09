"""BM-08: sharp erasure cap for ALL F2^s gain cycles of length >=2.

In the frozen two-hypothesis observation model, each episode draws fresh
uniform vertex labels; the monitor observes Boolean edge-satisfaction bits.
The adversary chooses a hypothesis-dependent XOR readout mask law, independent
of the current clean vector. Every mask coordinate has marginal <= eta.
The two reported laws can be made identical iff eta >= critical_erasure_cap.

For q=2 or 4, this cap is 1/(2L) and a COMMON one-hot mask law attains it.
For q>=8, the BM-07 parity-class construction is optimal, attaining
    q*2^(L-2) / ((q-2)^L + c_L*2^L),
where c_L=q-1 when L even and 1 when L odd.

The lower proof uses proper-subset Walsh coefficients to show
Q0(m)-Q1(m)=c*(-1)^|m|, plus an exact overlap/mask-cost argument.
This module supplies exact witnesses and finite proof-invariant checks; the
full algebraic argument is in SHARP_ERASURE_OPTIMALITY_BM08.md.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product

try:
    from .correlated_minimax import apply_correlated_mask, mask_marginals
    from .frontier_bounds import full_cycle_law, tv_distance
    from .hypothesis_aware_cycle_erasure import (
        erasure_mask_atom, erasure_parity_class_masks,
        erasure_per_bit_cap,
    )
except ImportError:
    from correlated_minimax import apply_correlated_mask, mask_marginals
    from frontier_bounds import full_cycle_law, tv_distance
    from hypothesis_aware_cycle_erasure import (
        erasure_mask_atom, erasure_parity_class_masks,
        erasure_per_bit_cap,
    )


def _validate(q: int, length: int) -> None:
    if q < 2 or q & (q - 1):
        raise ValueError("q must be 2^s with s>=1")
    if length < 2:
        raise ValueError("L must be >=2")


def common_channel_cap(length: int) -> Fraction:
    if length < 2:
        raise ValueError("L must be >=2")
    return Fraction(1, 2 * length)


def parity_class_candidate_cap(q: int, length: int) -> Fraction:
    _validate(q,length)
    if q < 4:
        raise ValueError("BM-07 parity class needs q>=4")
    return erasure_per_bit_cap(length,q)


def critical_erasure_cap(q: int, length: int) -> Fraction:
    """EXACT uniform per-bit cap for state-aware erasure, L>=2, q=2^s."""
    _validate(q,length)
    if q <= 4:
        return common_channel_cap(length)
    return parity_class_candidate_cap(q,length)


def common_one_hot_masks(length: int) -> dict[tuple[bool, ...], Fraction]:
    """Total odd-mask probability 1/2, each coordinate error 1/(2L)."""
    if length < 2:
        raise ValueError("L>=2 required")
    out={(False,)*length:Fraction(1,2)}
    for i in range(length):
        out[tuple(j==i for j in range(length))]=Fraction(1,2*length)
    return out


def sharp_erasure_masks(q: int,length: int):
    """Attaining (flat-mask, frustrated-mask) laws with exact capped marginals."""
    _validate(q,length)
    if q <= 4:
        mask=common_one_hot_masks(length)
        return dict(mask),dict(mask)
    return erasure_parity_class_masks(length,q)


def masked_distributions(q: int,length: int):
    """Independent full-pattern oracle for the achieving pair."""
    m0,m1=sharp_erasure_masks(q,length)
    clean0=full_cycle_law(length,q,flat=True)
    clean1=full_cycle_law(length,q,flat=False)
    return apply_correlated_mask(clean0,m0),apply_correlated_mask(clean1,m1)


def verify_sharp_witness(q: int,length: int) -> bool:
    """All equalities below are checked with exact rational arithmetic."""
    target=critical_erasure_cap(q,length)
    m0,m1=sharp_erasure_masks(q,length)
    if not all(sum(m.values())==1 for m in (m0,m1)):
        return False
    if any(v != target for m in (m0,m1) for v in mask_marginals(m)):
        return False
    a,b=masked_distributions(q,length)
    return a==b and tv_distance(a,b)==0


def clean_full_walsh(q: int,length: int) -> tuple[Fraction,Fraction]:
    """E[(-1)^sum satisfaction bits] flat/nonflat.

    This is the character of the set of ALL L edge indicators. Proper-set
    coefficients equal (1-2/q)^|S| under both hypotheses, q>2.
    """
    _validate(q,length)
    x=(q-2)**length
    t=(-2)**length
    return (Fraction(x+(q-1)*t,q**length),
            Fraction(x-t,q**length))


def proof_regime(q: int,length: int) -> str:
    """Choose the independent mathematical lower-bound certificate."""
    _validate(q,length)
    return ("binary-parity-union" if q==2
            else "q4-opposite-or-zero-full-Walsh" if q==4
            else "parity-difference-overlap-cost")


def overlap_lower_bound_for_erasing_pair(
    q: int,length: int,
    flat_masks: dict[tuple[bool, ...],Fraction],
    nonflat_masks: dict[tuple[bool, ...],Fraction],
) -> dict[str,Fraction | bool]:
    """Verify algebraic necessary inequality for q>=4 and zero-TV mask pairs.

    Fourier equality forces Q0(m)-Q1(m)=c*(-1)^|m| for all masks m,
    since all proper clean Walsh coefficients are common and nonzero.
    Let R(m)=min(Q0(m),Q1(m)), r=R(odd), a=|c|.
    Then average mask flip probability in EACH law is >=
        2^(L-2)*a + r/L.
    Hence max per-edge flip cap obeys the same lower bound.
    This is a necessary bound for ANY zero-TV pair under the contract.
    """
    _validate(q,length)
    if q==2:
        raise ValueError("proper Walsh argument requires q>2")
    masks=tuple(product((False,True),repeat=length))
    if not all(
        sum(law.values())==1 and all(p>=0 for p in law.values()) and
        all(len(mask)==length for mask in law)
        for law in (flat_masks,nonflat_masks)
    ):
        raise ValueError("need valid normalized mask laws")
    clean0=full_cycle_law(length,q,flat=True)
    clean1=full_cycle_law(length,q,flat=False)
    out0=apply_correlated_mask(clean0,flat_masks)
    out1=apply_correlated_mask(clean1,nonflat_masks)
    if out0!=out1:
        raise ValueError("mask pair does not erase output law")
    differences=[
        (flat_masks.get(m,Fraction(0))-nonflat_masks.get(m,Fraction(0))) *
        (-1)**sum(m) for m in masks
    ]
    if len(set(differences))!=1:
        raise AssertionError("proper-Walsh difference constraint failed")
    coeff=differences[0]
    a=abs(coeff)
    r=sum((min(flat_masks.get(m,Fraction(0)),
               nonflat_masks.get(m,Fraction(0)))
           for m in masks if sum(m)%2),Fraction(0))
    lower=2**(length-2)*a + r/length
    observed=max(mask_marginals(flat_masks)+mask_marginals(nonflat_masks))
    if lower>observed:
        raise AssertionError("overlap lower bound violated")
    return {"coefficient":coeff,"forced_mass":a,
            "shared_odd_mass":r,"necessary_cap":lower,
            "observed_cap":observed,
            "matches_theorem":observed>=critical_erasure_cap(q,length)}


def algebraic_optimality_certificate(q: int,length: int) -> dict[str,object]:
    """Finite exact check of the symbolic case distinction in the proof.

    This is a computational verifier of closed-form constants, not a
    substitute for the quantification over all mask distributions proved
    in the research note.
    """
    _validate(q,length)
    t=common_channel_cap(length)
    if q==2:
        return {"regime":proof_regime(q,length),
                "critical":t,"construction":t,
                "critical_reached":verify_sharp_witness(q,length)}
    A,B=clean_full_walsh(q,length)
    if q==4:
        if length%2:
            assert A==-B and A<0 and B>0
        else:
            assert A>0 and B==0
        return {"regime":proof_regime(q,length),
                "critical":t,"construction":t,
                "clean_full_walsh":(A,B),
                "critical_reached":verify_sharp_witness(q,length)}
    assert A>0 and B>0
    atom=erasure_mask_atom(length,q)
    v=2**(length-2)*atom
    assert v<=t
    D=(q-2)**length+((q-1) if length%2==0 else 1)*2**length
    assert atom==Fraction(q,D)
    return {"regime":proof_regime(q,length),"critical":v,
            "candidate_atom":atom,"common_cap":t,
            "clean_full_walsh":(A,B),
            "critical_reached":verify_sharp_witness(q,length)}
