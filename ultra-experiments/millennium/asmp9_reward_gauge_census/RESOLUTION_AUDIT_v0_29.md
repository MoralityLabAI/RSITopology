# ASMP-9 resolution audit after v0.29

## Verdict

**ASMP-9 remains unresolved.**

Version v0.29 closes the finite linear decision-relevance handoff left open by
v0.28:

```text
calibrated occupancy error
  -> quotient reward error
  -> policy regret or policy-identity certificate.
```

It also proves that positive reward scale may be irrelevant to a fixed-MDP
argmax while remaining essential to a fixed-unit regret threshold. The
legitimate quotient therefore depends on the declared downstream task.

This is a classical finite feature-occupancy result. It is not evidence that a
learned reward is correct or that regret against that reward captures safety.

## Status against the five obligations

### 1. Maximal invariance groups

**Partially addressed in declared finite linear models; open generally.**

The program distinguishes potential-shaping gauge, positive scale,
response-link shape, cell and context midpoints, component gauge, observation
kernel, and an arbitrary declared linear subspace `G`.

Version v0.29 adds the downstream test: `G` is a legitimate policy-decision
gauge exactly when every registered policy-occupancy difference annihilates
it. Positive scale is legitimate for argmax but not for fixed-unit regret.

There is still no maximal invariance classification for arbitrary policy data,
history-dependent or nonlinear reward, safety constraints, strategic
demonstrators, or non-expected-utility preferences.

### 2. Necessary and sufficient access conditions

**Sharp for the registered linear occupancy and finite-policy model; open for
practical and general environment access.**

Version v0.28 proves homogeneous scale nonidentification, calibrated
localization, the exact quotient criterion `ker(X)=G`, and an explicit finite
deterministic MDP realization for every registered integer row matrix.

Version v0.29 proves that quotient reconstruction supports the declared
policy decision if and only if the gauge is decision-null on policy
differences. An invalid-gauge control correctly makes the certificate
unavailable.

Open questions include semantics-preserving practical numeraires, reachable
row families in constrained natural environments, and policy families whose
occupancy set is unknown or learned.

### 3. Sharp query, sample, and intervention-order bounds

**Population row complexity, scalar localization, and the finite-policy regret
constant are sharp in the registered model; stochastic policy complexity
remains incomplete.**

At least `p-dim(G)` independent localized rows are necessary, with equality
when the allowed row family spans the quotient. Version v0.26 supplies a
matching dyadic scalar threshold bound; v0.28 supplies the exact quotient
conditioning factor `1/sigma_min(XU)`.

Version v0.29 adds the exact selected-policy factor:

```text
||mu_opt-mu_selected||_2,
```

with an equality witness, and its global replacement by the policy-occupancy
diameter.

Sharp finite-sample policy-selection rates under heterogeneous margins,
dependent responses, adaptive allocation, and occupancy estimation remain
missing.

### 4. Robustness to behavioral misspecification

**Structurally advanced, not closed.**

Versions v0.26-v0.28 separate common link shape, common midpoint, arbitrary
midpoint drift, context-only drift, scale, and row-space ambiguity. Version
v0.29 shows precisely how any surviving quotient error propagates to one
finite policy decision.

Still outside scope are approximately calibrated numeraires, side effects of
the offset intervention, latent context, approximate midpoint factorization,
response dependence, contamination, temporal drift, strategic answers,
non-scalar choice, and misspecified occupancy features.

### 5. No-go theorem without a coherent latent value object

**Several exact special-case no-go results exist; no complete
classification.**

Arbitrary cell-midpoint drift can absorb every utility change. Unlimited
homogeneous occupancy interventions cannot identify positive scale against a
rescalable unknown link, even adaptively. A declared gauge that is not
decision-null makes quotient-level policy certification ill-posed.

These are distinct failure mechanisms. They do not classify every
demonstrator law lacking a coherent scalar or quotient value object.

## Evidence

```text
implementation commit
  c54dde192b432b32feb41625a2db16f073e392b7

registration commit
  283c3420d940dcd1f8cf39df75a664d51555ce2c

registration SHA-256
  a2fe94f2be38ce9e4681de7a8466511172b5845dd408560db798b1901dc244f7

result SHA-256
  0d9b00cacfc4f6451df7dc5719636bff8b3533711e36b1de4b51a49ee7b5dd0e

run-receipt SHA-256
  485c3c73020f0bf8287b85cacf2c6162b32764141ab325343902f605bb80f878

independent-verification SHA-256
  7b91d202ba97f027bd1e3e220c9be420240ce306e7621c509aef1e6b35d10dae
```

The registered run passed ten of ten gates. The import-independent verifier
passed nineteen of nineteen checks.

## Next load-bearing sequence

### A. Semantics-preserving numeraire realization

Replace the synthetic calibrated consequence with a declared intervention
inside one fixed MDP. Characterize when it preserves the transition law,
horizon, feasible policies, feature occupancies, and the meaning of the target
reward.

### B. Approximate calibration and midpoint factorization

Freeze bounded context-midpoint drift and bounded numeraire-coefficient error.
Derive compatible, refuted, inconclusive, and unavailable decisions with
matching lower bounds, then propagate the resulting set-valued reward
uncertainty through the v0.29 support function.

### C. Sharp stochastic policy complexity

Combine the response-margin envelope, graph spectral floor, quotient singular
value, and policy-margin geometry in one adaptive minimax sample theorem.
Separate threshold localization, factorization-test power, occupancy
estimation, and policy-selection error.

### D. Broader decision targets

Characterize the decision-null quotient for constrained, risk-sensitive,
history-dependent, and multi-objective policy criteria. The v0.29 linear
expected-return result supplies a baseline, not the general answer.

## Epistemic boundary

Version v0.29 proves when one finite linear reward quotient is sufficient for
one finite expected-return policy decision. It does not show that the quotient
is behaviorally correct, that a safe policy exists, or that ASMP-9 is
resolved.
