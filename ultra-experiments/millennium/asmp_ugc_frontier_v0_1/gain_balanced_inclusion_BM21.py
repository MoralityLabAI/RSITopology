"""BM-21: balanced-subgraph inclusion/exclusion for any F2^s gain graph.

For S a selected set of edge-satisfaction report bits, the exact Walsh
coefficient under gain connection c is

    P_hat_c(S) = sum_{T subset S; c|T balanced}
                   (-2)^|T| * q^(-rank_graph(T)),

where rank_graph(T)=|V|-components(V,T), including isolated vertices.
Each constraint event has probability q^-rank when the chosen T is gain
balanced and zero otherwise. This is elementary Fourier expansion of
prod_{e in S}(1-2*1[edge satisfied]).

Compared with the FLAT connection, the exact discrepancy is

    Delta(S) = sum_{T subset S; T gain-unbalanced}
                      (-2)^|T| q^-rank(T).

Thus S must CONTAIN an unbalanced cycle for its clean Fourier discrepancy
to be nonzero. Containment need not SUFFICE: distinct cycle terms may
cancel (e.g. two frustrated triangles joined at an articulation vertex
over q=4, where the joint six-edge coefficient coincides).

For any *simple* unbalanced cycle C, Delta(C)=(-2)^|C|/q^(|C|-1)
and C is a minimal discrepancy support seed.

This exact oracle costs O(2^|S|*|S|*alpha(|V|)) operations plus rational
arithmetic, independently of q^|V| labeling enumeration. The complexity
is exponential in |S|; it is mainly a cross-check and a derivation tool.
"""
from __future__ import annotations

from fractions import Fraction

try:
    from .finite_seed import Game
except ImportError:
    from finite_seed import Game


def _validate(game:Game,subset:int)->None:
    if not isinstance(game,Game) or not isinstance(subset,int) or not (
        0<=subset<(1<<len(game.edges))
    ):
        raise ValueError("Game and valid edge-subset bitmask required")


def edge_subset_rank_balance(game:Game,subset:int)->tuple[int,bool]:
    """Weighted union-find returns (graphic rank, gain balance)."""
    _validate(game,subset)
    parent=list(range(game.vertices))
    size=[1]*game.vertices
    parity=[0]*game.vertices
    def find(v:int)->tuple[int,int]:
        if parent[v]==v:
            return v,0
        root,x=find(parent[v])
        parity[v]^=x
        parent[v]=root
        return root,parity[v]
    rank=0
    balanced=True
    for i,(u,v,gain) in enumerate(game.edges):
        if not subset&(1<<i):
            continue
        ru,pu=find(u)
        rv,pv=find(v)
        if ru==rv:
            if pu^pv!=gain:
                balanced=False
        else:
            # Enforce potential(u) XOR potential(v) == gain after joining.
            if size[ru]<size[rv]:
                ru,rv=rv,ru
            parent[rv]=ru
            parity[rv]=pu^pv^gain
            size[ru]+=size[rv]
            rank+=1
    return rank,balanced


def all_constraints_probability(game:Game,subset:int)->Fraction:
    """Uniform probability all selected edges are simultaneously satisfied."""
    rank,balanced=edge_subset_rank_balance(game,subset)
    return Fraction(1,game.q**rank) if balanced else Fraction(0)


def graph_walsh_inclusion(game:Game,subset:int)->Fraction:
    """Exact Fourier coefficient using only gain-balance subgraph subsets."""
    _validate(game,subset)
    out=Fraction(0)
    T=subset
    while True:
        rank,balanced=edge_subset_rank_balance(game,T)
        if balanced:
            out+=Fraction((-2)**T.bit_count(),game.q**rank)
        if T==0:
            break
        T=(T-1)&subset
    return out


def clean_difference_inclusion(game:Game,subset:int)->Fraction:
    """Flat - registered gain Fourier difference with no q^V enumeration."""
    _validate(game,subset)
    out=Fraction(0)
    T=subset
    while True:
        rank,balanced=edge_subset_rank_balance(game,T)
        if not balanced:
            out+=Fraction((-2)**T.bit_count(),game.q**rank)
        if T==0:
            break
        T=(T-1)&subset
    return out


def contains_unbalanced_cycle(game:Game,subset:int)->bool:
    """Necessary structural predicate for clean Fourier nonzero difference."""
    return not edge_subset_rank_balance(game,subset)[1]


def pure_cycle_minimal_difference(game:Game,cycle_edges:tuple[int,...])->Fraction:
    """Check a registered simple cycle whose gain XOR is nonzero."""
    if len(cycle_edges)<3 or len(set(cycle_edges))!=len(cycle_edges):
        raise ValueError("simple cycle must contain >=3 distinct edges")
    mask=sum(1<<i for i in cycle_edges)
    _validate(game,mask)
    if not contains_unbalanced_cycle(game,mask):
        raise ValueError("cycle is gain balanced")
    for i in cycle_edges:
        if contains_unbalanced_cycle(game,mask^(1<<i)):
            raise ValueError("cycle edge set has a smaller unbalanced cycle")
    value=clean_difference_inclusion(game,mask)
    want=Fraction((-2)**len(cycle_edges),game.q**(len(cycle_edges)-1))
    if value!=want:
        raise AssertionError("minimal unbalanced cycle character identity failed")
    return value
