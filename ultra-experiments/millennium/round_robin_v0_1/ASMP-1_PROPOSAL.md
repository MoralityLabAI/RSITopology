# ASMP-1 proposal: context-conditioned interaction tomography

## Status and target

ASMP-1 asks when interventions identify a causal abstraction modulo a declared
functional symmetry. Existing work establishes an exact finite Boolean design
instrument, then finds a useful real-model boundary: four lineage-certified
Qwen-0.8B projectors are causally live, but one global degree-two interaction
law predicts worse than an additive model in all nine held-out context
subconditions. The next experiment should test the narrowed alternative--a
context-conditioned interaction field--rather than repeat the rejected global
fit. This is a bounded real-model falsification, not a resolution of ASMP-1.

## Smallest decisive experiment: singleton-to-cube conditional atlas

Use the same four registered projector sites and the untouched confirmation
prompts reserved by the v0.2 successor. Retain its calibration/confirmation
split and magnitude-matched random arm. Before reading any confirmation mask
outcome, record for each prompt a target-blind context vector `z_p` from the
unintervened residual stream. Fit its PCA basis and all hyperparameters on the
revealed calibration split only.

For each prompt `p`, let `y_p(m)` be the answer-margin response at mask
`m in {0,1}^4`. The complete cube defines exact Mobius coefficients
`theta_p(S)`. At confirmation time, the predictor may see only `y_p(0)`, the
four singleton responses, and `z_p`; the remaining eleven coordinated masks
are held-out targets. The frozen model is

```text
y_hat_p(m) = theta_p(empty) + sum_i theta_p(i) m_i
             + sum_{|S|>=2} [B phi(z_p)]_S product_{i in S} m_i.
```

Choose `phi`, ridge penalty, and coefficient-field rank from a small sealed
grid by grouped calibration CV. The primary estimand is

```text
Delta_context = 1 - SSE_context / SSE_global,
```

on the eleven unseen masks, where `SSE_global` uses the best calibration-fit
context-independent higher-order coefficients while preserving the same
prompt-specific baseline and singleton terms. The geometry-specific estimand
is `Delta_context(selected) - Delta_context(magnitude-matched random)`.

### Frozen hypothesis and decision

Pass only if all conditions hold on untouched confirmation prompts:

1. `Delta_context(selected) >= 0.10` in aggregate;
2. at least eight of nine frozen subconditions have positive improvement over
   the global comparator (exact one-sided sign-test boundary `10/512`);
3. the selected-minus-random improvement is at least 0.05; and
4. the shuffled-context control has aggregate improvement at most 0.02.

These margins must be frozen after a synthetic/revealed-data pilot and before
confirmation capture. Equality is inconclusive. No threshold may be relaxed.

### Controls, falsifiers, and kill criteria

- **Magnitude-matched random projectors:** removes the v0.1 S0 scale confound.
- **Within-family shuffled `z_p`:** tests whether the context map adds signal
  rather than flexible parameter count.
- **Global and additive comparators:** distinguish conditional structure from
  the already-rejected global law and from no interaction law.
- **Planted/additive fixtures:** must recover a planted low-rank coefficient
  field and reject an additive null before model outcomes are admitted.
- **Leakage audit:** hashes must show that PCA, rank selection, folds, and
  prompt embeddings predate confirmation-mask reveal.

Failure of conditions 1 or 2 falsifies a reusable conditional atlas for this
frozen object. Failure of condition 3 rejects geometry specificity. Replay,
scale-match, causal-liveness, prompt-disjointness, or leakage failure makes the
instrument invalid rather than the hypothesis false. A context rank using
more than one quarter of calibration prompts is a preregistered overcapacity
kill, preventing near-interpolation from masquerading as structure.

### Evidence, consumer, and reusable artifact

The evidence class is **registered real-model predictive evidence with exact
within-prompt coefficients**. It neither proves generic identifiability nor
licenses weight edits. The named consumer is the **VPD edit planner**: it may
pool coordinated activation edits only inside context regions whose held-out
certificate passes; elsewhere it must fall back to independent or additive
edits. Emit a reusable `ContextInteractionCertificate` containing data/model
hashes, gauge-invariant projector IDs, context-map hash, selected rank,
per-subcondition margins, random/shuffle controls, and an abstention reason.

## Optional scale-up

If the four-site test passes, repeat with six certified sites and a complete
64-mask cube on Qwen-1.7B, using disjoint task families and a second checkpoint.
The decisive transfer question is whether one construction-split context map
predicts coefficients at a held-out checkpoint, not whether a newly fitted map
works there. A failure narrows the certificate to model-state-local use.

## Resource estimate

| Run | Evaluations | Wall time | CPU | RAM | Disk | GPU / VRAM | GPU-hours |
|---|---:|---:|---:|---:|---:|---:|---:|
| Pilot (revealed data + fixtures) | analysis only | 10-20 min | 2 cores | 2 GB | 0.2 GB | none | 0 |
| Four-site confirmation | about 3,500 including alpha calibration | 1-2 h | 4 cores | 6 GB | 2 GB | 1 GPU / 3.4 GB | 1-2 |
| Optional six-site Qwen-1.7B | about 12,300 | 6-10 h | 6 cores | 10 GB | 8 GB | 1 GPU / 6 GB | 6-10 |

## One reason not to run it

With only nine context subconditions, a conditional map can remain
underpowered or look stable because task metadata is repetitive. If the
unintervened context embeddings were not sealed before confirmation outcomes,
do not retrofit them: wait for a genuinely fresh prompt corpus, because a
post-outcome descriptor would make the central target-blind claim unauditable.
