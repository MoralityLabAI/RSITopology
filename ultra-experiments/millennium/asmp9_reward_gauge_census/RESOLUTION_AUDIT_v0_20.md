# ASMP-9 resolution audit after v0.20

## Verdict

ASMP-9 remains unresolved.

Version v0.20 closes the exact decomposition and between-block allocation
problem for the frozen independent-binomial conditional-access model. It
isolates, but does not solve, the exact finite-design problem inside a general
biconnected overlapping-cycle block.

## New milestone

For arbitrary finite simple comparison graphs:

```text
full residual quotient liveness
iff
every nontrivial vertex-biconnected block is residual-strongly-connected.
```

Consequently, under independent edge responses:

```text
F_G(n, labels) = product_B F_B(n_B, labels_B),
```

and the registered rectangular endpoint-label minimum factors as the product
of blockwise minima. Given exact local tables, a Bellman recursion solves the
positive integer allocation between blocks.

The registered run passed 10/10 gates; its independent verifier passed 14/14
checks.

## Status against the five ASMP-9 obligations

### 1. Maximal invariance groups

**Partially addressed in declared finite models; not closed generally.**

Versions v0.1-v0.13 characterize additive, affine, potential-shaping,
discounted gain-graph, context-gluing, scalar-gradient, and conditional
finite-sample quotients. Version v0.20 assumes the conditional scalar-gradient
quotient and adds no maximal invariance classification for broader behavioral
or history-sensitive sources.

### 2. Necessary and sufficient query/environment interventions

**Sharp for realized conditional full-rank liveness on a known finite
comparison graph; open for general interfaces.**

The combined criterion is now:

```text
full quotient available
iff every cyclic-core component is residual-strongly-connected
iff no one-way cyclic-core bond is fully boundary-saturated
iff every nontrivial biconnected block is residual-strongly-connected.
```

The last equivalence supplies exact decomposition. None of these statements
classifies arbitrary preference queries, transition interventions,
history-dependent access, unknown environments, or policy-level observation.

### 3. Sharp query, sample, and intervention-order bounds

**Exact between blocks; local arbitrary-block design and general adaptive
complexity remain open.**

The program now has:

- sharp direct-access comparison width;
- exact single-cycle finite design;
- a general-graph asymptotic exponent via cyclic-core cuts;
- exact finite cactus design;
- exact factorization over arbitrary biconnected blocks; and
- exact Bellman allocation between those blocks.

The remaining finite nonadaptive combinatorial problem is precisely the local
maximin availability design inside one biconnected block with overlapping
cycles. There is no polynomial algorithm, fixed-parameter result,
approximation guarantee, or hardness reduction for that frozen objective.
Adaptive allocation and dependent-sample bounds are also open.

### 4. Robustness to behavioral misspecification

**Open.**

Version v0.20 assumes independent Bernoulli trials, fixed positive counts, a
known symmetric probability interior, a rectangular edge-label adversary, and
a coherent scalar nuisance. It does not cover exchangeable dependence,
martingale drift, contamination, strategic response, nonstationarity,
unknown links, or non-expected-utility demonstrators.

### 5. No-go theorem without a coherent latent value object

**Only finite special cases exist.**

The context-gluing, unknown-link, deterministic-policy, and conditional-fiber
results give explicit obstructions. They do not classify demonstrator laws
for which no stable scalar or quotient value object exists.

## Evidence audit

```text
development commit
  d7a235ed6dcd8f141dada5d7432c3603758199f3

implementation freeze
  21da5b7aa04aa5f8ad1e70da0aff8da3f69b2bb0

registration commit
  8487edad48ba302cbf3d71192df593f2480842ca

registration SHA-256
  a26ef3900087416df5ba92e5c85fd23006ea35f3677ebeb98f5f2cb4fd7ede60

result SHA-256
  bd626d1ad1da1299ff05fd0be415acdffd264b561278a941e094982f8ad9394c
```

Burned development evidence checked 735,021 ternary states with zero
mismatches. The prospective run used disjoint full graphs, checked 262,440
additional states, passed exact probability/minimum/design gates, and remained
well inside its CPU/RAM cap.

The independent verifier imports neither the implementation module nor the
runner and reproduced every substantive result.

## Analytic versus finite evidence

Analytic:

- the block-excursion lemma;
- deterministic liveness equivalence;
- probability and rectangular-minimum factorization;
- exact Bellman allocation between blocks; and
- the fact that a one-block graph receives no computational decomposition.

Prospectively verified finite evidence:

- independent block partitions on six fresh graphs;
- four-way equivalence over 262,440 fresh ternary states;
- exact rational fixed-label and worst-label products;
- bridge-status/count/label irrelevance;
- Bellman/full-allocation optimizer equality; and
- the binding one-block control.

The finite evidence challenges the proof and implementation. It is not the
proof of the analytic theorem.

## Next load-bearing sequence

### A. Classify the local biconnected-block problem

The next theorem should be either:

1. an exact fixed-parameter algorithm in cycle rank, treewidth, branchwidth,
   or another frozen graph parameter; or
2. a hardness reduction for the exact maximin finite-budget objective.

Any algorithm must retain a direct exhaustive verifier on small blocks.

### B. Adaptive allocation

Freeze a sequential policy class, charge every observation used for edge
selection, and compare worst-case stopping time or fixed-budget availability
against the best nonadaptive design.

### C. Dependence and contamination

Replace edge independence by a registered exchangeable, martingale, or
contamination class. The deterministic block theorem should survive; the
product probability and Bellman objective generally will not.

### D. Behavioral bridge

Only after A-C should the program claim decision relevance. First test whether
the scalar quotient exists, then ask whether additional certified access
improves a held-out decision target.

## Epistemic boundary

Version v0.20 identifies the exact irreducible graph blocks of the frozen
finite access-design problem. It does not establish that human or model
preferences obey the response model, that added comparisons improve decisions,
that the local arbitrary-block problem is tractable, or that ASMP-9 is
resolved.
