# ASMP-2 active-design census v0.2.1 result

## Decision

**UNAVAILABLE — total wall ceiling crossed; emitted outputs quarantined.**

The optimized core reported 171.67 seconds, but the Python process remained alive after the external wrapper crossed the registered 180-second total wall ceiling and timed out at 184.1 seconds. The emitted result and receipt are preserved under `quarantined_*` names and are explicitly not claim-eligible. Their scientific fields were not inspected.

A performance-only diagnostic subsequently timed the unchanged registered computation at approximately 15.75 seconds without `tracemalloc`. The intrusive allocation tracer, not the 65,536-subset scientific computation, was the dominant runtime cost. This diagnosis does not use or alter selector outcomes.

## Binding

- Preregistered commit: `8ac30b8505bc55f489e13e4f3e2e0710bc2345f0`
- Quarantined result SHA-256: `a986b91804882714ce5d2a0f7f2d9853fc9101a4c9c1de728111cf6e57a410a1`
- Quarantined receipt SHA-256: `35e8cdc7336a1e10cce690d33a6638c3212086fc30cd07979a25633b9689aeb8`

## Successor constraint

A v0.2.2 performance amendment may replace `tracemalloc` with sampled process RSS and must measure from before input binding through final artifact construction. It may not alter the parent universe, selector definitions, seeds, thresholds, tie contract, or claim boundary.

## Claim boundary

No scientific ASMP-2 result is claimed from v0.2.1.
