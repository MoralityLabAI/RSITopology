# ASMP-9 v0.13 registered execution attempt

Date: 2026-07-28

Registration commit: `47cf967697c5504415b29f237fa65f8245293323`

## Status

```text
unavailable_resource_cap_no_scientific_result
```

The registered runner was launched with the local GPU hidden. It exceeded the
protocol's 180-second wall-time cap. The outer 240-second watchdog returned
timeout, after which the surviving process was terminated.

Observed immediately before termination:

```text
CPU time:            approximately 250 seconds
working set:         approximately 1.64 GB
registered RAM cap:  2 GiB
registered time cap: 180 seconds
```

No output directory or scientific artifact existed after termination. No gate
or fresh-cell result was read.

## Diagnosis

The theorem and registered cells are unchanged. The implementation materialized
large exact integer weight arrays and repeatedly reduced enormous rational
fractions. The exact arithmetic representation, rather than graph-fiber
enumeration or the scientific estimand, exhausted the wall-time envelope and
approached the RAM cap.

Any repair must be versioned, additive, and scientifically invariant. A
permitted repair may stream the exact weight sums and compare unreduced integer
ratios by cross multiplication. It may not change the fresh cells, power band,
gates, theorem, or claim boundary.
