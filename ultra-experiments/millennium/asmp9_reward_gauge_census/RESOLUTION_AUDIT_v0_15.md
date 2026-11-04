# ASMP-9 resolution audit after v0.15

## Verdict

ASMP-9 remains unresolved.

Version v0.15 closes one finite-sample obligation sharply for one declared
experiment: equal-count comparisons on a known oriented cycle, under
independence, a known Bernoulli response parameterization, and a declared
probability interior.

It does not close the full problem's model, intervention, robustness, or
well-posedness quantifiers.

## What v0.15 adds

Versions v0.13 and v0.14 established a separation:

1. conditioning on vertex win balance removes the scalar-gradient nuisance
   exactly;
2. conditional exactness need not imply useful unconditional power; and
3. an unbounded nuisance can make informative fibers arbitrarily rare.

Version v0.15 gives the sharp compact-interior complement. It proves:

```text
min over p in [epsilon,1-epsilon]^k P(informative fiber)
  = x^floor(k/2) y^ceil(k/2)
    + y^floor(k/2) x^ceil(k/2)
    - z^k,
```

with the notation in `THEOREM_v0_15.md`. This yields an exact necessary and
sufficient equal-count trial threshold for any declared availability target.

The result improves v0.14 in two ways:

- the lower bound is sharp; and
- the true bounded-interior adversary is the most even split of low and high
  endpoint probabilities, not the one-low drift used to demonstrate the
  unbounded collapse.

## Status against the frozen ASMP-9 obligations

### 1. Maximal invariance groups

**Partially addressed in finite declared models, not closed generally.**

Earlier versions characterize additive, positive-affine, potential-shaping,
and context-gluing ambiguities for several finite access models. Version
v0.15 assumes the v0.13 scalar-gradient quotient and does not enlarge the
invariance-group theorem.

### 2. Necessary and sufficient query/environment interventions

**Advanced for one cycle experiment, still open generally.**

Within the frozen model, v0.15 gives a necessary and sufficient number of
equal-count trials for informative-fiber availability over a probability
box. It does not characterize arbitrary intervention graphs, adaptive
policies, transition interventions, or environment families.

### 3. Sharp query/sample/intervention bounds

**Sharply closed for the frozen equal-count cycle case only.**

The formula for `n_star(k,epsilon,delta)` is exact. This is a genuine sharp
sample requirement, not merely a sufficient upper bound.

The general fixed-total-budget allocation problem remains open. Balanced
allocation passed 32 prospective finite cells, but the general theorem is
not claimed because the development proof route failed.

### 4. Robustness to behavioral misspecification

**Open.**

The theorem assumes independent Bernoulli comparisons in a known finite
cycle design. Dependence, unknown response links, context-sensitive response
laws, strategic demonstrators, and non-expected-utility behavior are outside
v0.15. Earlier negative results show that some of these extensions are
load-bearing rather than cosmetic.

### 5. No-go theorem when no coherent latent value object exists

**Only finite special cases exist.**

Earlier contextual and unknown-link witnesses establish finite
nonidentifiability and non-gluing examples. No full characterization of
incoherent or non-EU demonstrators is supplied by v0.15.

## Why the finite allocation pass is not a resolution step

For edge-specific counts, the probability adversary still reduces to endpoint
assignments. What remains is a discrete maximin design problem over integer
allocations.

The registered fresh grid found balanced allocation optimal in 32 of 32
cells. This is evidence that the conjecture is worth proving or attacking,
not evidence that it is true for arbitrary `k`, `epsilon`, and total budget.
A valid next step needs a pairwise-exchange, majorization, or equivalent
argument, plus a counterexample search outside the existing finite ranges.

## Next load-bearing milestone

The cleanest next theorem target is:

> Prove or refute that positive integer trial counts differing by at most one
> maximize worst-case informative-fiber availability over endpoint
> probabilities for every cycle length, interior, and fixed total budget.

Even a proof would remain below full ASMP-9. The subsequent load-bearing
extension is from one cycle to general comparison graphs, where the
conditional quotient can have multiple cycle directions and the design
problem must account for graph topology and response-model misspecification.

## Epistemic boundary

Version v0.15 is a prospectively registered exact theorem verification with a
clean independent replay. It is not evidence that human values are coherent,
that model preferences follow Bradley-Terry, that sufficient real-world
interventions are known, or that recursive self-improvement can be safely
evaluated from preference comparisons.
