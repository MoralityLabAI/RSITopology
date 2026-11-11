"""Finite exact sanity checks for provisional ASMP-13 through ASMP-16.

A standalone pure-stdlib module. Each edge occurrence (u,v,shift) is a
constraint a[v] == a[u] XOR shift over K=F2^s. Enumeration is exponential.
This module proves no general complexity or AI-safety claim.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import product


@dataclass(frozen=True)
class Game:
    vertices: int
    bits: int
    edges: tuple[tuple[int, int, int], ...]

    def __post_init__(self):
        if self.vertices < 1 or self.bits < 1:
            raise ValueError("positive vertex and alphabet sizes required")
        if any(not (0 <= u < self.vertices and 0 <= v < self.vertices and
                    0 <= shift < (1 << self.bits))
               for u, v, shift in self.edges):
            raise ValueError("invalid edge")

    @property
    def q(self) -> int:
        return 1 << self.bits


def forest(game: Game):
    adj = [[] for _ in range(game.vertices)]
    for i, (u, v, s) in enumerate(game.edges):
        adj[u].append((v, s, i))
        adj[v].append((u, s, i))
    potential: list[int | None] = [None] * game.vertices
    chosen: set[int] = set()
    components = 0
    for root in range(game.vertices):
        if potential[root] is not None:
            continue
        components += 1
        potential[root] = 0
        queue = [root]
        for u in queue:
            for v, shift, idx in adj[u]:
                if potential[v] is None:
                    potential[v] = int(potential[u]) ^ shift
                    queue.append(v)
                    chosen.add(idx)
    p = tuple(int(x) for x in potential)
    return p, frozenset(chosen), components


def cycle_signature(game: Game):
    p, tree, _ = forest(game)
    return tuple((i, p[u] ^ s ^ p[v])
                 for i, (u, v, s) in enumerate(game.edges)
                 if i not in tree)


def quotient_counts(game: Game):
    _, _, components = forest(game)
    beta = len(game.edges) - game.vertices + components
    return game.q ** beta, game.q ** (game.vertices - components)


def gauge_witness(a: Game, b: Game):
    if (a.vertices, a.bits) != (b.vertices, b.bits) or tuple(
        (u, v) for u, v, _ in a.edges
    ) != tuple((u, v) for u, v, _ in b.edges):
        raise ValueError("edge graph and alphabet must match")
    shifts = Game(a.vertices, a.bits, tuple(
        (u, v, s ^ t) for (u, v, s), (_, _, t) in zip(a.edges, b.edges)))
    p, _, _ = forest(shifts)
    if any(p[u] ^ p[v] != shift for u, v, shift in shifts.edges):
        return None
    return p


def optimum(game: Game):
    if not game.edges:
        return Fraction(1)
    best = 0
    for a in product(range(game.q), repeat=game.vertices):
        satisfied = sum(a[u] ^ a[v] == shift for u, v, shift in game.edges)
        best = max(best, satisfied)
    return Fraction(best, len(game.edges))


def satisfaction_law(game: Game, indices: tuple[int, ...]):
    if len(set(indices)) != len(indices) or any(
        i < 0 or i >= len(game.edges) for i in indices
    ):
        raise ValueError("invalid observed edges")
    hist = Counter()
    for a in product(range(game.q), repeat=game.vertices):
        hist[tuple(a[game.edges[i][1]] == (a[game.edges[i][0]] ^ game.edges[i][2])
                   for i in indices)] += 1
    return {k: Fraction(v, game.q ** game.vertices) for k, v in hist.items()}


def regular_flat_cover(game: Game):
    """Connected regular kernel-of-holonomy covering for connected base G."""
    p, _, components = forest(game)
    if components != 1:
        raise ValueError("base graph must be connected")
    span = {0}
    for _, hol in cycle_signature(game):
        span |= {h ^ hol for h in tuple(span)}
    fiber = tuple(sorted(span))
    idx = {h: j for j, h in enumerate(fiber)}
    d = len(fiber)
    edges = []
    for u, v, shift in game.edges:
        residual = p[u] ^ shift ^ p[v]
        for h in fiber:
            edges.append((u * d + idx[h], v * d + idx[h ^ residual], shift))
    lifted = Game(game.vertices * d, game.bits, tuple(edges))
    labels = tuple(p[u] ^ h for u in range(game.vertices) for h in fiber)
    return lifted, labels, d


def descent_error(lifted_labels: tuple[int, ...], n: int, r: int):
    """Minimum fiber disagreements using modal base label; tied modes allowed."""
    if n < 1 or r < 1 or len(lifted_labels) != n * r:
        raise ValueError("invalid cover label layout")
    errors = 0
    for u in range(n):
        cnt = Counter(lifted_labels[u*r:(u+1)*r])
        errors += r - max(cnt.values())
    return Fraction(errors, n*r)


def descent_upper_bound(base: Game, lifted: Game, labels: tuple[int, ...], r: int):
    """Verified coefficient bound for any labeled r-cover.

    This uses that lifted edges are exactly r occurrences of each base edge,
    in order, and that the supplied labels are in consecutive vertex fibers.
    Caller is responsible for providing a valid covering map; checks for
    incidence consistency and duplicate-count grouping are supplied below.
    """
    n, m = base.vertices, len(base.edges)
    if m == 0 or lifted.vertices != n*r or len(lifted.edges) != m*r:
        raise ValueError("invalid sizes")
    if len(labels) != n*r:
        raise ValueError("labels must cover lifted vertices")
    degrees = [0] * n
    for u, v, _ in base.edges:
        degrees[u] += 1
        degrees[v] += 1
    for j, (u, v, s) in enumerate(base.edges):
        lifts = lifted.edges[j*r:(j+1)*r]
        if sorted(x[0] % r for x in lifts) != list(range(r)):
            raise ValueError("incomplete lifted source fibers")
        if sorted(x[1] % r for x in lifts) != list(range(r)):
            raise ValueError("incomplete lifted target fibers")
        for x, y, t in lifts:
            if x//r != u or y//r != v or t != s:
                raise ValueError("not a matched ordered cover")
    bad = sum(labels[x] ^ labels[y] != s for x, y, s in lifted.edges)
    bad_fraction = Fraction(bad, r*m)
    eta = descent_error(labels, n, r)
    return bad_fraction + Fraction(max(degrees)*n, m)*eta


def maxcut(vertices: int, pairs):
    return max(sum(a[u] != a[v] for u, v in pairs)
               for a in product((0, 1), repeat=vertices))
