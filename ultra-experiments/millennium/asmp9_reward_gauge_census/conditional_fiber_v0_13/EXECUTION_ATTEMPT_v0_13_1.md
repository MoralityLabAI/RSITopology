# ASMP-9 v0.13.1 registered repair attempt

Date: 2026-07-28

Registration commit: `c2c5936fa275107182622affaf5fe420cb7865ad`

## Status

```text
unavailable_resource_cap_no_scientific_result
```

The v0.13.1 runner used the registered streaming exact-power repair but again
exceeded the unchanged 180-second wall-time cap. The outer watchdog returned
timeout after approximately 204 seconds. The surviving process was terminated
at approximately 207 CPU seconds and 1.72 GB working set.

No output directory or scientific artifact existed after termination. No gate
or fresh-cell result was read.

## Corrected diagnosis

The streaming power implementation was not the remaining bottleneck. The
closed-form verification arm first constructed a generic zero-balance fiber
by enumerating all `(n+1)^k` count vectors and filtering them. With
`formula_trials_per_edge=3` and fresh cycle length `k=18`, that attempted an
irrelevant `4^18` ambient enumeration even though the theorem proves the
zero-balance fiber contains only four vectors:

```text
(0,...,0), (1,...,1), (2,...,2), (3,...,3).
```

A scientifically invariant repair may construct those four vectors directly.
It may not alter any theorem, cell, gate, threshold, or resource limit.
