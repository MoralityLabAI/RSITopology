# ASMP-9 capped-simplex modulus verification protocol v0.63

Status: **prospective protocol; scientific settings freeze before execution**.

## Estimand

On the fixed three-alternative binary-choice fiber, verify the exact
full-dimensional formulas

```text
dist_TV(q,P)=V(q),

Delta(P,N_gamma)=gamma,

Lambda(P,N_gamma)=1+(5/2)gamma.
```

The continuous proof is in `THEOREM_DRAFT_v0_63.md`.  Finite verification
checks the implementation and explicit certificates; it does not replace
the proof.

## Burned development cells

The following values were inspected during development and may not count as
fresh confirmation:

```text
gamma={1/4096,3/1600,1/200,1/50},
grid denominators={20,40}.
```

The prospective cells in `verification_cells_v0_63.json` must be disjoint
from both sets.

## Frozen objects

```text
alternatives=(a,b,c),
caps=(2/5,3/5,2/5),
probability floor=1/10,
0<gamma<=1/50,
TV=half L1 on the full-menu distribution,
rho=max coordinatewise symmetric probability ratio.
```

Binary choice probabilities and ranking order are those in
`THEOREM_DRAFT_v0_63.md`.

## Gates

### H0 - binding and chronology

Every source and burned-development artifact must match the prospective
registration.  The registered source commit must be an ancestor of the
execution commit.

### T0 - prereveal tests

The exact unit suite must report the frozen expected pass count.

### R0 - RUM reconstruction

On every prospective exact-grid point:

- the ranking weights sum to one;
- weight nonnegativity agrees with capped-simplex membership; and
- every RUM point reconstructs the full-menu and fixed binary responses.

### P0 - exact projection

On every prospective exact-grid point:

- the constructive projection is in the floor-truncated RUM polygon;
- its TV distance equals `V(q)`; and
- exhaustive comparison with all same-grid RUM points finds no smaller
  distance.

### M0 - exact moduli

For every fresh gamma cell:

- the primal pair has TV distance `gamma`;
- its symmetric ratio is `1+(5/2)gamma`;
- all four feasible labelled violation supports obey their registered lower
  formulas; and
- the minimum support bound equals the claimed `Lambda`.

### C0 - corruption-boundary constructions

For every fresh gamma cell:

- the normalized-max Huber observation yields two valid contaminant
  distributions at `epsilon=gamma/(1+gamma)`; and
- the common recorded subprobability law yields two valid recording vectors
  at `u/ell=1+(5/2)gamma`.

### X0 - freshness

Prospective gamma cells and grid denominators must be disjoint from their
burned development counterparts.

### I0 - independent replay

An import-independent implementation must reproduce the primary rows,
counts, gates, and fact digest exactly.

### RESOURCE

The run must use one worker, remain below the registered wall-time and
resident-memory caps, and leave no background process.

## Decision

```text
all gates pass:
  capped_simplex_moduli_verified

otherwise:
  verification_failed
```

There is no discretionary near-pass override.

## Claim boundary

Passing verifies one full-dimensional finite calibration theorem with
matching primal and dual certificates.  It does not establish novelty,
efficient general modulus computation, hidden-menu or latent-confounding
identification, strategic/dynamic response, physical query access, welfare
semantics, or a resolution of ASMP-9.

