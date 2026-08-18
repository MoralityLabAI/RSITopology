# ASMP-8 v0.5 audit-efficiency result

**Verdict:** `efficiency_frontier_measured`

## Diffuse top-spike first-passage costs

| policy | partial census | empirical Bernstein min | median | max | Hoeffding min | full census |
|---|---:|---:|---:|---:|---:|---:|
| top_spike:alpha=0.1 | 31 | 8192 | 8192.0 | 8192 | 524288 | 64 |
| top_spike:alpha=0.25 | 31 | 8192 | 8192.0 | 8192 | 524288 | 64 |
| top_spike:alpha=0.5 | 31 | 8192 | 8192.0 | 8192 | 524288 | 64 |
| top_spike:alpha=0.75 | 31 | 8192 | 8192.0 | 8192 | 524288 | 64 |
| top_spike:alpha=1 | 31 | 8192 | 8192.0 | 8192 | 524288 | 64 |

The partial census is policy-specific and deterministic. Empirical Bernstein and Hoeffding are shared error-norm calibrators. Full census is an exact finite-universe reference.

## Soundness

- Conditional false crossings: 0.
- Monotonicity violations: 0.
- Reversions: 0.
- Partial-census endpoint mismatches: 0.

## Empirical-Bernstein instrument

| error family | invalid streams | CP upper |
|---|---:|---:|
| diffuse_low_error | 0/1024 | 0.002921 |
| heteroskedastic_proxy_coupled | 0/1024 | 0.002921 |
| rare_top_tail | 0/1024 | 0.002921 |

## Claim boundary

Synthetic 64-outcome audit-efficiency comparison; movement-ordered census assumes enumerable atoms and no learned reward model or ASMP-8 resolution.
