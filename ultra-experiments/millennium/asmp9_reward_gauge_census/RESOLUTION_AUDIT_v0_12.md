# ASMP-9 resolution audit after v0.12

Date: 2026-07-28

## Verdict

**ASMP-9 is not resolved.**

Version v0.12 adds a robust finite extension to the v0.11 contextual
scalar-gluing theorem. It separates within-context non-scalarity from
cross-context non-gluing, gives the exact Euclidean repair radius, and
distinguishes the number of identifying checks from their worst-case noise
amplification.

The result is classical nested-subspace and experimental-design mathematics
specialized to a prospectively registered finite access grammar. It is not a
general value-identifiability or inverse-reinforcement-learning theorem.

## New evidence

| Layer | Authoritative evidence | What is proved | Resolution status |
|---|---|---|---|
| Robust inconsistency decomposition | [v0.12 public summary](robust_context_gluing_v0_12/PUBLIC_SUMMARY_v0_12.md) | Squared distance to the shared-scalar model decomposes exactly into cross-context non-gluing and within-context non-scalarity. | Complete for the declared finite Euclidean model. |
| Exact repair radius | [v0.12 theorem](robust_context_gluing_v0_12/THEOREM_v0_12.md) | `dist(y,G)` is the minimum Euclidean correction needed to reach the shared-scalar subspace. | Exact under the declared norm; no stochastic coverage claim. |
| Query count versus conditioning | [v0.12 verification](robust_context_gluing_v0_12/verification_v0_12.json) | At least `q` queries are necessary; square row-normalized designs have amplification at least one, attained exactly by orthonormal designs. | Complete for arbitrary linear queries on the finite quotient. |
| Cycle-query counterexample | [v0.12 exact witness](robust_context_gluing_v0_12/CONDITIONING_COUNTEREXAMPLE_v0_12.md) | A six-support shortest cycle basis amplifies error by `sqrt(3/2)`, while an eight-support basis attains one. | Exact finite counterexample. |
| Fresh conditioning census | [v0.12 sealed result](robust_context_gluing_v0_12/artifacts_v0_12/RESULT_v0_12.md) | 103 of 512 fresh cells had a conditioning-suboptimal shortest basis; maximum ratio was `sqrt(3)`. | Synthetic liveness and prevalence evidence, not a population theorem. |

## Effect on the five obligations

### 1. Maximal invariance groups

**Improved but partial.** Versions v0.11-v0.12 identify the quotient separating
context-local and globally shared scalar models and quantify its Euclidean
geometry. They do not unify response-link, temperature, shaping, context, and
history transformations into one maximal invariance classification.

### 2. Necessary and sufficient access

**Substantially improved, still partial.** Exactly `q` independent linear
queries are necessary and sufficient to identify the finite context-gluing
coordinate. Version v0.12 adds the conditioning criterion for robust
reconstruction. There is no matching theorem for passive or adaptive
sequential demonstrations with latent context.

### 3. Sharp query, sample, and intervention-order bounds

**Improved but partial.** The exact query-count lower bound is now paired with
a sharp normalized amplification bound. The result also proves that
minimum-support simple-cycle bases can be condition-suboptimal. Matching
finite-sample minimax bounds and optimal adaptive allocation remain open.

### 4. Behavioral misspecification robustness

**Improved but still far from resolution scope.** This is the first ASMP-9
result in the sequence to give an exact quantitative repair radius and to
propagate bounded query error through the gluing coordinate. The improvement
is conditional on a known linear observation model, observed context labels,
and a chosen Euclidean norm. It does not cover response-model error,
policy-estimation error, latent-context error, approximate rationality,
dependent samples, or strategic reporting.

### 5. No-go classification

**Improved but incomplete.** The program now has an exact no-go for treating
query count or support size as a robustness certificate: both can be optimal
while conditioning is not. It still lacks a classification for arbitrary
history-sensitive, inconsistent, non-EU, or strategically reported
preferences.

## Highest-value remaining sequence

### Approximate contextual and sequential closure

The next useful result should move beyond deterministic Euclidean perturbation
without weakening the claim boundary:

- finite-sample lower bounds matching the existing coherence upper bound;
- context assignment error and latent-context uncertainty;
- norm sensitivity rather than one application-independent metric claim;
- adaptive allocation of comparisons and environments;
- sequential/history-dependent observation kernels; and
- explicit positive or no-go results for inconsistent demonstrators.

### Consolidation without a novelty overclaim

A typed index of the finite access models remains useful engineering work, but
the v0.12 prior-art gate correctly rejected a generic access-lattice theorem
as novelty-bearing. Any consolidation should be presented as an index over
already established invariances, not as new partition or subspace theory.

## Completion criterion

Current results cover exact comparison access, finite noisy choices,
discounted shaping, unknown response links, known finite soft policies,
deterministic-policy obstructions, finite contextual scalar existence, and a
bounded-error context-gluing geometry.

A defensible resolution still requires a maximal invariance classification
over a materially broad source family, matching upper and lower access bounds,
finite-sample and misspecification guarantees, and a sequential
no-go/positive theorem for history-sensitive behavior.
