# Conservative calibrated-consequence theorem

## Setting

Fix a finite-horizon feature MDP:

```text
M = (S, A, P, d0, H, phi).
```

A consequence level `c` is selected exogenously by the query designer, not by
the policy being evaluated. Let `M_c` denote the mechanics exposed at that
level.

## Theorem

### A. Exact mechanical certificate

The registered identity-level certificate is mechanically conservative when
every `M_c` has the same:

- state and action sets;
- initial distribution;
- transition kernel;
- horizon; and
- target feature map.

Under these equalities, every base policy remains feasible and has exactly the
same base trajectory law and target-feature occupancy at every consequence
level.

These equalities are sufficient for preservation and necessary for this
identity-level certificate. A changed MDP may still be equivalent under a
separately declared homomorphism or occupancy quotient; that coarser
classification is outside this theorem.

### B. Exact semantic certificate

Let `i in {1,...,m}` index base trajectories, policies, or lotteries. Let
`c_j`, `j in {0,...,n-1}`, be declared scalar consequence values, and suppose
the scalar comparison argument at the corresponding product cell is `V_ij`.

Relative to a reference consequence `j0`, the consequence is calibrated and
additive exactly when:

```text
V_ij - V_i,j0 = c_j - c_j0
```

for every `i,j`. Equivalently:

```text
V_ij = u_i + c_j + K
```

for row effects `u_i` and a common constant `K`.

The anchored test contains `m(n-1)` independent affine constraints. Every
constraint is necessary: omitting any one non-reference cell admits an exact
single-cell interaction witness satisfying all remaining constraints.

If the increments are row-independent but equal:

```text
kappa(c_j-c_j0)
```

for an unknown `kappa`, the consequence is separable but not cardinally
calibrated. If increments vary with `i`, the consequence interacts with the
base object.

### C. Composition with calibrated occupancy access

Mechanical conservativity preserves the occupancy difference `x`. Semantic
calibration supplies the comparison argument:

```text
x^T r + (c_plus-c_minus).
```

The v0.28 midpoint-localization theorem therefore applies without changing
the base row. Both certificates are required by the registered eligibility
rule.

### D. Mechanics-only semantic no-go

No procedure whose input is restricted to `(S,A,P,d0,H,phi)` and consequence
labels can certify the semantic coefficient. The same mechanically
conservative extension is compatible with:

```text
V_ij  = u_i + c_j,
V'_ij = u_i + kappa c_j,
```

and with context-interacting tables. These alternatives have identical
non-reward mechanics.

Even a complete population-response grid leaves positive scale unidentified
when `kappa` is unknown and the response-link class is closed under positive
rescaling:

```text
(u, kappa, F)
and
(alpha u, alpha kappa, F_alpha),

F_alpha(t) = F(t/alpha),
```

induce identical response laws. A semantic unit must therefore enter through
external calibration or a stronger behavioral measurement structure; it is
not created by a product-MDP construction.

### E. Approximate semantic certificate

Define anchored residuals:

```text
e_ij =
  V_ij - V_i,j0 - (c_j-c_j0).
```

If `|e_ij| <= epsilon` for every cell, then the bias in any two-sided
consequence difference is at most:

```text
2 epsilon.
```

The factor two is sharp.

## Proof

For A, equality of initial laws and transition kernels gives equality of the
state distribution at time zero and preserves it inductively at each finite
time. Equality of action sets preserves policy feasibility, and equality of
the feature map turns equality of transition occupancies into equality of
target-feature occupancies.

For B, the anchored equations imply:

```text
V_ij = V_i,j0 + c_j-c_j0.
```

Set `u_i=V_i,j0` and absorb `-c_j0` into the common constant. The converse is
immediate. In vectorized form, each constraint has its own non-reference cell
with coefficient one, so the rows are linearly independent and have rank
`m(n-1)`. If one is omitted, perturb only its unique non-reference cell.

For C, A fixes the occupancy row and B adds the declared scalar offset, which
is precisely the v0.28 access model.

For D, reward or scalar comparison values are absent from the mechanical
input. Replacing one compatible value table by another cannot alter a
mechanics-only transcript. Under population access, rescale `u` and `kappa`
by `alpha` and replace `F` by `F_alpha`; the scalar passed into the original
link is unchanged.

For E, a comparison using cells `(i,a)` and `(k,b)` has consequence-offset
bias:

```text
e_i,a - e_k,b.
```

The triangle inequality gives `2 epsilon`. Assigning `+epsilon` and
`-epsilon` to two cells attains equality.

## Claim boundary

Exogenous MDP decomposition, additive conjoint measurement, reward
invariances, environment design, rectangular separability, and the triangle
inequality are established mathematics. Novelty is not claimed.

The theorem assumes scalar comparison arguments for the semantic certificate;
it does not derive them from ordinal preferences. It does not establish that
money, tokens, approval, or another real consequence has a stable cardinal
utility coefficient; validate a demonstrator model; characterize coarser MDP
equivalences; or resolve ASMP-9.
