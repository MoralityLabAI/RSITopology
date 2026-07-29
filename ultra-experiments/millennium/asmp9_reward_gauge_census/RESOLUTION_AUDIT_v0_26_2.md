# ASMP-9 resolution audit after v0.26.2

## Verdict

**ASMP-9 remains unresolved.**

Version v0.26.2 closes one previously explicit gap: it gives sufficient link
calibration, a sharp population-query boundary, a restricted-access lower
bound, a finite-sample sufficient condition, and a no-uniform-rate theorem
for one unknown-link offset-query model.

It does not classify the full query/intervention grammar, behavioral
misspecification class, or coherent-value boundary required by ASMP-9.

## New theorem boundary

For an anchored finite utility vector and an unknown strictly increasing
symmetric response link:

1. a known additive offset spanning every admissible indifference point
   reduces the response to a link-free threshold query;
2. coordinate bisection gives a `d ceil(log2(B/eta))` population upper bound;
3. metric entropy gives
   `ceil(log2((B/eta)^d))` as a matching worst-case lower bound on dyadic
   cells;
4. an offset ceiling `C<B` leaves a minimax error of at least `(B-C)/4`;
5. a declared margin envelope gives a conservative finite-sample upper bound;
   and
6. arbitrarily flat admissible links preclude a uniform finite-sample rate.

The original no-offset non-affine witness from v0.8 remains the negative
control. The new access works because it supplies a known cardinal yardstick,
not because ordinary comparison probabilities determine utility scale.

## Status against the five ASMP-9 obligations

### 1. Maximal invariance groups

**Partially addressed in declared models; not closed generally.**

Versions v0.1-v0.13 characterize additive, affine, potential-shaping,
discounted, contextual, conditional, and policy-induced quotients in several
finite models. Version v0.26 identifies translation as the remaining utility
gauge once a known offset fixes scale.

It does not prove a maximal invariance theorem for arbitrary data sources,
history-dependent rewards, non-expected-utility preferences, or general MDP
policy observations.

### 2. Necessary and sufficient query/environment interventions

**Sharp for the registered scalar-offset grammar; open generally.**

Within v0.26, full indifference-threshold coverage is sufficient and
restricted coverage has a matching explicit obstruction. This is the
cleanest necessary/sufficient access statement in the unknown-link branch.

The cardinal offset is assumed as an interface primitive. The result does not
characterize which physical environment interventions implement it, whether
weaker trajectory or policy interventions suffice, or how the threshold
changes under context-dependent links.

### 3. Sharp query, sample, and intervention-order bounds

**Population query complexity is sharp on dyadic cells; finite-sample and
general intervention complexity remain incomplete.**

Version v0.26 adds:

- a dimension-dependent population upper bound;
- a matching metric-entropy lower bound on the registered dyadic cells;
- a quantitative error floor for a restricted offset range;
- a conservative finite-sample upper bound under a margin condition; and
- a no-uniform-rate theorem without such a condition.

The finite-sample rate is not minimax. There is no matching noisy-query lower
bound under the margin envelope, no adaptive-vs-nonadaptive classification
beyond bisection in this grammar, and no general MDP intervention-order
theorem.

### 4. Robustness to behavioral misspecification

**Materially advanced, still open.**

The population result is uniform over all strictly increasing symmetric
links sharing midpoint `1/2`. It therefore removes the known-logit
assumption that constrained much of v0.9-v0.23.

The robustness class still assumes a common link, common midpoint, strict
monotonicity, item/context invariance, conditional independence for the
finite-sample interpretation, and exact implementation of cardinal offsets.
Dependence, contamination, drift, strategy, heteroskedastic item links,
midpoint shifts, and non-expected-utility choice remain outside the theorem.

### 5. No-go theorem without a coherent latent value object

**Only structured no-go results; no complete classification.**

Versions v0.7, v0.8, v0.11-v0.14, and v0.26 give explicit failures of scalar
coherence, global gluing, unknown-link identifiability, unconditional
availability, and rate-free finite-sample recovery.

These do not classify all demonstrator laws lacking a coherent scalar or
quotient value object. In particular, v0.26 assumes such an object and varies
only the response link.

## Evidence chain

```text
v0.26 implementation
  3a6882656dc5dae5b622c7e0496188bbf06a0e1d

v0.26 registration commit
  4857f51145061114239ef369cf4f1cd2980eb6d0

v0.26 registration SHA-256
  50cf84a1921ad943adc3d6fb65c62e34939ea6621a93c775c8f31c4db917c52e

v0.26 failed result commit
  da5faf8edc746add4cfea7d9357774690969e636

v0.26.1 implementation and registration
  ce2586192e067d4fe612865db1a7d157d13a056d
  a108669c47ee7d19ef4037df2a82a6cc62b3ee99

v0.26.1 unavailable-run record
  de53dac3b59a34ae1a56a5e4b5dd967cce5a1ff9

v0.26.2 implementation
  94e04366197b713a7cfa2800b3bf9223f2c6b38f

v0.26.2 registration commit
  8e3f9e39ee612894ac53a8700d45005335346d96

v0.26.2 registration SHA-256
  74f98fa33d8dccdaf1f2b9955a61b9e51c25d64fbc425ad831f1685b06f2376c

v0.26.2 result SHA-256
  55700d9b0a17567a195d94cc45e61a874b1f4840b15c9ba9bfdf6810efe9689f

v0.26.2 independent verification SHA-256
  b6656b20e4317587f1ed047e4a03d21fbfbf806d48feb20c00bf255aa307a9b5
```

The v0.26.2 registration sealed eighteen files, including the complete v0.26
science, the v0.26 failure record, and the v0.26.1 registration and crash
record. All eight adjudication gates and all fifteen independent checks
passed.

## Next load-bearing sequence

### A. Heterogeneous-link obstruction and positive boundary

Allow context- or item-dependent links. Determine whether shared midpoint
alone preserves threshold localization and which gluing conditions are
necessary for one utility vector. Construct the smallest explicit
counterexample when midpoints drift.

### B. Environment realization theorem

Replace the abstract cardinal offset primitive with a registered finite-MDP
environment intervention. Prove when the intervention adds a known reward
amount to one anchored alternative without changing transition, policy, or
context semantics.

### C. Sharp noisy-query complexity

Under a frozen margin envelope, derive matching adaptive lower bounds and
compare repeated-midpoint bisection with sequential tests that allocate
samples near the root.

### D. Coherent-object frontier

Extend the graph-Hodge and context-gluing tests to a demonstrator class with
dependence, contamination, or non-expected-utility choice. State a total
three-way decision: coherent quotient, incoherent witness, or unavailable
under insufficient access.

## Epistemic boundary

Version v0.26.2 establishes an exact access boundary for one deliberately
strong intervention. It does not validate that humans or models respond
according to the assumed link class, that the offset exists in practical
preference elicitation, that more access improves a held-out decision, or
that ASMP-9 is resolved.
