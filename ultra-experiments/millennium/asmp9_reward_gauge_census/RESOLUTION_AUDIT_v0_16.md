# ASMP-9 resolution audit after v0.16.2

## Verdict

ASMP-9 remains unresolved.

Version v0.16.2 closes the fixed-total integer allocation question left open
by v0.15, but only for one independent Bernoulli experiment on one oriented
cycle with a known symmetric probability interior.

The full problem still asks for necessary and sufficient access conditions
across declared reward classes, response models, query interfaces, and
environment interventions, with robust recovery and matching lower bounds.

## The milestone that is now closed

The v0.15 resolution audit identified this next theorem target:

> Prove or refute that positive integer trial counts differing by at most one
> maximize worst-case informative-fiber availability over endpoint
> probabilities for every cycle length, interior, and fixed total budget.

Version v0.16 proves that statement for:

```text
k >= 3,
0 < epsilon <= 1/2,
n_i positive integers,
sum_i n_i = N,
independent Bernoulli trials,
p_i in [epsilon,1-epsilon].
```

The balanced allocation is the unique maximizer up to edge permutation. The
proof is analytic: every Robin-Hood transfer strictly increases the
worst-endpoint informative-fiber probability. The fresh census verifies
registered instances of the pair identities and global consequence; it is
not the basis of the theorem.

The exact compact optimum and total-budget threshold are now:

```text
F_star(k,N,epsilon)
  = exact worst-endpoint availability of the balanced allocation

N_star(k,epsilon,delta)
  = min {N>=k : F_star(k,N,epsilon) >= 1-delta}.
```

Thus the equal-count theorem in v0.15 and the fixed-total allocation theorem
in v0.16 together give a sharp availability design for this single-cycle
experiment.

## Status against the frozen ASMP-9 obligations

### 1. Maximal invariance groups

**Partially addressed in finite declared models, not closed generally.**

Earlier versions characterize additive, positive-affine,
potential-shaping, discounted gain-graph, context-gluing, and conditional
scalar-gradient quotients. Version v0.16 assumes the v0.13 conditional
quotient and adds no general maximal-invariance theorem.

### 2. Necessary and sufficient query/environment interventions

**Sharp for one fixed cycle experiment, open for general interfaces.**

Within the frozen cycle model, v0.16 gives the exact fixed-total allocation
and necessary and sufficient availability threshold. It does not characterize
general comparison graphs, adaptive query policies, transition
interventions, multiple environments, or history-dependent access.

### 3. Sharp query, sample, and intervention-order bounds

**The fixed-total single-cycle availability subproblem is closed. The general
obligation is not.**

The v0.15 equal-count threshold and v0.16 balanced-allocation theorem are
sharp, including boundary failures at zero interior and at cycle length two.
They do not give minimax downstream testing power, adaptive-allocation
bounds, dependent-sample bounds, or graph-wide allocation laws.

### 4. Robustness to behavioral misspecification

**Open.**

The theorem assumes independent Bernoulli comparisons and a known symmetric
probability interior. Dependence, unknown or drifting links, asymmetric
response classes, strategic demonstrators, and non-expected-utility behavior
are outside the result.

Earlier versions prove several finite obstructions, which shows this
obligation cannot be treated as routine perturbation analysis.

### 5. No-go theorem when no coherent latent value object exists

**Only finite special cases exist.**

The contextual-gluing, unknown-link, deterministic-policy, and
conditional-fiber witnesses expose specific nonidentifiability and
noncoherence mechanisms. They do not characterize the full class of
demonstrators for which no stable scalar or quotient value object exists.

## What the two registered resource aborts mean

The v0.16 and v0.16.1 runs both exceeded the same frozen wall-time cap before
scientific gate evaluation. They are not failed scientific replications.

Version v0.16.2 preserved the theorem, gates, and cap, froze a third disjoint
registry, and replaced the linear threshold scan with exact exponential
bracketing and binary search. Its pass establishes that the registered
verification is executable inside the original resource envelope. It does
not erase or reinterpret the earlier aborts.

## Next load-bearing milestone

The next theorem target is no longer single-cycle integer balancing. It is:

> Characterize maximin trial allocation on a general comparison graph whose
> conditional quotient has multiple independent cycle directions, including
> when balanced edge counts cease to be optimal and which graph or matroid
> object replaces them.

A useful positive result would provide:

1. a graph-wide objective that reduces to `F_star` on one cycle;
2. necessary and sufficient optimality conditions or a certified
   approximation ratio;
3. matching counterexamples to naive uniform allocation;
4. an adaptive-versus-nonadaptive access comparison; and
5. sensitivity to dependent or misspecified response laws.

This is load-bearing because real preference and rollout designs contain
overlapping cycles. A theorem confined to one cycle does not determine how
evidence should be allocated when comparisons jointly support several
quotient directions.

## Epistemic boundary

Version v0.16.2 is a prospectively registered exact theorem verification with
an independent clean replay. It is not evidence that human values are
coherent, that language-model preferences follow Bradley-Terry, that general
reward gauges are identified, or that recursive self-improvement can be
safely evaluated from preference comparisons.
