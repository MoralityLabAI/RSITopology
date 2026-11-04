# Round-robin review of ASMP-1 proposal

## Strongest objection — `scope_narrowing`

The estimand establishes whether an observational residual-stream vector predicts
unseen coordinated-mask responses better than a global coefficient model. It
does **not** identify a unique causal abstraction modulo symmetry. `z_p` may encode task
template, answer state, lexical identity, or effect scale rather than a reusable
context mechanism. Exact Mobius coefficients make the *responses* identifiable
on each cube, not the proposed context field. Rename the output
`ContextInteractionPredictionReceipt`, prohibit
claims of mechanism recovery, and do not let it define intervention-authorized
"context regions."

## Other findings

- **`repairable` — target blindness and leakage.** Prompt-disjoint confirmation
  is insufficient if calibration and confirmation share templates or families.
  Require a co-primary template/family-group holdout. Seal extraction layer,
  token position, pooling, PCA, features, and group assignments before capture;
  bind their hashes to the prereveal commit/run receipt.
- **`repairable` — capacity control.** Rank below one quarter of prompt count
  does not bound the parameter count of the multi-output map `B phi(z)`, and
  independent information is closer to prompt groups. Freeze a
  degrees-of-freedom ceiling relative to calibration groups and use
  nested grouped CV. Add a matched-capacity baseline using every allowed
  non-residual predictor: task/template metadata, `y_p(0)`, and all singleton
  responses. The residual feature must add held-out value beyond that baseline.
  Within-family shuffling remains useful but is not a substitute.
- **`repairable` — matched control.** Define magnitude matching without any
  confirmation-mask outcome. Match from calibration-only effect
  distributions or target-blind norm/Jacobian covariates, then seal pairs.
  Otherwise the geometry-specific contrast can leak its targets.
- **`nonissue` — held-out response design.** Predicting eleven masks from the
  baseline, four singletons, and prereveal features strongly tests conditional
  prediction. The global/additive comparators, exact
  sign gate, planted/additive fixtures, and explicit invalid-instrument states
  are appropriate.
- **`scope_narrowing` — authorization.** A pass may prioritize further VPD
  analysis or propose patch-local tests. It must not authorize an
  activation or weight edit; existing identity certification, trust-radius,
  damage, and utility gates remain independently necessary.
- **`repairable` — resources.** The estimates are plausible, but evaluation
  count alone is not a receipt. Freeze precision, batch size, prompt and
  generation-token ceilings, retry policy, and peak-VRAM abort threshold. Six
  GB for Qwen-1.7B should be treated as a measured preflight claim, not assumed.

## Concrete repair and verdict

Amend the estimand to incremental prediction over the matched-capacity
non-residual baseline; add template/family-held-out confirmation; seal
calibration-only control matching and the full feature provenance; and demote
the consumer artifact to advisory evidence.

**Verdict: `revise_before_pilot`.** The run is small and potentially useful,
but the current design could turn context leakage into an identifiability
certificate and downstream edit permission.
