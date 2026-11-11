"""ASMP-14 active intervention tomography for hidden F2^s cycle gains.

A declared controllable shift on one edge turns each exact balancedness query
into a K-valued *equality* test for that cycle's unknown holonomy.
Availability and physical cost of such interventions must be registered.
"""
from __future__ import annotations

from fractions import Fraction

try:
    from .finite_seed import Game, cycle_signature, forest
except ImportError:
    from finite_seed import Game, cycle_signature, forest


def intervene_edge(game: Game, index: int, delta: int) -> Game:
    """Apply a declared, known additive translation to one edge occurrence."""
    if not 0 <= index < len(game.edges) or not 0 <= delta < game.q:
        raise ValueError("invalid edge or F2^s translation")
    return Game(game.vertices, game.bits, tuple(
        (u, v, shift ^ delta if i == index else shift)
        for i, (u, v, shift) in enumerate(game.edges)
    ))


def joint_success_probability(game: Game, observed_edges: tuple[int, ...]) -> Fraction:
    """Probability all selected edges are satisfied by a uniform labeling."""
    if len(set(observed_edges)) != len(observed_edges) or any(
        not 0 <= i < len(game.edges) for i in observed_edges
    ):
        raise ValueError("observed edge indices must be distinct and valid")
    sub = Game(game.vertices, game.bits, tuple(game.edges[i] for i in observed_edges))
    if any(hol for _, hol in cycle_signature(sub)):
        return Fraction(0)
    _, _, components = forest(sub)
    return Fraction(1, game.q ** (game.vertices - components))


def _validate_simple_cycle(game: Game, indices: tuple[int, ...]) -> None:
    if not indices or len(set(indices)) != len(indices) or any(
        not 0 <= i < len(game.edges) for i in indices
    ):
        raise ValueError("cycle indices must be distinct and valid")
    # Connected and every participating vertex has degree two. A self-loop
    # contributes 2, and two parallel edges form a valid 2-edge cycle.
    adjacency: dict[int, set[int]] = {}
    deg: dict[int, int] = {}
    for idx in indices:
        u, v, _ = game.edges[idx]
        deg[u] = deg.get(u,0)+1
        deg[v] = deg.get(v,0)+1
        adjacency.setdefault(u,set()).add(v)
        adjacency.setdefault(v,set()).add(u)
    if any(d!=2 for d in deg.values()):
        raise ValueError("edge subset is not a simple cycle")
    seen={next(iter(deg))}
    todo=list(seen)
    for u in todo:
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    if seen != set(deg):
        raise ValueError("edge subset is not connected")


def exact_cycle_equality_probe(
    game: Game, cycle_edges: tuple[int,...], controlled_edge: int, delta: int
) -> bool:
    """In ideal infinite-data mode: does shift delta flatten a registered cycle?"""
    _validate_simple_cycle(game,cycle_edges)
    if controlled_edge not in cycle_edges:
        raise ValueError("controlled edge must belong to queried cycle")
    modified=intervene_edge(game,controlled_edge,delta)
    return joint_success_probability(modified,cycle_edges)>0


def recover_cycle_holonomy(
    game: Game, cycle_edges: tuple[int,...], controlled_edge: int
) -> tuple[int,int]:
    """Recover numerical holonomy from ideal equality-only balance queries.

    q-1 tests suffice in the worst case; if all fail, the final candidate
    is uniquely determined. Worst-case q-1 is also an equality-query lower
    bound for an adversarial unknown element of a q-element set.
    """
    for x in range(game.q-1):
        if exact_cycle_equality_probe(game,cycle_edges,controlled_edge,x):
            return x, x+1
    return game.q-1, game.q-1


def all_success_episodes_for_one_sided_power(
    length: int, alphabet: int, failure_target: Fraction
) -> int:
    """Sufficient i.i.d. samples to observe >=1 all-satisfied balanced cycle.

    For a true balanced length-L simple cycle this event has probability
    q^(1-L) per fresh uniform labeling. An unbalanced cycle never produces it.
    The returned N is minimal for miss probability (1-q^(1-L))^N <= target.
    """
    if length < 1 or alphabet < 2:
        raise ValueError("positive cycle length and nontrivial alphabet required")
    target=Fraction(failure_target)
    if not 0 < target < 1:
        raise ValueError("failure target must lie strictly between zero and one")
    chance=Fraction(1,alphabet**(length-1))
    miss=Fraction(1)
    n=0
    while miss>target:
        miss*=1-chance
        n+=1
    return n
