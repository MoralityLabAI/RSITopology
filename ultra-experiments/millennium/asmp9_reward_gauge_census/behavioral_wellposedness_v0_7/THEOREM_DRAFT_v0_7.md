# Behavioral access separates reconstruction from model checking

## Status

Development theorem draft. The graph-Hodge and comparison-search ingredients
are classical. This document specializes them to the remaining ASMP-9
behavioral-access and inconsistent-demonstrator obligations.

## 1. Exact pairwise response laws

Let `G=(V,E)` be a finite directed comparison graph. For every registered edge
`e=(i,j)`, let:

```text
l_e = log(P(j preferred to i) / P(i preferred to j)).
```

The log-odds are assumed finite and reciprocal, so reversing an edge negates
`l_e`. A coherent Bradley-Terry response law has:

```text
l_(i,j) = theta_j - theta_i.
```

If inverse temperature is known, `theta` is identified up to one additive
constant per connected component. If inverse temperature is unknown, only the
positive ray of `theta` differences is identified.

### Theorem 1: reconstruction/model-checking split

Let `c(G)` be the number of weak components and `m=|E|`.

1. Under the promise that the response law is coherent, `|V|-c(G)` exact
   log-odds queries on a spanning forest are necessary and sufficient to
   reconstruct `theta` modulo component constants.
2. Without that promise, an edge field is coherent if and only if every cycle
   sum vanishes.
3. Certifying only the *existence* of a scalar representation requires exactly
   the non-bridge edge values in the worst case. Bridge scores impose no cycle
   constraint and any assignment to them extends a coherent scalar by changing
   component offsets across the bridge.
4. If the goal is both to reconstruct the scalar on the full graph and to
   certify the coherence promise, all `m` edge values are necessary and
   sufficient. After a spanning forest has supplied the reconstruction, the
   additional model-checking burden is:

```text
m-(|V|-c(G)) = beta_1(G).
```

Thus a spanning tree can recover a scalar *if one is assumed to exist*, but
each chord supplies an independent fundamental-cycle check that the
demonstrator can fail.

### Proof

The comparison field is the incidence image `B theta`. The incidence matrix
has rank `|V|-c(G)`, proving the reconstruction count. An edge field is in
`im B` exactly when it is orthogonal to the cycle space, equivalently when
every cycle sum is zero. Every non-bridge edge lies on a cycle; if it is
unqueried, take a coherent field and add a nonzero value supported only on that
edge. The two worlds agree on every query, but the modified world is
incoherent. Conversely, bridge values never enter a cycle condition, so all
non-bridge values suffice for coherence-only certification. For the combined
objective, an unqueried bridge leaves the scalar offset across that bridge
unknown, while an unqueried non-bridge can hide incoherence. Hence every edge
must be queried.

## 2. Quantifying incoherence

For rational edge scores, define the closest coherent scalar model in weighted
least squares:

```text
theta_hat = argmin_theta ||l-B theta||_W^2.
```

After fixing one root per connected component, the minimizer is unique. The
residual:

```text
r = l-B theta_hat
```

is orthogonal to every gradient field. Its squared norm is zero if and only if
the demonstrator is exactly coherent. On a directed cycle `C` of length `k`,
any coherent approximation obeys:

```text
||r_C||_2^2 >= (sum_(e in C) l_e)^2 / k,

||r_C||_infinity >= |sum_(e in C) l_e| / k.
```

A nonzero cycle circulation is therefore not a different reward gauge. It is
a certificate that no scalar Bradley-Terry value object generates the
declared response law.

## 3. Deterministic policy observations

Consider the one-state two-action family with quotient reward coordinate
`theta in [0,1]`. An environment intervention chooses a rational threshold
`t`, and the demonstrator's deterministic optimal action returns:

```text
Y_t(theta) = 1{theta > t},
```

with equality reported separately if it occurs.

This is a minimal policy-observation model: the intervention changes the
relative action bonus, while the observation reveals only the chosen action,
not a return difference.

### Theorem 2: finite policy access cannot exactly identify a continuum

After `k` adaptive threshold interventions, the minimax worst-case ambiguity
interval has width:

```text
2^-k.
```

Binary search attains the bound; a binary decision tree with `2^k` leaves
cannot partition `[0,1]` into intervals all shorter than `2^-k`.

For `k` nonadaptive thresholds, the minimax worst-case ambiguity interval has
width:

```text
1/(k+1).
```

Equally spaced thresholds attain the bound; `k` points create only `k+1`
intervals, one of which has width at least `1/(k+1)`.

Consequently:

- no finite deterministic-policy experiment exactly identifies an arbitrary
  real reward quotient;
- adaptive interventions achieve `epsilon`-identification with
  `ceil(log2(1/epsilon))` policy observations; and
- nonadaptive interventions require at least `ceil(1/epsilon)-1`.

This does not contradict exact reward recovery from richer stochastic policies
or multiple transition laws. It isolates what deterministic policy outputs
alone can reveal in one declared access grammar.

## ASMP-9 consequence

The positive scalar-recovery theorem is conditional on a coherent response
model. The cycle tests are not optional diagnostics: they are the exact
additional access needed to establish that the inferred scalar exists on the
registered comparison graph. Deterministic policy demonstrations provide a
strictly weaker, inequality-valued channel whose exact-identification target
must be replaced by an approximation radius or a discrete reward class.

## Claim boundary

This is a finite graph and threshold-query consolidation. It does not
characterize general MDP reward invariances, dependent human responses,
contextual preference reversals, or all non-expected-utility choice. The
Hodge decomposition and binary-search bounds are classical; novelty is not
claimed.
