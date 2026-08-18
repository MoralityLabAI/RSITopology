# Completion audit v0.20

## Proved

- Raw `m`-color refinement preserves feasibility and beliefs.
- `A_m=mA`, `L_T(m)=m^T L_T`, and `rho(A_m)=m rho(A)`.
- Exact writes are invariant and coarsening recovers the base sensor.
- The computed family has an unbounded forced-raw read corner.
- Central and independent deterministic robustness ensembles validate larger
  nondeterministic belief graphs without serving as proof substitutes.
- Both implementations preserve the `80/176` split over 768 clone instances.
- Five plant-only/refinement mutations are rejected.

## Verification boundary

The predecessor inventory contains 20 packages and 234 tests. This package
adds 10 focused tests, so the expanded chain contains 244 tests. The final
current-state 21-package regression passed all 244 tests in 327.11 seconds.

## Stopping audit

The harness proves a scoped stop for plant-only forced-raw read entropy. It
does not prove ASMP-4 complete: fixed-sensor parameterization, optimization
over encoders, and quotient-first semantics remain legitimate global routes.
The separate requirement audit records the evidence and verdict for each of
the five frozen resolution requirements.
