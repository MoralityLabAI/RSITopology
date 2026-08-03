# ASMP-7 meter-coverage robustness result v0.3

## Verdict

`selective_suppression_weakens_registered_attestability`

The committed CPU-exact package evaluated all 96 frozen cells. Every
exactness, reproduction, monotonicity, common-law, and brute-force gate passed,
as did all five metric-robustness probes. The import-independent verifier
recomputed all 96 records, repeated the small-case census, and reported zero
failures.

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

Source checkpoint: `96f5fb1`.

| Artifact | SHA-256 |
|---|---|
| `artifacts_v0_3/result.json` | `630aaefc4045978b91e4c5fc18572ac6e24e02c40ab2c16e4cedceb920863130` |
| `artifacts_v0_3/receipt.json` | `8b90b3b341736e662e620c34d1960c3d2cc7b2a0c6f54d257f75c54b7c49e8b7` |
| `artifacts_v0_3/verification.json` | `66a5e690e7522d188e066d0564b7187117fa5d7a75a15efec0d583bf75278fd9` |

## Claim boundary

This result concerns a 16-point Boolean registry, exact-size event coverage,
fresh fair fallback bits, independent challenges, and two declared
suppression models. It does not establish real meter coverage, identify a
deployment threshold, characterize adaptive history-dependent suppression,
prove transformation-universal attestability, or resolve ASMP-7.
