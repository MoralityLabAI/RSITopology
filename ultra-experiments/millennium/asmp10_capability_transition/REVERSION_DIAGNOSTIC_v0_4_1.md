# ASMP-10 v0.4.1 reversion diagnostic

## Status

Post-hoc, descriptive analysis of the sealed v0.4 pilot. It does not change the
v0.4 gate, promote the pilot to claim-eligible evidence, or authorize another
run.

## Finding

The seven events called post-transition failures by the v0.4 single-threshold
detector were isolated threshold excursions, not observed persistent loss of
capability.

- All 7 lasted exactly one 100-step evaluation interval.
- All 7 recovered at the immediately following evaluation.
- All 7 coincided with a train-loss increase of at least 10 times and a
  gradient-norm increase of at least 100 times their respective preceding
  10-evaluation medians.
- The observed train-loss ratios ranged from 12.886 to 504.736.
- The observed gradient-norm ratios ranged from 195.669 to 11,614.882.
- There were 15 post-crossing spikes under that post-hoc rule. Only 7 caused an
  old-detector excursion, so the rule's descriptive positive predictive value
  was 7/15 = 46.7%.
- Only 4 of the 7 excursions crossed the proposed v0.5.1 down threshold of
  test accuracy below 0.80 or test loss above 0.75. None persisted for five
  evaluations.

The defensible result is therefore **optimizer-spike-correlated metric
instability under the old detector**. The data are consistent with the
Slingshot mechanism reported for adaptive optimizers, but this analysis does
not identify a cause, distinguish all optimizer mechanisms, or establish
ungrokking. In particular, spike association is not spike sufficiency.

## Why the endpoint changes

The old detector used one up/down boundary. That makes chatter and isolated
loss spikes look like reversions. The successor draft replaces it with a
finite-horizon state machine that freezes:

1. an entry dwell time;
2. a distinct, more adverse exit threshold and exit dwell time; and
3. a primary evaluation cadence plus deterministic coarser-grid sensitivity
   replays.

The successor outcome is horizon-stable capability, not irreversible or
infinite-time stability. The three primary classes are no adjudicable stable
transition, early stable transition, and delayed stable transition.

## Reproducibility

Run:

```powershell
python ultra-experiments/millennium/asmp10_capability_transition/analyze_reversion_diagnostics_v0_4_1.py
python -m pytest -q ultra-experiments/millennium/asmp10_capability_transition/test_analyze_reversion_diagnostics_v0_4_1.py
```

Canonical machine-readable output:
`pilot_artifacts_v0_4/reversion_diagnostics_v0_4_1.json`.

The script hashes each source `metrics.json`. The existing sealed v0.4 files
are not modified; this document and its artifacts form an additive correction
layer.

## Literature placement

Thilak et al. describe cyclic stable/unstable regimes, loss instability, and
last-layer-weight-norm signatures in late training with adaptive optimizers:
<https://arxiv.org/abs/2206.04817>. That makes Slingshot a live explanation to
control for, not a conclusion from these six cells.

