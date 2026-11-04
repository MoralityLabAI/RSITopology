# ASMP-9 v0.22 theory draft: uniform above-floor availability

Status: development-only; not registered and not claim-eligible.

## Setup

Inherit the v0.17-v0.21 independent-binomial conditional-access model.
Restrict to one finite simple biconnected comparison block `G=(V,E)`, set
`epsilon=1/2`, and assign the same fixed integer number `r>=1` of trials to
every edge.

Define

```text
z = 2^(-r).
```

For every edge:

```text
P(ZERO)     = z
P(FULL)     = z
P(INTERIOR) = 1 - 2z.
```

An `INTERIOR` edge is bidirected in the ASMP residual graph.  For purposes of
directed-cut liveness it plays exactly the role of an unoriented edge in
Backman's strongly connected partial orientations: either state prevents the
cut from being consistently one-way.

## Classical weighted Tutte identity

Backman's `(k,l)`-chromatic formula for strongly connected partial
orientations is

```text
(k+l)^(|V|-1) k^g
T_G(l/(k+l), (2k+l)/k),
```

where `g=|E|-|V|+1`.  The formula is polynomial in the state weights and
therefore extends from positive integer colors to rational weights.  Set

```text
k = z
l = 1 - 2z.
```

Because `2k+l=1`, the weighted count is already a probability:

```text
F_G(r)
  = (1-z)^(|V|-1) z^g
    T_G((1-2z)/(1-z), 1/z).
```

At `r=1`, this reduces to the v0.21 boundary
`T_G(0,2)/2^|E|`.

## Fixed-count hardness

For any fixed integer `r>=1`, define

```text
x_r = (2^r - 2)/(2^r - 1)
y_r = 2^r.
```

Then

```text
(x_r - 1)(y_r - 1) = -1.
```

Every point lies on the Jaeger-Vertigan-Welsh special curve `H_-1`, and none
is one of their exceptional easy points.  Their theorem therefore makes
exact Tutte evaluation at `(x_r,y_r)` #P-hard for every fixed `r`.
The multiplicative prefactor in `F_G(r)` is nonzero and polynomial-time
computable, so exact ASMP availability evaluation is #P-hard as well.

This statement remains hard when the oracle domain is restricted to finite
simple biconnected blocks.  Tutte evaluation factors over connected
components and vertex-biconnected blocks, and a bridge contributes the
explicit factor `x_r`.  Decomposing an arbitrary simple input graph into its
blocks therefore gives a polynomial-time Turing reduction to
biconnected-block evaluation.  This is a localization of the classical
dichotomy, not a new complexity theorem.

For fixed `r`, the numerator under common denominator `2^(r|E|)` counts fair
binary trial matrices whose residual graph is live.  A trial matrix has
polynomial length and liveness is polynomial-time checkable.  Hence the
numerator is in #P and is #P-complete under the polynomial-time Turing
reductions used by the Tutte dichotomy.

In particular the minimal uniform above-floor design `r=2`, with total budget
`N=2|E|`, evaluates the hard point:

```text
(x_2,y_2) = (2/3,4).
```

No interpolation over several counts is required.

## Scope

This classifies exact evaluation of a declared uniform allocation, not
maximin optimization over all allocations with the same total budget.
It does not say uniform allocation is optimal on a general biconnected block.

It also does not classify arbitrary endpoint probabilities, nonuniform edge
counts, approximation, adaptive allocation, dependence, misspecification,
behavioral reward identification, general inverse reinforcement learning, or
ASMP-9.
