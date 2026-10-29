# Which response-link heterogeneity survives offset calibration?

## Result

Version v0.27 gives a three-way boundary for the strong offset access
introduced in v0.26.

### 1. Link shape may vary freely if the midpoint is shared

For an item coordinate `i`, context `c`, known offset `a`, and a
cell-specific strictly increasing link `F_(i,c)`, suppose:

```text
F_(i,c)(0)=1/2.
```

Then:

```text
sign(F_(i,c)(d_i+a)-1/2)=sign(d_i+a).
```

The response curves may have different shapes and slopes. At population
level, their common known midpoint is sufficient for link-free threshold
localization. The common *shape* assumed in v0.26 was stronger than needed.

### 2. Arbitrary midpoint drift destroys utility identification

If cell `(i,c)` instead has an unknown midpoint `b_(i,c)`, offset access
identifies only:

```text
z_(i,c)=d_i-b_(i,c).
```

For any alternative utility vector `d'`, shifting each midpoint by

```text
b'_(i,c)=b_(i,c)+d'_i-d_i
```

preserves every effective threshold. Unlimited population queries cannot
separate the two utility vectors. This is an exact structural obstruction,
not sampling noise.

### 3. Context-only drift is a bipartite synchronization problem

Under the intermediate assumption

```text
b_(i,c)=b_c,
z_(i,c)=d_i-b_c,
```

the localized thresholds are the incidence image of the item-context
bipartite graph `H`. Therefore:

```text
rank(A_H)=|I|+|C|-components(H),
beta_1(H)=|E|-|I|-|C|+components(H).
```

The utility and context-bias parameters are identified modulo one joint shift
per connected component. A connected graph leaves one global
utility-versus-midpoint gauge; an externally known midpoint or one equivalent
normalization is still required to recover anchored utility levels. A
disconnected design cannot compare component levels.

A spanning forest reconstructs all quotient parameters under the model. The
remaining `beta_1(H)` chord measurements are exactly the independent
compatibility checks.

## The liveness rule

If `beta_1(H)=0`, every edge assignment factorizes as `d_i-b_c`. A tree may be
useful for reconstruction under the assumption, but it cannot provide
evidence for the assumption. Its correct certification status is:

```text
factorization_unavailable_by_design
```

When `beta_1(H)>0`, nonzero cycle circulation refutes context-only midpoint
drift. The four-cell item-context square is the smallest live design.

This separates two resources that are often conflated:

- connectivity is needed to share a coordinate system;
- cycles are needed to test whether that coordinate system is valid.

## Robust boundary

For approximate threshold measurements

```text
z_hat=A_H theta+e,
```

least-squares quotient error obeys:

```text
||theta_hat-theta||_2
  <= ||e||_2 / sigma_min^+(A_H)
  = ||e||_2 / sqrt(lambda_min^+(L_H)).
```

The constant is the exact pseudoinverse operator norm. Connectivity is the
exact identifiability threshold, while a positive spectral floor is the
stability threshold.

The orthogonal residual is the exact Euclidean distance to the context-only
model. Under an error budget `epsilon`, a residual above `epsilon` refutes the
model; a smaller residual is merely compatible or inconclusive.

## Prospective verification

The registered CPU run checked:

- 5,207 fresh utility thresholds;
- 585 link-shape/sign cells across logistic, arctangent, and rational links,
  with zero mismatches;
- a six-edge arbitrary-midpoint witness with utility displacement `10` and
  identical effective thresholds;
- four fresh access graphs, including connected, disconnected, cyclic, and
  acyclic designs;
- exact component, rank, cycle-rank, forest, and chord identities;
- three live planted cycle refutations;
- one tree correctly returned as unavailable; and
- two deterministic noisy reconstructions satisfying the registered spectral
  bound.

All nine gates and all sixteen independent verification checks passed.

## Prior-art and novelty boundary

Rasch-model connectedness, two-way additive identification, graph-incidence
rank, Hodge residuals, pseudoinverse stability, and threshold bisection are
classical. No novelty is claimed for these ingredients.

The contribution is an ASMP-9 access ledger that identifies the shared
midpoint—not shared link shape—as the operative robustness condition, and
states exactly when weaker context-only midpoint structure is identifiable,
stable, and falsifiable.

## Claim boundary

The result does not establish that real human or model response links have
shared midpoints, that context is observed correctly, that cardinal offsets
are implementable without side effects, that finite bisection certifies exact
factorization, or that ASMP-9 is resolved.

