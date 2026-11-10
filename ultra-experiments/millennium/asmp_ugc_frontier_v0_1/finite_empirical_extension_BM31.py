"""BM-31: quantitative finite exchangeability with an exceptional readout pair.

Work in the registered BM-24/BM-29 q8 two-edge-path mask channel.
Given n ordinary two-bit masks and one distinguished exceptional pair,
average any mask law under (S_2 wr S_n) x S_2. An orbit is represented
by counts (c0,c1,c2) of ordinary pairs with 0,1,2 flipped bits and the
EXACT two-bit exceptional mask z in {0,1,2,3}.

Conditioned on a histogram and exceptional z, the original first k
ordinary masks sample c0/c1/c2 WITHOUT replacement, using a fair
orientation for one-flip pairs. Replace this by WITH-replacement
sampling from empirical pair law
  lambda_c=(c0/n,c1/(2n),c1/(2n),c2/n).
Draw z first from its histogram-conditional law, retaining the
world-specific exceptional coupling. The latter defines a genuine
infinite exchangeable sequence of ordinary mask pairs with distinguished
exceptional noise, and preserves ALL individual bit marginals.

The exact coupling error in total variation on first k pairs + z is
  delta(n,k)=1-(n)_k/n^k <= k(k-1)/(2n),   1<=k<=n.
The statement is independent of hidden hypothesis and graph alphabet.

If Q0,Q1 are a FULL equalizing pair, strict positivity of all common
q8 ordinary and ordinary+one-exceptional clean Walsh coefficients
(BM-29) makes their empirical histogram distributions IDENTICAL, and
their histogram-conditional individual exceptional-bit marginals
identical. The two infinitely exchangeable approximants consequently
share the same empirical directing law and one-special-bit rigidity.

The approximate k+exceptional OUTPUT laws differ in TV by <=2delta,
by contraction of TV under XOR convolution. Each Walsh discrepancy is
bounded in absolute value by <=4delta. This is a quantitative finite
WINDOW approximation, not a quantitative rate for eta_n -> 5/52.
The constants follow from coupling uniformly sampled distinct indices
to iid indices; no finite de Finetti theorem is presumed as an oracle.

Standard-library Fraction code supplies two independent exact sampling
calculations, complete mask symmetrization, and hostile finite-only tests.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb, factorial

try:
    from .replication_uniform_upper_BM27 import (
        exact_clean_law, xor_convolve,
    )
except ImportError:
    from replication_uniform_upper_BM27 import (
        exact_clean_law, xor_convolve,
    )


Histogram=tuple[int,int,int]
JointHistogram=tuple[Histogram,int]


def _validate(n:int,k:int|None=None)->None:
    if not isinstance(n,int) or n<1:
        raise ValueError("n must be a positive ordinary-path count")
    if k is not None and (not isinstance(k,int) or not 1<=k<=n):
        raise ValueError("projection must select 1<=k<=n ordinary paths")


def collision_bound(n:int,k:int)->Fraction:
    """Exact collision coupling probability, without asymptotic rounding."""
    _validate(n,k)
    distinct=Fraction(1)
    for j in range(k):
        distinct*=Fraction(n-j,n)
    return 1-distinct


def window_bounds(n:int,k:int)->dict[str,Fraction]:
    """Explicit TV and Walsh guarantees for ANY finite legal equalizer."""
    e=collision_bound(n,k)
    assert e<=Fraction(k*(k-1),2*n)
    return {
        "mask_tv_each_world":e,
        "output_tv_between_worlds":min(Fraction(1),2*e),
        "max_abs_fourier_discrepancy":min(Fraction(2),4*e),
        "union_collision_upper":Fraction(k*(k-1),2*n),
    }


def mask_histogram(n:int,mask:int)->Histogram:
    """Ordinary path types: 0=no flip, 1=one flip, 2=two flips."""
    _validate(n)
    if not isinstance(mask,int) or not 0<=mask<1<<(2*n+2):
        raise ValueError("full mask outside n ordinary pairs + special pair")
    counts=[0,0,0]
    for j in range(n):
        t=((mask>>(2*j))&3).bit_count()
        counts[t]+=1
    return tuple(counts)


def _check_mask_law(n:int,law:dict[int,Fraction])->dict[int,Fraction]:
    _validate(n)
    if not law or any(
        not isinstance(mask,int) or not 0<=mask<1<<(2*n+2)
        or Fraction(weight)<0 for mask,weight in law.items()
    ):
        raise ValueError("mask law must have valid nonnegative atoms")
    converted={mask:Fraction(weight) for mask,weight in law.items()
               if weight}
    if sum(converted.values(),Fraction(0))!=1:
        raise ValueError("mask law must be normalized")
    return converted


def empirical_joint_law(n:int,law:dict[int,Fraction],
                        *,swap_exceptional:bool=True
                       )->dict[JointHistogram,Fraction]:
    """Orbit-average Q, returning mass on (ordinary type counts, special z).

    Full ordinary path permutations and independent within-path swaps
    are implicit in the histogram. Optional special pair swap makes
    the exceptional two bits exchangeable under the registered clean law.
    """
    law=_check_mask_law(n,law)
    out={}
    for mask,weight in law.items():
        hist=mask_histogram(n,mask)
        special=(mask>>(2*n))&3
        atoms=((special,Fraction(1)),)
        if swap_exceptional and special in (1,2):
            atoms=((1,Fraction(1,2)),(2,Fraction(1,2)))
        for s,p in atoms:
            key=(hist,s)
            out[key]=out.get(key,Fraction(0))+weight*p
    return {key:weight for key,weight in out.items() if weight}


def histogram_multinomial(n:int,hist:Histogram)->int:
    _validate(n)
    if len(hist)!=3 or any(not isinstance(x,int) or x<0 for x in hist) or (
        sum(hist)!=n
    ):
        raise ValueError("ordinary type histogram must be nonnegative and sum n")
    return factorial(n)//(factorial(hist[0])*factorial(hist[1])*
                          factorial(hist[2]))


def expand_empirical_joint_law(
    n:int,joint:dict[JointHistogram,Fraction],*,max_bits:int=12
)->dict[int,Fraction]:
    """Independently reconstruct the fully symmetrized n-pair mask law."""
    _validate(n)
    if 2*n+2>max_bits:
        raise ValueError("full orbit expansion exceeds declared bit budget")
    out={}
    for mask in range(1<<(2*n+2)):
        hist=mask_histogram(n,mask)
        s=(mask>>(2*n))&3
        weight=joint.get((hist,s),Fraction(0))
        if weight:
            ordinary_orbit_size=histogram_multinomial(n,hist)*(1<<hist[1])
            out[mask]=weight/ordinary_orbit_size
    if sum(out.values(),Fraction(0))!=1:
        raise AssertionError("joint histogram expansion is not normalized")
    return out


def directing_law(n:int,joint:dict[JointHistogram,Fraction]
                 )->dict[Histogram,Fraction]:
    """Probability distribution on EMPIRICAL ordinary mask pair laws."""
    _validate(n)
    out={}
    for (hist,special),weight in joint.items():
        if not 0<=special<=3:
            raise ValueError("invalid exceptional pair value")
        histogram_multinomial(n,hist)
        if Fraction(weight)<0:
            raise ValueError("negative directing mass")
        out[hist]=out.get(hist,Fraction(0))+Fraction(weight)
    if sum(out.values(),Fraction(0))!=1:
        raise ValueError("directing empirical distribution not normalized")
    return out


def empirical_pair_law(n:int,hist:Histogram)->tuple[Fraction,...]:
    """IID replacement pair law on 00,10,01,11, with one-flip orientation."""
    histogram_multinomial(n,hist)
    return (
        Fraction(hist[0],n),Fraction(hist[1],2*n),
        Fraction(hist[1],2*n),Fraction(hist[2],n)
    )


def _choose_pairs(n:int,k:int,joint:dict[JointHistogram,Fraction],
                  *,replacement:bool)->dict[int,Fraction]:
    """Exact count DP, leaving the exceptional pair value untouched."""
    _validate(n,k)
    out={}
    for (hist,special),initial_mass in joint.items():
        histogram_multinomial(n,hist)
        if not isinstance(special,int) or not 0<=special<=3 or (
            Fraction(initial_mass)<0
        ):
            raise ValueError("bad joint empirical mask atom")
        states={(hist if not replacement else (0,0,0),0):Fraction(initial_mass)}
        for j in range(k):
            nxt={}
            for (remaining,prefix),weight in states.items():
                available=hist if replacement else remaining
                denom=n if replacement else n-j
                for t,count in enumerate(available):
                    if not count:
                        continue
                    rest=(remaining if replacement else
                          tuple(v-int(t==i) for i,v in enumerate(remaining)))
                    options=((0,Fraction(1)),) if t==0 else (
                        ((1,Fraction(1,2)),(2,Fraction(1,2))) if t==1 else
                        ((3,Fraction(1)),)
                    )
                    for bits,orientation in options:
                        key=(rest,prefix|(bits<<(2*j)))
                        nxt[key]=nxt.get(key,Fraction(0))+(
                            weight*Fraction(count,denom)*orientation
                        )
            states=nxt
        for (_,prefix),weight in states.items():
            mask=prefix|(special<<(2*k))
            out[mask]=out.get(mask,Fraction(0))+weight
    if sum(out.values(),Fraction(0))!=1:
        raise AssertionError("finite or infinite empirical projection not normalized")
    return {key:value for key,value in out.items() if value}


def without_replacement_window(n:int,k:int,joint)->dict[int,Fraction]:
    """True k-path projection of the symmetrized n-mask law."""
    return _choose_pairs(n,k,joint,replacement=False)


def with_replacement_window(n:int,k:int,joint)->dict[int,Fraction]:
    """Projection of a genuine, infinitely exchangeable mask law."""
    return _choose_pairs(n,k,joint,replacement=True)


def total_variation(a:dict[int,Fraction],b:dict[int,Fraction])->Fraction:
    if sum(a.values(),Fraction(0))!=1 or sum(b.values(),Fraction(0))!=1:
        raise ValueError("two normalized laws needed")
    return sum((abs(a.get(s,0)-b.get(s,0))
                for s in a.keys()|b.keys()),Fraction(0))/2


def independent_project_full(n:int,k:int,
                             law:dict[int,Fraction])->dict[int,Fraction]:
    """Reference projection from the 2n+2 original Boolean mask bits."""
    _validate(n,k)
    law=_check_mask_law(n,law)
    keep=(1<<(2*k))-1
    out={}
    for mask,weight in law.items():
        s=(mask&keep)|(((mask>>(2*n))&3)<<(2*k))
        out[s]=out.get(s,Fraction(0))+weight
    return out


def exceptional_singlebit_marginal(n:int,joint:dict,
                                   special_bit:int)->dict[tuple,Fraction]:
    """Measure of (entire ordinary histogram, one exceptional noise bit)."""
    _validate(n)
    if special_bit not in (0,1):
        raise ValueError("exceptional bit index must be 0 or 1")
    out={}
    for (hist,special),weight in joint.items():
        key=(hist,(special>>special_bit)&1)
        out[key]=out.get(key,Fraction(0))+Fraction(weight)
    return out


@dataclass(frozen=True)
class FiniteWindowReceipt:
    n:int
    k:int
    collision_upper:Fraction
    actual_mask_tv_world0:Fraction
    actual_mask_tv_world1:Fraction
    approximate_output_tv:Fraction
    maximum_walsh_gap:Fraction
    shared_directing_mu:bool
    shared_exceptional_singlebits:bool
    true_output_laws_equal:bool


def certify_finite_window(
    n:int,k:int,mask0:dict[int,Fraction],mask1:dict[int,Fraction],
    *,verify_clean:bool=True
)->FiniteWindowReceipt:
    """Certify all math contracts for an EXACT q8 n-path equalizing pair.

    Only intended for small n: explicit original Q0,Q1 and 2^(2n+2)
    full outputs are needed. Large-n theorem uses collision_bound
    symbolically, without attempting exponential enumeration.
    """
    _validate(n,k)
    if n>5:
        raise ValueError("explicit finite certification limited to n<=5")
    j0=empirical_joint_law(n,mask0)
    j1=empirical_joint_law(n,mask1)
    a=expand_empirical_joint_law(n,j0)
    b=expand_empirical_joint_law(n,j1)
    if verify_clean:
        from0=exact_clean_law(n,0)
        from1=exact_clean_law(n,1)
        if xor_convolve(from0,a)!=xor_convolve(from1,b):
            raise AssertionError("supplied masks do not equalize q8 complete laws")
    mu_same=directing_law(n,j0)==directing_law(n,j1)
    bits_same=all(
        exceptional_singlebit_marginal(n,j0,i)==
        exceptional_singlebit_marginal(n,j1,i)
        for i in (0,1)
    )
    if not mu_same or not bits_same:
        raise AssertionError("BM-29 finite noise-marginal rigidity violated")
    true0=without_replacement_window(n,k,j0)
    true1=without_replacement_window(n,k,j1)
    fake0=with_replacement_window(n,k,j0)
    fake1=with_replacement_window(n,k,j1)
    # An independent projected-mask oracle: drop the unused n-k pairs.
    if true0!=independent_project_full(n,k,a) or (
        true1!=independent_project_full(n,k,b)
    ):
        raise AssertionError("without-replacement DP disagrees with direct mask projection")
    e=collision_bound(n,k)
    tv0=total_variation(true0,fake0)
    tv1=total_variation(true1,fake1)
    if max(tv0,tv1)>e:
        raise AssertionError("Diaconis-Freedman empirical coupling bound violated")
    clean0,clean1=exact_clean_law(k,0),exact_clean_law(k,1)
    true_out0=xor_convolve(clean0,true0)
    true_out1=xor_convolve(clean1,true1)
    if verify_clean and true_out0!=true_out1:
        raise AssertionError("projected original output equalities lost")
    fake_out0=xor_convolve(clean0,fake0)
    fake_out1=xor_convolve(clean1,fake1)
    tv=total_variation(fake_out0,fake_out1)
    if tv>2*e:
        raise AssertionError("approximate infinite output TV bound violated")
    gaps=tuple(abs(sum((
        (fake_out0.get(x,0)-fake_out1.get(x,0))*
        (-1 if (x&S).bit_count()%2 else 1)
        for x in range(1<<(2*k+2))
    ),Fraction(0))) for S in range(1,1<<(2*k+2)))
    worst=max(gaps,default=Fraction(0))
    if worst>4*e:
        raise AssertionError("approximate infinite Fourier discrepancy bound violated")
    return FiniteWindowReceipt(n,k,e,tv0,tv1,tv,worst,
                               mu_same,bits_same,true_out0==true_out1)


def growing_window_bound(n:int,*,power:int=3)->dict[str,object]:
    """A growing k with explicit vanishing collision error.

    k=floor(n^(1/3)) by integer binary search; for large n,
    delta<=k(k-1)/(2n)=O(n^(-1/3)).
    """
    if not isinstance(n,int) or n<1 or power<2:
        raise ValueError("positive n and integer exponent >=2 required")
    lo,hi=1,n
    while lo<hi:
        mid=(lo+hi+1)//2
        if mid**power<=n:
            lo=mid
        else:
            hi=mid-1
    k=max(1,lo)
    return {
        "n":n,"k":k,"k_exponent":power,
        "exact_collision_bound":collision_bound(n,k),
        "elementary_upper":Fraction(k*(k-1),2*n),
        "ordinary_paths_grow":True,
        "explicit_threshold_convergence_rate_claimed":False,
    }
