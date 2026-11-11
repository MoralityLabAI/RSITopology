"""BM-35: exact degree-five polynomial dual proves q8 eta_n gap O(1/n).

For the repeated q8 two-edge-path game, define the physical symmetric
ordinary-mask Fourier domain
    -1<=u<=1, 2*abs(u)-1<=w<=1.
The explicit degree-five polynomial f is given by 15 nonzero rational
monomial coefficients, all with the common exact denominator below.

Its pointwise dual constraints are:
  c=16*(1-u)/5,
  c-1+f(u,w)-f(u,w/2) >=0,
  c+1-f(u,w)+f(u,w/2) >=0,
  1+c-3*f(u,w)-15*f(u,w/2) >=0,
  1+c+3*f(u,w)+15*f(u,w/2) >=0.

The checker maps the physical wedge to 40 unit-square patches and
expands ALL FOUR slack polynomials in the degree-(5,5) Bernstein basis.
Every one of the resulting 5,760 coefficients is a nonnegative
Fraction (72 are exactly zero). Bernstein basis functions are
nonnegative and sum to one, so the check certifies each inequality
for EVERY real physical (u,w), not merely a finite evaluation grid.

Unlike the earlier piecewise-BILINEAR BM33 potential, this globally
polynomial f has bounded second derivatives on the full observed
unclipped-statistic rectangle [-4/3,4/3] x [-1,1].
The independent BM34 conditional moment table establishes
  clean matched: Var(Ubar)<=7/(9n), Var(Wbar)=0;
  clean unmatched: Var(Ubar)<=4/(9n), Var(Wbar)<=3/(4n).

Second-order Taylor with mean-zero fluctuations gives an expected
per-world potential bias <= C/n, where
 C=max(7*Muu/18, 2*Muu/9+3*Muw/5+3*Mww/8),
 and |partial_uu f|<=Muu, |partial_uw f|<=Muw,
     |partial_ww f|<=Mww.
The cross term uses E|dU dW|<=sqrt(1/3)/n<=3/(5n).
Thus |D[f]|<=32*C/n. The BM33 robust overlap dual yields
  0 <= 5/52-eta_n(8,2) <=(40*C/13)/n < 348/n
for EVERY n>=1, with arbitrary hypothesis-aware, correlated XOR masks
independent of the current clean sample.

The only discovery step used a numerical LP to find a coefficient
candidate. Its exact verification and finite-rate theorem use the
Python standard library only. No numerical solver or polynomial
optimization backend is trusted by the checker.

This is a stylized finite statistical channel result. It is not a
live-agent alignment/oversight guarantee or a UGC theorem.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb

try:
    from .infinite_replication_rigidity_BM29 import LIMIT
except ImportError:
    from infinite_replication_rigidity_BM29 import LIMIT


DEGREE=5
DENOMINATOR=10618397520826478241112875
COEFFICIENT_NUMERATORS={
    (0,0):-1076736653654158041110193,
    (0,2):18464882583625017233477460,
    (0,3):6486402490362451683275616,
    (0,4):-35835488780122577036523072,
    (0,5):-6593003805718016241762816,
    (1,0):-2587870994787646052289222,
    (1,1):-9876877388907284199697128,
    (1,2):37702214153042684718671136,
    (2,1):-13545651178393693820786304,
    (2,2):22915113666863066818300544,
    (2,3):2839140676754611310347776,
    (3,0):16624936351390026791749152,
    (3,1):-63356923913487888775100544,
    (3,2):35359145140666198863460864,
    (4,0):1226259363776323810894848,
}
U_BREAKS=(
    Fraction(-1),Fraction(-1,2),Fraction(0),Fraction(1,4),
    Fraction(1,2),Fraction(5,8),Fraction(11,16),Fraction(3,4),
    Fraction(13,16),Fraction(7,8),Fraction(1),
)
Y_BREAKS=(
    Fraction(0),Fraction(1,4),Fraction(1,2),Fraction(3,4),
    Fraction(1),
)
ONE={(0,0):Fraction(1)}


def polynomial(u:Fraction,w:Fraction, *, coefficients=None)->Fraction:
    """Exact smooth real dual, evaluated by a direct monomial sum."""
    u,w=Fraction(u),Fraction(w)
    terms=COEFFICIENT_NUMERATORS if coefficients is None else coefficients
    return sum((Fraction(a,DENOMINATOR)*u**i*w**j
                for (i,j),a in terms.items()),Fraction(0))


def physical_pair(u:Fraction,w:Fraction)->bool:
    u,w=Fraction(u),Fraction(w)
    return -1<=u<=1 and 2*abs(u)-1<=w<=1


def pointwise_slacks(u:Fraction,w:Fraction,
                     *,coefficients=None)->tuple[Fraction,...]:
    """Four rational inequalities on the entire physical Fourier domain."""
    u,w=Fraction(u),Fraction(w)
    if not physical_pair(u,w):
        raise ValueError("symmetric two-bit Fourier pair must be physical")
    a=polynomial(u,w,coefficients=coefficients)
    b=polynomial(u,w/2,coefficients=coefficients)
    c=Fraction(16,5)*(1-u)
    return c-1+a-b,c+1-a+b,1+c-3*a-15*b,1+c+3*a+15*b


def _scale(p:dict,v:Fraction)->dict:
    return {k:a*v for k,a in p.items() if a*v}


def _add(*polynomials:dict)->dict:
    result={}
    for p in polynomials:
        for k,a in p.items():
            result[k]=result.get(k,Fraction(0))+a
    return {k:a for k,a in result.items() if a}


def _multiply(a:dict,b:dict)->dict:
    result={}
    for (i,j),x in a.items():
        for (k,l),y in b.items():
            key=(i+k,j+l)
            result[key]=result.get(key,Fraction(0))+x*y
    return {k:x for k,x in result.items() if x}


def _powers(p:dict,n:int)->list[dict]:
    result=[ONE]
    for _ in range(n):
        result.append(_multiply(result[-1],p))
    return result


def _bernstein_coefficients(p:dict,degree:int=DEGREE)->tuple[Fraction,...]:
    """Exact power-to-Bernstein transform on the closed unit square.

    x^i = sum_{a=i}^d [binom(a,i)/binom(d,i)] B_{a,d}(x)
    and likewise for y^j. A bidegree-(d,d) Bernstein expansion
    with nonnegative coefficients certifies p(x,y)>=0 everywhere
    on [0,1]^2.
    """
    if any(i>degree or j>degree or i<0 or j<0
           for i,j in p):
        raise ValueError("slack polynomial exceeds Bernstein bidegree")
    return tuple(
        sum((
            value*Fraction(comb(a,i),comb(degree,i))*
            Fraction(comb(b,j),comb(degree,j))
            for (i,j),value in p.items() if i<=a and j<=b
        ),Fraction(0))
        for a in range(degree+1) for b in range(degree+1)
    )


@dataclass(frozen=True)
class BernsteinProof:
    cells:int
    inequalities:int
    coefficients_checked:int
    zero_coefficients:int
    minimum_coefficient:Fraction
    global_nonnegative:bool


def verify_bernstein_certificate(*,coefficients=None)->BernsteinProof:
    """Validate all 5,760 coefficients, including physical wedge edges.

    Split u at -1,-1/2,0,1/4,1/2,5/8,11/16,3/4,13/16,7/8,1.
    On each u interval parameterize the full physical w range by
       w=(2*abs(u)-1)+y*(2-2*abs(u)),
    partitioning y into the four intervals of Y_BREAKS.
    Both coordinate substitutions are bilinear/affine in local
    unit-square (x,y). Every slack retains bidegree at most (5,5).
    """
    terms=COEFFICIENT_NUMERATORS if coefficients is None else coefficients
    if any(i<0 or j<0 or i+j>DEGREE
           for (i,j) in terms):
        raise ValueError("dual candidate must have total degree <=5")
    checked=0
    zero=0
    minimum=None
    cells=0
    for ua,ub in zip(U_BREAKS[:-1],U_BREAKS[1:]):
        sign=1 if ua>=0 else -1
        u=_add({(0,0):ua},{(1,0):ub-ua})
        low=_add(_scale(u,2*sign),_scale(ONE,-1))
        for ya,yb in zip(Y_BREAKS[:-1],Y_BREAKS[1:]):
            cells+=1
            y=_add({(0,0):ya},{(0,1):yb-ya})
            w=_add(low,_multiply(_add(ONE,_scale(low,-1)),y))
            up=_powers(u,DEGREE)
            wp=_powers(w,DEGREE)
            f=_add(*(
                _scale(_multiply(up[i],wp[j]),Fraction(a,DENOMINATOR))
                for (i,j),a in terms.items()
            ))
            fs=_add(*(
                _scale(_multiply(up[i],wp[j]),
                       Fraction(a,DENOMINATOR*2**j))
                for (i,j),a in terms.items()
            ))
            c=_scale(_add(ONE,_scale(u,-1)),Fraction(16,5))
            slacks=(
                _add(c,_scale(ONE,-1),f,_scale(fs,-1)),
                _add(c,ONE,_scale(f,-1),fs),
                _add(ONE,c,_scale(f,-3),_scale(fs,-15)),
                _add(ONE,c,_scale(f,3),_scale(fs,15)),
            )
            for which,slack in enumerate(slacks):
                for value in _bernstein_coefficients(slack):
                    checked+=1
                    if value<0:
                        raise AssertionError(
                            f"nonphysical dual cell u={ua},{ub}, "
                            f"y={ya},{yb}, constraint={which}, value={value}"
                        )
                    if value==0:
                        zero+=1
                    if minimum is None or value<minimum:
                        minimum=value
    if (cells,checked)!=(40,5760):
        raise AssertionError("physical-domain coverage incomplete")
    return BernsteinProof(
        cells,4,checked,zero,minimum,True,
    )


@dataclass(frozen=True)
class SmoothRate:
    hessian_uu:Fraction
    hessian_uw:Fraction
    hessian_ww:Fraction
    matched_bias_coefficient:Fraction
    unmatched_bias_coefficient:Fraction
    worst_one_world_bias_coefficient:Fraction
    sharp_computable_rate_coefficient:Fraction
    simple_integer_rate_coefficient:int


def smooth_hessian_rate()->SmoothRate:
    """Exact second-derivative envelope on [-4/3,4/3] x [-1,1]."""
    U=Fraction(4,3)
    terms={
        ij:Fraction(a,DENOMINATOR)
        for ij,a in COEFFICIENT_NUMERATORS.items()
    }
    Muu=sum((
        abs(a)*i*(i-1)*U**(i-2)
        for (i,j),a in terms.items() if i>=2
    ),Fraction(0))
    Muw=sum((
        abs(a)*i*j*U**(i-1)
        for (i,j),a in terms.items() if i>=1 and j>=1
    ),Fraction(0))
    Mww=sum((
        abs(a)*j*(j-1)*U**i
        for (i,j),a in terms.items() if j>=2
    ),Fraction(0))
    # Matched A: VarU<=7/(9n), VarW=0.
    a=Fraction(7,18)*Muu
    # Unmatched B: VarU<=4/(9n), VarW<=3/(4n).
    # Cauchy gives E|dU*dW|<=sqrt(1/3)/n<=3/(5n).
    b=Fraction(2,9)*Muu+Fraction(3,5)*Muw+Fraction(3,8)*Mww
    C=max(a,b)
    K=Fraction(40,13)*C
    if K>=348:
        raise AssertionError("claimed 348/n constant not certified")
    return SmoothRate(Muu,Muw,Mww,a,b,C,K,348)


def scalar_gap_squared_bound(n:int)->Fraction:
    """Rational finite-n theorem: (5/52-eta_n)^2 <=(348/n)^2."""
    if not isinstance(n,int) or n<1:
        raise ValueError("positive integer ordinary-path count required")
    return Fraction(348**2,n**2)


def _unclipped_statistic(observed:int,n:int)->tuple[Fraction,Fraction,int]:
    if (not isinstance(n,int) or n<1 or
        not isinstance(observed,int) or
        not 0<=observed<1<<(2*n+2)):
        raise ValueError("invalid complete observed Boolean report")
    ordinary_sum=0
    parities=0
    for i in range(n):
        pair=(observed>>(2*i))&3
        ordinary_sum+=2-2*pair.bit_count()
        parities+=(-1 if pair.bit_count()%2 else 1)
    U=Fraction(2*ordinary_sum,3*n)
    W=Fraction(parities,n)
    special=(observed>>(2*n))&3
    sign=-1 if special.bit_count()%2 else 1
    return U,W,sign


def observable(observed:int,n:int)->Fraction:
    """A bounded real polynomial statistic on the observed finite report."""
    u,w,s=_unclipped_statistic(observed,n)
    return s*polynomial(u,w)


@dataclass(frozen=True)
class FullWitnessProof:
    ordinary_paths:int
    reported_laws_equal:bool
    observed_expectation_gap:Fraction
    dyadic_defect:Fraction
    world_biases:tuple[Fraction,Fraction]
    ordinary_bit_cost:Fraction
    exceptional_bit_cost:Fraction
    finite_scalar_gap_bound_holds:bool


def verify_full_witness(
    n:int,q0:dict[int,Fraction],q1:dict[int,Fraction]
)->FullWitnessProof:
    """Independent direct-output and latent histogram signed dual regression.

    n<=4 for full enumeration. This verifies the same scalar argument
    against previously certified BM-25/BM-26/BM-27 legal mask pairs.
    """
    if not 1<=n<=4:
        raise ValueError("full table checks are bounded to n<=4")
    try:
        from .finite_empirical_extension_BM31 import (
            empirical_joint_law,expand_empirical_joint_law,directing_law,
        )
        from .replication_uniform_upper_BM27 import (
            exact_clean_law,xor_convolve,
        )
    except ImportError:
        from finite_empirical_extension_BM31 import (
            empirical_joint_law,expand_empirical_joint_law,directing_law,
        )
        from replication_uniform_upper_BM27 import (
            exact_clean_law,xor_convolve,
        )
    joint=tuple(empirical_joint_law(n,law) for law in (q0,q1))
    ordinary=tuple(directing_law(n,j) for j in joint)
    if ordinary[0]!=ordinary[1]:
        raise AssertionError("finite full eraser must preserve ordinary mask law")
    outputs=tuple(
        xor_convolve(
            exact_clean_law(n,h),
            expand_empirical_joint_law(n,joint[h])
        ) for h in (0,1)
    )
    if outputs[0]!=outputs[1]:
        raise AssertionError("candidate finite masks do not equalize outputs")
    obs=tuple(sum((p*observable(out,n)
                   for out,p in law.items()),Fraction(0))
              for law in outputs)
    if obs[0]!=obs[1]:
        raise AssertionError("full output observable mismatched across worlds")
    ideal=[]
    for h,j in enumerate(joint):
        val=Fraction(0)
        for (hist,z),mass in j.items():
            u=Fraction(hist[0]-hist[2],n)
            w=Fraction(hist[0]-hist[1]+hist[2],n)
            parity=-1 if z.bit_count()%2 else 1
            if h==0:
                target=(Fraction(1,8)*polynomial(u,w)+
                        Fraction(7,16)*polynomial(u,w/2))
            else:
                target=(Fraction(1,16)*polynomial(u,w)+
                        Fraction(1,2)*polynomial(u,w/2))
            val+=mass*parity*target
        ideal.append(val)
    D=16*(ideal[0]-ideal[1])
    bias=tuple(obs[i]-ideal[i] for i in (0,1))
    bound=smooth_hessian_rate().worst_one_world_bias_coefficient
    for b in bias:
        if n*abs(b)>bound:
            raise AssertionError("second-order finite bias certificate violated")
    if n*abs(D)>32*bound:
        raise AssertionError("finite dyadic defect certificate violated")
    mu=ordinary[0]
    co=sum((p*Fraction(h[1]+2*h[2],2*n)
            for h,p in mu.items()),Fraction(0))
    cs=sum((p*Fraction(z.bit_count(),2)
            for (hist,z),p in joint[0].items()),Fraction(0))
    if max(co,cs)>LIMIT:
        raise AssertionError("registered masks exceed BM27 known upper")
    if LIMIT-max(co,cs)>Fraction(348,n):
        raise AssertionError("scalar O(1/n) upper is violated")
    return FullWitnessProof(
        n,True,obs[0]-obs[1],D,bias,co,cs,True
    )


def theorem_receipt(n:int=10**9)->dict[str,object]:
    b=verify_bernstein_certificate()
    r=smooth_hessian_rate()
    return {
        "alphabet":"F2^3 / q=8",
        "ordinary_paths":n,
        "degree":DEGREE,
        "nonzero_monomial_terms":len(COEFFICIENT_NUMERATORS),
        "exact_bernstein_cells":b.cells,
        "pointwise_inequalities_per_cell":b.inequalities,
        "bernstein_coefficients_checked":b.coefficients_checked,
        "negative_bernstein_coefficients":0,
        "identically_zero_bernstein_coefficients":b.zero_coefficients,
        "new_scalar_gap":"0 <= 5/52-eta_n <= 348/n",
        "exact_rate_constant":str(r.sharp_computable_rate_coefficient),
        "simple_integer_constant":348,
        "sampled_paths":"all n",
        "finite_exchangeability_replacement_needed":False,
        "all_checks_fraction_only":True,
        "external_numeric_optimizer_trusted":False,
        "finite_n_rate_sharp_claimed":False,
    }
