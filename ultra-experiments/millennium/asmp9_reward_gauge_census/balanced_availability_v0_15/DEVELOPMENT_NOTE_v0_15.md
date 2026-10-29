# ASMP-9 v0.15 burned development note

## Status

This note reports an unregistered CPU-only development census. Its parameter
registry is burned. No number in this directory is claim-eligible evidence for
a later prospective run.

The equal-count mathematical result is analytic. The census checks its
implementation and boundary behavior. The unequal-count balancing statement
remains a conjecture despite passing every bounded cell.

## Result 1: exact equal-count minimax

For a cycle of length `k`, `n` Bernoulli trials per edge, and the declared
interior

```text
epsilon <= p_e <= 1-epsilon,
```

the informative-fiber probability is separately concave in the edge
probabilities. Its minimum therefore occurs at an endpoint assignment. Among
endpoint assignments, the minimum is attained by splitting low and high
probabilities as evenly as possible.

With

```text
m=floor(k/2),  h=ceil(k/2),
a=(1-epsilon)^n,  b=epsilon^n,
x=1-a,  y=1-b,  z=1-a-b,
```

the exact worst-case availability is

```text
A_min = x^m y^h + y^m x^h - z^k.
```

This is a sharp identity: the balanced endpoint assignment attains it.

The 320-cell exact-rational registry covered:

- `k=3,...,10`;
- `n=1,...,8`; and
- `epsilon` in `{1/20, 1/10, 1/5, 1/4, 2/5}`.

Every formula value matched exhaustive endpoint enumeration. Every minimizing
endpoint count matched the middle split. The exact minimum always dominated
the conservative v0.14 bound. For `k>=4`, it was strictly below the one-low,
remaining-high drift control in every registered development cell.

This last control matters: the nuisance ray used to prove v0.14's unbounded
collapse is not the bounded-interior minimax adversary. Inside a compact
probability box, the worst nuisance distributes opposing endpoint biases as
evenly as the cycle permits.

## Result 2: exact per-edge trial threshold

For target availability `1-delta`, the exact equal-count threshold is

```text
n_star(k,epsilon,delta)
  = min {n>=1 : A_min(k,n,epsilon) >= 1-delta}.
```

All 80 threshold cells placed the predecessor strictly below the target and
the selected count at or above it. Selected examples:

| `k` | `epsilon` | target | `n_star` |
| ---: | ---: | ---: | ---: |
| 6 | 1/10 | 0.80 | 17 |
| 6 | 1/10 | 0.90 | 21 |
| 6 | 1/10 | 0.95 | 24 |
| 6 | 1/10 | 0.99 | 32 |
| 6 | 1/4 | 0.80 | 6 |
| 6 | 1/4 | 0.90 | 8 |
| 6 | 1/4 | 0.95 | 9 |
| 6 | 1/4 | 0.99 | 12 |
| 12 | 1/10 | 0.80 | 23 |
| 12 | 1/10 | 0.90 | 27 |
| 12 | 1/10 | 0.95 | 31 |
| 12 | 1/10 | 0.99 | 39 |

The 16 `epsilon=0` controls all returned zero worst-case availability,
confirming that no positive uniform guarantee exists without a probability
interior.

For fixed `k` and `0<epsilon<1/2`,

```text
1-A_min
  = floor(k/2) ceil(k/2) (1-epsilon)^(2n) [1+o(1)].
```

Thus the sharp threshold scales as

```text
n_star
  = log(floor(k/2) ceil(k/2) / delta)
    / (2 log(1/(1-epsilon)))
    + O(1).
```

The factor `2n` explains why the v0.14 one-sided no-zero lower bound can be
extremely conservative: an uninformative fiber requires both a zero edge and
a full edge.

## Result 3: bounded unequal-allocation census

For each of 81 cells, the runner exhaustively enumerated:

- all nondecreasing positive integer allocations for `k` in `{3,4,5}`;
- total budgets from `k` through `k+8`;
- `epsilon` in `{1/10,1/5,1/4}`; and
- every endpoint nuisance assignment.

The allocation whose counts differed by at most one was optimal in all 81
cells. This is development evidence for a balancing conjecture, not a theorem.
The optimizer was unique up to edge permutation in the inspected registry.

## Failed routes retained in the record

Two failures constrain the next step:

1. A naive exact-`Fraction` allocation enumeration exceeded a 124-second
   development budget before producing a result. The implemented census
   quotients edge-permutation symmetry by enumerating nondecreasing
   allocations.
2. A proposed uniform-adversary certificate for a pairwise averaging proof
   failed in 180 screened cases. That proof route is invalid. The balancing
   conjecture must not be promoted without a valid exchange, majorization, or
   equivalent argument.

These failures are not gate failures because no prospective protocol exists
for v0.15. They are recorded to prevent the successful finite census from
silently laundering an unproved general claim.

## Prior-art and novelty boundary

Conditional likelihood, exact conditional versus unconditional inference,
paired-comparison minimax rates, and Bradley-Terry optimal design are
established literatures. This development result is an ASMP-9 access-ledger
specialization:

- exact nuisance minimization for the v0.13 conditional quotient;
- a sharp replacement for the v0.14 conservative availability bound; and
- an exact equal-count trial threshold over a declared probability interior.

It is not a general optimal-design theorem, adaptive allocation theorem,
behavioral result, or resolution of ASMP-9.

## Registration decision

The equal-count theorem and its boundary controls are non-vacuous and
independent of the burned parameter grid. They merit a fresh prospective
registration on disjoint `k`, `n`, `epsilon`, and `delta` values.

The unequal-count allocation conjecture may be included only as a separately
labelled finite falsification target. A prospective census can reject it but
cannot establish the unbounded theorem.
