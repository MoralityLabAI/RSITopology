# ASMP-9 behavioral well-posedness development note v0.7

## Burned development evidence

Before any v0.7 prospective protocol was frozen, the implementation was tested
on every oriented simple graph through five vertices:

| vertices | graphs | access-ledger mismatches | coherent-field mismatches |
|---:|---:|---:|---:|
| 1 | 1 | 0 | 0 |
| 2 | 3 | 0 | 0 |
| 3 | 27 | 0 | 0 |
| 4 | 729 | 0 | 0 |
| 5 | 59,049 | 0 | 0 |

For every graph the census checked:

```text
spanning-forest query count = |V|-c(G),
post-forest chord count      = beta_1(G),
coherence-only query set     = all non-bridge edges.
```

It also planted a unit corruption on one non-bridge edge whenever available
and required incoherence, and changed one bridge value whenever available and
required coherence to remain possible. There were zero failures.

The current 60-test development suite also checks exact Hodge projection,
cycle inconsistency, parallel-edge bridge handling, adaptive interval width,
and the optimal nonadaptive threshold spacing.

## Correction made during development

The first theorem draft said that pure coherence certification required all
edge values. That was false on graphs with bridges: bridge scores impose no
cycle constraint. The corrected ledger distinguishes:

1. scalar reconstruction under a coherence promise;
2. coherence-only certification; and
3. combined reconstruction and certification.

This correction occurred before registration and before any claim-eligible
v0.7 run.

## Claim status

All counts above are burned implementation development. They cannot serve as
fresh verification cells. The written results remain classical finite graph
and comparison-search facts, not a full ASMP-9 resolution.
