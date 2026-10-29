# ASMP-9 discounted-shaping verification protocol v0.6

## Status

Prospective verification protocol. All oriented simple graphs through five
vertices and the unit tests' planted graphs are burned development data.

## Frozen claims

For `0<gamma<1`, with:

```text
(D_gamma Phi)(u->v)=gamma Phi(v)-Phi(u),
```

the registered claims are:

```text
rank(D_gamma)=|V|-b_gamma(G),

dim(R^E / im D_gamma)=|E|-|V|+b_gamma(G),
```

where `b_gamma(G)` is the number of balanced weak gain-graph components.

For a finite trajectory:

```text
q_tau^T D_gamma Phi
=gamma^T Phi(s_T)-Phi(s_0).
```

Thus trajectory comparisons are shaping-invariant exactly when their
discounted boundary signatures match.

Endpoints:

```text
gamma=1: rank=|V|-c(G);
gamma=0: rank=number of distinct edge sources.
```

## Fresh verification cells

### Rank cells

Seed `96061`: 32,768 oriented simple graphs on six vertices. For every graph,
exact rational matrix rank must match the balanced-component formula at:

```text
gamma in {1/3, 2/5, 99/100}.
```

### Multigraph cells

Seed `96062`: 8,192 seven-vertex directed multigraphs with self-loops,
parallel edges, and opposite-direction pairs. Check `gamma in {3/7,7/8}`.

### Endpoint cells

On every rank and multigraph cell, check the separate `gamma=0` and `gamma=1`
formulas.

### Trajectory cells

- seed `96063`: 16,384 random trajectories, rational potentials, and
  `gamma in {1/3,2/3,9/10}`; telescoping must hold exactly;
- seed `96064`: 4,096 matched-boundary trajectory pairs; shaping contributions
  must cancel exactly;
- seed `96065`: 4,096 same-start/end but unequal-horizon pairs; a registered
  terminal potential must witness non-invariance.

### Planted access controls

- directed cycles of lengths 2 through 128 must have discounted quotient
  dimension zero and ordinary quotient dimension one;
- equal-length two-route diamonds of lengths 2 through 32 must retain one
  discounted quotient direction;
- replacing one route by a one-step-shorter route must make the component
  unbalanced and reduce the quotient dimension from one to zero.

## Gates

- **G0:** registration, clean tree, implementation ancestry, and all hashes
  agree;
- **G1:** every fresh simple-graph rational rank matches the theorem;
- **G2:** every fresh multigraph rational rank matches the theorem;
- **G3:** both endpoint formulas match exact rank;
- **G4:** every random trajectory telescopes exactly;
- **G5:** every matched-boundary pair cancels shaping exactly;
- **G6:** every unequal-horizon control has distinct boundary signatures and a
  nonzero shaping witness;
- **G7:** every planted cycle, diamond, and shortcut follows the frozen
  quotient prediction.

All gates passing yields:

```text
discounted_shaping_gain_quotient_implementation_verified.
```

## Claim boundary

The written proof carries a classical gain-graph rank specialization and a
standard shaping telescoping identity. The run verifies implementation and
access consequences. It does not establish policy-based reward
identifiability, all invariance transformations, behavioral sufficiency,
human consistency, or a full ASMP-9 resolution.

## Resources

CPU only; 4 GiB RAM; 10 minutes; no GPU.
