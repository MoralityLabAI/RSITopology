# ASMP-8 v0.5 post-run audit

## Outcome

The registered verdict was:

```text
efficiency_frontier_measured
```

For every diffuse-error top-spike strength, the first positive robust
certificate occurred at:

| method | audits |
|---|---:|
| movement-ordered partial census | 31 |
| full exact census | 64 |
| shared empirical Bernstein | 8,192 |
| shared Hoeffding | 524,288 |

The empirical-Bernstein instrument reduced the shared-calibration cost by
exactly 64-fold on the registered checkpoint grid. The deterministic
movement-ordered audit reduced the Hoeffding cost by about 16,913-fold and
crossed before half of the finite universe had been revealed.

## Why the partial census can stop at 31

The auditor orders atoms by `|pi_i-p0_i|`, which is known without true reward.
For revealed atoms it uses the exact coupling contribution. Every unseen atom
retains the registered worst-case contribution under `|e_i| <= 1`. Each reveal
can only improve or preserve the lower bound, so the certificate is
deterministic and non-reverting.

All five top-spike strengths induce the same audit order and critical ratio.
The same 31 revealed atoms therefore certify the entire registered top-spike
path, not five disjoint 31-audit jobs.

## Soundness and replay

- Zero conditional false crossings.
- Zero monotonicity violations or reversions.
- Zero mismatches between the 64-atom partial-census endpoint and exact true
  gain.
- Zero empirical-Bernstein instrument failures across 3,072 nested streams;
  the largest one-sided 95% exact binomial upper bound was 0.002921.
- The independent verifier reproduced the focus result, all gates, and all
  three CSV artifacts byte-for-byte.
- All 22 ASMP-8 tests pass.

## Operational interpretation

The 524,288-audit estimate was not intrinsic to top-spike certification. It
was the price of a range-only, shared, with-replacement calibrator. On an
enumerable deterministic 64-atom universe:

- 31 targeted distinct labels suffice for this contemplated policy path;
- 64 labels determine every error atom and can be reused for every policy;
- 8,192 samples are relevant only when a shared stochastic calibration
  interface is required; and
- 524,288 should not be used as a deployment estimate.

The comparison also exposes a real tradeoff. Movement-ordered auditing is
policy-specific, whereas a shared norm certificate amortizes over policies.
For many unrelated policy paths, the union of targeted atoms may approach a
full census.

## Claim boundary

These reductions rely on a finite enumerable universe and deterministic hidden
error per atom. Open-ended language outputs, noisy human labels, and adaptive
policy generation require a new registered sampling model.
