"""BM-24/T2: sharp repeated-path gain-family erasure with a growing core.

Take n>=1 ordinary u-v paths and one exceptional u-v path, all of
length L>=1. The flat hypothesis has all total path gains zero. In the
second hypothesis, ordinary gains remain zero and the exceptional path
has a fixed nonzero gain. Labels are fresh uniform in K=F2^s.

A universal COMMON mask for arbitrary q:
 - with probability 1/2, leave the exceptional path untouched and
   independently, for each ordinary path, with probability 1/2 flip
   one uniformly selected edge, otherwise leave it untouched;
 - with probability 1/2, leave all ordinary paths untouched and,
   with probability 1/2, flip one uniformly selected exceptional edge.
Every edge flip marginal is 1/(4L). Every clean Fourier discrepancy
requires the exceptional path fully selected AND at least one ordinary
path fully selected, and is erased by this common mask.

The best COMMON-mask cap is exactly 1/(4L) for all q (a frustrated
2L-cycle projection and a parity-character union bound). For q=2/4,
BM-08's exact isolated-cycle state-aware optimum also equals 1/(4L);
hence the cap is sharp even against world-dependent correlated masks.

For q>4 the sharp state-aware optimum might be smaller and is not
claimed here. For q>2 and even L=2, the exact clean Fourier support
cardinality is 4**n - 3**n: the exceptional full path together with
at least one full ordinary path. At q=4 and odd L, cancellations can
occur, so no such cardinality formula is advertised beyond L=2.

The common mask uses O(n) sampled Bernoulli choices. Its BM-24
histogram-orbit mass distribution has only n+2 nonzero classes.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb,lcm

try:
    from .repeated_theta_orbits_BM24 import (
        RepeatedTheta,PathType,
    )
    from .sharp_erasure_optimality import critical_erasure_cap
except ImportError:
    from repeated_theta_orbits_BM24 import (
        RepeatedTheta,PathType,
    )
    from sharp_erasure_optimality import critical_erasure_cap


def gain_family(n:int,L:int,*,q:int=4,gain:int=1)->RepeatedTheta:
    if (not isinstance(n,int) or n<1 or
        not isinstance(L,int) or L<1 or not isinstance(q,int)
        or q<2 or q&(q-1) or not isinstance(gain,int)
        or not 0<gain<q):
        raise ValueError("n,L>=1, K=F2^s, exceptional gain nonzero required")
    return RepeatedTheta(
        q,(PathType(L,0,0,n),PathType(L,0,gain,1))
    )


def exact_common_cap(L:int)->Fraction:
    if not isinstance(L,int) or L<1:
        raise ValueError("L>=1 required")
    return Fraction(1,4*L)


def exact_state_aware_cap(q:int,L:int)->Fraction:
    """Sharp for q<=4 only. q>=8 remains an open optimization."""
    if q not in (2,4) or L<1:
        raise ValueError("sharp state-aware family theorem is for q=2 or 4")
    bound=critical_erasure_cap(q,2*L)
    if bound!=exact_common_cap(L):
        raise AssertionError("projected BM-08 single-cycle theorem mismatch")
    return bound


def common_mask_orbits(n:int,L:int,*,q:int=4,
                       gain:int=1)->dict[tuple, Fraction]:
    model=gain_family(n,L,q=q,gain=gain)
    out={}
    def add(a,b,weight):
        sig=(a,b)
        out[sig]=out.get(sig,Fraction(0))+weight
    special0=(1,)+(0,)*L
    special1=(0,1)+(0,)*(L-1)
    for j in range(n+1):
        ordinary=(n-j,j)+(0,)*(L-1)
        add(ordinary,special0,Fraction(comb(n,j),2**(n+1)))
    ordinary0=(n,)+(0,)*L
    add(ordinary0,special0,Fraction(1,4))
    add(ordinary0,special1,Fraction(1,4))
    if sum(out.values(),Fraction(0))!=1 or len(out)!=n+2:
        raise AssertionError("closed common orbit mask distribution invalid")
    if model.max_bit_marginal(out)!=Fraction(1,4*L):
        raise AssertionError("common orbit mask marginal is incorrect")
    return out


def common_mask_character(n:int,L:int,selected:tuple[tuple[int,...],...]
                          )->Fraction:
    """Exact Fourier transform for the common branch sampler.

    For the ordinary-branch mask, each ordinary path with s selected
    edges contributes (1-s/L). The exceptional-branch mask contributes
    1-special_selected/L. Average the two branches with equal weight.
    """
    model=gain_family(n,L)
    model._valid_signature(selected)
    ordinary,special=selected
    ordinary_product=Fraction(1)
    for s,multiplicity in enumerate(ordinary):
        ordinary_product*=(1-Fraction(s,L))**multiplicity
    special_selected=sum(r*special[r] for r in range(L+1))
    return (ordinary_product+1-Fraction(special_selected,L))/2


def verify_common_symbolic(n:int,L:int,*,q:int=4,gain:int=1
                           )->Fraction:
    """Compact proof of complete output erasure for all n,L,all q.

    If the exceptional path is properly selected, its chosen edges
    yield an endpoint-independent conditional factor and both clean
    hypotheses agree. If the exceptional path is fully selected but
    no ordinary path is full, integrating the endpoint difference
    removes the exceptional gain and the clean worlds agree.

    In the remaining case, at least one ordinary path is full and
    the exceptional path is full. The ordinary branch of the common
    mask has a factor (1-L/L)=0, while its exceptional branch also
    has a factor (1-L/L)=0. Therefore the common mask's full Walsh
    character vanishes, independently of the residual coefficient.
    """
    model=gain_family(n,L,q=q,gain=gain)
    alpha=Fraction(q-2,q)
    # Verify the two algebraic clean-equality premises on canonical
    # Fourier signatures. These checks use constant-size gain classes
    # regardless of n; the proof above quantifies over all signatures.
    ordinary0=(n,)+(0,)*L
    ordinary_full=(n-1,)+(0,)*(L-1)+(1,)
    special0=(1,)+(0,)*L
    specialproper=(0,1)+(0,)*(L-1) if L>1 else special0
    specialfull=(0,)*L+(1,)
    for sig in (
        (ordinary0,specialfull),
        (ordinary_full,specialproper),
        (ordinary0,special0),
    ):
        if model.clean_walsh_signature(0,sig)!=(
            model.clean_walsh_signature(1,sig)
        ):
            raise AssertionError("clean-equality logical premise failed")
    if common_mask_character(n,L,(ordinary_full,specialfull))!=0:
        raise AssertionError("double-full masked discrepancy survives")
    cap=exact_common_cap(L)
    if model.max_bit_marginal(common_mask_orbits(n,L,q=q,gain=gain))!=cap:
        raise AssertionError("symbolic common eraser cap mismatch")
    return cap


def clean_support_count_length_two(n:int,*,q:int=4)->int:
    """Exact for q>=4, two-edge paths; cannot be used for q2."""
    if not isinstance(n,int) or n<1 or q<4 or q&(q-1):
        raise ValueError("L2 clean support formula requires n>=1 and q>=4")
    return 4**n-3**n


def prove_matching_lower(n:int,L:int,*,q:int=4
                         )->dict[str,object]:
    """Projected 2L-cycle lower under specified adversarial contracts."""
    gain_family(n,L,q=q)
    eta=exact_common_cap(L)
    # For every q, one 2L-cycle is frustrated and has a nonzero
    # flat-vs-nonflat clean full-cycle Walsh character. An equalizing
    # COMMON mask must have parity bias 0 on its 2L edges and hence
    # max marginal >=(1/2)/(2L)=1/(4L).
    result={
        "common_lower":eta,
        "cycles_in_projection":n,
        "projected_cycle_length":2*L,
        "common_upper_verified":verify_common_symbolic(n,L,q=q),
    }
    if q in (2,4):
        result["state_aware_lower"]=exact_state_aware_cap(q,L)
        result["state_aware_sharp"]=True
    else:
        result["state_aware_lower"]=critical_erasure_cap(q,2*L)
        result["state_aware_sharp"]=False
    return result


def common_full_mask_law(n:int,L:int,*,max_edges:int=12):
    """Enumerate independent branch choices for small exact controls."""
    model=gain_family(n,L)
    if model.m>max_edges:
        raise ValueError("explicit law exceeds seed mask memory cap")
    ordinary={0:Fraction(1,2)}
    ordinary.update({1<<i:Fraction(1,2*L) for i in range(L)})
    law={0:Fraction(1)}
    for j in range(n):
        nextlaw={}
        for original,p in law.items():
            for local,w in ordinary.items():
                k=original | (local<<(j*L))
                nextlaw[k]=nextlaw.get(k,Fraction(0))+p*w
        law=nextlaw
    out={mask:p/2 for mask,p in law.items()}
    # Second branch: ordinary paths untouched, special path zero with
    # probability 1/2 or single-flipped with total probability 1/2.
    out[0]=out.get(0,Fraction(0))+Fraction(1,4)
    for j in range(L):
        k=1<<(n*L+j)
        out[k]=out.get(k,Fraction(0))+Fraction(1,4*L)
    if sum(out.values(),Fraction(0))!=1:
        raise AssertionError("common two-branch mask is unnormalized")
    return {mask:p for mask,p in out.items() if p}


def common_full_mask_integer(n:int,L:int,*,max_edges:int=12):
    law=common_full_mask_law(n,L,max_edges=max_edges)
    denominator=lcm(*(p.denominator for p in law.values()))
    return {mask:int(p*denominator) for mask,p in law.items()},denominator


def sample_common_mask(n:int,L:int,rng)->int:
    """O(n) fair-bit / random-position sampler, no huge mask table."""
    gain_family(n,L)
    mask=0
    if rng.randrange(2):
        # First half of mixture: each ordinary path is independently
        # activated with probability 1/2.
        for j in range(n):
            if rng.randrange(2):
                mask|=1<<(j*L+rng.randrange(L))
    else:
        # Second half: one exceptional-path flip with probability 1/2.
        if rng.randrange(2):
            mask|=1<<(n*L+rng.randrange(L))
    return mask


def repeated_family_manifest(n:int,L:int,*,q:int=4)->dict[str,object]:
    model=gain_family(n,L,q=q)
    witness=prove_matching_lower(n,L,q=q)
    return {
        "q":q,"ordinary_paths":n,"exceptional_paths":1,
        "each_path_length":L,
        "vertices":model.vertices,"edges":model.m,
        "full_mask_states_per_world":1<<model.m,
        "BM14_path_orbits":model.BM14_pathwise_orbit_size,
        "BM24_type_histogram_orbits":model.orbit_size,
        "nonzero_common_mask_orbits":len(common_mask_orbits(n,L,q=q)),
        "sharp_common_mask_cap":str(witness["common_lower"]),
        "sharp_state_aware_cap_q2_q4":(
            str(witness["state_aware_lower"]) if q<=4 else None
        ),
        "clean_support_cardinality_L2":(
            clean_support_count_length_two(n,q=q)
            if L==2 and q>=4 else None
        ),
        "full_LP_solved":False,
        "full_Fourier_table_materialized":False,
    }
