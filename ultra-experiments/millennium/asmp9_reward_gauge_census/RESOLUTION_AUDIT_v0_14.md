# ASMP-9 resolution audit after v0.14

Date: 2026-07-28

## Verdict

**ASMP-9 is not resolved.**

Version v0.14 proves a finite conditional/unconditional separation for one
Bradley-Terry cycle experiment. Conditioning on vertex win balance removes
the scalar nuisance exactly, but an unbounded scalar-gradient family can
concentrate almost all probability on uninformative singleton fibers. The
conditional test remains exact while its unconditional gain above size
vanishes.

A fixed probability-interior assumption restores a strictly positive finite
lower bound. This identifies an assumption that a positive access theorem
must expose; it does not supply the broad behavioral theorem required by
ASMP-9.

## New evidence

| Layer | Authoritative evidence | What is proved | Resolution status |
|---|---|---|---|
| Informative-fiber probability | [v0.14 theorem](unconditional_availability_v0_14/THEOREM_v0_14.md) | A closed exact formula gives the probability that a cycle balance fiber has positive quotient dimension. | Exact for independent equal-count Bernoulli cycle data. |
| Conditional/unconditional factorization | [v0.14 public summary](unconditional_availability_v0_14/PUBLIC_SUMMARY_v0_14.md) | Excess power is the alternative fiber mass weighted by the conditional gain. | Exact for the registered one-sided conditional test. |
| Nuisance-uniform no-go | [v0.14 sealed result](unconditional_availability_v0_14/artifacts_v0_14/RESULT_v0_14.md) | An explicit scalar-gradient nuisance makes informative-fiber probability and unconditional gain converge to zero without invalidating conditional exactness. | A constructive no-go within the frozen model. |
| Interior positive arm | [v0.14 verification](unconditional_availability_v0_14/verification_v0_14.json) | A fixed `epsilon=1/4` class gives a positive lower bound in all 18 fresh positive-control cells. | A sufficient finite guarantee, not a sharp minimax frontier. |

## Effect on the five obligations

### 1. Maximal invariance groups

**Unchanged and partial.** Version v0.14 uses the scalar-gradient nuisance
identified in v0.13. It does not unify reward shaping, response temperature,
unknown links, context, history, and non-expected-utility transformations
into one maximal invariance classification.

### 2. Necessary and sufficient access

**Improved within one finite experiment.** Version v0.13 gave the exact
fiber-rank condition after conditioning. Version v0.14 adds the probability
of reaching an informative fiber and proves that conditional accessibility
need not yield unconditional detectability. A broad necessary-and-sufficient
condition over designs, nuisance classes, and response laws remains open.

### 3. Sharp query, sample, and intervention-order bounds

**Improved but incomplete.** The upper and lower power inequalities are exact.
The registered nuisance collapse is decisive, but the interior lower bound is
conservative. There is no matching minimax allocation theorem, sharp adaptive
sample bound, or optimal intervention policy.

### 4. Behavioral misspecification robustness

**Not materially closed.** The result assumes independent Bernoulli
comparisons and a known logistic link. It does not cover overdispersion,
dependence, latent contexts, strategic responses, policy-estimation error, or
non-expected-utility demonstrators.

### 5. No-go classification

**Materially improved but incomplete.** Version v0.14 supplies an explicit
no-go for nuisance-uniform unconditional power based on conditional exactness
alone. It also lists sufficient escape routes: a probability interior,
balancing intervention, nuisance distribution, or availability floor. It is
not a complete impossibility classification for arbitrary behavior or
history-sensitive access.

## Highest-value remaining sequence

The next load-bearing work should broaden or sharpen the theorem rather than
add another presentation layer:

- derive matching minimax upper and lower bounds for trial allocation under a
  declared probability interior;
- compare passive fixed graphs with adaptive balancing interventions;
- replace independent Bernoulli responses with registered overdispersed and
  dependent alternatives;
- integrate unknown-link and latent-context uncertainty with the conditional
  quotient;
- connect comparison-fiber availability to sequential finite-MDP behavior;
  and
- prove a positive theorem or impossibility result under a materially broader
  misspecification class.

## Completion criterion

Current results now cover exact and ordinal reward access, robust comparison
width, finite noisy choices, discounted shaping, unknown response links,
deterministic-policy obstructions, finite contextual scalar existence, robust
gluing geometry, conditional finite-sample quotient access, and the
conditional/unconditional availability separation.

A defensible ASMP-9 resolution still requires a maximal invariance
classification over a materially broad behavioral source family, matching
upper and lower access bounds, finite-sample and misspecification guarantees,
and a sequential no-go/positive theorem for history-sensitive behavior.
