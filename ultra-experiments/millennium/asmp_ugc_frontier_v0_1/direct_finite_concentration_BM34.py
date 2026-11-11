"""BM-34: direct finite-population concentration proves O(n^-1/2) erasure rate.

The BM-33 scalar threshold bound used BM-31's with-replacement
approximation and paid an O(k/n) sampling penalty, optimizing to
O(n^-1/3). For the particular *permutation-invariant* output
statistic on ALL n ordinary path pairs, sampling mask types without
replacement incurs NO additional variance or bias.

Conditional on the exact n-path empirical mask histogram
c=(c0,c1,c2), exceptional mask z, and clean terminal difference:
  - the ordinary mask types occur in uniformly random order;
  - their within-one-flip orientations and the clean path outcomes
    are independent conditional on a FIXED type order;
  - the observed empirical Fourier statistic is permutation-invariant,
    so its distribution can be analyzed at that fixed order.

Let X_i,Y_i be the reported ±1 bits on ordinary path i. Define
  Uhat=clip[ (2/(3n)) sum_i (X_i+Y_i), -1,1],
  What=(1/n) sum_i X_i*Y_i.
Its conditional means are u=(c0-c2)/n, and
lambda*w, w=(c0-c1+c2)/n, with lambda=1 (clean matched A)
or lambda=1/2 (clean unmatched B). Exact conditional variances:
  matched A:
    Var[(2/3)(X+Y)] for types 0/1/2 = (7/9,0,7/9),
    Var[X*Y] for all types = 0.
  unmatched B:
    Var[(2/3)(X+Y)] for types 0/1/2 = (1/3,4/9,1/3),
    Var[X*Y] for all types = 3/4.

Thus for any globally coordinatewise Lipschitz test f with constants
Lu and Lw,
  abs(E[f(Uhat,What)] - f(u,lambda*w))
    <= max( (8/9)*Lu, (2/3)*Lu+(7/8)*Lw ) /sqrt(n),
using sqrt(7)<8/3 and sqrt(3)<7/4.

The two worlds' COMPLETE masked output laws agree, so their
expectations of the SAME observable
  (-1)^(special-output pair parity) f(Uhat,What)
are EXACTLY equal. By the BM-29 clean terminal weights, the
difference of ideal conditional expectations is D[f]/16.
Consequently without any iid replacement:
  |D[f]| <= (32/sqrt(n))*
            max((8/9)*Lu,(2/3)*Lu+(7/8)*Lw).

BM-33's exact overlap dual has Lu<=64/15, Lw<=18/5; the
maximum equals 1079/180. Its weighted robust lower inequality
then gives the FULL finite-n scalar theorem

  0<=5/52-eta_n(8,2)<=2158/(117*sqrt(n)), n>=1.

This improves BM-33's n^-1/3 rate to n^-1/2 and has no
empirical-replacement sampling approximation. All checks use
Fractions and an exact, independently enumerated conditional moment
table, with end-to-end tests on earlier exact mask witnesses.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

try:
    from .robust_overlap_potential_BM33 import (
        LIMIT, robust_potential, overlap_dual_gap,
        verify_analytic_potential,
    )
    from .robust_dyadic_observables_BM32 import (
        LipschitzTest, empirical_observable, observable_expectation,
        dyadic_residual,
    )
    from .finite_empirical_extension_BM31 import (
        empirical_joint_law, directing_law, exceptional_singlebit_marginal,
    )
    from .replication_uniform_upper_BM27 import (
        PAIR_A,PAIR_B,xor_pair,exact_clean_law,xor_convolve,
    )
except ImportError:
    from robust_overlap_potential_BM33 import (
        LIMIT, robust_potential, overlap_dual_gap,
        verify_analytic_potential,
    )
    from robust_dyadic_observables_BM32 import (
        LipschitzTest, empirical_observable, observable_expectation,
        dyadic_residual,
    )
    from finite_empirical_extension_BM31 import (
        empirical_joint_law, directing_law, exceptional_singlebit_marginal,
    )
    from replication_uniform_upper_BM27 import (
        PAIR_A,PAIR_B,xor_pair,exact_clean_law,
    )


ONE_BIT_LIP=Fraction(64,15)
PAIR_PARITY_LIP=Fraction(18,5)
MATCHED_U_SQRT_BOUND=Fraction(8,9)
UNMATCHED_U_SQRT_BOUND=Fraction(2,3)
UNMATCHED_W_SQRT_BOUND=Fraction(7,8)
SAMPLE_ERROR=Fraction(1079,180)
SIGNED_DEFECT_COEFFICIENT=Fraction(32)*SAMPLE_ERROR
SCALAR_RATE=Fraction(2158,117)


def _validate_n(n:int)->None:
    if not isinstance(n,int) or n<1:
        raise ValueError("number of ordinary paths must be a positive integer")


def _one_type_mask(t:int)->tuple[Fraction,...]:
    """Physical mask on 00,10,01,11 given exactly t flipped edges."""
    if t==0:
        return (Fraction(1),Fraction(0),Fraction(0),Fraction(0))
    if t==1:
        return (Fraction(0),Fraction(1,2),Fraction(1,2),Fraction(0))
    if t==2:
        return (Fraction(0),Fraction(0),Fraction(0),Fraction(1))
    raise ValueError("ordinary path mask Hamming type must be 0,1,2")


@dataclass(frozen=True)
class PathMoment:
    clean_regime:str
    mask_type:int
    mean_u:Fraction
    mean_parity:Fraction
    variance_u:Fraction
    variance_parity:Fraction


def path_moment(regime:str,t:int)->PathMoment:
    """Exact conditional moment table from 4-point XOR convolution.

    U=(2/3)(X+Y), V=X*Y, with X,Y observed ±1 characters.
    All four expectations are evaluated independently from the pair
    mass distribution, including fair one-flip mask orientation.
    """
    if regime not in ("A","B"):
        raise ValueError("conditional clean path regime must be A/B")
    noise=_one_type_mask(t)
    output=xor_pair(PAIR_A if regime=="A" else PAIR_B,noise)
    def stats(which):
        vals=[]
        for outcome,prob in enumerate(output):
            x=1 if not outcome&1 else -1
            y=1 if not outcome&2 else -1
            vals.append((Fraction(2,3)*(x+y) if which=="U" else
                         Fraction(x*y),prob))
        mean=sum((v*p for v,p in vals),Fraction(0))
        variance=sum((p*(v-mean)**2 for v,p in vals),Fraction(0))
        return mean,variance
    mu,vu=stats("U")
    mw,vw=stats("W")
    return PathMoment(regime,t,mu,mw,vu,vw)


def verify_variance_table()->dict[str,object]:
    """Finite rational proof of conditional means/variances and norm bounds."""
    expected={
        ("A",0):(1,1,Fraction(7,9),0),
        ("A",1):(0,-1,0,0),
        ("A",2):(-1,1,Fraction(7,9),0),
        ("B",0):(1,Fraction(1,2),Fraction(1,3),Fraction(3,4)),
        ("B",1):(0,-Fraction(1,2),Fraction(4,9),Fraction(3,4)),
        ("B",2):(-1,Fraction(1,2),Fraction(1,3),Fraction(3,4)),
    }
    for (regime,t),table in expected.items():
        point=path_moment(regime,t)
        if (point.mean_u,point.mean_parity,
            point.variance_u,point.variance_parity)!=table:
            raise AssertionError("conditional XOR/path variance table changed")
    if Fraction(7,9)>MATCHED_U_SQRT_BOUND**2:
        raise AssertionError("sqrt 7/3 bound false")
    if Fraction(4,9)>UNMATCHED_U_SQRT_BOUND**2:
        raise AssertionError("unmatched ordinary variance bound false")
    if Fraction(3,4)>UNMATCHED_W_SQRT_BOUND**2:
        raise AssertionError("sqrt3/2 rational bound false")
    if verify_analytic_potential()["l1_lipschitz_bound"]!=ONE_BIT_LIP:
        raise AssertionError("BM33 potential norm changed")
    # BM33's robust potential derivative ranges:
    #   middle: fu=16 f0, fw=t*f0'; upper:
    #   fu=-4 f0-2/3+clamp_u, clamp_u in {0,4};
    #   fw=(1-t)f0'+clamp_w, clamp_w in {0,2}.
    f0_values=(Fraction(-2,15),Fraction(1,15),Fraction(4,15))
    f0_slopes=(Fraction(0),Fraction(4,5),Fraction(8,5))
    middle_u=max(abs(16*a) for a in f0_values)
    upper_u=max(abs(-4*a-Fraction(2,3)+e)
                for a in f0_values for e in (0,4))
    middle_w=max(f0_slopes)
    upper_w=max(x+e for x in f0_slopes for e in (0,2))
    if max(middle_u,upper_u)!=ONE_BIT_LIP:
        raise AssertionError("global coordinate-u Lipschitz bound failed")
    if max(middle_w,upper_w)!=PAIR_PARITY_LIP:
        raise AssertionError("global coordinate-w Lipschitz bound failed")
    match=MATCHED_U_SQRT_BOUND*ONE_BIT_LIP
    unmatched=(UNMATCHED_U_SQRT_BOUND*ONE_BIT_LIP+
               UNMATCHED_W_SQRT_BOUND*PAIR_PARITY_LIP)
    if max(match,unmatched)!=SAMPLE_ERROR:
        raise AssertionError("conditional sqrt-variance envelope mismatch")
    if LIMIT*SIGNED_DEFECT_COEFFICIENT!=SCALAR_RATE:
        raise AssertionError("finite scalar rate coefficient mismatch")
    return {
        "clean_regimes":("A","B"),
        "path_mask_types":(0,1,2),
        "variance_cases_checked":6,
        "ordinary_coordinate_lipschitz":ONE_BIT_LIP,
        "parity_coordinate_lipschitz":PAIR_PARITY_LIP,
        "max_one_world_estimator_error_coefficient":SAMPLE_ERROR,
        "signed_dyadic_defect_coefficient":SIGNED_DEFECT_COEFFICIENT,
        "scalar_masking_gap_coefficient":SCALAR_RATE,
        "variance_bound_method":"conditional fixed-histogram, independent clean paths and orientations",
    }


@dataclass(frozen=True)
class ConditionalMoment:
    n:int
    histogram:tuple[int,int,int]
    clean_regime:str
    mean_u:Fraction
    mean_w:Fraction
    variance_u:Fraction
    variance_w:Fraction


def conditional_moments(n:int,hist:tuple[int,int,int],
                        regime:str)->ConditionalMoment:
    """Exact sample means/variances at fixed empirical mask histogram.

    Conditional on histogram plus special mask, fix any ordering of the
    three mask types. The empirical statistic is permutation-invariant,
    so the ordering carries NO variance. Outcomes from different paths
    are independent because clean internal labels and one-bit mask
    orientations are independent. All variances therefore ADD.
    """
    _validate_n(n)
    if (len(hist)!=3 or any(not isinstance(v,int) or v<0
                            for v in hist) or sum(hist)!=n or
        regime not in ("A","B")):
        raise ValueError("valid ordinary mask histogram and A/B regime required")
    points=[path_moment(regime,t) for t in range(3)]
    mean_u=sum((hist[t]*points[t].mean_u for t in range(3)),
               Fraction(0))/n
    mean_w=sum((hist[t]*points[t].mean_parity for t in range(3)),
               Fraction(0))/n
    variance_u=sum((hist[t]*points[t].variance_u for t in range(3)),
                   Fraction(0))/n**2
    variance_w=sum((hist[t]*points[t].variance_parity for t in range(3)),
                   Fraction(0))/n**2
    if mean_u!=Fraction(hist[0]-hist[2],n):
        raise AssertionError("ordinary empirical single-bit mean mismatch")
    parity=Fraction(hist[0]-hist[1]+hist[2],n)
    if mean_w!=parity*(1 if regime=="A" else Fraction(1,2)):
        raise AssertionError("ordinary empirical parity mean mismatch")
    if variance_u>(Fraction(7,9) if regime=="A" else
                   Fraction(4,9))/n:
        raise AssertionError("fixed histogram u variance upper violated")
    if variance_w>(0 if regime=="A" else Fraction(3,4))/n:
        raise AssertionError("fixed histogram w variance upper violated")
    return ConditionalMoment(n,hist,regime,mean_u,mean_w,
                             variance_u,variance_w)


def direct_signed_bound_squared(n:int, *,
                                lip_u:Fraction=ONE_BIT_LIP,
                                lip_w:Fraction=PAIR_PARITY_LIP)->Fraction:
    """Exact rational |D[f]|² <=(32*sample_error)²/n.

    Coordinatewise Lipschitz constants can be any nonnegative rationals;
    the coefficient uses rigorously bounded square roots of the
    conditional variances, without floating-point square roots.
    """
    _validate_n(n)
    a,b=Fraction(lip_u),Fraction(lip_w)
    if a<0 or b<0:
        raise ValueError("coordinatewise Lipschitz constants must be nonnegative")
    sampling=max(a*MATCHED_U_SQRT_BOUND,
                 a*UNMATCHED_U_SQRT_BOUND+
                 b*UNMATCHED_W_SQRT_BOUND)
    return (32*sampling)**2/n


def finite_threshold_bound_squared(n:int)->Fraction:
    """Exact finite-n scalar theorem: (5/52-eta_n)² <= K²/n."""
    return SCALAR_RATE**2/Fraction(n) if (
        isinstance(n,int) and n>=1
    ) else _bad_n(n)


def _bad_n(n):
    raise ValueError("positive integer ordinary path count required")


def certified_lower_squared(n:int)->dict[str,Fraction|int]:
    """A real inequality certificate with no numeric square-root rounding."""
    return {
        "ordinary_paths":n,
        "asymptotic_cap":LIMIT,
        "squared_scalar_gap_upper":finite_threshold_bound_squared(n),
        "squared_dyadic_defect_upper":direct_signed_bound_squared(n),
        "method":"all n paths, conditional fixed-histogram variance",
    }


@dataclass(frozen=True)
class DirectWitnessReceipt:
    ordinary_paths:int
    direct_observable_gap:Fraction
    latent_ideal_gap:Fraction
    signed_dyadic_defect:Fraction
    conditional_one_world_error_bound_squared:Fraction
    direct_signed_bound_squared:Fraction
    scalar_gap_bound_squared:Fraction
    ordinary_bit_cost:Fraction
    exceptional_bit_cost:Fraction
    complete_output_equal:bool


def verify_finite_witness(n:int,q0:dict[int,Fraction],
                          q1:dict[int,Fraction])->DirectWitnessReceipt:
    """Independent exact check of the NO-replacement estimator on real masks.

    Small n only: sum the actual complete reported output laws and the
    observable G on all 2^(2n+2) Boolean patterns. Separately derive
    the latent ideal from the finite joint ordinary-mask histogram,
    exceptional mask parity, and clean terminal conditional weights.
    """
    if not isinstance(n,int) or not 1<=n<=5:
        raise ValueError("explicit full-output checks limited to 1<=n<=5")
    j0=empirical_joint_law(n,q0)
    j1=empirical_joint_law(n,q1)
    mu0=directing_law(n,j0)
    mu1=directing_law(n,j1)
    if mu0!=mu1 or any(
        exceptional_singlebit_marginal(n,j0,i)!=
        exceptional_singlebit_marginal(n,j1,i)
        for i in (0,1)
    ):
        raise AssertionError("BM29 finite marginal rigidity violated")
    test=LipschitzTest("BM34 direct",Fraction(5,6),
                       ONE_BIT_LIP,robust_potential)
    ideal=[]
    output=[]
    observed=[]
    for h,joint in enumerate((j0,j1)):
        # Exactly symmetrize the mask in its own orbit, since the clean
        # laws and observable are invariant under every such symmetry.
        try:
            from .finite_empirical_extension_BM31 import (
                expand_empirical_joint_law,
            )
        except ImportError:
            from finite_empirical_extension_BM31 import (
                expand_empirical_joint_law,
            )
        sym=expand_empirical_joint_law(n,joint)
        clean=exact_clean_law(n,h)
        masked=xor_convolve(clean,sym)
        output.append(masked)
        observed.append(observable_expectation(n,masked,test))
        ideal_value=Fraction(0)
        for (hist,special),mass in joint.items():
            u=Fraction(hist[0]-hist[2],n)
            w=Fraction(hist[0]-hist[1]+hist[2],n)
            parity=(-1 if special.bit_count()%2 else 1)
            if h==0:
                component=(Fraction(1,8)*robust_potential(u,w)+
                           Fraction(7,16)*robust_potential(u,w/2))
            else:
                component=(Fraction(1,16)*robust_potential(u,w)+
                           Fraction(1,2)*robust_potential(u,w/2))
            ideal_value+=mass*parity*component
        ideal.append(ideal_value)
        bias=observed[-1]-ideal[-1]
        # |bias|<=1079/(180 sqrt(n)) by conditional variance.
        if n*bias*bias>SAMPLE_ERROR**2:
            raise AssertionError("direct conditional estimation error violated")
    if output[0]!=output[1] or observed[0]!=observed[1]:
        raise AssertionError("actual world outputs fail exact equality")
    dyadic=dyadic_residual(n,j0,j1,test)
    if ideal[0]-ideal[1]!=dyadic/16:
        raise AssertionError("latent ideal does not match BM32 signed defect")
    if n*dyadic*dyadic>SIGNED_DEFECT_COEFFICIENT**2:
        raise AssertionError("direct finite dyadic rate violated")
    # Both costs are determined by the shared ordinary empirical law
    # and the identical individual exceptional-bit mask marginal.
    ordinary=sum((mass*Fraction(hist[1]+2*hist[2],2*n)
                  for hist,mass in mu0.items()),Fraction(0))
    special=sum((weight*Fraction(special.bit_count(),2)
                 for (_,special),weight in j0.items()),Fraction(0))
    if ordinary>LIMIT or special>LIMIT:
        raise AssertionError("registered small witness budget above known upper")
    cap=max(ordinary,special)
    if n*(LIMIT-cap)**2>SCALAR_RATE**2:
        raise AssertionError("finite scalar rate fails registered witness")
    return DirectWitnessReceipt(
        n,observed[0]-observed[1],ideal[0]-ideal[1],dyadic,
        SAMPLE_ERROR**2/Fraction(n),direct_signed_bound_squared(n),
        finite_threshold_bound_squared(n),ordinary,special,True,
    )


def theorem_receipt(n:int=10**12)->dict[str,object]:
    certificate=verify_variance_table()
    return {
        **certificate,
        "ordinary_paths":n,
        "uniform_rate":"O(n^-1/2)",
        "rigorous_scalar_gap":"0 <= 5/52-eta_n <= 2158/(117*sqrt(n))",
        "squared_scalar_gap_upper":str(finite_threshold_bound_squared(n)),
        "permutation_sampling_penalty":"zero for the symmetric sample means",
        "finite_exchangeability_approximation_required":False,
        "abstract_de_Finetti_limit_required":False,
        "infinite_measure_theory_formalized_in_Lean":False,
    }
