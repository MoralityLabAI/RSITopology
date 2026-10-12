# ASMP-9 resolution audit after v0.21

## Verdict

ASMP-9 remains unresolved.

Version v0.21 classifies exact value computation at the positive-count,
maximally noisy boundary inside the irreducible biconnected block isolated by
v0.20.  It does not solve above-floor design, behavioral misspecification, or
the broader intervention problem.

## New milestone

For a finite simple biconnected comparison block at

```text
epsilon = 1/2
N = |E|
n_e >= 1,
```

the positive allocation is unique and

```text
F_G = T_G(0,2) / 2^|E|.
```

The numerator problem is #P-complete and exact rational value computation is
#P-hard under polynomial-time Turing reductions.  The hardness localizes to
biconnected blocks by the classical bridge test and block product.

The registered run passed 10/10 gates; its import-independent verifier passed
11/11 checks.

## Status against the five ASMP-9 obligations

### 1. Maximal invariance groups

**Partially addressed in declared finite models; not closed generally.**

Versions v0.1-v0.13 characterize several additive, affine,
potential-shaping, discounted, contextual, and conditional quotients.
Version v0.21 assumes the established conditional scalar-gradient quotient
and adds no broader maximal-invariance theorem.

### 2. Necessary and sufficient query/environment interventions

**Sharp for several finite known interfaces; open generally.**

The finite comparison-graph liveness criterion and its biconnected
factorization are exact.  Version v0.21 classifies the difficulty of
evaluating one boundary of that object; it does not classify arbitrary
preference queries, transition interventions, history-dependent access,
unknown environments, or policy-only observation.

### 3. Sharp query, sample, and intervention-order bounds

**The count-floor local value is classified; above-floor and adaptive design
remain open.**

The program now has:

- sharp direct-access comparison width;
- finite-sample known-channel bounds;
- exact single-cycle finite design;
- a general-graph asymptotic cut exponent;
- exact cactus and between-block allocation;
- exact arbitrary-block factorization; and
- a #P-hardness classification for exact value computation at
  `epsilon=1/2`, `N=|E|` inside one biconnected block.

Still missing are the complexity of weighted ternary availability away from
that boundary, the above-floor maximin optimizer, approximation guarantees,
the complete parameterized landscape, and adaptive allocation.

### 4. Robustness to behavioral misspecification

**Open.**

Version v0.21 uses independent Bernoulli trials, a known response interior,
positive fixed counts, and a coherent scalar nuisance.  It does not cover
dependence, drift, contamination, strategy, unknown links, or
non-expected-utility demonstrators.

### 5. No-go theorem without a coherent latent value object

**Only finite special cases exist.**

The context-gluing, unknown-link, deterministic-policy, and
conditional-fiber results give explicit obstructions.  They do not classify
all demonstrator laws lacking a stable scalar or quotient value object.

## Evidence audit

```text
development implementation
  ca7ca070dc614ea5f38a364b2df100cdf3c839fb

protocol/source freeze
  c7672b74024004a28601433de35b4d1f678553b4

registration commit
  e45d2b9f844e0275442770d182fc17c0efea7ef1

registration SHA-256
  6e79a421c1551e07d44fdaadff5a4967f2cf92371ac0434ce2460ae001aad6c1

result SHA-256
  b92f7b68547cbd84a7629ea270bd789a4b01087a70f62f43f94c08e3a43336aa

independent verification SHA-256
  dbe651faeebf53cc9a421fa405882ae1bd3c535d0d08678b95098660d212d680
```

Development checked all 1,024 simple labelled graphs on five vertices plus
named burned blocks.  The prospective run used six fresh full graphs, passed
all exact identities and controls, and stayed under its CPU/RAM caps.

## Analytic versus finite evidence

Analytic and prior-art-derived:

- the count-floor reduction from ASMP statuses to total orientations;
- the identity with `T_G(0,2)`;
- #P membership and Jaeger-Vertigan-Welsh hardness;
- normalization recovery for exact rational value; and
- biconnected-oracle localization.

Prospectively verified finite evidence:

- exact agreement on four fresh biconnected blocks;
- endpoint-label invariance;
- unique positive allocation at the count floor;
- the bridge scope distinction; and
- the two-block product.

The finite evidence tests the translation and code.  It is not proof of the
classical complexity theorem.

## Next load-bearing sequence

### A. Classify the above-floor weighted local block

Either prove #P-hardness for fixed rational `epsilon<1/2`, derive an exact
fixed-parameter algorithm for weighted ternary availability, or do both.
Then classify the maximin integer allocation for `N>|E|`.

### B. Adaptive allocation

Freeze a sequential policy class, charge every observation used for edge
selection, and compare worst-case stopping time or fixed-budget availability
against the best nonadaptive design.

### C. Dependence and contamination

Replace independence by a registered exchangeable, martingale, or
contamination class.  Deterministic block liveness should survive; product
probabilities generally will not.

### D. Behavioral bridge

Test whether the scalar quotient exists before asking whether additional
certified access improves a held-out decision target.

## Epistemic boundary

Version v0.21 gives a real complexity barrier for one exact finite access
boundary.  It does not show that human or model preferences obey the response
model, that more comparisons improve decisions, that above-floor allocation
is intractable, or that ASMP-9 is resolved.

