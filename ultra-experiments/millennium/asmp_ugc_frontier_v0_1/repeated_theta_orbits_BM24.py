"""BM-24: wreath-product path symmetry for theta networks with a growing core.

A theta gain graph consists of k internally vertex-disjoint u-v paths,
and its core has k parallel edge occurrences. BM-14 grouped the edges
INSIDE each path, leaving product_i(L_i+1) orbit mask states, exponential
when k grows. If several paths have the same joint type (length, gain0,
gain1), their whole path blocks are exchangeable under BOTH hypotheses.
The group is a product of imprimitive wreath-product actions
    (S_L wr S_n)_type.

For a type with n repeated paths length L, mask/Walsh orbit signatures
are histograms (c0,...,cL) with sum(c)=n, counting paths with each
Hamming weight 0..L. There are binomial(n+L,L) such states. Thus the
entire hypothesis-aware, correlated and current-clean-independent readout
erasure LP is EXACTLY equivalent to a rational orbit LP with
    M=product_type binomial(n_type+L_type,L_type),
    2M+1 variables, M+1 Fourier/normalization equalities,
    and 2*(number_of_types) marginal inequalities.

Individual orbit Walsh coefficients use BM-12 terminal conditioning.
The mask orbit kernel is a multivariate Krawtchouk average, computed by
an exact hypergeometric assignment DP. The quotient preserves the FULL
Boolean observation law, allowing distinct masks in the two worlds.

If both maximum path length L_max and the number r of joint path types
are fixed, the full LP has polynomial size in k and log q. For fixed
q and common path length L, at most q^2 joint gain types occur, so this
includes growing K2,k cores. The direct bound is XP in r,L_max; it is
NOT an FPT claim in variable r or L_max.

A separate BM-24/T2 theorem treats n ordinary paths and one
exceptional path, all length L, gains0 all zero, gains1 zero on ordinary
paths and a fixed nonzero gain on the exceptional path. For q=2 or 4,
the fully hypothesis-aware optimum is 1/(4L), for ALL n>=1. For ANY
q=2^s, the sharp COMMON-channel optimum is 1/(4L). An O(n)-description
mixture of two branch erasers attains it, while a projected two-path
cycle gives the matching BM-08 (q<=4) or parity (common mask) lower
bound. For q>4 the sharp fully state-aware optimum is left open.

No full-mask or full-Fourier table is needed for the large n fixtures.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb, factorial, prod

try:
    from .theta_orbit_lp_BM14 import walsh_kernel_one
    from .theta_fourier_transfer_BM12 import theta_path_game
except ImportError:
    from theta_orbit_lp_BM14 import walsh_kernel_one
    from theta_fourier_transfer_BM12 import theta_path_game


@dataclass(frozen=True, order=True)
class PathType:
    length: int
    gain0: int
    gain1: int
    count: int


def _compositions(n:int,parts:int):
    """Ordered nonnegative histograms; the total count is C(n+parts-1,parts-1)."""
    if parts==1:
        yield (n,)
        return
    for x in range(n+1):
        for rest in _compositions(n-x,parts-1):
            yield (x,)+rest


@lru_cache(maxsize=None)
def type_histograms(n:int,L:int)->tuple[tuple[int,...],...]:
    if not isinstance(n,int) or not isinstance(L,int) or n<1 or L<1:
        raise ValueError("positive type multiplicity and path length required")
    return tuple(_compositions(n,L+1))


def type_histogram_size(n:int,L:int)->int:
    if not isinstance(n,int) or not isinstance(L,int) or n<1 or L<1:
        raise ValueError("positive multiplicity/length required")
    return comb(n+L,L)


@lru_cache(maxsize=250000)
def type_krawtchouk_kernel(
    L:int, selected_hist:tuple[int,...], mask_hist:tuple[int,...]
)->Fraction:
    """Exact orbit Walsh character under uniform matching of path weights.

    First choose which path gets each requested mask Hamming weight,
    uniformly among all permutations of those weights. Conditional on
    the assigned path mask weight t, draw its t flipped bit positions
    uniformly. For a path with s selected edges, the character
    expectation is the binary Krawtchouk ratio Phi_L(s,t).

    The DP assigns mask weights without replacement, recording their
    remaining histogram. Its state count is at most
    product_t(mask_hist[t]+1), polynomial in n for FIXED L.
    """
    if (L<1 or len(selected_hist)!=L+1 or len(mask_hist)!=L+1
        or any(not isinstance(x,int) or x<0
               for x in selected_hist+mask_hist)
        or sum(selected_hist)!=sum(mask_hist) or sum(selected_hist)<1):
        raise ValueError("two nonnegative path histograms of equal size required")
    n=sum(selected_hist)
    states={mask_hist:Fraction(1)}
    processed=0
    for s,amount in enumerate(selected_hist):
        for _ in range(amount):
            updated={}
            for remaining,prob in states.items():
                total=n-processed
                for t,multiplicity in enumerate(remaining):
                    if not multiplicity:
                        continue
                    after=remaining[:t]+(multiplicity-1,)+remaining[t+1:]
                    add=prob*Fraction(multiplicity,total)*walsh_kernel_one(L,s,t)
                    updated[after]=updated.get(after,Fraction(0))+add
            states=updated
            processed+=1
    zero=(0,)*(L+1)
    if set(states)!={zero}:
        raise AssertionError("mask histogram not completely assigned")
    return states[zero]


def type_histogram_multiplicity(L:int,hist:tuple[int,...])->int:
    """Number of Walsh subsets represented by an exchangeability histogram."""
    if L<1 or len(hist)!=L+1 or any(n<0 for n in hist):
        raise ValueError("valid path histogram required")
    n=sum(hist)
    result=factorial(n)
    for x in hist:
        result//=factorial(x)
    # factorial divisions must be performed as a single multinomial,
    # so recompute exactly before multiplying by selected-edge choices.
    multi=factorial(n)//prod((factorial(x) for x in hist),start=1)
    return multi*prod((comb(L,s)**x for s,x in enumerate(hist)),start=1)


@dataclass(frozen=True)
class RepeatedTheta:
    q:int
    types:tuple[PathType,...]

    def __post_init__(self):
        if (not isinstance(self.q,int) or self.q<2 or self.q&(self.q-1)
            or not self.types
            or any(t.length<1 or t.count<1 or not 0<=t.gain0<self.q
                   or not 0<=t.gain1<self.q for t in self.types)
            or len({(t.length,t.gain0,t.gain1) for t in self.types})
               !=len(self.types)):
            raise ValueError("valid distinct joint path types and q=2^s required")

    @classmethod
    def from_paths(cls,q:int,paths:tuple[tuple[int,int,int],...]):
        """Group repeated (length,gain0,gain1) path specifications."""
        from collections import Counter
        freq=Counter(paths)
        types=tuple(
            PathType(L,g0,g1,n) for (L,g0,g1),n in sorted(freq.items())
        )
        return cls(q,types)

    @property
    def path_count(self)->int:
        return sum(t.count for t in self.types)

    @property
    def m(self)->int:
        return sum(t.length*t.count for t in self.types)

    @property
    def vertices(self)->int:
        return 2+sum(t.count*(t.length-1) for t in self.types)

    @property
    def orbit_size(self)->int:
        return prod((type_histogram_size(t.count,t.length)
                     for t in self.types),start=1)

    @property
    def BM14_pathwise_orbit_size(self)->int:
        return prod(((t.length+1)**t.count for t in self.types),start=1)

    @property
    def path_lengths(self)->tuple[int,...]:
        return tuple(L for t in self.types for L in (t.length,)*t.count)

    @property
    def groups(self)->int:
        return len(self.types)

    def game(self,h:int):
        """Independent full-label oracle, for modest-size regression tests."""
        if h not in (0,1):
            raise ValueError("hypothesis must be 0 or 1")
        gains=tuple(
            (t.gain0 if h==0 else t.gain1)
            for t in self.types for _ in range(t.count)
        )
        return theta_path_game(self.q,self.path_lengths,gains)

    def signature(self,mask:int):
        """Histogram of per-path Hamming weights in each joint gain type."""
        if not isinstance(mask,int) or not 0<=mask<1<<self.m:
            raise ValueError("edge subset outside theta readout")
        offset=0
        histograms=[]
        for t in self.types:
            h=[0]*(t.length+1)
            for _ in range(t.count):
                k=((mask>>offset)&((1<<t.length)-1)).bit_count()
                h[k]+=1
                offset+=t.length
            histograms.append(tuple(h))
        return tuple(histograms)

    def canonical_subset(self,sig:tuple[tuple[int,...],...])->int:
        self._valid_signature(sig)
        offset=0
        bits=0
        for t,hist in zip(self.types,sig):
            for r,multiplicity in enumerate(hist):
                for _ in range(multiplicity):
                    bits|=((1<<r)-1)<<offset
                    offset+=t.length
        return bits

    def _valid_signature(self,sig):
        if len(sig)!=len(self.types) or any(
            len(hist)!=t.length+1 or sum(hist)!=t.count
            or any(not isinstance(x,int) or x<0 for x in hist)
            for t,hist in zip(self.types,sig)
        ):
            raise ValueError("invalid repeated-path type histogram")

    def all_signatures(self,*,max_orbits:int=256):
        if self.orbit_size>max_orbits:
            raise ValueError("orbit materialization exceeds registered bound")
        return tuple(product(*(
            type_histograms(t.count,t.length) for t in self.types
        )))

    @lru_cache(maxsize=100000)
    def clean_walsh_signature(
        self,h:int,sig:tuple[tuple[int,...],...]
    )->Fraction:
        """Exact joint Boolean Fourier coefficient using terminal conditioning.

        All paths within a joint type have the same length and each
        hypothesis has the same total gain on them, so only the number
        of FULL selected paths and total selected PROPER edges matter.
        """
        if h not in (0,1):
            raise ValueError("hypothesis must be 0/1")
        self._valid_signature(sig)
        alpha=Fraction(self.q-2,self.q)
        proper=sum(sum(s*hist[s] for s in range(t.length))
                   for t,hist in zip(self.types,sig))
        selected=[]
        for t,hist in zip(self.types,sig):
            full=hist[t.length]
            if full:
                L=t.length
                A=alpha**L-Fraction(-2,self.q)**L
                B=Fraction((-2)**L,self.q**(L-1))
                gain=t.gain0 if h==0 else t.gain1
                selected.append((gain,full,A,B))
        baseline=prod((A**count for _,count,A,_ in selected),
                      start=Fraction(1))
        gains={gain for gain,_,_,_ in selected}
        total=(self.q-len(gains))*baseline
        for d in gains:
            total+=prod((
                (A+(B if gain==d else 0))**count
                for gain,count,A,B in selected
            ),start=Fraction(1))
        return alpha**proper*total/self.q

    def clean_walsh(self,h:int,subset:int)->Fraction:
        return self.clean_walsh_signature(h,self.signature(subset))

    def orbit_kernel(self,selected_sig,mask_sig)->Fraction:
        self._valid_signature(selected_sig)
        self._valid_signature(mask_sig)
        return prod((type_krawtchouk_kernel(
            t.length,selected,mask
        ) for t,selected,mask in zip(self.types,selected_sig,mask_sig)),
                    start=Fraction(1))

    def orbit_size_of_signature(self,sig)->int:
        self._valid_signature(sig)
        return prod((
            type_histogram_multiplicity(t.length,h)
            for t,h in zip(self.types,sig)
        ),start=1)

    def verify_primal(
        self,flat:dict,other:dict,*,cap:Fraction|None=None,
        max_orbits:int=256
    )->Fraction:
        """Full Walsh-orbit equalities, mask laws and per-edge cap."""
        classes=self.all_signatures(max_orbits=max_orbits)
        valid=set(classes)
        for law in (flat,other):
            if any(sig not in valid or Fraction(v)<0
                   for sig,v in law.items()) or sum(
                (Fraction(v) for v in law.values()),Fraction(0)
            )!=1:
                raise ValueError("normalized histogram-orbit mask laws required")
        for sig in classes:
            a=sum((Fraction(v)*self.orbit_kernel(sig,t)
                   for t,v in flat.items()),Fraction(0))
            b=sum((Fraction(v)*self.orbit_kernel(sig,t)
                   for t,v in other.items()),Fraction(0))
            if self.clean_walsh_signature(0,sig)*a!=(
                self.clean_walsh_signature(1,sig)*b
            ):
                raise AssertionError("full Fourier equality failed at "+str(sig))
        eta=self.max_bit_marginal(flat,other)
        if cap is not None and eta>Fraction(cap):
            raise AssertionError("mask cost above supplied cap")
        return eta

    def max_bit_marginal(self,*laws)->Fraction:
        """Each original edge in a repeated path type has the same marginal."""
        result=Fraction(0)
        for law in laws:
            for idx,t in enumerate(self.types):
                p=sum((
                    Fraction(v)*sum(r*hist[r] for r in range(t.length+1))
                    /Fraction(t.count*t.length)
                    for sig,v in law.items()
                    for hist in (sig[idx],)
                ),Fraction(0))
                result=max(result,p)
        return result

    def full_mask_to_orbits(self,weights:dict[int,int],denominator:int)->dict:
        if denominator<1 or sum(weights.values())!=denominator or any(
            not isinstance(m,int) or not 0<=m<1<<self.m or
            not isinstance(w,int) or w<0 for m,w in weights.items()
        ):
            raise ValueError("invalid full mask weights")
        result={}
        for mask,w in weights.items():
            sig=self.signature(mask)
            result[sig]=result.get(sig,Fraction(0))+Fraction(w,denominator)
        return {sig:v for sig,v in result.items() if v}

    def clean_support_count(self,*,max_orbits:int=256)->int:
        """Exact count of nonzero clean Fourier discrepancies from orbit weights."""
        return sum((
            self.orbit_size_of_signature(sig)
            for sig in self.all_signatures(max_orbits=max_orbits)
            if self.clean_walsh_signature(0,sig)!=
               self.clean_walsh_signature(1,sig)
        ),0)


@dataclass(frozen=True)
class RepeatedOrbitLP:
    signatures:tuple
    equalities:tuple[tuple[Fraction,...],...]
    equality_rhs:tuple[Fraction,...]
    inequalities:tuple[tuple[Fraction,...],...]
    inequality_rhs:tuple[Fraction,...]
    objective:tuple[Fraction,...]

    @property
    def variables(self)->int:
        return len(self.objective)


def build_repeated_lp(model:RepeatedTheta,*,max_orbits:int=64)->RepeatedOrbitLP:
    """A solver-ready exact rational LP with 2M+1 vars and M+1 equalities."""
    cls=model.all_signatures(max_orbits=max_orbits)
    M=len(cls)
    eq=[]
    for S in cls:
        if S==tuple(
            (t.count,)+(0,)*t.length for t in model.types
        ):
            continue
        a=model.clean_walsh_signature(0,S)
        b=model.clean_walsh_signature(1,S)
        eq.append(tuple(a*model.orbit_kernel(S,T) for T in cls)+
                  tuple(-b*model.orbit_kernel(S,T) for T in cls)+
                  (Fraction(0),))
    eq.append((Fraction(1),)*M+(Fraction(0),)*(M+1))
    eq.append((Fraction(0),)*M+(Fraction(1),)*M+(Fraction(0),))
    if len(eq)!=M+1:
        raise AssertionError("wrong number of Walsh normalization rows")
    marginal=[]
    for h in (0,1):
        for idx,t in enumerate(model.types):
            marginal.append(tuple(
                Fraction(sum(r*T[idx][r] for r in range(t.length+1)),
                         t.length*t.count)
                if hh==h else Fraction(0)
                for hh in (0,1) for T in cls
            )+(Fraction(-1),))
    return RepeatedOrbitLP(
        cls,tuple(eq),
        (Fraction(0),)*(M-1)+(Fraction(1),Fraction(1)),
        tuple(marginal),(Fraction(0),)*(2*model.groups),
        (Fraction(0),)*(2*M)+(Fraction(1),)
    )


def check_repeated_lp_matrix(lp:RepeatedOrbitLP,flat:dict,other:dict,
                             eta:Fraction)->bool:
    x=tuple(Fraction(flat.get(S,0)) for S in lp.signatures)+tuple(
        Fraction(other.get(S,0)) for S in lp.signatures
    )+(Fraction(eta),)
    return (
        all(v>=0 for v in x)
        and all(sum((u*v for u,v in zip(row,x)),Fraction(0))==rhs
                for row,rhs in zip(lp.equalities,lp.equality_rhs))
        and all(sum((u*v for u,v in zip(row,x)),Fraction(0))<=rhs
                for row,rhs in zip(lp.inequalities,lp.inequality_rhs))
    )


def repeated_manifest(model:RepeatedTheta)->dict[str,object]:
    M=model.orbit_size
    return {
        "q":model.q,"types":len(model.types),
        "paths":model.path_count,"vertices":model.vertices,
        "reported_edges":model.m,
        "mask_atoms_per_world":1<<model.m,
        "BM14_path_mask_orbits":model.BM14_pathwise_orbit_size,
        "BM24_repeated_type_orbits":M,
        "LP_variables":2*M+1,"LP_equalities":M+1,
        "LP_marginal_rows":2*len(model.types),
        "per_type_histogram_classes":tuple(
            type_histogram_size(t.count,t.length) for t in model.types
        ),
        "full_mask_or_clean_Fourier_table_materialized":False,
    }
