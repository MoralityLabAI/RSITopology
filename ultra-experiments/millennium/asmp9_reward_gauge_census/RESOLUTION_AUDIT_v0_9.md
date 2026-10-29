# ASMP-9 resolution audit after v0.9

Date: 2026-07-28

## Verdict

**ASMP-9 is not resolved.**

The [v0.8 audit](RESOLUTION_AUDIT_v0_8.md) remains the complete
requirement-by-requirement baseline. Version v0.9 changes one row materially:
finite samples can now certify a declared near-coherent Bradley-Terry edge
flow with simultaneous error control, certify a separated circulation
alternative, or stop inconclusive. That does not supply the general
reward-identification classification required by ASMP-9.

## New evidence

| Layer | Authoritative evidence | What is proved | Resolution status |
|---|---|---|---|
| Finite-sample scalar coherence | [v0.9 public summary](finite_sample_coherence_v0_9/PUBLIC_SUMMARY_v0_9.md) | A Bonferroni-Hoeffding probability event propagates through a registered logit interior to simultaneous fundamental-cycle bands. The resulting total decision has coherent, incoherent, inconclusive, and unavailable states, with a graph-dependent sufficient sample bound. | Complete only for independent fixed-count Bernoulli comparisons, a known logit link, and the declared tolerance regions. |

## Effect on the five obligations

### 1. Maximal invariance groups

Unchanged from v0.8: **partial**. Version v0.9 estimates one already-declared
Bradley-Terry gradient object; it does not enlarge the invariance
classification.

### 2. Necessary and sufficient access

Still **partial**. The cycle rank remains the exact structural access
criterion for population coherence, and v0.9 proves that `beta_1=0` makes the
finite-sample coherence instrument unavailable. The sample bound is
sufficient, not necessary, and adaptive allocation is open.

### 3. Sharp query, sample, and intervention-order bounds

Improved but still **partial**. Version v0.9 supplies the first finite-sample
behavioral coherence bound in the suite:

```text
n = O(k_max^2 log(m/alpha)/margin^2)
```

with explicit probability-interior factors. The bound is conservative and no
matching lower bound is proved. Unknown links, dependence, sequential
demonstrations, and general-MDP intervention order remain open.

### 4. Behavioral misspecification robustness

Still **not established at resolution scope**. The procedure can stop when
the probability interior is unsupported and can certify a circulation
alternative. It does not give downstream reward-error guarantees under a
misspecified response law.

### 5. No-go classification

Unchanged in scope, but operationally strengthened. Finite data no longer
silently turns a non-rejection into a scalar-existence claim. The broader
contextual, dependent, history-sensitive, and non-expected-utility no-go
classification remains open.

## Highest-value remaining sequence

### v0.10: general finite-MDP intervention access

Freeze a finite tabular MDP family and compute the remaining reward quotient
under:

- one deterministic optimal policy;
- stochastic policy probabilities;
- multiple transition kernels;
- multiple discount factors; and
- trajectory preferences.

The result should report an exact rank or polyhedral dimension and a matching
indistinguishability witness, explicitly below existing general
identifiability theory.

### v0.11: contextual/history-sensitive no-go

Construct a response family in which each context separately admits a scalar,
no shared scalar exists, and a context-indexed preference kernel does. Prove a
sharp access threshold separating the shared-scalar and context-indexed
hypotheses.

### Later statistical closure

A future successor may seek:

- minimax lower bounds matching v0.9;
- adaptive edge allocation;
- confidence regions under an estimated or normalized unknown link; and
- dependent-response concentration.

Those are not prerequisites for starting v0.10, but they remain prerequisites
for a broad ASMP-9 resolution.

## Completion criterion

Current results still cover separate specialized observation grammars rather
than one broad frozen family. A defensible resolution requires maximal
source-specific invariances, matched upper and lower access bounds, a
finite-sample misspecification theorem, and a two-sided
scalar-existence/no-go classification over a materially richer family.
