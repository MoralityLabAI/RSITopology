"""BM-20: exact weighted parity separation and rational primal sparsification.

The BM-19 common-mask residual-support LP has an exponential column set.
Its dual constraints have one per mask x:
  y0 + sum_{S in D} y_S * (-1)^popcount(S & x)
     + sum_i z_i*x_i <= 0.
A maximally violated constraint is a weighted parity-CSP (Max-XOR) problem.
With an elimination order of induced factor width w, exact max-sum variable
elimination runs in poly(m,|D|)*2^(w+1) rational operations and returns an
attaining mask x. This is a separation oracle, NOT an implemented ellipsoid
or column-generation LP solver.

A further rational Caratheodory argument preserves a feasible mask law's
entire D-Walsh vector AND all m individual flip marginals using at most
1+|D|+m atoms. A constructive exact affine-dependence routine is included.

All claims are conditional on explicit Fourier supports and the BM-19
hypothesis-blind independent postprocessing interface. Graph treewidth
alone is not asserted to control the residual support-hypergraph width.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from collections import deque


@dataclass(frozen=True)
class ParityFactor:
    scope: tuple[int,...]
    table: tuple[Fraction,...]

    def at(self, assignment:dict[int,int])->Fraction:
        idx=sum((assignment[v]<<i) for i,v in enumerate(self.scope))
        return self.table[idx]


@dataclass(frozen=True)
class SeparationReceipt:
    maximum: Fraction
    maximizing_mask: int
    elimination_order: tuple[int,...]
    max_join_scope: int
    induced_width: int
    candidate_assignments: int
    factors: int

    @property
    def feasible(self)->bool:
        return self.maximum<=0


def _support(m:int,support:tuple[int,...])->tuple[int,...]:
    if not isinstance(m,int) or m<1:
        raise ValueError("positive number of readout bits required")
    if len(set(support))!=len(support) or any(
        not isinstance(s,int) or not 0<s<(1<<m) for s in support
    ):
        raise ValueError("distinct nonempty Fourier supports required")
    return tuple(sorted(support))


def _check_dual(m:int,support:tuple[int,...],proof):
    _support(m,support)
    z=tuple(Fraction(v) for v in proof.marginal_multipliers)
    if len(z)!=m or any(v>0 for v in z) or -sum(z,Fraction(0))!=1:
        raise ValueError("signed marginal multipliers must sum to -1")
    if any(S not in support for S in proof.characters):
        raise ValueError("dual Fourier term not registered in support")
    return Fraction(proof.normalization),{
        S:Fraction(v) for S,v in proof.characters.items() if v
    },z


def parity_factors(m:int,support:tuple[int,...],proof,
                   *,max_factor_bits:int=16)->list[ParityFactor]:
    """Construct rational factors only for nonzero active dual terms."""
    y0,y,z=_check_dual(m,support,proof)
    factors=[ParityFactor((),(y0,))]
    for S,coefficient in sorted(y.items()):
        scope=tuple(i for i in range(m) if S&(1<<i))
        if len(scope)>max_factor_bits:
            raise ValueError("individual parity factor exceeds explicit memory cap")
        factors.append(ParityFactor(
            scope,tuple(coefficient*(-1 if k.bit_count()%2 else 1)
                        for k in range(1<<len(scope)))
        ))
    for i,weight in enumerate(z):
        if weight:
            factors.append(ParityFactor((i,),(Fraction(0),weight)))
    return factors


def min_fill_order(m:int,scopes:tuple[tuple[int,...],...])->tuple[int,...]:
    """Greedy factor-hypergraph min-fill; exactness holds for any order."""
    if not isinstance(m,int) or m<1 or any(
        any(not 0<=v<m for v in S) or len(set(S))!=len(S)
        for S in scopes
    ):
        raise ValueError("invalid factor scopes")
    adj=[set() for _ in range(m)]
    for scope in scopes:
        for a in scope:
            adj[a].update(v for v in scope if v!=a)
    alive=set(range(m))
    order=[]
    while alive:
        def key(v:int):
            nbr=sorted(adj[v]&alive-{v})
            fill=sum(1 for i,u in enumerate(nbr)
                     for x in nbr[i+1:] if x not in adj[u])
            return (fill,len(nbr),v)
        v=min(alive,key=key)
        nbr=tuple(sorted(adj[v]&alive-{v}))
        for i,a in enumerate(nbr):
            for b in nbr[i+1:]:
                adj[a].add(b)
                adj[b].add(a)
        alive.remove(v)
        order.append(v)
    return tuple(order)


def exact_separate(m:int,support:tuple[int,...],proof, *,
                   order:tuple[int,...]|None=None,
                   max_factor_bits:int=16)->SeparationReceipt:
    """Exact dual separation: maximum over all 2^m mask atoms, with witness.

    Each max-sum elimination step creates a factor on the eliminated
    variable's remaining neighbors and a backpointer table. The
    backpointers reconstruct a global maximizing Boolean mask.

    max_factor_bits limits ALL joined scopes, preventing accidental
    exponential allocation even when a supplied order is poor.
    """
    factors=parity_factors(
        m,support,proof,max_factor_bits=max_factor_bits
    )
    initial=len(factors)
    if order is None:
        order=min_fill_order(
            m,tuple(f.scope for f in factors if f.scope)
        )
    if len(order)!=m or set(order)!=set(range(m)):
        raise ValueError("elimination order must be a permutation of readout bits")
    back=[]
    max_scope=0
    operations=0
    for v in order:
        touched=[f for f in factors if v in f.scope]
        factors=[f for f in factors if v not in f.scope]
        if not touched:
            back.append((v,(),(0,)))
            continue
        join=tuple(sorted({u for f in touched for u in f.scope}))
        max_scope=max(max_scope,len(join))
        if len(join)>max_factor_bits:
            raise ValueError("joined factor exceeds explicit memory cap")
        rest=tuple(u for u in join if u!=v)
        table=[]
        choices=[]
        for rest_assignment in range(1<<len(rest)):
            values={u:(rest_assignment>>i)&1 for i,u in enumerate(rest)}
            scores=[]
            for bit in (0,1):
                values[v]=bit
                scores.append(sum((f.at(values) for f in touched),Fraction(0)))
                operations+=1
            better=1 if scores[1]>scores[0] else 0
            choices.append(better)
            table.append(scores[better])
        factors.append(ParityFactor(rest,tuple(table)))
        back.append((v,rest,tuple(choices)))
    if any(f.scope for f in factors):
        raise AssertionError("factor scope remained after full elimination")
    optimum=sum((f.table[0] for f in factors),Fraction(0))
    assignment:dict[int,int]={}
    for v,rest,choices in reversed(back):
        k=sum((assignment[u]<<i) for i,u in enumerate(rest))
        assignment[v]=choices[k]
    mask=sum(bit<<i for i,bit in assignment.items())
    assert len(assignment)==m
    if direct_slack(m,support,proof,mask)!=optimum:
        raise AssertionError("DP witness and direct slack differ")
    return SeparationReceipt(
        optimum,mask,tuple(order),max_scope,
        max(0,max_scope-1),operations,initial,
    )


def direct_slack(m:int,support:tuple[int,...],proof,mask:int)->Fraction:
    """Independent direct evaluation of one dual mask inequality."""
    y0,y,z=_check_dual(m,support,proof)
    if not 0<=mask<1<<m:
        raise ValueError("mask outside registered Boolean space")
    return y0+sum(
        (c*(-1 if (mask&S).bit_count()%2 else 1)
         for S,c in y.items()),Fraction(0)
    )+sum((z[i] for i in range(m) if mask&(1<<i)),Fraction(0))


def brute_separate(m:int,support:tuple[int,...],proof)->tuple[Fraction,int]:
    """Independent exhaustive oracle used ONLY in bounded tests."""
    if m>14:
        raise ValueError("exhaustive reference restricted to <=14 bits")
    vals=[direct_slack(m,support,proof,mask) for mask in range(1<<m)]
    best=max(vals)
    return best,vals.index(best)


def verify_dual_fast(m:int,support:tuple[int,...],proof,**kwargs)->Fraction:
    """Matching BM-19 rational weak-duality validator with width-aware oracle."""
    receipt=exact_separate(m,support,proof,**kwargs)
    if not receipt.feasible:
        raise AssertionError(
            "dual violated at mask %d by %s" %
            (receipt.maximizing_mask,receipt.maximum)
        )
    return Fraction(proof.normalization)


def _moment_vector(m:int,support:tuple[int,...],mask:int)->tuple[Fraction,...]:
    return (
        (Fraction(1),)+
        tuple(Fraction(-1 if (mask&S).bit_count()%2 else 1)
              for S in support)+
        tuple(Fraction(1 if mask&(1<<i) else 0) for i in range(m))
    )


def _kernel_vector(columns:list[tuple[Fraction,...]])->list[Fraction]:
    """Exact nonzero null vector for |columns| > coordinate dimension."""
    if not columns or len(columns)<=len(columns[0]):
        raise ValueError("linearly dependent overcomplete columns required")
    rows=[[col[i] for col in columns] for i in range(len(columns[0]))]
    pivot_cols=[]
    pivot_row=0
    for c in range(len(columns)):
        pivot=next((r for r in range(pivot_row,len(rows))
                    if rows[r][c]),None)
        if pivot is None:
            continue
        rows[pivot_row],rows[pivot]=rows[pivot],rows[pivot_row]
        v=rows[pivot_row][c]
        rows[pivot_row]=[x/v for x in rows[pivot_row]]
        for r in range(len(rows)):
            if r==pivot_row:
                continue
            mul=rows[r][c]
            if mul:
                rows[r]=[x-mul*y for x,y in zip(rows[r],rows[pivot_row])]
        pivot_cols.append(c)
        pivot_row+=1
        if pivot_row==len(rows):
            break
    free=next(c for c in range(len(columns)) if c not in pivot_cols)
    vector=[Fraction(0)]*len(columns)
    vector[free]=1
    for r,c in enumerate(pivot_cols):
        vector[c]=-rows[r][free]
    assert all(sum((v*col[k] for v,col in zip(vector,columns)),
                   Fraction(0))==0 for k in range(len(columns[0])))
    return vector


def sparsify_mask_law(
    m:int,support:tuple[int,...],law:dict[int,Fraction]
)->dict[int,Fraction]:
    """Exact constructive rational Caratheodory support bound.

    At every step remove at least one atom along a null direction of the
    normalization, D-Walsh and individual-bit-marginal moment matrix.
    Preserves EVERY registered moment and flip probability exactly.
    """
    support=_support(m,support)
    if any(not isinstance(mask,int) or not 0<=mask<(1<<m) or
           Fraction(p)<0 for mask,p in law.items()):
        raise ValueError("invalid mask distribution")
    weights={mask:Fraction(p) for mask,p in law.items() if p}
    if sum(weights.values(),Fraction(0))!=1:
        raise ValueError("mask distribution must be normalized")
    limit=1+len(support)+m
    while len(weights)>limit:
        chosen=sorted(weights)[:limit+1]
        cols=[_moment_vector(m,support,mask) for mask in chosen]
        null=_kernel_vector(cols)
        if not any(v>0 for v in null) or not any(v<0 for v in null):
            raise AssertionError("affine dependence must have mixed signs")
        lam=min(weights[mask]/v for mask,v in zip(chosen,null) if v>0)
        for mask,v in zip(chosen,null):
            weights[mask]-=lam*v
            if not weights[mask]:
                del weights[mask]
            elif weights[mask]<0:
                raise AssertionError("sparsification created negative mass")
    return weights


def moment_fingerprint(
    m:int,support:tuple[int,...],law:dict[int,Fraction]
)->tuple[Fraction,...]:
    """Independent exact normalization, Walsh moments, and m marginals."""
    support=_support(m,support)
    if any(not 0<=mask<(1<<m) for mask in law):
        raise ValueError("mask outside domain")
    return tuple(sum((p*v for mask,p in law.items())
                     ,Fraction(0))
                 for v in ()) if False else tuple(
        sum((Fraction(p)*x for mask,p in law.items()
             for x in (_moment_vector(m,support,mask)[i],)),Fraction(0))
        for i in range(1+len(support)+m)
    )


def bipartite_pair_support_certificate(
    m:int,edges:tuple[tuple[int,int],...]
):
    """An analytic exact r*=1/4 family for bipartite pair-character supports.

    Given >=1 distinct graph edges on m bits and any proper two-coloring,
    use common R with masses 1/2 at zero mask and 1/4 at each color-class
    mask. Every edge has opposite colors, so each parity character has
    zero expectation. Each bit flips at rate <=1/4.

    Lower bound comes from any one pair character:
      1/2=P(odd on pair)<=p_i+p_j<=2r.
    A single-character rational dual is a matching certificate.
    """
    if not isinstance(m,int) or m<2 or not edges:
        raise ValueError("need >=2 readout bits and >=1 pair support")
    adj=[set() for _ in range(m)]
    for u,v in edges:
        if not isinstance(u,int) or not isinstance(v,int) or not (
            0<=u<m and 0<=v<m and u!=v
        ):
            raise ValueError("simple pair-character edges required")
        adj[u].add(v);adj[v].add(u)
    colors=[None]*m
    for root in range(m):
        if colors[root] is not None:
            continue
        colors[root]=0
        queue=deque([root])
        while queue:
            u=queue.popleft()
            for v in adj[u]:
                if colors[v] is None:
                    colors[v]=1-colors[u]
                    queue.append(v)
                elif colors[v]==colors[u]:
                    raise ValueError("interaction graph must be bipartite")
    classes=tuple(
        sum(1<<i for i,c in enumerate(colors) if c==side)
        for side in (0,1)
    )
    masklaw:dict[int,Fraction]={}
    for mask,p in ((0,Fraction(1,2)),(classes[0],Fraction(1,4)),
                   (classes[1],Fraction(1,4))):
        masklaw[mask]=masklaw.get(mask,Fraction(0))+p
    supports=tuple(sorted({(1<<u)|(1<<v) for u,v in edges}))
    u,v=edges[0]
    # Import deferred to avoid a cycle with BM-19.
    try:
        from .support_aware_completion_BM19 import PostprocessorDual
    except ImportError:
        from support_aware_completion_BM19 import PostprocessorDual
    z=[Fraction(0)]*m
    z[u]=z[v]=Fraction(-1,2)
    dual=PostprocessorDual(Fraction(1,4),
                           {(1<<u)|(1<<v):Fraction(-1,4)},
                           tuple(z))
    assert moment_fingerprint(m,supports,masklaw)[0]==1
    return supports,masklaw,dual
