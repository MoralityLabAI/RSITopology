# ASMP-9 v0.19.1 post-outcome timing diagnostic

This diagnostic was run only after the v0.19.1 cells were burned and the
negative registered verdict was fixed. It is not part of the registered
scientific evidence.

## Result

The profiled workload took `430.209` seconds. One stage dominated:

| Stage | Wall seconds |
|---|---:|
| DP/exhaustive check, cycles `(4,6,8,11)` | 387.565 |
| DP/exhaustive check, cycles `(7,8,10)` | 26.666 |
| DP/exhaustive check, cycles `(5,7,9)` | 10.133 |
| full positive all-edge census | 1.998 |
| fresh bridge factorization | 0.955 |
| fresh `(4,4)` factorization | 0.331 |
| burned cache regression | 0.369 |
| all other comparator/regression stages | 2.190 |

The registered liveness cache was not the remaining bottleneck. The
independent cycle-total enumerator repeatedly called
`cycle_worst_direct(balanced_allocation(total, length), epsilon)` for the same
`(length,total)` pair in many different block-total compositions. The
four-block cell magnified that duplicated exact endpoint-label work.

## Permitted successor optimization

A computation-only successor may precompute, independently for every
registered cycle length and feasible total,

```text
g_independent(k,N,epsilon)
  = min over all 2^k endpoint-label assignments
      availability(balanced_allocation(N,k), labels, epsilon).
```

It may then enumerate every feasible vector of cycle totals and multiply the
precomputed exact values. This retains:

- complete endpoint-label enumeration;
- complete cycle-total enumeration;
- exact rational arithmetic;
- an implementation path independent of the compact Bellman factor; and
- the same optimizer-set equality gate.

The optimization removes duplicated evaluations; it does not weaken the
graph family, budget range, theorem, or registered resource cap.

## Evidence boundary

The diagnosis uses burned v0.19.1 cells. It may justify and benchmark a new
implementation, but it cannot be counted as fresh theorem confirmation.
