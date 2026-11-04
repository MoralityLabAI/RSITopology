# Discounted reward shaping is a gain-graph quotient

## Result

For a finite directed multigraph `G=(V,E)` and a fixed discount
`0<gamma<1`, define the discounted shaping operator

```text
(D_gamma Phi)(u->v) = gamma Phi(v) - Phi(u).
```

Give an edge gain `gamma^-1` when traversed in its registered direction and
`gamma` when traversed against it. Let `b_gamma(G)` be the number of weak
components whose every closed walk has gain one, including isolated vertices.
Then:

```text
rank(D_gamma) = |V| - b_gamma(G),

dim(R^E / im D_gamma)
  = |E| - |V| + b_gamma(G).
```

This is the classical gain-incidence rank theorem specialized to discounted
potential shaping. A component is balanced exactly when its vertices admit an
integer height satisfying:

```text
h(v) = h(u) + 1
```

on every directed edge `u->v`.

The endpoints are different objects and were checked separately:

```text
gamma=1: rank(D_1) = |V| - c(G),
gamma=0: rank(D_0) = number of distinct edge-source vertices.
```

## Why ordinary cycles stop being the right access object

For an undiscounted incidence matrix, every connected graph contributes its
ordinary cycle space. Discounting changes this. A directed cycle is
unbalanced for every `0<gamma<1`; its discounted shaping operator is full
rank, so:

```text
dim(R^E / im D_gamma) = 0.
```

Consequently, the ordinary loop return contains no shaping-invariant
edge-reward information in this case. Equal-length routes between the same
endpoints can retain a quotient direction, while changing one route's length
by one can remove it. The access grammar is controlled by the gain-balanced
quotient, not ordinary cycle rank alone.

## Finite-trajectory access

For a trajectory

```text
tau=(s_0 -> s_1 -> ... -> s_T)
```

with discounted edge occupancy `q_tau`, the shaping contribution telescopes:

```text
q_tau^T D_gamma Phi
  = gamma^T Phi(s_T) - Phi(s_0).
```

Two trajectory returns are therefore invariant under every discounted
potential shaping exactly when their discounted boundary signatures match:

```text
-e_(s_0) + gamma^T e_(s_T)
=
-e_(s'_0) + gamma^(T') e_(s'_(T')).
```

Same start, same end, and same horizon is a sufficient special case. Same
start and end alone is not sufficient when horizons differ.

## Prospective verification

The protocol and implementation were committed before the fresh cells were
run. The registered CPU-only execution checked:

- 32,768 fresh oriented simple graphs on six vertices at
  `gamma in {1/3,2/5,99/100}`;
- 8,192 fresh seven-vertex directed multigraphs, including self-loops,
  parallel edges, and opposite-direction pairs, at
  `gamma in {3/7,7/8}`;
- both endpoint formulas on every graph;
- 16,384 exact random telescoping identities;
- 4,096 matched-boundary trajectory pairs;
- 4,096 unequal-horizon counterexamples;
- directed cycles of lengths 2 through 128;
- equal- and unequal-length two-route controls; and
- 16 prereveal mathematical tests.

All eight registered gates passed. There were zero rational-rank, endpoint,
telescoping, boundary-cancellation, or planted-control mismatches. The
independent artifact verifier reproduced every sealed input and output hash.

## ASMP-9 contribution and remaining gap

This closes the discounted potential-shaping operator inside the current
finite edge-reward access program: it identifies the quotient dimension and
the exact boundary condition required for finite trajectory comparisons to
survive shaping.

It does not resolve ASMP-9. Remaining obligations include:

1. policy- and demonstration-based observation rather than declared exact
   return comparisons;
2. unknown or misspecified response parameters;
3. dependent and history-sensitive demonstrators;
4. characterization of invariances larger than discounted potential shaping;
   and
5. a no-go theorem for inconsistent demonstrations that admit no coherent
   scalar value object.

The gain-graph rank result and telescoping identity are classical. Novelty is
not claimed; the contribution is their explicit access-theoretic
specialization, prospective verification, and integration with the preceding
ASMP-9 exact-width and finite-sample results.
