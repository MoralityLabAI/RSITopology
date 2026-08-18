# Completion audit v0.22

## Proved

- Raw observer homogeneity is necessary and sufficient for a causal encoder.
- Belief tracking followed by current-`q` emission gives exact region
  `[2,infinity) x [2,infinity)` for every feasible finite local sensor.
- A three-symbol witness strictly separates static and causal coarsening.
- The complete 256-transducer and 53,108-relation censuses inherit the theorem.
- Exact finite-margin products and five timing/encoding mutations pass.
- Central and import-independent implementations agree.

## Verification boundary

The predecessor inventory contains 22 packages and 254 tests. This package
adds 10 focused tests, so the expanded chain contains 264 tests. The explicit
23-package regression passed all 264 tests in 307.25 seconds.

## Not claimed

This is not a delayed-sensing, bounded-memory, continuous-observation, or
global nonlinear theorem. Forced-raw experiments remain governed by the
v0.18-v0.21 contracts rather than this encoder-optimized one.

V0.23 subsequently freezes the delayed-sensing timing contract for the local
collar and proves the positive-delay impossibility plus preview and
predictability restorations. That successor does not alter this same-step
claim.
