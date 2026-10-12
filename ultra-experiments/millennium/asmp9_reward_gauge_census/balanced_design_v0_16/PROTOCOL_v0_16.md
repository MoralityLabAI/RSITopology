# ASMP-9 balanced maximin design protocol v0.16

## Status

This protocol prospectively verifies the pairwise balancing theorem, compact
optimal-value formula, and exact total-budget threshold. The entire v0.16
development census is burned.

## Fresh registries

### Pairwise proof registry

```text
epsilon in {1/32,3/16,5/16,11/24}
a in {7,9,12}
b-a in {8,11,15}
other count tuples in {(6),(3,7),(2,6,9)}
all endpoint labels on the other tuple.
```

This yields 504 exact local games.

### Global allocation registry

```text
k in {6,7}
epsilon in {1/32,5/16}
N-k in {11,13,15,17}.
```

Every nondecreasing positive integer allocation and every endpoint nuisance
assignment is enumerated.

### Compact-value registry

```text
k in {12,14}
epsilon in {3/16,11/24}
N-k in {3,8,13}.
```

The compact two-count formula is compared with all `2^k` endpoint labels.

### Total-budget threshold registry

```text
k in {12,14,17}
epsilon in {1/32,3/16,5/16,11/24}
delta in {1/32,1/128,1/512}.
```

### Negative boundaries

```text
epsilon=0 at k in {12,17}
k=2 at N in {13,17}, epsilon in {1/32,5/16}.
```

## Gates

- `G0_registration_binding`: execution occurs at the clean registration
  commit and every sealed hash matches.
- `G1_registry_completeness`: the exact cell counts and unique parameter
  keys match the protocol.
- `G2_pair_reduction`: same/opposite branch formulas and both nonnegative
  decompositions match direct four-label minimization.
- `G3_same_branch_smoothing`: every same-label branch strictly improves
  under the frozen Robin-Hood transfer.
- `G4_opposite_branch_smoothing`: every opposite-label branch strictly
  improves; the sum-only identity is invariant and all required factors have
  the registered direction.
- `G5_global_balanced_optimum`: every fresh global cell has the balanced
  allocation as its unique optimizer modulo edge permutation, and every
  unbalanced allocation's canonical smoothing step strictly improves it.
- `G6_compact_value_formula`: every compact optimal-value cell exactly
  matches exhaustive endpoint enumeration.
- `G7_total_budget_threshold`: every selected total meets its target, its
  predecessor does not, and optimal availability is monotone over the
  traversed totals.
- `G8_negative_boundaries`: `epsilon=0` destroys positive guarantees and the
  `k=2` controls show nonunique fixed-total optima.
- `G9_resource_and_scope`: the CPU-only run completes within 120 seconds and
  1 GiB and preserves the frozen claim boundary.

All gates are binding. A failure produces a failed registered verdict.

## Resources

```text
CPU only
wall time <= 120 seconds
peak resident memory <= 1 GiB
GPU prohibited
```

## Claim boundary

A passing run verifies fresh exact instances of a proved integer maximin
balancing theorem and its total-budget corollary for one independent
Bernoulli cycle experiment. It does not establish adaptive allocation,
multi-cycle optimal design, behavioral validity, a general RL rollout policy,
general IRL identifiability, or resolution of ASMP-9.
