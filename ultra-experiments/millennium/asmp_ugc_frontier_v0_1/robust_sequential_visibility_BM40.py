"""BM-40: exact-rational enclosures for finite-n Hellinger visibility.

A complete output likelihood under the fixed BM-27 graded channel is
permutation-invariant in the n ordinary paths. Count each four-category
ordinary histogram and exceptional outcome; the multinomial-weighted
joint law is EXACT over the original 4**(n+1) full reports.

Each Hellinger summand sqrt(P0(c,z)P1(c,z)) gets an exact rational
floor/ceiling from integer isqrt at decimal scale 10**digits.
A tight upper bound Bhi<1 certifies an iid-episode Bayes risk
  R_m^* <= Bhi**m/2.
A lower affinity bound Blo gives
  R_m^* >= (1-sqrt(1-Blo**(2m)))/2.
This is a fixed-channel IID episodic certificate; no guarantees for
arbitrary history-adaptive across-episode readout masking.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb, isqrt

try:
    from .replication_uniform_upper_BM27 import (
        PAIRS,CLEAN_COMPONENTS,COMPONENTS,xor_pair,
        exact_clean_law,explicit_mask_law,xor_convolve,
    )
    from .exact_graded_visibility_BM39 import graded_total_variation
except ImportError:
    from replication_uniform_upper_BM27 import (
        PAIRS,CLEAN_COMPONENTS,COMPONENTS,xor_pair,
        exact_clean_law,explicit_mask_law,xor_convolve,
    )
    from exact_graded_visibility_BM39 import graded_total_variation


def _valid(n:int,lam:Fraction)->Fraction:
    if not isinstance(n,int) or not 1<=n<=32:
        raise ValueError("explicit histogram oracle requires 1<=n<=32")
    lam=Fraction(lam)
    if not 0<=lam<=1:
        raise ValueError("mixing weight in [0,1] required")
    return lam


@lru_cache(maxsize=128)
def _branches(h:int,lam:Fraction)->tuple:
    if h not in (0,1):
        raise ValueError("hidden world must be 0 or 1")
    masks=[
        (o,s,(1-lam)*Fraction(w,13))
        for o,s,w in COMPONENTS[h]
    ]
    if lam:
        masks.append(("I","I",lam))
    out=[]
    for clean_ord,clean_special,clean_w in CLEAN_COMPONENTS[h]:
        for mask_ord,mask_special,mask_w in masks:
            w=Fraction(clean_w,8)*mask_w
            if w:
                out.append((
                    w,
                    xor_pair(PAIRS[clean_ord],PAIRS[mask_ord]),
                    xor_pair(PAIRS[clean_special],PAIRS[mask_special]),
                ))
    if sum((w for w,_,_ in out),Fraction())!=1:
        raise AssertionError("bad mixture weights")
    return tuple(out)


def histograms(n:int):
    for a in range(n+1):
        for b in range(n+1-a):
            for c in range(n+1-a-b):
                yield a,b,c,n-a-b-c


def multinomial(n:int,c:tuple[int,...])->int:
    if len(c)!=4 or sum(c)!=n or any(i<0 for i in c):
        raise ValueError("invalid four-category histogram")
    return comb(n,c[0])*comb(n-c[0],c[1])*comb(n-c[0]-c[1],c[2])


def _hist_masses(n:int,c:tuple[int,...],branches:tuple)->tuple[Fraction,...]:
    multiplier=multinomial(n,c)
    masses=[Fraction() for _ in range(4)]
    for weight,ordinary,special in branches:
        t=weight
        for i,num in enumerate(c):
            if num:
                t*=ordinary[i]**num
        if t:
            for z in range(4):
                masses[z]+=t*special[z]
    return tuple(multiplier*p for p in masses)


@lru_cache(maxsize=16)
def exact_histogram_laws(n:int,lam:Fraction)->tuple[dict,dict]:
    lam=_valid(n,lam)
    out=[{},{}]
    branches=tuple(_branches(h,lam) for h in (0,1))
    for c in histograms(n):
        for h in (0,1):
            masses=_hist_masses(n,c,branches[h])
            for z,p in enumerate(masses):
                if p:
                    out[h][(c,z)]=p
    for h in (0,1):
        if sum(out[h].values(),Fraction())!=1:
            raise AssertionError("histogram law not normalized")
    return out[0],out[1]


def exact_histogram_tv(n:int,lam:Fraction)->Fraction:
    p0,p1=exact_histogram_laws(n,_valid(n,lam))
    return sum((abs(p0.get(k,0)-p1.get(k,0))
                for k in p0.keys()|p1.keys()),Fraction())/2


def _sqrt_interval(p:Fraction,scale:int)->tuple[int,int]:
    if p<0 or scale<1:
        raise ValueError("sqrt interval needs nonnegative rational and scale")
    if not p:
        return 0,0
    a=p.numerator*scale*scale
    q=p.denominator
    lo=isqrt(a//q)
    exact=(lo*lo*q==a)
    return lo,lo if exact else lo+1


@dataclass(frozen=True)
class HellingerReceipt:
    n:int
    lam:Fraction
    histogram_states:int
    sqrt_terms:int
    precision_digits:int
    affinity_lower:Fraction
    affinity_upper:Fraction
    exact_tv:Fraction


def certified_finite_affinity(n:int,lam:Fraction,
                              *,digits:int=22)->HellingerReceipt:
    lam=_valid(n,lam)
    if not isinstance(digits,int) or not 8<=digits<=40:
        raise ValueError("choose 8..40 exact decimal digits")
    p0,p1=exact_histogram_laws(n,lam)
    if p0==p1:
        # Exact full-erasure symmetry, so affinity is exactly one.
        return HellingerReceipt(n,lam,comb(n+3,3)*4,0,digits,
                                Fraction(1),Fraction(1),
                                Fraction(0))
    scale=10**digits
    lo=hi=0
    terms=0
    for key in p0.keys()&p1.keys():
        product=p0[key]*p1[key]
        lower,upper=_sqrt_interval(product,scale)
        lo+=lower
        hi+=upper
        terms+=1
    lower=Fraction(lo,scale)
    upper=min(Fraction(1),Fraction(hi,scale))
    exact_tv=exact_histogram_tv(n,lam)
    if not (0<=lower<=upper<1):
        raise AssertionError("affinity certificate must be a strict contraction")
    if exact_tv!=graded_total_variation(n,lam):
        raise AssertionError("BM-39 family TV regression failed")
    if upper-lower>Fraction(terms,scale):
        raise AssertionError("roundoff certificate invalid")
    return HellingerReceipt(n,lam,comb(n+3,3)*4,terms,digits,
                            lower,upper,exact_tv)


def _asymptotic_joint(h:int,lam:Fraction)->dict:
    """Infinite-n directing-law oracle, grouped by distinct ordinary R."""
    out={}
    for weight,ordinary,special in _branches(h,lam):
        for z,p in enumerate(special):
            if p:
                key=(ordinary,z)
                out[key]=out.get(key,Fraction())+weight*p
    return {key:p for key,p in out.items() if p}


def certified_asymptotic_affinity(lam:Fraction,*,digits:int=22)->tuple:
    lam=_valid(1,lam)
    if not isinstance(digits,int) or not 8<=digits<=40:
        raise ValueError("precision 8..40 required")
    p0,p1=_asymptotic_joint(0,lam),_asymptotic_joint(1,lam)
    if p0==p1:
        return Fraction(1),Fraction(1)
    scale=10**digits
    a=b=0
    for k in p0.keys()&p1.keys():
        lo,hi=_sqrt_interval(p0[k]*p1[k],scale)
        a+=lo
        b+=hi
    return Fraction(a,scale),min(Fraction(1),Fraction(b,scale))


def iid_bayes_error_upper(affinity_upper:Fraction,m:int)->Fraction:
    if not isinstance(m,int) or m<0:
        raise ValueError("nonnegative number of independent episodes required")
    b=Fraction(affinity_upper)
    if not 0<=b<=1:
        raise ValueError("affinity upper bound in [0,1] required")
    return b**m/2


def episodes_for_risk_upper(
    affinity_upper:Fraction,
    target:Fraction=Fraction(1,20)
)->int|None:
    b=Fraction(affinity_upper)
    target=Fraction(target)
    if not 0<b<=1 or not 0<target<Fraction(1,2):
        raise ValueError("positive affinity and subhalf error target required")
    if b==1:
        return None
    # Monotone exact rational comparison, with logarithmic search.
    lo,hi=0,1
    while iid_bayes_error_upper(b,hi)>target:
        hi*=2
    while lo+1<hi:
        mid=(lo+hi)//2
        if iid_bayes_error_upper(b,mid)<=target:
            hi=mid
        else:
            lo=mid
    return hi


def theorem_receipt(n:int=25,lam:Fraction=Fraction(1,2),
                    *,digits:int=22)->dict:
    r=certified_finite_affinity(n,lam,digits=digits)
    alo,ahi=certified_asymptotic_affinity(lam,digits=digits)
    if not (r.affinity_lower>=alo and r.affinity_upper>=alo):
        raise AssertionError("finite-n affinity below its infinite-data limit")
    return {
        "n":n,
        "lambda":str(lam),
        "histogram_states":r.histogram_states,
        "affinity_rational_lower":str(r.affinity_lower),
        "affinity_rational_upper":str(r.affinity_upper),
        "affinity_interval_width":str(r.affinity_upper-r.affinity_lower),
        "TV_exact":str(r.exact_tv),
        "infinite_affinity_lower":str(alo),
        "infinite_affinity_upper":str(ahi),
        "independent_episodes_sufficient_for_Bayes_error_le_1_over_3":
            episodes_for_risk_upper(r.affinity_upper,Fraction(1,3)),
        "independent_episodes_sufficient_for_Bayes_error_le_0_05":
            episodes_for_risk_upper(r.affinity_upper,Fraction(1,20)),
        "fresh_iid_episode_requirement":True,
        "history_adaptive_attacker_guarantee":False,
    }
