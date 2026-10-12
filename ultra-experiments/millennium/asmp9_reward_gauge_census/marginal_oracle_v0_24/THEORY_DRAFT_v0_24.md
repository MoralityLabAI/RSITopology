# ASMP-9 v0.24 theory draft: exact marginal access is value-complete

Status: development-only; not registered and not claim-eligible.

## Frozen setting

Let `G=(V,E)` be a finite simple biconnected comparison block with
`m=|E|`.  Work at `epsilon=1/2` in the independent fair-microtrial model of
v0.23.  Write

```text
F_G(n_1,...,n_m)
```

for exact quotient-liveness availability under positive integer edge counts.
For uniform count `r`, write

```text
P_G(2^-r) = F_G(r,...,r).
```

Direct ternary-state expansion shows that `P_G(z)` is a polynomial in `z` of
degree at most `m`.  Since `z=0` makes every edge bidirected and `G` is
connected,

```text
P_G(0)=1.
```

## Ratio reconstruction theorem

Suppose an oracle returns the exact consecutive uniform ratios

```text
R_r = P_G(2^(-(r+1))) / P_G(2^-r),
r=1,...,m.
```

Define

```text
q_1 = 1,
q_(r+1) = product_(j=1)^r R_j.
```

Then

```text
q_r = P_G(2^-r) / P_G(1/2).
```

There is a unique degree-at-most-`m` polynomial `Q` through the `m+1` pairs

```text
(2^-r,q_r), r=1,...,m+1.
```

It is exactly `Q=P_G/P_G(1/2)`.  Evaluating the interpolant at zero and using
`P_G(0)=1` gives

```text
P_G(1/2) = 1 / Q(0).
```

Scaling all coefficients of `Q` by that value recovers the complete
polynomial `P_G`, not merely the floor value.

## Per-edge marginal reduction

For an arbitrary positive count vector `n` and edge `e_i`, define the exact
one-edge marginal ratio

```text
M_G(n,i) = F_G(n+e_i) / F_G(n).
```

Fix any edge ordering.  Starting at the uniform vector `(r,...,r)`, increment
each edge once.  The `m` local ratios telescope:

```text
product_(i=1)^m M_G(n^(i-1),i)
  = F_G(r+1,...,r+1) / F_G(r,...,r)
  = R_r.
```

Doing this for `r=1,...,m` uses exactly `m^2` marginal-oracle calls and
recovers `P_G`.

## Complexity consequence

At the floor,

```text
P_G(1/2) = T_G(0,2) / 2^m.
```

Versions v0.21 and v0.22.1 already localize exact evaluation of this quantity
to a #P-hard problem on finite simple biconnected blocks under polynomial-time
Turing reductions.  The interpolation nodes, coefficients, ratios, and
availability numerators in the reduction have polynomial bit length: queried
counts are at most `m+1`, and the total number of microtrials is `O(m^2)`.

Therefore:

> Exact computation of `M_G(n,i)` on positive count vectors is #P-hard under
> polynomial-time Turing reductions, even when `G` is restricted to a finite
> simple biconnected block and all queried counts are at most `m+1`.

The same conclusion holds for an oracle returning the exact uniform-round
ratios `R_r`.

This is an exact-value access result.  It is not a proof that returning a
globally optimal allocation is NP-hard or #P-hard.  An optimizer may use
ordinal information without exposing exact ratios.

## Development refutation of global balance

Exploration also refuted a tempting endpoint conjecture.  On the biconnected
six-vertex graph with edge order

```text
(01,02,12,34,35,45,03,14),
```

at total budget `N=16`, exhaustive exact development enumeration found eight
global optimizers, including

```text
(1,2,2,1,2,3,2,3).
```

Its common-denominator numerator is `40194`, versus `38354` for the balanced
allocation `(2,2,2,2,2,2,2,2)`, both over denominator `2^16`.

This cell was inspected before any prospective registration and is therefore
burned.  It is design evidence, not a claim-eligible experiment.  It shows
that v0.24 should not attempt a universal balanced-optimizer theorem at
`epsilon=1/2`.

## Remaining load-bearing gap

The global optimizer-output problem remains open.  A successor needs one of:

1. an exact calibration gadget that converts optimizer choices into enough
   marginal comparisons to recover `P_G`;
2. a reduction directly to optimizer output without exact-value leakage; or
3. a nontrivial graph class with a proved global allocation algorithm.

Value hardness, marginal hardness, a burned nonbalance witness, and the v0.23
exchange trap do not substitute for that missing classification.

