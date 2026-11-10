"""BM-23: full hostile-readout LP for substitutions of a fixed gain core.

Take ANY finite oriented gain multigraph H with k core edges over K=F2^s.
Subdivide edge e into an internally vertex-disjoint path of length L_e>=1
with total XOR gain g_(h,e) under either hidden hypothesis h=0/1. Fresh
uniform vertex labels produce all Boolean edge-satisfaction reports.

Conditional on core vertex labels, each substituted path's residuals are
uniform over the affine XOR-sum constraint. Therefore its Boolean law is
invariant under S_(L_e) permutations of its edge positions. The COMPLETE
hypothesis-aware, clean-current-sample-independent correlated-mask erasure
LP thus has an EXACT path-count orbit quotient with
    M=product_e(L_e+1),
    2M+1 primal variables, M+1 Walsh equalities, 2k marginal inequalities.
For any FIXED core H, this is polynomial in m=sum L_e and log q; for
variable k it is an XP rather than FPT bound.

A registered Walsh subset S has J={e: ALL path edges of e selected},
b=number of selected proper-path edges, alpha=1-2/q. Its clean character is
  W_h(S)=alpha^b * sum_(T subset J; g_h|T balanced)
      q^-r(T) prod_(e in T) B_L_e prod_(e in J\\T) A_L_e,
where A_L=alpha^L-(-2/q)^L, B_L=(-2)^L/q^(L-1).
This gain-balanced core-subgraph transfer costs at most 3^k total
subsets for all J and never enumerates q^core_vertices labelings.

This contains BM-14 theta networks as parallel-edge cores but also
handles three-or-more-terminal, biconnected non-series-parallel cores,
including K4 and subdivisions. Support counting for fixed core is exact
even with exponentially many Fourier indices.

Separate q4 K4 single-edge subdivision theorem and exact masks are in
k4_subdivision_erasure_BM23.py. No general theorem for arbitrary
variable-size cores or authenticated model intervention is claimed.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import prod

try:
    from .finite_seed import Game
    from .gain_balanced_inclusion_BM21 import edge_subset_rank_balance
    from .theta_orbit_lp_BM14 import (
        orbit_signatures,walsh_kernel,mask_signature,
        expand_orbit_masses,
    )
except ImportError:
    from finite_seed import Game
    from gain_balanced_inclusion_BM21 import edge_subset_rank_balance
    from theta_orbit_lp_BM14 import (
        orbit_signatures,walsh_kernel,mask_signature,
        expand_orbit_masses,
    )


@dataclass(frozen=True)
class CoreSubdivision:
    """One fixed gain core H and two path-gain assignments."""
    q: int
    core_vertices: int
    core_edges: tuple[tuple[int,int],...]
    lengths: tuple[int,...]
    gains0: tuple[int,...]
    gains1: tuple[int,...]

    def __post_init__(self):
        k=len(self.core_edges)
        if (not isinstance(self.q,int) or self.q<2 or self.q&(self.q-1)
            or self.core_vertices<2 or k<2
            or len(self.lengths)!=k or len(self.gains0)!=k
            or len(self.gains1)!=k
            or any(not isinstance(L,int) or L<1 for L in self.lengths)
            or any(not 0<=g<self.q or not isinstance(g,int)
                   for g in self.gains0+self.gains1)
            or any(not 0<=u<self.core_vertices or
                   not 0<=v<self.core_vertices or u==v
                   for u,v in self.core_edges)):
            raise ValueError("q=2^s, >=2 core edges, valid endpoints, "
                             "positive lengths, and path gains required")

    @property
    def k(self)->int:
        return len(self.core_edges)

    @property
    def m(self)->int:
        return sum(self.lengths)

    @property
    def vertices(self)->int:
        return self.core_vertices+sum(L-1 for L in self.lengths)

    @property
    def orbit_size(self)->int:
        return prod((L+1 for L in self.lengths),start=1)

    @property
    def path_masks(self)->tuple[int,...]:
        out=[]
        shift=0
        for L in self.lengths:
            out.append(((1<<L)-1)<<shift)
            shift+=L
        return tuple(out)

    def signature(self,S:int)->tuple[int,...]:
        if not isinstance(S,int) or not 0<=S<1<<self.m:
            raise ValueError("Walsh subset outside subdivided core")
        return tuple((S&mask).bit_count() for mask in self.path_masks)

    def canonical_subset(self,counts:tuple[int,...])->int:
        if len(counts)!=self.k or any(not 0<=r<=L
                                     for L,r in zip(self.lengths,counts)):
            raise ValueError("path-count Fourier signature incompatible")
        return sum((((1<<r)-1)*(mask&-mask))
                   for r,mask in zip(counts,self.path_masks))

    def subdivided_game(self,h:int)->Game:
        if h not in (0,1):
            raise ValueError("hypothesis must be 0/1")
        gains=self.gains0 if h==0 else self.gains1
        edges=[]
        nxt=self.core_vertices
        for (u,v),L,g in zip(self.core_edges,self.lengths,gains):
            prev=u
            for step in range(L):
                w=v if step==L-1 else nxt
                if step<L-1:
                    nxt+=1
                edges.append((prev,w,g if step==0 else 0))
                prev=w
        assert nxt==self.vertices and len(edges)==self.m
        return Game(self.vertices,self.q.bit_length()-1,tuple(edges))

    @lru_cache(maxsize=None)
    def _base_core(self,h:int)->Game:
        if h not in (0,1):
            raise ValueError("hypothesis must be 0 or 1")
        gains=self.gains0 if h==0 else self.gains1
        return Game(self.core_vertices,self.q.bit_length()-1,
                    tuple((u,v,g) for (u,v),g in zip(self.core_edges,gains)))

    @lru_cache(maxsize=None)
    def full_path_average(self,h:int,J:int)->Fraction:
        """Exact core-label average using balanced rank on 2^|J| subgraphs."""
        if h not in (0,1) or not isinstance(J,int) or not 0<=J<1<<self.k:
            raise ValueError("invalid hypothesis or full-path subset")
        alpha=Fraction(self.q-2,self.q)
        full=[i for i in range(self.k) if J&(1<<i)]
        AB={}
        for i in full:
            L=self.lengths[i]
            A=alpha**L-Fraction(-2,self.q)**L
            B=Fraction((-2)**L,self.q**(L-1))
            AB[i]=(A,B)
        total=Fraction(0)
        T=J
        core=self._base_core(h)
        while True:
            rank,balanced=edge_subset_rank_balance(core,T)
            if balanced:
                term=Fraction(1,self.q**rank)
                for i in full:
                    term*=AB[i][1] if T&(1<<i) else AB[i][0]
                total+=term
            if T==0:
                break
            T=(T-1)&J
        return total

    def clean_walsh(self,S:int,h:int)->Fraction:
        """Exact complete Boolean Walsh coefficient, no vertex enumeration."""
        counts=self.signature(S)
        J=sum(1<<i for i,(r,L) in enumerate(zip(counts,self.lengths))
              if r==L)
        proper=sum(r for r,L in zip(counts,self.lengths) if r<L)
        return Fraction(self.q-2,self.q)**proper*self.full_path_average(h,J)

    def orbit_clean_walsh(self,counts:tuple[int,...],h:int)->Fraction:
        return self.clean_walsh(self.canonical_subset(counts),h)

    def clean_delta(self,S:int)->Fraction:
        return self.clean_walsh(S,0)-self.clean_walsh(S,1)

    def support_path_types(self)->tuple[int,...]:
        return tuple(J for J in range(1<<self.k)
                     if self.full_path_average(0,J)!=
                     self.full_path_average(1,J))

    def clean_support_count(self)->int:
        """Exact count from at most 2^k path classes, without enumerating 2^m."""
        count=0
        for J in self.support_path_types():
            factor=prod((1 if self.q==2 else (1<<L)-1
                         for i,L in enumerate(self.lengths)
                         if not J&(1<<i)),start=1)
            count+=factor
        assert 0<=count<=(1<<self.m)
        return count

    def supports(self,S:int)->bool:
        return bool(self.clean_delta(S))

    def orbit_classes(self)->tuple[tuple[int,...],...]:
        return orbit_signatures(self.lengths)

    def verify_orbit_primal(self,flat:dict[tuple[int,...],Fraction],
                            other:dict[tuple[int,...],Fraction],
                            *,cap:Fraction|None=None)->Fraction:
        """All orbit Walsh constraints, normalization and edge flip bounds."""
        classes=set(self.orbit_classes())
        for masks in (flat,other):
            if any(s not in classes or v<0 for s,v in masks.items()) or (
                sum(masks.values(),Fraction(0))!=1
            ):
                raise ValueError("normalized path-orbit masks needed")
        for s in self.orbit_classes():
            a=sum((v*walsh_kernel(self.lengths,s,t)
                   for t,v in flat.items()),Fraction(0))
            b=sum((v*walsh_kernel(self.lengths,s,t)
                   for t,v in other.items()),Fraction(0))
            if self.orbit_clean_walsh(s,0)*a!=self.orbit_clean_walsh(s,1)*b:
                raise AssertionError(f"full masked Fourier mismatch at {s}")
        eta=max((sum((v*Fraction(t[i],L) for t,v in law.items()),
                     Fraction(0))
                 for law in (flat,other)
                 for i,L in enumerate(self.lengths)),default=Fraction(0))
        if cap is not None and eta>Fraction(cap):
            raise AssertionError("mask law exceeds per-edge rate")
        return eta

    def verify_orbit_dual(
        self,norm:tuple[Fraction,Fraction],
        coefficients:dict[tuple[int,...],Fraction],
        signed_marginals:tuple[tuple[Fraction,...],tuple[Fraction,...]],
    )->Fraction:
        """Check EXACT universal lower dual over 2*M orbit-mask atoms."""
        classes=set(self.orbit_classes())
        if (len(norm)!=2 or len(signed_marginals)!=2 or
            any(len(row)!=self.k for row in signed_marginals) or
            any(s not in classes or s==(0,)*self.k
                for s in coefficients)):
            raise ValueError("invalid orbit dual dimensions/support")
        if (any(v>0 for row in signed_marginals for v in row)
            or -sum((v for row in signed_marginals for v in row),
                    Fraction(0))!=1):
            raise ValueError("invalid dual marginal normalization")
        for h in (0,1):
            for t in self.orbit_classes():
                slack=Fraction(norm[h])
                for s,c in coefficients.items():
                    slack+=((1 if h==0 else -1)*Fraction(c)*
                            self.orbit_clean_walsh(s,h)*
                            walsh_kernel(self.lengths,s,t))
                slack+=sum((
                    Fraction(v)*Fraction(t[i],L)
                    for i,(v,L) in enumerate(zip(signed_marginals[h],
                                                 self.lengths))
                ),Fraction(0))
                if slack>0:
                    raise AssertionError(
                        "invalid orbit dual at world=%s mask=%s slack=%s"
                        %(h,t,slack)
                    )
        return sum((Fraction(v) for v in norm),Fraction(0))


@dataclass(frozen=True)
class CoreOrbitLP:
    signatures:tuple[tuple[int,...],...]
    equality_rows:tuple[tuple[Fraction,...],...]
    equality_rhs:tuple[Fraction,...]
    marginal_rows:tuple[tuple[Fraction,...],...]
    marginal_rhs:tuple[Fraction,...]
    objective:tuple[Fraction,...]

    @property
    def variables(self)->int:
        return len(self.objective)


def build_core_orbit_lp(model:CoreSubdivision,*,max_classes:int=128
                        )->CoreOrbitLP:
    """Exact rational matrix, O(M²) coefficients; bounded eager construction."""
    cls=model.orbit_classes()
    M=len(cls)
    if M>max_classes or max_classes<1:
        raise ValueError("orbit LP exceeds declared class resource cap")
    eq=[]
    for s in cls:
        if s==(0,)*model.k:
            continue
        a=model.orbit_clean_walsh(s,0)
        b=model.orbit_clean_walsh(s,1)
        eq.append(
            tuple(a*walsh_kernel(model.lengths,s,t) for t in cls)+
            tuple(-b*walsh_kernel(model.lengths,s,t) for t in cls)+
            (Fraction(0),)
        )
    eq.extend((
        (Fraction(1),)*M+(Fraction(0),)*(M+1),
        (Fraction(0),)*M+(Fraction(1),)*M+(Fraction(0),)
    ))
    marg=[]
    for h in (0,1):
        for i,L in enumerate(model.lengths):
            marg.append(tuple(
                Fraction(t[i],L) if world==h else Fraction(0)
                for world in (0,1) for t in cls
            )+(Fraction(-1),))
    assert len(eq)==M+1 and len(marg)==2*model.k
    return CoreOrbitLP(
        cls,tuple(eq),(Fraction(0),)*(M-1)+(Fraction(1),Fraction(1)),
        tuple(marg),(Fraction(0),)*(2*model.k),
        (Fraction(0),)*(2*M)+(Fraction(1),)
    )


def check_core_orbit_lp_matrix(
    lp:CoreOrbitLP,flat:dict[tuple[int,...],Fraction],
    other:dict[tuple[int,...],Fraction],eta:Fraction
)->bool:
    x=tuple(Fraction(flat.get(t,0)) for t in lp.signatures)+tuple(
        Fraction(other.get(t,0)) for t in lp.signatures
    )+(Fraction(eta),)
    if any(v<0 for v in x):
        return False
    return all(
        sum((a*b for a,b in zip(row,x)),Fraction(0))==rhs
        for row,rhs in zip(lp.equality_rows,lp.equality_rhs)
    ) and all(
        sum((a*b for a,b in zip(row,x)),Fraction(0))<=rhs
        for row,rhs in zip(lp.marginal_rows,lp.marginal_rhs)
    )


def core_subdivision_manifest(model:CoreSubdivision)->dict[str,object]:
    M=model.orbit_size
    return {
        "q":model.q,
        "base_vertices":model.core_vertices,
        "base_edges":model.k,
        "subdivided_vertices":model.vertices,
        "subdivided_edges":model.m,
        "raw_readout_masks_per_world":1<<model.m,
        "path_orbit_classes_per_world":M,
        "orbit_lp_variables":2*M+1,
        "orbit_lp_equalities":M+1,
        "orbit_lp_marginal_inequalities":2*model.k,
        "clean_residual_support_count":model.clean_support_count(),
        "full_output_or_Fourier_table_materialized":False,
    }
