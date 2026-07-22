# ASMP-10 v0.5.1 prior-art and baseline audit

## Purpose

This audit freezes the comparison classes that a transition predictor must
beat. A geometry model is not informative merely because it beats a monotone
data-fraction rule or a short loss prefix.

## Anchors

### Grokking regime

Power et al. introduced delayed generalization after overfitting on small
algorithmic datasets and reported its dependence on dataset size:
<https://arxiv.org/abs/2201.02177>.

### Optimizer instability

Thilak et al. identify the Slingshot mechanism in adaptive optimizers: cyclic
stable and unstable regimes whose behavior is visible in late-stage loss and
last-layer weight norms. Their result makes optimizer dynamics and norm
trajectories mandatory nuisance/progress baselines here:
<https://arxiv.org/abs/2206.04817>.

### Mechanistic progress measures

Nanda et al. reverse-engineer a Fourier multiplication circuit for modular
addition and define progress measures that separate memorization, circuit
formation, and cleanup. The successor baseline includes their restricted loss
(retain only the registered key Fourier components), excluded loss (remove
those components), Fourier sparsity/concentration, and associated weight-norm
trajectories:
<https://arxiv.org/abs/2301.05217>.

To prevent outcome leakage, key-frequency selection must be fitted only on the
construction split and then frozen before application to any holdout seed.
Selecting each holdout model's frequencies from its post-transition state is
forbidden.

### Effective-theory phase structure

Liu et al. derive a toy effective theory and map comprehension, grokking,
memorization, and confusion phases over training-set and hyperparameter
regimes. A construction-split phase-map predictor is therefore a required
baseline, not an optional discussion comparator:
<https://arxiv.org/abs/2205.10343>.

## Frozen baseline ladder

The registration must pin source revisions and exact implementations, but may
not remove a block from this ladder:

- `B0_hyperparameter`: train fraction, weight decay, split size, model size,
  optimizer identity, learning rate, and seed-cluster metadata.
- `B1_scalar_prefix`: `B0` plus the complete allowed train/test loss,
  train/test accuracy, gradient norm, global parameter norm, last-layer norm,
  and logit-scale trajectories through step 500.
- `B2_published_progress`: `B1` plus construction-frozen restricted loss,
  excluded loss, registered Fourier concentration/Gini measures, and the
  construction-split effective-theory phase-map prediction.
- `B3_geometry`: the target-blind spectral/representation block.

The primary question is whether `B2_published_progress + B3_geometry` improves
on `B2_published_progress`. Comparisons against `B0` and `B1` remain mandatory
diagnostics but cannot establish the geometry claim.

## Scope

The v0.4 spike association is consistent with, but does not prove, Slingshot.
No primary source was found here that licenses labeling the one-grid events as
persistent ungrokking. The successor claim is explicitly conditional on the
registered AdamW optimizer and regularization strata. Cross-optimizer
generalization requires a separate registered ablation.

