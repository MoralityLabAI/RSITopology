# ASMP-9 resolution synthesis after v0.78

Status: **evidence audit and program stop rule; no new theorem claim**.

## Bottom line

**ASMP-9 remains unresolved.**

The recent theorem stack now closes a coherent finite declared class, corrects
two ambiguities in the problem statement, and establishes one general
computational obstruction. It does not supply the behavioral evidence needed
to license the target, gauge, or observation law in a human or model.

Further abstract finite examples are no longer the load-bearing next step.

## Corrected problem statement

The original target:

```text
observation equality iff rewards differ by the maximal invariance group
```

compresses three distinct objects:

1. a **decision target** `T`, fixed by the downstream use;
2. a **licensed transformation grammar**, derived from transformations that
   preserve that target; and
3. an **observation interface** `O`, induced by physically available queries
   and interventions.

The corrected questions are:

```text
target recovery:
    O(x)=O(x') -> T(x)=T(x')

representative insensitivity:
    T(x)=T(x') -> O(x)=O(x')

exact target interface:
    both implications
```

A maximal abstract group preserving `O` always exists by permuting points
inside observation fibers. It is not thereby a physically licensed reward
gauge.

## What the finite theorem stack closes

| Component | Artifact | Exact conclusion |
|---|---|---|
| Joint linear quotient | v0.69 | `K=A^-1(N+A(G))`; representative-insensitive exact access iff `K=G` |
| Gaussian quotient complexity | v0.70-v0.70.1 | exact known-variance quotient MSE and coordinate-faithful scientific loss |
| Bounded non-Markov replacement | v0.71 | path values factor through a stationary edge reward iff they lie in the path-incidence column space; otherwise construct the minimal bounded history quotient |
| Noisy factorization liveness | v0.72 | edge identification and factorization falsifiability require different ranks; one exact Gaussian power cell |
| Open-ended history boundary | v0.73 | finite-state distinguishing bounds require a registered state bound; unrestricted finite prefixes admit delayed nonstationary continuations |
| Fiber/group correction | v0.74 | observation fibers are canonical; a maximal fiber-permutation group is tautological; licensed gauge orbits are independent |
| Decision-derived gauge | v0.75 | for all cardinal margins of a finite policy family, the maximal additive gauge is `ker(D)` |
| Recovery versus invariance | v0.76 | target sufficiency and representative insensitivity are opposite factorization directions |
| Finite stochastic access | v0.77 | known finite iid laws admit a population criterion, Hellinger recovery bound, binary Bayes calibration, and TV stress |
| Minimum-access hardness | v0.78 | arbitrary finite deterministic exact access contains Set Cover with optimum shift `+1` |

Together these resolve the algebraic identifiability question for:

```text
finite known policy occupancies;
all cardinal policy margins;
additive reward transformations;
linear measurements and known additive nuisance;
or a finite known iid law registry.
```

This is a restricted-class closure, not a full ASMP-9 resolution.

## Audit against the canonical five obligations

### 1. Maximal invariance or identifiability object

**Closed only conditionally.** The correct mathematical objects are now clear:
target fibers, licensed transformation orbits, and observation fibers.

**Missing:** evidence that a declared behavioral or moral target is the right
downstream object; evidence that proposed reward transformations preserve it
in the actual system.

### 2. Necessary and sufficient query/intervention access

**Closed for finite deterministic maps, finite known laws at population level,
and one linear nuisance class.**

**Missing:** a physically acquired response channel; continuous or open-ended
environment classes; adaptive interventions under model error.

### 3. Sharp query, sample, and intervention bounds

**Closed in several small structured cells.** Arbitrary finite exact design is
NP-hard, so no unrestricted efficient formula should be expected.

**Missing:** minimax rates for an empirically justified response family,
structured approximation algorithms, and actual acquisition cost.

### 4. Robustness to behavioral misspecification

**Partially addressed.** There is one Gaussian lack-of-fit test, one
finite-prefix no-go, one cross-cut interface taxonomy, and one iid TV stress.

**Missing:** dependence, context drift, heavy tails, contamination, strategic
responses, and uncertainty in occupancies/targets.

### 5. No-go without a coherent latent value object

**One branch addressed.** Deterministic bounded path values hand off to a
minimal history quotient; finite-prefix stabilization cannot certify a bounded
open-ended machine.

**Missing:** preference relations, stochastic choice kernels, set-valued
targets, continuous processes, and multi-agent value objects connected to
physical data.

## Program stop rule

Do not open another abstract ASMP-9 theorem version unless it does at least one
of the following:

1. consumes a physically acquired response artifact;
2. supplies a missing broad replacement-object theorem;
3. proves a sharp bound for a prospectively registered natural response class;
4. closes a cited prior-art gap that changes an obligation status; or
5. falsifies one premise of the finite-class closure.

In particular, another exact toy registry, isolated Gaussian fixture, or
restatement of partition refinement is not sufficient.

## Next evidence gate

The next admissible branch is the
[physical target-interface gate](NEXT_PHYSICAL_GATE_v0_79.md). It tests a
controlled finite-MDP demonstrator where:

- the decision target and potential-shaping gauge are known independently;
- raw behavior may leak the chosen shaping representative;
- matched non-gauge perturbations change the target;
- environment interventions are construction/holdout split; and
- v0.76-v0.77 decide recovery, leakage, and finite-sample robustness.

No claim from that branch is valid until its protocol and exact environment,
reward, query, seed, and evaluator artifacts are sealed before outcomes.

## Claim boundary

This synthesis is an audit of existing finite mathematical artifacts. It is
not evidence about humans, language models, moral truth, or real reward
learning. It does not resolve ASMP-9.
