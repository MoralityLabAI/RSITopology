# ASMP-9 v0.30 draft: conservative calibrated consequences

Status: development-only and unregistered.

## 1. Mechanical conservativity

Fix a finite-horizon feature MDP:

```text
M = (S, A, P, d0, H, phi).
```

A consequence level `c` is applied exogenously: it is selected by the query
designer, not by the evaluated policy. Let `M_c` denote the mechanics exposed
at that level.

The registered identity-level certificate calls the extension mechanically
conservative exactly when every `M_c` has the same:

- state and action sets;
- initial distribution;
- transition kernel;
- horizon; and
- target feature map.

Under these equalities, every base policy remains feasible and has the same
base trajectory law and feature occupancy at every consequence level. This is
an induction on the finite horizon.

These exact equalities are sufficient for preservation and necessary for this
registered identity-level certificate. If a field changes, the intervention
can change the occupancy row and this certificate abstains. A changed MDP may
still be equivalent under a separately declared homomorphism or occupancy
quotient; v0.30 does not characterize those coarser equivalences.

## 2. Semantic calibration on a finite rectangle

Let `i in {1,...,m}` index base trajectories, policies, or lotteries, and let
`c_j`, `j in {0,...,n-1}`, be declared consequence values. Suppose the scalar
comparison argument is `V_ij`.

Relative to a reference level `j0`, the consequence is calibrated and
additive exactly when:

```text
V_ij - V_i,j0 = c_j - c_j0
```

for every `i,j`.

Equivalently:

```text
V_ij = u_i + c_j + K
```

for row effects `u_i` and a common constant `K`. The test contains
`m(n-1)` independent affine constraints. Every one is necessary: if any
non-reference cell is unmeasured, changing only that cell produces an
interaction witness that satisfies all remaining checks.

If the increments are row-independent but equal `kappa(c_j-c_j0)` for an
unknown `kappa`, the consequence is separable but not cardinally calibrated.
If the increments depend on `i`, the consequence interacts with the base
object and is not an additive numeraire.

## 3. Composition with v0.28

Mechanical conservativity preserves the occupancy difference `x`. Semantic
calibration gives the comparison argument:

```text
x^T r + (c_plus-c_minus).
```

Consequently, the v0.28 midpoint localization theorem applies without changing
the base row: if the allowed consequence differences cover `-x^T r`, the
unique midpoint localizes that occupancy functional in the declared units.

Both certificates are required. Passing mechanics alone does not establish
the consequence's utility, and passing a value-table test while changing the
MDP does not preserve the original occupancy query.

## 4. Mechanics-only semantic no-go

No procedure whose input is limited to `(S,A,P,d0,H,phi)` and consequence
labels can certify the semantic coefficient.

The same mechanically conservative extension is compatible with:

```text
V_ij = u_i + c_j,
V'_ij = u_i + kappa c_j,
```

for arbitrary `kappa`, and with context-interacting value tables. These models
have identical non-reward mechanics.

Even a complete population-response grid does not identify absolute scale
when the response-link class is closed under positive rescaling and `kappa`
is unknown:

```text
(u, kappa, F)
and
(alpha u, alpha kappa, F_alpha),

F_alpha(t) = F(t/alpha),
```

induce identical laws. The semantic unit must therefore come from an external
calibration assumption or from a stronger behavioral measurement structure;
it is not created by the product-MDP construction.

## 5. Approximate calibration

Define anchored residuals:

```text
e_ij =
  V_ij - V_i,j0 - (c_j-c_j0).
```

If `|e_ij| <= epsilon` for every cell, then the error in any two-sided
consequence difference is at most `2 epsilon`:

```text
|(e_i,a-e_k,b)| <= 2 epsilon.
```

The factor two is sharp. Thus an approximate semantic certificate can be
propagated into the v0.28 localization error rather than silently treated as
exact.

## 6. Claim boundary

Exogenous MDP decomposition, additive conjoint measurement, reward
invariances, environment design, and rectangular separability are established
mathematics. Novelty is not claimed.

This theorem does not establish that money, tokens, approval, or any other
real consequence has a known stable utility coefficient. It does not infer a
scalar value table from ordinal responses, validate the demonstrator model,
or resolve ASMP-9.
