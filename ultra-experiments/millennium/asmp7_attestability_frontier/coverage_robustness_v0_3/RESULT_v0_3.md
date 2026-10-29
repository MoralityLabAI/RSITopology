# ASMP-7 meter-coverage robustness result v0.3

## Verdict

`selective_suppression_weakens_registered_attestability`

The CPU-exact package evaluated all 96 frozen cells. Every
exactness, reproduction, monotonicity, common-law, and brute-force gate passed,
as did the all-cell cross-model weakening gate and all five metric-robustness
probes. The import-independent verifier recomputed the exact registered
protocol, all 96 complete records, gates, probes, witnesses, and four conclusion
layers; it repeated the small-case census and reported zero failures.

## Exact contrast

At the representative boundary `k1=14`, channel `theta=3/4`, and 12/16
coverage, policy-independent missingness required 134 challenges while
adversarial selective suppression required 668. At 10/16 coverage, the
independent arm remained feasible at 194 challenges, but the selective arm
admitted a compliant/forbidden common report law, proving `FP+FN>=1` for every
sample count.

| Coverage | Policy-independent | Selective suppression |
|---:|---:|---:|
| 8/16 | 304 | common-law impossible |
| 10/16 | 194 | common-law impossible |
| 12/16 | 134 | 668 |
| 14/16 | 97 | 166 |
| 16/16 | 73 | 73 |

Full coverage reproduced the relevant v0.2.1 minima under both models:
`73,50,15` for `k1=14` and `40,26,5` for `k1=16` at
`theta=3/4,4/5,1`. Input-relabeling invariance, coverage sensitivity,
coverage monotonicity, the anti-gaming contrast, and the full-coverage clean
control all passed.

## Four conclusion layers

1. **Task result —** `selective_suppression_weakens_registered_attestability`.
   The frozen exact grid distinguishes independent missingness from strategic
   evidence suppression.
2. **Measurement reliability —** `reliable_exact_finite_measurement`. Exact
   adjacent certificates, v0.2.1 reproduction, brute-force small cases, and
   the independent replay all passed.
3. **Claim support —** `registered_finite_claim_supported`. On this Boolean
   grid, selective suppression can create an exact common-law region and
   otherwise increases or preserves audit burden relative to independent
   coverage.
4. **Operational decision —** `no_deployment_decision_authorized`. The finite
   synthetic result has no validated real-meter or deployment bridge.

## Artifact binding

The original v0.3 evidence used source checkpoint `96f5fb1`. The verifier
hardening source checkpoint is
`91c9f47bd9bc786a603c8a9a08e5bc4963be9f4f`. The artifact writers were
rerun afterward; the receipt's exact source-file hashes match the bytes in that
checkpoint, and the bundle receipt binds the regenerated verification.

| Artifact | SHA-256 |
|---|---|
| `artifacts_v0_3/result.json` | `8277b755f4ee26cfb1df48b9986d252a8102a2f92eb6a6a7afa6d2d3b7134ffa` |
| `artifacts_v0_3/receipt.json` | `f22d5e493028c6ec7c5679fb53f9d41fd94296c23c8a23b5c09e817dbf294c70` |
| `artifacts_v0_3/verification.json` | `e741bf99191e4de1f77ac25ebb170efb9b357659e6c424afd3839751450bf07a` |
| `artifacts_v0_3/bundle_receipt.json` | `b7ddbad42daa8aef0b85a627fac77112961594afaa80352b78be6368354381b6` |

## Claim boundary

This result concerns a 16-point Boolean registry, fresh per-challenge
policy-independent coverage events, an execution-dependent exact-`c`-point
selective mask fixed across challenges, fresh fair fallback bits, and
independent challenges. It does not cover an execution-fixed random independent
mask, establish real meter coverage, identify a deployment threshold,
characterize adaptive history-dependent suppression, prove
transformation-universal attestability, or resolve ASMP-7.
