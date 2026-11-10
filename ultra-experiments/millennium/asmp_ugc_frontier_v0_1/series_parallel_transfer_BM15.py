"""BM-15: exact sparse terminal-difference Fourier algebra for SP gain graphs.

A two-terminal series-parallel (SP) network has an ordered binary
construction tree of edges, series joins and parallel joins. The alphabet
is K=F2^s and each leaf is an oriented edge constraint with XOR gain.

For a registered Walsh subset S of Boolean satisfaction bits, define
f_N(d)=E[prod_{e in S}(1-2X_e) | a(t)^a(s)=d] over fresh, uniform
internal vertex labels. Every SP boundary message has the exact form
  f_N(d) = a + sum_g b[g] * 1[d=g].
Thus it is a uniform background plus finitely many gain-value spikes.

Leaf selected: (a=1, b[g]=-2); leaf omitted: (1,{}).
Parallel: pointwise multiplication (conditional independence).
Series: normalized K-convolution (uniform joined-terminal label).
For series messages (a,b) and (c,e):
  background=a*c + (a*sum(e)+c*sum(b))/q,
  spikes[k]=(sum_{g^h=k} b[g]*e[h])/q.
For parallel:
  background=a*c,
  spikes[k]=a*e[k]+c*b[k]+b[k]*e[k].

The unconditional Fourier coefficient is a+sum(b)/q. The exact oracle
needs no enumeration of q^|V| labelings, but its spike support CAN
grow exponentially in the tree size. It does not imply a compact full
mask-erasure LP or the BM-14 edge-exchangeability assumption.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product


@dataclass(frozen=True)
class SPNode:
    operation: str
    gain: int = 0
    left: "SPNode | None" = None
    right: "SPNode | None" = None

    @property
    def edges(self) -> int:
        if self.operation == "edge":
            return 1
        if self.operation not in ("series", "parallel") or (
            self.left is None or self.right is None
        ):
            raise ValueError("malformed two-terminal series-parallel expression")
        return self.left.edges + self.right.edges


def edge(gain: int) -> SPNode:
    if not isinstance(gain, int) or gain < 0:
        raise ValueError("edge gain must be a nonnegative integer")
    return SPNode("edge", gain)


def series(a: SPNode, b: SPNode) -> SPNode:
    if not isinstance(a, SPNode) or not isinstance(b, SPNode):
        raise ValueError("series operands must be SP expressions")
    return SPNode("series", left=a, right=b)


def parallel(a: SPNode, b: SPNode) -> SPNode:
    if not isinstance(a, SPNode) or not isinstance(b, SPNode):
        raise ValueError("parallel operands must be SP expressions")
    return SPNode("parallel", left=a, right=b)


@dataclass(frozen=True)
class SpikeMessage:
    """F(d)=background+spikes.get(d,0), coefficients exact rational."""
    background: Fraction
    spikes: dict[int, Fraction]

    def evaluate(self, d: int) -> Fraction:
        return self.background + self.spikes.get(d, Fraction(0))

    def average(self, q: int) -> Fraction:
        return self.background + sum(self.spikes.values(), Fraction(0)) / q

    @property
    def support_size(self) -> int:
        return len(self.spikes)


def _message(a: Fraction, spikes: dict[int, Fraction]) -> SpikeMessage:
    return SpikeMessage(Fraction(a), {g: Fraction(b) for g, b in spikes.items() if b})


def parallel_transfer(a: SpikeMessage, b: SpikeMessage) -> SpikeMessage:
    spikes = {}
    for g in a.spikes.keys() | b.spikes.keys():
        x, y = a.spikes.get(g, Fraction(0)), b.spikes.get(g, Fraction(0))
        spikes[g] = a.background * y + b.background * x + x * y
    return _message(a.background * b.background, spikes)


def series_transfer(a: SpikeMessage, b: SpikeMessage, q: int) -> SpikeMessage:
    if q < 2 or q & (q - 1):
        raise ValueError("q must be 2^s with s>=1")
    sa, sb = sum(a.spikes.values(), Fraction(0)), sum(b.spikes.values(), Fraction(0))
    base = a.background * b.background + (
        a.background * sb + b.background * sa
    ) / q
    spikes: dict[int, Fraction] = {}
    for x, u in a.spikes.items():
        for y, v in b.spikes.items():
            g = x ^ y
            spikes[g] = spikes.get(g, Fraction(0)) + u * v / q
    return _message(base, spikes)


def _validate_q(q: int) -> None:
    if not isinstance(q, int) or q < 2 or q & (q - 1):
        raise ValueError("alphabet q must be F2^s, s>=1")


def transfer(q: int, node: SPNode, subset: int) -> SpikeMessage:
    """Exact conditional Walsh message for arbitrary SP construction tree."""
    _validate_q(q)
    if not isinstance(node, SPNode) or not 0 <= subset < (1 << node.edges):
        raise ValueError("edge subset must fit the SP expression")
    if node.operation == "edge":
        if node.gain >= q:
            raise ValueError("edge gain outside alphabet")
        return _message(1, {node.gain: -2} if subset & 1 else {})
    if node.left is None or node.right is None:
        raise ValueError("malformed SP node")
    left_edges = node.left.edges
    l = transfer(q, node.left, subset & ((1 << left_edges) - 1))
    r = transfer(q, node.right, subset >> left_edges)
    if node.operation == "parallel":
        return parallel_transfer(l, r)
    if node.operation == "series":
        return series_transfer(l, r, q)
    raise ValueError("unknown SP operator")


def walsh(q: int, node: SPNode, subset: int) -> Fraction:
    return transfer(q, node, subset).average(q)


def _compile(node: SPNode):
    """Return nvertices, source=0,target=1, ordered (u,v,gain) leaves."""
    if node.operation == "edge":
        return 2, ((0, 1, node.gain),)
    if node.left is None or node.right is None:
        raise ValueError("malformed expression")
    n1, e1 = _compile(node.left)
    n2, e2 = _compile(node.right)
    if node.operation == "series":
        n = n1 + n2 - 1
        # Joined terminal takes index 2, final source/target remain 0/1.
        def left_map(x: int) -> int:
            return 0 if x == 0 else 2 if x == 1 else x + 1
        def right_map(x: int) -> int:
            return 2 if x == 0 else 1 if x == 1 else n1 + x - 1
    elif node.operation == "parallel":
        n = n1 + n2 - 2
        def left_map(x: int) -> int:
            return x
        def right_map(x: int) -> int:
            return x if x < 2 else n1 + x - 2
    else:
        raise ValueError("unknown SP operator")
    edges = tuple((left_map(u), left_map(v), g) for u, v, g in e1) + tuple(
        (right_map(u), right_map(v), g) for u, v, g in e2
    )
    if len(edges) != len(e1) + len(e2):
        raise AssertionError("edge order lost")
    return n, edges


def compile_game(q: int, node: SPNode):
    """Independent graph oracle with deterministic leaf/edge ordering."""
    _validate_q(q)
    try:
        from .finite_seed import Game
    except ImportError:
        from finite_seed import Game
    n, edges = _compile(node)
    return Game(n, q.bit_length() - 1, edges)


def direct_conditional(q: int, node: SPNode, subset: int, terminal_d: int) -> Fraction:
    """Brute-force reference; anchors source 0 and fixes target terminal_d."""
    g = compile_game(q, node)
    if not 0 <= subset < (1 << len(g.edges)) or not 0 <= terminal_d < q:
        raise ValueError("invalid edge subset or terminal difference")
    numerator = 0
    for interior in product(range(q), repeat=g.vertices - 2):
        labels = (0, terminal_d) + interior
        parity = sum(
            1 for i, (u, v, gain) in enumerate(g.edges)
            if (subset & (1 << i)) and ((labels[u] ^ labels[v]) == gain)
        ) % 2
        numerator += -1 if parity else 1
    return Fraction(numerator, q ** (g.vertices - 2))


def direct_walsh(q: int, node: SPNode, subset: int) -> Fraction:
    """Brute-force benchmark over terminal d and all internal labels."""
    return sum((direct_conditional(q, node, subset, d)
                for d in range(q)), Fraction(0)) / q


def selected_spike_profile(q: int, node: SPNode, subset: int):
    """Small exact receipt suitable for reproducibility and complexity audit."""
    m = transfer(q, node, subset)
    graph = compile_game(q, node)
    return {
        "vertices": graph.vertices,
        "edges": len(graph.edges),
        "q": q,
        "background": str(m.background),
        "spikes": tuple(sorted((g, str(v)) for g, v in m.spikes.items())),
        "conditional_support": m.support_size,
        "unconditional_walsh": str(m.average(q)),
        "enumerated_vertex_labelings": 0,
        "full_label_space": f"{q}^{graph.vertices}",
    }
