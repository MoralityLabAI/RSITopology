# ASMP-9 v0.18 formulation draft: bonds of the cyclic core

Status: development-only; not registered and not claim-eligible.

## Setup

Let `G=(V,E)` be a finite undirected simple graph with at least one cycle.
Fix an arbitrary reference orientation of every edge. A ternary residual
status assigns to each edge:

```text
Z: reference arc only
I: both arcs
F: reverse arc only.
```

The v0.17 residual-rank theorem says that full conditional-fiber quotient rank
is available exactly when every original nonbridge edge lies on a directed
residual cycle.

Delete every original bridge of `G`. Call the resulting graph `K`; isolated
vertices are harmless. Every edge-containing connected component of `K` is
bridgeless. Call these the cyclic-core components.

A **bond** of a connected graph is an inclusion-minimal nonempty edge cut.
Equivalently, a cut `delta(S)` is a bond exactly when both induced sides are
connected.

## Theorem 1: full liveness is componentwise strong connectivity

Full conditional-fiber quotient rank is available if and only if the residual
digraph restricted to every cyclic-core component is strongly connected.

### Proof

In a finite digraph an arc lies on a directed cycle exactly when its endpoints
belong to one strongly connected component. Every core edge must lie on such a
cycle by the v0.17 criterion. Hence the endpoints of every core edge belong to
one residual strongly connected component. Connectivity of each undirected
core component then forces all its vertices into one residual strongly
connected component.

Conversely, strong connectivity of a core component puts the endpoints of
every one of its edges in the same residual strongly connected component, so
every core edge lies on a directed residual cycle. Original bridges do not
contribute to cycle rank and cannot provide a route that leaves and re-enters a
core component, because such a route would put the bridge on an undirected
cycle. QED.

## Theorem 2: the minimal bad supports are exactly bonds

Let a boundary support be the set of edges assigned `Z` or `F`; all other
edges are `I`. Call a support bad if some orientation of its boundary edges
destroys full quotient rank. Then the inclusion-minimal bad supports are
exactly the bonds of the cyclic-core components, expressed in the original
edge index set.

### Proof

First take a bond `B=delta(S)` in one cyclic-core component. Assign every edge
of `B` a single residual arc directed from `S` to its complement, and assign
every other core edge status `I`. There is then no residual arc across the cut
in the reverse direction, so the component is not strongly connected.
Therefore `B` is bad.

No proper subset of `B` is bad. If a residual digraph fails strong
connectivity, a source or sink strongly connected component in its
condensation exposes a nonempty cut all of whose crossing edges are
single-arc boundary edges. Thus every bad support contains a nonempty edge
cut. But a proper subset of a bond contains no nonempty cut, by the
inclusion-minimal definition of a bond.

Conversely, let `A` be an inclusion-minimal bad support. By the preceding
condensation argument, `A` contains a nonempty cut `C` of some cyclic-core
component. Every nonempty cut of a connected graph contains an
inclusion-minimal nonempty cut, hence a bond `B subseteq C subseteq A`.
The first paragraph shows that `B` is itself bad. Minimality of `A` therefore
forces `A=B`. QED.

## Corollary 3: the exponent is a classical max-min cut design

For a nonnegative allocation `w` with total mass one, the v0.17 exponent
parameter becomes

```text
tau_G(w)
  = min over cyclic-core components H
      min over nontrivial cuts delta_H(S)
          sum_(e in delta_H(S)) w_e.
```

It is enough to minimize over bonds because every cut contains a bond and all
weights are nonnegative. Therefore:

```text
tau_G*
  = max_(w >= 0, sum_e w_e = 1)
      min_(cyclic-core cuts C) w(C).
```

Original bridges appear in no constraint and receive zero weight at every
optimum with positive value.

This is a specialization of the classical budgeted/design version of minimum
cut. It is not a new max-min cut optimization problem.

## Corollary 4: fractional bond packing dual

Let `B_G` be the bond family of all cyclic-core components. Define:

```text
nu_b*(G)
  = max sum_(B in B_G) x_B

subject to

  sum_(B containing e) x_B <= 1  for every edge e,
  x_B >= 0.
```

Then finite LP duality and rescaling give:

```text
tau_G* = 1 / nu_b*(G).
```

Indeed, a distribution `mu` on bonds with maximum edge load `q` rescales to a
fractional bond packing of total mass `1/q`; conversely a packing of total
mass `nu` normalizes to a bond distribution with maximum load at most
`1/nu`.

In matroid language, bonds are the circuits of the cographic matroid. The LP
is a standard fractional packing/covering pair; only its appearance as the
ASMP-9 conditional-access exponent is specific to this program.

## Theorem 5: closed form for cactus graphs

Suppose the nonbridge edges of `G` form a cactus: every nonbridge edge belongs
to exactly one simple cycle. Let `M` be the total number of nonbridge edges.
Then:

```text
tau_G* = 2/M.
```

The unique optimal allocation on the nonbridge edges is uniform:

```text
w_e = 1/M  for nonbridges,
w_e = 0    for bridges.
```

### Proof

The bonds of a cactus core are exactly the two-edge subsets lying in one
cycle. If cycle `j` has length `k_j` and receives total mass `s_j`, the
minimum pair weight within that cycle is at most its pair average:

```text
2 s_j / k_j.
```

Therefore any common lower bound `tau` requires
`s_j >= tau k_j/2`. Summing over cycles gives:

```text
1 >= sum_j s_j >= tau (sum_j k_j)/2 = tau M/2,
```

so `tau <= 2/M`. Uniform mass `1/M` on every nonbridge edge makes every
two-edge bond weigh exactly `2/M`, attaining the bound. Equality in every
pair-average bound forces uniformity within each cycle, and equality in the
sum forces the same per-edge weight across cycles. Bridges cannot receive
positive mass at an optimum. QED.

## Algorithmic consequence

The v0.17 procedure enumerated all `3^|E|` ternary status patterns before
minimizing their bad supports. Theorem 2 permits:

1. delete original bridges;
2. use a minimum-cut oracle as a separation oracle for the allocation LP; and
3. solve the classical design problem without enumerating the ternary status
space or all bonds explicitly.

This is a polynomial-time consequence of classical min-cut optimization and
LP separation/optimization equivalence. It is not claimed as a new algorithm.

## Claim boundary

If registered and independently verified, v0.18 would establish an exact
structural reduction for the independent-binomial conditional-access model
of v0.17 and a cactus closed form. It would not establish:

- a new theorem about max-min cut design;
- a finite-budget optimal integer allocation on arbitrary graphs;
- adaptive allocation;
- dependent responses or unknown response links;
- behavioral reward identification;
- downstream test power; or
- resolution of ASMP-9.
