# ASMP-9 v0.16 burned development note

## Status

This is unregistered CPU-only theorem development. Every parameter used by
`DEVELOPMENT_CENSUS_v0_16.json` is burned. The census verifies algebra and
implementation; the theorem rests on the pairwise proof in
`THEOREM_v0_16.md`.

## Problem closed inside the frozen model

Version v0.15 proved the sharp worst-case availability when every cycle edge
receives the same number of trials. It left open the fixed-total-budget
problem:

```text
maximize over positive integer n_i with sum n_i=N
minimum over p_i in [epsilon,1-epsilon]
P(informative conditional fiber).
```

For every cycle length `k>=3` and `0<epsilon<=1/2`, v0.16 proves that the
unique optimizer up to edge permutation has counts differing by at most one.

If two counts satisfy `a<=b-2`, the Robin-Hood transfer

```text
(a,b) -> (a+1,b-1)
```

strictly increases the endpoint-minimized availability. Repeating transfers
terminates at the balanced allocation.

## Why the v0.15 proof attempt failed

The first attempted proof tried to show that balancing improves availability
for every fixed endpoint-label assignment. That statement is false: a
particular signed assignment can get worse.

The correct order of operations is the order in the maximin problem:

1. fix the labels on all other edges;
2. minimize over the four labels on the selected pair; and only then
3. compare the imbalanced and balanced pair.

The minimized pair game has only two branches:

```text
same endpoint labels
opposite endpoint labels.
```

Both branches admit nonnegative decompositions into factors that are invariant
or improve under balancing. This is the load-bearing correction.

## Exact optimal value

For total budget

```text
N=qk+t,  0<=t<k,
```

the optimal design contains `k-t` counts equal to `q` and `t` counts equal to
`q+1`. Nature's endpoint choice then depends only on the number of low labels
in each count class. The exact optimal value requires at most

```text
(k-t+1)(t+1)
```

cells instead of all `2^k` label assignments.

This gives an exact necessary-and-sufficient total-budget threshold

```text
N_star(k,epsilon,delta)
  = min {N>=k : F_star(k,N,epsilon) >= 1-delta}.
```

## Burned exact census

The exact-rational development run completed:

- 4,752 local pair games;
- 275 global allocation cells;
- 416 closed-value versus full-label comparisons;
- 48 total-budget threshold checks;
- 4 `epsilon=0` boundary controls; and
- 9 `k=2` boundary controls.

All mismatch and failure counts were zero.

Before the proof was found, a separate float screening enumerated 2,640
allocation cells over cycle lengths `3,...,10`, several total budgets, and
interiors from `0.001` to `0.499`; it found no counterexample. That screening
motivated the theorem search but is not evidence for it.

## Boundary controls

- At `epsilon=0`, worst-case availability is zero for every finite allocation,
  so balancing is not unique.
- At `k=2`, every positive allocation with a fixed total is optimal from total
  budget 4 onward in the registered development cells. The opposite-label
  branch depends only on `a+b`, which is why the strict proof requires at
  least one other edge.

These controls prevent a true theorem on `k>=3` and positive interiors from
being reported as an unrestricted allocation principle.

## Prior-art boundary

Balanced reliability allocation, majorization, Robin-Hood transfers, and
paired-comparison optimal design are established mathematical areas. Recent
RLVR work also uses mixed success/failure probability as an empirical rollout
allocation objective.

The surviving contribution is the exact specialization to the ASMP-9
conditional cycle quotient, including the adversarial endpoint minimization,
strict integer transfer, compact optimal-value formula, and exact total-budget
threshold.

It is not a general Bradley-Terry design theorem, adaptive rollout policy,
behavioral result, or ASMP-9 resolution.

## Registration decision

The analytic proof closes the open v0.15 allocation conjecture and supports a
fresh prospective registration. The fresh registry should:

1. use disjoint cycle lengths, interiors, totals, and target errors;
2. verify every pair decomposition against direct four-label minimization;
3. verify the strict smoothing gate on arbitrary unbalanced allocations;
4. compare the compact optimal-value formula to full endpoint enumeration;
5. verify exact total-budget threshold straddling; and
6. include the `epsilon=0` and `k=2` negative boundaries.
