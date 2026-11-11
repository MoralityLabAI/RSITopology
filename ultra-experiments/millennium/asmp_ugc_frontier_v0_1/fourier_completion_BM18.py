"""BM-18: universal Fourier-completion noise and exact radial Krawtchouk LP.

For a graph with m observed Boolean edge indicators, let eta_d be the
least per-edge mask marginal needed to equalize the flat/other laws on all
Walsh subsets of size <=d, under the BM-17 current-sample-independent,
hypothesis-aware correlated XOR readout model. Compose either attaining
mask with the SAME independent, hypothesis-blind noise R satisfying
  E_R[chi_S]=0 for every |S|>d.
All lower-degree equalities are preserved, and every higher-degree
difference vanishes. If R is exchangeable with flip marginal r<=1/2,

 eta_m <= eta_d + r*(1-2*eta_d).

The uniform fair-noise-on-a-random-(m-d)-subset construction has
 r=(m-d)/(2m). The cheapest UNIVERSAL high-degree annihilator is itself
an exact polynomial-size rational Krawtchouk LP with m+1 orbit weights:
  min sum_t t*w_t/m,
  sum_t w_t=1, w_t>=0,
  sum_t K_s(t)/C(m,t)*w_t=0 for s>d.
The LP has m+1 variables, m-d+1 equalities and a matching explicit dual.

Exact universal optima: r(m,m-1)=1/(2m) and
r(m,m-2)=1/m (for m>=2). Small-degree fixtures give improvements:
r(5,2)=1/4, r(6,3)=5/24 and r(8,4)=5/26.

These completion bounds do NOT imply a polynomial-size graph-specific
Fourier truncation for fixed treewidth: d may need to be near m and
a graph-specific truncated LP may still have exponential size.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb

try:
    from .generic_fourier_erasure_BM17 import (
        Pair, Primal, census, signed_walsh, queried_subsets,
    )
except ImportError:
    from generic_fourier_erasure_BM17 import (
        Pair, Primal, census, signed_walsh, queried_subsets,
    )


def validate(m:int,d:int)->None:
    if not isinstance(m,int) or m<1 or not isinstance(d,int) or not 0<=d<=m:
        raise ValueError("m>=1 and Fourier degree d in 0..m required")


def krawtchouk_ratio(m:int,s:int,t:int)->Fraction:
    """Walsh parity average on |S|=s under uniform mask Hamming weight t."""
    if m<1 or not 0<=s<=m or not 0<=t<=m:
        raise ValueError("invalid Krawtchouk indices")
    return Fraction(sum(
        (-1)**j*comb(s,j)*comb(m-s,t-j)
        for j in range(max(0,t-(m-s)),min(t,s)+1)
    ),comb(m,t))


@dataclass(frozen=True)
class RadialLP:
    m:int
    d:int
    equalities:tuple[tuple[Fraction,...],...]
    rhs:tuple[Fraction,...]
    objective:tuple[Fraction,...]

    @property
    def variables(self)->int:
        return self.m+1

    @property
    def rows(self)->int:
        return self.m-self.d+1


def radial_lp(m:int,d:int)->RadialLP:
    """Solver-agnostic exact (m+1)-variable LP on Hamming weight orbits."""
    validate(m,d)
    eq=(tuple(Fraction(1) for _ in range(m+1)),)+tuple(
        tuple(krawtchouk_ratio(m,s,t) for t in range(m+1))
        for s in range(d+1,m+1)
    )
    return RadialLP(m,d,eq,(Fraction(1),)+(Fraction(0),)*(m-d),
                    tuple(Fraction(t,m) for t in range(m+1)))


def _radial_weights(m:int,w:tuple[Fraction,...])->tuple[Fraction,...]:
    if len(w)!=m+1:
        raise ValueError("radial mass vector length must be m+1")
    converted=tuple(Fraction(x) for x in w)
    if any(x<0 for x in converted) or sum(converted)!=1:
        raise ValueError("radial masses must be nonnegative and normalized")
    return converted


def check_radial_primal(m:int,d:int,w:tuple[Fraction,...])->Fraction:
    """Exact feasible universal annihilator and its per-bit flip cost."""
    lp=radial_lp(m,d)
    w=_radial_weights(m,w)
    if any(sum((a*b for a,b in zip(row,w)),Fraction(0))!=rhs
           for row,rhs in zip(lp.equalities,lp.rhs)):
        raise AssertionError("high-degree Walsh annihilation failed")
    return sum((a*b for a,b in zip(lp.objective,w)),Fraction(0))


def check_radial_dual(m:int,d:int,y:tuple[Fraction,...])->Fraction:
    """Universal lower certificate: y0 + sum_{s>d} ys*Phi_s(t) <= t/m."""
    lp=radial_lp(m,d)
    if len(y)!=lp.rows:
        raise ValueError("dual must contain normalization and each high degree")
    y=tuple(Fraction(v) for v in y)
    for t in range(m+1):
        lower=sum((yi*row[t] for yi,row in zip(y,lp.equalities)),Fraction(0))
        if lower>lp.objective[t]:
            raise AssertionError(f"invalid radial dual at mask weight {t}")
    return y[0]


def fair_hitting_noise(m:int,d:int)->tuple[Fraction,...]:
    """Draw H uniformly of size m-d, then independently fair-flip bits in H."""
    validate(m,d)
    k=m-d
    weights=[Fraction(0)]*(m+1)
    for t in range(k+1):
        weights[t]=Fraction(comb(k,t),2**k)
    assert sum(weights)==1
    return tuple(weights)


# Smaller exact primal and dual witnesses, discovered numerically then
# reconstructed to rational entries and verified independently in CI.
# DUAL entries are (normalization, degrees d+1,...,m).
SMALL_SHARP={
    (5,2):(
        {0:Fraction(3,16),1:Fraction(15,32),
         2:Fraction(5,16),5:Fraction(1,32)},
        (Fraction(1,4),Fraction(-1,2),Fraction(1,4),Fraction(0)),
    ),
    (6,3):(
        {0:Fraction(3,16),1:Fraction(15,32),
         2:Fraction(5,16),5:Fraction(1,32)},
        (Fraction(5,24),Fraction(-5,8),
         Fraction(1,2),Fraction(-1,12)),
    ),
    (7,4):(
        {0:Fraction(5,24),1:Fraction(35,72),
         2:Fraction(7,24),7:Fraction(1,72)},
        (Fraction(1,6),Fraction(-1,2),Fraction(1,3),Fraction(0)),
    ),
    (8,4):(
        {0:Fraction(63,416),1:Fraction(45,104),
         2:Fraction(35,104),5:Fraction(7,104),
         8:Fraction(5,416)},
        (Fraction(5,26),Fraction(-21,26),Fraction(7,13),
         Fraction(4,13),Fraction(-3,13)),
    ),
}


def sharp_radial_fixture(m:int,d:int):
    """Return rational matching primal/dual for analytic or tested small cases.

    Unsupported generic degrees still have an explicit valid UPPER bound
    from fair_hitting_noise and the exact radial LP for an external solver.
    """
    validate(m,d)
    if d==m:
        return (fair_hitting_noise(m,d),(Fraction(0),))
    if d==0:
        y=[Fraction(1,2),Fraction(-1,2)]
        y.extend([Fraction(0)]*(m-1))
        return fair_hitting_noise(m,d),tuple(y)
    if d==m-1:
        return (fair_hitting_noise(m,d),
                (Fraction(1,2*m),Fraction(-1,2*m)))
    if m>=2 and d==m-2:
        return (fair_hitting_noise(m,d),(
            Fraction(1,m),Fraction(-1,2),Fraction(m-2,2*m)
        ))
    if (m,d) in SMALL_SHARP:
        masses,dual=SMALL_SHARP[(m,d)]
        return tuple(masses.get(t,Fraction(0)) for t in range(m+1)),dual
    raise KeyError("exact radial optimum not bundled; use fair_hitting_noise upper bound")


def verify_sharp_radial(m:int,d:int)->Fraction:
    primal,dual=sharp_radial_fixture(m,d)
    upper=check_radial_primal(m,d,primal)
    lower=check_radial_dual(m,d,dual)
    if upper!=lower:
        raise AssertionError("radial primal and dual fail to match")
    return upper


def radial_mask_law(m:int,w:tuple[Fraction,...])->dict[int,Fraction]:
    """Uniform distribution within each Hamming weight orbit; exponential."""
    if m>12:
        raise ValueError("explicit masks restricted to at most 12 edges")
    w=_radial_weights(m,w)
    return {
        mask:w[mask.bit_count()]/comb(m,mask.bit_count())
        for mask in range(1<<m)
        if w[mask.bit_count()]
    }


def mask_marginals(m:int,law:dict[int,Fraction])->tuple[Fraction,...]:
    if not law or any(not 0<=mask<(1<<m) or value<0
                      for mask,value in law.items()) or sum(law.values())!=1:
        raise ValueError("normalized nonnegative complete Boolean mask law needed")
    return tuple(sum((v for mask,v in law.items() if mask&(1<<i)),
                     Fraction(0)) for i in range(m))


def xor_convolve_masks(m:int,a:dict[int,Fraction],b:dict[int,Fraction]
                      )->dict[int,Fraction]:
    mask_marginals(m,a)
    mask_marginals(m,b)
    output:dict[int,Fraction]={}
    for x,v in a.items():
        for y,w in b.items():
            index=x^y
            output[index]=output.get(index,Fraction(0))+v*w
    return {x:v for x,v in output.items() if v}


def convolve_clean(m:int,clean:tuple[int,...],mask:dict[int,Fraction]
                  )->tuple[Fraction,...]:
    if len(clean)!=(1<<m) or sum(clean)<=0 or any(c<0 for c in clean):
        raise ValueError("clean probability table dimension/normalizer")
    mask_marginals(m,mask)
    return tuple(
        sum((Fraction(clean[out^noise],sum(clean))*p
             for noise,p in mask.items()),Fraction(0))
        for out in range(1<<m)
    )


def postprocess_primal(pair:Pair,degree:int,witness:Primal,
                       radial:tuple[Fraction,...]):
    """Complete the degree-d primal; verify full output equality exactly.

    Returns the actual maximum mask marginal and the certified universal
    bound eta_d+r(1-2 eta_d). This is purely a proof/postprocessing operation.
    """
    try:
        from .generic_fourier_erasure_BM17 import check_primal
    except ImportError:
        from generic_fourier_erasure_BM17 import check_primal
    if pair.m>12:
        raise ValueError("explicit postprocessor limited to <=12 edges")
    check_primal(pair,degree,witness)
    r=check_radial_primal(pair.m,degree,radial)
    if r>Fraction(1,2):
        raise ValueError("postprocessor must have bit error <=1/2")
    eta=Fraction(witness.eta)
    if eta>Fraction(1,2):
        raise ValueError("input cap must lie in [0,1/2]")
    common=radial_mask_law(pair.m,radial)
    masks=[]
    for raw in (witness.q0,witness.q1):
        original={j:Fraction(v,witness.denominator)
                  for j,v in raw.items() if v}
        masks.append(xor_convolve_masks(pair.m,original,common))
    c0,c1=census(pair.flat),census(pair.other)
    if convolve_clean(pair.m,c0,masks[0])!=convolve_clean(pair.m,c1,masks[1]):
        raise AssertionError("completed mask pair fails complete distribution equality")
    actual=max(mask_marginals(pair.m,masks[0])+mask_marginals(pair.m,masks[1]))
    bound=eta+r*(1-2*eta)
    if actual>bound:
        raise AssertionError("postprocessed mask exceeds theorem bound")
    return actual,bound


def completion_bound(m:int,d:int,eta_d:Fraction,
                     radial:tuple[Fraction,...]|None=None)->Fraction:
    """Certified additive completion guarantee for any finite gain graph."""
    validate(m,d)
    eta=Fraction(eta_d)
    if not 0<=eta<=Fraction(1,2):
        raise ValueError("truncated optimum is assumed in [0,1/2]")
    if radial is None:
        radial=fair_hitting_noise(m,d)
    r=check_radial_primal(m,d,radial)
    if r>Fraction(1,2):
        raise ValueError("invalid completion mask rate")
    return eta+r*(1-2*eta)


def manifest():
    cases=[(5,2),(6,3),(7,4),(8,4)]
    return {
        "universal_completion":"eta_m <= eta_d + r*(1-2*eta_d)",
        "closed_m_minus_one":"r=1/(2m)",
        "closed_m_minus_two":"r=1/m",
        "improved_fixtures":[{
            "m":m,"d":d,
            "optimum":str(verify_sharp_radial(m,d)),
            "uniform_hitting_cost":str(check_radial_primal(
                m,d,fair_hitting_noise(m,d)
            ))
        } for m,d in cases],
        "mask_lp_variables":"m+1",
        "mask_lp_equalities":"m-d+1",
        "external_lp_solver_required_for_verification":False,
    }
