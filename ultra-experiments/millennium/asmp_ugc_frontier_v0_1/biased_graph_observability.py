"""ASMP-14/15: exact Boolean-monitor equivalence for gain graphs.

The complete law of edge satisfaction bits under independent uniformly
sampled vertex labelings is determined precisely by the balanced edge-subset
family (the underlying biased graph). Numerical holonomy, its image size, and
the minimum exact flat-cover degree can remain unidentifiable.

All probability calculations are exact Fraction arithmetic. Exponential
subset enumeration is a finite verification oracle, not an efficient decoder.
"""
from __future__ import annotations

from fractions import Fraction

try:
    from .finite_seed import Game, cycle_signature, forest
except ImportError:
    from finite_seed import Game, cycle_signature, forest


def balanced_subset_signature(game: Game) -> tuple[bool, ...]:
    """Bitmask-indexed balanced-subset flags, including loops/multiedges.

    A subset is balanced iff every fundamental cycle has zero XOR holonomy.
    As the spanning forest is recomputed on each subgraph, this tests all
    cycles and does not mistake cancellation across disjoint cycles for balance.
    """
    m = len(game.edges)
    flags = []
    for mask in range(1 << m):
        subgraph = Game(
            game.vertices, game.bits,
            tuple(e for i, e in enumerate(game.edges) if mask & (1 << i)),
        )
        flags.append(all(h == 0 for _, h in cycle_signature(subgraph)))
    return tuple(flags)


def exact_boolean_moments(game: Game) -> tuple[Fraction, ...]:
    """Moment[mask] = Pr(all listed edge-satisfaction indicators are true)."""
    q, n = game.q, game.vertices
    moments = []
    for mask in range(1 << len(game.edges)):
        subgraph = Game(
            n, game.bits,
            tuple(e for i, e in enumerate(game.edges) if mask & (1 << i)),
        )
        _, _, components = forest(subgraph)
        balanced = all(h == 0 for _, h in cycle_signature(subgraph))
        moments.append(Fraction(1, q ** (n-components)) if balanced else Fraction(0))
    return tuple(moments)


def full_boolean_law(game: Game) -> dict[tuple[bool, ...], Fraction]:
    """Recover the complete indicator law from joint moments by Möbius inversion.

    Result is the law for one fresh uniformly random vertex labeling.
    Repeated independent samples give tensor powers of the same law.
    """
    m = len(game.edges)
    result = list(exact_boolean_moments(game))
    for bit in range(m):
        flag = 1 << bit
        for mask in range(1 << m):
            if not mask & flag:
                result[mask] -= result[mask | flag]
    if any(p < 0 for p in result) or sum(result) != 1:
        raise AssertionError("invalid indicator distribution")
    return {
        tuple(bool(mask & (1 << i)) for i in range(m)): p
        for mask, p in enumerate(result) if p > 0
    }


def maximum_balanced_subset(game: Game) -> int:
    """Maximal jointly consistent edge set; equals max satisfied count."""
    flags = balanced_subset_signature(game)
    return max((mask.bit_count() for mask, ok in enumerate(flags) if ok), default=0)


def holonomy_image_size(game: Game) -> int:
    """Image order of H_1(G;F2) -> K, which controls exact flat-cover degree."""
    span = {0}
    for _, h in cycle_signature(game):
        span |= {s ^ h for s in tuple(span)}
    return len(span)


def cactus_pair(t: int, bits: int) -> tuple[Game, Game]:
    """Connected t triangles joined by bridges.

    Each triangle is frustrated in both games. In 'aligned' all triangle
    holonomies equal one. In 'independent' they are independent K directions,
    requiring bits>=t. Both have identical biased graphs and Boolean laws.
    Their minimum connected flat-cover degrees are 2 versus 2^t.
    """
    if t < 1 or bits < t:
        raise ValueError("requires t>=1 and alphabet bit width>=t")
    edges_a = []
    edges_b = []
    for j in range(t):
        u = 3*j
        edges_a.extend([(u,u+1,0),(u+1,u+2,0),(u+2,u,1)])
        edges_b.extend([(u,u+1,0),(u+1,u+2,0),(u+2,u,1<<j)])
        if j:
            edges_a.append((3*(j-1)+2,u,0))
            edges_b.append((3*(j-1)+2,u,0))
    return (
        Game(3*t,bits,tuple(edges_a)),
        Game(3*t,bits,tuple(edges_b)),
    )
