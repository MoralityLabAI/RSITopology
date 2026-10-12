# ASMP-9 v0.13 development note

## Burned result

The first CPU census is design evidence only. It is not registered and cannot
satisfy a future confirmation gate.

Across triangle, square, theta, and complete-four comparison graphs, exact
enumeration confirmed:

- scalar gauge transforms left every tested conditional law byte-for-byte
  unchanged;
- conditional-fiber affine rank never exceeded graph cycle rank;
- singleton fibers exposed no quotient coordinate; and
- the flat-null probability of a full-rank fiber increased strongly with
  trials per edge.

The full-quotient masses at one, two, and three trials per edge were:

| graph | beta1 | n=1 | n=2 | n=3 |
|---|---:|---:|---:|---:|
| cycle 3 | 1 | 0.2500 | 0.7188 | 0.9180 |
| cycle 4 | 1 | 0.1250 | 0.5703 | 0.8560 |
| theta 5 | 2 | 0.1875 | 0.7168 | 0.9282 |
| complete 4 | 3 | 0.3750 | 0.8809 | 0.9839 |

These are flat-null, registry-specific availability masses. They are not
universal probabilities over comparison tasks.

## Exact conditional-power development

For conditional size `alpha=0.05` and target power `0.8`, the first exact
attainments were:

| odds ratio | k=3 | k=4 | k=6 | k=8 | k=12 |
|---|---:|---:|---:|---:|---:|
| 3/2 | 453 | 603 | 903 | 1203 | 1805 |
| 2 | 155 | 207 | 309 | 413 | 619 |
| 3 | 63 | 84 | 125 | 167 | 251 |

The normalized quantity:

```text
n_first / k * log(R)^2
```

stayed near `25`, matching the local `k/log(R)^2` scaling prediction.

This does **not** define a monotone sample threshold. Exact-size randomized
conditional power has finite-lattice sawteeth as `n` changes, because each
sample count creates a different conditioned experiment and a different
randomized boundary. For example, the `k=4, R=2` cell first clears 0.8 at
`n=207`, falls below at `n=208`, and clears it again at `n=209`.

A future protocol must call these values `first attainments`, not critical
sample thresholds. Any sustained-power quantity needs its own frozen
definition and cannot be inferred from the first crossing.

## Freeze decision

The exact nuisance-elimination and fiber-rank theorem merits a prospective
v0.13 verification because it closes a finite-sample gauge bookkeeping gap.
The power table is explanatory and should remain secondary. No gate should
promote non-rejection into a scalar-coherence certificate.
