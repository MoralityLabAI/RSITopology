# ASMP-9 finite cactus-design protocol v0.19.2

## Amendment reason

Versions 0.19 and 0.19.1 passed every mathematical gate but failed the frozen
`180`-second wall-time gate. The post-outcome v0.19.1 profile localized
`387.565` of `430.209` profiled seconds to one four-cycle DP/exhaustive cell.

The Bellman recursion was not the bottleneck. The independent exhaustive
checker recomputed the same endpoint-label minimum for a given cycle length
and cycle total in many different total-vector compositions.

Version 0.19.2 changes only that checker:

1. for every registered `(cycle length, cycle total)` pair, exhaust all
   endpoint-label assignments once;
2. cache the resulting exact rational minimum; and
3. exhaust every feasible vector of cycle totals using those independent
   values.

The scientific scope and `180`-second/`1 GiB`/CPU-only cap are unchanged. The
fresh four-cycle cell has more total cycle length and a longer largest cycle
than the v0.19.1 cell, so the successor is not a narrowed workload.

## Fresh cells

Factorization:

```text
(4,5), no bridge, epsilon=8/27, every endpoint-label vector
(3,7), one bridge, epsilon=6/23, eight label vectors and two bridge counts
```

Dynamic programming:

```text
(5,8,10,12), bridges=2, N=50, epsilon=8/27
(4,7,10),    bridges=2, N=36, epsilon=7/26
(6,9,11),    bridges=1, N=40, epsilon=6/23
```

Full edge census:

```text
(3,4), one bridge, N=12, epsilon=7/26
```

Outcome-neutral comparators:

```text
(5,7),   N=18, epsilon=8/27
(7,7,7), N=31, epsilon=6/23
(8,11),  N=30, epsilon=7/26
```

All listed epsilon values lie outside the frozen v0.19/v0.19.1 development
registry.

## Gates

- `G0`: registration, ancestry, and all sealed hashes pass.
- `G1`: the fresh registry is complete and disjoint from the burned epsilon
  set.
- `G2`: the memoized independent checker reproduces all three burned v0.19.1
  DP values and complete optimizer sets.
- `G3`: every fresh direct residual probability equals the cactus cycle
  product.
- `G4`: bridge-count changes are irrelevant and every full-census optimizer
  leaves bridges at count one.
- `G5`: Bellman and memoized independent exhaustive enumeration return
  identical exact values and complete optimizer sets.
- `G6`: the full positive edge census equals Bellman; every optimizer balances
  within each cycle and induces a Bellman-optimal total vector.
- `G7`: the two frozen nonconcavity/asymptotic-uniform counterexamples
  reproduce exactly.
- `G8`: every fresh comparator is completely classified; no gap sign is
  required.
- `G9`: CPU only, no GPU, at most `180` seconds and `1 GiB` peak resident
  memory.

Any failed gate returns:

```text
finite_budget_cactus_dp_not_established_v0_19_2
```

## Claim boundary

Exact finite-budget maximin allocation on cactus cyclic cores inside the
frozen independent-binomial, known symmetric-interior, positive-count
conditional-access model inherited from ASMP-9 v0.16-v0.18. Version 0.19.2 is
a computation-only successor to the v0.19 and v0.19.1 wall-time failures. It
preserves complete independent endpoint-label and cycle-total enumeration but
memoizes repeated one-cycle minima. The ASMP-9-specific result is the
reduction to a classical series-product integer resource-allocation problem.
Dynamic programming, redundancy allocation, and greedy criteria are not
claimed as new. This is not an arbitrary-graph every-budget theorem, adaptive
allocation theorem, dependent-response theorem, unknown-link theorem,
downstream policy-estimation theorem, behavioral reward-identification
theorem, general IRL theorem, or ASMP-9 resolution.
