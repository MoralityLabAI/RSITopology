# ASMP-9 finite cactus-design protocol v0.19.1

## Amendment reason

The registered v0.19 execution passed all eight mathematical gates but took
`261.413` seconds against a frozen `180`-second cap. Its verdict is therefore
`finite_budget_cactus_dp_not_established`.

Version 0.19.1 does not alter the theorem, scientific margins, or resource
cap. It changes only the exact residual evaluator:

1. compute liveness once for each ternary graph status;
2. reuse that table across endpoint-label vectors and count allocations; and
3. contract integer status numerators under a common exact denominator.

Every v0.19 scientific cell is burned. Version 0.19.1 uses new graphs,
epsilon values, budgets, and comparator cells.

## Exact arithmetic

For rational

```text
epsilon=a/d,
```

an edge with count `n` has the common status denominator `d^n`. At a low
endpoint its integer numerators are

```text
Z=(d-a)^n,
F=a^n,
I=d^n-(d-a)^n-a^n,
```

with `Z` and `F` swapped at the high endpoint. Products over edges therefore
share one exact denominator. No floating-point arithmetic enters a scientific
gate.

## Fresh cells

### Factorization

- cycle blocks `(4,4)`, no bridge, `epsilon=7/23`, every `2^8` label vector;
- cycle blocks `(3,6)` plus one bridge, `epsilon=4/19`, eight frozen label
  vectors and two allocations differing only in bridge count.

### Dynamic programming

```text
(5,7,9),    bridges=2, N=35, epsilon=7/24
(4,6,8,11), bridges=2, N=46, epsilon=4/17
(7,8,10),   bridges=1, N=39, epsilon=5/19.
```

### Full edge census

```text
(3,5), bridges=1, N=13, epsilon=4/19.
```

### Outcome-neutral comparators

```text
(4,5),   N=15, epsilon=4/17
(6,6,6), N=26, epsilon=7/24
(6,9),   N=24, epsilon=5/19.
```

## Gates

- `G0`: all registered hashes and ancestry checks pass.
- `G1`: the fresh registry is complete and all fresh epsilons lie outside the
  burned set.
- `G2`: the cached integer engine reproduces the burned v0.19 factorization
  row hash and bridge equalities exactly.
- `G3`: every fresh direct residual probability equals the cactus cycle
  product.
- `G4`: bridge-count changes are irrelevant and every full-census optimizer
  leaves bridges at count one.
- `G5`: Bellman and independent exhaustive cycle-total enumeration return
  identical exact values and complete optimizer sets.
- `G6`: the full positive edge census equals Bellman; every optimizer balances
  within each cycle and induces a Bellman-optimal total vector.
- `G7`: the two frozen nonconcavity/asymptotic-uniform regression certificates
  reproduce exactly.
- `G8`: every fresh comparator is completely classified; no gap sign is
  required.
- `G9`: CPU only, no GPU, at most `180` seconds and `1 GiB` peak resident
  memory.

Any failed gate returns

```text
finite_budget_cactus_dp_not_established_v0_19_1.
```

## Claim boundary

Exact finite-budget maximin allocation on cactus cyclic cores inside the
frozen independent-binomial, known symmetric-interior, positive-count
conditional-access model inherited from ASMP-9 v0.16-v0.18. Version 0.19.1 is
a computation-only successor to the v0.19 wall-time failure: it caches graph
liveness by ternary residual state and contracts exact integer status
numerators, while using wholly new scientific cells. The ASMP-9-specific
result is the reduction to a classical series-product integer
resource-allocation problem. Dynamic programming, redundancy allocation, and
greedy criteria are not claimed as new. This is not an arbitrary-graph
every-budget theorem, adaptive allocation theorem, dependent-response theorem,
unknown-link theorem, downstream policy-estimation theorem, behavioral
reward-identification theorem, general IRL theorem, or ASMP-9 resolution.

