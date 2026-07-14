# Qwen3-1.7B identity-calibration prereveal result

## Outcome

The Windows-native Research_Engine run reached the registered prereveal stop
without starting behavioral outcomes. The terminal status is
`noise_floor_only`; thresholds were not relaxed.

The immediate stop reason recorded by the frozen pipeline is
`required_predictor_reliability_below_0.5:certification_level`. That string
needs one important qualification: this was not disagreement between the two
split-half estimators. All 192 registered component sites received
`certification_level = 0` in both split A and split B. Spearman correlation is
undefined for two constant vectors, and the frozen Spearman-Brown helper maps
that undefined value to reliability zero.

The result is therefore a structural-degeneracy stop, not an ordinary noisy-
estimator stop. The registered discrimination endpoint cannot be identified
when every site has the same certificate. Independently, the null-floor site
pool contained zero level-2 sites against a minimum of 16, so the pipeline
would have stopped before outcomes even if constant agreement had been treated
as perfect classification agreement.

## What the target-blind measurements show

The continuous geometry estimates were numerically repeatable across the two
prompt halves:

| Predictor | Split-half reliability |
| --- | ---: |
| Jacobian visibility | 0.9965 |
| Mean edge chordal lineage | 0.9986 |
| Minimum edge chordal lineage | 0.9891 |
| Minimum worst-direction retention | 0.9892 |
| Occupancy margin | 0.9897 |
| Maximum canonical holonomy angle | 0.8873 |
| Holonomy noise-null exceedance quantile | 1.0000 |
| Patch identity-loss bound | 0.9893 |
| Realized in-context bundle energy | 0.1062 |

The materialized values describe an identity geometry that is repeatably
inadmissible under the frozen construction:

- mean edge chordal lineage: mean 0.04145;
- minimum edge chordal lineage: mean 0.00489;
- minimum worst-direction retention: mean 3.49e-9;
- maximum loop angle: mean 3.14019 radians, close to pi;
- orientation-reversing holonomy: 176/192 sites (91.67%);
- patch membership: 0/192 sites;
- mean worst-case identity-loss bound: 1.999994 on the registered 0-2 scale.

The frozen random-pair lineage thresholds were 4.69e-8 and 4.59e-8 in the
two halves. Certification uses the bundle's worst-direction chordal lineage,
which is approximately half the already tiny worst-direction retention near
zero; no module cleared even that random-pair threshold. The holonomy null
95th-percentile angles were 3.1246 and 3.1231 radians, while most observed
loops saturated at pi. This is why the all-zero certificate is substantive
under the registered construction rather than a rounding artifact.

Thus the current VPD rank-one weight-component bundles do not define a stable
global signed coordinate across the registered adjacent-layer x replicate
grid. Under the harness's frozen policy, no signed intervention or energy
reward should be promoted on the basis of these certificates.

This repeatability should not be over-read as fully independent estimator
reliability. The A and B prompt halves reuse replica initializations (`a0` and
`b0` share one seed; `a1` and `b1` share the other), and only eight small update
steps separate them. Shared initialization can inflate the split-half values.
It cannot rescue the certificate: the all-zero decision survives in both
halves.

Direct checkpoint inspection also rules out ill-conditioned component bases
as the simple explanation. Component self-Grams are full rank with median
condition number 1.56 and maximum 2.76. Adjacent-layer bundle-overlap singular
values look effectively random (median 0.0031, mean 0.00518, maximum 0.0347).
Same-layer independent-replica bundles show a different pattern: median
singular value 0.095 and maxima as high as 0.948, but their weakest directions
remain only 0.00054-0.015. The rank-16 minimum-singular-value gate therefore
rejects a possible lower-rank core along with the unstable tail.

That suggests a mathematical refinement, not a new invariant level: treat
lineage as a rank filtration. For ordered canonical correlations
`sigma_1 >= ... >= sigma_r`, report the target-blind persistence curve
`R(k) = sigma_k^2` (or its registered chordal transform) against a matched-null
threshold. The largest admitted `k` is the empirically supported identity rank.
It must be selected and sealed before outcomes, rather than chosen after seeing
which rank predicts behavior.

## Claim boundary

This result does not show that transformers lack high-dimensional functional
sections, consensus bands, or useful holonomy structure. The measured bundles
are spans of vectorized rank-one VPD weight components. Adjacent modules are
compared by whitened component Gram overlap; they are not connected by
activation-space Jacobian or secant transports along the model computation.

The supported conclusion is narrower:

> For the frozen Qwen3-1.7B VPD component construction over layers 16-27,
> identity certification is structurally unidentifiable because every site is
> engineering evidence and no level-2 site exists.

Behavioral calibration remains unrun. The real-model predictive claim remains
`not_established`.

There is also a conformance issue to fix before any new behavioral run. The
registered `min_edge_chordal_lineage` formula is the bundle minimum-canonical-
correlation statistic, but the emitted per-site column uses same-index diagonal
retention from the Procrustes transport. Certification itself uses the correct
bundle-level value, so this mismatch did not cause the stop; it would make a
behavioral endpoint using the mislabeled column invalid.

## Legitimate next step

Do not run the frozen v1 outcomes and do not relax its thresholds. Preserve
this run as the negative boundary. A new, separately registered construction
would need independent prompt x seed crossing and transported activation
subspaces at the same physical site across prompts/checkpoints, with Jacobian
or norm-matched secant maps admitted only when their naturality defects pass.
It should preregister a stable-rank lineage filtration and include a conformance
test that every emitted predictor implements its registered equation. Its gate
zero should again require nonconstant certification support before any
behavioral labels are collected.

Canonical hashes and resource receipts are recorded in
`artifacts/qwen3_1p7b_one_prompt/identity_prereveal_result.json`.
