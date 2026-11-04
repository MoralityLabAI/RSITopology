# Prior-art audit: ASMP-10 finite-prefix obstruction v0.1

## Disposition

**Classical consolidation; no theorem novelty claimed.**

The exact rank threshold, uniqueness below degree `n(k+1)`, nonuniqueness at
and above that degree, and the product-form kernel witness are the standard
univariate Hermite-interpolation theorem expressed through a confluent
Vandermonde matrix. The ASMP-10 artifact contributes an obstruction framing
against a declared observation filtration, an exact-rational executable
census, a normalized future-divergence witness with scores `-1` and `+1`, and
an explicit claim boundary. It does not contribute a new interpolation
theorem.

This audit is an additive correction beside the sealed protocol and result. It
does not change their gates, artifacts, or outcome.

## Classical source map

Hermite's original interpolation paper is:

- C. Hermite, [“Sur la formule d'interpolation de
  Lagrange”](https://doi.org/10.1515/crelle-1878-18788405), *Journal für die
  reine und angewandte Mathematik*, volume 84 (1878), pages 70–79.

Standard later treatments include:

- Philip J. Davis, *Interpolation and Approximation*, Blaisdell, 1963; and
- Josef Stoer and Roland Bulirsch, *Introduction to Numerical Analysis*, in
  its polynomial-interpolation treatment.

The registered matrix is precisely a confluent Vandermonde evaluation map:
its rows evaluate derivatives of monomials at repeated nodes. For `n` distinct
nodes with multiplicity `k+1`, Hermite interpolation supplies a unique
polynomial of degree less than `J=n(k+1)` matching arbitrary jet data. This is
equivalent to the rank formula used in v0.1.

## Claim-by-claim classification

### Exact rank and identification threshold

`rank H(n,k,D)=min(D+1,n(k+1))` is classical for distinct nodes. The v0.1
census validates the implementation; it does not establish a new rank theorem.

### Sharp kernel witness

The polynomial

`q(x)=product_i (x-x_i)^(k+1)`

is the standard minimal-degree polynomial vanishing to the registered
multiplicity at every node. The statement that every invisible difference is
divisible by `q` is the corresponding factor theorem. Again, this is
classical.

### Mirage-pair normalization

Choosing `epsilon=1/q'(n)` so that the two gradient-descent continuations have
future scores exactly `-1` and `+1` is application-specific packaging. It
makes the obstruction auditable and gives it a metric-robust unit margin, but
it is an elementary normalization of the classical kernel witness.

## What the result reaches

The obstruction applies to the frozen filtration consisting of a finite loss
prefix and finitely many local derivatives, inside a degree-bounded polynomial
loss class. It does not cover richer observations that expose the objective,
dataset, optimizer state, representations, or global analytic constraints. It
also does not establish an obstruction inside a realistic grokking model.

The strongest defensible external description is:

> v0.1 consolidates classical Hermite interpolation into a preregistered
> ASMP-10 instrument showing exactly when a finite local-jet filtration admits
> prefix-indistinguishable polynomial continuations with opposite future
> outcomes.

## Search limitation

This is a targeted classification audit, not an exhaustive novelty search. No
novelty claim survives or depends on it; an additional source can improve the
bibliography without changing the result's position.

