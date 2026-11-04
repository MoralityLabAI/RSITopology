# Development note: ASMP-9 v0.31

The registered predecessor audit named one joint approximate factorization as
the next load-bearing result. The candidate model is:

```text
y = (A+Delta)theta + Cb + l + m + Ds.
```

The design decision is to preserve source geometry. Context-only drift is an
exact nuisance space; semantic calibration is cell-indexed; localization and
midpoint residuals are row-indexed; mechanical drift is multiplicative.

The burned controls must include:

- context confounding after residualization;
- mechanical gain exactly one;
- strict/equality policy margins;
- a shared semantic-cell cancellation; and
- a support witness attaining the reported zonotope boundary.

No stochastic interpretation is assigned to deterministic widths. No
confidence level is implied. A successor may calibrate the widths
statistically, but this version treats them as registered assumptions.
