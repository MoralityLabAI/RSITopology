"""BM-32: finite-observation robust signed dyadic equation.

BM-29's exact infinite signed parity relation is
  D=(2I+7S_*)nu0-(I+8S_*)nu1 = 0,
  S(u,w)=(u,w/2).
Given INFINITE exchangeable ordinary mask-pair laws with distinguished
exceptional-pair masks under both worlds, the observed k-ordinary-plus-
special output laws may differ by total variation epsilon.

The ordinary observed pair i has characters X_i,Y_i in {+1,-1}.
Conditional on the ordinary directing mask pair M=(u,w) and
the clean terminal regime, these are iid across paths with
    E X_i=E Y_i=3u/4,
    E X_i Y_i = v, with v=w or w/2.
Estimate
    Uhat=clip[(2/(3k)) sum_i(X_i+Y_i), -1,1],
    What=(1/k) sum_i X_i Y_i.
Conditional L1 expected error <= 7/(3 sqrt(k)) by Cauchy-Schwarz.

For any bounded f:[-1,1]^2->R with sup|f|<=B and Lipschitz
constant L in L1 distance, use the observable
    g=chi_exceptional_output * f(Uhat,What).
Then
  abs(integral f dD) <=32 B epsilon + 224 L/(3 sqrt(k)).
This is a rigorous BL-norm approximate dyadic equation, not an
erasure-threshold convergence-rate inequality.

For an EXACTLY equalizing finite n-path pair, BM-31 gives an infinite
empirical replacement extension with k-window output epsilon <= 2e,
where e^2<=k(k-1)/[2(n-1)(n-k+1)].
Consequently
  abs(integral f dD)
    <=64 B sqrt(e²) + 224 L/(3 sqrt(k)),
with an entirely rational, certified bound on its SQUARE via
  bound² <=2*[4096 B² e² + (224L/3)²/k].
Choosing k=floor(n^(2/3)) makes this O(n^(-1/3)) in BL norm.

The implementation checks exact rational finite probability identities
and the inequality WITHOUT evaluating floating-point square roots.
It does not claim a scalar eta_n-to-5/52 rate.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable

try:
    from .finite_empirical_extension_BM31 import (
        empirical_joint_law, with_replacement_window,
        finite_alphabet_tv_squared_bound,entropy_growing_window_bound,
        total_variation,
    )
    from .replication_uniform_upper_BM27 import (
        exact_clean_law,xor_convolve,
    )
except ImportError:
    from finite_empirical_extension_BM31 import (
        empirical_joint_law, with_replacement_window,
        finite_alphabet_tv_squared_bound,entropy_growing_window_bound,
        total_variation,
    )
    from replication_uniform_upper_BM27 import (
        exact_clean_law,xor_convolve,
    )


@dataclass(frozen=True)
class LipschitzTest:
    name:str
    bound:Fraction
    lipschitz:Fraction
    function:Callable[[Fraction,Fraction],Fraction]

    def evaluate(self,u:Fraction,w:Fraction)->Fraction:
        u,w=Fraction(u),Fraction(w)
        if not -1<=u<=1 or not -1<=w<=1:
            raise ValueError("test functions expect Fourier coordinates in [-1,1]")
        value=Fraction(self.function(u,w))
        if abs(value)>self.bound:
            raise AssertionError("declared test function sup norm violated")
        return value


TESTS=(
    LipschitzTest("u",Fraction(1),Fraction(1),lambda u,w:u),
    LipschitzTest("w",Fraction(1),Fraction(1),lambda u,w:w),
    LipschitzTest("uw",Fraction(1),Fraction(1),lambda u,w:u*w),
    LipschitzTest("w²",Fraction(1),Fraction(2),lambda u,w:w*w),
    LipschitzTest("u_plus_w_clipped",Fraction(1),Fraction(1),
                  lambda u,w:max(Fraction(-1),min(Fraction(1),u+w))),
)


def _validate_joint(n:int,joint:dict)->None:
    if not isinstance(n,int) or n<1:
        raise ValueError("positive ordinary-path count required")
    if any(
        not isinstance(hist,tuple) or len(hist)!=3 or
        any(not isinstance(v,int) or v<0 for v in hist) or
        sum(hist)!=n or not isinstance(special,int) or
        not 0<=special<=3 or Fraction(p)<0
        for (hist,special),p in joint.items()
    ) or sum((Fraction(p) for p in joint.values()),Fraction(0))!=1:
        raise ValueError("normalized joint empirical mask law required")


def _coordinates(n:int,hist:tuple[int,int,int])->tuple[Fraction,Fraction]:
    """One-bit and full-pair parity Fourier coordinates of ordinary noise."""
    return Fraction(hist[0]-hist[2],n),Fraction(n-2*hist[1],n)


def dyadic_residual(n:int,joint0:dict,joint1:dict,test:LipschitzTest
                    )->Fraction:
    """Exact integral of test against BM-29 signed dyadic defect measure."""
    for j in (joint0,joint1):
        _validate_joint(n,j)
    result=Fraction(0)
    for h,joint in enumerate((joint0,joint1)):
        for (hist,special),weight in joint.items():
            u,w=_coordinates(n,hist)
            nu=Fraction(weight)*(-1 if special.bit_count()%2 else 1)
            if h==0:
                result+=nu*(2*test.evaluate(u,w)+
                            7*test.evaluate(u,w/2))
            else:
                result-=nu*(test.evaluate(u,w)+
                            8*test.evaluate(u,w/2))
    return result


def empirical_observable(mask:int,k:int,test:LipschitzTest)->Fraction:
    """Special output parity times test of two empirical Fourier moments."""
    if not isinstance(k,int) or k<1 or not (
        isinstance(mask,int) and 0<=mask<1<<(2*k+2)
    ):
        raise ValueError("mask outside k ordinary plus exceptional observation")
    total_first=0
    total_pair=0
    for i in range(k):
        x=1 if not mask&(1<<(2*i)) else -1
        y=1 if not mask&(1<<(2*i+1)) else -1
        total_first+=x+y
        total_pair+=x*y
    u=Fraction(2*total_first,3*k)
    u=max(Fraction(-1),min(Fraction(1),u))
    w=Fraction(total_pair,k)
    exceptional=(mask>>(2*k))&3
    parity=-1 if exceptional.bit_count()%2 else 1
    return parity*test.evaluate(u,w)


def observable_expectation(k:int,law:dict[int,Fraction],
                           test:LipschitzTest)->Fraction:
    if not isinstance(k,int) or k<1 or sum(law.values(),Fraction(0))!=1:
        raise ValueError("normalized complete observed law required")
    return sum(
        (Fraction(weight)*empirical_observable(mask,k,test)
         for mask,weight in law.items()),Fraction(0)
    )


@dataclass(frozen=True)
class RobustDyadicReceipt:
    n:int
    k:int
    test_name:str
    signed_dyadic_defect:Fraction
    output_total_variation:Fraction
    observed_statistic_difference:Fraction
    bounded_sup_component:Fraction
    sampling_component_squared:Fraction
    finite_n_bound_squared:Fraction
    finite_n_bound_verified:bool


def robust_sampling_term_squared(k:int,L:Fraction)->Fraction:
    if not isinstance(k,int) or k<1 or Fraction(L)<0:
        raise ValueError("positive k and nonnegative Lipschitz constant")
    return Fraction(224,3)**2 * Fraction(L)**2/k


def assert_robust_dyadic_inequality(
    residual:Fraction,epsilon:Fraction,k:int,
    *,bound:Fraction=1,lipschitz:Fraction=1
)->bool:
    """Exact test of |D(f)|<=32B eps+(224L/3)/sqrt(k), no square roots."""
    epsilon=Fraction(epsilon)
    B,L=Fraction(bound),Fraction(lipschitz)
    if epsilon<0 or B<0 or L<0:
        raise ValueError("TV, supremum bound and Lipschitz constant nonnegative")
    deterministic=32*B*epsilon
    excess=abs(Fraction(residual))-deterministic
    if excess>0 and excess*excess>robust_sampling_term_squared(k,L):
        raise AssertionError("finite-window dyadic signed-measure bound violated")
    return True


def finite_n_squared_bound(n:int,k:int,*,bound:Fraction=1,
                           lipschitz:Fraction=1)->Fraction:
    """Rational squared upper for the FULL signed dyadic defect |D(f)|.

    With e² from BM-31, |D(f)|<=64B sqrt(e²)+(224L/3)/sqrt(k).
    By (a+b)²<=2a²+2b² we certify:
      |D(f)|² <=2*(4096 B² e²+(224L/3)²/k).
    """
    if Fraction(bound)<0 or Fraction(lipschitz)<0:
        raise ValueError("negative test norm")
    e2=finite_alphabet_tv_squared_bound(n,k)
    return (2*4096*Fraction(bound)**2*e2+
            2*robust_sampling_term_squared(k,Fraction(lipschitz)))


def empirical_extended_outputs(n:int,k:int,j0:dict,j1:dict):
    """Both exact output windows of the BM-31 with-replacement extensions."""
    _validate_joint(n,j0)
    _validate_joint(n,j1)
    if k>n or 2*k+2>12:
        raise ValueError("small exact output control limited to k<=5")
    outputs=[]
    for h,joint in enumerate((j0,j1)):
        masks=with_replacement_window(n,k,joint)
        outputs.append(xor_convolve(exact_clean_law(k,h),masks))
    return tuple(outputs)


def certify_finite_dyadic_window(
    n:int,k:int,mask0:dict[int,Fraction],mask1:dict[int,Fraction],
    test:LipschitzTest
)->RobustDyadicReceipt:
    """Two independent exact finite checks of the observable error bound."""
    if not 1<=k<=n<=5:
        raise ValueError("explicit full-mask certificate restricted to n<=5")
    j0=empirical_joint_law(n,mask0)
    j1=empirical_joint_law(n,mask1)
    output0,output1=empirical_extended_outputs(n,k,j0,j1)
    epsilon=total_variation(output0,output1)
    signed=dyadic_residual(n,j0,j1,test)
    observed=(observable_expectation(k,output0,test)-
              observable_expectation(k,output1,test))
    if abs(observed)>2*test.bound*epsilon:
        raise AssertionError("observable exceeds total variation inequality")
    assert_robust_dyadic_inequality(
        signed,epsilon,k,bound=test.bound,lipschitz=test.lipschitz
    )
    finite_bound=finite_n_squared_bound(
        n,k,bound=test.bound,lipschitz=test.lipschitz
    )
    if signed*signed>finite_bound:
        raise AssertionError("finite-n signed residual square bound violated")
    return RobustDyadicReceipt(
        n,k,test.name,signed,epsilon,observed,
        32*test.bound*epsilon,
        robust_sampling_term_squared(k,test.lipschitz),
        finite_bound,True,
    )


def growing_horizon_rate(n:int,*,bound:Fraction=1,
                         lipschitz:Fraction=1)->dict[str,object]:
    """No big state allocations; k=floor(n^2/3) gives O(n^-1/3) in BL."""
    info=entropy_growing_window_bound(n)
    k=info["k"]
    return {
        "ordinary_paths":n,
        "window_ordinary_paths":k,
        "bounded_lipschitz_defect_squared_upper":
            finite_n_squared_bound(n,k,bound=bound,lipschitz=lipschitz),
        "rate":"O(n^(-1/3)) for fixed BL test norms",
        "explicit_threshold_rate_claimed":False,
        "external_numeric_solver_used":False,
    }
