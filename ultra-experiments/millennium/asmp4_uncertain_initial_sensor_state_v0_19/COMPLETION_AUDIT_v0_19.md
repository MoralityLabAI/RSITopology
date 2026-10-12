# Completion audit v0.19

## Proved

- The start belief is exactly the registered initial uncertainty set `I`.
- Reachable current-`q` homogeneity is necessary and sufficient.
- Exact finite counts and the `rho(A_I)` asymptotic threshold are proved.
- Transient-only and rate-inflating uncertainty fixtures are separated.
- Two independent implementations reproduce the complete 768-pair census.
- Five initial-state and counting mutations are rejected.

## Verification boundary

The predecessor inventory contains 19 packages and 224 tests. This package
adds 10 focused tests, so the expanded chain contains 234 tests. The central
implementation uses frozenset beliefs and numerical eigenspectra; the
independent verifier uses integer masks and direct small-matrix spectra. The
explicit 20-package regression passed all 234 tests in 271.32 seconds.

## Not claimed

Probabilistic initial priors, active pre-safety calibration, continuous sensor
state, raw compression, expected length, average or block error, and the global
ASMP-4 variational theorem remain outside this package.
