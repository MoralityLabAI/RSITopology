# ASMP-9 resolution audit after v0.19.2

## Verdict

ASMP-9 remains unresolved.

Version 0.19.2 closes exact finite-budget maximin allocation for cactus cyclic
cores in the frozen independent-binomial conditional-access model. It does
not close the full value-identifiability problem over reward classes,
behavioral response models, query interfaces, and environment interventions.

## Milestone closed by v0.19.2

Version 0.18 reduced the large-budget allocation exponent to max-min cut
design and gave a uniform closed form for cactus cyclic cores. It explicitly
left exact finite budgets open.

For cactus cyclic cores, v0.19.2 proves:

```text
F_G(n) = product_j F_Cj(n restricted to C_j),
```

then combines the exact one-cycle balance theorem with:

```text
D_j(b)
  = max_(k_j <= t <= b)
      D_(j-1)(b-t) f_(k_j)(t).
```

Thus the exact finite allocation is pseudo-polynomially computable, every
bridge remains at its positive-count floor, every cycle is internally
balanced, and the remaining budget is allocated among cycle blocks by a
classical Bellman recursion.

The result also proves that neither maximum-one-step marginal allocation nor
the asymptotically uniform edge design is exact at every finite budget.

## Status against the ASMP-9 obligations

### 1. Maximal invariance groups

**Partially addressed in declared finite models; not closed generally.**

Versions v0.1-v0.13 characterize several additive, affine, potential-shaping,
discounted gain-graph, context-gluing, scalar-gradient, and conditional
finite-sample quotients. Version v0.19.2 assumes the conditional
scalar-gradient quotient and adds no maximal invariance theorem for broader
reward, preference, or behavior classes.

### 2. Necessary and sufficient query/environment interventions

**Sharp for realized conditional full-rank liveness on a known finite
comparison graph; open for general interfaces.**

The combined v0.17-v0.18 criterion remains:

```text
full quotient available
iff every cyclic-core component is residual-strongly-connected
iff no one-way cyclic-core bond is fully boundary-saturated.
```

Version v0.19.2 gives an exact finite design algorithm when the cyclic core is
a cactus. It does not characterize arbitrary preference queries, transition
interventions, history-dependent interfaces, unknown environments, or
policy-level observation.

### 3. Sharp query, sample, and intervention-order bounds

**Exact for one nonadaptive cactus subclass; still open generally.**

The program now contains:

- a sharp asymptotic general-graph exponent characterized by cyclic-core cuts;
- a cactus closed form for that exponent; and
- an exact finite-budget cactus algorithm with complete optimizer recovery.

The exact finite objective for arbitrary cyclic cores is still open. No
complexity classification, approximation guarantee, fixed-parameter result,
or hardness theorem is established for that general network-reliability
design problem. Adaptive comparison allocation and dependent-sample bounds
also remain open.

### 4. Robustness to behavioral misspecification

**Open.**

The finite-allocation theorem assumes independent Bernoulli trials, fixed
counts, a known symmetric probability interior, and a coherent
Bradley-Terry-type scalar nuisance. Dependence, contamination, unknown or
asymmetric links, strategic demonstrators, nonstationarity, and
non-expected-utility behavior remain outside the result.

### 5. No-go theorem without a coherent latent value object

**Only finite special cases exist.**

Contextual gluing, unknown-link, deterministic-policy, and conditional-fiber
results provide explicit obstructions. They do not classify all demonstrator
laws for which no stable scalar or quotient value object exists.

## Evidence audit

The v0.19.2 implementation and protocol were frozen before its fresh cells
were evaluated:

- implementation freeze:
  `da0734da7d5a8c6f89f98b64cd7f0fed9df0ba42`;
- registration commit:
  `4667857250855cf0e11254846e997c07e8e12826`;
- registration SHA-256:
  `7328118a2b76aa0cb8f79c369f5deaaf61bd0663ab9ab35877f4b0ff94089298`.

The two previous executions remain in the record:

- v0.19: eight mathematical gates passed, but `261.413 > 180` seconds;
- v0.19.1: nine mathematical gates passed and independent replay passed, but
  `431.872 > 180` seconds.

Neither result was promoted. Every one of their cells was burned.

The post-outcome v0.19.1 profile identified duplicated exact local
enumerations as the bottleneck. The v0.19.2 implementation removed only that
duplication, preserved exhaustive independent checking, and registered
larger fresh structural cells.

The v0.19.2 run passed all ten gates in `50.568574` seconds with
`24,293,376` bytes peak resident memory and no GPU. Its independent verifier
passed all eleven checks, including:

- all sealed hashes;
- the total positive/negative gate-to-verdict mapping;
- reproduction of the three burned v0.19.1 DP values and optimizer sets;
- direct factorization and bridge checks;
- Bellman versus independent exhaustive equality on every fresh cell;
- the full positive edge census; and
- both exact counterexamples and all comparator classifications.

## What is analytic versus finite evidence

Analytic:

- cactus liveness factorizes over edge-disjoint cycle blocks;
- bridges are irrelevant to liveness and stay at their positive-count floor;
- the v0.16 cycle-balance theorem reduces the global problem to cycle totals;
- Bellman recursion is exact;
- greedy marginal allocation can fail because discrete log-concavity fails;
  and
- the asymptotically uniform design need not be finite-budget optimal.

Prospectively verified finite evidence:

- direct residual-state factorization on fresh cactus cells;
- complete independent endpoint-label and cycle-total enumeration;
- three fresh Bellman optimizer sets;
- a fresh 330-allocation all-edge census; and
- exact reproduction of the two counterexamples.

The finite evidence tests the implementation and challenges the statements on
fresh objects. It is not the proof of the general analytic theorem.

## Next load-bearing sequence

### A. Arbitrary cyclic-core finite design

Classify the exact finite positive-integer allocation problem beyond cactus
cores. Determine whether the general objective is polynomial, fixed-parameter
tractable in cycle rank or treewidth, approximable with a certified ratio, or
hard. A useful next object is a block decomposition in which cactus blocks
are solved exactly and genuinely overlapping cycle blocks are isolated.

### B. Adaptive allocation

Freeze a sequential policy class that chooses the next comparison edge from
observed counts. Compare its worst-case stopping time or budget with the best
nonadaptive design, charging every selection observation.

### C. Response dependence and contamination

Replace independent edge trials with a registered exchangeable, martingale,
or contamination class. Determine which deterministic bond statements remain
valid and which availability and allocation conclusions fail.

### D. Behavioral bridge

Only after A-C should the program attempt preference or policy learning. It
must first test whether the coherent quotient value object exists and then
show that additional certified access improves a held-out decision target.

## Epistemic boundary

Version v0.19.2 closes a real exact-design subclass and repairs two
resource-gated negative attempts without changing their outcomes. It does not
show that human or model preferences are coherent, that the frozen response
model is behaviorally valid, that comparisons improve downstream decisions,
or that ASMP-9 is resolved.
