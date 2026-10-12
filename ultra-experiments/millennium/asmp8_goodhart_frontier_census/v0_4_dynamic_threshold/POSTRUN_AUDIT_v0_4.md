# ASMP-8 v0.4 post-run audit

## Outcome

The registered outcome was:

```text
dynamic_threshold_measured
```

The arbitrary v0.3a 50% optimizer-transfer threshold is no longer part of the
estimand. The result is a first-passage bracket on a monotone certificate
margin.

## Top-spike threshold

Every one of the 1,024 diffuse-error nested streams crossed for every
top-spike policy at the `524,288`-audit checkpoint. No stream crossed by
`262,144`, so the registered-grid threshold is:

```text
262,144 < m_cross <= 524,288.
```

For `top_spike:alpha=0.1`, the mean robust margin moved from approximately
`-0.004652` at 262,144 audits to `+0.001636` at 524,288. The exact-population
calculation also predicted 524,288 as the first registered checkpoint.

The identical threshold across all five top-spike strengths is structural.
Along

```text
pi_alpha = (1-alpha) p0 + alpha delta_top,
```

both proxy gain and every dual movement coordinate scale linearly in `alpha`.
Their critical error-radius ratios are therefore invariant along the path.
Increasing top-spike pressure changes the size of the certified margin but not
the audit count at which its sign becomes identifiable.

## Instrument behavior

- Zero simultaneous-instrument failures across 3,072 nested streams; the
  largest one-sided 95% exact binomial upper bound was 0.002921.
- Zero false crossings conditional on valid norm bounds.
- Zero margin-monotonicity violations.
- Zero post-crossing reversions.
- Forty-seven of 60 error-family/policy cells had positive exact oracle
  margins; 13 were structurally uncertifiable under the registered error
  geometries.

## Verification qualification

The original registered verifier failed because a generic module import was
shadowed by the reused v0.3 source path. It is preserved unchanged. The
additive, explicitly post-run v0.4.1 verifier replayed the scientific core,
all gates, and all three tabular artifacts byte-for-byte; every registered
source and result hash matched. This is valid independent reproducibility
evidence but not a prospective-verifier pass.

## Interpretation

The v0.3 top-spike failure at 512 audits was calibration-censored, not
structural. Under the registered distribution-free finite-grid instrument,
the concentrated policy path required roughly three orders of magnitude more
audits before its robust margin became positive. A more efficient successor
should compare alternate prospectively frozen audit designs against this
measured first-passage cost rather than lowering a certification-fraction
threshold.

## Claim boundary

This is a synthetic finite-population result for one finite-grid Hoeffding
instrument. It does not show that 524,288 audits are necessary for all sound
calibrators or that the same threshold transfers to learned reward models.
