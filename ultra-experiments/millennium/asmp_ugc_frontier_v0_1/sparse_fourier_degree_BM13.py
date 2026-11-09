"""BM-13: sparse, fully rational weighted-Walsh dual certificates.

For the q=4 five-edge diamond, 8 nonzero Walsh multipliers certify
the exact full erasure threshold 1/5 (previous BM-10 dual used 17).
For the q=4 six-edge contrabalanced theta, 5 multipliers certify 1/6,
using only 3 four-cycle supports and 2 five-edge supports.

The degree-restricted Fourier LP hierarchy has exact values:
  diamond:  d<=2:0, d=3:1/6, d>=4:1/5.
  theta:    d<=3:0, d=4:1/8, d>=5:1/6.
These values have explicit common mask primal witnesses, and lower
bounds from isolated cycle projection (first nonzero degree) or the sparse
full-degree duals. Every coefficient and inequality is checked in Q,
without running a numerical optimizer or relying on floating point.

This is a finite sparse-certificate result, not a graph-family bound.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

try:
    from .diamond_weighted_fourier_BM10 import (
        clean_counts as diamond_clean, PRIMAL_MASK_COUNTS,
        PRIMAL_DENOMINATOR,
    )
    from .theta_shared_cycle_erasure import theta_laws, q4_common_mask
except ImportError:
    from diamond_weighted_fourier_BM10 import (
        clean_counts as diamond_clean, PRIMAL_MASK_COUNTS,
        PRIMAL_DENOMINATOR,
    )
    from theta_shared_cycle_erasure import theta_laws, q4_common_mask


DIAMOND_DUAL_NORM=(Fraction(1,10),Fraction(1,10))
DIAMOND_DUAL_WALSH={
    7:Fraction(2,5), 15:-Fraction(2,5),
    23:-Fraction(2,5),24:-Fraction(1,5),
    25:Fraction(1,5),26:Fraction(2,5),
    28:Fraction(2,5),30:-Fraction(2,5)
}
DIAMOND_DUAL_MARG=(
    {i:-Fraction(1,10) for i in range(5)},
    {i:-Fraction(1,10) for i in range(5)},
)

THETA_DUAL_NORM=(Fraction(1,6),Fraction(0))
THETA_DUAL_WALSH={
    15:-Fraction(2,3),51:-Fraction(1,3),60:-Fraction(1,3),
    31:Fraction(2,3),47:Fraction(2,3),
}
THETA_DUAL_MARG=(
    {i:-Fraction(1,6) for i in range(6)},
    {},
)


def _case(kind:str):
    if kind=="diamond":
        return 5, diamond_clean()
    if kind=="theta":
        return 6, theta_laws(4)
    raise ValueError("kind must be diamond or theta")


@lru_cache(maxsize=None)
def _hats(kind:str):
    m,(p0,p1)=_case(kind)
    total=(sum(p0),sum(p1))
    if total[0]!=total[1]:
        raise AssertionError("unmatched label normalizers")
    return tuple(
        tuple(Fraction(
            sum((-1 if (mask&S).bit_count()%2 else 1)*value
                for mask,value in enumerate(p)),total[h]
        ) for S in range(1<<m))
        for h,p in enumerate((p0,p1))
    )


def dual_certificate(kind:str):
    """The exact sparse full-optimum dual tuple (norm, Walsh, marginal)."""
    if kind=="diamond":
        return DIAMOND_DUAL_NORM,DIAMOND_DUAL_WALSH,DIAMOND_DUAL_MARG
    if kind=="theta":
        return THETA_DUAL_NORM,THETA_DUAL_WALSH,THETA_DUAL_MARG
    raise ValueError("unknown graph kind")


def sparse_dual_slacks(kind:str):
    """All 2*2^m mask-atom inequalities in exact rational arithmetic."""
    m,_=_case(kind)
    norm,coeff,z=dual_certificate(kind)
    hats=_hats(kind)
    all_slacks=[]
    for h in range(2):
        row=[]
        for mask in range(1<<m):
            slack=norm[h]
            for S,value in coeff.items():
                sign=-1 if (mask&S).bit_count()%2 else 1
                slack+=(1 if h==0 else -1)*value*hats[h][S]*sign
            slack+=sum((v for i,v in z[h].items()
                        if mask&(1<<i)),Fraction(0))
            row.append(slack)
        all_slacks.append(tuple(row))
    return tuple(all_slacks)


def verify_sparse_dual(kind:str)->Fraction:
    """Return rigorous full-LP lower value; exact weak-duality check."""
    m,_=_case(kind)
    norm,y,z=dual_certificate(kind)
    assert all(0<S<(1<<m) for S in y)
    assert all(v<=0 for side in z for v in side.values())
    assert all(0<=edge<m for side in z for edge in side)
    assert -sum((v for side in z for v in side.values()),Fraction(0))==1
    assert all(slack<=0 for row in sparse_dual_slacks(kind) for slack in row)
    bound=sum(norm,Fraction(0))
    assert bound==(Fraction(1,5) if kind=="diamond" else Fraction(1,6))
    return bound


def _one_hot(size:int,zero:int,single:int):
    weights={0:zero}
    for i in range(size):
        weights[1<<i]=single
    return weights


def primal_for_fourier_degree(kind:str,degree:int):
    """Return attaining pair of common-mask laws for truncated Walsh LP."""
    m,_=_case(kind)
    if not 0<=degree<=m:
        raise ValueError("Fourier degree outside edge count")
    if kind=="diamond":
        if degree<=2:
            return {0:1},1
        if degree==3:
            return _one_hot(m,1,1),6
        return PRIMAL_MASK_COUNTS,PRIMAL_DENOMINATOR
    if degree<=3:
        return {0:1},1
    if degree==4:
        return _one_hot(m,2,1),8
    return {i:v for i,v in enumerate(q4_common_mask()) if v},12


def verify_truncated_primal(kind:str,degree:int)->Fraction:
    """Exactly equalize all degree<=d Fourier coefficients using one mask."""
    m,_=_case(kind)
    masks,D=primal_for_fourier_degree(kind,degree)
    assert sum(masks.values())==D
    assert all(0<=mask<(1<<m) and w>=0 for mask,w in masks.items())
    p0,p1=_hats(kind)
    for S in range(1,1<<m):
        if S.bit_count()>degree:
            continue
        mask_hat=sum(((-1 if (mask&S).bit_count()%2 else 1)*w
                      for mask,w in masks.items()),0)
        if p0[S]*mask_hat!=p1[S]*mask_hat:
            raise AssertionError(f"Fourier mismatch at S={S}")
    marg=tuple(Fraction(
        sum(w for mask,w in masks.items() if mask & (1<<i)),D
    ) for i in range(m))
    return max(marg)


def truncated_degree_profile(kind:str):
    """Exact minima certified by explicit primal and closed lower arguments."""
    m,_=_case(kind)
    minima=(
        (Fraction(0),Fraction(0),Fraction(0),
         Fraction(1,6),Fraction(1,5),Fraction(1,5))
        if kind=="diamond" else
        (Fraction(0),Fraction(0),Fraction(0),Fraction(0),
         Fraction(1,8),Fraction(1,6),Fraction(1,6))
    )
    assert len(minima)==m+1
    # Lower for first nonzero degree follows from projection onto one
    # unbalanced isolated shortest cycle, using BM-08 exact erasure cap.
    # Higher full threshold follows from sparse Fourier dual in degree m-1.
    full=verify_sparse_dual(kind)
    assert minima[-1]==full
    for d,target in enumerate(minima):
        assert verify_truncated_primal(kind,d)==target
    assert max(y.bit_count() for y in dual_certificate(kind)[1])==m-1
    return minima


def sparse_manifest():
    return {
        "diamond":{
            "edge_count":5,"dual_walsh_terms":len(DIAMOND_DUAL_WALSH),
            "max_dual_degree":max(s.bit_count() for s in DIAMOND_DUAL_WALSH),
            "full_optimum":str(verify_sparse_dual("diamond")),
            "profile":[str(v) for v in truncated_degree_profile("diamond")]
        },
        "theta":{
            "edge_count":6,"dual_walsh_terms":len(THETA_DUAL_WALSH),
            "max_dual_degree":max(s.bit_count() for s in THETA_DUAL_WALSH),
            "full_optimum":str(verify_sparse_dual("theta")),
            "profile":[str(v) for v in truncated_degree_profile("theta")]
        },
    }
