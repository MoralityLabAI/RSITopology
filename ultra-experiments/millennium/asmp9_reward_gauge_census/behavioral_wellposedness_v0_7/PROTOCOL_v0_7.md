# ASMP-9 behavioral well-posedness verification protocol v0.7

## Status

Prospective CPU-only verification protocol. Every oriented simple graph through
five vertices and all current unit-test fixtures are burned development data.

## Frozen claims

For a directed comparison graph `G=(V,E)` with exact antisymmetric log-odds
scores:

```text
coherent response law: l_(i,j)=theta_j-theta_i.
```

The registered access ledger is:

```text
scalar reconstruction, coherence promised: |V|-c(G);
coherence-only certification:               all non-bridge edges;
reconstruction plus certification:          |E|;
post-forest model-checking surcharge:        beta_1(G).
```

An edge field is coherent exactly when its fundamental-cycle residuals vanish.
Its exact least-squares Hodge residual is orthogonal to every gradient field
and is zero exactly for coherent data.

For a directed cycle `C` of length `k`, every scalar approximation residual
obeys:

```text
||r_C||_2^2 >= circulation(C)^2/k,
||r_C||_infinity >= |circulation(C)|/k.
```

For deterministic optimal-policy threshold observations on
`theta in [0,1]`, the sharp worst-case ambiguity widths after `k` queries are:

```text
adaptive:    2^-k;
nonadaptive: 1/(k+1).
```

No finite `k` exactly identifies the continuum.

## Fresh cells

### Graph access cells

- seed `97071`: 32,768 oriented simple graphs on six vertices;
- seed `97072`: 8,192 directed multigraphs on seven vertices, including
  loops, parallel edges, and opposite directions;
- seed `97073`: rational latent utilities and planted edge corruptions.

Every cell checks the access counts, exact reconstruction from a spanning
forest, corruption detection on a non-bridge edge, and preservation of
coherence after changing a bridge score.

### Hodge and cycle cells

- seed `97074`: 4,096 rational edge fields on seven-vertex multigraphs;
- seed `97075`: 1,024 directed cycles of lengths 3 through 12 with rational
  scores.

The Hodge residual must be exactly orthogonal to the incidence image and must
vanish exactly when the fundamental-cycle test does. Every cycle bound must
hold exactly.

### Policy-access cells

- adaptive binary search for every `k=0..24`, using a non-dyadic witness;
- optimal nonadaptive grids for every `k=0..1024`;
- seed `97076`: 4,096 random nonadaptive threshold designs with
  `k=1..64`.

The registered widths must be attained by the optimal constructions, and no
random design may beat the lower bound.

### Inconsistent-demonstrator control

The three-edge unit-circulation preference cycle must fail scalar coherence,
have cycle residual `3`, and have a nonzero Hodge residual.

## Gates

- **G0:** registration commit, implementation ancestry, tree cleanliness, and
  every sealed hash agree;
- **G1:** all simple-graph access and reconstruction checks pass;
- **G2:** all multigraph access and reconstruction checks pass;
- **G3:** all Hodge projection checks pass;
- **G4:** all cycle lower-bound checks pass;
- **G5:** the inconsistent-demonstrator control is detected;
- **G6:** every adaptive width equals `2^-k`;
- **G7:** every optimal nonadaptive width equals `1/(k+1)` and random designs
  do not beat it;
- **G8:** every finite registered policy-query count retains positive
  worst-case ambiguity.

All gates passing yields:

```text
behavioral_reconstruction_model_checking_split_verified.
```

## Claim boundary

This verifies an exact population-law graph instrument and a deterministic
threshold-policy calibration. It is not finite-sample Bradley-Terry
estimation, a general IRL identifiability theorem, a human consistency model,
or a complete ASMP-9 resolution. The underlying mathematics is classical.

## Resources

CPU only; 4 GiB RAM; 10 minutes; no GPU.
