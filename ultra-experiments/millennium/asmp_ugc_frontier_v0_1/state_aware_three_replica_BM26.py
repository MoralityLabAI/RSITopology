"""BM-26: exact q8 erasure for THREE replicated ordinary length-2 paths.

A fresh-uniform-label K=F2^3 gain graph has n=3 ordinary two-edge u-v
paths with gain zero in both worlds and one exceptional two-edge path
with gain zero/any nonzero gamma. The full 8-bit Boolean satisfaction
readout is subject to hypothesis-aware, within-episode correlated XOR
masks independent of the current clean observation, each coordinate
having flip probability <=eta.

Exact optimum:
    eta_sym(n=3, q=8, L=2) = 751225 / 13956626
                         = 0.0538256882429894...

A rational upper certificate uses 30 path-histogram mask classes in
each world, of which 16 have positive weight per world, normalized
by denominator 27913252. An independent rational lower certificate
uses 29 nonempty Fourier histogram coefficients, normalized by
3979313205120, with 4 signed marginal multipliers normalized by
6978313. All 60 quotient-mask dual inequalities are exact.

The full eight-bit expansion verifies 256 complete output probabilities
and 512 full-mask dual inequalities independently through BM-17. The
29 orbit characters expand into 255 original Walsh characters. The
dual can be lifted to arbitrary n>=3 using only the first three ordinary
paths and the exceptional path. The n>=3 upper bound is BM-24's 1/8
common-channel witness. No asymptotic limit is claimed.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import lcm

try:
    from .repeated_gain_erasure_BM24 import gain_family, exact_common_cap
    from .repeated_theta_orbits_BM24 import (
        type_histograms, build_repeated_lp, check_repeated_lp_matrix,
    )
    from .generic_fourier_erasure_BM17 import Pair, Primal, Dual, certify
except ImportError:
    from repeated_gain_erasure_BM24 import gain_family, exact_common_cap
    from repeated_theta_orbits_BM24 import (
        type_histograms, build_repeated_lp, check_repeated_lp_matrix,
    )
    from generic_fourier_erasure_BM17 import Pair, Primal, Dual, certify


EXACT_CAP = Fraction(751225, 13956626)
MASK_DENOMINATOR = 27913252
DUAL_DENOMINATOR = 3979313205120
DUAL_MARGINAL_DENOMINATOR = 6978313

# Entries indexed by (ordinary path histogram (c0,c1,c2), special
# mask Hamming weight t=0/1/2). The ordinary histograms are enumerated
# in the order (a,b,n-a-b) with increasing a then b, and t increases
# fastest. They encode TOTAL mass on each orbit, not per-mask mass.
FLAT_ORBIT_NUMERATORS = (
    1218,0,1218, 0,19934,0, 25252,0,25252,
    0,40760,0, 0,40234,0, 11334,0,11334,
    57800,0,57800, 0,722096,0,
    6016165,0,655621, 19547808,679426,0,
)
FRUSTRATED_ORBIT_NUMERATORS = (
    0,2436,0, 9967,0,9967, 0,50504,0,
    20380,0,20380, 20117,0,20117, 0,22668,0,
    0,115600,0, 361048,0,361048,
    5360544,1311242,0, 19887521,0,339713,
)

# Exactly 29 nonzero Walsh-orbit multipliers: all nonempty signature
# classes in this n=3 representation. The zero (trivial) Fourier
# character sits at index 27, whose coefficient is 0.
ORBIT_DUAL_WALSH_NUMERATORS = (
    -42385425984,-710646951168,1709333176320,
    -29190447360,2768754355200,-5762893086720,
    118308101120,-2707226480640,7419944632320,
    60436907520,451204413440,-1381669273600,
    -132650460000,2699535496320,-4689659842560,
    -149465184000,676806620160,-276488847360,
    -86594713920,507604965120,-1219545169920,
    69922741680,126901241280,-293997496320,
    -508322568600,-571055585760,995301457920,
    0,499673637540,471875120640,
)
DUAL_NORMALIZATION_NUMERATORS = (-117251951355,331441223355)
# h=0 ordinary, h=0 exceptional, h=1 ordinary, h=1 exceptional.
DUAL_MARGINAL_NUMERATORS = (-2972592,0,0,-4005721)


def model(gain:int=1):
    return gain_family(3,2,q=8,gain=gain)


def _signature(hist:tuple[int,int,int],t:int)->tuple:
    return hist,tuple(int(j==t) for j in range(3))


def _indexed_signatures()->tuple:
    return tuple(
        _signature(h,t)
        for h in type_histograms(3,2) for t in range(3)
    )


def orbit_masks()->tuple[dict,dict]:
    sigs=_indexed_signatures()
    if len(sigs)!=30:
        raise AssertionError("BM-24 histogram ordering changed")
    return tuple(
        {sig:Fraction(w,MASK_DENOMINATOR)
         for sig,w in zip(sigs,weights) if w}
        for weights in (
            FLAT_ORBIT_NUMERATORS,FRUSTRATED_ORBIT_NUMERATORS
        )
    )


def orbit_dual():
    sigs=_indexed_signatures()
    coeff={
        sig:Fraction(v,DUAL_DENOMINATOR)
        for sig,v in zip(sigs,ORBIT_DUAL_WALSH_NUMERATORS) if v
    }
    norm=tuple(Fraction(v,DUAL_DENOMINATOR)
               for v in DUAL_NORMALIZATION_NUMERATORS)
    marg=tuple(
        tuple(Fraction(v,DUAL_MARGINAL_DENOMINATOR)
              for v in DUAL_MARGINAL_NUMERATORS[2*h:2*h+2])
        for h in (0,1)
    )
    return norm,coeff,marg


def verify_exact_orbit_certificate(gain:int=1)->Fraction:
    net=model(gain)
    a,b=orbit_masks()
    norm,coeff,marg=orbit_dual()
    if net.orbit_size!=30 or len(coeff)!=29:
        raise AssertionError("unexpected BM-26 histogram quotient")
    if sum(FLAT_ORBIT_NUMERATORS)!=MASK_DENOMINATOR or (
        sum(FRUSTRATED_ORBIT_NUMERATORS)!=MASK_DENOMINATOR
    ):
        raise AssertionError("invalid registered rational mask masses")
    upper=net.verify_primal(a,b,cap=EXACT_CAP,max_orbits=64)
    lower=net.verify_dual(norm,coeff,marg,max_orbits=64)
    if upper!=lower or upper!=EXACT_CAP:
        raise AssertionError("BM-26 sharp upper/lower mismatch")
    matrix=build_repeated_lp(net,max_orbits=64)
    if (matrix.variables,len(matrix.equalities),
        len(matrix.inequalities))!=(61,31,4):
        raise AssertionError("BM-26 LP matrix dimension mismatch")
    if not check_repeated_lp_matrix(matrix,a,b,EXACT_CAP):
        raise AssertionError("independent LP matrix rejects sharp primal")
    return upper


def full_mask_law(h:int):
    """Expand orbit masses into exact probability of each of 2^8 masks."""
    if h not in (0,1):
        raise ValueError("hypothesis must be 0 or 1")
    net=model()
    masses=orbit_masks()[h]
    out={}
    for mask in range(1<<net.m):
        sig=net.signature(mask)
        weight=masses.get(sig,Fraction(0))
        if weight:
            out[mask]=weight/net.orbit_size_of_signature(sig)
    if sum(out.values(),Fraction(0))!=1:
        raise AssertionError("full expansion lost mask normalization")
    return out


def _to_integer_distribution(law):
    D=lcm(*(v.denominator for v in law.values()))
    return {mask:int(weight*D) for mask,weight in law.items()},D


def full_dual():
    """Lift the rational orbit dual into the full 256-Walsh basis."""
    net=model()
    norm,coeff,marg=orbit_dual()
    weights={}
    for S in range(1,1<<net.m):
        sig=net.signature(S)
        v=coeff.get(sig,Fraction(0))
        if v:
            weights[S]=v/net.orbit_size_of_signature(sig)
    denominator=lcm(*(v.denominator for v in (*norm,*weights.values())))
    z=[]
    for h in range(2):
        for ty,x in zip(net.types,marg[h]):
            z.extend((x/(ty.length*ty.count),)*(ty.length*ty.count))
    marginal_denominator=lcm(*(v.denominator for v in z))
    result=Dual(
        denominator,
        {S:int(v*denominator) for S,v in weights.items()},
        tuple(int(x*denominator) for x in norm),
        marginal_denominator,
        tuple(int(x*marginal_denominator) for x in z),
    )
    if -sum(result.marginal_numerators)!=result.marginal_denominator:
        raise AssertionError("full dual marginal normalization")
    return result


@lru_cache(maxsize=8)
def verify_exact_full_certificate(gain:int=1):
    """Independent BM-17 256-output, 512-dual-mask rational proof."""
    net=model(gain)
    p0,D0=_to_integer_distribution(full_mask_law(0))
    p1,D1=_to_integer_distribution(full_mask_law(1))
    D=lcm(D0,D1)
    witness=Primal(
        D,{x:v*(D//D0) for x,v in p0.items()},
        {x:v*(D//D1) for x,v in p1.items()},EXACT_CAP
    )
    report=certify(
        Pair(net.game(0),net.game(1)),net.m,witness,full_dual()
    )
    if (report.optimum!=EXACT_CAP or not report.full_output_equal or
        report.walsh_terms!=255 or
        report.checked_mask_inequalities!=512):
        raise AssertionError("BM-26 full rational certificate incomplete")
    return report


def _embed(mask:int,n:int)->int:
    if not isinstance(n,int) or n<3 or not 0<=mask<256:
        raise ValueError("eight-bit mask and >=3 ordinary paths needed")
    return (mask&63)|((mask>>6)<<(2*n))


def lifted_full_dual(n:int):
    """Retain first 3 ordinary 2-edge paths and the final exceptional path."""
    if not isinstance(n,int) or n<3:
        raise ValueError("n>=3 ordinary paths required for projection")
    base=full_dual()
    m=2*n+2
    combined=[]
    for h in (0,1):
        z=base.marginal_numerators[h*8:(h+1)*8]
        combined.extend(z[:6]+(0,)*(m-8)+z[6:])
    return Dual(
        base.walsh_denominator,
        {_embed(mask,n):v for mask,v in base.walsh_numerators.items()},
        base.normalization_numerators,
        base.marginal_denominator,tuple(combined)
    )


def verify_symbolic_lift(n:int,*,gain:int=1)->Fraction:
    """Exact n-path lower dual from a fixed 8-bit certificate.

    Each supported Walsh coefficient in the n-path instance is a
    marginal Fourier coefficient of the corresponding n=3 graph.
    The dual ignores all added ordinary paths, so every one of the
    2^(2n+2) inequalities reduces to one of 512 validated 8-bit
    inequalities. Only 255 Fourier projection equalities are checked,
    using BM-24's gain-grouped formula without vertex enumeration.
    """
    net=gain_family(n,2,q=8,gain=gain)
    original=model(gain)
    base=full_dual()
    lifted=lifted_full_dual(n)
    m=net.m
    if len(lifted.marginal_numerators)!=2*m:
        raise AssertionError("incorrect full dual dimension")
    for h in (0,1):
        for S in base.walsh_numerators:
            if original.clean_walsh(h,S)!=net.clean_walsh(
                h,_embed(S,n)
            ):
                raise AssertionError("added paths changed marginal Fourier law")
    if -sum(lifted.marginal_numerators)!=lifted.marginal_denominator:
        raise AssertionError("global dual marginal sum invalid")
    if Fraction(sum(lifted.normalization_numerators),
                lifted.walsh_denominator)!=EXACT_CAP:
        raise AssertionError("global dual lower objective incorrect")
    # Entire mask-space feasibility follows by projection onto the
    # first 3 ordinary paths and the exceptional path. Independently
    # check all 512 original dual constraints once in BM-17.
    if verify_exact_full_certificate(gain).optimum!=EXACT_CAP:
        raise AssertionError("projected base proof not certified")
    return EXACT_CAP


def projection_bounds(n:int)->tuple[Fraction,Fraction]:
    if not isinstance(n,int) or n<3:
        raise ValueError("at least 3 ordinary paths required")
    return EXACT_CAP,exact_common_cap(2)


def theorem_receipt():
    quotient=verify_exact_orbit_certificate()
    full=verify_exact_full_certificate()
    return {
        "alphabet":"F2^3 / q=8",
        "ordinary_paths":3,
        "exceptional_paths":1,
        "path_length":2,
        "vertices":6,"edges":8,
        "exact_hypothesis_aware_cap":str(quotient),
        "previous_n2_exact_cap":"5/118",
        "full_output_patterns_verified":1<<8,
        "full_dual_mask_inequalities_verified":full.checked_mask_inequalities,
        "orbit_classes_per_world":30,
        "nonzero_primal_orbit_masses":(16,16),
        "nonzero_orbit_dual_characters":len(orbit_dual()[1]),
        "nonzero_full_dual_characters":full.walsh_terms,
        "n_ge3_lower":str(projection_bounds(250)[0]),
        "n_ge3_common_upper":str(projection_bounds(250)[1]),
        "n_ge4_sharp_claimed":False,
        "asymptotic_limit_claimed":False,
    }
