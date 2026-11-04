# Robust contextual scalar-gluing theorem — development draft

## Status

Unregistered development theorem. No claim-eligible run exists.

## Setup

Let `Y = R^m` be the space of context-labelled edge-difference observations.
Let:

```text
G = im(D_shared)
L = im(D_local),
```

where `D_shared` uses one utility vector across all contexts and `D_local` is
block diagonal with one utility vector per context. Then `G` is a subspace of
`L`.

Use the registered Euclidean observation norm. Let `P_G` and `P_L` be the
orthogonal projectors and define:

```text
g(y) = P_G y
q(y) = (P_L - P_G)y
r(y) = (I - P_L)y.
```

The corresponding radii are:

```text
rho_glue(y) = ||q(y)||_2
rho_local(y) = ||r(y)||_2
rho_total(y) = ||y-P_G y||_2.
```

## Theorem A: unique inconsistency decomposition

For every observation `y`,

```text
y = g(y) + q(y) + r(y)
```

is an orthogonal decomposition with:

- `g(y)` shared-scalar;
- `q(y)` context-locally scalar but orthogonal to every shared-scalar flow;
  and
- `r(y)` orthogonal to every context-local scalar flow.

Consequently:

```text
rho_total(y)^2
  = rho_glue(y)^2 + rho_local(y)^2.
```

Moreover:

```text
rho_total(y) = min_{z in G} ||y-z||_2,
rho_local(y) = min_{z in L} ||y-z||_2,
rho_glue(y) = min_{z in G} ||P_L y-z||_2.
```

The cross-context obstruction space is:

```text
Q = L intersect G^perp
```

and:

```text
dim(Q)
  = rank(D_local)-rank(D_shared)
  = q_v0.11.
```

## Corollary A1: exact bounded-error feasibility

For a declared edge-observation error radius `epsilon`, there exists a shared
scalar flow `z` satisfying:

```text
||y-z||_2 <= epsilon
```

if and only if:

```text
rho_total(y) <= epsilon.
```

Thus `rho_total` is not a heuristic inconsistency score. It is the exact
minimum repair budget in the declared norm. The pair
`(rho_local,rho_glue)` identifies whether that budget is spent inside
contexts or between contexts.

## Theorem B: robust linear mixed-cycle access

Let `d = dim(Q)`. Suppose a query design consists of `k` linear functionals on
`Q`, represented by a matrix:

```text
A : Q -> R^k.
```

The gluing component is identifiable exactly when `rank(A)=d`; hence `k >= d`
is necessary.

Under additive query-output error `e` with `||e||_2 <= eta`, every left-inverse
reconstruction has worst-case amplification at least:

```text
1/sigma_min(A).
```

The Moore-Penrose inverse attains that bound.

For the square case `k=d`, constrain every query row to Euclidean norm at most
one. Then:

```text
sigma_min(A) <= 1.
```

Equality holds exactly when the rows are an orthonormal basis of `Q`.
Therefore orthonormal mixed-cycle coordinates are minimax optimal among
arbitrary normalized linear queries, and the optimal worst-case amplification
is one.

Proof: the squared singular values sum to `||A||_F^2 <= d`, so the smallest
squared singular value is at most their mean, one. Equality requires every
singular value to equal one.

## Simple-cycle access

The arbitrary linear optimum need not be an admissible single-loop query.
For a registered context-labelled multigraph, let every candidate query be a
normalized signed simple-cycle circulation. The robust design problem is:

```text
maximize sigma_min(A_B)
over d-element simple-cycle families B spanning Q.
```

A minimum-length cycle basis instead minimizes total support. These are
different objectives. The development census must determine whether they
coincide on the frozen graph class; either a proof of coincidence or a
smallest counterexample is acceptable.

## Required controls before registration

1. The two-item/two-context v0.11 witness has:
   `rho_local=0`, `rho_glue=rho_total=1/sqrt(2)`.
2. A within-context inconsistent triangle has positive `rho_local`.
3. Shared scalar flows have all three radii zero.
4. The decomposition is invariant under invertible changes of utility
   coordinates.
5. An orthonormal query basis attains amplification one.
6. Every design with fewer than `d` queries has a nonzero kernel witness.
7. The simple-cycle census reports all ties; no arbitrary cycle-basis
   tie-break may be promoted to a theorem.

## Claim boundary

The theorem is finite Euclidean nested-subspace geometry. It does not prove
that a human or model has scalar preferences, estimate a latent context,
provide a finite-sample stochastic guarantee, choose the norm
application-independently, or resolve ASMP-9.
