# Behavioral acquisition of an additive semantic rectangle

## Status

This document records the finite theorem exercised by
`ASMP-9-BEHAVIORAL-RECTANGLE-v0.32`.

The mixture-space representation, standard-gamble method, additive conjoint
representation, binary search, binomial tails, and support-function calculus
are classical. This is an ASMP-9 access ledger and executable composition,
not a novelty claim.

## Setting

Let `X=I x J` be a finite rectangle of base objects and consequence levels.
Preferences are defined on a mixture space containing:

- each deterministic cell `x in X`;
- one common worst anchor `x_minus`;
- one common best anchor `x_plus`; and
- registered objective lotteries
  `L(p)=p x_plus+(1-p)x_minus`.

Assume the Herstein-Milnor mixture-space conditions needed for an affine
utility representation and normalize:

```text
U(x_minus)=0,
U(x_plus)=1.
```

The population response model is:

```text
Pr[x preferred to L(p)] = F(U(x)-p),
```

where `F` is strictly increasing and has common midpoint `F(0)=1/2`. The
registered oracle returns the one-bit answer:

```text
Q(x,p)=1{Pr[x preferred to L(p)]>1/2},
```

assigning equality to zero.

## Theorem 1: binary population acquisition

Under the setting above:

```text
Q(x,p)=1{U(x)>p}.
```

Depth-`d` bisection therefore localizes every `U(x)` to an interval of width
at most `2^-d`.

If every cell belongs to the centered dyadic grid

```text
G_d={(2k+1)/2^(d+1): k=0,...,2^d-1},
```

then `d` registered binary queries per cell recover the complete table
exactly. For an unrestricted `N`-cell table on this grid, `Nd` queries are
also necessary: there are `2^(Nd)` possible tables and at most `2^q`
length-`q` binary transcripts.

### Proof

Mixture affinity gives `U(L(p))=p`. Strict monotonicity and the common
midpoint give the binary identity. Ordinary bisection gives the interval.
Centered grid points are the centers of depth-`d` leaves and never equal a
registered boundary query. The transcript-counting argument proves the
lower bound. QED.

## Theorem 2: rectangle additivity and exact uncertainty geometry

Let `D` be the anchored cross-difference operator:

```text
(DU)_ij=U_ij-U_i0-U_0j+U_00,  i>0,j>0.
```

Then:

```text
DU=0
```

if and only if there exist row effects `a_i`, consequence effects `c_j`, and
a constant `K` with:

```text
U_ij=a_i+c_j+K.
```

If behavioral acquisition returns the simultaneous cell enclosure

```text
U in U_hat + Box(eta),
```

then:

```text
DU in D U_hat + D Box(eta).
```

For every residual-space direction `q`, the exact support of this constructed
zonotope is:

```text
h(q)=sum_x eta_x |(D^Tq)_x|.
```

Consequently, for any declared interaction tolerance, each residual can be
classified conservatively as certified, rejected, or inconclusive while
retaining correlations caused by cell reuse.

### Proof

An additive table has zero cross-differences. Conversely, when all
cross-differences vanish, set:

```text
K=U_00,
a_i=U_i0-U_00,
c_j=U_0j-U_00.
```

The cross-difference equation gives the additive representation. Linear
propagation gives the residual zonotope, and the support formula is the
standard support of a linear image of a box. QED.

## Theorem 3: exact finite-sample majority certificate

Assume independent responses and a correct-sign probability of at least
`p_min>1/2` at every registered query. For an odd repeat count `r`, the
worst registered majority-vote error is:

```text
B(r,p_min)=
sum_{k=0}^{(r-1)/2}
  binom(r,k) p_min^k (1-p_min)^(r-k).
```

If `Q B(r,p_min)<=delta`, then with probability at least `1-delta`, all `Q`
bisection decisions are correct simultaneously. Every resulting cell
interval and residual zonotope then covers its target.

No finite uniform repeat certificate exists over a class permitting
`p_min=1/2`.

### Proof

The displayed sum is the exact lower tail for a majority of independent
Bernoulli responses at the worst admitted success probability. Monotonicity
in that probability and a union bound over `Q` queries give the result. At
one half, majority error does not converge to zero. QED.

## Proposition 4: finite mixture-affinity audit

For registered cells `x,y` and weight `w`, acquire the compound lottery
`z=w x+(1-w)y` with the same global ruler. Mixture affinity predicts:

```text
U(z)-wU(x)-(1-w)U(y)=0.
```

If the three cell estimates have radii `eta_z,eta_x,eta_y`, the exact support
of this residual is:

```text
eta_z+w eta_x+(1-w)eta_y.
```

This permits registered-cell certify/reject/inconclusive decisions. Passing
finitely many compound lotteries does not prove the mixture-space axioms
globally.

## Proposition 5: access no-go witnesses

### Deterministic ordinal comparisons

The normalized tables

```text
[[0,1/3],[2/3,1]]
[[0,1/9],[4/9,1]]
```

have the same complete deterministic order. The first is additive; the
second has cross-difference `4/9`. Ordinal rankings do not identify additive
cardinal structure.

### Row-local standard-gamble rulers

The tables

```text
[[0,1/4,1/2],[1/3,7/12,5/6]]
[[0,1/4,1/2],[1/2,2/3,5/6]]
```

both produce row-local coordinates `(0,1/2,1)` in each row. Only the first is
additive on one global scale. Row-local rulers do not glue cardinal units
across contexts.

### Incomplete cell coverage

If any rectangle cell is unmeasured, begin with the additive zero table and
perturb only that cell. Every observed cell remains unchanged and at least
one cross-difference becomes nonzero. Complete cell coverage is necessary
for a full-table certificate in this unrestricted class.

## Claim boundary

The theorem recovers the scalar object defined by its registered
mixture-affine response model. It does not validate expected utility for
humans or models, show that arbitrary outcomes can be mixed, establish
context-invariant anchors, cover dependent responses, prove minimax
finite-sample constants, identify value from ordinary deterministic
comparisons, or resolve ASMP-9.
