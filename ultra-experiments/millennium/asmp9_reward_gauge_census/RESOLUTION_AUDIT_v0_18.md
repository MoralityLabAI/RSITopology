# ASMP-9 resolution audit after v0.18

## Verdict

ASMP-9 remains unresolved.

Version v0.18 closes the structural identity of the general-graph failure
supports in the v0.17 independent-binomial conditional-access model. It does
not close the full value-identifiability problem over reward classes,
behavioral response models, query interfaces, and environment interventions.

## Milestone closed by v0.18

Version v0.17 left the allocation exponent in terms of an abstract family
`B_G` of inclusion-minimal bad boundary supports:

```text
tau_G* = max_w min_(B in B_G) w(B).
```

Version v0.18 proves:

```text
B_G = bonds of the cyclic core.
```

Therefore:

```text
tau_G*
  = max_(w >= 0, sum w = 1)
      min_(cyclic-core cuts C) w(C)
  = 1 / nu_b*(G).
```

The optimization is the classical max-min cut design problem. The contribution
is the exact reduction from the conditional reward-gauge access ledger to that
classical object. The result replaces exponential ternary structural search
with minimum-cut separation and supplies the closed form `2/M` for cactus
cores with `M` nonbridge edges.

## Status against the ASMP-9 obligations

### 1. Maximal invariance groups

**Partially addressed in declared finite models; not closed generally.**

Versions v0.1-v0.13 characterize additive, affine, potential-shaping,
discounted gain-graph, context-gluing, scalar-gradient, and conditional
finite-sample quotients. Version v0.18 assumes the conditional
scalar-gradient quotient and adds no maximal invariance theorem for broader
reward, preference, or behavior classes.

### 2. Necessary and sufficient query/environment interventions

**Sharp for realized conditional full-rank liveness on a known finite
comparison graph; open for general interfaces.**

The combined v0.17-v0.18 criterion is:

```text
full quotient available
iff every cyclic-core component is residual-strongly-connected
iff no one-way cyclic-core bond is fully boundary-saturated.
```

This is necessary and sufficient for the declared conditional count fiber.
It does not characterize arbitrary preference queries, transition
interventions, history-dependent interfaces, unknown environments, or
policy-level observation.

### 3. Sharp query, sample, and intervention-order bounds

**The asymptotic nonadaptive graph-allocation exponent now has a classical
cut characterization. Exact finite graph design remains open generally.**

The exponent can be optimized with a minimum-cut separation oracle, and its
fractional bond-packing dual supplies exact certificates. The cactus class has
a closed form.

No theorem yet characterizes the optimal positive integer allocation for
every finite total budget on every graph. The exact finite objective is a
network-reliability design problem rather than merely the max-min cut
exponent. No adaptive allocation bound, dependent-sample bound, or minimax
downstream test-power theorem is established.

### 4. Robustness to behavioral misspecification

**Open.**

The probability and allocation conclusions assume independent Bernoulli edge
trials, fixed counts, a known symmetric probability interior, and a coherent
Bradley-Terry-type scalar nuisance. Dependence, contamination, unknown or
asymmetric links, strategic demonstrators, nonstationarity, and
non-expected-utility behavior remain outside the result.

The bond theorem itself is deterministic conditional on the realized count
statuses, but its risk exponent and allocation interpretation are not robust
to arbitrary changes in the response law.

### 5. No-go theorem without a coherent latent value object

**Only finite special cases exist.**

The contextual-gluing, unknown-link, deterministic-policy, and
conditional-fiber results provide explicit obstructions and unavailable
states. They do not classify all demonstrator laws for which no stable scalar
or quotient value object exists.

## Evidence audit

The v0.18 implementation and protocol were frozen before the replacement
scientific registry was evaluated:

- implementation freeze:
  `e063a7707b3203e21442c4a77330f72596260a57`;
- registration commit:
  `c72ff1db597c22a56f1a1e13488967fdd116d30e`;
- registration SHA-256:
  `696d7e46c385e3614e99f2da87cacf77bfb3a741c596ac5d4687ca59f8854d0a`.

The initially proposed registry was exercised by a pre-freeze unit test. It
was explicitly burned, preserved in the development registry, and replaced
before the implementation freeze. No claim uses those premature cells.

The registered run then checked four fresh graphs:

- 1,299,078 residual status vectors;
- 170 cyclic-core bonds;
- four exact rational primal/dual design certificates;
- one fresh cactus closed-form cell; and
- graph-isomorphism freshness against every declared inherited and
  development graph.

All eight registered gates passed. The separately sealed verifier passed all
eight checks, including all registration hashes, an independent
cut-minimization reconstruction of every bond family, and all rational
certificate arithmetic.

The run used no GPU, finished in approximately 110.21 seconds, and remained
well below the one-GiB memory cap.

A clean detached replay from the result commit passed the same verifier,
reproduced the full scientific payload, and emitted a byte-identical report.
The only JSON differences were the expected execution-commit and resource/time
telemetry fields.

## What is analytic versus finite evidence

Analytic:

- componentwise strong-connectivity equivalence;
- minimal bad supports are cyclic-core bonds;
- max-min cut and fractional bond-packing formulations;
- cactus threshold `2/M` and unique uniform cyclic-edge optimum.

Prospectively verified finite evidence:

- exact SCC-versus-bond equality on four fresh graphs;
- 1,299,078 direct residual states with no mismatch;
- exact primal/dual certificates at `1/5` and `1/4`;
- bridge exclusion and cactus closed form.

The finite census verifies the implementation and challenges the statement on
fresh objects. It is not the proof of the general analytic theorem.

## Next load-bearing sequence

### A. Exact finite-budget graph design

Classify the positive-integer allocation problem for the exact finite
availability objective. Determine whether general optimization is
polynomial, fixed-parameter tractable, approximable with a certified ratio, or
hard. Keep the max-min cut exponent separate from the finite reliability
objective.

### B. Adaptive allocation

Freeze a sequential policy class that chooses the next comparison edge from
observed counts. Compare its worst-case stopping time or budget with the best
nonadaptive design, charging every selection observation.

### C. Response dependence and contamination

Replace independent edge trials with a registered exchangeable, martingale,
or contamination class. Determine which deterministic bond statements remain
valid and which availability/exponent conclusions fail.

### D. Behavioral bridge

Only after A-C should the program attempt a preference or policy-learning
bridge. It must first test whether the coherent quotient value object exists
and then show that additional certified access improves a held-out decision
target.

## Epistemic boundary

Version v0.18 materially sharpens the access-design component of ASMP-9:
the residual failure object is now a standard, auditable graph invariant
rather than an enumerated hypergraph. It does not show that human or model
preferences are coherent, that the frozen response model is behaviorally
valid, that the comparisons improve downstream decisions, or that ASMP-9 is
resolved.
