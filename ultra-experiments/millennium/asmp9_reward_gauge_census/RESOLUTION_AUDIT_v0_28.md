# ASMP-9 resolution audit after v0.28

## Verdict

**ASMP-9 remains unresolved.**

Version v0.28 closes one stylized environment-realization gap and separates
three resources:

```text
occupancy interventions  -> quotient row span;
known cardinal numeraire -> positive scale;
response margin          -> finite-sample threshold cost.
```

It proves that homogeneous reward-independent interventions cannot calibrate
positive scale against a rescalable unknown link, even adaptively. It also
constructs a finite deterministic MDP realizing every finite integer
occupancy matrix and proves the exact criterion `ker(X)=G` for identification
modulo a declared linear reward gauge.

The construction is an existence result, not evidence that a practical
environment supplies a semantically valid cardinal consequence.

## Status against the five obligations

### 1. Maximal invariance groups

**Partially addressed in declared finite linear models; open generally.**

The program now distinguishes potential-shaping gauge, positive scale,
response-link shape, cell midpoint, context midpoint, component gauge, and an
arbitrary declared linear subspace `G`. Under calibrated occupancy access,
`ker(X)` is the complete linear ambiguity and exact identification modulo `G`
occurs precisely when the two agree.

There is still no maximal invariance classification for arbitrary policy data,
history-sensitive reward, non-expected-utility preferences, strategic
demonstrators, or nonlinear reward representations.

### 2. Necessary and sufficient access conditions

**Sharp for the registered linear occupancy model; open for practical and
general environment access.**

Version v0.28 proves:

- homogeneous occupancy rows alone cannot fix positive scale under the
  declared unknown-link class;
- an unknown-valued extra feature remains homogeneous;
- a known full-range additive consequence localizes each row;
- `ker(X)=G` is necessary and sufficient after localization; and
- every finite integer matrix has an explicit finite deterministic
  query-initial-state realization.

What remains open is whether a natural intervention can supply a known
cardinal consequence while preserving the target semantics, and which row
families are reachable inside constrained MDP classes without constructing a
new query environment around the desired matrix.

### 3. Sharp query, sample, and intervention-order bounds

**Population row complexity and scalar localization are sharp in the
registered model; stochastic policy complexity remains incomplete.**

At least `p-dim(G)` independent localized rows are necessary, with equality
when the allowed occupancy family spans the quotient. Version v0.26 supplies
the matching dyadic scalar threshold bound and shows that finite-sample
recovery needs a link-margin condition. Version v0.28 adds the exact
`1/sigma_min(XU)` stability constant.

Sharp adaptive sample allocation under heterogeneous margins, dependent
responses, constrained environment design, and policy-estimation error remain
missing.

### 4. Robustness to behavioral misspecification

**Structurally advanced, not closed.**

Versions v0.26-v0.28 separate common link shape, common midpoint, arbitrary
midpoint drift, context-only drift, positive scale, and row-space ambiguity.
The scale obstruction is uniform over the declared rescalable link class.

Still outside scope are approximately calibrated numeraires, side effects of
the offset intervention, latent context, approximate midpoint factorization,
response dependence, contamination, temporal drift, strategic answers, and
non-scalar choice.

### 5. No-go theorem without a coherent latent value object

**Several exact special-case no-go results exist; no complete
classification.**

Version v0.27 shows that arbitrary cell-midpoint drift can absorb every utility
change. Version v0.28 shows that unlimited homogeneous occupancy
interventions, including deterministic adaptive ones, cannot separate
positive reward scale from a rescalable unknown link; an unknown side-feature
coefficient does not help.

These results classify two failure mechanisms. They do not characterize every
demonstrator law lacking a coherent scalar or quotient value object.

## Evidence

```text
implementation commit
  fcab52dd08ff88f382d3a33d585bd439bfa3c99d

registration commit
  9fdeaca64da1e59c13ca24e00f54bf2fe0022eeb

registration SHA-256
  a8cd1d8633c2e4017889dbd06ddb90db1c9d1799432deb09a8e593da38d466af

result SHA-256
  0f7b5bb876f8b7b6d58f7b891ed6e54b69f0c7168db5eb379ea8c21d675fad14

run-receipt SHA-256
  97b152cf7ab380823ecd33b89969dbb49e67bc30be6a1e1018ec92051f8996f6

independent-verification SHA-256
  f8336fb7b93724e34cc183b9d42c2fe7c97ed699d8d0b88b3195ef1343e6d2e3
```

The registered run passed ten of ten gates. The import-independent verifier
passed eighteen of eighteen checks.

## Next load-bearing sequence

### A. Semantics-preserving numeraire realization

Replace the synthetic calibrated feature with a declared intervention class
inside one fixed MDP. Characterize when a known additive consequence can be
inserted without changing transition law, horizon, policy feasibility, or the
meaning of the target reward.

### B. Approximate midpoint and calibration factorization

Freeze bounded drift around the v0.27 context-only midpoint model and bounded
error in the v0.28 numeraire coefficient. Derive total compatible, refuted,
inconclusive, and unavailable decisions with matching lower bounds.

### C. Sharp stochastic complexity

Combine the v0.26 link-margin envelope, v0.27 graph spectral floor, and v0.28
quotient singular value in one adaptive minimax sample theorem. Separate
threshold-localization error, factorization-test power, and occupancy
estimation error.

### D. Decision relevance

Prove how quotient reconstruction error, scale nonidentification, or
midpoint-model failure bounds regret for a declared policy decision. Without
that reduction, latent-coordinate recovery remains an instrument result rather
than a safety theorem.

## Epistemic boundary

Version v0.28 shows how row span, scale calibration, and conditioning divide
the work in one finite linear access model. It does not show that the model is
behaviorally true, that its numeraire exists in practice, or that ASMP-9 is
resolved.
