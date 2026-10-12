# ASMP-9 resolution audit after v0.31

## Verdict

**ASMP-9 remains unresolved.**

Version v0.31 closes the first item in the v0.30 load-bearing sequence under
declared deterministic widths:

```text
exact context nuisance
  -> project out at zero error cost;

bounded mechanical, localization, residual-midpoint, and semantic sources
  -> one joint outer zonotope when the mechanical gain is below one;

outer zonotope + finite policy occupancies
  -> exact directional identity and regret calculation over that set.
```

At gain one, an admissible scalar mechanical perturbation erases the entire
measurement channel. Shared semantic-cell incidence and anisotropic policy
directions both produce strict improvements over independent scalar error
aggregation.

## Status against the five obligations

### 1. Maximal invariance groups

**Partially addressed in declared finite linear models; open generally.**

The program distinguishes potential shaping, positive scale, response-link
shape, midpoint drift, component gauge, observation kernel, decision-null
gauge, and semantic consequence calibration. Version v0.31 begins after a
decision-null quotient has been declared; it does not prove that quotient is
maximal.

The maximal invariance group for history-dependent rewards, nonlinear
representations, strategic demonstrators, non-expected-utility preferences,
and coarser behavioral equivalences remains open.

### 2. Necessary and sufficient access conditions

**Sharp for the registered projected linear access model; open under
behavioral and coarser environment access.**

For exact context-only nuisance, v0.31 proves the necessary-and-sufficient
condition

```text
rank(PA) = dim(theta).
```

If it fails, a reward direction is confounded with the context nuisance. If
it holds, the registered analysis map satisfies `LA=I` and `LC=0`.

For the declared norm-only mechanical uncertainty class, `lambda<1` is a
sufficient finite-certificate condition and the scalar `lambda=1` erasure
witness proves the boundary is live for the class. This is not a complete
classification of structured mechanical perturbations.

The scalar observations and all source widths are still assumed available.
They are not derived from ordinary preference comparisons.

### 3. Sharp query, sample, and intervention-order bounds

**Several exact finite bounds are sharp; stochastic acquisition complexity
remains incomplete.**

Earlier versions establish sharp population widths, finite noisy-channel
bounds, graph-allocation results, calibrated-occupancy rank conditions, and
finite-policy margin rules.

Version v0.31 adds exact support computation for the registered outer
zonotope and explicit attaining vertices. It does not give the sample
complexity of estimating localization, semantic, midpoint, or mechanical
widths from dependent behavioral data.

### 4. Robustness to behavioral misspecification

**Joint deterministic composition is now addressed; stochastic and model
misspecification remain open.**

Version v0.31 combines:

- rowwise mechanical occupancy drift;
- threshold-localization error;
- residual midpoint drift;
- exactly projected context-only drift; and
- shared-cell semantic-calibration error.

The theorem gives a finite reward bound when `lambda<1`, preserves the full
zonotope, and propagates its support function into policy identity and regret.
The primary planted realization was covered in seven directions, and every
source class was necessary in a dedicated ablation.

This closes the v0.30 item called **joint approximate factorization**, but
only conditional on registered deterministic source widths. It does not
cover uncertain response-link shape, dependent sampling, strategic
reporting, learned occupancy error, or distributional ambiguity in one
minimax statement.

### 5. No-go theorem without a coherent latent value object

**The no-go branch is stronger but incomplete.**

Earlier versions show that unknown monotone links can preserve non-affine
utility ambiguity, context-only nuisance can confound reward directions,
mechanics cannot create a semantic unit, and deterministic policies can be
nonidentifying.

Version v0.31 adds two local impossibility witnesses:

- if the projected design loses rank, reward and context nuisance are
  observationally confounded; and
- at mechanical gain one, an admissible perturbation can erase the
  measurement channel.

These do not classify every inconsistent or non-scalar demonstrator law.

## Evidence

```text
original implementation commit
  896904058fd80a0343f2c0ef4ee736f0edd2738c

original registration commit
  7af9a09a9db9677aea542aea5e1e4d6f015a5611

original registration SHA-256
  4a3d57e5c71335d157fe3e1bd65a4f0b184515dc3be06a143bcca3f019b81379

repair implementation commit
  c50659e9c21b9c34783d2f89ec7757a4aef94f97

repair registration/run commit
  50593abf361afcf867f753b2039261a01434725c

repair registration SHA-256
  d9c044c9b477478a54b55c79d2111d1efca4b7ee2932190dbe718259ef54310c

result SHA-256
  f07ee0b7ef11339f97b2862987495a9d4088e44f55b58c7d708ba9ee0d578e94

run-receipt SHA-256
  f73b10d3e9e06196c230400b77feab8f13f6b4e4640c0d8a6f4cf5fe51d83918

independent-verification SHA-256
  618373a9a5430aa74fc88512be1c5733cc3b9ed4f6d275bf78c3f856aecbde84

repair-verification SHA-256
  3612669c29965fd8ade4288d48c1aa5acc220408d6bd204fbca27a1287a8e235
```

The separately registered repaired execution passed twelve of twelve
scientific gates, twenty-nine of twenty-nine independent scientific checks,
and ten of ten repair-integrity checks.

## Remaining load-bearing sequence

### A. Behavioral acquisition of the semantic rectangle

Freeze a response model or additive-conjoint access grammar under which the
scalar consequence increments and their source widths can be estimated or
falsified. Derive matching indistinguishability results when the qualitative
measurement axioms fail.

### B. Sharp stochastic policy complexity

Combine response margins, graph and quotient spectral floors, adaptive
allocation, occupancy estimation, shared semantic cells, and policy margins
in one minimax theorem.

### C. Coarser environment equivalence

Replace exact registered occupancy rows with a declared MDP homomorphism,
bisimulation, simulation metric, or occupancy-equivalence class. Determine
when consequence interventions preserve the downstream query despite changes
to the raw MDP.

### D. General misspecification and no-go classification

Characterize which non-scalar, context-dependent, history-dependent, or
strategic demonstrator laws admit any coherent quotient-valued object, and
give indistinguishability lower bounds when they do not.

## Epistemic boundary

Version v0.31 proves how four declared deterministic uncertainty sources
compose after exact context projection and how the resulting set controls a
finite policy decision. It does not show that those source bounds can be
obtained from humans or models, that the latent value object is coherent, or
that ASMP-9 is resolved.
