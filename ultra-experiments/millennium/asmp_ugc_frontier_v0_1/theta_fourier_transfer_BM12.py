"""BM-12: finite Walsh transfer oracle for parallel u-v path gain graphs.

A theta/network consists of k >=2 internally vertex-disjoint paths from u
to v, with positive edge lengths L_i and K=F2^s gain g_i along each path.
All Boolean satisfied-edge patterns are evaluated on independent fresh
uniform vertex labels.

For each Walsh query subset S, a proper subset of path i contributes
(1-2/q)^|S_i|. A complete path contributes a_i+b_i*1[d=g_i] given
the shared endpoint difference d, where
    a_i=(1-2/q)^L_i - (-2/q)^L_i,
    b_i=(-2)^L_i / q^(L_i-1).
Average over uniform d. Expanding equality events gives an exact
2^k-subset computation, independent of the number of vertex labelings.

This is an exact coefficient oracle, not a sparse optimal-dual theorem.
The equality partition of path gains determines every coefficient.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product

try:
    from .finite_seed import Game
except ImportError:
    from finite_seed import Game


def _validate(q:int,lengths:tuple[int,...],gains:tuple[int,...]) -> None:
    if q < 2 or q&(q-1) or len(lengths)<2 or len(gains)!=len(lengths):
        raise ValueError("q=2^s, >=2 paths, matching gains required")
    if any(n<1 for n in lengths) or any(not 0<=g<q for g in gains):
        raise ValueError("path lengths positive and gains in F2^s")


def theta_path_game(
    q:int,lengths:tuple[int,...],gains:tuple[int,...]
) -> Game:
    """Build paths with endpoint vertices 0 and 1, edges in path order."""
    _validate(q,lengths,gains)
    edges=[]
    next_vertex=2
    for n,gain in zip(lengths,gains):
        prev=0
        for j in range(n):
            nxt=(1 if j==n-1 else next_vertex)
            if j<n-1:
                next_vertex+=1
            edges.append((prev,nxt,gain if j==0 else 0))
            prev=nxt
    return Game(next_vertex,q.bit_length()-1,tuple(edges))


def theta_walsh_transfer(
    q:int,lengths:tuple[int,...],gains:tuple[int,...],subset:int
) -> Fraction:
    """Exact full-satisfaction Walsh Fourier coefficient at edge subset S.

    Complexity O(k*2^k + log L_i bit operations) with k the number of
    u-v paths. No loop over q alphabet values or vertex labelings is used.
    """
    _validate(q,lengths,gains)
    edges=sum(lengths)
    if not 0<=subset<(1<<edges):
        raise ValueError("Walsh edge subset outside path network")
    independent=Fraction(1)
    complete=[]
    offset=0
    h=Fraction(1)-Fraction(2,q)
    for i,(n,g) in enumerate(zip(lengths,gains)):
        local=(subset>>offset)&((1<<n)-1)
        count=local.bit_count()
        if count==n:
            a=h**n - Fraction(-2,q)**n
            b=Fraction((-2)**n,q**(n-1))
            complete.append((g,a,b))
        else:
            independent*=h**count
        offset+=n
    # Endpoint difference d is uniform over K. Empty selection contributes
    # prod a_i. Nonempty selections of equal-gain paths contribute 1/q.
    value=Fraction(1)
    for _,a,_ in complete:
        value*=a
    for size in range(1,len(complete)+1):
        for indices in combinations(range(len(complete)),size):
            if any(complete[j][0]!=complete[indices[0]][0]
                   for j in indices[1:]):
                continue
            included=set(indices)
            term=Fraction(1,q)
            for j,(_,a,b) in enumerate(complete):
                term*=b if j in included else a
            value+=term
    return independent*value


def theta_walsh_direct(
    game: Game,subset:int
) -> Fraction:
    """Independent full-label enumeration oracle (exponential in vertices)."""
    if not 0<=subset<1<<len(game.edges):
        raise ValueError("invalid queried edge set")
    count=0
    for labels in product(range(game.q), repeat=game.vertices):
        yes=sum(1<<i for i,(u,v,shift) in enumerate(game.edges)
                if labels[u]^labels[v]==shift)
        count+=(-1 if (yes&subset).bit_count()%2 else 1)
    return Fraction(count,game.q**game.vertices)


def theta_walsh_from_counts(
    counts:tuple[int,...], subset:int, denominator:int
) -> Fraction:
    """Independent fast direct-count Fourier oracle, exact integer numerator."""
    if denominator<1 or not counts or len(counts)&(len(counts)-1):
        raise ValueError("counts must span a power-of-two observation space")
    if not 0<=subset<len(counts):
        raise ValueError("invalid Fourier index")
    return Fraction(sum(
        (-1 if (mask&subset).bit_count()%2 else 1)*v
        for mask,v in enumerate(counts)
    ),denominator)


def theta_observation_counts(game: Game) -> tuple[int,...]:
    """Generate a complete Boolean pattern census once, for small tests."""
    n=1<<len(game.edges)
    out=[0]*n
    for labels in product(range(game.q),repeat=game.vertices):
        index=sum(1<<i for i,(u,v,shift) in enumerate(game.edges)
                  if labels[u]^labels[v]==shift)
        out[index]+=1
    if sum(out)!=game.q**game.vertices:
        raise AssertionError("vertex census normalization")
    return tuple(out)


def gain_equality_signature(gains:tuple[int,...]) -> tuple[int,...]:
    """Canonical partition of paths by their gain-equality classes."""
    seen={}
    signature=[]
    for value in gains:
        if value not in seen:
            seen[value]=len(seen)
        signature.append(seen[value])
    return tuple(signature)


def transfer_manifest(q:int,lengths:tuple[int,...],gains:tuple[int,...]):
    """Small exact metadata for registered theta and diamond transfer cases."""
    game=theta_path_game(q,lengths,gains)
    return {
        "q":q,"path_lengths":lengths,
        "gain_partition":gain_equality_signature(gains),
        "vertices":game.vertices,"edges":len(game.edges),
        "full_walsh":str(theta_walsh_transfer(q,lengths,gains,
                                            (1<<len(game.edges))-1)),
        "evaluated_alphabet_states":0,
        "coefficient_subsets_max":1<<len(lengths),
    }
