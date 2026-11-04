# ASMP-9 resolution audit after v0.27

## Verdict

**ASMP-9 remains unresolved.**

Version v0.27 sharpens the behavioral robustness boundary:

```text
heterogeneous shape + common known midpoint
  -> offset localization survives;

arbitrary cell midpoint drift
  -> utility is completely confounded;

context-only midpoint drift
  -> incidence quotient, component gauges, cycle liveness,
     and Laplacian stability.
```

This removes the common-link-shape assumption from the population theorem. It
does not remove the need for midpoint structure or for a practical cardinal
offset.

## Status against the five obligations

### 1. Maximal invariance groups

**Partially addressed in declared finite models; open generally.**

The program now distinguishes reward gauge, link shape, cell midpoint,
context midpoint, and component gauge. For the v0.27 context-only model,
`ker(A_H)` is the complete parameter gauge: one joint shift per connected
component.

There is still no maximal invariance classification for arbitrary policy
data, history-sensitive reward, non-expected-utility preferences, or
strategic demonstrators.

### 2. Necessary and sufficient access conditions

**Sharp for two offset-query models; open generally.**

Version v0.26 gives full threshold coverage as the scalar offset condition.
Version v0.27 adds:

- one observed shared-midpoint cell per item for independent localization;
- connectedness for one global context-bias quotient;
- cycle rank for a live test of the context-only midpoint restriction; and
- one calibration constraint per component to fix absolute
  utility-versus-midpoint level.

Whether ordinary environment or policy interventions can realize these
cardinal offsets without changing the target semantics remains open.

### 3. Sharp query, sample, and intervention-order bounds

**Structural ranks and v0.26 population bounds are sharp; noisy and practical
intervention complexity remain incomplete.**

The exact parameter dimension is `|V(H)|-components(H)` and the compatibility
dimension is `beta_1(H)`. The robust amplification constant is the exact norm
of the incidence pseudoinverse. These are structural query dimensions, not a
new finite-sample minimax theorem.

Matching noisy-query lower bounds, adaptive sequential allocation near each
midpoint, and general finite-MDP intervention-order bounds remain missing.

### 4. Robustness to behavioral misspecification

**Substantially advanced, not closed.**

Cell-specific link shapes and slopes are now allowed. The result gives an
exact no-go theorem for arbitrary cell midpoint drift and an intermediate
positive theorem for context-only drift.

Still outside scope are unknown or latent context, midpoint drift that only
approximately factorizes, response dependence, contamination, temporal
drift, strategic answers, and non-scalar choice.

### 5. No-go theorem without a coherent latent value object

**A stronger exact special-case no-go now exists; no complete classification.**

Arbitrary cell midpoint drift can absorb every change in the item utility
vector while preserving all offset thresholds. Cycle residuals can refute the
context-only restriction only on live cyclic designs.

This classifies one failure mechanism. It does not characterize every
demonstrator law without a coherent scalar or quotient value object.

## Evidence

```text
implementation commit
  ea335d0b0316b4e293b76d3bfa2ec252074a21ab

registration commit
  deddcb97a8eb0401a14e1182bbd0f32bd11cb18a

registration SHA-256
  706764883d5b65398850f61982a10e8d7a7d4b14d1c60afd2ca6e2864aaa22a5

result SHA-256
  64ed8a0d390d1ffa5a0f47a55571447267fd9c819efee5d62e4c4b2193f6c1df

run-receipt SHA-256
  0a6217e6f7effc08b66532927d093f4d3b6c1cf8fe9849aa543325f9c8dd423c

independent-verification SHA-256
  77c9ff5b7a9b25917c4ba2980e23d9d25ca04523daf06478ec94fa4cd5953318
```

The registered run passed nine of nine gates. The import-independent verifier
passed sixteen of sixteen checks.

## Next load-bearing sequence

### A. Environment realization

Replace the abstract `d_i+a` primitive with a finite-MDP intervention. State
necessary and sufficient conditions for adding a known offset to one
alternative while preserving transition and context semantics.

### B. Approximate midpoint factorization

Freeze a contamination or bounded-drift class around `b_(i,c)=b_c`. Derive a
total decision rule and matching lower bounds for coherent, refuted, and
unavailable outcomes.

### C. Sharp stochastic complexity

Derive minimax adaptive query bounds under the v0.26 margin envelope and the
v0.27 graph spectral floor. Separate threshold-localization error from
factorization-test power.

### D. Decision relevance

Prove how quotient-reconstruction error or midpoint-model failure bounds
regret for a declared policy choice. Without that reduction, identifying a
latent coordinate remains an instrument result rather than a safety theorem.

## Epistemic boundary

Version v0.27 shows exactly how one form of link heterogeneity enters the
reward gauge. It does not show that the declared model is behaviorally true,
that its offset intervention exists in practice, or that ASMP-9 is resolved.

