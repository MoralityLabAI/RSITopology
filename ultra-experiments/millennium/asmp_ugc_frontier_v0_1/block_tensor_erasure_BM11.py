"""BM-11: exact erasure-cap tensorization for one-vertex graph sums.

G=G_A vee G_B is formed by identifying one vertex from each factor, and
keeping edge occurrences disjoint. With fresh uniform vertex labels in
K=F2^s, complete satisfaction-pattern laws factor exactly by block.
Therefore the sharp state-aware readout erasure cap of the combined pair
(flat vs c_A vee c_B) equals max(eta_sym(G_A),eta_sym(G_B)).

The lower bound projects ANY adversarial joint output channel onto each
block, preserving its per-edge readout cap. The upper bound takes products
of attaining independent block masks. This holds even if an adversary
can choose correlated masks across blocks and depending on the hypothesis.

Worked exact example: glue BM-10 q4 diamond (eta=1/5) to BM-09 q4
contrabalanced theta (eta=1/6) at root vertex. The combined graph has
8 vertices, 11 edges, and beta1=4; eta remains exactly 1/5.
A sparse dual from the diamond extends with exactly the same support
to the larger graph, providing a size-independent exact lower certificate.

All computations use exact integers/Fractions. No network/GPU/LP runtime.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product

try:
    from .finite_seed import Game
    from .diamond_weighted_fourier_BM10 import (
        EDGES as DIAMOND_EDGES, SHIFT as DIAMOND_SHIFTS,
        PRIMAL_MASK_COUNTS as DIAMOND_MASKS,
        PRIMAL_DENOMINATOR as DIAMOND_DENOM,
        DUAL_NORMALIZATION, DUAL_WALSH, DUAL_MARGINAL,
        full_dual_slacks, walsh as diamond_walsh,
    )
    from .theta_shared_cycle_erasure import (
        THETA_EDGES, THETA_SHIFTS, q4_common_mask,
    )
except ImportError:
    from finite_seed import Game
    from diamond_weighted_fourier_BM10 import (
        EDGES as DIAMOND_EDGES, SHIFT as DIAMOND_SHIFTS,
        PRIMAL_MASK_COUNTS as DIAMOND_MASKS,
        PRIMAL_DENOMINATOR as DIAMOND_DENOM,
        DUAL_NORMALIZATION, DUAL_WALSH, DUAL_MARGINAL,
        full_dual_slacks, walsh as diamond_walsh,
    )
    from theta_shared_cycle_erasure import (
        THETA_EDGES, THETA_SHIFTS, q4_common_mask,
    )


def vertex_sum(a: Game, b: Game, *, root_a: int=0, root_b: int=0) -> Game:
    """Glue selected vertices, respecting every original edge occurrence."""
    if a.bits != b.bits or not (0 <= root_a < a.vertices and 0 <= root_b < b.vertices):
        raise ValueError("alphabets must agree; roots must be valid")
    mapping={
        v:(root_a if v==root_b else a.vertices+v-int(v>root_b))
        for v in range(b.vertices)
    }
    edges = tuple(a.edges) + tuple(
        (mapping[u],mapping[v],s) for u,v,s in b.edges
    )
    result=Game(a.vertices+b.vertices-1,a.bits,edges)
    if len(result.edges)!=len(a.edges)+len(b.edges):
        raise AssertionError("edge occurrences lost")
    return result


def exact_satisfaction_counts(g: Game) -> tuple[int,...]:
    """Direct independent vertex enumeration; denominator q^|V|."""
    m=len(g.edges)
    out=[0]*(1<<m)
    for labels in product(range(g.q),repeat=g.vertices):
        pattern=sum(1<<i for i,(u,v,s) in enumerate(g.edges)
                    if labels[u]^labels[v]==s)
        out[pattern]+=1
    if sum(out)!=g.q**g.vertices:
        raise AssertionError("probability normalization")
    return tuple(out)


def factor_counts(a: Game,b: Game) -> tuple[int,...]:
    """C_G(pattern_a,pattern_b)=C_A*C_B/q under one-vertex identification."""
    if a.bits!=b.bits:
        raise ValueError("need matching gain alphabet")
    x,y=exact_satisfaction_counts(a),exact_satisfaction_counts(b)
    q=a.q
    return tuple(
        (u*v)//q for v in y for u in x
    ) if all((u*v)%q==0 for u in x for v in y) else _fraction_failure()


def _fraction_failure():
    raise AssertionError("root-shift invariance did not give integer census")


def product_masks(
    masks_a:dict[int,int],denom_a:int,edges_a:int,
    masks_b:dict[int,int],denom_b:int,edges_b:int,
) -> tuple[dict[int,int],int]:
    """Independent exact mask product on disjoint registered edge coordinates."""
    if denom_a<1 or denom_b<1 or edges_a<0 or edges_b<0:
        raise ValueError("invalid mask dimensions/normalizers")
    if sum(masks_a.values())!=denom_a or sum(masks_b.values())!=denom_b:
        raise ValueError("mask laws need normalization")
    if any(k<0 or k>=1<<edges_a or w<0 for k,w in masks_a.items()) or any(
        k<0 or k>=1<<edges_b or w<0 for k,w in masks_b.items()
    ):
        raise ValueError("mask support outside edge space")
    return ({
        x|(y<<edges_a):u*v for x,u in masks_a.items()
        for y,v in masks_b.items() if u*v
    },denom_a*denom_b)


def mask_marginals_counts(masks:dict[int,int],edges:int) -> tuple[int,...]:
    return tuple(
        sum(weight for mask,weight in masks.items() if mask & (1<<i))
        for i in range(edges)
    )


def convolve_exact(
    counts:tuple[int,...],masks:dict[int,int]
) -> tuple[int,...]:
    """Full output convolution for a modest exact finite graph."""
    n=len(counts)
    if n<1 or n&(n-1) or any(m<0 or m>=n for m in masks):
        raise ValueError("mask space incompatible with output patterns")
    return tuple(
        sum(counts[y^mask]*w for mask,w in masks.items())
        for y in range(n)
    )


def worked_diamond_theta_pair() -> tuple[Game,Game,dict[int,int],int]:
    """Two-cycle-rank blocks glued at one vertex, q=4 and 11 edges."""
    diamond0=Game(4,2,tuple((u,v,0) for u,v in DIAMOND_EDGES))
    diamond1=Game(4,2,tuple(
        (u,v,s) for (u,v),s in zip(DIAMOND_EDGES,DIAMOND_SHIFTS)
    ))
    theta0=Game(5,2,tuple((u,v,0) for u,v in THETA_EDGES))
    theta1=Game(5,2,tuple(
        (u,v,s) for (u,v),s in zip(THETA_EDGES,THETA_SHIFTS)
    ))
    theta_mask={j:w for j,w in enumerate(q4_common_mask()) if w}
    masks,denom=product_masks(
        DIAMOND_MASKS,DIAMOND_DENOM,len(diamond0.edges),
        theta_mask,12,len(theta0.edges),
    )
    return vertex_sum(diamond0,theta0),vertex_sum(diamond1,theta1),masks,denom


def verify_block_tensorization() -> dict[str,int|str|bool]:
    """Full independent census and mask equality for diamond vee theta."""
    a,b,masks,denom=worked_diamond_theta_pair()
    assert a.vertices==b.vertices==8 and len(a.edges)==len(b.edges)==11
    diamond0=Game(4,2,tuple((u,v,0) for u,v in DIAMOND_EDGES))
    diamond1=Game(4,2,tuple(
        (u,v,s) for (u,v),s in zip(DIAMOND_EDGES,DIAMOND_SHIFTS)
    ))
    theta0=Game(5,2,tuple((u,v,0) for u,v in THETA_EDGES))
    theta1=Game(5,2,tuple(
        (u,v,s) for (u,v),s in zip(THETA_EDGES,THETA_SHIFTS)
    ))
    p0,p1=exact_satisfaction_counts(a),exact_satisfaction_counts(b)
    assert p0==factor_counts(diamond0,theta0)
    assert p1==factor_counts(diamond1,theta1)
    assert convolve_exact(p0,masks)==convolve_exact(p1,masks)
    assert sum(masks.values())==denom==240
    marg=mask_marginals_counts(masks,11)
    assert marg==(48,48,48,48,48,40,40,40,40,40,40)
    assert Fraction(max(marg),denom)==Fraction(1,5)
    return {
        "vertices":8,"edges":11,"cycle_rank":4,
        "erasure_cap":"1/5",
        "full_pattern_equality":True,
        "product_law_verified_by_direct_labels":True,
        "mask_denominator":denom,
    }


def extended_diamond_dual_slacks() -> tuple[tuple[Fraction,...],tuple[Fraction,...]]:
    """Lift BM-10 dual to all 2*2048 joint mask atoms.

    The local Walsh coefficient for a subset of the diamond's edges is
    unchanged by vertex-summing an arbitrary rooted block. The dual uses
    no theta-edge multiplier, so every 11-bit slack equals the earlier
    5-bit diamond slack at its low-bit projection.
    """
    local=full_dual_slacks()
    m=len(DIAMOND_EDGES)
    return tuple(
        tuple(local[h][mask&((1<<m)-1)] for mask in range(1<<11))
        for h in (0,1)
    )  # type: ignore[return-value]


def verify_extended_dual() -> bool:
    """Independent global exact Walsh check and every dual inequality."""
    p0,p1,masks,_=worked_diamond_theta_pair()
    count0,count1=exact_satisfaction_counts(p0),exact_satisfaction_counts(p1)
    q=p0.q
    assert sum(DUAL_NORMALIZATION)==Fraction(1,5)
    assert -sum((x for row in DUAL_MARGINAL for x in row.values()),
                Fraction(0))==1
    # Directly confirm each global low-subset Walsh coefficient is the
    # exact local diamond coefficient, not merely inferred symbolically.
    for h,counts in enumerate((count0,count1)):
        diamond=Game(4,2,tuple(
            (u,v,0 if h==0 else DIAMOND_SHIFTS[i])
            for i,(u,v) in enumerate(DIAMOND_EDGES)
        ))
        localcounts=exact_satisfaction_counts(diamond)
        for subset in DUAL_WALSH:
            global_hat=sum(
                (-1 if (x&subset).bit_count()%2 else 1)*k
                for x,k in enumerate(counts)
            )
            local_hat=sum(
                (-1 if (x&subset).bit_count()%2 else 1)*k
                for x,k in enumerate(localcounts)
            )
            assert Fraction(global_hat,q**8)==Fraction(local_hat,q**4)
    # Check every one of the 4096 global dual mask inequalities.
    slacks=extended_diamond_dual_slacks()
    assert all(v<=0 for s in slacks for v in s)
    return True
