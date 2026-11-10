"""BM-30: rigidity and quantitative stability at the q8 limiting optimum.

BM-29 proves lim_n eta_n(8,2)=5/52 with de Finetti directing
measure mu over symmetric ordinary mask pairs and signed exceptional
pair-parity measures nu0,nu1. Here we identify ALL equality cases of
the sharp weighted inequality
    8*C_ordinary + 5*C_special >= 5/4.

Exact equality requires a ONE-PARAMETER continuum of directing laws:
  mu(I)=1-10c,  mu(A)=2c,  mu(B)=8c, 0<=c<=1/10;
  nu0(I,A,B)=(0,c,8c);
  nu1(I,A,B)=(0,2c,7c).
Nonnegative exceptional masks saturate the overlap inequality exactly,
forcing their conditional pair laws:
  I: both worlds E,
  A: flat (I+E)/2, frustrated A,
  B: flat (3I+A)/4, frustrated (3I+B)/4.

Ordinary and exceptional error costs on that frontier are
    C_o=5c/4, C_s=1/4-2c.
Their unique minimax intersection is c=1/13, with eta=5/52.
This is exactly the BM-27 all-n eraser. Hence the limiting
symmetrized optimal readout channel is UNIQUE as a joint infinite law.

For any sequence of feasible finite-n masks with per-bit caps tending
to 5/52, after path/bit permutation averaging the projection onto
ANY FIXED k ordinary paths and the exceptional pair converges in
total variation to BM-27's corresponding finite projection. This is
a qualitative convergence theorem from compactness + uniqueness,
with no explicit convergence rate.

Quantitative stability for any infinite equalizer with cap
eta<=5/52+delta follows from the sharp BM-29 weighted proof. Let
  H=integral min(dnu0,dnu1), J=integral(1-u)dmu, and
  G=16J/5-H>=0.
  T=(mu+nu0 wedge nu1)/2-v >=0 as a measure.
Then EXACTLY
  8 C_o+5 C_s-5/4 = (5/4)G+(5/2)T(total),
so G<=52*delta/5 and T(total)<=26*delta/5.
Using the two-level dyadic lemma for u>5/8 gives a local lower gap
  g(u) =
   16(1-u)/5-1         if u<=5/8,
   16(3/4-u)/5         if 5/8<u<=3/4,
   16(1-u)/5           if 3/4<u<=1,
with G>=integral g(u)dmu. Thus for every eps in (0,1],
  mu{dist(u,{3/4,1})>=eps}
      <= 52*delta/min(1,16*eps).
All finite arithmetic and the full one-parameter attaining family are
tested in Fractions. The de Finetti uniqueness and general measure
stability arguments live in the companion Markdown proof, and are NOT
machine-formalized in Lean.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import lcm

try:
    from .replication_uniform_upper_BM27 import (
        PAIR_I,PAIR_A,PAIR_B,PAIR_E,PAIRS,COMPONENTS,
        exact_clean_law,xor_convolve,verify_convolution_identity,
    )
    from .infinite_replication_rigidity_BM29 import (
        LIMIT,WEIGHTED_BOUND,pair_walsh,
        ordinary_pair_mask_coordinates,
        weighted_limit_inequality,
    )
except ImportError:
    from replication_uniform_upper_BM27 import (
        PAIR_I,PAIR_A,PAIR_B,PAIR_E,PAIRS,COMPONENTS,
        exact_clean_law,xor_convolve,verify_convolution_identity,
    )
    from infinite_replication_rigidity_BM29 import (
        LIMIT,WEIGHTED_BOUND,pair_walsh,
        ordinary_pair_mask_coordinates,
        weighted_limit_inequality,
    )


def _blend(*weighted):
    """Exact normalized four-state convex combination."""
    output=tuple(
        sum((Fraction(p)*law[i] for p,law in weighted),Fraction(0))
        for i in range(4)
    )
    if sum(output,Fraction(0))!=1 or any(x<0 for x in output):
        raise AssertionError("invalid pair mixture")
    return output


SPECIAL_CONDITIONAL={
    "I":(PAIR_E,PAIR_E),
    "A":(_blend((Fraction(1,2),PAIR_I),(Fraction(1,2),PAIR_E)),
         PAIR_A),
    "B":(_blend((Fraction(3,4),PAIR_I),(Fraction(1,4),PAIR_A)),
         _blend((Fraction(3,4),PAIR_I),(Fraction(1,4),PAIR_B))),
}


@dataclass(frozen=True)
class DirectingAtom:
    name: str
    mu: Fraction
    u: Fraction
    w: Fraction
    nu0: Fraction
    nu1: Fraction
    v: Fraction

    @property
    def overlap(self)->Fraction:
        return min(self.nu0,self.nu1)


def _check_c(c:Fraction)->Fraction:
    c=Fraction(c)
    if not 0<=c<=Fraction(1,10):
        raise ValueError("weighted-equality directing parameter c outside [0,1/10]")
    return c


def canonical_equality_atoms(c:Fraction)->tuple[DirectingAtom,...]:
    """The complete BM-29 weighted-dual equality family."""
    c=_check_c(c)
    return (
        DirectingAtom("I",1-10*c,Fraction(1),Fraction(1),
                      Fraction(0),Fraction(0),(1-10*c)/2),
        DirectingAtom("A",2*c,Fraction(3,4),Fraction(1),
                      c,2*c,3*c/2),
        DirectingAtom("B",8*c,Fraction(3,4),Fraction(1,2),
                      8*c,7*c,15*c/2),
    )


def conditional_special_from_moments(atom:DirectingAtom,h:int):
    """Recover nonnegative two-bit exceptional law from its signed moments."""
    if h not in (0,1):
        raise ValueError("hidden hypothesis must be 0 or 1")
    if not atom.mu:
        raise ValueError("zero-mass directing atom has no conditional mask")
    mean=atom.v/atom.mu
    parity=(atom.nu0 if h==0 else atom.nu1)/atom.mu
    law=(
        (1+2*mean+parity)/4,
        (1-parity)/4,
        (1-parity)/4,
        (1-2*mean+parity)/4,
    )
    if any(p<0 for p in law) or sum(law,Fraction(0))!=1:
        raise AssertionError("nonphysical special mask from equality moments")
    return tuple(Fraction(p) for p in law)


def frontier_costs(c:Fraction)->tuple[Fraction,Fraction,Fraction]:
    """Two exactly attained per-bit costs and minimax maximum."""
    c=_check_c(c)
    co=Fraction(5,4)*c
    cs=Fraction(1,4)-2*c
    return co,cs,max(co,cs)


def frontier_components(c:Fraction,h:int):
    """All-n legal world-specific mixtures for the weighted frontier.

    The zero ordinary-mask/exceptional E component individually erases
    both hypotheses. The other BM-27 branches, renormalized, also
    erase both worlds; any convex mixture of the two does likewise.
    """
    c=_check_c(c)
    if h not in (0,1):
        raise ValueError("hypothesis must be 0/1")
    comps=[("I","E",1-10*c)]
    for ordinary,special,numerator in COMPONENTS[h]:
        if (ordinary,special)==("I","E"):
            if numerator!=3:
                raise AssertionError("BM-27 initial eraser branch changed")
            continue
        comps.append((ordinary,special,c*numerator))
    if sum((p for _,_,p in comps),Fraction(0))!=1:
        raise AssertionError("frontier component probabilities not normalized")
    if any(p<0 for _,_,p in comps):
        raise AssertionError("negative frontier mixture branch")
    return tuple((o,e,p) for o,e,p in comps if p)


def _pair_tensor(a:dict[int,Fraction],law,shift:int):
    out={}
    for x,p in a.items():
        for j,w in enumerate(law):
            if w:
                mask=x|(j<<shift)
                out[mask]=out.get(mask,Fraction(0))+p*w
    return out


def explicit_frontier_mask(n:int,c:Fraction,h:int, *,
                           max_bits:int=12):
    """Direct full-mask law for bounded n, independent of Fourier LP."""
    if not isinstance(n,int) or n<1 or 2*n+2>max_bits:
        raise ValueError("bounded finite frontier mask requires 1<=2n+2<=12")
    out={}
    for ordinary,special,branch in frontier_components(c,h):
        partial={0:branch}
        for i in range(n):
            partial=_pair_tensor(partial,PAIRS[ordinary],2*i)
        partial=_pair_tensor(partial,PAIRS[special],2*n)
        for mask,p in partial.items():
            out[mask]=out.get(mask,Fraction(0))+p
    out={mask:p for mask,p in out.items() if p}
    if sum(out.values(),Fraction(0))!=1:
        raise AssertionError("full frontier mask not normalized")
    return out


def verify_exact_frontier(c:Fraction,*,n_values=(1,2,3)):
    """Independent complete-output and marginal checks for finite controls."""
    c=_check_c(c)
    if not verify_convolution_identity():
        raise AssertionError("prior BM-27 component algebra unavailable")
    atoms=canonical_equality_atoms(c)
    if sum((a.mu for a in atoms),Fraction(0))!=1:
        raise AssertionError("directing masses not normalized")
    for atom in atoms:
        if atom.mu:
            for h in (0,1):
                if conditional_special_from_moments(atom,h)!=(
                    SPECIAL_CONDITIONAL[atom.name][h]
                ):
                    raise AssertionError("exceptional conditional law changed")
    co,cs,cap=frontier_costs(c)
    if weighted_limit_inequality(co,cs)!=WEIGHTED_BOUND:
        raise AssertionError("8:5 weighted equality not attained")
    for n in n_values:
        clean0,clean1=exact_clean_law(n,0),exact_clean_law(n,1)
        masks=[]
        for h in (0,1):
            mask=explicit_frontier_mask(n,c,h)
            masks.append(mask)
            for bit in range(2*n+2):
                observed=sum((p for x,p in mask.items()
                              if x&(1<<bit)),Fraction(0))
                expected=co if bit<2*n else cs
                if observed!=expected:
                    raise AssertionError("frontier mask marginal mismatch")
        if xor_convolve(clean0,masks[0])!=xor_convolve(clean1,masks[1]):
            raise AssertionError("frontier masks fail complete output equality")
    return co,cs,cap


def optimized_frontier():
    """Closed-form unique minimax optimum and its finite exact checks."""
    # 5c/4 = 1/4-2c -> 13c=1.
    c=Fraction(1,13)
    co,cs,cap=verify_exact_frontier(c)
    if co!=cs or cap!=LIMIT:
        raise AssertionError("minimax intersection not at BM-27")
    for endpoint in (Fraction(0),Fraction(1,10)):
        if frontier_costs(endpoint)[2]<=cap:
            raise AssertionError("frontier endpoints should be suboptimal")
    return {
        "optimal_directing_parameter":"1/13",
        "mu_I":"3/13","mu_A":"2/13","mu_B":"8/13",
        "ordinary_cost":str(co),"exceptional_cost":str(cs),
        "minimax_cap":str(cap),
        "frontier_Cordinary":"5*c/4",
        "frontier_Cexceptional":"1/4-2*c",
        "unique_symmetric_infinite_mask_channel":True,
        "quantitative_finite_n_rate_claimed":False,
    }


def local_overlap_gap_lower(u:Fraction)->Fraction:
    """Exact pointwise bound for dyadic overlap-deficit G on a u-fiber.

    For u<=5/8, H_u<=mu_u, producing 16(1-u)/5-1.
    For 5/8<u<=3/4, w>=2u-1>1/4 permits at most two
    dyadic levels and H_u<=4 mu_u/5.
    For u>3/4, no pair is physically possible; H_u=0.
    """
    u=Fraction(u)
    if not -1<=u<=1:
        raise ValueError("ordinary one-bit Walsh coordinate outside [-1,1]")
    if u<=Fraction(5,8):
        gap=Fraction(16,5)*(1-u)-1
    elif u<=Fraction(3,4):
        gap=Fraction(16,5)*(Fraction(3,4)-u)
    else:
        gap=Fraction(16,5)*(1-u)
    if gap<0:
        raise AssertionError("negative local overlap-deficit certificate")
    return gap


def stability_bounds(delta:Fraction,epsilon:Fraction)->dict:
    """Certified near-optimal infinite-channel localization inequalities.

    If eta<=5/52+delta then:
      G<=52*delta/5,
      special positivity slack T<=26*delta/5,
      mu{distance(u,{3/4,1})>=epsilon}
          <=52*delta/min(1,16*epsilon).
    These are bounds on infinite exchangeable *directing measures*,
    with no explicit finite-n convergence-rate claim.
    """
    delta=Fraction(delta)
    epsilon=Fraction(epsilon)
    if delta<0 or not 0<epsilon<=1:
        raise ValueError("delta>=0 and 0<epsilon<=1 required")
    gap=Fraction(52,5)*delta
    return {
        "weighted_cost_gap":13*delta,
        "overlap_deficit_upper":gap,
        "special_nonnegativity_slack_upper":Fraction(26,5)*delta,
        "mass_far_from_optimal_u_upper":
            min(Fraction(1),Fraction(52)*delta/min(
                Fraction(1),16*epsilon
            )),
        "localization_epsilon":epsilon,
    }


def proof_receipt():
    values=optimized_frontier()
    values.update({
        "BM29_limit":str(LIMIT),
        "weighted_inequality":"8*C_ordinary+5*C_exceptional>=5/4",
        "stability_gap":"G <= 52*delta/5",
        "near_optimal_directing_mass":
          "mu{dist(u,{3/4,1})>=eps}<=52*delta/min(1,16eps)",
        "finite_n_fixed_projection_convergence":"qualitative by compactness and uniqueness",
        "measure_theory_machine_formalized":False,
    })
    return values
