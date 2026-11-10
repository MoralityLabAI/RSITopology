"""BM-21: compressed Fourier discrepancy circuits on cactus gain graphs.

Fixed observations: each vertex label is a fresh independent uniform
element of K=F2^s (q>=2); each observed Boolean edge bit is satisfaction.
The two hypotheses are flat gain 0 versus the registered connection c.
A 'cactus' is a connected SIMPLE graph whose cycles share no edges and
meet at at most one vertex; all cyclic blocks are simple cycles.

The graph's satisfaction laws factor over cycle blocks and bridge edges.
For any Walsh edge subset S, their coefficients are products of exact
cycle coefficients and alpha=1-2/q on selected bridges.

A UNICYCLE with an unbalanced cycle C and t bridges has
    Delta(S)=(-2)^|C|/q^(|C|-1) * alpha^|S\\C|   if C subset S,
             0                                otherwise.
For q>2, its exact residual Fourier support (under identity readout
masks) is the upward cone {S: C subset S}, of cardinality 2^t.
For q=2 it consists only of C. Therefore a graph with treewidth two
and m=t+|C| edges can have exponentially many Fourier discrepancies,
and the support hypergraph can contain the full m-edge clique.

Despite that explosion, a COMMON independent XOR postprocessor erases
the full flat/other laws at sharp per-bit rate
    max_{C unbalanced} 1/(2|C|),
attained by independent random-one-hot parity erasers on each unbalanced
cycle. A per-cycle Walsh parity union bound proves optimality for common
postprocessing, even allowing correlated masks across all blocks.
This is not the hypothesis-aware BM-08 optimum (smaller for q>=8).

The circuit also gives O(#cyclic-blocks+#bridges) *membership queries*
for arbitrary residual S on a cactus, without listing all S.
For arbitrary explicit hypothesis-dependent masks Q0/Q1, multiplying
these coefficients by each mask Walsh transform provides an exact
residual-membership oracle without an exhaustive Fourier table.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from fractions import Fraction
from itertools import product

try:
    from .finite_seed import Game, forest
except ImportError:
    from finite_seed import Game, forest


@dataclass(frozen=True)
class CycleBlock:
    edge_mask: int
    gain: int

    @property
    def length(self)->int:
        return self.edge_mask.bit_count()


@dataclass(frozen=True)
class CactusCircuit:
    q: int
    vertices: int
    edge_count: int
    cycles: tuple[CycleBlock,...]
    bridge_mask: int

    @property
    def unbalanced(self)->tuple[CycleBlock,...]:
        return tuple(c for c in self.cycles if c.gain)

    @property
    def cycle_rank(self)->int:
        return len(self.cycles)

    @property
    def common_erasure_cap(self)->Fraction:
        return max((Fraction(1,2*c.length) for c in self.unbalanced),
                   default=Fraction(0))

    def fourier(self,subset:int,*,frustrated:bool=False)->Fraction:
        """Exact full Boolean satisfaction Walsh coefficient for a cactus."""
        if not isinstance(subset,int) or not 0<=subset<(1<<self.edge_count):
            raise ValueError("Fourier subset outside observed edges")
        alpha=Fraction(self.q-2,self.q)
        out=alpha**(subset&self.bridge_mask).bit_count()
        for cycle in self.cycles:
            selected=(subset&cycle.edge_mask).bit_count()
            if selected<cycle.length:
                out*=alpha**selected
            else:
                a=alpha**cycle.length
                t=Fraction(-2,self.q)**cycle.length
                out*= a-t if frustrated and cycle.gain else a+(self.q-1)*t
        return out

    def delta(self,subset:int)->Fraction:
        """Flat minus registered connection, including exact cancellations."""
        return self.fourier(subset)-self.fourier(subset,frustrated=True)

    def residual_support_member(self,subset:int)->bool:
        return bool(self.delta(subset))

    def residual_from_mask_pair(
        self,subset:int,q0:dict[int,int],q1:dict[int,int],denominator:int
    )->Fraction:
        """Exact post-readout discrepancy for explicit independent masks."""
        if denominator<=0 or any(sum(q.values())!=denominator or
                any(not 0<=x<(1<<self.edge_count) or v<0 or
                    not isinstance(x,int) or not isinstance(v,int)
                    for x,v in q.items()) for q in (q0,q1)):
            raise ValueError("invalid normalized correlated XOR masks")
        def mask_hat(weights):
            return Fraction(sum(
                (-v if (mask&subset).bit_count()%2 else v)
                for mask,v in weights.items()
            ),denominator)
        return self.fourier(subset)*mask_hat(q0)-self.fourier(
            subset,frustrated=True
        )*mask_hat(q1)

    def symbolic_receipt(self)->dict[str,object]:
        """No expansion of exponentially large Fourier support or masks."""
        t=self.bridge_mask.bit_count()
        return {
            "vertices":self.vertices,"edges":self.edge_count,
            "cycle_rank":self.cycle_rank,
            "bridge_edges":t,
            "cycle_lengths":tuple(c.length for c in self.cycles),
            "cycle_gain_zero":tuple(c.gain==0 for c in self.cycles),
            "exact_common_erasure_cap":str(self.common_erasure_cap),
            "unicyclic_support_count":(
                self.unicyclic_support_count() if self.cycle_rank==1 else None
            ),
            "explicit_Fourier_table_constructed":False,
            "explicit_2_to_m_mask_distribution_constructed":False,
        }

    def unicyclic_support_count(self)->int:
        if len(self.cycles)!=1:
            raise ValueError("unicyclic support count needs exactly one cycle")
        if not self.cycles[0].gain:
            return 0
        if self.q==2:
            return 1
        return 1<<self.bridge_mask.bit_count()

    def unicyclic_cone_member(self,subset:int)->bool:
        """O(1) compressed support membership for a single unbalanced cycle."""
        if len(self.cycles)!=1:
            raise ValueError("unicyclic cone applies to one cycle")
        if not 0<=subset<1<<self.edge_count:
            raise ValueError("subset outside edge reports")
        c=self.cycles[0]
        if not c.gain or (subset&c.edge_mask)!=c.edge_mask:
            return False
        return self.q>2 or (subset&self.bridge_mask)==0


def _validate_simple_connected(game:Game)->None:
    if not isinstance(game,Game):
        raise ValueError("Game required")
    pairs=set()
    for u,v,_ in game.edges:
        if u==v or (min(u,v),max(u,v)) in pairs:
            raise ValueError("cactus oracle requires simple nonloop graph")
        pairs.add((min(u,v),max(u,v)))
    _,_,components=forest(game)
    if components!=1:
        raise ValueError("connected graph required")


def compile_cactus(game:Game)->CactusCircuit:
    """Extract edge-disjoint fundamental cycles; reject shared-edge cycles.

    BFS paths in the spanning tree yield each fundamental cycle. In a
    cactus these paths have disjoint edge sets; a shared edge witnesses
    failure of the cactus condition. Graph and labels are small encoded
    objects: no q^|V| vertex enumeration occurs.
    """
    _validate_simple_connected(game)
    n,m=game.vertices,len(game.edges)
    _,tree,_=forest(game)
    adj=[[] for _ in range(n)]
    for i in tree:
        u,v,_=game.edges[i]
        adj[u].append((v,i))
        adj[v].append((u,i))
    used=0
    blocks=[]
    for i,(source,target,gain) in enumerate(game.edges):
        if i in tree:
            continue
        parents={source:(-1,-1)}
        queue=deque([source])
        while queue and target not in parents:
            v=queue.popleft()
            for nxt,edge_id in adj[v]:
                if nxt not in parents:
                    parents[nxt]=(v,edge_id)
                    queue.append(nxt)
        if target not in parents:
            raise AssertionError("spanning tree missed a graph path")
        cycle=1<<i
        node=target
        while node!=source:
            ancestor,edge_id=parents[node]
            cycle|=1<<edge_id
            node=ancestor
        if cycle.bit_count()<3:
            raise AssertionError("simple cycles must have >=3 edges")
        if used&cycle:
            raise ValueError("overlapping cycles: graph is not a cactus")
        used|=cycle
        gain_xor=0
        for edge_id in range(m):
            if cycle&(1<<edge_id):
                gain_xor ^= game.edges[edge_id][2]
        blocks.append(CycleBlock(cycle,gain_xor))
    blocks.sort(key=lambda c:(c.edge_mask&-c.edge_mask).bit_length())
    return CactusCircuit(game.q,n,m,tuple(blocks),((1<<m)-1)^used)


def one_hot_cycle_sampler(circuit:CactusCircuit,rng)->int:
    """Sample a completed mask in O(sum unbalanced cycle lengths) time."""
    result=0
    for block in circuit.unbalanced:
        if rng.randrange(2):
            edges=[i for i in range(circuit.edge_count)
                   if block.edge_mask&(1<<i)]
            result |= 1<<edges[rng.randrange(len(edges))]
    return result


def explicit_common_eraser(circuit:CactusCircuit, *,
                           max_edges:int=14)->dict[int,Fraction]:
    """Enumerate a common legal erasing distribution only for small checks."""
    if circuit.edge_count>max_edges:
        raise ValueError("explicit mask distribution exceeds resource cap")
    law={0:Fraction(1)}
    for block in circuit.unbalanced:
        choices={0:Fraction(1,2)}
        for i in range(circuit.edge_count):
            if block.edge_mask&(1<<i):
                choices[1<<i]=Fraction(1,2*block.length)
        out={}
        for a,pa in law.items():
            for b,pb in choices.items():
                if a&b:
                    raise AssertionError("cactus cycles must be edge-disjoint")
                x=a|b
                out[x]=out.get(x,Fraction(0))+pa*pb
        law=out
    if sum(law.values(),Fraction(0))!=1:
        raise AssertionError("common mask law normalization")
    assert all(sum((p for mask,p in law.items() if mask&(1<<i)),
                   Fraction(0))<=circuit.common_erasure_cap
               for i in range(circuit.edge_count))
    return law


def common_eraser_dual_lower(circuit:CactusCircuit)->Fraction:
    """Universal common-mask lower bound using one unbalanced cycle parity.

    For each unbalanced cycle C, flat and registered coefficient differ
    on exactly C. Equalization by the SAME mask R demands hatR(C)=0.
    Thus 1/2=P(odd mask parity on C)<=sum_(i in C) P(M_i=1)
         <= |C|*max_i P(M_i=1).
    """
    for block in circuit.unbalanced:
        if circuit.delta(block.edge_mask)!=Fraction((-2)**block.length,
                                                   circuit.q**(block.length-1)):
            raise AssertionError("unexpected exact cycle character difference")
    return circuit.common_erasure_cap


def verify_common_eraser_small(circuit:CactusCircuit)->bool:
    """Exact full 2^m Fourier law equality after common XOR mask."""
    R=explicit_common_eraser(circuit)
    for S in range(1<<circuit.edge_count):
        hatR=sum((p*(-1 if (mask&S).bit_count()%2 else 1)
                  for mask,p in R.items()),Fraction(0))
        if circuit.delta(S)*hatR:
            raise AssertionError("mask failed at Fourier subset "+str(S))
    return True


def make_triangle_with_bridges(t:int,*,q:int=4,shift:int=1)->Game:
    """Construct connected simple tw=2 unicyclic examples of unbounded size."""
    if not isinstance(t,int) or t<0 or q<2 or q&(q-1) or not 0<=shift<q:
        raise ValueError("invalid bridge count, alphabet or cycle shift")
    edges=[(0,1,0),(1,2,0),(2,0,shift)]
    for j in range(t):
        edges.append((2+j,3+j,0))
    return Game(3+t,q.bit_length()-1,tuple(edges))
