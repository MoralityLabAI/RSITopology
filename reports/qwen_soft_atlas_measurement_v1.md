# Qwen soft-atlas measurement gate v1

## Outcome

The frozen, target-blind measurement component **failed**. The instrument was
valid; this is a scientific failure rather than a provenance or calibration
failure.

The result closes the near-term prompt-corpus investment under protocol
`qwen-soft-atlas-measurement-v1` (SHA-256
`01eaf1f1566c8a189c74b4f4616ff7ad4cc76e2cbad9aa03cb3c6200a774dc58`).
The prompt-scale component is independently unavailable because the current
eight ARC groups have no sealed interchangeable-behavior families. Overall G1
is therefore `not_evaluated`, G2-G4 are not reached, and no recursive or signed
edit experiment is authorized.

## Frozen gate values

| Quantity | Result | Frozen boundary | Outcome |
| --- | ---: | ---: | --- |
| `lambda_measurement` | 0.1694149742 | derived | - |
| Measurement edges | 112 | exactly 112 | pass |
| Central `d_eff` range | 4.343180 | strictly below 1.0 | fail |
| Simultaneous-band intersection margin | -3.100099 | strictly above 0 | fail |
| Minimum observed-minus-null identity margin | -0.094024 | pass above 0.05; fail below 0 | fail |
| Minimum informative fraction | 1.000000 | strictly above 0.20 | pass |
| Minimum median anisotropy | 0.421853 | strictly above 0.10 | pass |
| Audit-null false-support rate | 255/4096 = 0.0622559 | at most 256/4096 = 0.0625 | pass, one draw inside ceiling |

## Mathematical interpretation

The soft construction exposes a scale tradeoff rather than a plateau. At very
small regularization, the operator is almost the identity: minimum similarity
is near one, but the spectrum is nearly flat and therefore uninformative. As
regularization enters the measurement-noise neighborhood, anisotropy becomes
substantial, but the median effective dimension falls from 6.63 to 2.29 across
the frozen central decade and minimum cross-fit identity falls through the
matched-null threshold.

Thus no registered scale near `lambda_measurement` is simultaneously:

- spectrally informative;
- dimensionally persistent; and
- cross-context identity-bearing above the matched null.

This is stronger and cleaner than the earlier hard-rank boundary failure. It
does not merely say that a singular-value cut was ambiguous. It says that the
continuous, gauge-invariant soft family has no stable measurement-scale window
under the frozen criteria.

The result does **not** show that transformers lack high-dimensional behavioral
structures. It rejects one specific object: a single global soft atlas formed
from the existing Qwen probe-response Grams over all twelve registered modules,
eight prompt groups, four replicas, and three checkpoints.

## Decision

The registered decision is `do_not_invest_stop_branch`: do not build the new
prompt-family corpus for this atlas. The methods protocol remains useful as a
standalone artifact, and the negative joins the VPD site-selection null and
hard-lineage `noise_floor_only` result as a progressively stronger boundary on
globally stable edit coordinates.

## Claim boundary

This target-blind gate uses no behavioral outcomes. It does not identify
coordinated weight-space edits, authorize signed edits, measure recursive
improvement, or establish or rule out RSI.

Canonical artifacts are under
`artifacts/qwen_soft_atlas_measurement_v1/`.
