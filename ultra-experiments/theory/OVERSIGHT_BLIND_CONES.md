# Oversight Blind Cones — Theorem Draft v0.1

## Purpose

This object asks a control question that subspace identity does not answer:
which permitted edit directions can create large registered behavior change
while producing little registered monitor signal?

It is a local theorem plus an empirical prediction. The theorem supplies a
sharp quadratic bound under frozen derivatives and metrics. Whether the
extremal subspace predicts real intervention outcomes is a separate,
cross-fitted experiment.

## Frozen objects

Let `E` be a finite-dimensional edit space with a registered positive-definite
metric `R`. At baseline weights `W`, define

```text
c(u) = C(W+u) - C(W)       behavior/capability outputs
m(u) = M(W+u) - M(W)       monitor outputs
J_C = D c(0)
J_M = D m(0)
```

Freeze positive-semidefinite output metrics `W_C` and `W_M`, including their
units and scale, before outcomes. Set

```text
A = J_C^T W_C J_C
B_0 = J_M^T W_M J_M
B_lambda = B_0 + lambda R
q_lambda(u) = (u^T A u) / (u^T B_lambda u).
```

For `lambda>0`, `B_lambda` is positive definite. The largest generalized
eigenvalue is

```text
mu_lambda = max_(u != 0) q_lambda(u).
```

The blind cone at practical ratio `gamma` is the homogeneous, generally
nonconvex set `{u != 0 : q_lambda(u)>gamma}`. Its blind index is the number of
generalized eigenvalues above `gamma`. When the top eigenvalue is repeated, the
scientific object is its eigenspace/projector, not an arbitrarily chosen vector.

## Sharp linear bound

For every edit direction,

```text
||J_C u||_(W_C)
  <= sqrt(mu_lambda)
     sqrt(||J_M u||_(W_M)^2 + lambda ||u||_R^2).
```

The constant is sharp because

```text
mu_lambda = lambda_max(B_lambda^(-1/2) A B_lambda^(-1/2))
           = inf {mu : A <= mu B_lambda}.
```

Thus the regularized theorem certifies a combined monitor-and-edit-norm gate.
It does **not** establish that the monitor alone covers the edit family.

At `lambda=0`, a finite pure-monitor constant exists exactly when

```text
ker(B_0) subset ker(A).
```

If the inclusion fails, a monitor-null, behavior-live direction exists and the
pure-monitor ratio is infinite. If it holds, the finite quotient is evaluated
on the `B_0`-supported subspace (equivalently the quotient by its kernel).

## Coordinate invariance

For an invertible edit-coordinate change `u=S z`, transform every form by
congruence:

```text
A' = S^T A S
B_0' = S^T B_0 S
R' = S^T R S
B_lambda' = S^T B_lambda S.
```

Then `q'_lambda(z)=q_lambda(Sz)`, the complete generalized eigenvalue multiset
is unchanged, and the blind cone maps as `K'_gamma=S^(-1)K_gamma`.

This fails if a fresh `lambda I` is inserted after a non-orthogonal coordinate
change. The edit metric `R` is part of the estimand and must transform with it.
Output reparameterizations likewise require contragredient transformation of
their output metrics.

## Finite nonlinear-radius gate

Assume that, for every `||u||_R<=r`, registered uniform remainder bounds hold:

```text
||c(u)-J_Cu||_(W_C) <= (L_C/2) ||u||_R^2
||m(u)-J_Mu||_(W_M) <= (L_M/2) ||u||_R^2.
```

Writing `s=||u||_R`, the triangle inequality and the sharp linear bound give

```text
||c(u)||_(W_C)
 <= sqrt(mu_lambda)
    sqrt((||m(u)||_(W_M) + (L_M/2)s^2)^2 + lambda s^2)
    + (L_C/2)s^2.
```

An edit is locally authorized only when an upper bound on the right-hand side
strictly clears a frozen behavior tolerance and `s<=r`. Equality is
inconclusive. Analytic Hessian bounds can make this uniform. A finite sampled
dose sweep cannot: it yields a certificate only for an enumerated edit set or a
distributional held-out guarantee under a frozen generator.

## Liveness fixtures

1. **Covered:** `R=I`, `J_C=alpha J_M` with full rank. Every generalized
   eigenvalue is `alpha^2` and the bound attains equality.
2. **Exact blind:** `J_M=[1,0]`, `J_C=[0,1]`. The unregularized ratio is
   infinite; `mu_lambda=1/lambda` with top direction `e_2`.
3. **Relative alignment:** with `J_M=diag(1,epsilon)`, compare
   `J_C=diag(1,epsilon)` and `J_C=diag(epsilon,1)`. Both capability maps have
   the same singular spectrum, but the top ratio changes from `1` to
   `1/epsilon^2` in the pure-monitor case.
4. **Coordinate trap:** `S=diag(100,0.01)` must leave the result unchanged only
   when `R` is transformed covariantly. Reinserting `I` must change the result
   and be rejected.
5. **Multiplicity:** a repeated top generalized eigenvalue must return an
   eigenspace, never a unique risk vector.

These cases make the instrument capable of passing, failing, detecting an exact
blind direction, and rejecting a false invariance implementation.

## Empirical falsification protocol

Construction prompts estimate metrics, Jacobians, regularization windows, and
candidate subspaces. Validation prompts and intervention outcomes remain
sealed. A `risk_vector_established` result requires all of:

- construction-to-validation replication of the generalized eigenspace;
- a nonzero registered linearization-validity radius;
- stability over a `lambda` window tied to measurement noise;
- separation from a relative-Haar null that preserves the marginal spectra of
  `A` and `B_0` in `R`-whitened coordinates;
- held-out prediction of the event
  `behavior shift > b_C AND monitor signal <= b_M` beyond edit norm, rank,
  attribution, `||J_Cu||`, and `||J_Mu||`; and
- grouped prompt/site/seed evaluation with no candidate-level
  pseudoreplication.

Hard kills include a failed coordinate trap, ridge domination, a non-replicated
eigenspace, no certified radius, Taylor residual above its bound, no advantage
over the relative-orientation null, or no incremental held-out prediction.

## Claim boundary

Permitted theorem statement:

> For a frozen edit family, frozen behavior/monitor metrics, and a certified
> local radius, the largest generalized eigenvalue is the sharp,
> coordinate-invariant constant relating linearized behavior energy to combined
> monitor-and-edit energy. With uniform Taylor bounds it yields the displayed
> finite-radius upper gate.

Prohibited: a large plug-in eigenvalue is not by itself a risk vector; a small
regularized eigenvalue is not monitor coverage; and no part of this draft is
evidence for recursive self-improvement.
