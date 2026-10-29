# ASMP-9 balanced maximin design protocol v0.16.1

## Amendment reason

The registered v0.16 run exceeded its 120-second cap and emitted no atomic
result. Version v0.16.1 keeps the theorem, gates, and cap but replaces the
burned registry with a disjoint workload sized using timing measurements from
the failed cells.

The runner must create a start ledger before scientific computation and update
a progress ledger after every stage. Exceptions emit an abort ledger.

## Fresh registries

### Pairwise proof

```text
epsilon in {1/28,5/24,7/20,13/28}
a in {8,10,13}
b-a in {9,12,16}
other counts in {(5),(4,8),(1,7,10)}
all other-edge endpoint labels.
```

Total: 504 exact pair games.

### Global allocation

```text
k in {5,6}
epsilon in {1/28,7/20}
N-k in {12,14,18,21}.
```

Total: 16 cells.

### Compact optimal value

```text
k in {11,13}
epsilon in {5/24,13/28}
N-k in {4,7,10}.
```

Total: 12 compact-versus-full endpoint enumerations.

### Total-budget threshold

```text
k in {13,15,18}
epsilon in {1/28,5/24,7/20,13/28}
delta in {1/40,1/160,1/640}.
```

Total: 36 exact thresholds.

### Boundaries

```text
epsilon=0 at k in {8,9}
k=2 at N in {14,18}, epsilon in {5/24,13/28}.
```

## Gates

The ten v0.16 gates are retained without weakening:

1. registration binding;
2. registry completeness;
3. direct pair reduction;
4. strict same-branch smoothing;
5. strict opposite-branch smoothing and identities;
6. unique global balanced optimum;
7. compact-value equality;
8. exact total-budget threshold;
9. negative boundaries; and
10. resource and scope.

## Resources

```text
CPU only
wall time <= 120 seconds
peak resident memory <= 1 GiB
GPU prohibited
```

The cap is identical to v0.16. A post-failure cap increase is prohibited.

## Claim boundary

A pass verifies fresh exact instances of the proved balanced maximin theorem
and total-budget threshold for one independent Bernoulli cycle experiment.
It is not adaptive allocation, multi-cycle design, behavioral validation, a
general RL rollout policy, general IRL identifiability, or ASMP-9 resolution.
