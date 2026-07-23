# ASMP-8 v0.4 dynamic audit-threshold result

**Verdict:** `dynamic_threshold_measured`

## Correction

This run does not ask whether 50% of replicates certify. It reports the first registered audit checkpoint at which each nested stream's monotone robust margin becomes positive.

## Instrument

- Nested streams per error family: 1,024.
- Checkpoint range: 32 to 1,048,576 audits.
- Conditional false crossings: 0.
- Margin monotonicity violations: 0.
- Post-crossing reversions: 0.

## Diffuse-error top-spike path

| policy | oracle margin | predicted checkpoint | min | q25 | median | q75 | max | censored |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| top_spike:alpha=0.1 | 0.040156 | 524288 | 524288 | 524288.0 | 524288.0 | 524288.0 | 524288 | 0 |
| top_spike:alpha=0.25 | 0.100391 | 524288 | 524288 | 524288.0 | 524288.0 | 524288.0 | 524288 | 0 |
| top_spike:alpha=0.5 | 0.200781 | 524288 | 524288 | 524288.0 | 524288.0 | 524288.0 | 524288 | 0 |
| top_spike:alpha=0.75 | 0.301172 | 524288 | 524288 | 524288.0 | 524288.0 | 524288.0 | 524288 | 0 |
| top_spike:alpha=1 | 0.401562 | 524288 | 524288 | 524288.0 | 524288.0 | 524288.0 | 524288 | 0 |

Crossing fractions and quantiles are descriptive outputs, not decision thresholds.

## Simultaneous instrument

| error family | invalid streams | CP upper |
|---|---:|---:|
| diffuse_low_error | 0/1024 | 0.002921 |
| heteroskedastic_proxy_coupled | 0/1024 | 0.002921 |
| rare_top_tail | 0/1024 | 0.002921 |

## Claim boundary

Synthetic finite-population first-passage audit thresholds under a finite-grid simultaneous Hoeffding instrument; no learned reward model, no universal sequential-optimality claim, and no ASMP-8 resolution.
