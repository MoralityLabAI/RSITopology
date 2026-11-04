# ASMP-9 exact finite-budget cactus-design protocol v0.19

## Question

Version v0.18 identifies cyclic-core bonds as the minimal asymptotic failure
supports and proves that the exponent-optimal cactus allocation is uniform on
nonbridge edges. It explicitly leaves exact finite budgets open.

Version v0.19 tests and registers the finite replacement:

1. cactus liveness factors into independent cycle events;
2. v0.16 balances counts within each cycle;
3. cycle totals form a classical separable integer allocation problem;
4. an exact Bellman recursion solves that problem; and
5. neither one-step marginal greedy allocation nor asymptotic global edge
   balance is an exact finite-budget rule.

## Mathematical object

Let the cyclic core of `G` be a cactus with edge-disjoint cycle blocks
`C_1,...,C_c`, of lengths `k_1,...,k_c`. Every edge receives a positive
integer trial count. Original bridges therefore consume one mandatory trial
each but do not affect quotient liveness.

For one cycle, let

```text
f_k(N)=F_star(k,N,epsilon)
```

denote the exact v0.16 maximin availability after balancing `N` trials over
its `k` edges.

The registered theorem is

```text
F_G(n)=product_j F_Cj(n restricted to C_j),
```

and hence

```text
max F_G
  = max product_j f_(k_j)(N_j)

subject to

  N_j>=k_j,
  sum_j N_j=N-number_of_bridges.
```

The exact recurrence is

```text
D_0(0)=1,

D_j(b)
  = max_(k_j<=t<=b)
      D_(j-1)(b-t) f_(k_j)(t).
```

The proof and boundaries are frozen in `THEORY_DRAFT_v0_19.md`.

## Fresh cells

No fresh epsilon value occurs in the burned development sweeps.

### Residual-state factorization

- figure-eight cactus with cycle lengths `(3,4)`, no bridge,
  `epsilon=3/11`, every one of its `2^7` endpoint-label vectors;
- figure-eight cactus with lengths `(3,5)` plus one bridge,
  `epsilon=5/17`, eight frozen endpoint-label vectors, and two allocations
  differing only in the bridge count.

The first cell compares direct `3^7` residual-state enumeration against the
cycle product for every label vector. The second checks both factorization and
bridge-count irrelevance.

### Exact dynamic programming

Three fresh cycle-block registries:

```text
(5,6,8),    bridges=2, N=32, epsilon=4/15
(4,7,9,10), bridges=3, N=47, epsilon=5/18
(6,7,11),   bridges=1, N=37, epsilon=3/14
```

The Bellman result must match an independently routed exhaustive enumeration
of every feasible cycle-total vector, including all optimizers.

### Full edge-allocation census

On cycle lengths `(3,4)` plus one bridge, `N=12`, and `epsilon=3/11`,
enumerate every positive labelled edge allocation. Its exact optimum must
equal the Bellman value. Every optimizer must:

- leave the bridge at count one;
- balance counts inside each cycle; and
- induce a Bellman-optimal cycle-total vector.

### Fresh comparator classifications

The protocol freezes three additional cells before their outcomes:

```text
(4,4),   N=14, epsilon=5/18
(5,5,5), N=22, epsilon=7/20
(5,7),   N=20, epsilon=3/14.
```

For each, report exact Bellman optima, every maximum-one-step-ratio greedy
endpoint, and every cycle-total vector induced by globally balanced edge
counts. A zero or nonzero gap is an outcome, not a gate direction.

## Registered gates

### G0 — registration binding

Every sealed file matches its registered SHA-256; the registered
implementation commit is an ancestor of execution; and the protocol path is
exact.

### G1 — fresh registry

Every declared cell appears exactly once. No fresh epsilon is in the burned
development epsilon set. All label/count dimensions match their graph.

### G2 — exact cactus factorization

Every direct residual-state probability equals the product of its cycle
probabilities exactly.

### G3 — bridge irrelevance and floor

The two bridge-count allocations give identical availability on every frozen
label vector. Every full-census optimizer assigns the bridge exactly one
trial.

### G4 — DP equals independent exhaustive totals

On every fresh DP cell, exact value and the complete optimizer set from the
Bellman recurrence equal the independent cycle-total enumeration.

### G5 — DP equals all-edge census

The fresh full labelled edge census equals the Bellman value. Every edge-level
optimizer balances within each cycle and induces a Bellman-optimal
cycle-total vector.

### G6 — nonconcavity and comparator certificates

The two frozen exact development witnesses reproduce:

```text
two C3 blocks, epsilon=1/4, N=10:
  greedy endpoints=(4,6),(6,4)
  optimum=(5,5)
  exact gap=45/262144

C3+C4, epsilon=1/10, N=12:
  best globally balanced totals=(4,8)
  optimum=(3,9)
  exact gap=26235981/125000000000.
```

These are analytic regression certificates, not fresh evidence.

### G7 — fresh comparator classification

All three fresh comparator cells return complete exact classifications. The
gate checks completeness and arithmetic agreement, not the sign of a
preselected gap.

### G8 — resource and scope

```text
CPU only
GPU prohibited
wall time <= 180 seconds
peak resident memory <= 1 GiB
```

The exact claim boundary must be emitted without alteration.

## Stop and interpretation rules

- Any failed gate gives
  `finite_budget_cactus_dp_not_established`.
- No cell, threshold, comparator, or resource cap may change after
  registration.
- Burned development cells never count as fresh verification.
- A pass closes exact finite-budget allocation only for cactus cyclic cores
  under the frozen independent known-link model.

## Claim boundary

Exact finite-budget maximin allocation on cactus cyclic cores inside the
frozen independent-binomial, known symmetric-interior, positive-count
conditional-access model inherited from ASMP-9 v0.16-v0.18. The ASMP-9-specific
result is the reduction to a classical series-product integer
resource-allocation problem. Dynamic programming, redundancy allocation, and
greedy criteria are not claimed as new. This is not an arbitrary-graph
every-budget theorem, adaptive allocation theorem, dependent-response theorem,
unknown-link theorem, downstream policy-estimation theorem, behavioral
reward-identification theorem, general IRL theorem, or ASMP-9 resolution.

