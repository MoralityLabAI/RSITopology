# ASMP-8 adaptive deterministic-audit result v0.6

## Verdict

`adaptive_pointwise_certificate_sound`

The movement-weighted deterministic partial-census lower bound remained sound
under transcript-adaptive policy and audit selection on the complete frozen
six-atom class.  The matched plug-in selector, which treated unaudited error
as zero, produced live false declarations.

## Task result

The primary census checked all `729 x 64 x 30 = 1,399,680` combinations of
ternary error population, revealed subset, and directed mass-move policy.  It
found:

| Check | Outcome |
|---|---:|
| robust lower-bound violations | 0 |
| full-census equality failures | 0 |
| plug-in false declarations over all pointwise cells | 133,488 |
| fixed-policy reveal-monotonicity failures | 0 |

The frozen adaptive selector generated 729 complete audit traces.  Its robust
certificate made zero false positive-gain declarations.  The plug-in
selection metric made 512 false declarations across 252 traces.  A minimal
recorded control occurs before any audit: the proxy-only move from atom zero
to atom five scores `1/6`, its robust lower bound is `-1/6`, and its exact true
gain is zero under the displayed adverse error population.

The mechanism is pointwise.  For every selected policy and revealed set, each
unseen term `d_i e_i` is at least `-|d_i|` under the frozen error cap.  The
lower bound therefore holds simultaneously before and after adaptive
selection; no stochastic multiplicity correction is being inferred.

## Metric robustness

All five frozen probe families passed: joint atom relabeling, error-cap
sensitivity, fixed-policy reveal monotonicity, adaptive plug-in anti-gaming,
and full-census equality.

## Measurement reliability

The primary path used exact `Fraction` arithmetic. A standalone verifier that
does not import the implementation repeated all 1,399,680 pointwise cells and
all 729 adaptive traces with scaled exact integers. It independently matched
the complete pointwise/adaptive summaries, first witnesses, digest, policy
feasibility, reveal monotonicity, five probes, seven primary gates, exact result
key universe, and four conclusion layers. All comparisons agreed. On the
review machine the primary replay took 89.0 seconds and the independent replay
took 7.4 seconds.

## Claim support and operation

The result supports reuse of this deterministic worst-case certificate after
adaptive selection on a finite enumerable atom set.  It does not establish
favorable audit efficiency for every search: a valid bound may remain too
conservative to cross.

The next experiment must separately register noisy or drifting labels,
stochastic optional stopping, and nonenumerable output sampling.  This package
does not validate data-dependent confidence-sequence reuse, a learned reward
model, or ASMP-8 as a whole.

## Artifact integrity

| Artifact | SHA-256 |
|---|---|
| `artifacts_v0_6/result_v0_6.json` | `2d5a83acf7cd0fcb5964a5040ca695eff0444a3e625173b7f9750b75740787d4` |
| `artifacts_v0_6/run_receipt_v0_6.json` | `5d95014895f40682f92180fab3232fe999aa235b249f9cf8c2a452a95a03760f` |
| `artifacts_v0_6/verification_v0_6.json` | `b1ec0abbad370c5c0cb1a87955068986373ae52ba9fb71e8f7d20cbacbda7a8c` |
| `artifacts_v0_6/bundle_receipt_v0_6.json` | `4735bc4d4e2d15f1848e487589bebdbb7b64b1cf7cf2ad16028c22ca9f2d8501` |

The verifier-hardening source checkpoint is
`78ac61ea553c2f2936edb7b62897850d47d327ff`. The primary and independent
writers were rerun afterward; their exact source-file hashes match that
checkpoint, and the bundle receipt binds the regenerated verification.

Dedicated tests: `15 passed`.
