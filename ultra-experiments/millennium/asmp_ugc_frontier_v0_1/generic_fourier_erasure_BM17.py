"""BM-17: generic exact Fourier-erasure LP certificate checker.

For two gain connections on the SAME ordered graph, generate their
Boolean satisfaction pattern census under fresh uniform vertex labels.
The adversary chooses hypothesis-aware correlated XOR masks Q0/Q1
independently of the current clean pattern, subject to a common per-edge
flip cap. For degree d in [0,m], require equal masked Walsh coefficients
on ALL selected edge subsets S with |S|<=d.

A rational primal witness and a rational dual lower-bound witness certify
the exact optimal eta_d, without using a numerical solver. The finite
optimization has 2*2^m+1 primal variables; the certificate verifier is
exponential in m, with tests deliberately restricted to small graphs.
This is the complete LP, not the BM-16 individual-coefficient oracle.

Primal:
  hatP0(S) hatQ0(S) = hatP1(S) hatQ1(S), |S|<=d;
  Qh>=0, sum Qh=1, E_Qh[mask bit i]<=eta.
Dual:
  y_S free for each nonempty queried S, y_norm0,y_norm1 free,
  z_h,i<=0, -sum(z)=1;
  y_norm_h + (-1)^h sum_S y_S hatP_h(S) chi_S(mask)
            + sum_{i:mask_i=1} z_h,i <=0 for all mask,h.
Then eta_d >= y_norm0+y_norm1. Equality with a primal witness
proves the exact optimum using integer/Fraction operations.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

try:
    from .finite_seed import Game
except ImportError:
    from finite_seed import Game


@dataclass(frozen=True)
class Pair:
    flat: Game
    other: Game

    def __post_init__(self):
        if (self.flat.vertices != self.other.vertices or
            self.flat.bits != self.other.bits or
            tuple((u,v) for u,v,_ in self.flat.edges) !=
            tuple((u,v) for u,v,_ in self.other.edges)):
            raise ValueError("same graph, ordered edge occurrences and alphabet required")

    @property
    def m(self) -> int:
        return len(self.flat.edges)

    @property
    def mask_count(self) -> int:
        return 1 << self.m

    @property
    def q(self) -> int:
        return self.flat.q


@dataclass(frozen=True)
class Primal:
    denominator: int
    q0: dict[int,int]
    q1: dict[int,int]
    eta: Fraction


@dataclass(frozen=True)
class Dual:
    walsh_denominator: int
    walsh_numerators: dict[int,int]
    normalization_numerators: tuple[int,int]
    marginal_denominator: int
    marginal_numerators: tuple[int,...]


@dataclass(frozen=True)
class ProofReceipt:
    degree: int
    optimum: Fraction
    primal_valid: bool
    dual_valid: bool
    full_output_equal: bool
    walsh_terms: int
    checked_mask_inequalities: int


def census(g: Game) -> tuple[int,...]:
    """Independent exact vertex-label enumeration."""
    if len(g.edges)>12:
        raise ValueError("seed census supports at most 12 edge occurrences")
    out=[0]*(1<<len(g.edges))
    for labels in product(range(g.q),repeat=g.vertices):
        mask=sum(1<<i for i,(u,v,s) in enumerate(g.edges)
                 if (labels[u]^labels[v])==s)
        out[mask]+=1
    if sum(out)!=g.q**g.vertices:
        raise AssertionError("census mass mismatch")
    return tuple(out)


def signed_walsh(counts: tuple[int,...],subset: int) -> Fraction:
    """Normalized Walsh coefficient, with indicator bit=1 for satisfaction."""
    n=len(counts)
    if n<1 or n&(n-1) or not 0<=subset<n or sum(counts)<=0:
        raise ValueError("valid positive-mass Boolean census required")
    return Fraction(
        sum(((-1 if (x&subset).bit_count()%2 else 1)*weight
             for x,weight in enumerate(counts))),
        sum(counts),
    )


def queried_subsets(m:int,degree:int)->tuple[int,...]:
    if m<0 or not 0<=degree<=m:
        raise ValueError("Fourier degree outside graph edge count")
    return tuple(s for s in range(1,1<<m) if s.bit_count()<=degree)


def mask_walsh(weights:dict[int,int],denominator:int,S:int)->Fraction:
    return Fraction(sum(
        (-(w) if (mask&S).bit_count()%2 else w
         for mask,w in weights.items())),denominator)


def mask_marginals(weights:dict[int,int],denominator:int,m:int):
    return tuple(Fraction(
        sum(w for mask,w in weights.items() if mask&(1<<i)),
        denominator,
    ) for i in range(m))


def _check_distribution(weights:dict[int,int],D:int,m:int)->None:
    if D<=0 or sum(weights.values())!=D or any(
        not 0<=mask<(1<<m) or not isinstance(w,int) or w<0
        for mask,w in weights.items()
    ):
        raise ValueError("invalid integer mask distribution")


def output_counts(counts:tuple[int,...],weights:dict[int,int])->tuple[int,...]:
    if any(not 0<=mask<len(counts) for mask in weights):
        raise ValueError("mask index outside observation space")
    return tuple(
        sum(counts[y^mask]*w for mask,w in weights.items())
        for y in range(len(counts))
    )


def check_primal(
    pair:Pair,degree:int,witness:Primal,
    *,counts:tuple[tuple[int,...],tuple[int,...]]|None=None,
)->bool:
    """Verify complete degree-d Fourier equality and per-bit mask constraints."""
    subsets=queried_subsets(pair.m,degree)
    _check_distribution(witness.q0,witness.denominator,pair.m)
    _check_distribution(witness.q1,witness.denominator,pair.m)
    eta=Fraction(witness.eta)
    if not 0<=eta<=1:
        raise ValueError("invalid common per-bit mask allowance")
    if any(x>eta for weights in (witness.q0,witness.q1)
           for x in mask_marginals(weights,witness.denominator,pair.m)):
        raise AssertionError("primal mask marginal exceeds eta")
    c0,c1=counts if counts is not None else (census(pair.flat),census(pair.other))
    for S in subsets:
        lhs=signed_walsh(c0,S)*mask_walsh(witness.q0,witness.denominator,S)
        rhs=signed_walsh(c1,S)*mask_walsh(witness.q1,witness.denominator,S)
        if lhs!=rhs:
            raise AssertionError(f"degree-{degree} primal Fourier mismatch S={S}")
    return True


def check_dual(
    pair:Pair,degree:int,proof:Dual,
    *,counts:tuple[tuple[int,...],tuple[int,...]]|None=None,
)->Fraction:
    """Exact weak-duality feasibility over every mask atom and both worlds."""
    subsets=set(queried_subsets(pair.m,degree))
    if proof.walsh_denominator<1 or proof.marginal_denominator<1:
        raise ValueError("positive rational dual denominators required")
    if any(S not in subsets for S in proof.walsh_numerators):
        raise ValueError("dual Fourier support outside registered degree")
    if len(proof.normalization_numerators)!=2 or len(
        proof.marginal_numerators
    )!=2*pair.m:
        raise ValueError("dual normalization/marginal dimensions incorrect")
    marg=tuple(Fraction(v,proof.marginal_denominator)
               for v in proof.marginal_numerators)
    if any(v>0 for v in marg) or -sum(marg,Fraction(0))!=1:
        raise AssertionError("invalid dual marginal sign or eta normalization")
    norms=tuple(Fraction(v,proof.walsh_denominator)
                for v in proof.normalization_numerators)
    coefficients={S:Fraction(v,proof.walsh_denominator)
                  for S,v in proof.walsh_numerators.items() if v}
    c0,c1=counts if counts is not None else (census(pair.flat),census(pair.other))
    hat0={S:signed_walsh(c0,S) for S in coefficients}
    hat1={S:signed_walsh(c1,S) for S in coefficients}
    for h in (0,1):
        for mask in range(pair.mask_count):
            slack=norms[h]+sum((
                (1 if h==0 else -1)*v*(hat0[S] if h==0 else hat1[S])*
                (-1 if (S&mask).bit_count()%2 else 1)
                for S,v in coefficients.items()
            ),Fraction(0))
            slack+=sum(
                (marg[h*pair.m+i] for i in range(pair.m)
                 if mask&(1<<i)),Fraction(0)
            )
            if slack>0:
                raise AssertionError(
                    f"dual mask inequality violated (h={h}, mask={mask}): {slack}"
                )
    return sum(norms,Fraction(0))


def certify(pair:Pair,degree:int,primal:Primal,dual:Dual)->ProofReceipt:
    """Exact matching upper and lower certificates yield an LP optimum."""
    counts=(census(pair.flat),census(pair.other))
    check_primal(pair,degree,primal,counts=counts)
    lower=check_dual(pair,degree,dual,counts=counts)
    upper=Fraction(primal.eta)
    if upper!=lower:
        raise AssertionError(f"unmatched primal/dual bounds {upper} vs {lower}")
    full_eq=(output_counts(counts[0],primal.q0)==
             output_counts(counts[1],primal.q1))
    if degree==pair.m and not full_eq:
        raise AssertionError("full Fourier erasure has different complete laws")
    return ProofReceipt(
        degree=degree,optimum=upper,primal_valid=True,dual_valid=True,
        full_output_equal=full_eq,
        walsh_terms=sum(bool(v) for v in dual.walsh_numerators.values()),
        checked_mask_inequalities=2*pair.mask_count,
    )
