# ASMP-9 v0.20 theory draft: block factorization beyond cactus cores

Status: development-only; not registered and not claim-eligible.

## Setup

Inherit the v0.17-v0.19 independent Bernoulli comparison model and the event
that every original nonbridge edge lies on a directed residual cycle.

Delete original bridges and decompose each remaining connected component into
its vertex-biconnected edge blocks:

```text
B_1,...,B_q.
```

The blocks partition the cyclic edges and intersect only at articulation
vertices. The block-cut incidence graph is a forest.

## Candidate theorem 1: deterministic block liveness

For every ternary residual edge-status vector:

```text
full quotient liveness on G
iff
the residual digraph induced by every B_j is strongly connected.
```

### Lemma: outside excursions return to the same block vertex

Let `B` be a nontrivial block and let a walk leave `B` at `a`, use at least
one edge outside `B`, and first return to `B` at `b`. Then `a=b`.

If `a` and `b` were distinct, the outside subwalk contains an undirected
`a`-to-`b` path whose internal vertices are outside `B`. Combining a simple
subpath of it with any `a`-to-`b` path in the connected block produces a
simple cycle containing an outside edge and an edge of `B`. Every edge of a
simple cycle lies in one vertex-biconnected block, contradicting the
maximality and edge partition of the block decomposition. Equivalently, the
same contradiction is a cycle in the block-cut forest.

Consequently, every directed path between vertices of `B` can be converted
to a directed path wholly inside `B` by deleting its maximal outside
excursions.

### Proof of the equivalence

Assume full quotient liveness. For every edge `{u,v}` in a nontrivial block,
the registered liveness criterion says `u` and `v` lie in the same residual
strong component, so there are residual paths `u -> v` and `v -> u` in the
full graph. The lemma projects both paths into `B`. Because the undirected
block is connected, concatenating these within-block paths along any
undirected path in `B` makes every two vertices mutually reachable. Thus the
residual digraph induced by `B` is strongly connected.

Conversely, if every nontrivial block is residual-strongly-connected, the
endpoints of every original nonbridge edge are mutually reachable inside
their unique nontrivial block. This is exactly the full-quotient liveness
criterion. Singleton bridge blocks are absent from the quotient and impose no
condition.

The statement is a classical block-decomposition fact specialized to the
registered residual-liveness event.

## Candidate theorem 2: exact probability factorization

For any fixed positive edge allocation and fixed endpoint probabilities:

```text
F_G(n,p) = product_j F_Bj(n restricted to B_j, p restricted to B_j).
```

The deterministic success event is the intersection of block-local events on
disjoint edge sets. Under independent edge responses their probabilities
multiply.

For a rectangular endpoint-label adversary the worst case also separates:

```text
min_labels F_G(n,labels)
  = product_j min_(labels on B_j) F_Bj(n_Bj,labels_Bj).
```

Original bridges affect neither factor.

The minimum identity follows because block factors are nonnegative and the
endpoint-label universe is a Cartesian product over disjoint block edge sets.
For every global label assignment the product is at least the product of the
blockwise minima, and concatenating one minimizing label assignment from each
block attains that bound.

## Candidate corollary 3: exact global resource allocation

Let

```text
f_B(t)
```

be the exact block-local maximin availability using `t` positive integer
trials. No closed form or polynomial algorithm for `f_B` is assumed.

After assigning one mandatory trial to each bridge, the exact global problem
is:

```text
maximize  product_j f_Bj(N_j)

subject to

  N_j >= |E(B_j)|,
  sum_j N_j = N - number_of_bridges.
```

The same Bellman recursion as v0.19 solves allocation *between* blocks once
the local tables are known. Cactus cores are the special case in which every
block is a simple cycle and v0.16 supplies each table efficiently.

This reduction does not solve the local reliability-design problem inside a
general biconnected block. A graph whose cyclic core is one biconnected block
receives no computational simplification.

## Development evidence

Before any registration:

- three hand-built articulation graphs (two diamonds, `K4` plus a triangle,
  and a theta block plus a triangle) showed zero mismatches over `98,415`
  ternary residual states;
- a central cycle with attachments at two different articulation vertices
  and two cyclic components separated by an ignored bridge were added as
  explicit hostile tests;
- an independent NetworkX graph-atlas sweep checked 96 connected graphs with
  three to six vertices and at most nine edges, including eight multiblock
  graphs, over `636,606` status vectors with zero mismatches; and
- exact rational availability on a two-diamond one-point union equaled the
  product of its two block availabilities.

The complete reproducible development receipt is
`artifacts_v0_20/development_census.json`. Its SHA-256 is
`ba0a768ff6179257196c91e161af2b17f6185965553ea725172af974fdba17ac`.

Every development graph and parameter cell is burned.

## Claim boundary

If prospectively registered and independently verified, v0.20 would extend
the exact factorization and between-component allocation theorem from cactus
cycles to arbitrary vertex-biconnected blocks. The block decomposition and
classical reliability-product principle are not claimed as new.

It would not give an efficient exact local design algorithm for general
biconnected blocks, a complexity classification, adaptive allocation,
dependent-response robustness, behavioral reward identification, general
inverse reinforcement learning, or a resolution of ASMP-9.
