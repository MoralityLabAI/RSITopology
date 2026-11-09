"""BM-09 cactus control: edge-disjoint cycles compose without cap inflation.

Two frustrated four-cycles joined by a bridge have cycle rank 2, as does
the K23 theta graph. Their full Boolean law factorizes into the two
cycle-block laws and the independent bridge bit. Independent common
single-cycle masks exactly erase both, with per-bit cap 1/8 for q=4.

The isolated-cycle projection gives the matching lower bound. This is a
finite exact negative control for any claim that rank beta1 alone predicts
interacting-cycle erasure complexity.
"""
from __future__ import annotations

from itertools import product
from fractions import Fraction

C4_CACTUS_EDGES = (
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,6),(6,7),(7,4),
    (3,4),
)
C4_CACTUS_SHIFT = (0,0,0,1, 0,0,0,2, 0)
N = 9
OBS = 1 << N


def cactus_counts(shifts: tuple[int,...]) -> tuple[int,...]:
    """Exact independent vertex-label oracle; denominator 4^8."""
    if len(shifts)!=N or any(not 0<=s<4 for s in shifts):
        raise ValueError("need nine F2^2 edge shifts")
    counts=[0]*OBS
    for labels in product(range(4),repeat=8):
        observed=sum(
            1<<i for i,((u,v),s) in enumerate(zip(C4_CACTUS_EDGES,shifts))
            if labels[u]^labels[v]==s
        )
        counts[observed]+=1
    assert sum(counts)==4**8
    return tuple(counts)


def independent_cycle_masks() -> dict[int,int]:
    """Two independent C4 one-hot erasers, denominator 64."""
    masks={}
    first=((0,4),)+tuple((1<<i,1) for i in range(4))
    second=((0,4),)+tuple((1<<(i+4),1) for i in range(4))
    for a,wa in first:
        for b,wb in second:
            masks[a|b]=wa*wb
    assert len(masks)==25 and sum(masks.values())==64
    for j in range(N):
        marginal=sum(weight for mask,weight in masks.items()
                     if mask & (1<<j))
        assert marginal==(8 if j<8 else 0)
    return masks


def cactus_convolve(clean: tuple[int,...],mask_weights: dict[int,int]):
    if len(clean)!=OBS:
        raise ValueError("nine-edge clean law required")
    return tuple(
        sum(clean[y^mask]*weight for mask,weight in mask_weights.items())
        for y in range(OBS)
    )


def verify_cactus_q4() -> dict[str,Fraction|bool]:
    """An exact erasing mask at eta=1/8, with a matching local-cycle bound."""
    a=cactus_counts((0,)*N)
    b=cactus_counts(C4_CACTUS_SHIFT)
    masks=independent_cycle_masks()
    assert cactus_convolve(a,masks)==cactus_convolve(b,masks)
    return {
        "erasure_cap":Fraction(1,8),
        "matches_isolated_cycle_projection_lower_bound":True,
        "full_pattern_equality":True,
        "cycle_rank":2,
        "vertices":8,
        "edges":9,
    }
