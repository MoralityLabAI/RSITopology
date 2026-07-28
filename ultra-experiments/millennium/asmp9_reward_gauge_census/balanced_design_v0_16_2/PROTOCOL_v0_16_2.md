# ASMP-9 balanced maximin design protocol v0.16.2

## Amendment reason

Version v0.16 exceeded its cap during exhaustive verification. Version
v0.16.1 completed four stages but exceeded the cap in a linear scan for the
small-interior total-budget threshold.

Version v0.16.2 keeps the theorem, gate IDs, and resource cap. It freezes:

1. exact exponential bracketing;
2. exact binary search;
3. exact selected/predecessor verification; and
4. a third disjoint registry with cheap global enumeration but larger
   allocation imbalance.

## Fresh registries

### Pairwise proof

```text
epsilon in {1/30,7/30,11/30,7/15}
a in {14,16,19}
b-a in {10,13,17}
other counts in {(9),(5,11),(2,8,12)}
all other-edge endpoint labels.
```

Total: 504.

### Global allocation

```text
k in {3,4}
epsilon in {1/30,11/30}
N-k in {22,30,40,50}.
```

Total: 16. These cells have small endpoint universes but much wider integer
allocation ranges than either prior registered attempt.

### Compact optimal value

```text
k in {9,10}
epsilon in {7/30,7/15}
N-k in {13,17,23}.
```

Total: 12.

### Total-budget threshold

```text
k in {11,16,19}
epsilon in {1/30,7/30,11/30,7/15}
delta in {1/48,1/192,1/768}.
```

Total: 36.

### Boundaries

```text
epsilon=0 at k in {10,11}
k=2 at N in {15,19}, epsilon in {7/30,7/15}.
```

## Exact logarithmic threshold algorithm

For each threshold cell:

1. evaluate the minimum legal total `N=k`;
2. if it fails, double an upper total until it passes;
3. binary search between the last failing and first passing totals;
4. recompute `F_star(N-1)` and `F_star(N)` exactly; and
5. require strict predecessor failure and selected-total passage.

All bracket decisions use exact fractions. The monotonicity justification is
the theorem's coupling argument: adding a trial cannot turn an interior count
into a zero or full count.

## Gates and resources

The ten v0.16 gate IDs are unchanged. The resource cap is unchanged:

```text
CPU only
wall time <= 120 seconds
peak resident memory <= 1 GiB
GPU prohibited
```

Start, progress, completion, and abort ledgers remain mandatory.

## Claim boundary

A pass verifies fresh exact instances of the balanced integer maximin theorem,
compact optimal value, and exact total-budget threshold for one independent
Bernoulli cycle experiment. It is not adaptive allocation, multi-cycle
optimal design, behavioral validation, a general RL rollout policy, general
IRL identifiability, or ASMP-9 resolution.
