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

The primary path used exact `Fraction` arithmetic.  A standalone verifier that
does not import the implementation repeated all 1,399,680 pointwise cells and
matched the total cell count, robust violation count, full-census count, and
plug-in false-declaration count.  All comparisons agreed.

The first combined shell wrapper reached its external 120-second limit after
the primary artifact had completed.  The independent replay was then run as a
separate bounded command and completed successfully in 73.7 seconds.  No
scientific threshold or cell selection changed between those commands.

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
| `artifacts_v0_6/result_v0_6.json` | `13ae6cee5333247f4906b089f68782aeaecbf24515063fb3374f885105b6b2eb` |
| `artifacts_v0_6/verification_v0_6.json` | `73e518d61d53901ac64c9bebcab0c928b199eb48138916ce087bf4fa61ae14f2` |

Dedicated tests: `6 passed`.
