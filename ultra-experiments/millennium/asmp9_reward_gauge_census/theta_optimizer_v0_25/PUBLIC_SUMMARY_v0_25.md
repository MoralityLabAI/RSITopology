# ASMP-9 v0.25: exact allocation on generalized-theta blocks

## Result

For the frozen ASMP-9 independent fair-microtrial model at
`epsilon = 1/2`, exact finite-budget allocation is tractable on a
generalized-theta block after a strict dimension reduction.

A generalized-theta block consists of `k >= 2` internally
vertex-disjoint paths with common terminals.  The class contains overlapping
cycles when `k >= 3`.

For path `j`, define

```text
A_j = product_(e in path j) (2^(n_e)-1)
B_j = product_(e in path j) (2^(n_e)-2).
```

The exact common-denominator numerator of strong residual availability is

```text
S(n) = product_j(2A_j-B_j) - 2 product_j(A_j-B_j).
```

The first product requires every path to support at least one terminal
direction.  The subtraction removes the two cases in which every usable path
supports only the same direction.

## Balancing theorem

Fix one path and all other path allocations.  If two edges on the fixed path
have counts `p >= q+2`, moving one trial from the high-count edge to the
low-count edge strictly increases `S`.

Consequently, every global optimum balances counts within each individual
path: counts on one path differ by at most one.

This is deliberately not a global edge-balancing theorem.  Different paths
can receive different total budgets.

If path `j` has length `l_j` and total `s_j`, its balanced edge counts and
therefore `A_j(s_j), B_j(s_j)` are fixed.  Exact global optimization reduces
to enumerating

```text
binomial(N-|E|+k-1, k-1)
```

path-total allocations.  For fixed `k`, this is polynomial in the numerical
trial budget `N` and pseudopolynomial when `N` is binary encoded.

## Prospective validation

The implementation and protocol were pushed before the registration, and
the registration was pushed before any fresh outcome was read.

All nine gates passed:

| Fresh optimizer cell | Full edge allocations | Reduced path-total cells | Exact optimal path totals |
|---|---:|---:|---|
| lengths `(1,2,4)`, `N=12` | 462 | 21 | `(1,3,8)` |
| lengths `(2,3,3)`, `N=13` | 792 | 21 | `(3,5,5)` |
| lengths `(1,2,2,3)`, `N=13` | 792 | 56 | `(1,3,3,6)` |

In every cell, reduced and full enumeration returned the same exact maximum,
and every full-enumeration optimizer was path-internally balanced.

An additional fresh exhaustive census checked 43,740 admissible smoothing
moves on a `(2,3,4)` theta block.  All improvements were strictly positive;
the minimum numerator gain was 4.

An independent verifier:

- enumerated edge orientation states directly on the fresh formula cells;
- reimplemented the reduced optimizer separately;
- rechecked sealed hashes, gate coverage, resource caps, and the verdict.

All 11 independent checks passed.

## Prior art and attribution

Majorization, Schur-convex component assignment, active-spare allocation, and
pseudopolynomial reliability allocation in ordinary parallel-series and
series-parallel systems are classical.  The closest primary sources were
audited directly and are itemized in `PRIOR_ART_GATE_v0_25.md`.

Those sources provide the methodological neighborhood but optimize different
objects: heterogeneous component assignment, multistate component quality,
or spare placement under ordinary reliability laws.  The present result is a
specialized ASMP partial-orientation theorem.  No novelty claim is registered;
absence of an exact match from the bounded search is not proof of novelty.

## What this changes

The v0.23 K4 construction showed that one-unit exchange ascent can become
trapped on an overlapping-cycle block.  v0.25 now supplies the complementary
positive boundary: generalized-theta blocks admit an exact global optimizer
after path-internal smoothing.

The remaining ASMP-9 optimizer problem is inside arbitrary biconnected blocks
beyond this theta class.

## Claim boundary

This result does not:

- solve all series-parallel or arbitrary biconnected blocks;
- give a polynomial-time algorithm in binary input length;
- prove optimizer hardness or approximation hardness;
- cover arbitrary `epsilon`, adaptive allocation, dependent responses, or
  response misspecification;
- identify behavioral reward functions or solve general inverse
  reinforcement learning; or
- resolve ASMP-9.

It establishes one exact tractable overlapping-cycle class inside the
registered access model.
