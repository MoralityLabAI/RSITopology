"""BM-16: exact bounded-separator Walsh factor elimination for gain graphs.

For any edge-occurrence graph with alphabet K=F2^s and a chosen Walsh
subset S of edge-satisfaction bits, factor
    F(a)=prod_{e in S} (1-2*1[a(u)^a(v)==c_e]).
Each vertex label is sampled independently uniformly. To compute the
unconditional Walsh coefficient or a conditional table over a retained
separator B, eliminate every other vertex by normalized summation:
    f_new(assignment_to_neighbors)
      = (1/q) sum_{x in K} prod_{factor touching v} f(...,v=x).

This works for ALL graphs including K4, a nonseries-parallel
2-terminal network and graphs with intersecting cycles. If the chosen
elimination order has induced width w (maximum factor scope w+1), a
single Fourier coefficient can be evaluated in
O(poly(n,m) q^(w+1)) rational arithmetic and space O(poly(n,m)q^w)
for explicit tables, with bit complexity depending on input length.
A retained boundary table has q^|B| entries. No polynomial-in-log(q)
claim is made when w>1; the BM-15 sparse transfer can exploit group
structure further for series-parallel graphs.

This is standard exact factor/junction-tree elimination specialized to the
gain-graph Boolean monitor. It does not compress the full 2^m erasure LP.
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
class Factor:
    scope: tuple[int,...]
    table: dict[tuple[int,...],Fraction]

    def value(self, labels: dict[int,int]) -> Fraction:
        return self.table[tuple(labels[v] for v in self.scope)]


@dataclass(frozen=True)
class BoundaryResult:
    boundary: tuple[int,...]
    values: dict[tuple[int,...],Fraction]
    max_join_scope: int
    new_table_entries: int
    elimination_order: tuple[int,...]

    def at(self, *labels:int) -> Fraction:
        if len(labels)!=len(self.boundary):
            raise ValueError("boundary assignment dimension mismatch")
        return self.values[tuple(labels)]


def _initial_factors(game:Game,subset:int) -> list[Factor]:
    if not 0<=subset<(1<<len(game.edges)):
        raise ValueError("Walsh subset outside edge set")
    q=game.q
    factors=[]
    for i,(u,v,shift) in enumerate(game.edges):
        if not subset & (1<<i):
            continue
        scope=tuple(sorted({u,v}))
        table={}
        for labels in product(range(q),repeat=len(scope)):
            lookup=dict(zip(scope,labels))
            table[labels]=Fraction(
                -1 if (lookup[u]^lookup[v])==shift else 1
            )
        factors.append(Factor(scope,table))
    return factors


def min_fill_order(game:Game,subset:int,
                   preserve:tuple[int,...]=()) -> tuple[int,...]:
    """Greedy min-fill elimination order; proof works for ANY valid order."""
    if len(set(preserve))!=len(preserve) or any(
        not 0<=v<game.vertices for v in preserve
    ):
        raise ValueError("invalid boundary vertices")
    if not 0<=subset<1<<len(game.edges):
        raise ValueError("invalid Walsh subset")
    adjacency=[set() for _ in range(game.vertices)]
    for i,(u,v,_) in enumerate(game.edges):
        if subset&(1<<i) and u!=v:
            adjacency[u].add(v)
            adjacency[v].add(u)
    alive=set(range(game.vertices))
    to_eliminate=alive-set(preserve)
    order=[]
    while to_eliminate:
        def priority(v):
            nbr=sorted(adjacency[v]&alive)
            missing=sum(1 for i,a in enumerate(nbr)
                        for b in nbr[i+1:] if b not in adjacency[a])
            return (missing,len(nbr),v)
        v=min(to_eliminate,key=priority)
        nbr=tuple(adjacency[v]&alive)
        for i,a in enumerate(nbr):
            for b in nbr[i+1:]:
                adjacency[a].add(b)
                adjacency[b].add(a)
        alive.remove(v)
        to_eliminate.remove(v)
        order.append(v)
    return tuple(order)


def eliminate_factor(
    factors:list[Factor],vertex:int,q:int
) -> tuple[list[Factor],int,int]:
    """Exact single-variable normalized elimination."""
    touched=[f for f in factors if vertex in f.scope]
    untouched=[f for f in factors if vertex not in f.scope]
    if not touched:
        # A free label has expectation 1 and leaves no factor.
        return list(factors),0,0
    join=tuple(sorted(set(v for f in touched for v in f.scope)))
    rest=tuple(v for v in join if v!=vertex)
    table={}
    for labels in product(range(q),repeat=len(rest)):
        assignment=dict(zip(rest,labels))
        total=Fraction(0)
        for x in range(q):
            assignment[vertex]=x
            value=Fraction(1)
            for f in touched:
                value*=f.value(assignment)
            total+=value
        table[labels]=total/q
    untouched.append(Factor(rest,table))
    return untouched,len(join),len(table)


def boundary_expectation(
    game:Game,subset:int,boundary:tuple[int,...]=(),
    *,order:tuple[int,...]|None=None
)->BoundaryResult:
    """Full conditional exact table on retained boundary labels.

    All other vertex labels are uniformly resampled and averaged out.
    For no boundary, the result contains a single scalar at key ().
    """
    if len(set(boundary))!=len(boundary) or any(
        not 0<=v<game.vertices for v in boundary
    ):
        raise ValueError("boundary vertices distinct and in graph")
    remaining=set(range(game.vertices))-set(boundary)
    if order is None:
        order=min_fill_order(game,subset,boundary)
    if len(set(order))!=len(order) or set(order)!=remaining:
        raise ValueError("order must eliminate every nonboundary vertex once")
    factors=_initial_factors(game,subset)
    max_scope=max((len(f.scope) for f in factors),default=0)
    entries=sum(len(f.table) for f in factors)
    for v in order:
        factors,scope,created=eliminate_factor(factors,v,game.q)
        max_scope=max(max_scope,scope)
        entries+=created
    table={}
    for labels in product(range(game.q),repeat=len(boundary)):
        assignment=dict(zip(boundary,labels))
        value=Fraction(1)
        for f in factors:
            value*=f.value(assignment)
        table[labels]=value
    max_scope=max(max_scope,len(boundary))
    entries+=len(table)
    return BoundaryResult(boundary,table,max_scope,entries,order)


def exact_walsh(game:Game,subset:int,
                *,order:tuple[int,...]|None=None)->Fraction:
    return boundary_expectation(game,subset,order=order).at()


def anchored_boundary(
    result:BoundaryResult, q:int
)->dict[tuple[int,...],Fraction]:
    """Quotient global gauge by anchoring first retained boundary label 0."""
    if q<2 or q&(q-1) or not result.boundary:
        raise ValueError("nonempty boundary and F2^s alphabet required")
    out={}
    for shifts in product(range(q),repeat=len(result.boundary)-1):
        out[shifts]=result.at(0,*shifts)
    # A global XOR translation leaves every satisfaction factor invariant.
    for labels,value in result.values.items():
        canonical=tuple(x^labels[0] for x in labels[1:])
        if out[canonical]!=value:
            raise AssertionError("boundary transfer violates gauge invariance")
    return out


def direct_boundary_oracle(
    game:Game,subset:int,boundary:tuple[int,...]
)->dict[tuple[int,...],Fraction]:
    """Independent exponential vertex-label oracle for finite controls."""
    if len(set(boundary))!=len(boundary) or any(
        not 0<=v<game.vertices for v in boundary
    ) or not 0<=subset<(1<<len(game.edges)):
        raise ValueError("invalid direct boundary query")
    rest=tuple(v for v in range(game.vertices) if v not in boundary)
    out={}
    for labels in product(range(game.q),repeat=len(boundary)):
        root=dict(zip(boundary,labels))
        total=0
        for interior in product(range(game.q),repeat=len(rest)):
            assignment={**root,**dict(zip(rest,interior))}
            parity=sum(
                1 for i,(u,v,g) in enumerate(game.edges)
                if subset&(1<<i) and assignment[u]^assignment[v]==g
            )%2
            total+=-1 if parity else 1
        out[labels]=Fraction(total,game.q**len(rest))
    return out


def elimination_manifest(game:Game,subset:int,
                         boundary:tuple[int,...]=()):
    r=boundary_expectation(game,subset,boundary)
    return {
        "q":game.q,"vertices":game.vertices,"edges":len(game.edges),
        "selected_edges":subset.bit_count(),
        "boundary_vertices":boundary,
        "induced_max_join_scope":r.max_join_scope,
        "max_table_states":game.q**r.max_join_scope,
        "explicit_table_entries":r.new_table_entries,
        "boundary_entries":len(r.values),
        "elimination_order":r.elimination_order,
    }
