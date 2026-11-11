"""Exact ASMP-13/14 boundary examples.

The inference part is classical cycle-code coset decoding; the spectral and
binary-channel visibility statements apply only to the frozen observation
grammar and do not establish claims about physical model monitoring.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import product
from math import comb

try:
    from .finite_seed import Game, forest
except ImportError:
    from finite_seed import Game, forest


def full_cycle_pattern_counts(length: int, q: int, *, flat: bool) -> dict[tuple[bool, ...], int]:
    """Closed-form counts for Boolean satisfaction patterns of one cycle.

    Each pattern with k unsatisfied edges occurs N_k times in the residual
    space, where N_k = ((q-1)^k + (q-1)(-1)^k)/q when flat,
    and N_k = ((q-1)^k - (-1)^k)/q when frustrated.

    The law gives probability count/q^(length-1) for each pattern.
    """
    if length < 1 or q < 2:
        raise ValueError("positive cycle length and alphabet >=2 required")
    counts: dict[tuple[bool, ...], int] = {}
    for bits in product((False, True), repeat=length):
        k = bits.count(False)
        numerator = (q-1)**k + ((q-1) if flat else -1) * (-1)**k
        if numerator % q:
            raise AssertionError("character-sum formula must give integer counts")
        count = numerator // q
        if count < 0:
            raise AssertionError("probability count must be nonnegative")
        if count:
            counts[bits] = count
    if sum(counts.values()) != q**(length-1):
        raise AssertionError("cycle residuals must have q^(length-1) possibilities")
    return counts


def full_cycle_law(length: int, q: int, *, flat: bool) -> dict[tuple[bool, ...], Fraction]:
    denom = q**(length-1)
    return {p: Fraction(n, denom) for p, n in full_cycle_pattern_counts(length, q, flat=flat).items()}


def tv_distance(a: dict, b: dict) -> Fraction:
    """Total variation on union of two finite discrete supports."""
    return sum((abs(a.get(p, Fraction(0)) - b.get(p, Fraction(0)))
                for p in a.keys() | b.keys()), Fraction(0)) / 2


def cycle_tv_formula(length: int, q: int) -> Fraction:
    """Exactly TV between flat and any nonzero-holonomy q-cycle bit patterns."""
    if length < 1 or q < 2:
        raise ValueError("length>=1, q>=2")
    return Fraction(2, q) ** (length-1)


def minimum_iid_replicates_by_coupling(length: int, q: int, advantage: Fraction) -> int:
    """Necessary iid samples to achieve Bayes success >= 1/2 + advantage.

    Derived from TV(P^N,Q^N) <= N*TV(P,Q). Bound is necessary,
    not sufficient and generally not optimal.
    """
    if not 0 < advantage < Fraction(1, 2):
        raise ValueError("advantage must lie strictly between 0 and 1/2")
    # N >= 2*advantage / delta.
    delta = cycle_tv_formula(length, q)
    ratio = 2 * advantage / delta
    return (ratio.numerator + ratio.denominator - 1) // ratio.denominator


def noisy_binary_cycle_tv(length: int, flip_probability: Fraction) -> Fraction:
    """Exact TV of parity-coset law after iid binary symmetric noise.

    Only valid for q=2 and *jointly* observed cycle bits; no observation
    chaining from independent labelings is assumed.
    """
    eta = Fraction(flip_probability)
    if length < 1 or not 0 <= eta <= 1:
        raise ValueError("valid length and binary flip probability required")
    return abs(1-2*eta)**length


def apply_bsc(law: dict[tuple[bool, ...], Fraction], eta: Fraction):
    if not law:
        raise ValueError("nonempty input law")
    eta = Fraction(eta)
    if not 0 <= eta <= 1:
        raise ValueError("flip probability must lie in [0,1]")
    ell = len(next(iter(law)))
    if any(len(bits) != ell for bits in law):
        raise ValueError("all patterns must have same length")
    out = {}
    for output in product((False, True), repeat=ell):
        out[output] = sum((
            prob * eta**sum(x != y for x,y in zip(input_,output)) *
            (1-eta)**sum(x == y for x,y in zip(input_,output))
            for input_, prob in law.items()
        ), Fraction(0))
    return out


def exact_forest_chord_decoder(game: Game) -> tuple[int, tuple[int, ...]]:
    """FPT in q and cycle rank: O(q^(2 beta1) * m*q²), plus bookkeeping.

    Enumerate labels only at chord endpoints. For each boundary assignment,
    minimize violated forest constraints by tree DP. Chord costs are then
    fixed. Loops, parallel edges and disconnected components are supported.
    The returned witness is a full labeling attaining the minimum cost.
    """
    q, n, m = game.q, game.vertices, len(game.edges)
    _, tree, _ = forest(game)
    chords = [i for i in range(m) if i not in tree]
    boundary = tuple(sorted({
        x for i in chords for x in game.edges[i][:2]
    }))
    children: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for i in tree:
        u, v, shift = game.edges[i]
        children[u].append((v, shift))
        children[v].append((u, shift))
    best_cost = m + 1
    best_assignment: tuple[int, ...] = ()
    # All rooted forest components; traversal order guarantees child-after-parent.
    parents = [-1] * n
    roots: list[int] = []
    order: list[int] = []
    directed_children: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for root in range(n):
        if parents[root] != -1:
            continue
        parents[root] = root
        roots.append(root)
        todo = [root]
        for u in todo:
            order.append(u)
            for v, shift in children[u]:
                if parents[v] == -1:
                    parents[v] = u
                    directed_children[u].append((v, shift))
                    todo.append(v)
    for values in product(range(q), repeat=len(boundary)):
        fixed = dict(zip(boundary, values))
        chord_cost = sum(
            (fixed[game.edges[i][0]] ^ fixed[game.edges[i][1]]) != game.edges[i][2]
            for i in chords
        )
        if chord_cost >= best_cost:
            continue
        costs = [[m+1] * q for _ in range(n)]
        # Keep the minimizing child label for each parent-label choice.
        argmins: list[list[list[int]]] = [[] for _ in range(n)]
        for u in reversed(order):
            allowed = [fixed[u]] if u in fixed else range(q)
            for x in allowed:
                cost = 0
                for v, shift in directed_children[u]:
                    target = x ^ shift
                    y = min(range(q), key=lambda y: (costs[v][y] + (y != target), y))
                    cost += costs[v][y] + (y != target)
                costs[u][x] = cost
        total = chord_cost + sum(min(costs[root]) for root in roots)
        if total < best_cost:
            best_cost = total
            labels = [0]*n
            for root in roots:
                labels[root] = min(range(q), key=lambda x: (costs[root][x],x))
            for u in order:
                for v, shift in directed_children[u]:
                    target = labels[u] ^ shift
                    labels[v] = min(range(q), key=lambda y: (costs[v][y] + (y != target), y))
            best_assignment = tuple(labels)
    if not best_assignment or sum(
        best_assignment[u] ^ best_assignment[v] != shift
        for u,v,shift in game.edges
    ) != best_cost:
        raise AssertionError("forest/chord decoder witness check failed")
    return best_cost, best_assignment
