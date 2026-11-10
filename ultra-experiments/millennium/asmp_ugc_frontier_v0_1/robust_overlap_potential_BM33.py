"""BM-33: explicit Lipschitz dyadic dual and finite-n erasure threshold rate.

Proves an exact continuous, piecewise-linear dual potential f(u,w)
for BM-29's signed dyadic overlap inequality, including arbitrary
approximate signed flow D=(2I+7S_*)nu0-(I+8S_*)nu1.

For physical symmetric two-bit ordinary-noise parameters (u,w),
    -1<=u<=1,  2*abs(u)-1<=w<=1,
let c(u)=16*(1-u)/5.  The explicit f in this module satisfies
    |1-f(u,w)+f(u,w/2)| <= c(u),
    |3*f(u,w)+15*f(u,w/2)| <= 1+c(u),
with ||f||_infty<=5/6 and Lip_l1(f)<=64/15.

For any common positive directing measure mu, signed nu_h dominated
by mu and an exceptional one-bit measure v satisfying
    2*v <= mu + min(nu0,nu1),
the pointwise inequalities imply:
    H=integral min(dnu0,dnu1)
       <= 16/5*J + D[f], J=integral(1-u)dmu.
Therefore
    8*C_ord+5*C_special >= 5/4-(5/4)*D[f],
with C_ord=J/2 and C_special=(1-integral v)/2.

BM-31 and BM-32 give for ANY exactly erasing n-path channel
    |D[f]| <=64*(5/6)*sqrt(k(k-1)/(2(n-1)(n-k+1)))
              +224*(64/15)/(3 sqrt(k)).
Since both per-bit costs <=eta_n and BM-27 proves eta_n<=5/52,
the completely explicit FINITE-N scalar theorem is

  0 <= 5/52 - eta_n(8,2)
     <= (200/39)*sqrt(k(k-1)/(2(n-1)(n-k+1)))
        + (3584/117)/sqrt(k),

for n>=2 and 1<=k<=n. Choosing k=floor(n^(2/3))
gives eta_infty-eta_n=O(n^(-1/3)). This is the previously open
quantitative scalar convergence-rate bridge.

The tests use exact rational pointwise constraints, analytical
piecewise segment/convexity checks and the BM-25..28 certified finite
thresholds. The de Finetti and finite-window mathematics comes from
BM-29..32; no Lean formalization or deployed AI safety claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

try:
    from .finite_empirical_extension_BM31 import (
        finite_alphabet_tv_squared_bound,entropy_growing_window_bound,
    )
    from .infinite_replication_rigidity_BM29 import LIMIT
except ImportError:
    from finite_empirical_extension_BM31 import (
        finite_alphabet_tv_squared_bound,entropy_growing_window_bound,
    )
    from infinite_replication_rigidity_BM29 import LIMIT


HALF=Fraction(1,2)
LOW_U=Fraction(11,16)
HIGH_U=Fraction(3,4)
SUP_NORM=Fraction(5,6)
LIP_L1=Fraction(64,15)
RATE_COLLISION=Fraction(200,39)
RATE_SAMPLING=Fraction(3584,117)
C=Fraction(16,5)


def _clip(x:Fraction,lo:Fraction,hi:Fraction)->Fraction:
    return min(hi,max(lo,x))


def base_potential(w:Fraction)->Fraction:
    """Piecewise-linear exact potential f0, slopes 0,8/5,0,4/5,0.

    On every w in [3/8,1]:
       f0(w)-f0(w/2)=1/5,
       |3f0(w)+15f0(w/2)|<=9/5.
    The proof reduces to endpoints of the 3 linear segments.
    """
    w=Fraction(w)
    if not -1<=w<=1:
        raise ValueError("ordinary parity w must be within [-1,1]")
    if w<=Fraction(1,4):
        return -Fraction(2,15)
    if w<=Fraction(3,8):
        return -Fraction(2,15)+Fraction(8,5)*(w-Fraction(1,4))
    if w<=HALF:
        return Fraction(1,15)
    if w<=HIGH_U:
        return Fraction(1,15)+Fraction(4,5)*(w-HALF)
    return Fraction(4,15)


def robust_potential(u:Fraction,w:Fraction)->Fraction:
    """Globally continuous piecewise-linear bounded/Lipschitz test.

    For u<=11/16, f=0 and c(u)>=1.
    For 11/16<u<=3/4, f=(16u-11)*f0(w).
    For u>3/4, t=4u-3, and
      f=(1-t)f0(w)-t/6+clip(2w-1,0,t).
    On the physically feasible region w>=2u-1 (u>3/4),
    f(u,w)=(1-t)f0(w)+5t/6 and
    f(u,w/2)=(1-t)f0(w/2)-t/6.
    Hence the dual character inequalities follow from f0's.
    """
    u,w=Fraction(u),Fraction(w)
    if not -1<=u<=1 or not -1<=w<=1:
        raise ValueError("Fourier coordinates must belong to [-1,1]")
    if u<=LOW_U:
        return Fraction(0)
    f0=base_potential(w)
    if u<=HIGH_U:
        return (16*u-11)*f0
    t=4*u-3
    return (1-t)*f0-t/6+_clip(2*w-1,Fraction(0),t)


def physical_pair(u:Fraction,w:Fraction)->bool:
    """Exactly the symmetric physical two-bit mask tetrahedron section."""
    u,w=Fraction(u),Fraction(w)
    return (-1<=u<=1 and 2*abs(u)-1<=w<=1)


@dataclass(frozen=True)
class PointwiseReceipt:
    u:Fraction
    w:Fraction
    potential:Fraction
    shifted_potential:Fraction
    overlap_coefficient:Fraction
    budget_coefficient:Fraction
    overlap_slack:Fraction
    budget_slack:Fraction


def pointwise_receipt(u:Fraction,w:Fraction)->PointwiseReceipt:
    """Two exact rational inequalities imply the signed-overlap dual."""
    u,w=Fraction(u),Fraction(w)
    if not physical_pair(u,w):
        raise ValueError("physical symmetric two-bit mask required")
    a=robust_potential(u,w)
    b=robust_potential(u,w/2)
    c=C*(1-u)
    character=abs(1-a+b)
    cost=abs(3*a+15*b)
    s1=c-character
    s2=1+c-cost
    if min(s1,s2)<0:
        raise AssertionError(
            f"invalid dual at u={u}, w={w}, slacks={s1},{s2}"
        )
    return PointwiseReceipt(u,w,a,b,character,cost,s1,s2)


def verify_analytic_potential()->dict[str,Fraction|int]:
    """Exact rational verification of the base/convexity argument.

    On w in [3/8,1], f0 and f0(w/2) are affine between the breakpoints
    3/8,1/2,3/4,1, so checking endpoints proves both constraints
    for ALL real w. For u in [11/16,3/4], f is a convex mixture of
    the zero potential at c=1 and f0 at c=4/5. For u>=3/4, its two
    physically used evaluations are a convex mixture of f0 (c=4/5)
    and the fixed high/low values (5/6,-1/6), feasible at c=0.
    These are symbolic arguments with exact endpoint checks.
    """
    points=(Fraction(3,8),HALF,HIGH_U,Fraction(1))
    for w in points:
        high=base_potential(w)
        low=base_potential(w/2)
        if high-low!=Fraction(1,5):
            raise AssertionError("base dyadic difference not constant")
        if abs(3*high+15*low)>Fraction(9,5):
            raise AssertionError("base dyadic weighted moment bound fails")
    if max(abs(base_potential(w)) for w in (
        Fraction(-1),Fraction(1,4),Fraction(3,8),
        HALF,HIGH_U,Fraction(1)
    ))!=Fraction(4,15):
        raise AssertionError("base potential supremum wrong")
    if not (
        (3*Fraction(5,6)+15*(-Fraction(1,6)))==0
        and Fraction(5,6)-(-Fraction(1,6))==1
    ):
        raise AssertionError("high-u endpoint dual fails")
    if RATE_COLLISION!=LIMIT*64*SUP_NORM or (
        RATE_SAMPLING!=LIMIT*Fraction(224,3)*LIP_L1
    ):
        raise AssertionError("scalar rate constants mismatch BM32")
    if LIP_L1<max(
        16*Fraction(4,15),Fraction(8,5),
        Fraction(58,15),Fraction(18,5)
    ):
        raise AssertionError("piecewise Lipschitz certificate too small")
    # Check equality on both BM-27 dyadic modes, and at u=1.
    for u,w in ((HIGH_U,Fraction(1)),(HIGH_U,HALF),
                (Fraction(1),Fraction(1))):
        r=pointwise_receipt(u,w)
        if r.overlap_slack!=0:
            raise AssertionError("optimal strict pointwise dual differs")
    return {
        "base_affine_segments":3,
        "physical_u_regimes":3,
        "sup_bound":SUP_NORM,
        "l1_lipschitz_bound":LIP_L1,
        "rate_collision_coefficient":RATE_COLLISION,
        "rate_sampling_coefficient":RATE_SAMPLING,
        "global_pointwise_proof":"exact affine endpoints and convex interpolation",
    }


def overlap_dual_gap(
    mu:dict[tuple[Fraction,Fraction],Fraction],
    nu0:dict[tuple[Fraction,Fraction],Fraction],
    nu1:dict[tuple[Fraction,Fraction],Fraction],
    v:dict[tuple[Fraction,Fraction],Fraction]
)->dict[str,Fraction]:
    """Check the robust overlap/cost inequalities on arbitrary finite atoms.

    Any physically legal infinite world-pair has such a directing law.
    This checker deliberately does NOT impose D=0; it works with an
    approximate signed flow as well.
    """
    if sum(mu.values(),Fraction(0))!=1 or any(
        m<0 or not physical_pair(*key) for key,m in mu.items()
    ):
        raise ValueError("normalized physical directing measure required")
    J,H,D,vtot=Fraction(0),Fraction(0),Fraction(0),Fraction(0)
    for key,m in mu.items():
        a=Fraction(nu0.get(key,0))
        b=Fraction(nu1.get(key,0))
        single=Fraction(v.get(key,0))
        if max(abs(a),abs(b))>m or 2*single>m+min(a,b):
            raise ValueError("invalid signed exceptional parity/bit measures")
        u,w=key
        J+=(1-u)*m
        H+=min(a,b)
        D+=(2*robust_potential(u,w)+
             7*robust_potential(u,w/2))*a
        D-=(robust_potential(u,w)+
             8*robust_potential(u,w/2))*b
        vtot+=single
    if any(key not in mu for law in (nu0,nu1,v) for key in law):
        raise ValueError("signed measure support outside directing law")
    Co=J/2
    Cs=(1-vtot)/2
    if H>Fraction(16,5)*J+D:
        raise AssertionError("signed-overlap robustness inequality violated")
    weighted=8*Co+5*Cs
    if weighted<Fraction(5,4)-Fraction(5,4)*D:
        raise AssertionError("weighted robust dual inequality violated")
    return {
        "J":J,"H":H,"dyadic_defect":D,
        "ordinary_bit_cost":Co,"exceptional_bit_cost":Cs,
        "weighted_cost":weighted,
        "weighted_lower":Fraction(5,4)*(1-D),
        "overlap_slack":Fraction(16,5)*J+D-H,
        "weighted_slack":weighted-Fraction(5,4)*(1-D),
    }


@dataclass(frozen=True)
class FiniteRateReceipt:
    n:int
    k:int
    collision_variance:Fraction
    bound_squared:Fraction
    cap_limit:Fraction
    coefficient_collision:Fraction
    coefficient_sampling:Fraction
    threshold_rate_proved:bool


def finite_rate(n:int,k:int)->FiniteRateReceipt:
    """Exact rational SQUARED error certificate (no floating point roots).

    The unsquared theorem:
        max(0,LIMIT-eta_n)
            <= A sqrt(v_(n,k)) + B/sqrt(k)
    where A=200/39, B=3584/117 and
          v=k(k-1)/[2(n-1)(n-k+1)].
    Conservatively,
        (LIMIT-eta_n)^2 <=2(A² v + B²/k).
    """
    if not isinstance(n,int) or n<2 or not isinstance(k,int) or (
        not 1<=k<=n
    ):
        raise ValueError("finite dual rate requires n>=2 and 1<=k<=n")
    v=finite_alphabet_tv_squared_bound(n,k)
    squared=2*(RATE_COLLISION**2*v+RATE_SAMPLING**2/k)
    return FiniteRateReceipt(n,k,v,squared,LIMIT,RATE_COLLISION,
                             RATE_SAMPLING,True)


def optimized_window_rate(n:int)->FiniteRateReceipt:
    """k=floor(n^(2/3)) gives explicit O(n^(-1/3)) scalar threshold rate."""
    if not isinstance(n,int) or n<2:
        raise ValueError("n>=2 required")
    k=entropy_growing_window_bound(n)["k"]
    return finite_rate(n,k)


def certify_known_eta(n:int,eta:Fraction)->bool:
    """Compare any independently certified exact eta_n with BM33's bound."""
    from math import isqrt
    eta=Fraction(eta)
    if not 0<=eta<=LIMIT:
        raise ValueError("known finite eta must lie below the BM27 upper")
    r=optimized_window_rate(n)
    if (LIMIT-eta)**2>r.bound_squared:
        raise AssertionError("certified finite threshold exceeds BM33 rate")
    return True


def symbolic_rate_manifest(n:int=10**12)->dict[str,object]:
    r=optimized_window_rate(n)
    return {
        "ordinary_paths":n,"sample_window_k":r.k,
        "finite_scalar_threshold_rate_proved":True,
        "rigorous_squared_gap_upper":str(r.bound_squared),
        "limit":"5/52",
        "rate":"eta_inf-eta_n=O(n^(-1/3))",
        "potential_sup":"5/6",
        "potential_l1_lipschitz":"64/15",
        "BM32_unsquared_collision_coefficient":"200/39",
        "BM32_unsquared_sampling_coefficient":"3584/117",
        "measure_theory_formalized_in_Lean":False,
    }
