# ASMP-8 v0.5 claim packet: audit-efficiency frontier

## Question

ASMP-8 v0.4 measured a first-passage threshold of 524,288 audits for the
diffuse top-spike path under a finite-grid Hoeffding instrument. Version 0.5
asks whether that cost belongs to the safety certificate or only to the chosen
calibrator.

## Matched methods

All methods use the same hidden finite error populations, proxy-only policies,
unit pointwise error cap, and strictly positive robust-margin crossing rule.

1. `hoeffding_shared`: the frozen v0.4 policy-agnostic baseline.
2. `empirical_bernstein_shared`: the same nested IID streams and alpha
   allocation, replacing range-only bounds with the sample-variance bound of
   Maurer and Pontil (2009).
3. `movement_ordered_partial_census`: audit distinct outcomes in descending
   `|pi-p0|`. Revealed coupling is exact; every unrevealed term is bounded at
   its worst allowed value. The audit order depends on the proxy-only policy,
   never on hidden error.
4. `full_census`: reveal all 64 outcomes and compute true gain exactly.

Each method yields a monotone certificate margin and a first-passage audit
count. No fraction of crossing streams is a gate.

## Claim boundary

This is an audit-efficiency comparison on a 64-outcome synthetic registry.
Movement-ordered partial census is policy-specific and assumes the finite
outcome atoms are enumerable. A pass does not imply the same efficiency in
open-ended language output spaces or resolve ASMP-8.
