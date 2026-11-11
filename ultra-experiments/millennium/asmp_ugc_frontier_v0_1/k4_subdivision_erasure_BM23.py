"""BM-23/T2: sharp q4 erasure for a single subdivided K4 core edge.

Core K4 has vertices 0..3, ordered edges
  e0=01, e1=02, e2=03, e3=12, e4=13, e5=23,
with flat gains zero and frustrated gains (0,0,0,1,2,1).
Replace e0 by a path of L edges, retaining the other five edges.

Exact fully hypothesis-aware XOR readout erasure cap:
    L=1: 3/14, by BM-17.
    L>=2: 1/5, by projecting to the five-edge contrabalanced diamond
           K4-e0 (BM-10) for the lower bound, and an explicit COMMON
           mask for the upper bound.

L=2: a 21-path-orbit exact rational common mask with denominator 40.
L>=3: take the BM-10 diamond common eraser (cap 1/5), independently
       add fair one-hot parity erasure of the entire new e0 path
       (rate 1/(2L)<=1/6). Under any Fourier selected subset S:
       - if long e0 path is fully selected, its one-hot Walsh factor
         is zero;
       - otherwise its selected proper edges factor alpha^s out of
         the clean Walsh difference, leaving only the independently
         erased five-edge diamond character.

The upper construction verifies every necessary Fourier identity from
32 diamond subsets without enumerating 2^(L+5) edge masks or q^V labels.
For small L the complete output equality is independently verified by
direct vertex-label enumeration. The result concerns this frozen K4
gain configuration; no general arbitrary-core sharp formula is implied.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import lcm

try:
    from .core_subdivision_orbit_BM23 import CoreSubdivision
    from .diamond_weighted_fourier_BM10 import (
        PRIMAL_MASK_COUNTS as BM10_DIAMOND_MASK,
        PRIMAL_DENOMINATOR as BM10_DIAMOND_DENOM,
        verify_full_primal as verify_BM10_diamond,
        verify_full_dual as verify_BM10_dual,
    )
    from .theta_orbit_lp_BM14 import expand_orbit_masses
except ImportError:
    from core_subdivision_orbit_BM23 import CoreSubdivision
    from diamond_weighted_fourier_BM10 import (
        PRIMAL_MASK_COUNTS as BM10_DIAMOND_MASK,
        PRIMAL_DENOMINATOR as BM10_DIAMOND_DENOM,
        verify_full_primal as verify_BM10_diamond,
        verify_full_dual as verify_BM10_dual,
    )
    from theta_orbit_lp_BM14 import expand_orbit_masses


K4_EDGES=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))
K4_FLAT=(0,0,0,0,0,0)
K4_OTHER=(0,0,0,1,2,1)

# Exact symmetric readout orbit witness discovered by a numerical LP,
# reconstructed at denominator 40, and checked in Q in all regression tests.
# Orbit coordinates are (number flipped in the L=2 path, bit1,...,bit5).
L2_ORBIT_NUMERATORS={
    (0,0,0,0,0,0):6,
    (0,0,0,0,0,1):2,
    (0,0,0,0,1,0):3,
    (0,0,0,0,1,1):1,
    (0,0,0,1,0,0):2,
    (0,0,1,0,0,0):2,
    (0,0,1,0,0,1):1,
    (0,0,1,1,0,0):1,
    (0,1,0,0,0,0):3,
    (0,1,0,0,1,0):2,
    (0,1,0,1,0,0):1,
    (1,0,0,0,0,0):4,
    (1,0,0,0,0,1):2,
    (1,0,0,0,1,0):1,
    (1,0,0,0,1,1):1,
    (1,0,0,1,0,0):2,
    (1,0,1,0,0,0):2,
    (1,0,1,0,0,1):1,
    (1,0,1,1,0,0):1,
    (1,1,0,0,0,0):1,
    (1,1,0,1,0,0):1,
}
L2_DENOM=40


def k4_single_subdivision(L:int,*,q:int=4)->CoreSubdivision:
    if not isinstance(L,int) or L<1 or q!=4:
        raise ValueError("registered theorem needs L>=1 and q=4")
    return CoreSubdivision(
        q,4,K4_EDGES,(L,1,1,1,1,1),K4_FLAT,K4_OTHER
    )


def exact_cap(L:int)->Fraction:
    if not isinstance(L,int) or L<1:
        raise ValueError("positive subdivision length required")
    return Fraction(3,14) if L==1 else Fraction(1,5)


def l2_orbit_mask()->dict[tuple[int,...],Fraction]:
    law={s:Fraction(w,L2_DENOM) for s,w in L2_ORBIT_NUMERATORS.items()}
    if sum(law.values(),Fraction(0))!=1:
        raise AssertionError("invalid rational L2 mask total")
    return law


def l2_mask_law()->dict[int,Fraction]:
    """Expand a 21-orbit mass witness uniformly within its path counts."""
    return {m:w for m,w in expand_orbit_masses(
        k4_single_subdivision(2).lengths,l2_orbit_mask()
    ).items() if w}


def _diamond_k4_mask(L:int)->dict[int,Fraction]:
    """Pull the BM-10 exact mask through the diamond edge isomorphism.

    BM-10 direct / via A / via B edge order maps to K4 e5/e1/e2/e3/e4.
    The K4-e0 path gains are (1,0,3) and the original BM-10 gains are
    (0,1,2), each a triple of distinct F2^2 values; by switching and the
    gain-equality partition they have identical full Boolean pattern laws.
    """
    if L<1:
        raise ValueError("positive long-path length required")
    d_to_core=(L+4,L,L+1,L+2,L+3)
    result={}
    for m,w in BM10_DIAMOND_MASK.items():
        pattern=sum(1<<target for i,target in enumerate(d_to_core)
                    if m&(1<<i))
        result[pattern]=Fraction(w,BM10_DIAMOND_DENOM)
    if sum(result.values(),Fraction(0))!=1:
        raise AssertionError("diamond mask remapping normalization")
    return result


def product_mask_law(L:int,*,max_states:int=25000)->dict[int,Fraction]:
    """Common exact full-mask witness for L>=3, for bounded sizes."""
    if not isinstance(L,int) or L<3:
        raise ValueError("product construction needs L>=3")
    diamond=_diamond_k4_mask(L)
    if len(diamond)*(L+1)>max_states:
        raise ValueError("full mask expansion exceeds resource cap")
    path={0:Fraction(1,2)}
    path.update({1<<i:Fraction(1,2*L) for i in range(L)})
    result={}
    for a,pa in diamond.items():
        for b,pb in path.items():
            if a&b:
                raise AssertionError("independent mask blocks overlap")
            result[a|b]=pa*pb
    assert sum(result.values(),Fraction(0))==1
    return result


def mask_for_small(L:int,*,max_states:int=25000)->dict[int,Fraction]:
    if L==2:
        return l2_mask_law()
    if L>=3:
        return product_mask_law(L,max_states=max_states)
    raise ValueError("L=1 is handled by the original BM-17 witness")


def _mask_character(law:dict[int,Fraction],S:int)->Fraction:
    return sum(
        (p*(-1 if (x&S).bit_count()%2 else 1)
         for x,p in law.items()),Fraction(0)
    )


def exact_mask_rate(m:int,law:dict[int,Fraction])->Fraction:
    if sum(law.values(),Fraction(0))!=1:
        raise ValueError("normalized mask law needed")
    return max((sum(
        (p for x,p in law.items() if x&(1<<i)),Fraction(0)
    ) for i in range(m)),default=Fraction(0))


def prove_diamond_projection_lower(L:int)->Fraction:
    """Exact lower bound from the unchanged five-edge contrabalanced minor.

    Any full-graph equalizing mask pair projects onto K4-e0, whose three
    u-v path gains (1,0,3) are distinct over F2^2. The BM-10 theorem
    and the BM-12 gain-equality invariance give eta>=1/5, independently
    of L and independent of whether the full-world masks differ.
    """
    c=k4_single_subdivision(L)
    assert c.q==4 and c.k==6
    gains=(c.gains1[5],c.gains1[1]^c.gains1[2],
           c.gains1[3]^c.gains1[4])
    if len(set(gains))!=3:
        raise AssertionError("remaining five-edge diamond not contrabalanced")
    assert verify_BM10_diamond() and verify_BM10_dual()
    return Fraction(1,5)


def verify_L2_exact()->Fraction:
    """Full-orbit K4-subdivision q4 upper plus BM-10 diamond lower."""
    c=k4_single_subdivision(2)
    rate=c.verify_orbit_primal(l2_orbit_mask(),l2_orbit_mask())
    if rate!=Fraction(1,5):
        raise AssertionError("L2 common channel cap changed")
    if prove_diamond_projection_lower(2)!=rate:
        raise AssertionError("L2 witness does not match lower bound")
    return rate


def verify_L_ge3_symbolic(L:int)->Fraction:
    """Constant-core-sized upper/lower proof, including huge L.

    For any Fourier edge set with a full long path, fair one-hot noise
    gives mask Walsh zero. For a proper subset of the long path,
    the clean difference factors as alpha^s times the 5-edge
    diamond difference, which the BM-10 common mask nullifies.
    Thus every full observation character is equalized.
    """
    if not isinstance(L,int) or L<3:
        raise ValueError("L>=3 required")
    c=k4_single_subdivision(L)
    diamond=_diamond_k4_mask(L)
    for subset in range(32):
        S=subset<<L
        if c.clean_delta(S)*_mask_character(diamond,S):
            raise AssertionError(
                "BM-10 diamond mask fails proper-path Fourier restriction"
            )
    # The long-path Fourier transform is 1-s/L, so it is zero
    # on the full path and otherwise simply multiplies a zero
    # already supplied by the diamond mask (or a zero clean delta).
    long_path_rate=Fraction(1,2*L)
    diamond_rate=max(
        sum((p for x,p in diamond.items() if x&(1<<(L+i))),
            Fraction(0))
        for i in range(5)
    )
    cap=max(long_path_rate,diamond_rate)
    if cap!=prove_diamond_projection_lower(L):
        raise AssertionError("product mask misses projected sharp bound")
    return cap


def sample_common_mask(L:int,rng)->int:
    """Exact small-description sampler for the entire long-subdivision family."""
    if L<3:
        raise ValueError("sampler uses product construction for L>=3")
    ticket=rng.randrange(BM10_DIAMOND_DENOM)
    chosen=0
    for mask,mass in BM10_DIAMOND_MASK.items():
        ticket-=mass
        if ticket<0:
            chosen=mask
            break
    mapping=(L+4,L,L+1,L+2,L+3)
    output=sum((1<<mapping[i] for i in range(5)
                if chosen&(1<<i)),0)
    if rng.randrange(2):
        output|=1<<rng.randrange(L)
    return output


def theorem_receipt(L:int)->dict[str,object]:
    cap=(verify_L2_exact() if L==2 else
         verify_L_ge3_symbolic(L) if L>=3 else Fraction(3,14))
    c=k4_single_subdivision(L)
    return {
        "core":"K4, q4, one subdivided edge",
        "subdivision_length":L,
        "total_vertices":c.vertices,
        "total_reported_edges":c.m,
        "raw_masks_per_world":1<<c.m,
        "path_orbit_masks_per_world":c.orbit_size,
        "sharp_hypothesis_aware_cap":str(cap),
        "common_channel_attains":True,
        "clean_residual_support_count":c.clean_support_count(),
        "full_mask_table_created":False,
        "independent_subgraph_lower_bound":"BM-10 diamond 1/5" if L>=2
                                      else "BM-17 K4 3/14",
    }
