"""BM-29: exact q8 infinite-replica masking limit via exchangeability.

Proved in INFINITE_REPLICATION_LIMIT_BM29.md:

    lim_{n->infty} eta_sym(n;q=8,L=2) = 5/52.

The argument uses
(1) exact finite-n rigidity of ordinary-mask marginals and ordinary
    + one exceptional-bit marginals, because the shared clean laws have
    strictly positive Walsh transforms;
(2) compactness and the classical de Finetti representation for
    infinitely exchangeable two-bit ordinary-mask sequences;
(3) a signed-measure parity relation across scales w and w/2, with
    w>=2u-1 for a physical exchangeable two-bit mask;
(4) a two-level dyadic overlap inequality
         integral min(dnu0,dnu1)
              <= (16/5) integral (1-u) dmu;
(5) the special-mask nonnegativity and shared special single-bit Fourier
    marginal, giving
         8 C_ordinary + 5 C_exceptional >= 5/4;
(6) BM-27's independent exact all-n attaining construction at 5/52.

The routine below checks all FINITE algebraic identities, the exact
two-level chain recurrence, its sharp equality case, small-n marginal
rigidity and the attained BM-27 branch mixture, using Fractions.

The infinite de Finetti compactness/disintegration and signed-measure
arguments are mathematical proofs in the accompanying note, not claims
of machine-verified measure theory. No numerical optimization is used.

This theorem assumes masks independent of the CURRENT clean input.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

try:
    from .replication_uniform_upper_BM27 import (
        PAIR_I, PAIR_A, PAIR_B, PAIR_E, PAIRS, COMPONENTS,
        UPPER_CAP, exact_mask_rate, verify_convolution_identity,
        theorem_upper,
    )
except ImportError:
    from replication_uniform_upper_BM27 import (
        PAIR_I, PAIR_A, PAIR_B, PAIR_E, PAIRS, COMPONENTS,
        UPPER_CAP, exact_mask_rate, verify_convolution_identity,
        theorem_upper,
    )


LIMIT=Fraction(5,52)
ORD_COEFFICIENT=8
SPECIAL_COEFFICIENT=5
WEIGHTED_BOUND=Fraction(5,4)
U_THRESHOLD=Fraction(11,16)


def pair_walsh(pair:tuple[Fraction,...])->tuple[Fraction,...]:
    """Independent four-state character transform (index order 00/10/01/11)."""
    if len(pair)!=4:
        raise ValueError("four two-bit masses required")
    return tuple(
        sum((Fraction(w)*(-1 if (x&S).bit_count()%2 else 1)
             for x,w in enumerate(pair)),Fraction(0))
        for S in range(4)
    )


def shared_clean_marginal_walsh(b:int,r:int,exception_bits:int=0)->Fraction:
    """All ordinary-edge Fourier characters are nonzero for q8.

    Ordinary S selects b edges from proper (single-edge) paths and
    both edges from r fully selected paths.
      What(S)=(3/4)^b [1+7*(1/2)^r]/8 >0.
    Adding zero or one exceptional edge multiplies this by (3/4)^j.
    This expression holds identically under both hypotheses.
    """
    if any(not isinstance(x,int) or x<0
           for x in (b,r,exception_bits)) or exception_bits>1:
        raise ValueError("nonnegative proper/full counts and <=1 special edge")
    return Fraction(3,4)**(b+exception_bits)*(
        1+7*Fraction(1,2)**r)/8


def ordinary_pair_mask_coordinates(pair:tuple[Fraction,...]
                                   )->tuple[Fraction,Fraction]:
    """Return symmetric one-bit u and pair-parity w of a physical mask."""
    p=tuple(Fraction(x) for x in pair)
    if len(p)!=4 or any(x<0 for x in p) or sum(p)!=1 or p[1]!=p[2]:
        raise ValueError("exchangeable physical two-bit mask law required")
    h=pair_walsh(p)
    if h[1]!=h[2]:
        raise AssertionError("ordinary pair mask symmetry lost")
    u,w=h[1],h[3]
    if w<2*u-1 or w>1:
        raise AssertionError("pair nonnegativity feasibility violated")
    return u,w


@dataclass(frozen=True)
class TwoLevelChain:
    """One dyadic chain in a fixed-u de Finetti fiber.

    The two feasible ordinary-mask parity values are high_w and
    high_w/2. Let c=nu0(high_w) signed, then the exact exceptional
    parity equation forces
        nu1(high)=2c, nu0(low)=8c, nu1(low)=7c.
    Densities are represented as signed MASSES, not probabilities.
    """
    u:Fraction
    high_w:Fraction
    mu_high:Fraction
    mu_low:Fraction
    c:Fraction

    @property
    def low_w(self)->Fraction:
        return self.high_w/2

    @property
    def signed_nu(self)->tuple[Fraction,Fraction,Fraction,Fraction]:
        c=self.c
        return c,2*c,8*c,7*c

    @property
    def ordinary_rate_mass(self)->Fraction:
        return (1-self.u)*(self.mu_high+self.mu_low)/2

    @property
    def overlap(self)->Fraction:
        n0h,n1h,n0l,n1l=self.signed_nu
        return min(n0h,n1h)+min(n0l,n1l)

    def check(self)->bool:
        u,w=self.u,self.high_w
        if not (U_THRESHOLD<u<=Fraction(3,4)
                and 2*u-1<=w/2<=Fraction(1,2)
                and Fraction(1,2)<w<=1):
            raise ValueError("high-u dyadic two-level feasibility required")
        if (self.mu_high<2*abs(self.c)
            or self.mu_low<8*abs(self.c)):
            raise ValueError("signed parity mass must be dominated by mu")
        a,b,c,d=self.signed_nu
        if not (b==2*a and 2*c+7*a==d+8*b and 7*c==8*d):
            raise AssertionError("dyadic signed parity equations violated")
        mass=self.mu_high+self.mu_low
        if self.overlap>Fraction(4,5)*mass:
            raise AssertionError("sharp two-level overlap bound failed")
        if self.overlap>Fraction(16,5)*(1-u)*mass:
            raise AssertionError("weighted ordinary marginal inequality failed")
        return True


def low_u_overlap_certificate(u:Fraction,mass:Fraction,
                              overlap:Fraction)->bool:
    """For u<=11/16, overlap<=mu is enough for the global dual."""
    u,mass,overlap=Fraction(u),Fraction(mass),Fraction(overlap)
    if u>U_THRESHOLD or mass<0 or overlap>mass:
        raise ValueError("low-u signed measure dominance conditions required")
    if overlap>Fraction(16,5)*(1-u)*mass:
        raise AssertionError("trivial low-u dual violates its bound")
    return True


def isolated_high_u_certificate(u:Fraction,
                                n0:Fraction,n1:Fraction)->bool:
    """For u>3/4, no w/2 state is physical: signed parity must vanish."""
    if Fraction(u)<=Fraction(3,4) or n0 or n1:
        raise ValueError("isolated high-u fiber must have nu0=nu1=0")
    return True


def weighted_limit_inequality(ordinary_rate:Fraction,
                              special_rate:Fraction)->Fraction:
    """Linear dual inequality; requires the lemma's physical assumptions."""
    o,s=Fraction(ordinary_rate),Fraction(special_rate)
    return ORD_COEFFICIENT*o+SPECIAL_COEFFICIENT*s


def bm27_directing_atoms():
    """The exact two-world BM-27 de Finetti coupling at 3 finite mask modes.

    Ordinary noise law mu is shared:
        I with 3/13, A with 2/13, B with 8/13.
    Signed exceptional pair-parity nu values:
        I: 0,0; A: 1/13,2/13; B: 8/13,7/13.
    Exceptional SINGLE-bit Walsh measures v are shared for the two
    hypotheses, separately at each ordinary mask mode.
    """
    atoms={}
    for key in ("I","A","B"):
        mu=[Fraction(0),Fraction(0)]
        parity=[Fraction(0),Fraction(0)]
        single=[Fraction(0),Fraction(0)]
        for h in (0,1):
            for ordinary,exception,weight in COMPONENTS[h]:
                if ordinary!=key:
                    continue
                probability=Fraction(weight,13)
                mu[h]+=probability
                w=pair_walsh(PAIRS[exception])
                single[h]+=probability*w[1]
                parity[h]+=probability*w[3]
        if mu[0]!=mu[1] or single[0]!=single[1]:
            raise AssertionError("BM-27 conditional single-bit rigidity failed")
        u,w=ordinary_pair_mask_coordinates(PAIRS[key])
        atoms[key]={
            "mu":mu[0],"u":u,"w":w,
            "nu0":parity[0],"nu1":parity[1],
            "v":single[0],
        }
    if sum((a["mu"] for a in atoms.values()),Fraction(0))!=1:
        raise AssertionError("directing mixture not normalized")
    return atoms


def verify_bm27_equality_case():
    """Exact saturation of the new 8:5 cost dual at BM-27's erasing law."""
    if not verify_convolution_identity():
        raise AssertionError("BM-27 all-n upper certificate invalid")
    atoms=bm27_directing_atoms()
    if tuple(atoms[k]["mu"] for k in ("I","A","B"))!=(
        Fraction(3,13),Fraction(2,13),Fraction(8,13)
    ):
        raise AssertionError("unexpected BM-27 ordinary directing masses")
    atomI,atomA,atomB=(atoms[k] for k in ("I","A","B"))
    if not (atomI["u"]==atomI["w"]==1 and
            atomI["nu0"]==atomI["nu1"]==0):
        raise AssertionError("isolated identity-mode parity mismatch")
    chain=TwoLevelChain(
        atomA["u"],atomA["w"],
        atomA["mu"],atomB["mu"],atomA["nu0"],
    )
    if not chain.check() or chain.signed_nu!=(
        atomA["nu0"],atomA["nu1"],atomB["nu0"],atomB["nu1"]
    ):
        raise AssertionError("dyadic 1:2:8:7 proportions violated")
    overlap=sum((min(a["nu0"],a["nu1"]) for a in atoms.values()),
                Fraction(0))
    ord_rate=sum((a["mu"]*(1-a["u"])/2 for a in atoms.values()),
                 Fraction(0))
    special_rate=(1-sum((a["v"] for a in atoms.values()),
                        Fraction(0)))/2
    if not overlap==Fraction(8,13):
        raise AssertionError("BM-27 parity overlap should saturate 8/13")
    if not ord_rate==special_rate==LIMIT:
        raise AssertionError("BM-27 does not attain the 5/52 lower")
    if not weighted_limit_inequality(ord_rate,special_rate)==WEIGHTED_BOUND:
        raise AssertionError("BM-29 weighted 8:5 inequality not sharp")
    if not overlap==Fraction(16,5)*sum(
        ((1-a["u"])*a["mu"] for a in atoms.values()),Fraction(0)
    ):
        raise AssertionError("dyadic overlap bound not saturated")
    if not all(exact_mask_rate(h)==(LIMIT,LIMIT) for h in (0,1)):
        raise AssertionError("BM-27 per-edge mask budget mismatched")
    return {
        "limit":str(LIMIT),
        "weighted_dual":"8 C_ordinary + 5 C_special >= 5/4",
        "ordinary_mask_modes":("I","A","B"),
        "dyadic_signed_parity_ratio":(1,2,8,7),
        "mu_I":str(atomI["mu"]),
        "mu_A":str(atomA["mu"]),
        "mu_B":str(atomB["mu"]),
        "special_parity_overlap":str(overlap),
        "ordinary_per_bit":str(ord_rate),
        "special_per_bit":str(special_rate),
        "infinite_measure_theory_formalized_in_python":False,
    }


def theorem_receipt():
    """The infinite proof is in BM-29 Markdown; exact finite lemmas here."""
    equal=verify_bm27_equality_case()
    if LIMIT!=Fraction(WEIGHTED_BOUND,ORD_COEFFICIENT+SPECIAL_COEFFICIENT):
        raise AssertionError("weighted inequality normalization")
    if theorem_upper(250)!=LIMIT:
        raise AssertionError("BM-27 all-n upper has changed")
    return {
        **equal,
        "analytic_lower":str(LIMIT),
        "analytic_upper":str(LIMIT),
        "conjecture_BM27_C1":"settled in the registered readout model",
        "remaining_finite_n_closed_form":False,
        "exact_finite_algebra_checked":True,
    }
