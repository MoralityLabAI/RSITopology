# ASMP-9 v0.21 theory draft: the count-floor boundary is a Tutte point

Status: development-only; not registered and not claim-eligible.

## Frozen-model boundary

Inherit the independent-binomial conditional-access object from ASMP-9
v0.17-v0.20.  Restrict attention to one finite, simple, biconnected
comparison block `G = (V,E)`, and set

```text
epsilon = 1/2
total budget N = |E|
positive integer edge counts n_e >= 1.
```

The budget constraint forces the unique allocation `n_e = 1` on every edge.
At `epsilon = 1/2`, either endpoint label gives the same Bernoulli law.  With
one trial, each residual edge is `ZERO` or `FULL` with probability `1/2`;
`INTERIOR` has probability zero.  Thus the residual digraph is a uniformly
random total orientation of `G`.

Because a biconnected graph is bridgeless, the v0.17 quotient-liveness event
requires every oriented edge to lie on a directed cycle.  This is precisely a
totally cyclic orientation.  Therefore

```text
F_G(count floor, epsilon=1/2)
    = number of totally cyclic orientations of G / 2^|E|
    = T_G(0,2) / 2^|E|.
```

For a connected graph this is equivalently the number of strong orientations
divided by `2^|E|`.

## Complexity classification

Las Vergnas's orientation interpretation identifies the numerator with
`T_G(0,2)`.  Jaeger, Vertigan, and Welsh's Tutte-plane dichotomy makes
evaluation at `(0,2)` #P-hard for graphic matroids: the point is neither on
the easy hyperbola `(x-1)(y-1)=1` nor one of their exceptional points.
Counting totally cyclic orientations is in #P because an orientation is a
polynomial-size witness and total cyclicity is polynomial-time checkable.

Consequently:

1. computing the count-floor availability numerator is #P-complete under the
   polynomial-time Turing reductions used by Jaeger, Vertigan, and Welsh;
2. computing the exact rational count-floor availability is #P-hard, because
   multiplying by `2^|E|` recovers the numerator; and
3. computing the exact maximin value at `N=|E|` is #P-hard, because the
   positive allocation is unique and endpoint labels are immaterial.

This is a value-computation result.  Optimizer search at the count floor is
trivial and is not claimed hard.

## Localization to one biconnected block

The surrounding counting problem remains #P-hard when accessed through an
oracle restricted to biconnected blocks, under polynomial-time Turing
reductions:

1. if an input graph has a bridge, `T_G(0,2)=0`;
2. otherwise decompose it into nontrivial vertex-biconnected edge blocks;
3. totally cyclic orientation counts multiply over those edge-disjoint
   blocks; and
4. query the hypothetical biconnected-block oracle once per block and
   multiply its answers.

Hence a polynomial algorithm for every biconnected block would give a
polynomial algorithm for the general `T_G(0,2)` evaluation.

## Bridge warning

The literal identity with `T_G(0,2)` must not be stated for the ASMP quotient
event on an arbitrary graph with original bridges.  A totally cyclic
orientation cannot contain a bridge, so its count is zero.  The registered
ASMP quotient deliberately removes original bridges and leaves their
orientations unconstrained.  On a triangle with one leaf edge, for example,
`T_G(0,2)=0` while the ASMP count-floor availability is `1/4`.

The complexity theorem targets exactly the unresolved object from v0.20: one
biconnected overlapping-cycle block, where the distinction disappears.

## What finite verification can establish

A prospective run can independently verify, on fresh graph cells, that:

- deletion-contraction at `(0,2)`;
- explicit enumeration of total orientations; and
- the ASMP residual-liveness implementation

return the same integer.  It can also verify exact normalization, label
invariance, unique allocation, the bridge warning, and the block product.

Those checks challenge the translation and code.  They do not prove the
classical complexity theorem.

## Claim boundary

The candidate result classifies exact value computation at a deliberately
frozen boundary of the v0.20 local problem and localizes the hardness to
biconnected blocks under Turing reductions.  It does not classify optimizer
search above the count floor, arbitrary-`epsilon` weighted partial
orientations, fixed-parameter tractability of the full ASMP objective,
approximation, adaptive allocation, dependent responses, response-link
misspecification, behavioral reward identification, general inverse
reinforcement learning, or ASMP-9.

