# ASMP-9 conditional-fiber implementation repair v0.13.1

## Status

This amendment supersedes the resource-unavailable v0.13 execution attempt.
It changes exact-arithmetic implementation only.

## Scientific invariants

Unchanged from v0.13:

- theorem and proof;
- all fresh liveness graphs;
- all nine fresh power-calibration cells;
- exact size and power band;
- all ten gates;
- success verdict;
- claim boundary; and
- 180-second, 2-GiB, CPU-only resource envelope.

## Permitted repair

Version v0.13 materialized exact weight arrays and reduced giant fractions.
Version v0.13.1:

1. streams null and alternative integer weight sums in two passes;
2. constructs the randomized-boundary and power ratios without reducing them;
3. checks the registered rational inequalities by exact integer cross
   multiplication; and
4. stores bit lengths and byte hashes of the unreduced integers plus a
   30-digit decimal rendering.

The literal and streaming implementations must agree exactly on every burned
small registry cell. The repair may not run a registered fresh cell before
its own implementation and registration are committed.
