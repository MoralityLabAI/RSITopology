# Completion audit v0.18

## Proved within the registered family

- The known-initial-state finite transducer is feasible exactly when every
  reachable subset-observer transition is current-`q` homogeneous.
- Exact read counts are `L_T ceil(rho*2^T)` and exact write counts are
  `2^T ceil(rho*2^T)`.
- The raw-language exponent is exactly `log2(rho(A))`.
- Five separating fixtures include a non-integer golden threshold and a
  history-essential feasible sensor.
- Independent exhaustive implementations classify all 256 two-state
  deterministic binary transducers as 80 feasible and 176 infeasible.
- Five targeted mutations are rejected.

## Verification boundary

The predecessor inventory contains 18 packages and 214 tests. This package
adds 10 focused tests, so the expanded ASMP-4 chain contains 224 tests. The
central implementation uses frozenset beliefs and numerical eigenvalues; the
independent verifier uses integer bitmasks and closed-form one/two-state
spectral calculations. The explicit 19-package regression passed all 224 tests
in 370.34 seconds.

## Not claimed

This is not a proof of the full ASMP-4 variational conjecture. Unknown initial
sensor state, infinite or continuous memory, controller-side raw compression,
block error, expected-length coding, and general nonlinear coordinate-
invariant transversal entropies remain open registered directions.
