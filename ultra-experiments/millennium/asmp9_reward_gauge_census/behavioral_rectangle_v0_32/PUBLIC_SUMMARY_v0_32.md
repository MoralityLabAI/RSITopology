# ASMP-9 behavioral rectangle v0.32

## Result

Version v0.32 closes one behavioral-access gap under an explicit,
falsifiable expected-utility interface.

Given common global worst and best lottery anchors, mixture-affine
preferences, and a shared response midpoint, comparing a rectangle cell `x`
with the anchor lottery `L(p)` reveals one bit:

```text
1{Pr[x preferred to L(p)]>1/2}=1{U(x)>p}.
```

Binary bisection therefore acquires a normalized scalar value for every cell.
The rectangle cross-difference operator:

```text
(DU)_ij=U_ij-U_i0-U_0j+U_00
```

then tests whether one common additive consequence scale exists. Cellwise
uncertainty is retained as `D Box(eta)`, so the same estimated cell can cancel
across multiple residuals instead of being charged repeatedly as independent
error.

## Registered execution

The prospectively registered exact-rational run returned:

```text
scientific gates              12/12 pass
independent checks            20/20 pass
runtime                       0.0555525 seconds
peak resident memory          21,557,248 bytes
GPU                           none
```

On the 3x4 centered-dyadic fixture:

```text
cells                         12
bisection depth               4
population queries            48
binary transcript lower bound 48
cross-difference shape        6 x 12
cross-difference rank         6
```

All cells were recovered exactly. The additive fixture had six zero
cross-differences; a one-cell perturbation produced the registered `1/16`
interaction. Omitting any of the twelve cells admitted a nonadditive witness
agreeing on every observed cell.

At continuous depth three, the exact support in a registered residual
direction was `1/4`; treating the six residuals as independent gave `1/2`.
The shared-cell geometry therefore mattered operationally.

## Assumption-liveness controls

The expected-utility assumption was given a finite opportunity to fail:

```text
consistent compound lottery   residual 0       certified
distorted compound lottery    residual 1/16    rejected
width-straddling lottery      residual 1/12    inconclusive
```

Two access no-gos also passed:

- a strictly increasing transformation preserved every deterministic ranking
  while changing additivity by cross-difference `4/9`; and
- two tables had identical row-local standard-gamble coordinates but differed
  on global additivity.

Thus deterministic ordinal data and separately normalized context rulers are
not substitutes for one global behavioral scale.

## Finite-sample control

For 48 binary population queries, independent correct-sign probability at
least `3/4`, and family error `1/100`, exact binomial arithmetic found:

```text
minimum odd repeats per query  43
previous odd count             41, fails
chance-level response          unavailable
```

This is a registered sufficient majority-vote certificate, not a minimax
sampling theorem.

## What changed in the resolution audit

The v0.31 audit left behavioral acquisition of the semantic rectangle as the
first missing item. Version v0.32 closes it for a finite mixture-affine access
grammar with common global anchors and a declared response margin.

It does not close:

- whether humans or models satisfy that grammar;
- broader non-expected-utility or strategic demonstrator classes;
- dependent-response and joint occupancy-estimation complexity;
- coarser MDP equivalences; or
- maximal reward invariance and general no-go classification.

ASMP-9 remains unresolved.
