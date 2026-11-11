"""BM-19: exact support-aware common readout postprocessing.

For a fixed pair of already masked Boolean observation distributions,
identify the actual nonzero Fourier discrepancy support D:
  D={S != empty : hat(P0*Q0)(S) != hat(P1*Q1)(S)}.
A further *common*, clean-sample-independent XOR mask R completes erasure
iff hatR(S)=0 for every S in D. Optimize the worst per-bit flip marginal
of R through an exact finite LP with 2^m mask masses, |D| Fourier
equalities, one normalization, and m marginal constraints.

Matching rational primal/dual witnesses prove the optimum without a
numerical solver. This is conditional on a particular partially masking
pair Q0,Q1; it is not the globally optimal new pair of masks. The full
erasure LP may attain a lower cap by replacing Q0,Q1 altogether.

For K4 after its degree-4 partial certificate, the residual support
D={47,61,63} permits R at max marginal 1/10, versus BM-18's universal
m=6,d=4 annihilator at 1/6. A 5-edge residual character gives a sharp
1/10 union-bound lower certificate; an explicit 8-mask law attains it.
For K4 degree 3 the sharp residual-specific cap is 7/38 (universal
5/24). For diamond/theta the corresponding residual cap matches the
universal BM-18 postprocessor, supplying adverse controls.

All exact rational bounds concern this finite Fourier monitoring model.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

try:
    from .generic_fourier_erasure_BM17 import (
        Pair, Primal, check_primal, census, signed_walsh, mask_walsh,
        mask_marginals as initial_mask_marginals,
    )
    from .fourier_completion_BM18 import (
        xor_convolve_masks, convolve_clean, mask_marginals,
    )
except ImportError:
    from generic_fourier_erasure_BM17 import (
        Pair, Primal, check_primal, census, signed_walsh, mask_walsh,
        mask_marginals as initial_mask_marginals,
    )
    from fourier_completion_BM18 import (
        xor_convolve_masks, convolve_clean, mask_marginals,
    )


@dataclass(frozen=True)
class PostprocessorPrimal:
    denominator: int
    weights: dict[int, int]


@dataclass(frozen=True)
class PostprocessorDual:
    normalization: Fraction
    characters: dict[int, Fraction]
    marginal_multipliers: tuple[Fraction, ...]


@dataclass(frozen=True)
class PostprocessorReceipt:
    discrepancy_support: tuple[int, ...]
    optimal_extra_flip: Fraction
    completed_max_flip: Fraction
    uniform_completion_upper: Fraction
    checked_dual_inequalities: int
    complete_laws_equal: bool


def _validate_support(m:int,support:tuple[int,...])->tuple[int,...]:
    if not isinstance(m,int) or not 1<=m<=12:
        raise ValueError("explicit mask verification requires 1..12 edges")
    if (len(set(support))!=len(support) or
        any(not isinstance(s,int) or not 0<s<(1<<m) for s in support)):
        raise ValueError("support must contain distinct nonzero Fourier indices")
    return tuple(sorted(support))


def remaining_fourier_support(
    pair:Pair,degree:int,initial:Primal
)->tuple[int,...]:
    """Compute actual residual Fourier support from independent clean counts."""
    check_primal(pair,degree,initial)
    p0,p1=census(pair.flat),census(pair.other)
    return tuple(s for s in range(1,1<<pair.m) if
        signed_walsh(p0,s)*mask_walsh(initial.q0,initial.denominator,s) !=
        signed_walsh(p1,s)*mask_walsh(initial.q1,initial.denominator,s)
    )


def verify_postprocessor_primal(
    m:int,support:tuple[int,...],witness:PostprocessorPrimal
)->Fraction:
    """Upper certificate: normalized mask, zero residual Walsh, all marginals."""
    support=_validate_support(m,support)
    D=witness.denominator
    if not isinstance(D,int) or D<=0 or sum(witness.weights.values())!=D or any(
        not isinstance(mask,int) or not 0<=mask<(1<<m) or
        not isinstance(weight,int) or weight<0
        for mask,weight in witness.weights.items()
    ):
        raise ValueError("invalid exact integer mask mass distribution")
    for S in support:
        if mask_walsh(witness.weights,D,S):
            raise AssertionError(f"postprocessor left residual Fourier index {S}")
    return max(initial_mask_marginals(witness.weights,D,m))


def verify_postprocessor_dual(
    m:int,support:tuple[int,...],proof:PostprocessorDual
)->Fraction:
    """Lower certificate: exact weak-duality constraints over ALL 2^m masks.

    Normalization multiplier y0, free Walsh y_S (for S in support),
    nonpositive per-bit z_i with -sum z=1, such that
      y0 + sum y_S chi_S(mask) + sum_{i:mask_i=1} z_i <=0
    for every mask. Then any feasible R has max marginal >=y0.
    """
    registered=set(_validate_support(m,support))
    if len(proof.marginal_multipliers)!=m or any(
        s not in registered for s in proof.characters
    ):
        raise ValueError("dual dimensions or character support invalid")
    z=tuple(Fraction(v) for v in proof.marginal_multipliers)
    if any(v>0 for v in z) or -sum(z,Fraction(0))!=1:
        raise AssertionError("dual marginal signs or normalization invalid")
    y0=Fraction(proof.normalization)
    for mask in range(1<<m):
        slack=y0+sum((
            Fraction(v)*(-1 if (mask&S).bit_count()%2 else 1)
            for S,v in proof.characters.items()
        ),Fraction(0))
        slack+=sum((z[i] for i in range(m) if mask&(1<<i)),Fraction(0))
        if slack>0:
            raise AssertionError(f"dual slack positive at mask={mask}")
    return y0


def certify_support_optimum(
    m:int,support:tuple[int,...],
    witness:PostprocessorPrimal,dual:PostprocessorDual
)->Fraction:
    """Matching exact upper/lower certificates establish optimum for fixed D."""
    upper=verify_postprocessor_primal(m,support,witness)
    lower=verify_postprocessor_dual(m,support,dual)
    if upper!=lower:
        raise AssertionError(f"primal/dual mismatch {upper} vs {lower}")
    return upper


def postprocess_partial_pair(
    pair:Pair,degree:int,initial:Primal,
    witness:PostprocessorPrimal,dual:PostprocessorDual
)->PostprocessorReceipt:
    """Independently verify full observation equality after common convolution."""
    m=pair.m
    support=remaining_fourier_support(pair,degree,initial)
    r=certify_support_optimum(m,support,witness,dual)
    if r>Fraction(1,2):
        raise ValueError("postprocessor bit cap must be <= 1/2")
    eta=Fraction(initial.eta)
    if not 0<=eta<=Fraction(1,2):
        raise ValueError("initial mask cap must be in [0,1/2]")
    common={mask:Fraction(w,witness.denominator)
            for mask,w in witness.weights.items() if w}
    completed=[]
    for original in (initial.q0,initial.q1):
        q={mask:Fraction(w,initial.denominator) for mask,w in original.items()
           if w}
        completed.append(xor_convolve_masks(m,q,common))
    c0,c1=census(pair.flat),census(pair.other)
    a=convolve_clean(m,c0,completed[0])
    b=convolve_clean(m,c1,completed[1])
    if a!=b:
        raise AssertionError("completed full observation distributions differ")
    actual=max(mask_marginals(m,completed[0])+
               mask_marginals(m,completed[1]))
    bound=eta+r*(1-2*eta)
    if actual>bound:
        raise AssertionError("completed marginal exceeds universal XOR bound")
    return PostprocessorReceipt(
        discrepancy_support=support,optimal_extra_flip=r,
        completed_max_flip=actual,uniform_completion_upper=bound,
        checked_dual_inequalities=1<<m,complete_laws_equal=True,
    )


def singleton_union_bound(support:tuple[int,...])->Fraction:
    """Necessary cap from the smallest residual Fourier subset."""
    if not support:
        return Fraction(0)
    return max(Fraction(1,2*s.bit_count()) for s in support)


def support_lp_metadata(m:int,support:tuple[int,...])->dict[str,int]:
    """Exact full finite LP dimensions, independent of any solver."""
    support=_validate_support(m,support)
    return {
        "variables":(1<<m)+1, "normalization_and_fourier_rows":1+len(support),
        "marginal_inequality_rows":m,
        "dual_mask_inequalities":1<<m,
    }



@dataclass(frozen=True)
class SupportLP:
    """Exact rational standard-form LP for a frozen residual Fourier support."""
    m: int
    support: tuple[int, ...]
    equalities: tuple[tuple[Fraction, ...], ...]
    equality_rhs: tuple[Fraction, ...]
    inequalities: tuple[tuple[Fraction, ...], ...]
    inequality_rhs: tuple[Fraction, ...]
    objective: tuple[Fraction, ...]


def build_support_lp(
    m:int,support:tuple[int,...],*,max_mask_states:int=256
)->SupportLP:
    """Expose exact matrix to optional LP discovery software.

    Variable order is R_mask for mask 0..2^m-1 and final variable r.
    There are 2^m+1 variables, 1+|D| equality rows and m marginal rows.
    CI always verifies returned witnesses independently with exact Q.
    """
    support=_validate_support(m,support)
    n=1<<m
    if max_mask_states<1 or n>max_mask_states:
        raise ValueError("eager mask matrix exceeds caller's memory cap")
    eq=[tuple(Fraction(1) for _ in range(n))+(Fraction(0),)]
    eq.extend(tuple(Fraction(-1 if (mask&S).bit_count()%2 else 1)
                    for mask in range(n))+(Fraction(0),)
              for S in support)
    inequalities=tuple(
        tuple(Fraction(1 if mask&(1<<i) else 0)
              for mask in range(n))+(Fraction(-1),)
        for i in range(m)
    )
    return SupportLP(
        m,support,tuple(eq),
        (Fraction(1),)+(Fraction(0),)*len(support),
        inequalities,(Fraction(0),)*m,
        (Fraction(0),)*n+(Fraction(1),)
    )


def check_support_lp_matrix(
    lp:SupportLP,witness:PostprocessorPrimal,r:Fraction
)->bool:
    """Independent direct-matrix feasibility check of an exact primal."""
    if lp.m>12 or len(lp.objective)!=(1<<lp.m)+1:
        raise ValueError("bad matrix dimensions")
    if witness.denominator<=0:
        raise ValueError("invalid witness denominator")
    values=tuple(Fraction(witness.weights.get(i,0),witness.denominator)
                 for i in range(1<<lp.m))+(Fraction(r),)
    if any(v<0 for v in values):
        return False
    return (
        all(sum((x*y for x,y in zip(row,values)),Fraction(0))==rhs
            for row,rhs in zip(lp.equalities,lp.equality_rhs))
        and all(sum((x*y for x,y in zip(row,values)),Fraction(0))<=rhs
                for row,rhs in zip(lp.inequalities,lp.inequality_rhs))
    )
